import azure.functions as func
import json
import logging
import requests
import hashlib
from datetime import datetime, timezone
from typing import Dict, Any, List
import sys
import os

# Add the function_app directory to the path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.foundry_client import FoundryClient
from shared.vector_client import VectorSearchClient
from shared.storage_client import ContentStorageClient

def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    Content Crawler Function - Implements adaptive crawling with change detection
    POST /api/crawl_content
    Accepts: {"sources": [{"url": "...", "location": "...", "category": "..."}], "force_crawl": false}
    Returns: Crawling results with change detection and processed content
    """

    logging.info('Content crawler function processed a request.')

    try:
        req_body = req.get_json()
        sources = req_body.get('sources', [])
        force_crawl = req_body.get('force_crawl', False)

        if not sources:
            return func.HttpResponse(
                json.dumps({"error": "No sources provided for crawling"}),
                status_code=400,
                mimetype="application/json"
            )

        # Initialize clients
        storage_client = ContentStorageClient()
        vector_client = VectorSearchClient()
        foundry_client = FoundryClient()

        crawled_results = []
        processed_content = []

        for source in sources:
            if not all(key in source for key in ['url', 'location', 'category']):
                logging.warning(f"Skipping source with missing required fields: {source}")
                continue

            try:
                # Crawl the source
                crawl_result = crawl_source(source)

                if not crawl_result:
                    continue

                # Store content snapshot and detect changes
                snapshot = storage_client.store_content_snapshot(
                    url=source['url'],
                    content=crawl_result['content'],
                    metadata={
                        'title': crawl_result.get('title', ''),
                        'location': source['location'],
                        'category': source['category'],
                        'crawl_timestamp': datetime.now(timezone.utc).isoformat()
                    }
                )

                crawl_result['has_changed'] = snapshot['has_changed']
                crawled_results.append(crawl_result)

                # Process content if it has changed or force_crawl is enabled
                if snapshot['has_changed'] or force_crawl:
                    # Apply content quality rules
                    if meets_quality_rules(crawl_result):
                        # Process with Foundry agent
                        processed = process_with_agent(crawl_result, source, foundry_client)

                        if processed:
                            # Store in vector search for future context
                            vector_item = {
                                'id': f"{source['url']}_{datetime.now(timezone.utc).isoformat()}",
                                'title': crawl_result.get('title', 'Untitled'),
                                'content': processed['summary'],
                                'source': source['url'],
                                'category': processed['category'],
                                'location': source['location'],
                                'date': datetime.now(timezone.utc).isoformat(),
                                'url': source['url'],
                                'sentiment': processed.get('sentiment', 'neutral')
                            }

                            vector_client.store_content(vector_item)

                            # Add to editorial queue if significant
                            if processed.get('significance', 'low') in ['medium', 'high']:
                                storage_client.add_to_editorial_queue({
                                    'source_url': source['url'],
                                    'location': source['location'],
                                    'processed_content': processed,
                                    'priority': 'high' if processed['significance'] == 'high' else 'normal'
                                })

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
            json.dumps({"error": "Crawler service temporarily unavailable"}),
            status_code=500,
            mimetype="application/json"
        )

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