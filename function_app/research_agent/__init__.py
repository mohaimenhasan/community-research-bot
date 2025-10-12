import azure.functions as func
import json
import logging
import os
import requests
from datetime import datetime, timezone

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

        # Get environment variables
        resource_name = os.environ.get('RESOURCE_NAME')
        agent_id = os.environ.get('AGENT_ID')
        azure_openai_key = os.environ.get('AZURE_OPENAI_KEY')

        if not all([resource_name, agent_id]):
            return func.HttpResponse(
                json.dumps({"error": "Missing required environment variables"}),
                status_code=500,
                mimetype="application/json"
            )

        # Construct Foundry Agent API call
        foundry_url = f"https://{resource_name}.services.ai.azure.com/openai/agents/{agent_id}/runs?api-version=2024-05-01-preview"

        headers = {
            "Content-Type": "application/json"
        }

        # Use API key if available, otherwise managed identity
        if azure_openai_key:
            headers["api-key"] = azure_openai_key
        else:
            # For now, return error if no key - managed identity setup needs additional config
            return func.HttpResponse(
                json.dumps({"error": "Authentication configuration required"}),
                status_code=500,
                mimetype="application/json"
            )

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

        payload = {
            "messages": [
                {
                    "role": "system",
                    "content": system_content
                },
                {
                    "role": "user",
                    "content": f"Research and summarize current information about {query} in {location}. Provide a comprehensive overview of what's happening in the community."
                }
            ],
            "tools": [
                {
                    "type": "function",
                    "function": {
                        "name": "search_web",
                        "description": "Search the web for current information about a location and topic"
                    }
                }
            ]
        }

        # Log the API call
        logging.info(f"Calling Foundry endpoint {foundry_url} for research_agent")

        # Make API call to Foundry Agent
        response = requests.post(foundry_url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()

        # Try to parse JSON response, fallback to raw response if not JSON
        try:
            result = response.json()
        except json.JSONDecodeError:
            result = {"raw_response": response.text}

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

    except requests.RequestException as e:
        logging.error(f"Foundry API call failed: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": f"Agent service unavailable: {str(e)}"}),
            status_code=502,
            mimetype="application/json"
        )
    except Exception as e:
        logging.error(f"Research agent function failed: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": "Research service temporarily unavailable"}),
            status_code=500,
            mimetype="application/json"
        )