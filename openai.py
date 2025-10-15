import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get Azure OpenAI configuration from environment
endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
api_key = os.getenv("AZURE_OPENAI_API_KEY")
api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2025-04-01-preview")
model = os.getenv("AZURE_OPENAI_MODEL", "gpt-5-mini")

if not endpoint or not api_key:
    print("Error: Azure OpenAI credentials not found!")
    print("Please ensure .env file contains AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_API_KEY")
    exit(1)

url = f"{endpoint}?api-version={api_version}"
headers = {
    "Content-Type": "application/json",
    "api-key": api_key
}
payload = {
    "model": model,
    "input": "Write a short poem about AI and learning."
}

response = requests.post(url, headers=headers, json=payload)

# Extract just the text from response
response_data = response.json()

# Handle different response formats
text_found = False

# Check if response has 'output' key (your Azure format)
if isinstance(response_data, dict) and 'output' in response_data:
    output = response_data['output']
    if isinstance(output, list):
        for item in output:
            if isinstance(item, dict) and item.get('type') == 'message':
                for content in item.get('content', []):
                    if content.get('type') == 'output_text':
                        print(content.get('text', ''))
                        text_found = True
                        break
            if text_found:
                break

# Check if response is a list (another format)
elif isinstance(response_data, list):
    for item in response_data:
        if isinstance(item, dict) and item.get('type') == 'message':
            for content in item.get('content', []):
                if content.get('type') == 'output_text':
                    print(content.get('text', ''))
                    text_found = True
                    break
        if text_found:
            break

# If no text found, print error
if not text_found:
    print("Could not extract text from response")