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
            # Return sample sources for testing
            sources = [
                {
                    "url": "https://vancouver.ca/news-calendar.aspx",
                    "location": "Vancouver",
                    "category": "government"
                },
                {
                    "url": "https://www.cbc.ca/news/canada/british-columbia",
                    "location": "Vancouver",
                    "category": "news"
                }
            ]

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

        mock_content = f"Sample content from {source['url']} for {source['location']} in category {source['category']}. This is a test crawl result with sufficient content length to meet the 50 character minimum requirement."

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