"""
Azure AI Search vector store client for contextual content retrieval
"""
import os
import logging
from typing import List, Dict, Any, Optional
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from azure.identity import ManagedIdentityCredential
from azure.core.exceptions import AzureError

class VectorSearchClient:
    """Client for Azure AI Search vector operations"""

    def __init__(self, index_name: str = "community-content"):
        self.endpoint = os.environ.get('AZURE_AISEARCH_ENDPOINT')
        self.key = os.environ.get('AZURE_AISEARCH_KEY')
        self.index_name = index_name

        if not self.endpoint:
            raise ValueError("AZURE_AISEARCH_ENDPOINT environment variable is required")

        # Use managed identity if no key provided
        if self.key:
            credential = AzureKeyCredential(self.key)
        else:
            credential = ManagedIdentityCredential()

        try:
            self.client = SearchClient(
                endpoint=self.endpoint,
                index_name=self.index_name,
                credential=credential
            )
        except Exception as e:
            logging.error(f"Failed to initialize search client: {str(e)}")
            raise

    def search_community_content(self, location: str, query: str,
                               top: int = 5) -> List[Dict[str, Any]]:
        """Search for relevant community content based on location and query"""
        try:
            search_text = f"{location} {query}"

            results = self.client.search(
                search_text=search_text,
                top=top,
                select=["id", "title", "content", "source", "category",
                       "location", "date", "url"],
                filter=f"location eq '{location}' or location eq 'regional'",
                order_by=["date desc"]
            )

            return [dict(result) for result in results]

        except AzureError as e:
            logging.error(f"Search operation failed: {str(e)}")
            return []
        except Exception as e:
            logging.error(f"Unexpected error in search: {str(e)}")
            return []

    def store_content(self, content_item: Dict[str, Any]) -> bool:
        """Store or update content item in the search index"""
        try:
            # Ensure required fields are present
            required_fields = ['id', 'title', 'content', 'location']
            if not all(field in content_item for field in required_fields):
                logging.error("Missing required fields for content storage")
                return False

            # Upload or update the document
            result = self.client.upload_documents([content_item])

            if result[0].succeeded:
                logging.info(f"Successfully stored content: {content_item['id']}")
                return True
            else:
                logging.error(f"Failed to store content: {result[0].error_message}")
                return False

        except AzureError as e:
            logging.error(f"Content storage failed: {str(e)}")
            return False
        except Exception as e:
            logging.error(f"Unexpected error in storage: {str(e)}")
            return False

    def search_by_category(self, category: str, location: str,
                          top: int = 10) -> List[Dict[str, Any]]:
        """Search content by category and location"""
        try:
            results = self.client.search(
                search_text="*",
                top=top,
                select=["id", "title", "content", "source", "category",
                       "location", "date", "url"],
                filter=f"category eq '{category}' and (location eq '{location}' or location eq 'regional')",
                order_by=["date desc"]
            )

            return [dict(result) for result in results]

        except AzureError as e:
            logging.error(f"Category search failed: {str(e)}")
            return []

    def get_recent_content(self, location: str, hours: int = 24,
                          top: int = 20) -> List[Dict[str, Any]]:
        """Get recent content for a location within specified hours"""
        try:
            from datetime import datetime, timedelta
            cutoff_date = (datetime.utcnow() - timedelta(hours=hours)).isoformat()

            results = self.client.search(
                search_text="*",
                top=top,
                select=["id", "title", "content", "source", "category",
                       "location", "date", "url"],
                filter=f"(location eq '{location}' or location eq 'regional') and date ge {cutoff_date}",
                order_by=["date desc"]
            )

            return [dict(result) for result in results]

        except AzureError as e:
            logging.error(f"Recent content search failed: {str(e)}")
            return []