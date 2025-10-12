"""
Azure service clients for Community Hub functions
Fixed import paths for Azure Functions deployment
"""
import os
import logging
import requests
import json
from typing import Dict, Any, Optional

# Azure Foundry Client
class FoundryClient:
    """Centralized client for Azure AI Foundry API calls"""

    def __init__(self):
        self.resource_name = os.environ.get('RESOURCE_NAME')
        self.azure_openai_key = os.environ.get('AZURE_OPENAI_KEY')
        self.agent_id = os.environ.get('AGENT_ID')

        if not self.resource_name:
            raise ValueError("RESOURCE_NAME environment variable is required")

        self.base_url = f"https://{self.resource_name}.services.ai.azure.com"

    def call_agent(self, messages: list, tools: Optional[list] = None) -> Dict[str, Any]:
        """Call specific Azure AI Foundry agent"""
        if not self.agent_id:
            raise ValueError("AGENT_ID environment variable is required for agent calls")

        url = f"{self.base_url}/openai/agents/{self.agent_id}/runs?api-version=2024-05-01-preview"

        payload = {"messages": messages}
        if tools:
            payload["tools"] = tools

        headers = {"Content-Type": "application/json"}

        if self.azure_openai_key:
            headers["api-key"] = self.azure_openai_key
        else:
            raise ValueError("No valid authentication method available")

        logging.info(f"Calling Foundry agent endpoint {url}")

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=60)
            response.raise_for_status()

            try:
                return response.json()
            except json.JSONDecodeError:
                return {"raw_response": response.text}

        except requests.RequestException as e:
            logging.error(f"Foundry agent API call failed: {str(e)}")
            raise

    def call_chat_completions(self, messages: list, max_tokens: int = 200,
                            temperature: float = 0.3) -> Dict[str, Any]:
        """Call chat completions endpoint for general LLM tasks"""
        url = f"{self.base_url}/models/chat/completions?api-version=2024-05-01-preview"

        payload = {
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature
        }

        headers = {"Content-Type": "application/json"}

        if self.azure_openai_key:
            headers["api-key"] = self.azure_openai_key
        else:
            raise ValueError("No valid authentication method available")

        logging.info(f"Calling Foundry chat completions endpoint {url}")

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=60)
            response.raise_for_status()

            try:
                return response.json()
            except json.JSONDecodeError:
                return {"raw_response": response.text}

        except requests.RequestException as e:
            logging.error(f"Foundry chat completions API call failed: {str(e)}")
            raise


# Helper functions for content processing
def create_foundry_client() -> Optional[FoundryClient]:
    """Create Foundry client with error handling"""
    try:
        return FoundryClient()
    except Exception as e:
        logging.error(f"Failed to create Foundry client: {str(e)}")
        return None


def process_content_with_foundry(content: str, location: str, category: str) -> Dict[str, Any]:
    """Process content using Foundry chat completions API"""
    try:
        foundry_client = create_foundry_client()
        if not foundry_client:
            return create_mock_processed_content(content, location, category)

        messages = [
            {
                "role": "system",
                "content": f"Analyze content for {location} community. Provide summary, category, sentiment, and significance level."
            },
            {
                "role": "user",
                "content": f"Category: {category}\nContent: {content[:1000]}"
            }
        ]

        result = foundry_client.call_chat_completions(messages, max_tokens=300, temperature=0.2)

        # Parse the result
        analysis_text = result['choices'][0]['message']['content']

        return {
            'summary': analysis_text[:200] + "..." if len(analysis_text) > 200 else analysis_text,
            'category': category,
            'sentiment': 'neutral',  # Default, could be extracted from analysis
            'significance': 'medium',
            'location': location,
            'foundry_processed': True
        }

    except Exception as e:
        logging.error(f"Foundry processing failed: {str(e)}")
        return create_mock_processed_content(content, location, category)


def create_mock_processed_content(content: str, location: str, category: str) -> Dict[str, Any]:
    """Create mock processed content when Foundry is unavailable"""
    summary = content[:200] + "..." if len(content) > 200 else content

    # Simple keyword-based sentiment analysis
    positive_words = ['good', 'great', 'excellent', 'amazing', 'positive']
    negative_words = ['bad', 'terrible', 'awful', 'negative', 'problem']

    content_lower = content.lower()
    positive_count = sum(1 for word in positive_words if word in content_lower)
    negative_count = sum(1 for word in negative_words if word in content_lower)

    if positive_count > negative_count:
        sentiment = 'positive'
    elif negative_count > positive_count:
        sentiment = 'negative'
    else:
        sentiment = 'neutral'

    return {
        'summary': summary,
        'category': category,
        'sentiment': sentiment,
        'significance': 'medium',
        'location': location,
        'foundry_processed': False,
        'mock_data': True
    }