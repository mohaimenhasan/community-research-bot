"""
Local Foundry client helper for research agent function using managed identity
"""
import os
import logging
import requests
import json
from typing import Dict, Any, Optional
from azure.identity import DefaultAzureCredential

def call_foundry_agent(messages: list, tools: Optional[list] = None) -> Dict[str, Any]:
    """Call Azure AI Foundry agent using managed identity authentication"""
    try:
        resource_name = os.environ.get('RESOURCE_NAME')

        logging.info(f"Environment check - RESOURCE_NAME: {resource_name}")

        if not resource_name:
            raise ValueError("Missing RESOURCE_NAME environment variable")

        # For now, let's test without managed identity to see if the function works
        logging.info("Testing function without Azure AI call for debugging")

        # Mock response to test if function structure works
        mock_result = {
            "choices": [{
                "message": {
                    "content": f"Mock response for testing managed identity setup. Messages received: {len(messages)} messages."
                }
            }],
            "usage": {"total_tokens": 25},
            "managed_identity_test": True
        }

        logging.info("Returning mock response for managed identity testing")
        return mock_result

        # TODO: Re-enable this code once basic function works
        # # Use chat completions endpoint since agents endpoint may not be available
        # url = f"https://{resource_name}.cognitiveservices.azure.com/openai/deployments/gpt-5-mini/chat/completions?api-version=2024-05-01-preview"
        #
        # # Get access token using managed identity
        # logging.info("Attempting to get managed identity token")
        # credential = DefaultAzureCredential()
        # token = credential.get_token("https://cognitiveservices.azure.com/.default")
        # logging.info("Managed identity token obtained successfully")
        #
        # headers = {
        #     "Content-Type": "application/json",
        #     "Authorization": f"Bearer {token.token}"
        # }
        #
        # # Convert messages to a simpler format for chat completions
        # payload = {
        #     "messages": messages,
        #     "max_tokens": 500,
        #     "temperature": 0.3
        # }
        #
        # logging.info(f"Calling Azure AI endpoint {url}")
        # logging.info(f"Using managed identity authentication")
        # logging.info(f"Payload size: {len(json.dumps(payload))} characters")
        #
        # response = requests.post(url, headers=headers, json=payload, timeout=30)
        #
        # logging.info(f"Response status: {response.status_code}")
        #
        # if response.status_code != 200:
        #     logging.error(f"HTTP Error {response.status_code}: {response.text}")
        #
        # response.raise_for_status()
        #
        # try:
        #     result = response.json()
        #     logging.info(f"Azure AI response received successfully")
        #     return result
        # except json.JSONDecodeError:
        #     logging.warning("Invalid JSON response, returning raw text")
        #     return {"raw_response": response.text}

    except Exception as e:
        logging.error(f"Function call failed: {str(e)}")
        raise