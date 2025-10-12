import azure.functions as func
import json
import logging
from datetime import datetime

def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    Simple test function to verify basic functionality
    """
    logging.info('Simple test function processed a request.')

    try:
        method = req.method
        req_body = {}

        if method == 'POST':
            try:
                req_body = req.get_json() or {}
            except:
                req_body = {}

        response = {
            "message": "Simple test function working",
            "method": method,
            "timestamp": datetime.utcnow().isoformat(),
            "request_body": req_body,
            "status": "success"
        }

        return func.HttpResponse(
            json.dumps(response),
            status_code=200,
            mimetype="application/json"
        )

    except Exception as e:
        logging.error(f"Simple test function failed: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": f"Test function error: {str(e)}"}),
            status_code=500,
            mimetype="application/json"
        )