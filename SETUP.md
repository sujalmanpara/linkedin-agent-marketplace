# 🚀 LinkedIn Agent - Quick Setup

## Step 1: Configure Environment Variables

**Two options:**

### **Option A: Use .env file** (Local development)
```bash
# Edit the .env file
nano .env

# Fill in your credentials:
LINKEDIN_EMAIL=your-email@example.com
LINKEDIN_PASSWORD=your-password
LLM_API_KEY=your-gemini-key
```

### **Option B: Use headers** (Marketplace integration)
```bash
# Pass credentials via HTTP headers
curl -X POST .../execute \
  -H "X-Key-LINKEDIN_EMAIL: your@email.com" \
  -H "X-Key-LINKEDIN_PASSWORD: password" \
  -H "X-User-LLM-Key: gemini-key"
```

---

## Step 2: Get API Keys

### **Google Gemini (Recommended - FREE tier!)**
1. Go to: https://aistudio.google.com/app/apikey
2. Click "Create API Key"
3. Copy key → paste in `.env` as `LLM_API_KEY`
4. Set `LLM_PROVIDER=google`

**Free tier:** 60 requests/minute ✅

### **Anthropic Claude** (Optional)
1. Go to: https://console.anthropic.com/
2. Create account → get API key
3. Cost: ~$0.001 per connection note

### **OpenAI GPT** (Optional)
1. Go to: https://platform.openai.com/api-keys
2. Create account → get API key
3. Cost: ~$0.0001 per connection note

---

## Step 3: Test Locally (Optional)

If testing outside marketplace:

```bash
# Install dependencies
pip install playwright httpx

# Install browser
python -m playwright install chromium

# Test
python test_agent.py
```

---

## Step 4: Deploy to Marketplace

**For Dhruvit (marketplace owner):**
1. Copy `linkedin_agent/` to `app/agents/`
2. Add `playwright==1.45.0` to requirements.txt
3. Install: `python -m playwright install chromium`
4. Reload: `curl -X POST .../admin/agents/reload`

**For users (via OpenClaw):**
1. Set environment variables in OpenClaw
2. Agent auto-discovered from marketplace
3. Just say: "Send LinkedIn connection to [URL]"

---

## Security Notes ⚠️

✅ **DO:**
- Use strong, unique LinkedIn password
- Enable 2FA on LinkedIn account
- Keep credentials in `.env` (never commit to Git!)
- Test with a separate test LinkedIn account first

❌ **DON'T:**
- Use your main LinkedIn account for testing
- Share credentials with anyone
- Commit `.env` to Git (it's in `.gitignore`)
- Send 100+ connections/day (respect LinkedIn limits)

---

## Troubleshooting

**"LinkedIn credentials missing"**
→ Check `.env` file has `LINKEDIN_EMAIL` and `LINKEDIN_PASSWORD`

**"Invalid Google API key"**
→ Verify key is correct, no extra spaces

**"Connect button not found"**
→ Already connected or profile is private

**"Timeout error"**
→ LinkedIn slow to load, try again

---

## Support

**Author:** Sam (@sujalmanpara)  
**GitHub:** https://github.com/sujalmanpara/linkedin-agent-marketplace  
**Telegram:** @Sujal_manpara

---

**Ready to go! 🎉**
