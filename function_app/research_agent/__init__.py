import azure.functions as func
import json
import os
import requests
import logging

def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    Research Agent Function - Calls Foundry Agent API
    POST /api/research_agent
    Accepts: {"location": "Vancouver"}
    Returns: Agent's JSON response directly
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

        # Get environment variables for Foundry Agent API
        resource_name = os.environ.get('RESOURCE_NAME')
        agent_id = os.environ.get('AGENT_ID')
        azure_openai_key = os.environ.get('AZURE_OPENAI_KEY')

        if not all([resource_name, agent_id, azure_openai_key]):
            return func.HttpResponse(
                json.dumps({"error": "Missing required environment variables"}),
                status_code=500,
                mimetype="application/json"
            )

        # Construct Foundry Agent API call
        foundry_url = f"https://{resource_name}.services.ai.azure.com/openai/agents/{agent_id}/runs?api-version=2024-05-01-preview"
        headers = {
            "Content-Type": "application/json",
            "api-key": azure_openai_key
        }

        payload = {
            "messages": [
                {
                    "role": "user",
                    "content": f"Please research community information for {location}"
                }
            ]
        }

        # Log the API call
        logging.info(f"Calling Foundry endpoint {foundry_url} for function research_agent")

        # Make API call to Foundry Agent
        response = requests.post(foundry_url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()

        # Try to parse JSON response, fallback to raw response if not JSON
        try:
            result = response.json()
            return func.HttpResponse(
                json.dumps(result),
                status_code=200,
                mimetype="application/json"
            )
        except json.JSONDecodeError:
            return func.HttpResponse(
                json.dumps({"raw_response": response.text}),
                status_code=200,
                mimetype="application/json"
            )

    except requests.RequestException as e:
        logging.error(f"API call failed: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": f"External API call failed: {str(e)}"}),
            status_code=502,
            mimetype="application/json"
        )
    except Exception as e:
        logging.error(f"Function failed: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": "Internal server error"}),
            status_code=500,
            mimetype="application/json"
        )