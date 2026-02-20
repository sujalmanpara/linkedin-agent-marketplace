"""
LinkedIn Agent - Executor
Sends personalized LinkedIn connection requests and messages using AI.
"""
import httpx
import re
from app.core.sse import sse_event, sse_error
from app.core.config import settings

# Import agent-specific modules
from .linkedin_service import send_connection_request, send_message
from .llm_service import generate_personalized_note


async def execute(prompt: str, keys: dict, language: str = None, options: dict = None):
    """
    Main executor for LinkedIn agent.
    
    Args:
        prompt: User's request (e.g., "Send connection to https://linkedin.com/in/john-smith")
        keys: {
            "LINKEDIN_SESSION_COOKIE": "AQEDATg...",  # Primary auth method (recommended)
            "LINKEDIN_EMAIL": "user@example.com",     # Fallback (may hit security checkpoint)
            "LINKEDIN_PASSWORD": "password",          # Fallback
            "LLM_API_KEY": "sk-...",
            "LLM_PROVIDER": "google",  # optional: anthropic/openai/google
            "LLM_MODEL": "gemini-2.5-flash"  # optional
        }
        language: "en", "es", etc.
        options: {
            "action": "connect" or "message",  # default: connect
            "personalize": true/false,         # default: true
            "full_name": "John Smith",         # optional
            "title": "CEO at TechCorp",        # optional
            "company": "TechCorp",             # optional
            "message_text": "..."              # for message action
        }
    
    Yields:
        SSE events with status updates and final result
    """
    try:
        # Extract credentials (prioritize session cookie)
        linkedin_session_cookie = keys.get("LINKEDIN_SESSION_COOKIE")
        linkedin_email = keys.get("LINKEDIN_EMAIL")
        linkedin_password = keys.get("LINKEDIN_PASSWORD")
        llm_api_key = keys.get("LLM_API_KEY")
        
        # Check if we have either cookie OR email+password
        has_cookie = bool(linkedin_session_cookie)
        has_password = bool(linkedin_email and linkedin_password)
        
        if not has_cookie and not has_password:
            yield sse_error(
                "LinkedIn authentication missing. Provide either:\n"
                "1. LINKEDIN_SESSION_COOKIE (recommended - no security checkpoints)\n"
                "2. LINKEDIN_EMAIL + LINKEDIN_PASSWORD (may trigger security verification)"
            )
            return
        
        if not llm_api_key:
            yield sse_error("LLM API key missing (LLM_API_KEY)")
            return
        
        # Determine auth method
        auth_method = "cookie" if has_cookie else "password"
        if auth_method == "password":
            yield sse_event("status", "⚠️ Using password auth - may encounter security checkpoint. Consider using session cookie instead.")
        
        # Package credentials
        linkedin_creds = {
            "method": auth_method,
            "session_cookie": linkedin_session_cookie,
            "email": linkedin_email,
            "password": linkedin_password
        }
        
        # Extract options
        opts = options or {}
        action = opts.get("action", "connect")
        personalize = opts.get("personalize", True)
        
        # LLM config
        llm_provider = keys.get("LLM_PROVIDER", "google").lower()
        llm_model = keys.get("LLM_MODEL", _default_model(llm_provider))
        
        llm_config = {
            "provider": llm_provider,
            "model": llm_model,
            "api_key": llm_api_key
        }
        
        # Extract LinkedIn profile URL from prompt
        linkedin_url = _extract_linkedin_url(prompt)
        if not linkedin_url:
            yield sse_error("No LinkedIn profile URL found in prompt. Example: https://linkedin.com/in/username")
            return
        
        yield sse_event("status", f"🔗 Found LinkedIn profile: {linkedin_url}")
        
        # Extract prospect info (from options or prompt)
        full_name = opts.get("full_name", _extract_name_from_prompt(prompt))
        title = opts.get("title", "")
        company = opts.get("company", "")
        
        async with httpx.AsyncClient(timeout=90) as client:
            # Action: Send connection request
            if action == "connect":
                yield sse_event("status", "🤖 Generating personalized connection note...")
                
                if personalize:
                    note = await generate_personalized_note(
                        client,
                        llm_config,
                        {
                            "full_name": full_name,
                            "title": title,
                            "company": company,
                            "linkedin_url": linkedin_url
                        }
                    )
                    yield sse_event("status", f"✅ Generated note: \"{note[:50]}...\"")
                else:
                    note = None
                
                yield sse_event("status", "📤 Sending LinkedIn connection request...")
                
                result = await send_connection_request(
                    client,
                    linkedin_creds,
                    linkedin_url,
                    note
                )
                
                if result["success"]:
                    yield sse_event("result", {
                        "success": True,
                        "action": "connect",
                        "linkedin_url": linkedin_url,
                        "personalized_note": note,
                        "message": f"✅ Connection request sent to {full_name or linkedin_url}"
                    })
                else:
                    yield sse_error(f"Failed to send connection: {result.get('error', 'Unknown error')}")
            
            # Action: Send message
            elif action == "message":
                message_text = opts.get("message_text")
                
                if not message_text:
                    yield sse_error("Message text required for 'message' action (provide in options.message_text)")
                    return
                
                if personalize:
                    yield sse_event("status", "🤖 Personalizing message with AI...")
                    message_text = await generate_personalized_note(
                        client,
                        llm_config,
                        {
                            "full_name": full_name,
                            "title": title,
                            "company": company,
                            "linkedin_url": linkedin_url,
                            "base_message": message_text
                        }
                    )
                
                yield sse_event("status", "📤 Sending LinkedIn message...")
                
                result = await send_message(
                    client,
                    linkedin_creds,
                    linkedin_url,
                    message_text
                )
                
                if result["success"]:
                    yield sse_event("result", {
                        "success": True,
                        "action": "message",
                        "linkedin_url": linkedin_url,
                        "message": message_text,
                        "status": f"✅ Message sent to {full_name or linkedin_url}"
                    })
                else:
                    yield sse_error(f"Failed to send message: {result.get('error', 'Unknown error')}")
            
            else:
                yield sse_error(f"Unknown action: {action}. Use 'connect' or 'message'")
    
    except Exception as e:
        yield sse_error(f"LinkedIn agent error: {str(e)}")


def _extract_linkedin_url(text: str) -> str:
    """Extract LinkedIn profile URL from text."""
    # Match linkedin.com/in/username or linkedin.com/company/name
    pattern = r'https?://(?:www\.)?linkedin\.com/(?:in|company)/[\w\-]+'
    match = re.search(pattern, text)
    return match.group(0) if match else None


def _extract_name_from_prompt(text: str) -> str:
    """Try to extract person's name from prompt."""
    # Simple heuristic: look for capitalized words after "to" or "with"
    pattern = r'(?:to|with|for)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)'
    match = re.search(pattern, text)
    return match.group(1) if match else ""


def _default_model(provider: str) -> str:
    """Get default model for provider."""
    defaults = {
        "anthropic": "claude-sonnet-4-5",
        "openai": "gpt-4o-mini",
        "google": "gemini-2.0-flash-exp"
    }
    return defaults.get(provider, "gemini-2.0-flash-exp")
