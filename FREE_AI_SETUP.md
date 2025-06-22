# 🆓 Free AI API Setup Guide

This guide shows you how to set up free AI services as alternatives to OpenAI when you hit rate limits.

## 🚀 Quick Start - Ollama (Recommended)

**Ollama** is completely free and runs locally on your machine. No API keys needed!

### 1. Install Ollama

**macOS:**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

**Linux:**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

**Windows:**
Download from https://ollama.ai/download

### 2. Download a Model

```bash
# Download Llama 2 (recommended for general use)
ollama pull llama2

# Or try other models:
ollama pull mistral    # Fast and good quality
ollama pull codellama  # Great for coding
ollama pull phi        # Lightweight and fast
```

### 3. Configure Your App

Update your `.env` file:
```env
AI_SERVICE=ollama
OLLAMA_MODEL=llama2
```

### 4. Start Ollama

```bash
ollama serve
```

### 5. Test Your Setup

```bash
# Test Ollama directly
ollama run llama2 "Hello, how are you?"

# Start your AI agent
cd server && python main.py
```

## 🌐 Alternative Free Services

### Option 1: Hugging Face Inference API

1. **Get Free API Key:**
   - Go to https://huggingface.co/
   - Create account
   - Go to Settings → Access Tokens
   - Create new token

2. **Configure:**
   ```env
   AI_SERVICE=huggingface
   HUGGINGFACE_API_KEY=your-token-here
   ```

### Option 2: Google Gemini (Free Tier)

1. **Get API Key:**
   - Go to https://makersuite.google.com/app/apikey
   - Create free account
   - Generate API key

2. **Add to server/main.py:**
   ```python
   # Add this function to main.py
   async def get_gemini_response(user_message: str) -> str:
       GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
       if not GEMINI_API_KEY:
           raise Exception("Gemini API key not configured")
           
       async with httpx.AsyncClient() as http_client:
           response = await http_client.post(
               f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GEMINI_API_KEY}",
               json={
                   "contents": [{"parts": [{"text": user_message}]}]
               },
               timeout=30.0
           )
           
           if response.status_code == 200:
               result = response.json()
               return result["candidates"][0]["content"]["parts"][0]["text"]
           else:
               raise Exception(f"Gemini API error: {response.status_code}")
   ```

3. **Configure:**
   ```env
   AI_SERVICE=gemini
   GEMINI_API_KEY=your-api-key-here
   ```

### Option 3: Anthropic Claude (Free Tier)

1. **Get API Key:**
   - Go to https://console.anthropic.com/
   - Create account
   - Generate API key

2. **Add to server/main.py:**
   ```python
   # Add this function to main.py
   async def get_claude_response(user_message: str) -> str:
       CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY", "")
       if not CLAUDE_API_KEY:
           raise Exception("Claude API key not configured")
           
       async with httpx.AsyncClient() as http_client:
           response = await http_client.post(
               "https://api.anthropic.com/v1/messages",
               headers={
                   "x-api-key": CLAUDE_API_KEY,
                   "anthropic-version": "2023-06-01",
                   "content-type": "application/json"
               },
               json={
                   "model": "claude-3-haiku-20240307",
                   "max_tokens": 500,
                   "messages": [{"role": "user", "content": user_message}]
               },
               timeout=30.0
           )
           
           if response.status_code == 200:
               result = response.json()
               return result["content"][0]["text"]
           else:
               raise Exception(f"Claude API error: {response.status_code}")
   ```

3. **Configure:**
   ```env
   AI_SERVICE=claude
   CLAUDE_API_KEY=your-api-key-here
   ```

## 📊 Service Comparison

| Service | Cost | Setup | Quality | Speed | Offline |
|---------|------|-------|---------|-------|---------|
| **Ollama** | 🆓 Free | ⭐ Easy | ⭐⭐⭐⭐ | ⭐⭐⭐ | ✅ Yes |
| Hugging Face | 🆓 Free tier | ⭐⭐ Medium | ⭐⭐⭐ | ⭐⭐ | ❌ No |
| Google Gemini | 🆓 Free tier | ⭐⭐ Medium | ⭐⭐⭐⭐ | ⭐⭐⭐ | ❌ No |
| Anthropic Claude | 🆓 Free tier | ⭐⭐ Medium | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ❌ No |
| OpenAI | 💰 Paid | ⭐ Easy | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ❌ No |

## 🎯 Recommended Setup

**For beginners:** Use **Ollama** - it's completely free, runs locally, and requires no API keys.

**For production:** Use **Google Gemini** or **Anthropic Claude** - they have generous free tiers and excellent quality.

## 🔧 Troubleshooting

### Ollama Issues

**Model not found:**
```bash
# List available models
ollama list

# Pull the model again
ollama pull llama2
```

**Server not running:**
```bash
# Start Ollama server
ollama serve

# Check if it's running
curl http://localhost:11434/api/tags
```

### API Key Issues

**Invalid API key:**
- Double-check your API key
- Make sure there are no extra spaces
- Verify the service is enabled in your account

**Rate limits:**
- Most free services have rate limits
- Consider using Ollama for unlimited usage

## 🚀 Next Steps

1. Choose your preferred free AI service
2. Follow the setup instructions above
3. Update your `.env` file
4. Restart your server
5. Test the chat functionality

Your AI agent will now work without any rate limits! 🎉 