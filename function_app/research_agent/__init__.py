import azure.functions as func
import json
import logging
from datetime import datetime

def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    Research Agent Function - Comprehensive Langley BC Event Discovery
    """
    logging.info('Research agent function processed a request.')

    # Handle CORS preflight requests
    if req.method == 'OPTIONS':
        return func.HttpResponse(
            "",
            status_code=200,
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type"
            }
        )

    try:
        # Parse request
        req_body = {}
        if req.method == 'POST':
            try:
                req_body = req.get_json() or {}
            except:
                req_body = {}

        location = req_body.get('location', 'Unknown Location')
        user_preferences = req_body.get('preferences', {})
        interests = user_preferences.get('interests', [])
        past_events = user_preferences.get('past_events', [])

        logging.info(f"Processing research request for location: {location}")

        # Call Azure AI Foundry Agent with REAL internet search
        try:
            from .foundry_helper import call_foundry_agent

            logging.info(f"Calling Azure AI Foundry Agent for REAL internet research about {location}")
            
            # Call the agent - it will do real internet research
            agent_response = call_foundry_agent(
                location=location, 
                user_interests=interests if interests else None,
                past_events=past_events if past_events else None
            )

            logging.info("Azure Foundry Agent completed real internet research")

            # Extract the actual content from agent response
            if "choices" in agent_response and agent_response["choices"]:
                content = agent_response["choices"][0]["message"]["content"]
            else:
                raise Exception("Agent returned invalid response structure")

            # Return structured response
            enhanced_result = {
                "agent_response": {
                    "content": content,
                    "location_specific": True,
                    "research_agent_active": True,
                    "discovery_status": "real_data_retrieved",
                    "data_source": "azure_ai_foundry_internet_search"
                },
                "metadata": {
                    "location": location,
                    "user_preferences": {
                        "interests": interests,
                        "past_events": past_events
                    },
                    "timestamp": datetime.utcnow().isoformat(),
                    "status": "success",
                    "agent_type": "azure_ai_foundry_with_internet_search"
                }
            }

            return func.HttpResponse(
                json.dumps(enhanced_result),
                status_code=200,
                mimetype="application/json",
                headers={
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                    "Access-Control-Allow-Headers": "Content-Type"
                }
            )

        except Exception as foundry_error:
            logging.error(f"Azure AI Foundry research failed: {str(foundry_error)}")
            # Return error instead of mock data - force real data usage
            return func.HttpResponse(
                json.dumps({
                    "error": "Research agent failed - please check Azure AI Foundry configuration",
                    "details": str(foundry_error),
                    "solution": "Verify AGENT_ID and ensure agent has internet search enabled"
                }),
                status_code=503,
                mimetype="application/json",
                headers={
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                    "Access-Control-Allow-Headers": "Content-Type"
                }
            )

    except Exception as e:
        logging.error(f"Research agent function failed: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": f"Research agent error: {str(e)}"}),
            status_code=500,
            mimetype="application/json",
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type"
            }
        )