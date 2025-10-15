# ML POC MCP - Azure OpenAI Testing & MCP Server

This project provides tools to test Azure OpenAI API endpoints and run an MCP (Model Context Protocol) server with calculator and Azure OpenAI integration tools.

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Install Python dependencies
pip install -r requirement.txt
```

### 2. Test Azure OpenAI API

```bash
# Run the comprehensive API test
python test_azure_openai.py
```

This will test your Azure OpenAI endpoint with multiple test cases and provide detailed diagnostics.

### 3. Run MCP Server

#### Option A: Without Node.js (Direct Python)
```bash
# Run the server directly with Python
python run_server.py
```

#### Option B: With Node.js installed
```bash
# First, install Node.js if not already installed
chmod +x setup_nodejs.sh
./setup_nodejs.sh

# Then run with MCP dev command
mcp dev server_setup/server.py
```

## 📁 Project Structure

```
ml_poc-mcp/
├── test_azure_openai.py    # Comprehensive Azure OpenAI API tester
├── run_server.py            # Direct Python MCP server runner
├── server_setup/
│   └── server.py           # MCP server with calculator & Azure tools
├── setup_nodejs.sh         # Script to install Node.js for MCP dev
└── requirement.txt         # Python dependencies
```

## 🛠️ Available MCP Tools

The MCP server provides the following tools:

### Calculator Tools
- `add(a, b)` - Add two numbers
- `multiply(a, b)` - Multiply two numbers  
- `divide(a, b)` - Divide two numbers

### Azure OpenAI Tools
- `test_azure_openai(prompt)` - Test the Azure OpenAI API with a prompt
- `get_azure_config()` - Get current Azure configuration

## 🔧 Configuration

### Environment Variables (Optional)

Create a `.env` file in the project root:

```env
# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT=https://your-endpoint.openai.azure.com/openai/responses
AZURE_OPENAI_API_KEY=your-api-key-here
AZURE_OPENAI_API_VERSION=2025-04-01-preview
AZURE_OPENAI_MODEL=gpt-5-mini

# MCP Server Configuration
MCP_SERVER_NAME=ml_poc_server
MCP_SERVER_HOST=0.0.0.0
MCP_SERVER_PORT=8050
MCP_TRANSPORT=stdio
```

If no `.env` file is provided, the scripts will use the default values configured in the code.

## 🧪 Testing the API

### Basic Test
```bash
python test_azure_openai.py
```

Expected output:
- ✅ **Status 200**: API is working correctly
- ❌ **Status 401**: Invalid or expired API key
- ❌ **Status 404**: Wrong endpoint URL
- ⚠️ **Status 429**: Rate limit exceeded

### Manual Test with curl
```bash
curl -X POST "https://oai-connect-sbx-demo.openai.azure.com/openai/responses?api-version=2025-04-01-preview" \
  -H "Content-Type: application/json" \
  -H "api-key: YOUR_API_KEY" \
  -d '{"model": "gpt-5-mini", "input": "Hello, test"}'
```

## 🐛 Troubleshooting

### "npx not found" Error
This occurs when trying to use `mcp dev` without Node.js installed. Solutions:
1. Use `python run_server.py` instead (no Node.js required)
2. Install Node.js using `./setup_nodejs.sh`

### API Connection Errors
- Check internet connection
- Verify API endpoint URL is correct
- Ensure API key is valid
- Check firewall/proxy settings

### Rate Limiting
If you encounter rate limiting (HTTP 429):
- Wait before retrying (check Retry-After header)
- Reduce request frequency
- Consider upgrading your Azure tier

## 📚 Additional Resources

- [MCP Documentation](https://modelcontextprotocol.io/)
- [Azure OpenAI Documentation](https://learn.microsoft.com/en-us/azure/ai-services/openai/)
- [FastMCP Documentation](https://github.com/jlowin/fastmcp)