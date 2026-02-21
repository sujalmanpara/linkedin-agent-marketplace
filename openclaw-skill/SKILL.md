# LinkedIn Automation Skill

AI-powered LinkedIn automation using marketplace AI + local browser control.

## How It Works

```
User (Telegram): "Connect with John on LinkedIn"
         ↓
OpenClaw (reads this SKILL.md)
         ↓
Calls marketplace API → Get AI personalized message
         ↓
Controls local browser (user already logged in)
         ↓
Sends connection with AI message
         ↓
Reports back to user
```

## Setup

### 1. Install Playwright

```bash
pip install playwright
python -m playwright install chromium
```

### 2. Login to LinkedIn

Just login to LinkedIn in your regular browser once. The skill will use your existing session.

### 3. Configure LLM API Key

Set your LLM API key in OpenClaw config or environment:
- `LLM_API_KEY` - API key for Anthropic/OpenAI/Google (required)
- `LLM_PROVIDER` - `anthropic`, `openai`, or `google` (optional, default: google)

## Usage

**Send connection request:**
```
Connect with John Smith on LinkedIn: https://linkedin.com/in/john-smith
```

**Send message:**
```
Send LinkedIn message to https://linkedin.com/in/jane-doe
Message: Hey! Saw your post about AI, would love to chat
```

**With context for better personalization:**
```
Connect with Sarah (CEO at TechCorp) on LinkedIn: https://linkedin.com/in/sarah
Mention I'm also in SaaS
```

## How OpenClaw Executes This

When user mentions LinkedIn automation:

1. **Extract info** from user message (URL, name, context)
2. **Call marketplace** API for AI message generation
3. **Control browser** locally using Playwright
4. **Execute action** (connect/message) with AI-generated text
5. **Report result** back to user

## Security

- ✅ No credentials sent to marketplace (uses local browser session)
- ✅ All browser automation happens locally
- ✅ Marketplace only generates AI messages
- ✅ Works from any machine you're logged into LinkedIn

## Troubleshooting

**"Browser not found"**
- Run: `python -m playwright install chromium`

**"Not logged into LinkedIn"**
- Open Chrome/Brave and login to LinkedIn manually
- The skill will reuse your session

**"Connect button not found"**
- Already connected or profile is private
- Check URL is correct

## Cost

- **OpenClaw skill**: FREE (runs locally)
- **Marketplace AI**: ~$0.0001-0.001 per message (user's LLM API key)
- **Google Gemini**: FREE tier available

## Limits

Respect LinkedIn's limits:
- 100-200 connections/week
- 200-500 messages/day
- Use delays between actions (built into skill)
