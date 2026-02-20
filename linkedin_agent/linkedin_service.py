"""
LinkedIn Service - Browser automation for LinkedIn actions
Uses Playwright for headless LinkedIn automation
"""
import httpx
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout


async def _authenticate_linkedin(page, context, credentials: dict) -> dict:
    """
    Helper function to authenticate to LinkedIn using either cookie or password.
    
    Args:
        page: Playwright page object
        context: Playwright browser context
        credentials: {
            "method": "cookie" | "password",
            "session_cookie": "..." (if method=cookie),
            "email": "..." (if method=password),
            "password": "..." (if method=password)
        }
    
    Returns:
        {"success": bool, "error": str (if failed)}
    """
    auth_method = credentials.get("method", "password")
    
    if auth_method == "cookie":
        # Use session cookie (no login required)
        session_cookie = credentials.get("session_cookie")
        if not session_cookie:
            return {"success": False, "error": "Session cookie missing"}
        
        # Add cookie to browser context
        await context.add_cookies([{
            "name": "li_at",
            "value": session_cookie,
            "domain": ".linkedin.com",
            "path": "/",
            "secure": True,
            "httpOnly": True
        }])
        
        # Go directly to feed (already authenticated)
        await page.goto("https://www.linkedin.com/feed/", timeout=30000)
        await page.wait_for_load_state("networkidle")
        
        # Verify we're logged in
        if "login" in page.url or "checkpoint" in page.url:
            return {"success": False, "error": "Session cookie expired or invalid. Please provide a fresh cookie."}
        
        return {"success": True}
    
    else:
        # Use email/password login
        email = credentials.get("email")
        password = credentials.get("password")
        
        if not email or not password:
            return {"success": False, "error": "Email and password required"}
        
        await page.goto("https://www.linkedin.com/login", timeout=30000)
        await page.fill('input[name="session_key"]', email)
        await page.fill('input[name="session_password"]', password)
        await page.click('button[type="submit"]')
        
        # Wait for login to complete
        try:
            await page.wait_for_url("https://www.linkedin.com/feed/*", timeout=30000)
            return {"success": True}
        except:
            # Check for security checkpoint
            if "checkpoint" in page.url or "challenge" in page.url:
                return {
                    "success": False,
                    "error": "LinkedIn security checkpoint detected. Please use session cookie authentication instead."
                }
            raise


async def send_connection_request(
    client: httpx.AsyncClient,
    credentials: dict,
    profile_url: str,
    note: str = None
) -> dict:
    """
    Send LinkedIn connection request using Playwright.
    
    Args:
        client: httpx.AsyncClient (unused, for consistency)
        credentials: {
            "method": "cookie" | "password",
            "session_cookie": "AQEDATg..." (if method=cookie),
            "email": "user@example.com" (if method=password),
            "password": "..." (if method=password)
        }
        profile_url: Target profile URL
        note: Optional personalized note (max 300 chars)
    
    Returns:
        {"success": bool, "error": str (if failed)}
    """
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                viewport={"width": 1280, "height": 720},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            )
            page = await context.new_page()
            
            try:
                # 1. Authenticate to LinkedIn
                auth_result = await _authenticate_linkedin(page, context, credentials)
                if not auth_result.get("success"):
                    return auth_result
                
                # 2. Go to profile
                await page.goto(profile_url, timeout=30000)
                await page.wait_for_load_state("networkidle")
                
                # 3. Click "Connect" button
                connect_button = await page.query_selector('button:has-text("Connect")')
                
                if not connect_button:
                    # Maybe already connected?
                    pending = await page.query_selector('button:has-text("Pending")')
                    if pending:
                        return {"success": False, "error": "Connection request already sent"}
                    
                    connected = await page.query_selector('button:has-text("Message")')
                    if connected:
                        return {"success": False, "error": "Already connected with this person"}
                    
                    return {"success": False, "error": "Connect button not found on profile"}
                
                await connect_button.click()
                await page.wait_for_timeout(2000)
                
                # 4. Add note if provided
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
                
                # 5. Send connection request
                send_button = await page.query_selector('button[aria-label*="Send"]')
                if not send_button:
                    send_button = await page.query_selector('button:has-text("Send")')
                
                if send_button:
                    await send_button.click()
                    await page.wait_for_timeout(3000)
                    
                    return {"success": True}
                else:
                    return {"success": False, "error": "Send button not found"}
            
            finally:
                await browser.close()
    
    except PlaywrightTimeout:
        return {"success": False, "error": "LinkedIn operation timeout"}
    except Exception as e:
        return {"success": False, "error": f"LinkedIn automation error: {str(e)}"}


async def send_message(
    client: httpx.AsyncClient,
    credentials: dict,
    profile_url: str,
    message: str
) -> dict:
    """
    Send LinkedIn message using Playwright.
    
    Args:
        client: httpx.AsyncClient (unused, for consistency)
        credentials: {
            "method": "cookie" | "password",
            "session_cookie": "AQEDATg..." (if method=cookie),
            "email": "user@example.com" (if method=password),
            "password": "..." (if method=password)
        }
        profile_url: Target profile URL
        message: Message text
    
    Returns:
        {"success": bool, "error": str (if failed)}
    """
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                viewport={"width": 1280, "height": 720},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            )
            page = await context.new_page()
            
            try:
                # 1. Authenticate to LinkedIn
                auth_result = await _authenticate_linkedin(page, context, credentials)
                if not auth_result.get("success"):
                    return auth_result
                
                # 2. Go to profile
                await page.goto(profile_url, timeout=30000)
                await page.wait_for_load_state("networkidle")
                
                # 3. Click "Message" button
                message_button = await page.query_selector('button:has-text("Message")')
                
                if not message_button:
                    return {"success": False, "error": "Message button not found. Are you connected with this person?"}
                
                await message_button.click()
                await page.wait_for_timeout(2000)
                
                # 4. Type message in the message box
                message_field = await page.query_selector('div[contenteditable="true"]')
                if not message_field:
                    message_field = await page.query_selector('textarea[name="message"]')
                
                if message_field:
                    await message_field.fill(message)
                    await page.wait_for_timeout(1000)
                else:
                    return {"success": False, "error": "Message input field not found"}
                
                # 5. Send message
                send_button = await page.query_selector('button[type="submit"]')
                if not send_button:
                    send_button = await page.query_selector('button:has-text("Send")')
                
                if send_button:
                    await send_button.click()
                    await page.wait_for_timeout(3000)
                    
                    return {"success": True}
                else:
                    return {"success": False, "error": "Send button not found"}
            
            finally:
                await browser.close()
    
    except PlaywrightTimeout:
        return {"success": False, "error": "LinkedIn operation timeout"}
    except Exception as e:
        return {"success": False, "error": f"LinkedIn automation error: {str(e)}"}
