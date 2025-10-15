import asyncio
import json
import os
from contextlib import AsyncExitStack
from typing import Any, Dict, List, Optional
import aiohttp

import nest_asyncio
from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Apply nest_asyncio to allow nested event loops
nest_asyncio.apply()

# Load environment variables
load_dotenv("../.env")


def extract_text_from_response(response_data):
    """Extract only the text content from Azure OpenAI response."""
    try:
        # Handle different response formats
        if isinstance(response_data, dict):
            # Check for 'output' key containing list (Azure format)
            if 'output' in response_data and isinstance(response_data['output'], list):
                for item in response_data['output']:
                    if item.get('type') == 'message' and 'content' in item:
                        for content in item['content']:
                            if content.get('type') == 'output_text':
                                return content.get('text', '')
            
            # Check for standard OpenAI format
            if 'choices' in response_data:
                return response_data['choices'][0]['message'].get('content', '')
            
            # Check for direct output string
            if 'output' in response_data and isinstance(response_data['output'], str):
                return response_data['output']
            
            # Check for content directly
            if 'content' in response_data:
                return response_data['content']
            
            # Check for text directly
            if 'text' in response_data:
                return response_data['text']
        
        elif isinstance(response_data, list):
            # Handle list response
            for item in response_data:
                if isinstance(item, dict):
                    if item.get('type') == 'message' and 'content' in item:
                        for content in item['content']:
                            if content.get('type') == 'output_text':
                                return content.get('text', '')
        
        # If we can't parse it, return error
        return "Unable to extract text from response"
    
    except Exception as e:
        return f"Error: {e}"


