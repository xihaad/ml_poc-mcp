#!/usr/bin/env python3
"""
Test Azure OpenAI with clean text-only output
"""

import os
import json
import aiohttp
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def extract_clean_text(response_data):
    """Extract only the text content from various response formats."""
    
    # If response is a dict
    if isinstance(response_data, dict):
        # Check for 'output' key containing list (Azure format)
        if 'output' in response_data and isinstance(response_data['output'], list):
            for item in response_data['output']:
                if item.get('type') == 'message' and 'content' in item:
                    for content in item.get('content', []):
                        if content.get('type') == 'output_text':
                            return content.get('text', '')
        
        # Standard OpenAI format
        if 'choices' in response_data:
            return response_data['choices'][0]['message'].get('content', '')
        
        # Direct output string
        if 'output' in response_data and isinstance(response_data['output'], str):
            return response_data['output']
        
        # Direct content
        if 'content' in response_data:
            return response_data['content']
        
        # Direct text
        if 'text' in response_data:
            return response_data['text']
    
    # If response is a list
    elif isinstance(response_data, list):
        for item in response_data:
            if isinstance(item, dict) and item.get('type') == 'message':
                for content in item.get('content', []):
                    if content.get('type') == 'output_text':
                        return content.get('text', '')
    
    # Fallback
    return "Unable to extract text"


async def test_azure_clean():
    """Test Azure OpenAI and show clean output only."""
    
    # Load configuration
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2025-04-01-preview")
    model = os.getenv("AZURE_OPENAI_MODEL", "gpt-5-mini")
    
    if not endpoint or not api_key:
        print("Error: Azure credentials not found in .env file")
        return
    
    url = f"{endpoint}?api-version={api_version}"
    headers = {
        "Content-Type": "application/json",
        "api-key": api_key
    }
    
    # Test prompts
    test_prompts = [
        "Say hello in 3 words",
        "What is 10 + 20?",
        "Write a one-line joke"
    ]
    
    async with aiohttp.ClientSession() as session:
        for prompt in test_prompts:
            payload = {
                "model": model,
                "input": prompt
            }
            
            try:
                async with session.post(url, headers=headers, json=payload) as response:
                    if response.status == 200:
                        # Get the full response
                        full_response = await response.json()
                        
                        # Extract only the text
                        text_only = extract_clean_text(full_response)
                        
                        # Just print the text, nothing else
                        print(text_only)
                        
                    else:
                        print(f"Error: Status {response.status}")
                        
            except Exception as e:
                print(f"Error: {e}")
            
            # Add blank line between responses
            if prompt != test_prompts[-1]:
                print()


def parse_response_example():
    """Parse the example response you provided."""
    
    # Your example response
    example = [
        {
            'id': 'rs_0ade0eb92db495dd0068ee1531cdc08193b6f329326518e055',
            'type': 'reasoning',
            'summary': []
        },
        {
            'id': 'msg_0ade0eb92db495dd0068ee1536ae70819393840a2f3cc50f8b',
            'type': 'message',
            'status': 'completed',
            'content': [
                {
                    'type': 'output_text',
                    'annotations': [],
                    'logprobs': [],
                    'text': '''I don't have access to your company's internal files — can you tell me which company (or upload your employee handbook/intranet link)? If you prefer, I can also search a copy you paste here and summarize.

Meanwhile, here are quick ways to find the policy yourself and what to look for, plus a ready-to-send email to HR.

Where to find your company's vacation policy
- Employee handbook (PDF or printed copy)
- HR or benefits portal / intranet
- Offer letter or employment agreement
- Payroll or time-off system (e.g., ADP, Workday, BambooHR)
- Ask your manager or HR representative

Key things the policy usually specifies (check these)
- Accrual method: accrual per pay period vs. lump sum at year start
- Accrual rate: hours/days per year (often increases with tenure)
- Eligibility: probationary period before you can take vacation
- Request/approval process: how much notice, who approves, blackout dates
- Carryover rules: whether unused days carry over and limits
- Payout on termination: whether unused vacation is paid out
- Interaction with other leave: sick leave, FMLA, holidays
- Booking restrictions: minimum increments, maximum consecutive days
- Emergencies & unpaid leave provisions

Sample email to HR (paste/modify and send)
Subject: Request for company vacation/PTO policy

Hi [HR name],

Could you please send me the current company vacation/PTO policy or point me to where it's posted? I'd like clarification on accrual rates, any probationary requirements, carryover limits, and the approval process for time off.

Thanks,
[Your name]

If you want, tell me your company name or upload the handbook and I'll extract the exact rules for you.'''
                }
            ],
            'role': 'assistant'
        }
    ]
    
    # Extract clean text
    clean_text = extract_clean_text(example)
    
    # Just print the text, nothing else
    print(clean_text)


async def main():
    """Run all tests."""
    # Test Azure OpenAI with clean output
    await test_azure_clean()
    
    # Parse the example response
    parse_response_example()


if __name__ == "__main__":
    asyncio.run(main())
