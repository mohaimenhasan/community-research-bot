"""
Azure AI Foundry client utilities for consistent API interactions
"""
import os
import logging
import requests
import json
from typing import Dict, Any, Optional
from azure.identity import ManagedIdentityCredential

API_VERSION = "2024-05-01-preview"

class FoundryClient:
    """Centralized client for Azure AI Foundry API calls"""

    def __init__(self):
        self.resource_name = os.environ.get('RESOURCE_NAME')
        self.azure_openai_key = os.environ.get('AZURE_OPENAI_KEY')
        self.agent_id = os.environ.get('AGENT_ID')

        if not self.resource_name:
            raise ValueError("RESOURCE_NAME environment variable is required")

        self.base_url = f"https://{self.resource_name}.services.ai.azure.com"

    def _get_headers(self) -> Dict[str, str]:
        """Get authentication headers, preferring API key over managed identity"""
        headers = {"Content-Type": "application/json"}

        if self.azure_openai_key:
            headers["api-key"] = self.azure_openai_key
        else:
            try:
                credential = ManagedIdentityCredential()
                token = credential.get_token("https://cognitiveservices.azure.com/.default")
                headers["Authorization"] = f"Bearer {token.token}"
            except Exception as e:
                logging.error(f"Failed to get managed identity token: {str(e)}")
                raise ValueError("No valid authentication method available")

        return headers

    def call_agent(self, messages: list, tools: Optional[list] = None) -> Dict[str, Any]:
        """Call specific Azure AI Foundry agent"""
        if not self.agent_id:
            raise ValueError("AGENT_ID environment variable is required for agent calls")

        url = f"{self.base_url}/openai/agents/{self.agent_id}/runs?api-version={API_VERSION}"

        payload = {"messages": messages}
        if tools:
            payload["tools"] = tools

        return self._make_request(url, payload, "agent")

    def call_chat_completions(self, messages: list, max_tokens: int = 200,
                            temperature: float = 0.3) -> Dict[str, Any]:
        """Call chat completions endpoint for general LLM tasks"""
        url = f"{self.base_url}/models/chat/completions?api-version={API_VERSION}"

        payload = {
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature
        }

        return self._make_request(url, payload, "chat_completions")

    def _make_request(self, url: str, payload: Dict[str, Any],
                     function_name: str) -> Dict[str, Any]:
        """Make HTTP request to Foundry API with consistent error handling"""
        headers = self._get_headers()

        logging.info(f"Calling Foundry endpoint {url} for function {function_name}")

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=60)
            response.raise_for_status()

            try:
                return response.json()
            except json.JSONDecodeError:
                logging.warning(f"Non-JSON response from {function_name}")
                return {"raw_response": response.text}

        except requests.RequestException as e:
            logging.error(f"Foundry API call failed for {function_name}: {str(e)}")
            raise