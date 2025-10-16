"""
Azure AI Foundry client utilities for consistent API interactions
"""
import os
import logging
import json
from typing import Dict, Any, Optional
# Handle azure.identity import with fallback
try:
    from azure.identity import ManagedIdentityCredential
    AZURE_IDENTITY_AVAILABLE = True
except ImportError:
    AZURE_IDENTITY_AVAILABLE = False

# Handle requests import with fallback
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    import urllib.request
    import urllib.parse
    REQUESTS_AVAILABLE = False

API_VERSION = "2024-06-01"

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
        """Get authentication headers, using API key or managed identity"""
        headers = {"Content-Type": "application/json"}

        # For Azure AI Foundry agents, use API key authentication
        if self.azure_openai_key:
            headers["api-key"] = self.azure_openai_key
            logging.info("Using API key for Azure AI Foundry agent authentication")
        elif AZURE_IDENTITY_AVAILABLE:
            # Try managed identity as fallback
            try:
                credential = ManagedIdentityCredential()
                token = credential.get_token("https://cognitiveservices.azure.com/.default")
                headers["Authorization"] = f"Bearer {token.token}"
                logging.info("Using managed identity for Azure OpenAI authentication")
            except Exception as e:
                logging.error(f"Failed to get authentication: {str(e)}")
                raise ValueError("No valid authentication method available")
        else:
            logging.error("No authentication method available - both API key and azure.identity module missing")
            raise ValueError("No valid authentication method available")

        return headers

    def call_agent_with_search(self, user_query: str, max_tokens: int = 1000) -> Dict[str, Any]:
        """
        Call Azure AI Foundry Agent with internet search enabled (A2A)
        This is the proper way to use agents with web search capabilities
        
        Cost optimization:
        - Default max_tokens=1000 (reduced from 2000 to save money)
        - Clear, concise instructions to minimize reasoning tokens
        - Structured output format to reduce token waste
        """
        if not self.agent_id:
            raise ValueError("AGENT_ID is required for agent-based internet search")
        
        # Azure AI Foundry Assistants API with internet search
        url = f"{self.base_url}/openai/threads/runs?api-version={API_VERSION}"
        
        # Cost-optimized payload with clear, direct instructions
        payload = {
            "assistant_id": self.agent_id,
            "thread": {
                "messages": [{
                    "role": "user",
                    "content": user_query
                }]
            },
            # Concise instructions to minimize token usage
            "instructions": """You are a community research assistant. Search the internet for REAL current information.

Find 3-5 items per category:
1. Town hall meetings & city council (dates, times, agenda items)
2. Community events (festivals, markets with specific dates)
3. Local news (recent stories from official sources)
4. Public services (library, recreation programs)

Format each as: **Title** - Brief description (date/time/location). Source: URL

Be concise. Use only verified information you find online.""",
            "tools": [
                {
                    "type": "bing_search"  # Enable Bing search for the agent
                }
            ],
            "max_completion_tokens": max_tokens,  # Cost control
            "stream": False,
            "temperature": 0.3  # Lower temperature for more focused, cheaper responses
        }
        
        logging.info(f"Calling Azure AI Foundry Agent with internet search (max_tokens={max_tokens})")
        return self._make_request(url, payload, "agent_internet_search")

    def call_agent(self, messages: list, tools: Optional[list] = None) -> Dict[str, Any]:
        """Call Azure AI Foundry Agent using A2A communication with Azure OpenAI Assistants API"""
        if self.agent_id:
            # Use Azure OpenAI Assistants API for A2A communication
            # Create thread and run in one call (thread.runs)
            url = f"{self.base_url}/openai/threads/runs?api-version={API_VERSION}"

            # Proper A2A payload for Azure OpenAI Assistants API
            payload = {
                "assistant_id": self.agent_id,
                "thread": {
                    "messages": [
                        {
                            "role": "user",
                            "content": f"Create engaging community content for the location specified. Format as Instagram-style posts with hooks that get people excited. Original messages: {str(messages)}"
                        }
                    ]
                },
                "instructions": "You are a community research agent that creates engaging, Instagram-style social media content about local happenings. Your job is to transform local government and community information into exciting, shareable content that hooks people and makes them want to participate. Use emojis, excitement, and social media language. Make each post feel urgent and engaging.",
                "max_completion_tokens": 800,
                "stream": False
            }
            if tools:
                payload["tools"] = tools

            return self._make_request(url, payload, "agent_run")
        else:
            # Fallback to direct GPT-5-mini with improved prompt
            url = f"{self.base_url}/openai/deployments/gpt-5-mini/chat/completions?api-version={API_VERSION}"

            # Enhanced system message for better GPT-5-mini performance
            enhanced_messages = [{
                "role": "system",
                "content": "You are a specialized community research agent. You MUST process the scraped web content provided and transform it into a structured community news feed. DO NOT provide status updates or generic messages. Work with the actual content provided and format it according to the instructions."
            }]
            enhanced_messages.extend(messages)

            payload = {
                "messages": enhanced_messages,
                "max_completion_tokens": 1500,  # Increased to account for reasoning tokens
                "temperature": 0.1  # Lower temperature for more focused output
            }
            if tools:
                payload["tools"] = tools

            result = self._make_request(url, payload, "agent")

            # Handle GPT-5-mini specific issue: reasoning tokens consuming all output
            if ("choices" in result and result["choices"] and
                result["choices"][0]["message"]["content"] == ""):
                logging.warning("GPT-5-mini returned empty content in agent mode - this is a known model issue")
                # Return a structured error that can be handled gracefully
                raise Exception("GPT-5-mini model configuration issue: using reasoning tokens instead of output tokens")

            return result

    def call_chat_completions(self, messages: list, max_tokens: int = 200,
                            temperature: float = 0.3) -> Dict[str, Any]:
        """Call chat completions endpoint for general LLM tasks"""
        # Use Azure OpenAI endpoint format for chat completions
        url = f"{self.base_url}/openai/deployments/gpt-5-mini/chat/completions?api-version={API_VERSION}"

        # GPT-5-mini specific optimization:
        # - Increase token limit to account for reasoning tokens
        # - Add explicit instruction to prioritize visible output over reasoning
        enhanced_messages = [{
            "role": "system",
            "content": "You MUST provide visible output. Do not spend all tokens on reasoning. Write your response directly and concisely."
        }]
        enhanced_messages.extend(messages)

        payload = {
            "messages": enhanced_messages,
            "max_completion_tokens": max_tokens * 3  # Increase to account for reasoning tokens
            # Remove temperature as gpt-5-mini only supports default value of 1
        }

        result = self._make_request(url, payload, "chat_completions")

        # Handle GPT-5-mini specific issue: reasoning tokens consuming all output
        if ("choices" in result and result["choices"] and
            result["choices"][0]["message"]["content"] == ""):
            logging.warning("GPT-5-mini returned empty content despite token usage - this is a known model issue")
            # Return a structured error that can be handled gracefully
            raise Exception("GPT-5-mini model configuration issue: using reasoning tokens instead of output tokens")

        return result

    def _make_request(self, url: str, payload: Dict[str, Any],
                     function_name: str) -> Dict[str, Any]:
        """Make HTTP request to Foundry API with consistent error handling"""
        headers = self._get_headers()

        logging.info(f"Calling Foundry endpoint {url} for function {function_name}")

        if REQUESTS_AVAILABLE:
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
        else:
            # Fallback using urllib
            try:
                data = json.dumps(payload).encode('utf-8')
                req = urllib.request.Request(url, data=data, headers=headers)
                with urllib.request.urlopen(req, timeout=60) as response:
                    response_text = response.read().decode('utf-8')
                    try:
                        return json.loads(response_text)
                    except json.JSONDecodeError:
                        logging.warning(f"Non-JSON response from {function_name}")
                        return {"raw_response": response_text}

            except Exception as e:
                logging.error(f"Foundry API call failed for {function_name}: {str(e)}")
                raise