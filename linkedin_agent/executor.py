"""
LinkedIn Agent - Marketplace Coordinator
Generates personalized messages and provides automation commands for OpenClaw to execute locally.
"""
import httpx
import re
from app.core.sse import sse_event, sse_error
from app.core.config import settings

# Import agent-specific modules
from .llm_service import generate_personalized_note


async def execute(prompt: str, keys: dict, language: str = None, options: dict = None):
    """
    LinkedIn Agent - Coordinator/Brain
    
    Generates personalized AI messages and provides structured commands for OpenClaw to execute.
    OpenClaw will handle the actual browser automation locally using the user's logged-in browser.
    
    Args:
        prompt: User's request (e.g., "Send connection to https://linkedin.com/in/john-smith")
        keys: {
            "LLM_API_KEY": "sk-...",           # Required for AI personalization
            "LLM_PROVIDER": "google",          # Optional: anthropic/openai/google (default: google)
            "LLM_MODEL": "gemini-2.0-flash-exp" # Optional
        }
        language: "en", "es", etc.
        options: {
            "action": "connect" or "message",  # Default: connect
            "personalize": true/false,         # Default: true
            "full_name": "John Smith",         # Optional
            "title": "CEO at TechCorp",        # Optional
            "company": "TechCorp",             # Optional
            "message_text": "..."              # For message action or custom note
        }
    
    Yields:
        SSE events with:
        - status: Progress updates
        - result: Final command for OpenClaw to execute {
            "action": "connect" | "message",
            "linkedin_url": "...",
            "personalized_note": "..." (if applicable),
            "openclaw_command": {
              "type": "linkedin_automation",
              "action": "connect" | "message",
              "profile_url": "...",
              "message": "..."
            }
          }
    """
    try:
        # Extract LLM credentials
        llm_api_key = keys.get("LLM_API_KEY")
        
        if not llm_api_key:
            yield sse_error("LLM_API_KEY required for AI personalization")
            return
        
        # LLM config
        llm_provider = keys.get("LLM_PROVIDER", "google").lower()
        llm_model = keys.get("LLM_MODEL", _default_model(llm_provider))
        
        llm_config = {
            "provider": llm_provider,
            "model": llm_model,
            "api_key": llm_api_key
        }
        
        # Extract options
        opts = options or {}
        action = opts.get("action", "connect")
        personalize = opts.get("personalize", True)
        
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
        
        async with httpx.AsyncClient(timeout=30) as client:
            # Generate personalized message/note
            if action == "connect":
                if personalize:
                    yield sse_event("status", "🤖 Generating personalized connection note...")
                    
                    note = await generate_personalized_note(
                        client,
                        llm_config,
                        {
                            "full_name": full_name,
                            "title": title,
                            "company": company,
                            "linkedin_url": linkedin_url,
                            "base_message": opts.get("message_text")
                        }
                    )
                    
                    yield sse_event("status", f"✅ Generated: \"{note[:60]}...\"")
                else:
                    note = opts.get("message_text", None)
                
                # Return command for OpenClaw to execute
                yield sse_event("result", {
                    "success": True,
                    "action": "connect",
                    "linkedin_url": linkedin_url,
                    "personalized_note": note,
                    "openclaw_command": {
                        "type": "linkedin_automation",
                        "action": "connect",
                        "profile_url": linkedin_url,
                        "note": note,
                        "full_name": full_name
                    },
                    "message": f"✅ Ready to send connection request{' with personalized note' if note else ''}"
                })
            
            elif action == "message":
                message_text = opts.get("message_text")
                
                if not message_text:
                    yield sse_error("message_text required for 'message' action")
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
                    
                    yield sse_event("status", f"✅ Personalized: \"{message_text[:60]}...\"")
                
                # Return command for OpenClaw to execute
                yield sse_event("result", {
                    "success": True,
                    "action": "message",
                    "linkedin_url": linkedin_url,
                    "message": message_text,
                    "openclaw_command": {
                        "type": "linkedin_automation",
                        "action": "message",
                        "profile_url": linkedin_url,
                        "message": message_text,
                        "full_name": full_name
                    },
                    "status": f"✅ Ready to send message"
                })
            
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
