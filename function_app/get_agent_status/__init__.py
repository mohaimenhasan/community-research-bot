import azure.functions as func
import json
import os
import logging

def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    Get Agent Status Function - Health check endpoint
    GET /api/get_agent_status
    Returns: {"status": "ok", "agent_id": "...", "resource_name": "..."}
    """

    logging.info('Get agent status function processed a request.')

    try:
        # Get environment variables
        agent_id = os.environ.get('AGENT_ID', 'not-configured')
        resource_name = os.environ.get('RESOURCE_NAME', 'not-configured')
        azure_openai_key = os.environ.get('AZURE_OPENAI_KEY')

        # Determine status based on configuration
        status = "ok" if azure_openai_key else "degraded"

        # Build response
        response_data = {
            "status": status,
            "agent_id": agent_id,
            "resource_name": resource_name,
            "timestamp": req.datetime.isoformat() if hasattr(req, 'datetime') else None,
            "configured": {
                "agent_id": agent_id != 'not-configured',
                "resource_name": resource_name != 'not-configured',
                "azure_openai_key": azure_openai_key is not None
            }
        }

        return func.HttpResponse(
            json.dumps(response_data),
            status_code=200,
            mimetype="application/json"
        )

    except Exception as e:
        logging.error(f"Function failed: {str(e)}")
        error_response = {
            "status": "error",
            "agent_id": "unknown",
            "resource_name": "unknown",
            "error": "Health check failed"
        }
        return func.HttpResponse(
            json.dumps(error_response),
            status_code=500,
            mimetype="application/json"
        )