class MCPAzureOpenAIClient:
    """Client for interacting with Azure OpenAI models using MCP tools - Clean output version."""

    def __init__(self, 
                 endpoint: str = None,
                 api_key: str = None,
                 api_version: str = "2025-04-01-preview",
                 model: str = "gpt-5-mini"):
        """Initialize the Azure OpenAI MCP client."""
        # Load from environment variables
        self.endpoint = endpoint or os.getenv("AZURE_OPENAI_ENDPOINT")
        self.api_key = api_key or os.getenv("AZURE_OPENAI_API_KEY")
        self.api_version = api_version or os.getenv("AZURE_OPENAI_API_VERSION", "2025-04-01-preview")
        self.model = model or os.getenv("AZURE_OPENAI_MODEL", "gpt-5-mini")
        
        # Validate required configuration
        if not self.endpoint:
            raise ValueError("AZURE_OPENAI_ENDPOINT not found. Please set it in .env file")
        if not self.api_key:
            raise ValueError("AZURE_OPENAI_API_KEY not found. Please set it in .env file")
        
        # Build URL
        if "/responses" in self.endpoint:
            self.chat_url = f"{self.endpoint}?api-version={self.api_version}"
            self.use_custom_format = True
        else:
            base_url = self.endpoint.rstrip('/')
            self.chat_url = f"{base_url}/openai/deployments/{self.model}/chat/completions?api-version={self.api_version}"
            self.use_custom_format = False
        
        # Initialize session objects
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.stdio: Optional[Any] = None
        self.write: Optional[Any] = None
        self.http_session: Optional[aiohttp.ClientSession] = None

    async def connect_to_server(self, server_script_path: str = "server.py"):
        """Connect to an MCP server."""
        server_params = StdioServerParameters(
            command="python",
            args=[server_script_path],
        )

        stdio_transport = await self.exit_stack.enter_async_context(
            stdio_client(server_params)
        )
        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(
            ClientSession(self.stdio, self.write)
        )

        await self.session.initialize()
        self.http_session = aiohttp.ClientSession()

        # List available tools silently
        tools_result = await self.session.list_tools()

    async def get_mcp_tools(self) -> List[Dict[str, Any]]:
        """Get available tools from the MCP server in OpenAI format."""
        tools_result = await self.session.list_tools()
        return [
            {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.inputSchema,
                },
            }
            for tool in tools_result.tools
        ]

    async def call_azure_openai(self, messages: List[Dict[str, Any]], 
                                tools: Optional[List[Dict[str, Any]]] = None,
                                tool_choice: str = "auto") -> Dict[str, Any]:
        """Call Azure OpenAI API."""
        headers = {
            "Content-Type": "application/json",
            "api-key": self.api_key
        }
        
        if self.use_custom_format:
            if messages:
                user_message = next((msg["content"] for msg in reversed(messages) 
                                    if msg["role"] == "user"), "Hello")
            payload = {
                "model": self.model,
                "input": user_message
            }
        else:
            payload = {
                "messages": messages,
                "model": self.model,
                "temperature": 0.7,
                "max_tokens": 1000
            }
            
            if tools:
                payload["tools"] = tools
                payload["tool_choice"] = tool_choice
        
        async with self.http_session.post(self.chat_url, 
                                         headers=headers, 
                                         json=payload) as response:
            if response.status != 200:
                error_text = await response.text()
                raise Exception(f"Azure OpenAI API error: {response.status} - {error_text}")
            
            response_data = await response.json()
            return response_data

    async def process_query(self, query: str, verbose: bool = False) -> str:
        """
        Process a query using Azure OpenAI and available MCP tools.
        
        Args:
            query: The user query
            verbose: If True, show full response; if False, show only text
            
        Returns:
            The response from Azure OpenAI (text only by default)
        """
        # Get available tools
        tools = await self.get_mcp_tools()
        messages = [{"role": "user", "content": query}]
        
        try:
            # Call Azure OpenAI
            response = await self.call_azure_openai(messages, tools, "auto")
            
            if verbose:
                # Show full response for debugging
                print("\n🔍 Full Response:")
                print(json.dumps(response, indent=2))
                print("-" * 60)
            
            # Extract and return only the text
            text_response = extract_text_from_response(response)
            
            # Handle tool calls if present (for standard format)
            if not self.use_custom_format and isinstance(response, dict) and 'choices' in response:
                assistant_message = response["choices"][0]["message"]
                
                if assistant_message.get("tool_calls"):
                    messages.append(assistant_message)
                    
                    for tool_call in assistant_message["tool_calls"]:
                        # Execute tool call
                        result = await self.session.call_tool(
                            tool_call["function"]["name"],
                            arguments=json.loads(tool_call["function"]["arguments"]),
                        )
                        
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call["id"],
                            "content": result.content[0].text,
                        })
                    
                    # Get final response
                    final_response = await self.call_azure_openai(messages, tools, "none")
                    text_response = extract_text_from_response(final_response)
            
            return text_response
            
        except Exception as e:
            # Fallback to MCP tools silently
            if "vacation" in query.lower() or "policy" in query.lower():
                result = await self.session.call_tool("get_knowledge_base", arguments={})
                kb_content = result.content[0].text
                
                try:
                    enhanced_query = f"Based on this knowledge base:\n{kb_content}\n\nAnswer: {query}"
                    messages = [{"role": "user", "content": enhanced_query}]
                    response = await self.call_azure_openai(messages, None, "none")
                    return extract_text_from_response(response)
                except:
                    return kb_content
            
            return f"Error: {str(e)}"

    async def cleanup(self):
        """Clean up resources."""
        if self.http_session:
            await self.http_session.close()
        await self.exit_stack.aclose()


async def query_azure_clean(prompt: str) -> str:
    """
    Simple function to query Azure OpenAI and get ONLY the text response.
    
    Args:
        prompt: Your question or prompt
        
    Returns:
        Just the text response, nothing else
    """
    import os
    import aiohttp
    from dotenv import load_dotenv
    
    load_dotenv("../.env")
    
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2025-04-01-preview")
    model = os.getenv("AZURE_OPENAI_MODEL", "gpt-5-mini")
    
    if not endpoint or not api_key:
        return "Error: Azure credentials not found in .env file"
    
    url = f"{endpoint}?api-version={api_version}"
    headers = {
        "Content-Type": "application/json",
        "api-key": api_key
    }
    payload = {
        "model": model,
        "input": prompt
    }
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(url, headers=headers, json=payload) as response:
                if response.status == 200:
                    full_response = await response.json()
                    return extract_text_from_response(full_response)
                else:
                    return f"Error: Status {response.status}"
        except Exception as e:
            return f"Error: {e}"


async def main():
    """Main entry point with clean output."""
    client = MCPAzureOpenAIClient()
    
    try:
        # Connect to MCP server
        await client.connect_to_server("server.py")
        
        # Test queries
        queries = [
            "What is our company's vacation policy?",
            "Tell me about the available information",
        ]
        
        for query in queries:
            response = await client.process_query(query, verbose=False)
            
            # Just print the text, nothing else
            print(response)
            
            # Add a blank line between responses
            if query != queries[-1]:
                print()
        
    finally:
        await client.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
