"""
LLM Service - Generate personalized LinkedIn messages
Supports Anthropic, OpenAI, and Google Gemini
"""
import httpx
import json
from typing import Dict, Any


async def generate_personalized_note(
    client: httpx.AsyncClient,
    llm_config: Dict[str, str],
    prospect: Dict[str, Any]
) -> str:
    """
    Generate personalized LinkedIn connection note using LLM.
    
    Args:
        client: httpx.AsyncClient
        llm_config: {
            "provider": "anthropic" | "openai" | "google",
            "model": "claude-sonnet-4-5" | "gpt-4o-mini" | "gemini-2.0-flash-exp",
            "api_key": "..."
        }
        prospect: {
            "full_name": "John Smith",
            "title": "CEO",
            "company": "TechCorp",
            "linkedin_url": "...",
            "base_message": "..." (optional, for personalization)
        }
    
    Returns:
        Personalized note text (max 300 chars for LinkedIn)
    """
    provider = llm_config["provider"]
    model = llm_config["model"]
    api_key = llm_config["api_key"]
    
    # Build prompt
    if prospect.get("base_message"):
        # Personalize existing message
        system_prompt = """You are a LinkedIn outreach expert. Personalize the following message for the prospect.
Keep it professional, warm, and under 300 characters (LinkedIn connection note limit).
DO NOT add greetings like "Hi [Name]" - just the core message."""
        
        user_prompt = f"""Prospect: {prospect.get('full_name', 'Unknown')}
Title: {prospect.get('title', 'Unknown')}
Company: {prospect.get('company', 'Unknown')}

Base message: {prospect['base_message']}

Personalize this message for the prospect above. Keep under 300 characters."""
    
    else:
        # Generate from scratch
        system_prompt = """You are a LinkedIn outreach expert. Write a personalized connection request note.
Requirements:
- Professional and warm tone
- Reference their role/company
- Mention a genuine reason to connect
- Max 300 characters (LinkedIn limit)
- NO greetings like "Hi [Name]" - just the core message
- NO placeholders like [Your Name] or [Your Company]"""
        
        user_prompt = f"""Write a personalized LinkedIn connection note for:

Name: {prospect.get('full_name', 'this person')}
Title: {prospect.get('title', 'Unknown')}
Company: {prospect.get('company', 'Unknown')}

Generate a warm, professional note (max 300 chars)."""
    
    # Call appropriate provider
    if provider == "anthropic":
        note = await _call_anthropic(client, api_key, model, system_prompt, user_prompt)
    elif provider == "openai":
        note = await _call_openai(client, api_key, model, system_prompt, user_prompt)
    elif provider == "google":
        note = await _call_google(client, api_key, model, system_prompt, user_prompt)
    else:
        raise ValueError(f"Unknown LLM provider: {provider}")
    
    # Trim to 300 chars (LinkedIn limit)
    return note.strip()[:300]


async def _call_anthropic(
    client: httpx.AsyncClient,
    api_key: str,
    model: str,
    system: str,
    user: str
) -> str:
    """Call Anthropic API."""
    try:
        response = await client.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json"
            },
            json={
                "model": model,
                "max_tokens": 300,
                "system": system,
                "messages": [{"role": "user", "content": user}]
            },
            timeout=30
        )
        
        if response.status_code != 200:
            error_detail = response.text[:200]
            if response.status_code == 401:
                raise ValueError("Invalid Anthropic API key. Please check your API key and try again.")
            elif response.status_code == 429:
                raise ValueError("Anthropic rate limit exceeded. Please try again later.")
            else:
                raise ValueError(f"Anthropic API error ({response.status_code}): {error_detail}")
        
        data = response.json()
        return data["content"][0]["text"]
    
    except httpx.TimeoutException:
        raise ValueError("Anthropic API timeout. Please try again.")
    except Exception as e:
        raise ValueError(f"Anthropic error: {str(e)}")


async def _call_openai(
    client: httpx.AsyncClient,
    api_key: str,
    model: str,
    system: str,
    user: str
) -> str:
    """Call OpenAI API."""
    try:
        response = await client.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": model,
                "max_tokens": 300,
                "temperature": 0.7,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": user}
                ]
            },
            timeout=30
        )
        
        if response.status_code != 200:
            error_detail = response.text[:200]
            if response.status_code == 401:
                raise ValueError("Invalid OpenAI API key. Please check your API key and try again.")
            elif response.status_code == 429:
                raise ValueError("OpenAI rate limit exceeded. Please try again later.")
            else:
                raise ValueError(f"OpenAI API error ({response.status_code}): {error_detail}")
        
        data = response.json()
        return data["choices"][0]["message"]["content"]
    
    except httpx.TimeoutException:
        raise ValueError("OpenAI API timeout. Please try again.")
    except Exception as e:
        raise ValueError(f"OpenAI error: {str(e)}")


async def _call_google(
    client: httpx.AsyncClient,
    api_key: str,
    model: str,
    system: str,
    user: str
) -> str:
    """Call Google Gemini API."""
    try:
        # Gemini uses a different endpoint structure
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        
        response = await client.post(
            url,
            headers={"Content-Type": "application/json"},
            json={
                "contents": [{
                    "parts": [{
                        "text": f"{system}\n\n{user}"
                    }]
                }],
                "generationConfig": {
                    "maxOutputTokens": 300,
                    "temperature": 0.7
                }
            },
            timeout=30
        )
        
        if response.status_code != 200:
            error_detail = response.text[:200]
            if response.status_code == 400:
                raise ValueError("Invalid Google API key. Please check your API key and try again.")
            elif response.status_code == 429:
                raise ValueError("Google rate limit exceeded. Please try again later.")
            else:
                raise ValueError(f"Google API error ({response.status_code}): {error_detail}")
        
        data = response.json()
        return data["candidates"][0]["content"]["parts"][0]["text"]
    
    except httpx.TimeoutException:
        raise ValueError("Google API timeout. Please try again.")
    except Exception as e:
        raise ValueError(f"Google error: {str(e)}")
