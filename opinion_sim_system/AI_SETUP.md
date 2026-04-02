# 🔑 AI Configuration for CSPOPS

## Add to your `.env` file:

```bash
# DeepSeek API (Recommended - Cheaper)
# Get key from: https://platform.deepseek.com/
DEEPSEEK_API_KEY=sk_your_deepseek_key_here
DEEPSEEK_MODEL=deepseek-chat

# OpenRouter API (Alternative - More models)
# Get key from: https://openrouter.ai/
OPENROUTER_API_KEY=sk_or_your_openrouter_key_here
OPENROUTER_MODEL=deepseek/deepseek-chat

# Use OpenRouter instead of DeepSeek direct (true/false)
USE_OPENROUTER=false
```

## 📊 API Pricing (as of 2026)

| Provider | Model | Input Price | Output Price | Speed |
|----------|-------|-------------|--------------|-------|
| **DeepSeek** | deepseek-chat | $0.27/1M tokens | $1.10/1M tokens | Fast |
| **OpenRouter** | deepseek-chat | $0.27/1M tokens | $1.10/1M tokens | Fast |
| **OpenRouter** | gpt-4o | $2.50/1M tokens | $10.00/1M tokens | Fast |
| **OpenRouter** | claude-3.5-sonnet | $3.00/1M tokens | $15.00/1M tokens | Fast |

**Recommended:** DeepSeek direct (cheapest, good quality)

## 🚀 Setup Steps

### Option 1: DeepSeek Direct (Recommended)
1. Go to https://platform.deepseek.com/
2. Sign up / Log in
3. Create API key
4. Add to `.env`:
   ```
   DEEPSEEK_API_KEY=sk_your_key_here
   USE_OPENROUTER=false
   ```

### Option 2: OpenRouter (More Models)
1. Go to https://openrouter.ai/
2. Sign up / Log in
3. Create API key
4. Add to `.env`:
   ```
   OPENROUTER_API_KEY=sk_or_your_key_here
   USE_OPENROUTER=true
   ```

## 💡 Usage Examples

### In Chat:
```
User: "What does DGS10 mean?"
AI: "DGS10 is the 10-Year Treasury Rate..."
```

### Generate Summary:
```python
chatbot = AIChatbot(config)
summary = chatbot.generate_summary(dashboard_data)
```

### Explain Indicator:
```python
explanation = chatbot.explain_indicator("DGS10")
# Returns: "**DGS10**\n\n10-Year Treasury Rate..."
```

## 🔒 Security Notes
- API keys stored in `.env` (gitignored)
- Keys never exposed to frontend
- All API calls server-side
- Suitable for government use
