import azure.functions as func
import json
import os
import requests
import logging

def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    Summarize Events Function - Summarizes array of event objects
    POST /api/summarize_events
    Accepts: [{"title": "...", "date": "...", "description": "..."}]
    Returns: {"summary": "..."}
    """

    logging.info('Summarize events function processed a request.')

    try:
        # Parse request body - expecting array of events
        req_body = req.get_json()
        if not req_body or not isinstance(req_body, list):
            return func.HttpResponse(
                json.dumps({"error": "Request body must be an array of event objects"}),
                status_code=400,
                mimetype="application/json"
            )

        events = req_body

        # Get Azure OpenAI configuration
        azure_openai_key = os.environ.get('AZURE_OPENAI_KEY')
        resource_name = os.environ.get('RESOURCE_NAME')

        if not azure_openai_key or not resource_name:
            # Return dummy summary if no API key
            summary = f"Summary of {len(events)} events: " + ", ".join([
                event.get('title', 'Untitled event') for event in events[:3]
            ])
            if len(events) > 3:
                summary += f" and {len(events) - 3} more events."

            return func.HttpResponse(
                json.dumps({"summary": summary}),
                status_code=200,
                mimetype="application/json"
            )

        # Prepare events text for summarization
        events_text = ""
        for event in events:
            title = event.get('title', 'No title')
            date = event.get('date', 'No date')
            description = event.get('description', 'No description')
            events_text += f"- {title} ({date}): {description}\n"

        # Call Azure AI Foundry for summarization
        foundry_url = f"https://{resource_name}.services.ai.azure.com/models/chat/completions?api-version=2024-05-01-preview"
        headers = {
            "Content-Type": "application/json",
            "api-key": azure_openai_key
        }

        payload = {
            "messages": [
                {
                    "role": "system",
                    "content": "You are a helpful assistant that summarizes community events."
                },
                {
                    "role": "user",
                    "content": f"Please provide a concise summary of these community events:\n\n{events_text}"
                }
            ],
            "max_tokens": 200,
            "temperature": 0.3
        }

        # Log the API call
        logging.info(f"Calling Foundry endpoint {foundry_url} for function summarize_events")

        response = requests.post(foundry_url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()

        result = response.json()
        summary = result['choices'][0]['message']['content']

        return func.HttpResponse(
            json.dumps({"summary": summary}),
            status_code=200,
            mimetype="application/json"
        )

    except requests.RequestException as e:
        logging.error(f"Foundry API call failed: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": f"Summarization service unavailable: {str(e)}"}),
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