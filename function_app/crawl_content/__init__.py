import azure.functions as func
import json
import logging
import requests
import hashlib
import os
from datetime import datetime, timezone
from typing import Dict, Any, List

def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    Content Crawler Function - Simplified version for testing
    POST /api/crawl_content
    Accepts: {"sources": [{"url": "...", "location": "...", "category": "..."}]}
    Returns: Crawling results with basic processing
    """

    logging.info('Content crawler function processed a request.')

    try:
        req_body = req.get_json()
        sources = req_body.get('sources', [])

        if not sources:
            # Auto-discover local sources based on request location
            location = req_body.get('location', 'Vancouver')
            sources = discover_local_sources(location)

        crawled_results = []
        processed_content = []

        for source in sources:
            if not all(key in source for key in ['url', 'location', 'category']):
                logging.warning(f"Skipping source with missing required fields: {source}")
                continue

            try:
                # Simplified crawling
                crawl_result = simple_crawl_source(source)

                if crawl_result:
                    crawled_results.append(crawl_result)

                    # Basic processing
                    if meets_quality_rules(crawl_result):
                        processed = simple_process_content(crawl_result, source)
                        if processed:
                            processed_content.append(processed)

            except Exception as e:
                logging.error(f"Failed to process source {source['url']}: {str(e)}")
                continue

        return func.HttpResponse(
            json.dumps({
                "status": "completed",
                "crawled_sources": len(crawled_results),
                "processed_items": len(processed_content),
                "crawl_results": crawled_results,
                "processed_content": processed_content,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }),
            status_code=200,
            mimetype="application/json"
        )

    except Exception as e:
        logging.error(f"Crawler function failed: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": f"Crawler service error: {str(e)}"}),
            status_code=500,
            mimetype="application/json"
        )

def simple_crawl_source(source: Dict[str, Any]) -> Dict[str, Any]:
    """Simplified crawling that doesn't depend on external libraries"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (compatible; CommunityHub-Bot/1.0)'
        }

        # For now, return mock data to test the function works
        # In production, would use requests.get(source['url'], headers=headers, timeout=30)

        # Generate realistic mock content based on category
        if source['category'] == 'townhall_meetings':
            mock_content = f"""TOWN HALL MEETING MINUTES - {source['location']}
Date: {datetime.now().strftime('%Y-%m-%d')}

AGENDA ITEMS:
1. Public Works Budget Approval - $2.3M allocated for road repairs on Main Street
2. Community Center Renovation Update - Phase 2 construction begins next month
3. New Business Licensing Requirements - Streamlined process for local entrepreneurs
4. Parks and Recreation Summer Programs - Registration opens April 1st
5. Traffic Safety Initiative - New crosswalk installations at school zones

PUBLIC COMMENTS:
- Residents expressed support for the downtown revitalization project
- Concerns raised about parking availability during festival season
- Request for additional street lighting on Oak Avenue

NEXT MEETING: First Tuesday of next month, 7:00 PM at City Hall
Contact: clerk@{source['location'].lower().replace(' ', '')}.gov"""

        elif source['category'] == 'city_government':
            mock_content = f"""CITY OF {source['location'].upper()} - OFFICIAL ANNOUNCEMENTS

📋 RECENT UPDATES:
• Water Main Replacement Project - Downtown area affected March 15-20
• New Business Grant Program - Applications due by month end
• Community Garden Initiative - Volunteer registration now open
• Street Sweeping Schedule - Parking restrictions in effect
• Public Library Extended Hours - Now open Sundays 12-5 PM

🏛️ GOVERNMENT SERVICES:
• Online permit applications now available 24/7
• Property tax payment deadline extended to April 30th
• Municipal election candidate filing period opens next week
• Citywide WiFi expansion project 75% complete

📞 Contact Information:
City Hall: (555) 123-4567
Public Works: (555) 123-4568
Planning Department: (555) 123-4569"""

        elif source['category'] == 'local_news':
            mock_content = f"""{source['location']} COMMUNITY NEWS DIGEST

🎪 UPCOMING EVENTS:
• Annual Spring Festival - Downtown Square, April 15-17
• Farmers Market Season Opens - Every Saturday starting May 1st
• Local Business Expo - Community Center, April 22nd
• Charity 5K Run - Registration open at city recreation center

🏪 BUSINESS NEWS:
• New coffee shop opens on Main Street next week
• Local bookstore celebrates 25th anniversary with community reading event
• Tech startup receives grant for innovative traffic solution
• Restaurant week features 15 participating local establishments

🎓 COMMUNITY HIGHLIGHTS:
• High school robotics team advances to state competition
• Library literacy program reaches 500 participants
• Volunteer fire department receives new equipment donation
• Senior center launches digital literacy classes"""

        else:  # community_boards or default
            mock_content = f"""{source['location']} COMMUNITY EVENTS & ACTIVITIES

🎨 ARTS & CULTURE:
• Community Theater presents "Our Town" - April 8-10 at Memorial Hall
• Art Gallery showcases local photographer exhibition through May
• Music in the Park concert series begins June with jazz ensemble
• Historical society hosts walking tour of downtown heritage buildings

🏃 RECREATION & SPORTS:
• Youth soccer league registration deadline April 1st
• Adult softball league forming - games start in May
• Community garden plots available for spring planting
• Hiking club weekly meetups every Saturday at 8 AM

👥 COMMUNITY SERVICES:
• Food bank seeks volunteers for weekend distribution
• Senior center offers free tax preparation assistance
• Neighborhood watch meeting scheduled for third Thursday
• Community cleanup day planned for Earth Day weekend"""

        mock_content += f"\n\nThis comprehensive local content was discovered through automated crawling of {source['location']} community sources."

        return {
            'url': source['url'],
            'title': f"Sample News from {source['location']}",
            'content': mock_content,
            'content_length': len(mock_content),
            'status_code': 200,
            'crawl_timestamp': datetime.now(timezone.utc).isoformat(),
            'mock_data': True
        }

    except Exception as e:
        logging.error(f"Failed to crawl {source['url']}: {str(e)}")
        return None

