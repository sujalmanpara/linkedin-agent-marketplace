# LinkedIn Agent

Send personalized LinkedIn connection requests and messages using AI.

> **Marketplace agent by Sam (@sujalmanpara).** Logic runs on Nextbase servers. Your API keys are used in-memory only and never stored.

## When to Use

- User wants to send LinkedIn connection request
- User wants to send LinkedIn message to someone
- User mentions "LinkedIn", "connect with", "reach out to", etc.
- User provides a LinkedIn profile URL

## Usage Examples

**Simple connection request:**
```
Send a LinkedIn connection to https://linkedin.com/in/john-smith
```

**With context:**
```
Connect with Jane Doe on LinkedIn: https://linkedin.com/in/jane-doe
She's a SaaS founder, mention I'm also building in AI
```

**Send message (must be connected):**
```
Send a LinkedIn message to https://linkedin.com/in/alice
Message: Hey! Saw your post about AI agents, would love to chat
```

## Setup

### **Recommended: Session Cookie Authentication** ✅

**Why:** Avoids LinkedIn security checkpoints, works reliably from any server

**How to get your session cookie:**

1. **Login to LinkedIn** in your browser: https://linkedin.com
2. **Open Developer Tools:**
   - Chrome/Edge: Press `F12` or `Ctrl+Shift+I` (Windows) / `Cmd+Option+I` (Mac)
   - Firefox: Press `F12` or `Ctrl+Shift+I` (Windows) / `Cmd+Option+I` (Mac)
3. **Go to Application → Cookies → https://www.linkedin.com**
4. **Find cookie named `li_at`**
5. **Copy the Value** (starts with `AQEDAT...`)
6. **Paste into marketplace agent settings** as `LINKEDIN_SESSION_COOKIE`

**Visual guide:** [Watch 30-second video](#) _(coming soon)_

**Environment variables:**

- **LINKEDIN_SESSION_COOKIE** - Your `li_at` cookie value (recommended) ✅
- **LLM_API_KEY** - API key for AI personalization (Anthropic/OpenAI/Google)

Optional:
- **LLM_PROVIDER** - `anthropic`, `openai`, or `google` (default: `google`)
- **LLM_MODEL** - Model name (default: `gemini-2.5-flash`)

---

### **Alternative: Email/Password Authentication** ⚠️

**Warning:** May trigger LinkedIn security checkpoints requiring manual verification

- **LINKEDIN_EMAIL** - Your LinkedIn account email
- **LINKEDIN_PASSWORD** - Your LinkedIn account password
- **LLM_API_KEY** - API key for AI personalization

**Note:** If you encounter "LinkedIn security checkpoint" error, switch to session cookie method above.

## How to Execute

### **Method 1: With Session Cookie** (Recommended) ✅

```bash
curl -s -X POST https://marketplacebackend-production-58c8.up.railway.app/v1/agents/linkedin-agent/execute \
  -H "Content-Type: application/json" \
  -H "X-User-LLM-Key: YOUR_LLM_API_KEY" \
  -H "X-Key-LINKEDIN_SESSION_COOKIE: AQEDATg..." \
  -d '{
    "prompt": "Send connection to https://linkedin.com/in/john-smith",
    "language": "en",
    "options": {
      "action": "connect",
      "personalize": true,
      "full_name": "John Smith"
    }
  }'
```

### **Method 2: With Email/Password** (May trigger security checkpoint) ⚠️

```bash
curl -s -X POST https://marketplacebackend-production-58c8.up.railway.app/v1/agents/linkedin-agent/execute \
  -H "Content-Type: application/json" \
  -H "X-User-LLM-Key: YOUR_LLM_API_KEY" \
  -H "X-Key-LINKEDIN_EMAIL: your@email.com" \
  -H "X-Key-LINKEDIN_PASSWORD: your_password" \
  -d '{
    "prompt": "Send connection to https://linkedin.com/in/john-smith",
    "language": "en",
    "options": {
      "action": "connect",
      "personalize": true,
      "full_name": "John Smith"
    }
  }'
```

## Response (SSE Stream)

The agent streams events as it works:

| Event | Meaning |
|-------|---------|
| `event: status` | Progress update — display to user |
| `event: result` | Final output — return as answer |
| `event: error` | Something went wrong |

**Example stream:**

```
event: status
data: {"message": "🔗 Found LinkedIn profile: https://linkedin.com/in/john"}

event: status
data: {"message": "🤖 Generating personalized connection note..."}

event: status
data: {"message": "📤 Sending LinkedIn connection request..."}

event: result
data: {"success": true, "action": "connect", "personalized_note": "Hi John! Noticed we're both building AI tools...", "message": "✅ Connection request sent to John Smith"}
```

## Options

Pass these in the `options` field of the request:

- **action** - `"connect"` or `"message"` (default: `"connect"`)
- **personalize** - `true` to use AI personalization (default: `true`)
- **full_name** - Prospect name (optional, extracted from prompt if not provided)
- **title** - Prospect job title (optional)
- **company** - Prospect company (optional)
- **message_text** - Message to send (required for `action: "message"`)

## Limitations

- **LinkedIn rate limits**: ~100 connections/week, ~200 messages/day (LinkedIn's limits)
- **Connection note**: Max 300 characters (LinkedIn limit)
- **Automation timeout**: 90 seconds max per request
- **Must be logged in**: Requires valid LinkedIn credentials
- **Already connected**: Will fail if connection request already sent

## Security Notes

- Credentials are NEVER stored by the agent
- Each request receives credentials fresh from marketplace
- Agent is stateless (forgets everything after request completes)
- Use strong LinkedIn password and 2FA on your account

## Troubleshooting

**"LinkedIn security checkpoint detected"** ⚠️
- You're using email/password authentication
- **Solution**: Switch to session cookie authentication (see Setup above)
- LinkedIn blocks automated logins from new locations

**"Session cookie expired or invalid"**
- Your `li_at` cookie has expired (happens every 30-90 days)
- **Solution**: Get a fresh cookie (repeat setup steps)
- Make sure you copied the full cookie value

**"Connect button not found"**
- Profile may be private or not accepting connections
- Already connected with this person
- Check profile URL is correct

**"Message button not found"**
- You're not connected yet (send connection first)
- Profile doesn't allow messages

**"LinkedIn automation timeout"**
- Profile took >90s to load
- LinkedIn may be slow, try again

**"Invalid [Provider] API key"**
- Check LLM_API_KEY is correct
- Ensure provider (LLM_PROVIDER) matches the key type

## Cost

- **Agent execution**: FREE (marketplace handles compute)
- **LLM API calls**: User pays (uses their LLM_API_KEY)
  - ~$0.0001-0.001 per personalized note
  - Google Gemini has free tier (60 requests/min)

## Author

Sam (@sujalmanpara)  
GitHub: https://github.com/sujalmanpara/linkedin-agent-marketplace
