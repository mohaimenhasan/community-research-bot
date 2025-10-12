"""
Local Foundry client helper for research agent function
"""
import os
import logging
import requests
import json
from typing import Dict, Any, Optional

def call_foundry_agent(messages: list, tools: Optional[list] = None) -> Dict[str, Any]:
    """Call Azure AI Foundry agent with proper error handling"""
    try:
        resource_name = os.environ.get('RESOURCE_NAME')
        agent_id = os.environ.get('AGENT_ID')
        azure_openai_key = os.environ.get('AZURE_OPENAI_KEY')

        logging.info(f"Environment check - RESOURCE_NAME: {resource_name}, AGENT_ID: {agent_id}, Has key: {bool(azure_openai_key)}")

        if not all([resource_name, agent_id]):
            raise ValueError("Missing required environment variables")

        url = f"https://{resource_name}.services.ai.azure.com/openai/agents/{agent_id}/runs?api-version=2024-05-01-preview"

        headers = {"Content-Type": "application/json"}

        if azure_openai_key:
            headers["api-key"] = azure_openai_key
        else:
            raise ValueError("No authentication method available")

        payload = {"messages": messages}
        if tools:
            payload["tools"] = tools

        logging.info(f"Calling Foundry agent endpoint {url}")
        logging.info(f"Payload size: {len(json.dumps(payload))} characters")

        response = requests.post(url, headers=headers, json=payload, timeout=30)

        logging.info(f"Response status: {response.status_code}")

        if response.status_code != 200:
            logging.error(f"HTTP Error {response.status_code}: {response.text}")

        response.raise_for_status()

        try:
            result = response.json()
            logging.info(f"Foundry response received successfully")
            return result
        except json.JSONDecodeError:
            logging.warning("Invalid JSON response, returning raw text")
            return {"raw_response": response.text}

    except requests.Timeout:
        logging.error("Foundry agent call timed out")
        raise
    except requests.RequestException as e:
        logging.error(f"Foundry agent request failed: {str(e)}")
        raise
    except Exception as e:
        logging.error(f"Foundry agent call failed: {str(e)}")
        raise