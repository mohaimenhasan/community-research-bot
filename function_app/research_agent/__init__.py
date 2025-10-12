import azure.functions as func
import json
import logging
from datetime import datetime
import sys
import os

# Add the function_app directory to the path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.foundry_client import FoundryClient
from shared.vector_client import VectorSearchClient
from shared.storage_client import ContentStorageClient

def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    Enhanced Research Agent Function with Vector Search Context
    POST /api/research_agent
    Accepts: {"location": "Vancouver", "query": "community events", "use_context": true}
    Returns: Enhanced agent response with local context
    """

    logging.info('Enhanced research agent function processed a request.')

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
        query = req_body.get('query', 'local news and events')
        use_context = req_body.get('use_context', True)

        # Initialize clients
        foundry_client = FoundryClient()

        context_text = "No local context available."
        context_sources = 0

        # Get contextual information if requested
        if use_context:
            try:
                vector_client = VectorSearchClient()
                context_results = vector_client.search_community_content(location, query, top=5)

                if context_results:
                    context_text = "\n".join([
                        f"- {item.get('title', 'Untitled')}: {item.get('content', '')[:200]}..."
                        for item in context_results
                    ])
                    context_sources = len(context_results)
                    logging.info(f"Found {context_sources} context items for {location}")
                else:
                    context_text = f"No recent local content found for {location}."

            except Exception as e:
                logging.warning(f"Vector search failed: {str(e)}")
                context_text = "Vector search temporarily unavailable."

        # Prepare messages for the agent
        messages = [
            {
                "role": "system",
                "content": f"""You are a community research agent specializing in {location}.

Use the following local context when available: {context_text}

Your task is to research and provide comprehensive information about community activities, local news, events, and developments in {location}. Focus on:
1. Recent community events and initiatives
2. Local government updates and decisions
3. Business openings, closings, or significant changes
4. Community groups and organizations
5. Infrastructure or development projects
6. Cultural and social happenings

Provide sources when possible and prioritize recent, relevant information."""
            },
            {
                "role": "user",
                "content": f"Research and summarize current information about {query} in {location}. Provide a comprehensive overview of what's happening in the community."
            }
        ]

        # Define tools for the agent
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "search_web",
                    "description": "Search the web for current information about a location and topic",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string"},
                            "location": {"type": "string"}
                        },
                        "required": ["query", "location"]
                    }
                }
            }
        ]

        # Call the Foundry agent
        result = foundry_client.call_agent(messages, tools)

        # Store successful research for future context
        try:
            storage_client = ContentStorageClient()
            research_item = {
                'id': f"research_{location}_{datetime.utcnow().isoformat()}",
                'title': f"Research: {query} in {location}",
                'content': json.dumps(result),
                'source': 'research_agent',
                'category': 'research',
                'location': location,
                'date': datetime.utcnow().isoformat(),
                'url': f"internal://research/{location}"
            }

            vector_client = VectorSearchClient()
            vector_client.store_content(research_item)

        except Exception as e:
            logging.warning(f"Failed to store research results: {str(e)}")

        # Enhanced response
        enhanced_result = {
            "agent_response": result,
            "metadata": {
                "context_sources": context_sources,
                "location": location,
                "query": query,
                "timestamp": datetime.utcnow().isoformat(),
                "context_used": use_context
            }
        }

        return func.HttpResponse(
            json.dumps(enhanced_result),
            status_code=200,
            mimetype="application/json"
        )

    except ValueError as e:
        logging.error(f"Configuration error: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": f"Configuration error: {str(e)}"}),
            status_code=500,
            mimetype="application/json"
        )
    except Exception as e:
        logging.error(f"Research agent function failed: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": "Research service temporarily unavailable"}),
            status_code=502,
            mimetype="application/json"
        )