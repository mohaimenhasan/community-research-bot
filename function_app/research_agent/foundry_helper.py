"""
Azure Foundry client helper for research agent function
"""
import os
import logging
import sys
from typing import Dict, Any, Optional

# Add the function_app directory to the path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def call_foundry_agent(messages: list, tools: Optional[list] = None, location: str = "your area") -> Dict[str, Any]:
    """Call Azure Foundry AI using the centralized client"""
    try:
        from shared.foundry_client import FoundryClient

        logging.info("Initializing Azure Foundry client for research agent")

        # Create foundry client
        foundry_client = FoundryClient()

        # Use the actual agent endpoint for real research capabilities
        agent_id = os.environ.get('AGENT_ID')

        if agent_id:
            logging.info(f"Calling Azure Foundry Agent {agent_id} for real-time research")
            result = foundry_client.call_agent(messages, tools=None)
        else:
            logging.warning("No AGENT_ID found, falling back to chat completions")
            result = foundry_client.call_chat_completions(
                messages,
                max_tokens=800
            )

        logging.info("Azure Foundry response received successfully")

        # Handle case where GPT-5-mini returns empty content but has reasoning tokens
        if "choices" in result and result["choices"]:
            choice = result["choices"][0]
            if "message" in choice and choice["message"].get("content") == "":
                # If content is empty but reasoning tokens were used, log and return error to retry
                if "usage" in result and result["usage"].get("completion_tokens_details", {}).get("reasoning_tokens", 0) > 0:
                    logging.warning("GPT-5-mini returned empty content despite reasoning tokens - model may need different prompt")
                    raise Exception("Model returned empty response despite processing - requires retry")

        return result

    except Exception as e:
        logging.error(f"Azure Foundry call failed: {str(e)}")
        raise