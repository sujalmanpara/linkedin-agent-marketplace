# LinkedIn Agent for Nextbase Marketplace

AI-powered LinkedIn automation agent. Send personalized connection requests and messages using Anthropic, OpenAI, or Google Gemini.

---

## 📦 **Installation (for Dhruvit)**

### **Step 1: Copy to Marketplace**

```bash
# Copy entire folder to your marketplace agents directory
cp -r linkedin_agent /path/to/marketplace/app/agents/
```

### **Step 2: Install Dependencies**

Add to `requirements.txt`:

```txt
playwright==1.45.0
```

Then install Playwright browsers:

```bash
pip install playwright
python -m playwright install chromium
```

### **Step 3: Reload Agents**

```bash
# Local development
curl -X POST http://localhost:8000/admin/agents/reload

# Production (requires admin secret)
curl -s -X POST https://marketplacebackend-production-58c8.up.railway.app/admin/agents/reload \
  -H "X-Admin-Secret: YOUR_ADMIN_SECRET"
```

No server restart needed — hot reload!

---

## ✅ **Verification**

### **Check Agent is Loaded**

```bash
curl https://marketplacebackend-production-58c8.up.railway.app/marketplace/agents | jq '.[] | select(.id=="linkedin-agent")'
```

Expected output:

```json
{
  "id": "linkedin-agent",
  "name": "LinkedIn Automation Agent",
  "description": "Send personalized LinkedIn connection requests and messages using AI...",
  "version": "2.0.0",
  "enabled": true,
  "requiredEnv": ["LINKEDIN_EMAIL", "LINKEDIN_PASSWORD", "LLM_API_KEY"],
  "tags": ["linkedin", "outreach", "automation", "ai-personalization"]
}
```

---

## 🧪 **Test the Agent**

**Local testing (after integration):**
```bash
curl -X POST http://localhost:8000/v1/agents/linkedin-agent/execute \
  -H "X-User-LLM-Key: YOUR_GEMINI_KEY" \
  -H "X-Key-LINKEDIN_EMAIL: your@email.com" \
  -H "X-Key-LINKEDIN_PASSWORD: your_password" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Send connection to https://linkedin.com/in/test-profile",
    "language": "en",
    "options": {
      "action": "connect",
      "personalize": true,
      "full_name": "Test Person"
    }
  }'
```

**Production (once deployed):**
```bash
curl -s -X POST https://marketplacebackend-production-58c8.up.railway.app/v1/agents/linkedin-agent/execute \
  -H "Content-Type: application/json" \
  -H "X-User-LLM-Key: YOUR_GEMINI_KEY" \
  -H "X-Key-LINKEDIN_EMAIL: your@email.com" \
  -H "X-Key-LINKEDIN_PASSWORD: your_password" \
  -d '{
    "prompt": "Send connection to https://linkedin.com/in/test-profile",
    "options": {"action": "connect", "personalize": true}
  }'
```

Expected SSE stream:

```
event: status
data: {"message": "🔗 Found LinkedIn profile: https://linkedin.com/in/test-profile"}

event: status
data: {"message": "🤖 Generating personalized connection note..."}

event: result
data: {"success": true, "action": "connect", ...}
```

---

## 📂 **File Structure**

```
linkedin_agent/
├── manifest.json           # Agent metadata
├── executor.py             # Main entry point
├── SKILL.md               # OpenClaw documentation
├── linkedin_service.py    # Playwright automation
├── llm_service.py         # AI personalization (3 providers)
└── README.md              # This file
```

---

## 🔧 **Dependencies**

**Python packages:**
- `playwright` - LinkedIn browser automation
- `httpx` - HTTP client (already in marketplace)

**Playwright browsers:**
- Chromium (headless)

**Installation:**
```bash
pip install playwright
python -m playwright install chromium
```

---

## 🎯 **Features**

✅ Send LinkedIn connection requests  
✅ Send LinkedIn messages (must be connected)  
✅ AI personalization (Anthropic/OpenAI/Google)  
✅ User-friendly error messages  
✅ 90-second timeout (no infinite hangs)  
✅ Stateless (no database needed)  
✅ Multi-LLM support (free tier available with Gemini)  

---

## 💰 **Pricing Model**

**Agent execution:** FREE (marketplace handles compute)  
**LLM API calls:** User pays (uses their own API key)

- Anthropic Claude: ~$0.0001-0.001 per note
- OpenAI GPT-4o-mini: ~$0.0001 per note
- Google Gemini: **FREE tier** (60 requests/min)

---

## 🔐 **Security**

- ✅ Credentials passed per-request (never stored by agent)
- ✅ Playwright runs in sandboxed browser
- ✅ No user data retention
- ✅ Stateless execution

**Marketplace responsibility:**
- Store user credentials (encrypted)
- Pass credentials in each request
- Handle authentication

---

## 📊 **Example Use Cases**

**Sales outreach:**
```
"Send connection to 10 SaaS founders: [URLs]"
```

**Recruiting:**
```
"Connect with senior React developers: [URLs]"
```

**Partnership:**
```
"Reach out to AI tool founders: [URLs]"
```

---

## 🐛 **Known Issues & Solutions**

**Issue:** Playwright timeout  
**Solution:** LinkedIn may be slow, retry or increase timeout in code

**Issue:** "Connect button not found"  
**Cause:** Already connected or profile private  
**Solution:** Return user-friendly error (already implemented)

**Issue:** LinkedIn CAPTCHA  
**Cause:** Too many automated actions  
**Solution:** Respect rate limits (concurrency: 2 in manifest)

---

## 🚀 **Production Deployment**

### **Docker** (if marketplace uses Docker)

Add to `Dockerfile`:

```dockerfile
# Install Playwright browsers
RUN python -m playwright install --with-deps chromium
```

### **Railway/Render**

Add build command:

```bash
pip install -r requirements.txt && python -m playwright install chromium
```

---

## 📞 **Support**

**Author:** Sam (@sujalmanpara)  
**GitHub:** https://github.com/sujalmanpara/linkedin-agent-marketplace  
**Telegram:** @Sujal_manpara  

---

## ✅ **Integration Checklist for Dhruvit**

- [ ] Copy `linkedin_agent/` to `app/agents/`
- [ ] Add `playwright==1.45.0` to `requirements.txt`
- [ ] Run `python -m playwright install chromium`
- [ ] Test with `curl` (see above)
- [ ] Verify SSE events stream correctly
- [ ] Test with real LinkedIn profile (use test account!)
- [ ] Deploy to production (Railway/Render)
- [ ] Update marketplace UI to show this agent

---

**Ready to ship!** 🎉
