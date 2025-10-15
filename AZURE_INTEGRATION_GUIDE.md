# Azure OpenAI Integration with MCP

This guide shows how to use Azure OpenAI (GPT-5) with your MCP server.

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Test Azure OpenAI Connection

```bash
python test_azure_integration.py
```

This will test:
- Direct Azure OpenAI API calls
- MCP server integration with Azure OpenAI

### 3. Run the Azure-Integrated Client

```bash
cd llm_integration_setup
python client_azure.py
```

## 📁 File Structure

```
llm_integration_setup/
├── client_azure.py      # Azure OpenAI integrated MCP client
├── client.py            # Original OpenAI client (requires API key)
├── server.py            # MCP server with knowledge base tool
└── data/
    └── kb.json          # Knowledge base data
```

## 🔧 Configuration

### Setting Up Credentials (IMPORTANT!)

1. **Create .env file** (if not already created):
   ```bash
   cp env.template .env
   ```

2. **Edit .env file** and add your Azure OpenAI credentials:
   ```env
   AZURE_OPENAI_ENDPOINT=https://oai-connect-sbx-demo.openai.azure.com/openai/responses
   AZURE_OPENAI_API_KEY=your-actual-api-key-here
   AZURE_OPENAI_API_VERSION=2025-04-01-preview
   AZURE_OPENAI_MODEL=gpt-5-mini
   ```

3. **IMPORTANT Security Notes**:
   - ⚠️ **NEVER** commit the `.env` file to version control
   - ✅ The `.env` file is already in `.gitignore`
   - 🔒 Keep your API keys secret and secure
   - 📝 Use `env.template` as a reference for required variables

## 📝 How It Works

1. **MCP Server** (`server.py`): Provides tools to access the knowledge base
2. **Azure Client** (`client_azure.py`): 
   - Connects to the MCP server
   - Sends queries to Azure OpenAI
   - Uses MCP tools when needed
   - Returns AI-generated responses

## 🎯 Usage Examples

### Basic Usage

```python
from llm_integration_setup.client_azure import MCPAzureOpenAIClient

async def example():
    # Create client
    client = MCPAzureOpenAIClient()
    
    # Connect to MCP server
    await client.connect_to_server("server.py")
    
    # Process a query
    response = await client.process_query("What is our vacation policy?")
    print(response)
    
    # Cleanup
    await client.cleanup()
```

### Custom Configuration

```python
client = MCPAzureOpenAIClient(
    endpoint="https://your-resource.openai.azure.com/openai/responses",
    api_key="your-api-key",
    model="gpt-5-mini"
)
```

## 🧪 Testing

### Test Direct Azure OpenAI

```python
import requests

url = "https://oai-connect-sbx-demo.openai.azure.com/openai/responses?api-version=2025-04-01-preview"
headers = {
    "Content-Type": "application/json",
    "api-key": "YOUR_API_KEY"
}
payload = {
    "model": "gpt-5-mini",
    "input": "Hello, Azure!"
}

response = requests.post(url, headers=headers, json=payload)
print(response.json())
```

### Test with MCP Tools

```bash
# Terminal 1: Start the MCP server
cd llm_integration_setup
python server.py

# Terminal 2: Run the client
python client_azure.py
```

## 🐛 Troubleshooting

### Connection Errors
- Verify the API key is correct
- Check if the endpoint URL is accessible
- Ensure you're on the company network/VPN if required

### MCP Server Issues
- Make sure the server.py is running
- Check that the knowledge base file exists at `data/kb.json`
- Verify all Python packages are installed

### Azure OpenAI Errors
- **401 Unauthorized**: API key is invalid
- **404 Not Found**: Endpoint URL or model name is incorrect
- **429 Too Many Requests**: Rate limit exceeded, wait and retry

## 🔄 Switching Between OpenAI and Azure OpenAI

If you have both Azure OpenAI and standard OpenAI access:

1. **Use Azure OpenAI** (your current setup):
   ```python
   from llm_integration_setup.client_azure import MCPAzureOpenAIClient
   client = MCPAzureOpenAIClient()
   ```

2. **Use Standard OpenAI** (requires API key):
   ```python
   from llm_integration_setup.client import MCPOpenAIClient
   client = MCPOpenAIClient(model="gpt-4o")
   ```

## 📚 Additional Notes

- The Azure endpoint format (`/openai/responses`) appears to be a custom format
- Standard Azure OpenAI uses `/openai/deployments/{model}/chat/completions`
- The client handles both formats automatically
- Tool calling may not work with the custom format, but direct queries will
