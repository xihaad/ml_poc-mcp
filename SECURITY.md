# 🔒 Security Guidelines

## API Key Security

### ✅ DO's:
1. **Store API keys in `.env` file**
   - All sensitive credentials should be in `.env`
   - Use `env.template` as a reference

2. **Load from environment variables**
   ```python
   import os
   from dotenv import load_dotenv
   
   load_dotenv()
   api_key = os.getenv("AZURE_OPENAI_API_KEY")
   ```

3. **Validate credentials exist**
   ```python
   if not api_key:
       raise ValueError("API key not found in environment variables")
   ```

### ❌ DON'Ts:
1. **NEVER hardcode API keys in source code**
   ```python
   # BAD - Never do this!
   api_key = "Tur0txFhLykkRRgv..."  # EXPOSED!
   ```

2. **NEVER commit `.env` file to version control**
   - `.env` is already in `.gitignore`
   - Double-check before committing

3. **NEVER share API keys in documentation**
   - Use placeholders like `your-api-key-here`
   - Reference `env.template` for structure

## File Security Status

| File | Status | Notes |
|------|--------|-------|
| `.env` | 🔒 Secure | Contains actual credentials, ignored by git |
| `env.template` | ✅ Safe | Template without real credentials |
| `client_azure.py` | ✅ Safe | Loads from environment variables |
| `test_azure_integration.py` | ✅ Safe | Loads from environment variables |
| `openai.py` | ✅ Safe | Loads from environment variables |

## Quick Security Check

Run this command to ensure no API keys are exposed in your code:

```bash
# Search for potential exposed keys (should return nothing)
grep -r "Tur0txFhLykkRRgv" --exclude=".env" --exclude-dir=".git" .
```

## Environment Setup

1. **First time setup**:
   ```bash
   cp env.template .env
   # Edit .env with your actual credentials
   ```

2. **Install dependencies**:
   ```bash
   pip install python-dotenv  # Required for loading .env
   pip install -r requirements.txt
   ```

3. **Test configuration**:
   ```python
   from dotenv import load_dotenv
   import os
   
   load_dotenv()
   print("API Key configured:", bool(os.getenv("AZURE_OPENAI_API_KEY")))
   ```

## If You Accidentally Exposed Keys

If you accidentally committed API keys:

1. **Immediately revoke/regenerate the exposed keys** in Azure Portal
2. Remove the commit from history (if not pushed)
3. Update `.env` with new credentials
4. Never use the exposed keys again

## Best Practices

1. **Rotate API keys regularly**
2. **Use different keys for development/production**
3. **Limit API key permissions** to minimum required
4. **Monitor API key usage** in Azure Portal
5. **Use Azure Key Vault** for production deployments