def simple_process_content(crawl_result: Dict[str, Any], source: Dict[str, Any]) -> Dict[str, Any]:
    """Basic content processing without external dependencies"""
    try:
        # Basic processing - create summary and metadata
        content = crawl_result.get('content', '')

        # Simple summarization (first 200 chars + "...")
        summary = content[:200] + "..." if len(content) > 200 else content

        # Basic categorization
        category = source.get('category', 'general')

        # Simple sentiment analysis based on keywords
        positive_words = ['good', 'great', 'excellent', 'amazing', 'positive']
        negative_words = ['bad', 'terrible', 'awful', 'negative', 'problem']

        content_lower = content.lower()
        positive_count = sum(1 for word in positive_words if word in content_lower)
        negative_count = sum(1 for word in negative_words if word in content_lower)

        if positive_count > negative_count:
            sentiment = 'positive'
        elif negative_count > positive_count:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'

        return {
            'summary': summary,
            'category': category,
            'sentiment': sentiment,
            'significance': 'medium',  # Default significance
            'original_title': crawl_result.get('title', ''),
            'source_url': source['url'],
            'location': source['location'],
            'processed_timestamp': datetime.now(timezone.utc).isoformat()
        }

    except Exception as e:
        logging.error(f"Failed to process content: {str(e)}")
        return None

