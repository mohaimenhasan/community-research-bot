import azure.functions as func
import json
import logging
from datetime import datetime

def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    Research Agent Function - Simplified for debugging
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

        response = {
            "message": "Research agent function working",
            "method": method,
            "location": location,
            "query": query,
            "timestamp": datetime.utcnow().isoformat(),
            "status": "success"
        }

        return func.HttpResponse(
            json.dumps(response),
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