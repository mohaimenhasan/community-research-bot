import azure.functions as func
import json
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List
import sys
import os

# Add the function_app directory to the path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.storage_client import ContentStorageClient
from shared.vector_client import VectorSearchClient

def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    User Profile and Personalization Function
    GET /api/user_profile/{user_id} - Get user profile and preferences
    POST /api/user_profile - Create new user profile
    PUT /api/user_profile/{user_id} - Update user profile or record interaction
    """

    logging.info('User profile function processed a request.')

    try:
        method = req.method
        user_id = req.route_params.get('user_id')

        storage_client = ContentStorageClient()

        if method == 'GET':
            return handle_get_profile(req, storage_client, user_id)
        elif method == 'POST':
            return handle_create_profile(req, storage_client)
        elif method == 'PUT':
            return handle_update_profile(req, storage_client, user_id)
        else:
            return func.HttpResponse(
                json.dumps({"error": "Method not allowed"}),
                status_code=405,
                mimetype="application/json"
            )

    except Exception as e:
        logging.error(f"User profile function failed: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": "User profile service temporarily unavailable"}),
            status_code=500,
            mimetype="application/json"
        )

def handle_get_profile(req: func.HttpRequest, storage_client: ContentStorageClient,
                      user_id: str) -> func.HttpResponse:
    """Get user profile and personalized content recommendations"""
    try:
        if not user_id:
            return func.HttpResponse(
                json.dumps({"error": "User ID is required"}),
                status_code=400,
                mimetype="application/json"
            )

        # Get user profile from storage
        profile = get_user_profile(storage_client, user_id)

        if not profile:
            return func.HttpResponse(
                json.dumps({"error": "User profile not found"}),
                status_code=404,
                mimetype="application/json"
            )

        # Get personalized content recommendations
        include_recommendations = req.params.get('include_recommendations', 'true').lower() == 'true'

        if include_recommendations:
            recommendations = get_personalized_recommendations(profile)
            profile['recommendations'] = recommendations

        return func.HttpResponse(
            json.dumps(profile),
            status_code=200,
            mimetype="application/json",
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, PUT, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type"
            }
        )

    except Exception as e:
        logging.error(f"Failed to get user profile: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": "Failed to retrieve user profile"}),
            status_code=500,
            mimetype="application/json"
        )

def handle_create_profile(req: func.HttpRequest, storage_client: ContentStorageClient) -> func.HttpResponse:
    """Create new user profile"""
    try:
        req_body = req.get_json()
        if not req_body:
            return func.HttpResponse(
                json.dumps({"error": "Request body is required"}),
                status_code=400,
                mimetype="application/json"
            )

        # Validate required fields
        required_fields = ['user_id', 'primary_location']
        missing_fields = [field for field in required_fields if field not in req_body]

        if missing_fields:
            return func.HttpResponse(
                json.dumps({"error": f"Missing required fields: {missing_fields}"}),
                status_code=400,
                mimetype="application/json"
            )

        user_id = req_body['user_id']

        # Check if profile already exists
        existing_profile = get_user_profile(storage_client, user_id)
        if existing_profile:
            return func.HttpResponse(
                json.dumps({"error": "User profile already exists"}),
                status_code=409,
                mimetype="application/json"
            )

        # Create new profile
        profile = {
            'id': user_id,
            'user_id': user_id,
            'primary_location': req_body['primary_location'],
            'additional_locations': req_body.get('additional_locations', []),
            'interests': req_body.get('interests', []),
            'categories': req_body.get('categories', ['news', 'events', 'community']),
            'notification_preferences': req_body.get('notification_preferences', {
                'email': True,
                'push': True,
                'frequency': 'daily'
            }),
            'content_preferences': {
                'max_articles_per_day': req_body.get('max_articles_per_day', 10),
                'preferred_time_slots': req_body.get('preferred_time_slots', ['morning', 'evening']),
                'content_length': req_body.get('content_length', 'medium')
            },
            'interaction_history': [],
            'engagement_score': 0.0,
            'created_at': datetime.now(timezone.utc).isoformat(),
            'updated_at': datetime.now(timezone.utc).isoformat()
        }

        # Store profile
        success = store_user_profile(storage_client, profile)

        if success:
            return func.HttpResponse(
                json.dumps({
                    "message": "User profile created successfully",
                    "user_id": user_id,
                    "profile": profile
                }),
                status_code=201,
                mimetype="application/json"
            )
        else:
            return func.HttpResponse(
                json.dumps({"error": "Failed to create user profile"}),
                status_code=500,
                mimetype="application/json"
            )

    except Exception as e:
        logging.error(f"Failed to create user profile: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": "Failed to create user profile"}),
            status_code=500,
            mimetype="application/json"
        )

def handle_update_profile(req: func.HttpRequest, storage_client: ContentStorageClient,
                         user_id: str) -> func.HttpResponse:
    """Update user profile or record interaction"""
    try:
        if not user_id:
            return func.HttpResponse(
                json.dumps({"error": "User ID is required"}),
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

        # Get existing profile
        profile = get_user_profile(storage_client, user_id)
        if not profile:
            return func.HttpResponse(
                json.dumps({"error": "User profile not found"}),
                status_code=404,
                mimetype="application/json"
            )

        update_type = req_body.get('update_type', 'profile')

        if update_type == 'interaction':
            # Record user interaction for personalization
            interaction = {
                'content_id': req_body.get('content_id'),
                'action': req_body.get('action'),  # 'view', 'save', 'share', 'like', 'dismiss'
                'category': req_body.get('category'),
                'location': req_body.get('location'),
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'engagement_time': req_body.get('engagement_time', 0)
            }

            # Add interaction to history
            if 'interaction_history' not in profile:
                profile['interaction_history'] = []

            profile['interaction_history'].append(interaction)

            # Limit history size (keep last 1000 interactions)
            if len(profile['interaction_history']) > 1000:
                profile['interaction_history'] = profile['interaction_history'][-1000:]

            # Update engagement score based on interaction
            profile['engagement_score'] = calculate_engagement_score(profile['interaction_history'])

            # Update interests based on interactions
            profile['interests'] = update_interests_from_interactions(profile['interaction_history'])

        else:
            # Update profile settings
            updatable_fields = [
                'additional_locations', 'interests', 'categories',
                'notification_preferences', 'content_preferences'
            ]

            for field in updatable_fields:
                if field in req_body:
                    profile[field] = req_body[field]

        profile['updated_at'] = datetime.now(timezone.utc).isoformat()

        # Store updated profile
        success = store_user_profile(storage_client, profile)

        if success:
            return func.HttpResponse(
                json.dumps({
                    "message": "User profile updated successfully",
                    "user_id": user_id,
                    "update_type": update_type,
                    "engagement_score": profile.get('engagement_score', 0.0)
                }),
                status_code=200,
                mimetype="application/json"
            )
        else:
            return func.HttpResponse(
                json.dumps({"error": "Failed to update user profile"}),
                status_code=500,
                mimetype="application/json"
            )

    except Exception as e:
        logging.error(f"Failed to update user profile: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": "Failed to update user profile"}),
            status_code=500,
            mimetype="application/json"
        )

def get_user_profile(storage_client: ContentStorageClient, user_id: str) -> Dict[str, Any]:
    """Get user profile from storage"""
    try:
        # In a full implementation, this would use the users_container
        # For now, returning a placeholder implementation
        container = storage_client.users_container
        return container.read_item(item=user_id, partition_key=user_id)
    except Exception:
        return None

def store_user_profile(storage_client: ContentStorageClient, profile: Dict[str, Any]) -> bool:
    """Store user profile to storage"""
    try:
        container = storage_client.users_container
        container.upsert_item(profile)
        return True
    except Exception as e:
        logging.error(f"Failed to store user profile: {str(e)}")
        return False

def get_personalized_recommendations(profile: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Get personalized content recommendations for user"""
    try:
        vector_client = VectorSearchClient()

        recommendations = []

        # Get content based on primary location and interests
        primary_location = profile.get('primary_location')
        interests = profile.get('interests', [])

        if primary_location:
            # Get recent content for primary location
            recent_content = vector_client.get_recent_content(primary_location, hours=48, top=10)
            recommendations.extend(recent_content)

            # Get content by categories of interest
            categories = profile.get('categories', [])
            for category in categories[:3]:  # Limit to top 3 categories
                category_content = vector_client.search_by_category(category, primary_location, top=5)
                recommendations.extend(category_content)

        # Remove duplicates and limit results
        seen_ids = set()
        unique_recommendations = []
        for item in recommendations:
            if item.get('id') not in seen_ids:
                seen_ids.add(item.get('id'))
                unique_recommendations.append(item)

        # Limit to reasonable number
        return unique_recommendations[:20]

    except Exception as e:
        logging.error(f"Failed to get recommendations: {str(e)}")
        return []