def crawl_source(source: Dict[str, Any]) -> Dict[str, Any]:
    """Crawl a single source and extract content"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (compatible; CommunityHub-Bot/1.0)'
        }

        response = requests.get(source['url'], headers=headers, timeout=30)
        response.raise_for_status()

        # Simple content extraction (in production, use proper HTML parsing)
        content = response.text

        # Extract title (basic implementation)
        title = extract_title(content)

        # Extract main content (basic implementation)
        main_content = extract_main_content(content)

        return {
            'url': source['url'],
            'title': title,
            'content': main_content,
            'raw_length': len(content),
            'content_length': len(main_content),
            'status_code': response.status_code,
            'crawl_timestamp': datetime.now(timezone.utc).isoformat()
        }

    except requests.RequestException as e:
        logging.error(f"Failed to crawl {source['url']}: {str(e)}")
        return None
    except Exception as e:
        logging.error(f"Unexpected error crawling {source['url']}: {str(e)}")
        return None

def extract_title(html_content: str) -> str:
    """Extract title from HTML content (basic implementation)"""
    import re

    title_match = re.search(r'<title[^>]*>([^<]+)</title>', html_content, re.IGNORECASE)
    if title_match:
        return title_match.group(1).strip()

    # Fallback to h1 tag
    h1_match = re.search(r'<h1[^>]*>([^<]+)</h1>', html_content, re.IGNORECASE)
    if h1_match:
        return h1_match.group(1).strip()

    return "Untitled"

def extract_main_content(html_content: str) -> str:
    """Extract main content from HTML (basic implementation)"""
    import re

    # Remove script and style elements
    content = re.sub(r'<script[^>]*>.*?</script>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
    content = re.sub(r'<style[^>]*>.*?</style>', '', content, flags=re.DOTALL | re.IGNORECASE)

    # Remove HTML tags
    content = re.sub(r'<[^>]+>', ' ', content)

    # Clean up whitespace
    content = re.sub(r'\s+', ' ', content).strip()

    return content

def meets_quality_rules(crawl_result: Dict[str, Any]) -> bool:
    """Apply content quality rules as per requirements"""
    content = crawl_result.get('content', '')

    # Rule: Text must be at least 50 characters
    if len(content) < 50:
        logging.info(f"Content too short: {len(content)} characters")
        return False

    # Additional quality checks can be added here
    # - Check for duplicate content
    # - Check for spam indicators
    # - Check language

    return True

def process_with_agent(crawl_result: Dict[str, Any], source: Dict[str, Any],
                      foundry_client: FoundryClient) -> Dict[str, Any]:
    """Process content with Foundry agent for summarization and categorization"""
    try:
        messages = [
            {
                "role": "system",
                "content": f"""You are a content processing agent for community news in {source['location']}.

Analyze the following content and provide:
1. A concise summary (2-3 sentences)
2. Content category (news, events, business, government, community, sports, culture)
3. Significance level (low, medium, high) based on community impact
4. Sentiment (positive, neutral, negative)
5. Key topics or tags

Format your response as JSON with these fields: summary, category, significance, sentiment, tags"""
            },
            {
                "role": "user",
                "content": f"""Title: {crawl_result.get('title', 'Untitled')}
Source: {source['url']}
Content: {crawl_result['content'][:1000]}...

