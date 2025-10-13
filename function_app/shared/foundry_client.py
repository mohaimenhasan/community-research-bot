"""
Azure AI Foundry client utilities for consistent API interactions
"""
import os
import logging
import requests
import json
from typing import Dict, Any, Optional
from azure.identity import ManagedIdentityCredential

API_VERSION = "2024-10-01-preview"

class FoundryClient:
    """Centralized client for Azure AI Foundry API calls"""

    def __init__(self):
        self.resource_name = os.environ.get('RESOURCE_NAME')
        self.azure_openai_key = os.environ.get('AZURE_OPENAI_KEY')
        self.agent_id = os.environ.get('AGENT_ID')

        if not self.resource_name:
            raise ValueError("RESOURCE_NAME environment variable is required")

        # Use the correct Azure OpenAI endpoint
        self.base_url = f"https://{self.resource_name}.cognitiveservices.azure.com"

    def _get_headers(self) -> Dict[str, str]:
        """Get authentication headers, using managed identity for AI Foundry"""
        headers = {"Content-Type": "application/json"}

        # For Azure AI Foundry agents, use API key authentication
        if self.azure_openai_key:
            headers["api-key"] = self.azure_openai_key
            logging.info("Using API key for Azure AI Foundry agent authentication")
        else:
            # Try managed identity as fallback
            try:
                credential = ManagedIdentityCredential()
                token = credential.get_token("https://cognitiveservices.azure.com/.default")
                headers["Authorization"] = f"Bearer {token.token}"
                logging.info("Using managed identity for Azure OpenAI authentication")
            except Exception as e:
                logging.error(f"Failed to get authentication: {str(e)}")
                raise ValueError("No valid authentication method available")

        return headers

    def call_agent(self, messages: list, tools: Optional[list] = None) -> Dict[str, Any]:
        """Call Azure OpenAI deployment (using gpt-5-mini for research tasks)"""
        # Use Azure OpenAI chat completions endpoint with gpt-5-mini deployment
        url = f"{self.base_url}/openai/deployments/gpt-5-mini/chat/completions?api-version={API_VERSION}"

        payload = {
            "messages": messages,
            "max_completion_tokens": 800
        }
        if tools:
            payload["tools"] = tools

        return self._make_request(url, payload, "agent")

    def call_chat_completions(self, messages: list, max_tokens: int = 200,
                            temperature: float = 0.3) -> Dict[str, Any]:
        """Call chat completions endpoint for general LLM tasks"""
        # Use Azure OpenAI endpoint format for chat completions
        url = f"{self.base_url}/openai/deployments/gpt-5-mini/chat/completions?api-version={API_VERSION}"

        payload = {
            "messages": messages,
            "max_completion_tokens": max_tokens
            # Remove temperature as gpt-5-mini only supports default value of 1
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