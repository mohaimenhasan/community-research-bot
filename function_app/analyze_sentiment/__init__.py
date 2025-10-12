import azure.functions as func
import json
import os
import requests
import logging
import re

def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    Analyze Sentiment Function - Analyzes sentiment of text
    POST /api/analyze_sentiment
    Accepts: {"text": "some text"}
    Returns: {"sentiment": "positive|neutral|negative", "score": float}
    """

    logging.info('Analyze sentiment function processed a request.')

    try:
        # Parse request body
        req_body = req.get_json()
        if not req_body or 'text' not in req_body:
            return func.HttpResponse(
                json.dumps({"error": "Missing 'text' in request body"}),
                status_code=400,
                mimetype="application/json"
            )

        text = req_body['text']

        # Get Azure OpenAI configuration
        azure_openai_key = os.environ.get('AZURE_OPENAI_KEY')
        resource_name = os.environ.get('RESOURCE_NAME')

        if not azure_openai_key or not resource_name:
            # Return mock sentiment based on keywords
            return _get_mock_sentiment(text)

        # Call Azure AI Foundry for sentiment analysis
        foundry_url = f"https://{resource_name}.services.ai.azure.com/models/chat/completions?api-version=2024-05-01-preview"
        headers = {
            "Content-Type": "application/json",
            "api-key": azure_openai_key
        }

        payload = {
            "messages": [
                {
                    "role": "system",
                    "content": "You are a sentiment analysis assistant. Analyze the sentiment and return only 'positive', 'neutral', or 'negative' followed by a confidence score from 0.0 to 1.0. Format: sentiment,score"
                },
                {
                    "role": "user",
                    "content": f"Analyze the sentiment of this text: {text}"
                }
            ],
            "max_tokens": 50,
            "temperature": 0.1
        }

        # Log the API call
        logging.info(f"Calling Foundry endpoint {foundry_url} for function analyze_sentiment")

        response = requests.post(foundry_url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()

        result = response.json()
        analysis = result['choices'][0]['message']['content'].strip()

        # Parse response (expecting format like "positive,0.85")
        try:
            sentiment, score_str = analysis.split(',')
            score = float(score_str)
            sentiment = sentiment.strip().lower()
        except (ValueError, IndexError):
            # Fallback to mock if parsing fails
            return _get_mock_sentiment(text)

        return func.HttpResponse(
            json.dumps({"sentiment": sentiment, "score": score}),
            status_code=200,
            mimetype="application/json"
        )

    except requests.RequestException as e:
        logging.error(f"Foundry API call failed: {str(e)}")
        # Fallback to mock sentiment
        return _get_mock_sentiment(text)
    except Exception as e:
        logging.error(f"Function failed: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": "Internal server error"}),
            status_code=500,
            mimetype="application/json"
        )

def _get_mock_sentiment(text):
    """
    Generate mock sentiment based on keyword analysis
    """
    positive_words = ['good', 'great', 'excellent', 'amazing', 'wonderful', 'love', 'happy', 'fantastic']
    negative_words = ['bad', 'terrible', 'awful', 'hate', 'horrible', 'sad', 'angry', 'disappointing']

    text_lower = text.lower()
    positive_count = sum(1 for word in positive_words if word in text_lower)
    negative_count = sum(1 for word in negative_words if word in text_lower)

    if positive_count > negative_count:
        sentiment = "positive"
        score = min(0.7 + (positive_count * 0.1), 1.0)
    elif negative_count > positive_count:
        sentiment = "negative"
        score = min(0.7 + (negative_count * 0.1), 1.0)
    else:
        sentiment = "neutral"
        score = 0.5

    return func.HttpResponse(
        json.dumps({"sentiment": sentiment, "score": score}),
        status_code=200,
        mimetype="application/json"
    )