def calculate_engagement_score(interactions: List[Dict[str, Any]]) -> float:
    """Calculate user engagement score based on interaction history"""
    if not interactions:
        return 0.0

    # Weight different actions
    action_weights = {
        'view': 1.0,
        'save': 3.0,
        'share': 4.0,
        'like': 2.0,
        'dismiss': -1.0
    }

    total_score = 0.0
    total_interactions = 0

    for interaction in interactions[-100:]:  # Consider last 100 interactions
        action = interaction.get('action', 'view')
        weight = action_weights.get(action, 1.0)
        engagement_time = interaction.get('engagement_time', 0)

        # Factor in engagement time
        time_multiplier = min(engagement_time / 30.0, 2.0)  # Cap at 2x for 30+ seconds

        score = weight * (1 + time_multiplier)
        total_score += score
        total_interactions += 1

    return total_score / max(total_interactions, 1)

def update_interests_from_interactions(interactions: List[Dict[str, Any]]) -> List[str]:
    """Update user interests based on interaction patterns"""
    category_scores = {}

    for interaction in interactions[-50:]:  # Consider last 50 interactions
        category = interaction.get('category')
        action = interaction.get('action', 'view')

        if category:
            if category not in category_scores:
                category_scores[category] = 0

            # Weight positive interactions more
            if action in ['save', 'share', 'like']:
                category_scores[category] += 2
            elif action == 'view':
                category_scores[category] += 1
            elif action == 'dismiss':
                category_scores[category] -= 1

    # Return top categories as interests
    sorted_categories = sorted(category_scores.items(), key=lambda x: x[1], reverse=True)
    return [category for category, score in sorted_categories[:5] if score > 0]