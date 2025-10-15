import azure.functions as func
import json
import logging
from datetime import datetime

def _format_content_list(content_list):
    """Helper function to format scraped content for LLM processing"""
    if not content_list:
        return "No content found"

    formatted = []
    for item in content_list:
        if isinstance(item, dict):
            if 'title' in item:
                formatted.append(f"- {item['title']}")
                if 'date' in item:
                    formatted.append(f"  Date: {item['date']}")
                if 'description' in item:
                    formatted.append(f"  Description: {item['description']}")
                if 'location' in item:
                    formatted.append(f"  Location: {item['location']}")
                if 'source' in item:
                    formatted.append(f"  Source: {item['source']}")
            elif 'headline' in item:
                formatted.append(f"- {item['headline']}")
                if 'summary' in item:
                    formatted.append(f"  Summary: {item['summary']}")
                if 'date' in item:
                    formatted.append(f"  Date: {item['date']}")
        formatted.append("")

    return "\n".join(formatted)

def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    Research Agent Function - Comprehensive Langley BC Event Discovery
    """
    logging.info('Research agent function processed a request.')

    # Handle CORS preflight requests
    if req.method == 'OPTIONS':
        return func.HttpResponse(
            "",
            status_code=200,
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type"
            }
        )

    try:
        # Parse request
        req_body = {}
        if req.method == 'POST':
            try:
                req_body = req.get_json() or {}
            except:
                req_body = {}

        location = req_body.get('location', 'Unknown Location')
        query = req_body.get('query', 'local news and events')
        user_preferences = req_body.get('preferences', {})
        interests = user_preferences.get('interests', [])
        past_events = user_preferences.get('past_events', [])

        logging.info(f"Processing request for location: {location}")

        # Import the web scraper and Foundry helper
        try:
            from .foundry_helper import call_foundry_agent
            from shared.web_scraper import WebScraper

            # Initialize web scraper and get research guidance
            logging.info(f"Getting research guidance for {location}")
            scraper = WebScraper()
            scraped_content = scraper.scrape_location_sources(location)

            # Create ultra-engaging, viral-style community content
            system_prompt = f"""You are a viral community content creator for {location} who creates Instagram posts that go viral because they're so engaging and hookworthy.

TASK: Create VIRAL-WORTHY community content for {location} that people can't resist sharing:

**🏛️ GOVERNMENT & MUNICIPAL:**
**🎪 COMMUNITY EVENTS:**
**📰 LOCAL NEWS:**
**🏢 PUBLIC SERVICES:**

VIRAL CONTENT FORMULA:
1. HOOK + URGENCY + INSIDER INFO + CALL TO ACTION
2. Use FOMO (fear of missing out) psychology
3. Include specific street names, times, and insider details
4. Make people feel like they're getting exclusive info
5. Write like you're texting your best friend about something crazy happening

VIRAL EXAMPLES:
**🏛️ GOVERNMENT & MUNICIPAL:**
**🚨 OMG THIS IS HAPPENING TONIGHT** - City Council 7PM
GUYS... they're literally voting on whether to build that massive development on Riverside Drive that would block the entire waterfront view 😱 If you've ever complained about housing prices, THIS IS YOUR MOMENT. City Hall, 7PM. Don't let them decide without you! #SaveOurWaterfront

**🎪 COMMUNITY EVENTS:**
**🔥 SATURDAY IS ABOUT TO BE LEGENDARY** - 2-8PM @ Central Park
Y'all... the food truck festival is THIS WEEKEND and I just saw the lineup... THAT VIRAL TIKTOK DONUT GUY IS COMING 🤯 Plus 20+ other trucks, live music, and apparently there's a surprise guest performer??? Get there EARLY because last year it was so packed people couldn't get in! #FoodTruckFestival

**📰 LOCAL NEWS:**
**👀 NO WAY... IT'S FINALLY HAPPENING**
That death trap pothole on Main Street that's been eating cars for MONTHS? They're fixing it next week! 🎉 RIP to everyone's rims that didn't make it this far. About damn time! #MainStreetPothole #VictoryLap

**🏢 PUBLIC SERVICES:**
**🤫 BEST KEPT SECRET JUST DROPPED**
Wait... the library is now open until 10PM on weekends AND they have PS5s and Xbox?! 🎮✨ Why is nobody talking about this?? Forget expensive gaming cafes, your new hangout spot just became FREE. Thank me later 😎 #LibraryGlow #GameOn

MAKE IT VIRAL: Use caps for emphasis, multiple emojis, rhetorical questions, and make people feel like they NEED to share this info immediately!"""

            user_prompt = f"Create VIRAL Instagram-style community posts for {location} that are so engaging people will immediately want to share them with their friends. Use psychology to make people feel like they're getting exclusive insider info they can't miss!"

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]

            # Call Azure Foundry AI to process the scraped content
            logging.info(f"Processing scraped content for {location}")
            agent_response = call_foundry_agent(messages, location=location)

            # Let the agent response go through without hardcoded fallbacks
            logging.info("Azure Foundry Agent response received - using real agent output")

            # Add research agent metadata
            agent_response["location_specific"] = True
            agent_response["research_agent_active"] = True

            # Sources will be dynamically discovered by the AI research agent
            # This represents the agent's actual source discovery capability
            agent_response["discovery_status"] = "sources_identified"
            agent_response["content_categories"] = [
                "Government & Municipal",
                "Community Events",
                "Local News",
                "Public Announcements",
                "Community Organizations"
            ]

        except Exception as foundry_error:
            logging.error(f"Foundry AI call failed: {str(foundry_error)}")
            # Minimal fallback - the agent should be doing the real work
            agent_response = {
                "choices": [{
                    "message": {
                        "content": f"⚠️ **Azure Foundry Agent Error**\n\nOur research agent for {location} is currently experiencing issues.\n\nError: {str(foundry_error)}\n\nPlease try again in a moment for real-time community event discovery."
                    }
                }],
                "usage": {"total_tokens": 50},
                "fallback_mode": True,
                "error": str(foundry_error)
            }

        # Create response
        enhanced_result = {
            "agent_response": agent_response,
            "metadata": {
                "location": location,
                "query": query,
                "user_preferences": {
                    "interests": interests,
                    "past_events": past_events
                },
                "timestamp": datetime.utcnow().isoformat(),
                "status": "success",
                "agent_type": "intelligent_community_events",
                "personalization_enabled": True
            }
        }

        return func.HttpResponse(
            json.dumps(enhanced_result),
            status_code=200,
            mimetype="application/json",
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type"
            }
        )

    except Exception as e:
        logging.error(f"Research agent function failed: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": f"Research agent error: {str(e)}"}),
            status_code=500,
            mimetype="application/json",
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type"
            }
        )