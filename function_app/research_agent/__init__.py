import azure.functions as func
import json
import logging
import os
import requests
from datetime import datetime

def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    Research Agent Function - Simple working version
    """
    logging.info('Research agent function processed a request.')

    try:
        method = req.method
        req_body = {}

        if method == 'POST':
            try:
                req_body = req.get_json() or {}
            except:
                req_body = {}

        location = req_body.get('location', 'Unknown Location')
        query = req_body.get('query', 'local news and events')

        # Try Azure AI call with simple managed identity approach
        try:
            resource_name = os.environ.get('RESOURCE_NAME', 'community-research')

            # Try to get managed identity token using the simplest approach
            token_url = "http://169.254.169.254/metadata/identity/oauth2/token?api-version=2018-02-01&resource=https://cognitiveservices.azure.com/"
            token_headers = {"Metadata": "true"}

            logging.info("Attempting to get managed identity token")
            token_response = requests.get(token_url, headers=token_headers, timeout=10)

            if token_response.status_code == 200:
                token_data = token_response.json()
                access_token = token_data["access_token"]

                # Call Azure AI
                ai_url = f"https://{resource_name}.cognitiveservices.azure.com/openai/deployments/gpt-5-mini/chat/completions?api-version=2024-05-01-preview"
                ai_headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {access_token}"
                }

                ai_payload = {
                    "messages": [
                        {"role": "user", "content": f"Provide a brief research summary about {query} in {location}"}
                    ],
                    "max_tokens": 200,
                    "temperature": 0.3
                }

                logging.info("Calling Azure AI with managed identity token")
                ai_response = requests.post(ai_url, headers=ai_headers, json=ai_payload, timeout=15)

                if ai_response.status_code == 200:
                    agent_response = ai_response.json()
                    logging.info("Azure AI call successful!")
                else:
                    logging.warning(f"Azure AI returned {ai_response.status_code}: {ai_response.text}")
                    raise Exception(f"AI API error: {ai_response.status_code}")
            else:
                logging.warning(f"Token request failed: {token_response.status_code}")
                raise Exception(f"Token request failed: {token_response.status_code}")

        except Exception as e:
            logging.warning(f"Azure AI integration failed: {str(e)}, using fallback")
            agent_response = {
                "choices": [{
                    "message": {
                        "content": f"Research summary for {query} in {location}: This is a working research agent response with fallback mode. Azure AI integration attempted but failed: {str(e)[:50]}"
                    }
                }],
                "usage": {"total_tokens": 35},
                "fallback_mode": True,
                "error": str(e)
            }

        enhanced_result = {
            "agent_response": agent_response,
            "metadata": {
                "location": location,
                "query": query,
                "timestamp": datetime.utcnow().isoformat(),
                "status": "success",
                "function_mode": "working_baseline"
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
            json.dumps({"error": f"Research agent error: {str(e)}"}),
            status_code=500,
            mimetype="application/json"
        )