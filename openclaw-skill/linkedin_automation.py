#!/usr/bin/env python3
"""
LinkedIn Automation for OpenClaw
Calls marketplace for AI personalization, executes actions locally via browser control.
"""
import os
import sys
import re
import asyncio
import httpx
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout


# Marketplace API endpoint
MARKETPLACE_URL = os.getenv(
    "LINKEDIN_MARKETPLACE_URL",
    "https://marketplacebackend-production-58c8.up.railway.app"
)


async def send_connection_request(profile_url: str, note: str = None, full_name: str = None):
    """
    Send LinkedIn connection request using local browser.
    
    Args:
        profile_url: LinkedIn profile URL
        note: Optional connection note (max 300 chars)
        full_name: Person's name (for logging)
    
    Returns:
        {"success": bool, "error": str (if failed)}
    """
    try:
        async with async_playwright() as p:
            # Launch browser (will use existing Chrome profile if available)
            browser = await p.chromium.launch(
                headless=False,  # Show browser so user can see what's happening
                channel="chrome"  # Use installed Chrome
            )
            
            context = await browser.new_context(
                viewport={"width": 1280, "height": 720}
            )
            page = await context.new_page()
            
            try:
                # Go to LinkedIn (user should already be logged in)
                await page.goto("https://www.linkedin.com/feed/", timeout=30000)
                await page.wait_for_load_state("networkidle")
                
                # Check if logged in
                if "login" in page.url or "checkpoint" in page.url:
                    return {
                        "success": False,
                        "error": "Not logged into LinkedIn. Please login in your browser first."
                    }
                
                print("✅ Logged into LinkedIn")
                
                # Navigate to profile
                await page.goto(profile_url, timeout=30000)
                await page.wait_for_load_state("networkidle")
                print(f"✅ Opened profile: {profile_url}")
                
                # Find and click "Connect" button
                connect_button = await page.query_selector('button:has-text("Connect")')
                
                if not connect_button:
                    # Check if already connected
                    if await page.query_selector('button:has-text("Pending")'):
                        return {"success": False, "error": "Connection request already sent"}
                    if await page.query_selector('button:has-text("Message")'):
                        return {"success": False, "error": "Already connected with this person"}
                    
                    return {"success": False, "error": "Connect button not found on profile"}
                
                await connect_button.click()
                await page.wait_for_timeout(2000)
                print("✅ Clicked Connect")
                
                # Add note if provided
                if note:
                    # Look for "Add a note" button
                    add_note_button = await page.query_selector('button:has-text("Add a note")')
                    
                    if add_note_button:
                        await add_note_button.click()
                        await page.wait_for_timeout(1000)
                        
                        # Find textarea and type note
                        note_field = await page.query_selector('textarea[name="message"]')
                        if note_field:
                            await note_field.fill(note[:300])  # LinkedIn limit
                            await page.wait_for_timeout(1000)
                            print(f"✅ Added note: {note[:50]}...")
                
                # Send connection request
                send_button = await page.query_selector('button[aria-label*="Send"]')
                if not send_button:
                    send_button = await page.query_selector('button:has-text("Send")')
                
                if send_button:
                    await send_button.click()
                    await page.wait_for_timeout(3000)
                    print(f"✅ Connection request sent to {full_name or profile_url}")
                    
                    return {"success": True}
                else:
                    return {"success": False, "error": "Send button not found"}
            
            finally:
                await browser.close()
    
    except PlaywrightTimeout:
        return {"success": False, "error": "Browser timeout (LinkedIn might be slow)"}
    except Exception as e:
        return {"success": False, "error": f"Automation error: {str(e)}"}


async def send_message(profile_url: str, message: str, full_name: str = None):
    """
    Send LinkedIn message using local browser.
    
    Args:
        profile_url: LinkedIn profile URL
        message: Message text
        full_name: Person's name (for logging)
    
    Returns:
        {"success": bool, "error": str (if failed)}
    """
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False, channel="chrome")
            context = await browser.new_context(viewport={"width": 1280, "height": 720})
            page = await context.new_page()
            
            try:
                # Go to LinkedIn
                await page.goto("https://www.linkedin.com/feed/", timeout=30000)
                await page.wait_for_load_state("networkidle")
                
                # Check if logged in
                if "login" in page.url:
                    return {"success": False, "error": "Not logged into LinkedIn"}
                
                # Navigate to profile
                await page.goto(profile_url, timeout=30000)
                await page.wait_for_load_state("networkidle")
                
                # Click "Message" button
                message_button = await page.query_selector('button:has-text("Message")')
                
                if not message_button:
                    return {
                        "success": False,
                        "error": "Message button not found. Are you connected with this person?"
                    }
                
                await message_button.click()
                await page.wait_for_timeout(2000)
                
                # Type message
                message_field = await page.query_selector('div[contenteditable="true"]')
                if not message_field:
                    message_field = await page.query_selector('textarea[name="message"]')
                
                if message_field:
                    await message_field.fill(message)
                    await page.wait_for_timeout(1000)
                else:
                    return {"success": False, "error": "Message input field not found"}
                
                # Send message
                send_button = await page.query_selector('button[type="submit"]')
                if not send_button:
                    send_button = await page.query_selector('button:has-text("Send")')
                
                if send_button:
                    await send_button.click()
                    await page.wait_for_timeout(3000)
                    print(f"✅ Message sent to {full_name or profile_url}")
                    
                    return {"success": True}
                else:
                    return {"success": False, "error": "Send button not found"}
            
            finally:
                await browser.close()
    
    except PlaywrightTimeout:
        return {"success": False, "error": "Browser timeout"}
    except Exception as e:
        return {"success": False, "error": f"Automation error: {str(e)}"}


