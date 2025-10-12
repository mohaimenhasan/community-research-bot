import azure.functions as func
import json
import logging
from datetime import datetime, timezone
from .foundry_helper import call_foundry_agent

def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    Research Agent Function - Calls Azure AI Foundry Agent
    POST /api/research_agent
    Accepts: {"location": "Vancouver", "query": "community events"}
    Returns: Agent's JSON response with enhanced context
    """

    logging.info('Research agent function processed a request.')

    try:
        # Parse request body
        req_body = req.get_json()
        if not req_body or 'location' not in req_body:
            return func.HttpResponse(
                json.dumps({"error": "Missing 'location' in request body"}),
                status_code=400,
                mimetype="application/json"
            )

        location = req_body['location']
        query = req_body.get('query', 'local news and events')

        # Prepare enhanced prompt for the agent
        system_content = f"""You are a community research agent specializing in {location}.

Your task is to research and provide comprehensive information about community activities, local news, events, and developments in {location}. Focus on:
1. Recent community events and initiatives
2. Local government updates and decisions
3. Business openings, closings, or significant changes
4. Community groups and organizations
5. Infrastructure or development projects
6. Cultural and social happenings

Provide sources when possible and prioritize recent, relevant information."""

        messages = [
            {
                "role": "system",
                "content": system_content
            },
            {
                "role": "user",
                "content": f"Research and summarize current information about {query} in {location}. Provide a comprehensive overview of what's happening in the community."
            }
        ]

        tools = [
            {
                "type": "function",
                "function": {
                    "name": "search_web",
                    "description": "Search the web for current information about a location and topic"
                }
            }
        ]

        try:
            # Call Foundry agent using helper function with timeout handling
            logging.info("Starting Foundry agent call")
            result = call_foundry_agent(messages, tools)
            logging.info("Foundry agent call completed successfully")
        except Exception as e:
            # Fallback to mock response if Foundry call fails
            logging.warning(f"Foundry agent call failed, using fallback: {str(e)}")
            result = {
                "choices": [{
                    "message": {
                        "content": f"Mock research summary for {query} in {location}: Community is active with various local events and initiatives. This is a fallback response when the Foundry agent is unavailable. Error: {str(e)[:100]}"
                    }
                }],
                "usage": {"total_tokens": 50},
                "fallback_response": True,
                "error_details": str(e)
            }

        # Enhanced response with metadata
        enhanced_result = {
            "agent_response": result,
            "metadata": {
                "location": location,
                "query": query,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "status": "success"
            }
        }

        return func.HttpResponse(
            json.dumps(enhanced_result),
            status_code=200,
            mimetype="application/json"
        )

    except Exception as e:
        logging.error(f"Research agent function failed: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": "Research service temporarily unavailable"}),
            status_code=500,
            mimetype="application/json"
        )