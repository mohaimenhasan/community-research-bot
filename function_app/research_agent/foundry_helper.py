"""
Local Foundry client helper for research agent function using managed identity
"""
import os
import logging
import requests
import json
from typing import Dict, Any, Optional
# from azure.identity import DefaultAzureCredential  # Temporarily removed to test import issue

def call_foundry_agent(messages: list, tools: Optional[list] = None) -> Dict[str, Any]:
    """Call Azure AI using managed identity authentication"""
    try:
        resource_name = os.environ.get('RESOURCE_NAME')

        logging.info(f"Environment check - RESOURCE_NAME: {resource_name}")

        if not resource_name:
            raise ValueError("Missing RESOURCE_NAME environment variable")

        # Use chat completions endpoint
        url = f"https://{resource_name}.cognitiveservices.azure.com/openai/deployments/gpt-5-mini/chat/completions?api-version=2024-05-01-preview"

        try:
            # For now, return a fallback response while we debug managed identity
            logging.info("Using fallback response while debugging managed identity")

            # Simulate a successful Azure AI response for testing
            result = {
                "choices": [{
                    "message": {
                        "content": f"Research summary for {len(messages)} messages: This is a test response while we resolve managed identity authentication. The system is working but using a fallback due to authentication timeout issues."
                    }
                }],
                "usage": {"total_tokens": 45},
                "fallback_mode": True,
                "debug_info": "Managed identity authentication bypassed for testing"
            }

            logging.info("Returning fallback response for managed identity debugging")
            return result

            # TODO: Re-enable managed identity authentication once timeout issue is resolved
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

        except Exception as token_error:
            # If anything fails, log the error and raise it
            logging.error(f"Function execution failed: {str(token_error)}")
            raise

    except Exception as e:
        logging.error(f"Azure AI call failed: {str(e)}")
        raise