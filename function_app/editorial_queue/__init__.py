import azure.functions as func
import json
import logging
import os
from datetime import datetime, timezone
from typing import Dict, Any, List

def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    Editorial Queue Management Function - Simplified version
    GET /api/editorial_queue/{location} - Get queue items for location
    POST /api/editorial_queue/{location} - Add item to queue
    PUT /api/editorial_queue/{location} - Update item status
    """

    logging.info('Editorial queue function processed a request.')

    try:
        method = req.method
        location = req.route_params.get('location', 'Vancouver')

        if method == 'GET':
            return handle_get_queue_simple(req, location)
        elif method == 'POST':
            return handle_add_to_queue_simple(req, location)
        elif method == 'PUT':
            return handle_update_queue_item_simple(req, location)
        else:
            return func.HttpResponse(
                json.dumps({"error": "Method not allowed"}),
                status_code=405,
                mimetype="application/json"
            )

    except Exception as e:
        logging.error(f"Editorial queue function failed: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": f"Editorial queue service error: {str(e)}"}),
            status_code=500,
            mimetype="application/json"
        )

def handle_get_queue_simple(req: func.HttpRequest, location: str) -> func.HttpResponse:
    """Get editorial queue items for a location - simplified version"""
    try:
        # Get query parameters
        status = req.params.get('status', 'pending')
        limit = min(int(req.params.get('limit', 50)), 100)

        # Return mock queue items for testing
        mock_items = [
            {
                "id": f"item_1_{location}",
                "title": f"Community Event in {location}",
                "content": f"Sample content for editorial review in {location}",
                "status": status,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "priority": "normal",
                "category": "community"
            },
            {
                "id": f"item_2_{location}",
                "title": f"Local News from {location}",
                "content": f"Another sample content item for {location}",
                "status": status,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "priority": "high",
                "category": "news"
            }
        ]

        # Limit results
        limited_items = mock_items[:limit]

        response = {
            "location": location,
            "status_filter": status,
            "items": limited_items,
            "count": len(limited_items),
            "statistics": {
                "pending": 5,
                "approved": 12,
                "rejected": 2,
                "total": 19
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "mock_data": True
        }

        return func.HttpResponse(
            json.dumps(response),
            status_code=200,
            mimetype="application/json"
        )

    except Exception as e:
        logging.error(f"Failed to get editorial queue: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": "Failed to retrieve queue items"}),
            status_code=500,
            mimetype="application/json"
        )

def handle_add_to_queue_simple(req: func.HttpRequest, location: str) -> func.HttpResponse:
    """Add new item to editorial queue - simplified version"""
    try:
        req_body = req.get_json()
        if not req_body:
            return func.HttpResponse(
                json.dumps({"error": "Request body is required"}),
                status_code=400,
                mimetype="application/json"
            )

        # Validate required fields
        title = req_body.get('title', 'Untitled')
        content = req_body.get('content', 'No content')

        # Mock successful addition
        new_item_id = f"item_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}_{location}"

        return func.HttpResponse(
            json.dumps({
                "message": "Item added to editorial queue",
                "item_id": new_item_id,
                "location": location,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "mock_data": True
            }),
            status_code=201,
            mimetype="application/json"
        )

    except Exception as e:
        logging.error(f"Failed to add to editorial queue: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": "Failed to add item to queue"}),
            status_code=500,
            mimetype="application/json"
        )

def handle_update_queue_item_simple(req: func.HttpRequest, location: str) -> func.HttpResponse:
    """Update editorial queue item status - simplified version"""
    try:
        req_body = req.get_json()
        if not req_body:
            return func.HttpResponse(
                json.dumps({"error": "Request body is required"}),
                status_code=400,
                mimetype="application/json"
            )

        # Validate required fields
        item_id = req_body.get('item_id')
        new_status = req_body.get('status')

        if not item_id or not new_status:
            return func.HttpResponse(
                json.dumps({"error": "item_id and status are required"}),
                status_code=400,
                mimetype="application/json"
            )

        # Validate status
        valid_statuses = ['pending', 'approved', 'rejected', 'published', 'archived']
        if new_status not in valid_statuses:
            return func.HttpResponse(
                json.dumps({"error": f"Invalid status. Must be one of: {valid_statuses}"}),
                status_code=400,
                mimetype="application/json"
            )

        # Mock successful update
        response = {
            "message": "Queue item updated successfully",
            "item_id": item_id,
            "new_status": new_status,
            "location": location,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "mock_data": True
        }

        if new_status == 'approved':
            response["message"] += " and queued for publishing"

        return func.HttpResponse(
            json.dumps(response),
            status_code=200,
            mimetype="application/json"
        )

    except Exception as e:
        logging.error(f"Failed to update queue item: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": "Failed to update queue item"}),
            status_code=500,
            mimetype="application/json"
        )

def handle_get_queue(req: func.HttpRequest, storage_client: ContentStorageClient,
                    location: str) -> func.HttpResponse:
    """Get editorial queue items for a location"""
    try:
        if not location:
            return func.HttpResponse(
                json.dumps({"error": "Location parameter is required"}),
                status_code=400,
                mimetype="application/json"
            )

        # Get query parameters
        status = req.params.get('status', 'pending')
        limit = min(int(req.params.get('limit', 50)), 100)  # Max 100 items

        # Get queue items
        queue_items = storage_client.get_editorial_queue(location, status)

        # Limit results
        if len(queue_items) > limit:
            queue_items = queue_items[:limit]

        # Add summary statistics
        all_pending = storage_client.get_editorial_queue(location, 'pending')
        all_approved = storage_client.get_editorial_queue(location, 'approved')
        all_rejected = storage_client.get_editorial_queue(location, 'rejected')

        response = {
            "location": location,
            "status_filter": status,
            "items": queue_items,
            "count": len(queue_items),
            "statistics": {
                "pending": len(all_pending),
                "approved": len(all_approved),
                "rejected": len(all_rejected),
                "total": len(all_pending) + len(all_approved) + len(all_rejected)
            },
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

        return func.HttpResponse(
            json.dumps(response),
            status_code=200,
            mimetype="application/json"
        )

    except Exception as e:
        logging.error(f"Failed to get editorial queue: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": "Failed to retrieve queue items"}),
            status_code=500,
            mimetype="application/json"
        )

def handle_add_to_queue(req: func.HttpRequest, storage_client: ContentStorageClient,
                       location: str) -> func.HttpResponse:
    """Add new item to editorial queue"""
    try:
        if not location:
            return func.HttpResponse(
                json.dumps({"error": "Location parameter is required"}),
                status_code=400,
                mimetype="application/json"
            )

        req_body = req.get_json()
        if not req_body:
            return func.HttpResponse(
                json.dumps({"error": "Request body is required"}),
                status_code=400,
                mimetype="application/json"
            )

        # Validate required fields
        required_fields = ['title', 'content', 'source_url']
        missing_fields = [field for field in required_fields if field not in req_body]

        if missing_fields:
            return func.HttpResponse(
                json.dumps({"error": f"Missing required fields: {missing_fields}"}),
                status_code=400,
                mimetype="application/json"
            )

        # Prepare content item
        content_item = {
            'title': req_body['title'],
            'content': req_body['content'],
            'source_url': req_body['source_url'],
            'location': location,
            'category': req_body.get('category', 'general'),
            'priority': req_body.get('priority', 'normal'),
            'tags': req_body.get('tags', []),
            'submitted_by': req_body.get('submitted_by', 'system'),
            'submission_notes': req_body.get('notes', '')
        }

        # Add to queue
        success = storage_client.add_to_editorial_queue(content_item)

        if success:
            return func.HttpResponse(
                json.dumps({
                    "message": "Item added to editorial queue",
                    "location": location,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }),
                status_code=201,
                mimetype="application/json"
            )
        else:
            return func.HttpResponse(
                json.dumps({"error": "Failed to add item to queue"}),
                status_code=500,
                mimetype="application/json"
            )

    except Exception as e:
        logging.error(f"Failed to add to editorial queue: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": "Failed to add item to queue"}),
            status_code=500,
            mimetype="application/json"
        )

def handle_update_queue_item(req: func.HttpRequest, storage_client: ContentStorageClient,
                           location: str) -> func.HttpResponse:
    """Update editorial queue item status"""
    try:
        if not location:
            return func.HttpResponse(
                json.dumps({"error": "Location parameter is required"}),
                status_code=400,
                mimetype="application/json"
            )

        req_body = req.get_json()
        if not req_body:
            return func.HttpResponse(
                json.dumps({"error": "Request body is required"}),
                status_code=400,
                mimetype="application/json"
            )

        # Validate required fields
        item_id = req_body.get('item_id')
        new_status = req_body.get('status')

        if not item_id or not new_status:
            return func.HttpResponse(
                json.dumps({"error": "item_id and status are required"}),
                status_code=400,
                mimetype="application/json"
            )

        # Validate status
        valid_statuses = ['pending', 'approved', 'rejected', 'published', 'archived']
        if new_status not in valid_statuses:
            return func.HttpResponse(
                json.dumps({"error": f"Invalid status. Must be one of: {valid_statuses}"}),
                status_code=400,
                mimetype="application/json"
            )

        # Optional editor notes
        editor_notes = req_body.get('editor_notes')

        # Update item
        success = storage_client.update_queue_item_status(
            item_id, location, new_status, editor_notes
        )

        if success:
            response = {
                "message": "Queue item updated successfully",
                "item_id": item_id,
                "new_status": new_status,
                "location": location,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }

            # If approved, trigger publishing workflow
            if new_status == 'approved':
                response["message"] += " and queued for publishing"
                # In a full implementation, this would trigger the publishing function

            return func.HttpResponse(
                json.dumps(response),
                status_code=200,
                mimetype="application/json"
            )
        else:
            return func.HttpResponse(
                json.dumps({"error": "Failed to update queue item"}),
                status_code=500,
                mimetype="application/json"
            )

    except Exception as e:
        logging.error(f"Failed to update queue item: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": "Failed to update queue item"}),
            status_code=500,
            mimetype="application/json"
        )