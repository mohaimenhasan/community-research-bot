import azure.functions as func
import json
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Tuple
import sys
import os

# Add the function_app directory to the path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.storage_client import ContentStorageClient
from shared.vector_client import VectorSearchClient

def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    Geographic Content Distribution Function
    POST /api/content_distribution
    Accepts: {"content_id": "...", "current_location": "Local", "engagement_stats": {...}}
    Implements viral content algorithm based on engagement thresholds
    """

    logging.info('Content distribution function processed a request.')

    try:
        req_body = req.get_json()
        if not req_body:
            return func.HttpResponse(
                json.dumps({"error": "Request body is required"}),
                status_code=400,
                mimetype="application/json"
            )

        # Validate required fields
        content_id = req_body.get('content_id')
        current_location = req_body.get('current_location')
        engagement_stats = req_body.get('engagement_stats', {})

        if not content_id or not current_location:
            return func.HttpResponse(
                json.dumps({"error": "content_id and current_location are required"}),
                status_code=400,
                mimetype="application/json"
            )

        # Initialize clients
        storage_client = ContentStorageClient()
        vector_client = VectorSearchClient()

        # Determine if content should spread based on engagement
        should_spread, next_level = should_content_spread(current_location, engagement_stats)

        distribution_result = {
            "content_id": content_id,
            "current_location": current_location,
            "engagement_stats": engagement_stats,
            "should_spread": should_spread,
            "next_level": next_level,
            "distribution_actions": [],
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

        if should_spread and next_level:
            # Get neighboring locations for the next level
            neighboring_locations = get_neighboring_locations(current_location, next_level)

            # Distribute content to neighboring locations
            for location in neighboring_locations:
                success = distribute_to_location(content_id, location, storage_client, vector_client)

                distribution_result["distribution_actions"].append({
                    "target_location": location,
                    "success": success,
                    "action": "content_distributed"
                })

        return func.HttpResponse(
            json.dumps(distribution_result),
            status_code=200,
            mimetype="application/json"
        )

    except Exception as e:
        logging.error(f"Content distribution function failed: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": "Content distribution service temporarily unavailable"}),
            status_code=500,
            mimetype="application/json"
        )

def should_content_spread(current_location: str, engagement_stats: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Determine if content should spread based on engagement thresholds

    Thresholds:
    - Local: 25% user selection
    - Local+: 20% user selection
    - Regional: 15% user selection
    - Provincial: 10% user selection
    - Federal: 5% user selection
    """

    # Define location hierarchy and thresholds
    location_hierarchy = {
        "Local": {"threshold": 0.25, "next": "Local+"},
        "Local+": {"threshold": 0.20, "next": "Regional"},
        "Regional": {"threshold": 0.15, "next": "Provincial"},
        "Provincial": {"threshold": 0.10, "next": "Federal"},
        "Federal": {"threshold": 0.05, "next": None}
    }

    if current_location not in location_hierarchy:
        logging.warning(f"Unknown location level: {current_location}")
        return False, None

    # Calculate engagement rate
    total_users = engagement_stats.get('total_users', 0)
    engaged_users = engagement_stats.get('engaged_users', 0)

    if total_users == 0:
        return False, None

    engagement_rate = engaged_users / total_users
    required_threshold = location_hierarchy[current_location]["threshold"]

    logging.info(f"Content engagement: {engagement_rate:.2%} (required: {required_threshold:.2%})")

    if engagement_rate >= required_threshold:
        next_level = location_hierarchy[current_location]["next"]
        return True, next_level

    return False, None

