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

# Apply nest_asyncio to allow nested event loops (needed for Jupyter/IPython)
nest_asyncio.apply()

# Load environment variables
load_dotenv("../.env")


class MCPAzureOpenAIClient:
    """Client for interacting with Azure OpenAI models using MCP tools."""

    def __init__(self, 
                 endpoint: str = None,
                 api_key: str = None,
                 api_version: str = "2025-04-01-preview",
                 model: str = "gpt-5-mini"):
        """Initialize the Azure OpenAI MCP client.

        Args:
            endpoint: Azure OpenAI endpoint URL
            api_key: Azure OpenAI API key
            api_version: API version
            model: The model deployment name
        """
        # Azure OpenAI configuration - Load from environment variables
        self.endpoint = endpoint or os.getenv("AZURE_OPENAI_ENDPOINT")
        self.api_key = api_key or os.getenv("AZURE_OPENAI_API_KEY")
        self.api_version = api_version or os.getenv("AZURE_OPENAI_API_VERSION", "2025-04-01-preview")
        self.model = model or os.getenv("AZURE_OPENAI_MODEL", "gpt-5-mini")
        
        # Validate required configuration
        if not self.endpoint:
            raise ValueError("AZURE_OPENAI_ENDPOINT not found in environment variables. Please set it in .env file")
        if not self.api_key:
            raise ValueError("AZURE_OPENAI_API_KEY not found in environment variables. Please set it in .env file")
        
        # Build the full URL for chat completions
        # Note: Azure OpenAI uses different URL patterns
        # Standard pattern: https://{resource}.openai.azure.com/openai/deployments/{deployment}/chat/completions
        # Your pattern appears to be: https://{resource}/openai/responses
        
        # For standard Azure OpenAI chat endpoint
        if "/responses" in self.endpoint:
            # Custom endpoint pattern (as provided by your manager)
            self.chat_url = f"{self.endpoint}?api-version={self.api_version}"
            self.use_custom_format = True
        else:
            # Standard Azure OpenAI pattern
            base_url = self.endpoint.rstrip('/')
            self.chat_url = f"{base_url}/openai/deployments/{self.model}/chat/completions?api-version={self.api_version}"
            self.use_custom_format = False
        
        # Initialize session and client objects
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.stdio: Optional[Any] = None
        self.write: Optional[Any] = None
        self.http_session: Optional[aiohttp.ClientSession] = None

    async def connect_to_server(self, server_script_path: str = "server.py"):
        """Connect to an MCP server.

        Args:
            server_script_path: Path to the server script.
        """
        # Server configuration
        server_params = StdioServerParameters(
            command="python",
            args=[server_script_path],
        )

        # Connect to the server
        stdio_transport = await self.exit_stack.enter_async_context(
            stdio_client(server_params)
        )
        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(
            ClientSession(self.stdio, self.write)
        )

        # Initialize the connection
        await self.session.initialize()
        
        # Initialize HTTP session for Azure OpenAI
        self.http_session = aiohttp.ClientSession()

        # List available tools
        tools_result = await self.session.list_tools()
        print("\nConnected to MCP server with tools:")
        for tool in tools_result.tools:
            print(f"  - {tool.name}: {tool.description}")
        
        print(f"\nUsing Azure OpenAI:")
        print(f"  - Endpoint: {self.endpoint}")
        print(f"  - Model: {self.model}")
        print(f"  - API Version: {self.api_version}")

    async def get_mcp_tools(self) -> List[Dict[str, Any]]:
        """Get available tools from the MCP server in OpenAI format.

        Returns:
            A list of tools in OpenAI format.
        """
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
        """Call Azure OpenAI API.
        
        Args:
            messages: List of message dictionaries
            tools: Optional list of tools in OpenAI format
            tool_choice: Tool choice strategy
            
        Returns:
            Response from Azure OpenAI
        """
        headers = {
            "Content-Type": "application/json",
            "api-key": self.api_key
        }
        
        if self.use_custom_format:
            # Use the custom format from your manager's code
            # This appears to be a simplified format
            if messages:
                # Extract the last user message for the simple format
                user_message = next((msg["content"] for msg in reversed(messages) 
                                    if msg["role"] == "user"), "Hello")
            payload = {
                "model": self.model,
                "input": user_message
            }
        else:
            # Standard Azure OpenAI chat format
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
            
            # Handle custom format response
            if self.use_custom_format:
                # Convert custom format to standard format
                return {
                    "choices": [{
                        "message": {
                            "role": "assistant",
                            "content": response_data.get("output", str(response_data))
                        }
                    }]
                }
            
            return response_data

    async def process_query(self, query: str) -> str:
        """Process a query using Azure OpenAI and available MCP tools.

        Args:
            query: The user query.

        Returns:
            The response from Azure OpenAI.
        """
        # Get available tools
        tools = await self.get_mcp_tools()
        
        # Initialize messages
        messages = [{"role": "user", "content": query}]
        
        try:
            # Initial Azure OpenAI API call
            response = await self.call_azure_openai(messages, tools, "auto")
            
            # Get assistant's response
            assistant_message = response["choices"][0]["message"]
            messages.append(assistant_message)
            
            # Handle tool calls if present (only for standard format)
            if not self.use_custom_format and assistant_message.get("tool_calls"):
                # Process each tool call
                for tool_call in assistant_message["tool_calls"]:
                    # Execute tool call
                    result = await self.session.call_tool(
                        tool_call["function"]["name"],
                        arguments=json.loads(tool_call["function"]["arguments"]),
                    )
                    
                    # Add tool response to conversation
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call["id"],
                        "content": result.content[0].text,
                    })
                
                # Get final response from Azure OpenAI with tool results
                final_response = await self.call_azure_openai(
                    messages, tools, "none"
                )
                
                return final_response["choices"][0]["message"]["content"]
            
            # No tool calls or custom format, return the direct response
            return assistant_message.get("content", "")
            
        except Exception as e:
            # If Azure OpenAI fails, try to use MCP tools directly
            print(f"Azure OpenAI error: {e}")
            print("Attempting to use MCP tools directly...")
            
            # Check if the query is about knowledge base
            if "vacation" in query.lower() or "policy" in query.lower() or "knowledge" in query.lower():
                # Call the get_knowledge_base tool directly
                result = await self.session.call_tool("get_knowledge_base", arguments={})
                kb_content = result.content[0].text
                
                # Try Azure OpenAI again with the knowledge base content
                enhanced_query = f"Based on this knowledge base:\n{kb_content}\n\nAnswer this question: {query}"
                messages = [{"role": "user", "content": enhanced_query}]
                
                try:
                    response = await self.call_azure_openai(messages, None, "none")
                    return response["choices"][0]["message"]["content"]
                except:
                    # If still fails, return the raw knowledge base
                    return f"Here's the relevant information from our knowledge base:\n\n{kb_content}"
            
            return f"Error processing query: {str(e)}"

    async def cleanup(self):
        """Clean up resources."""
        if self.http_session:
            await self.http_session.close()
        await self.exit_stack.aclose()


async def main():
    """Main entry point for the client."""
    # Initialize client with Azure OpenAI
    client = MCPAzureOpenAIClient()
    
    try:
        # Connect to MCP server
        await client.connect_to_server("server.py")
        
        # Test queries
        queries = [
            "What is our company's vacation policy?",
            "Tell me about the knowledge base",
            "What information do you have available?"
        ]
        
        for query in queries:
            print(f"\n{'='*60}")
            print(f"Query: {query}")
            print(f"{'='*60}")
            
            response = await client.process_query(query)
            print(f"\nResponse: {response}")
        
    finally:
        await client.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