async def call_marketplace_for_ai_message(
    prompt: str,
    linkedin_url: str,
    action: str = "connect",
    **context
):
    """
    Call marketplace API to generate AI-personalized message.
    
    Args:
        prompt: User's original request
        linkedin_url: LinkedIn profile URL
        action: "connect" or "message"
        **context: Additional context (full_name, title, company, message_text, etc.)
    
    Returns:
        {"success": bool, "personalized_note": str, "error": str}
    """
    try:
        llm_api_key = os.getenv("LLM_API_KEY")
        if not llm_api_key:
            return {
                "success": False,
                "error": "LLM_API_KEY not set. Configure in OpenClaw settings."
            }
        
        async with httpx.AsyncClient(timeout=60) as client:
            print(f"🤖 Calling marketplace for AI message generation...")
            
            response = await client.post(
                f"{MARKETPLACE_URL}/v1/agents/linkedin-agent/execute",
                headers={
                    "Content-Type": "application/json",
                    "X-User-LLM-Key": llm_api_key
                },
                json={
                    "prompt": prompt,
                    "language": "en",
                    "options": {
                        "action": action,
                        "personalize": True,
                        **context
                    }
                }
            )
            
            if response.status_code != 200:
                return {
                    "success": False,
                    "error": f"Marketplace API error: {response.status_code}"
                }
            
            # Parse SSE stream to get result
            result = None
            for line in response.text.split("\n"):
                if line.startswith("data: "):
                    import json
                    try:
                        data = json.loads(line[6:])
                        if isinstance(data, dict):
                            result = data
                    except:
                        pass
            
            if result and result.get("success"):
                note = result.get("personalized_note") or result.get("message")
                print(f"✅ AI generated: {note[:60]}...")
                return {
                    "success": True,
                    "personalized_note": note
                }
            else:
                return {
                    "success": False,
                    "error": result.get("error", "Unknown error") if result else "No response"
                }
    
    except Exception as e:
        return {"success": False, "error": f"Marketplace call failed: {str(e)}"}


async def main():
    """Main entry point for OpenClaw skill."""
    if len(sys.argv) < 2:
        print("Usage: linkedin_automation.py <prompt>")
        print("Example: linkedin_automation.py 'Connect with John on LinkedIn: https://linkedin.com/in/john'")
        sys.exit(1)
    
    prompt = " ".join(sys.argv[1:])
    
    # Extract LinkedIn URL
    url_match = re.search(r'https?://(?:www\.)?linkedin\.com/in/[\w\-]+', prompt)
    if not url_match:
        print("❌ No LinkedIn URL found in prompt")
        sys.exit(1)
    
    linkedin_url = url_match.group(0)
    
    # Determine action
    action = "message" if "message" in prompt.lower() else "connect"
    
    # Extract context
    name_match = re.search(r'(?:with|to)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)', prompt)
    full_name = name_match.group(1) if name_match else None
    
    # Get AI-generated message from marketplace
    result = await call_marketplace_for_ai_message(
        prompt=prompt,
        linkedin_url=linkedin_url,
        action=action,
        full_name=full_name
    )
    
    if not result.get("success"):
        print(f"❌ {result.get('error')}")
        sys.exit(1)
    
    ai_message = result.get("personalized_note")
    
    # Execute action locally
    if action == "connect":
        result = await send_connection_request(
            profile_url=linkedin_url,
            note=ai_message,
            full_name=full_name
        )
    else:
        result = await send_message(
            profile_url=linkedin_url,
            message=ai_message,
            full_name=full_name
        )
    
    if result["success"]:
        print(f"\n✅ SUCCESS! LinkedIn {action} completed.")
        sys.exit(0)
    else:
        print(f"\n❌ FAILED: {result.get('error')}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