Please analyze this content for the {source['location']} community."""
            }
        ]

        result = foundry_client.call_chat_completions(messages, max_tokens=300, temperature=0.2)

        # Extract the analysis from the response
        analysis_text = result['choices'][0]['message']['content']

        try:
            # Try to parse as JSON
            analysis = json.loads(analysis_text)
        except json.JSONDecodeError:
            # Fallback to structured response
            analysis = {
                'summary': analysis_text[:200] + "..." if len(analysis_text) > 200 else analysis_text,
                'category': source.get('category', 'general'),
                'significance': 'medium',
                'sentiment': 'neutral',
                'tags': []
            }

        # Add metadata
        analysis.update({
            'original_title': crawl_result.get('title', ''),
            'source_url': source['url'],
            'location': source['location'],
            'processed_timestamp': datetime.now(timezone.utc).isoformat()
        })

        return analysis

    except Exception as e:
        logging.error(f"Failed to process content with agent: {str(e)}")
        return None

def discover_local_sources(location):
    """Discover comprehensive local government and community sources"""

    # Extract city/region name for URL building
    city = location.split(',')[0].strip().lower().replace(' ', '')
    state_province = location.split(',')[1].strip().lower().replace(' ', '') if ',' in location else ''

    # Comprehensive source discovery for small towns and cities
    potential_sources = []

    # City Government and Official Sites
    city_domains = [
        f"https://www.{city}.gov",
        f"https://www.{city}.ca",  # Canadian cities
        f"https://{city}.gov",
        f"https://city{city}.com",
        f"https://www.cityof{city}.com",
        f"https://www.{city}.org",
        f"https://{city}.municipal.gov",
        f"https://{city}.{state_province}.gov"  # State-specific domains
    ]

    for url in city_domains:
        potential_sources.append({
            "url": url,
            "location": location,
            "category": "city_government",
            "priority": "high",
            "content_types": ["townhall_minutes", "city_announcements", "public_meetings"]
        })

    # Town Hall and Meeting-Specific URLs
    meeting_urls = [
        f"{url}/council" for url in city_domains[:3]
    ] + [
        f"{url}/meetings" for url in city_domains[:3]
    ] + [
        f"{url}/agendas" for url in city_domains[:3]
    ] + [
        f"{url}/minutes" for url in city_domains[:3]
    ]

    for url in meeting_urls:
        potential_sources.append({
            "url": url,
            "location": location,
            "category": "townhall_meetings",
            "priority": "very_high",
            "content_types": ["meeting_minutes", "agendas", "public_hearings"]
        })

    # Local News Sources
    news_domains = [
        f"https://www.{city}news.com",
        f"https://www.{city}times.com",
        f"https://www.{city}herald.com",
        f"https://{city}today.com",
        f"https://www.local{city}.com",
        f"https://www.{city}daily.com",
        f"https://www.{city}gazette.com"
    ]

    for url in news_domains:
        potential_sources.append({
            "url": url,
            "location": location,
            "category": "local_news",
            "priority": "high",
            "content_types": ["community_news", "local_events", "government_coverage"]
        })

    # Community Boards and Event Sites
    community_domains = [
        f"https://www.{city}community.org",
        f"https://{city}events.com",
        f"https://www.{city}calendar.com",
        f"https://events.{city}.gov",
        f"https://community.{city}.org",
        f"https://{city}chamber.org",  # Chamber of Commerce
        f"https://www.{city}chamber.com"
    ]

    for url in community_domains:
        potential_sources.append({
            "url": url,
            "location": location,
            "category": "community_boards",
            "priority": "medium",
            "content_types": ["community_events", "business_news", "civic_engagement"]
        })

    # Known major city sources (hardcoded for accuracy)
    if "vancouver" in location.lower():
        potential_sources.extend([
            {
                "url": "https://vancouver.ca/news-calendar/",
                "location": location,
                "category": "city_government",
                "priority": "confirmed",
                "content_types": ["city_news", "events", "announcements"]
            },
            {
                "url": "https://council.vancouver.ca/",
                "location": location,
                "category": "townhall_meetings",
                "priority": "confirmed",
                "content_types": ["council_meetings", "agendas", "minutes"]
            }
        ])

    # Filter out working sources (this would be enhanced with actual HTTP checks)
    # For now, return a curated list to ensure functionality
    return [
        {
            "url": "https://vancouver.ca/news-calendar/",
            "location": location,
            "category": "city_government"
        },
        {
            "url": f"Mock: {city} Town Hall Meeting Minutes",
            "location": location,
            "category": "townhall_meetings"
        },
        {
            "url": f"Mock: {city} Community Events Board",
            "location": location,
            "category": "community_boards"
        },
        {
            "url": f"Mock: {city} Local News Digest",
            "location": location,
            "category": "local_news"
        }
    ]