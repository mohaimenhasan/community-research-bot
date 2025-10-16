"""
Azure Foundry client helper for research agent function
Uses Agent-to-Agent (A2A) communication with internet search
"""
import os
import logging
import sys
from typing import Dict, Any, Optional, List

# Add the function_app directory to the path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def call_foundry_agent(location: str, user_interests: Optional[List[str]] = None, past_events: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Call Azure AI Foundry Agent with internet search enabled
    This uses A2A communication to let the agent do REAL web research
    """
    try:
        from shared.foundry_client import FoundryClient

        logging.info(f"Calling Azure AI Foundry Agent for REAL internet research about {location}")

        # Create foundry client
        foundry_client = FoundryClient()

        # Build concise user query for the agent (cost optimization)
        user_query = f"Find current events, meetings, and news in {location}."
        
        if user_interests:
            user_query += f" Focus on: {', '.join(user_interests[:3])}."  # Limit to 3 interests
        
        user_query += " Provide 3-5 items per category with dates/times/locations and sources."

        # Call the agent with internet search enabled (with cost limits)
        result = foundry_client.call_agent_with_search(user_query, max_tokens=800)

        logging.info("Azure Foundry Agent completed internet research successfully")
        
        return result

    except Exception as e:
        logging.error(f"Azure Foundry Agent research failed: {str(e)}")
        raise