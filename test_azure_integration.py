#!/usr/bin/env python3
"""
Test script to verify Azure OpenAI integration
This tests both direct Azure OpenAI calls and MCP integration
"""

import asyncio
import aiohttp
import json


async def test_azure_openai_direct():
    """Test Azure OpenAI API directly (without MCP)"""
    print("=" * 60)
    print("  TESTING AZURE OPENAI DIRECTLY")
    print("=" * 60)
    
    # Load Azure OpenAI configuration from environment
    import os
    from dotenv import load_dotenv
    load_dotenv()
    
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2025-04-01-preview")
    model = os.getenv("AZURE_OPENAI_MODEL", "gpt-5-mini")
    
    if not endpoint or not api_key:
        print("❌ Error: Azure OpenAI credentials not found in environment variables")
        print("Please create a .env file with AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_API_KEY")
        return
    
    url = f"{endpoint}?api-version={api_version}"
    headers = {
        "Content-Type": "application/json",
        "api-key": api_key
    }
    
    test_prompts = [
        "Say 'Hello, Azure OpenAI is working!'",
        "What is 2 + 2?",
        "Write a haiku about cloud computing"
    ]
    
    async with aiohttp.ClientSession() as session:
        for prompt in test_prompts:
            print(f"\nPrompt: {prompt}")
            print("-" * 40)
            
            payload = {
                "model": model,
                "input": prompt
            }
            
            try:
                async with session.post(url, headers=headers, json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        print(f"✅ Success!")
                        print(f"Response: {json.dumps(result, indent=2)[:500]}")
                    else:
                        error_text = await response.text()
                        print(f"❌ Error (Status {response.status}): {error_text[:200]}")
            except Exception as e:
                print(f"❌ Exception: {e}")
    
    print("\n" + "=" * 60)


async def test_mcp_with_azure():
    """Test MCP integration with Azure OpenAI"""
    print("\n" + "=" * 60)
    print("  TESTING MCP WITH AZURE OPENAI")
    print("=" * 60)
    
    try:
        # Import the Azure client
        from llm_integration_setup.client_azure import MCPAzureOpenAIClient
        
        # Create client
        client = MCPAzureOpenAIClient()
        
        # Connect to MCP server
        print("\n📡 Connecting to MCP server...")
        await client.connect_to_server("llm_integration_setup/server.py")
        
        # Test query
        query = "What is our company's vacation policy?"
        print(f"\n📝 Query: {query}")
        
        response = await client.process_query(query)
        print(f"\n✅ Response: {response}")
        
        # Cleanup
        await client.cleanup()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nMake sure:")
        print("  1. The MCP server script exists at llm_integration_setup/server.py")
        print("  2. The knowledge base file exists at llm_integration_setup/data/kb.json")
        print("  3. All required packages are installed (pip install -r requirements.txt)")


async def main():
    """Run all tests"""
    print("\n🚀 AZURE OPENAI INTEGRATION TEST SUITE\n")
    
    # Test 1: Direct Azure OpenAI
    await test_azure_openai_direct()
    
    # Test 2: MCP with Azure OpenAI
    await test_mcp_with_azure()
    
    print("\n✅ All tests completed!")


if __name__ == "__main__":
    # Install aiohttp if not available
    try:
        import aiohttp
    except ImportError:
        import subprocess
        import sys
        print("Installing aiohttp...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "aiohttp"])
        import aiohttp
    
    asyncio.run(main())