def get_neighboring_locations(current_location: str, target_level: str) -> List[str]:
    """
    Get neighboring locations for content distribution
    In a full implementation, this would use a geographic database
    """

    # Simplified neighboring location mapping
    # In production, this would be a proper geographic hierarchy database
    location_mapping = {
        "Vancouver": {
            "Local+": ["Burnaby", "Richmond", "North Vancouver", "West Vancouver"],
            "Regional": ["Surrey", "Langley", "Coquitlam", "New Westminster"],
            "Provincial": ["Victoria", "Kelowna", "Prince George"],
            "Federal": ["Seattle", "Portland", "Calgary"]
        },
        "Toronto": {
            "Local+": ["Mississauga", "Brampton", "Markham", "Vaughan"],
            "Regional": ["Hamilton", "London", "Kitchener", "Oshawa"],
            "Provincial": ["Ottawa", "Thunder Bay", "Sudbury"],
            "Federal": ["Montreal", "Detroit", "Buffalo"]
        },
        "Montreal": {
            "Local+": ["Laval", "Longueuil", "Gatineau"],
            "Regional": ["Quebec City", "Sherbrooke", "Trois-Rivières"],
            "Provincial": ["Toronto", "Ottawa"],
            "Federal": ["Boston", "New York", "Burlington"]
        }
    }

    # Extract base city from location if it contains more specific info
    base_location = current_location.split(",")[0].strip()

    neighbors = location_mapping.get(base_location, {}).get(target_level, [])

    logging.info(f"Found {len(neighbors)} neighboring locations for {current_location} -> {target_level}")

    return neighbors

def distribute_to_location(content_id: str, target_location: str,
                         storage_client: ContentStorageClient,
                         vector_client: VectorSearchClient) -> bool:
    """Distribute content to a target location"""
    try:
        # Get original content
        original_content = get_content_by_id(content_id, vector_client)

        if not original_content:
            logging.error(f"Original content not found: {content_id}")
            return False

        # Create distributed content item
        distributed_content = {
            "id": f"{content_id}_distributed_{target_location}_{datetime.now(timezone.utc).isoformat()}",
            "title": original_content.get("title", ""),
            "content": original_content.get("content", ""),
            "source": original_content.get("source", ""),
            "category": original_content.get("category", ""),
            "location": target_location,  # Updated location
            "date": datetime.now(timezone.utc).isoformat(),
            "url": original_content.get("url", ""),
            "original_content_id": content_id,
            "distribution_type": "viral_spread",
            "sentiment": original_content.get("sentiment", "neutral")
        }

        # Store in vector search for the new location
        success = vector_client.store_content(distributed_content)

        if success:
            # Add to editorial queue for the target location
            editorial_success = storage_client.add_to_editorial_queue({
                'source_url': original_content.get('url', ''),
                'location': target_location,
                'processed_content': {
                    'title': distributed_content['title'],
                    'summary': distributed_content['content'],
                    'category': distributed_content['category'],
                    'significance': 'high',  # Viral content is significant
                    'original_location': original_content.get('location', ''),
                    'distribution_reason': 'viral_engagement'
                },
                'priority': 'high'  # Viral content gets high priority
            })

            logging.info(f"Distributed content {content_id} to {target_location}")
            return success and editorial_success

        return False

    except Exception as e:
        logging.error(f"Failed to distribute content to {target_location}: {str(e)}")
        return False

def get_content_by_id(content_id: str, vector_client: VectorSearchClient) -> Dict[str, Any]:
    """Get content by ID from vector search"""
    try:
        # In a full implementation, this would query by document ID
        # For now, using a search approach
        results = vector_client.client.search(
            search_text="*",
            filter=f"id eq '{content_id}'",
            top=1
        )

        content_list = list(results)
        return dict(content_list[0]) if content_list else None

    except Exception as e:
        logging.error(f"Failed to get content by ID {content_id}: {str(e)}")
        return None

def calculate_engagement_metrics(content_id: str, location: str) -> Dict[str, Any]:
    """
    Calculate engagement metrics for content in a location
    This would typically be called by a separate analytics function
    """
    # Placeholder implementation
    # In production, this would query user interaction data
    return {
        "total_users": 1000,
        "engaged_users": 300,  # 30% engagement
        "views": 1500,
        "saves": 150,
        "shares": 50,
        "engagement_rate": 0.30
    }