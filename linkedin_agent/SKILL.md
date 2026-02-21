# LinkedIn Agent (Marketplace API)

Generate AI-personalized LinkedIn messages for OpenClaw to execute locally.

> **Hybrid architecture:** This marketplace agent generates AI messages. OpenClaw executes browser automation locally.

## Architecture

```
User (Telegram):
  "Connect with John on LinkedIn"
         ↓
OpenClaw (local):
  1. Calls this marketplace API
  2. Gets AI-personalized message
  3. Controls local browser (user logged in)
  4. Sends connection with AI message
  5. Reports back to user
```

## What This Agent Does

**Marketplace responsibilities:**
- ✅ Generate personalized connection notes using AI
- ✅ Generate personalized messages using AI
- ✅ Support multiple LLM providers (Anthropic/OpenAI/Google)
- ✅ Return structured commands for OpenClaw

**What this agent does NOT do:**
- ❌ Control browsers (happens locally in OpenClaw)
- ❌ Authenticate to LinkedIn (uses user's local session)
- ❌ Click buttons (OpenClaw does this)

## Setup

### 1. For Marketplace Owner (Dhruvit)

**No special dependencies!** This agent only needs:
- Standard marketplace environment (httpx already included)
- No Playwright, no browsers, no cookies

**Installation:**
```bash
# Copy agent to marketplace
cp -r linkedin_agent /path/to/marketplace/app/agents/

# Reload
curl -X POST http://localhost:8000/admin/agents/reload
```

### 2. For End Users (OpenClaw)

Users need to install the OpenClaw skill (see `openclaw-skill/` directory):
- Install Playwright locally
- Login to LinkedIn in their browser once
- OpenClaw skill handles the rest

## How to Execute

**From OpenClaw:**

```bash
curl -s -X POST https://marketplacebackend-production-58c8.up.railway.app/v1/agents/linkedin-agent/execute \
  -H "Content-Type: application/json" \
  -H "X-User-LLM-Key: YOUR_LLM_API_KEY" \
  -d '{
    "prompt": "Connect with John on LinkedIn: https://linkedin.com/in/john-smith",
    "options": {
      "action": "connect",
      "personalize": true,
      "full_name": "John Smith",
      "title": "CEO",
      "company": "TechCorp"
    }
  }'
```

## Response

**SSE Stream:**

```
event: status
data: {"message": "🔗 Found LinkedIn profile: https://linkedin.com/in/john"}

event: status
data: {"message": "🤖 Generating personalized connection note..."}

event: status
data: {"message": "✅ Generated: \"Hi John! Fellow tech entrepreneur here...\""}

event: result
data: {
  "success": true,
  "action": "connect",
  "linkedin_url": "https://linkedin.com/in/john",
  "personalized_note": "Hi John! Fellow tech entrepreneur here. Love what you're building at TechCorp...",
  "openclaw_command": {
    "type": "linkedin_automation",
    "action": "connect",
    "profile_url": "https://linkedin.com/in/john",
    "note": "Hi John! Fellow tech entrepreneur here...",
    "full_name": "John Smith"
  },
  "message": "✅ Ready to send connection request with personalized note"
}
```

**OpenClaw reads `openclaw_command` and executes it locally using browser control.**

## Options

- **action** - `"connect"` or `"message"` (default: `"connect"`)
- **personalize** - `true` to use AI personalization (default: `true`)
- **full_name** - Prospect name (extracted from prompt if not provided)
- **title** - Prospect job title (for better personalization)
- **company** - Prospect company (for better personalization)
- **message_text** - Custom message or base text to personalize

## Required Environment

**For marketplace (passed per-request):**
- `LLM_API_KEY` - API key for AI personalization

**Optional:**
- `LLM_PROVIDER` - `anthropic`, `openai`, or `google` (default: `google`)
- `LLM_MODEL` - Specific model name (default: provider-specific)

## Benefits of This Architecture

**Why split marketplace (AI) + OpenClaw (browser)?**

✅ **Better security:**
- No LinkedIn credentials sent to marketplace
- User's browser session stays local
- No cookie security risks

✅ **Better reliability:**
- Uses real browser (not headless)
- Real IP address (not datacenter)
- No LinkedIn security checkpoints
- Works from any machine user is logged in

✅ **Simpler marketplace:**
- No Playwright dependencies
- No browser management
- Just AI message generation
- Easier to deploy and scale

✅ **Better UX:**
- User just logs into LinkedIn once in their browser
- No session cookie extraction needed
- No F12, no developer tools
- "It just works"

## Cost

- **Marketplace execution:** FREE (just AI generation)
- **LLM API calls:** User pays (~$0.0001-0.001 per message)
- **Google Gemini:** FREE tier available (60 req/min)

## Limitations

Respects LinkedIn's limits (enforced by OpenClaw skill):
- 100-200 connections/week
- 200-500 messages/day
- Human-like delays between actions

## For Developers

**OpenClaw skill location:** `openclaw-skill/` directory
- `SKILL.md` - OpenClaw skill documentation
- `linkedin_automation.py` - Browser automation script

The skill:
1. Calls this marketplace API
2. Gets AI message from response
3. Controls browser locally via Playwright
4. Executes LinkedIn action
5. Reports success/failure

## Troubleshooting

**"LLM_API_KEY required"**
- User needs to configure API key in OpenClaw

**Agent returns command but nothing happens**
- User needs to install OpenClaw skill
- Skill executes the `openclaw_command` from result

**Messages not personalized well**
- Provide more context in options (title, company)
- Try different LLM provider/model

## Author

Sam (@sujalmanpara)  
GitHub: https://github.com/sujalmanpara/linkedin-agent-marketplace
