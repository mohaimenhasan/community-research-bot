import azure.functions as func
import json
import requests
import logging

def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    Fetch News Function - Fetches news articles
    GET /api/fetch_news?topic=community
    Returns: [{"title": "...", "url": "...", "source": "..."}]
    """

    logging.info('Fetch news function processed a request.')

    try:
        # Get topic from query parameters
        topic = req.params.get('topic', 'community')

        # Try to use NewsAPI (free tier available)
        news_api_key = req.headers.get('X-NewsAPI-Key') or req.params.get('api_key')

        if news_api_key:
            # Call NewsAPI
            news_url = f"https://newsapi.org/v2/everything?q={topic}&sortBy=publishedAt&pageSize=10"
            headers = {'X-API-Key': news_api_key}

            response = requests.get(news_url, headers=headers, timeout=30)
            response.raise_for_status()

            news_data = response.json()
            articles = []

            for article in news_data.get('articles', []):
                articles.append({
                    'title': article.get('title', 'No title'),
                    'url': article.get('url', ''),
                    'source': article.get('source', {}).get('name', 'Unknown')
                })

            return func.HttpResponse(
                json.dumps(articles),
                status_code=200,
                mimetype="application/json"
            )

        else:
            # Return mock news data
            mock_articles = [
                {
                    "title": f"Community Initiative Launches in Local Area",
                    "url": "https://example.com/news/1",
                    "source": "Community Herald"
                },
                {
                    "title": f"Local {topic.title()} Group Hosts Annual Event",
                    "url": "https://example.com/news/2",
                    "source": "City Times"
                },
                {
                    "title": f"Neighborhood {topic.title()} Program Sees Success",
                    "url": "https://example.com/news/3",
                    "source": "Local News Network"
                },
                {
                    "title": f"New {topic.title()} Center Opens Downtown",
                    "url": "https://example.com/news/4",
                    "source": "Metro Daily"
                },
                {
                    "title": f"Volunteer Program Strengthens {topic.title()} Bonds",
                    "url": "https://example.com/news/5",
                    "source": "Regional Observer"
                }
            ]

            return func.HttpResponse(
                json.dumps(mock_articles),
                status_code=200,
                mimetype="application/json"
            )

    except requests.RequestException as e:
        logging.error(f"News API call failed: {str(e)}")
        # Fallback to mock data on API failure
        fallback_articles = [
            {
                "title": "Community News Service Temporarily Unavailable",
                "url": "https://example.com/status",
                "source": "System Notice"
            }
        ]
        return func.HttpResponse(
            json.dumps(fallback_articles),
            status_code=200,
            mimetype="application/json"
        )
    except Exception as e:
        logging.error(f"Function failed: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": "Internal server error"}),
            status_code=500,
            mimetype="application/json"
        )