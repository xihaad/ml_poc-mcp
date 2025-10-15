#!/usr/bin/env python3
"""
Simple Azure OpenAI Query Tool - Clean Text Output Only
Usage: python azure_query.py "Your question here"
"""

import os
import sys
import json
import asyncio
import aiohttp
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def extract_text_only(response_data):
    """Extract only the text from Azure OpenAI response."""
    
    # Handle list format (like your example)
    if isinstance(response_data, list):
        for item in response_data:
            if isinstance(item, dict) and item.get('type') == 'message':
                for content in item.get('content', []):
                    if content.get('type') == 'output_text':
                        return content.get('text', '')
    
    # Handle dict format
    elif isinstance(response_data, dict):
        # Standard OpenAI format
        if 'choices' in response_data:
            return response_data['choices'][0]['message'].get('content', '')
        
        # Custom formats
        if 'output' in response_data:
            return response_data['output']
        if 'content' in response_data:
            return response_data['content']
        if 'text' in response_data:
            return response_data['text']
    
    return "Could not extract text from response"


async def query_azure(prompt: str, show_raw: bool = False):
    """Query Azure OpenAI and return clean text."""
    
    # Load configuration
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2025-04-01-preview")
    model = os.getenv("AZURE_OPENAI_MODEL", "gpt-5-mini")
    
    if not endpoint or not api_key:
        return "❌ Error: Azure credentials not found in .env file"
    
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
                    
                    if show_raw:
                        print("\n🔍 Raw Response:")
                        print("-" * 60)
                        print(json.dumps(full_response, indent=2))
                        print("-" * 60)
                    
                    # Return only the text
                    return extract_text_only(full_response)
                else:
                    error_text = await response.text()
                    return f"❌ API Error ({response.status}): {error_text[:200]}"
                    
        except Exception as e:
            return f"❌ Exception: {e}"


async def main():
    """Main entry point."""
    
    # Check for command line argument
    if len(sys.argv) > 1:
        # Use command line input
        prompt = " ".join(sys.argv[1:])
        show_raw = "--raw" in sys.argv
        if show_raw:
            prompt = prompt.replace("--raw", "").strip()
    else:
        # Interactive mode
        print("=" * 60)
        print("  Azure OpenAI Query Tool (Clean Output)")
        print("=" * 60)
        print("\nEnter your question (or 'quit' to exit)")
        print("Add --raw to see full response\n")
        
        prompt = input("📝 Your question: ").strip()
        if prompt.lower() == 'quit':
            return
        
        show_raw = "--raw" in prompt
        if show_raw:
            prompt = prompt.replace("--raw", "").strip()
    
    # Query Azure OpenAI
    print("\n⏳ Querying Azure OpenAI...")
    result = await query_azure(prompt, show_raw)
    
    # Display clean result
    print("\n✅ Response:")
    print("=" * 60)
    print(result)
    print("=" * 60)
    
    # Option to continue in interactive mode
    if len(sys.argv) <= 1:
        print("\nPress Enter to ask another question or type 'quit' to exit")
        next_action = input().strip()
        if next_action.lower() != 'quit':
            await main()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nExiting...")
    except Exception as e:
        print(f"Error: {e}")
