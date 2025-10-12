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

        response = requests.post(url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()

        try:
            return response.json()
        except json.JSONDecodeError:
            return {"raw_response": response.text}

    except Exception as e:
        logging.error(f"Foundry agent call failed: {str(e)}")
        raise