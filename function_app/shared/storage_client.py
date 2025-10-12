"""
Azure storage client for content persistence and change detection
"""
import os
import logging
import json
import hashlib
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from azure.cosmos import CosmosClient, PartitionKey
from azure.identity import ManagedIdentityCredential
from azure.core.exceptions import AzureError

class ContentStorageClient:
    """Client for content storage and change detection using Cosmos DB"""

    def __init__(self):
        self.endpoint = os.environ.get('AZURE_COSMOS_ENDPOINT')
        self.key = os.environ.get('AZURE_COSMOS_KEY')
        self.database_name = os.environ.get('AZURE_COSMOS_DATABASE', 'CommunityHub')

        if not self.endpoint:
            raise ValueError("AZURE_COSMOS_ENDPOINT environment variable is required")

        # Use managed identity if no key provided
        if self.key:
            self.client = CosmosClient(self.endpoint, self.key)
        else:
            credential = ManagedIdentityCredential()
            self.client = CosmosClient(self.endpoint, credential)

        try:
            # Create database and containers if they don't exist
            self.database = self.client.create_database_if_not_exists(self.database_name)
            self._initialize_containers()
        except Exception as e:
            logging.error(f"Failed to initialize Cosmos client: {str(e)}")
            raise

    def _initialize_containers(self):
        """Initialize required containers"""
        # Content snapshots for change detection
        self.content_container = self.database.create_container_if_not_exists(
            id="content_snapshots",
            partition_key=PartitionKey(path="/source_url"),
            offer_throughput=400
        )

        # Crawling targets and their frequencies
        self.targets_container = self.database.create_container_if_not_exists(
            id="crawling_targets",
            partition_key=PartitionKey(path="/location"),
            offer_throughput=400
        )

        # Editorial queue
        self.queue_container = self.database.create_container_if_not_exists(
            id="editorial_queue",
            partition_key=PartitionKey(path="/location"),
            offer_throughput=400
        )

        # User profiles
        self.users_container = self.database.create_container_if_not_exists(
            id="user_profiles",
            partition_key=PartitionKey(path="/user_id"),
            offer_throughput=400
        )

    def store_content_snapshot(self, url: str, content: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Store content snapshot and detect changes"""
        content_hash = hashlib.sha256(content.encode()).hexdigest()
        timestamp = datetime.utcnow().isoformat()

        # Check for existing content
        existing = self.get_latest_snapshot(url)
        has_changed = not existing or existing.get('content_hash') != content_hash

        snapshot = {
            'id': f"{url}_{timestamp}",
            'source_url': url,
            'content': content,
            'content_hash': content_hash,
            'timestamp': timestamp,
            'metadata': metadata,
            'has_changed': has_changed,
            'ttl': int((datetime.utcnow() + timedelta(days=90)).timestamp())  # Auto-delete after 90 days
        }

        try:
            self.content_container.create_item(snapshot)
            logging.info(f"Stored content snapshot for {url}, changed: {has_changed}")
            return snapshot
        except AzureError as e:
            logging.error(f"Failed to store content snapshot: {str(e)}")
            raise

    def get_latest_snapshot(self, url: str) -> Optional[Dict[str, Any]]:
        """Get the latest content snapshot for a URL"""
        try:
            query = "SELECT * FROM c WHERE c.source_url = @url ORDER BY c.timestamp DESC OFFSET 0 LIMIT 1"
            parameters = [{"name": "@url", "value": url}]

            items = list(self.content_container.query_items(
                query=query,
                parameters=parameters,
                partition_key=url
            ))

            return items[0] if items else None
        except AzureError as e:
            logging.error(f"Failed to get latest snapshot: {str(e)}")
            return None

    def store_crawling_target(self, target: Dict[str, Any]) -> bool:
        """Store or update a crawling target"""
        try:
            target['id'] = target['url']
            target['last_updated'] = datetime.utcnow().isoformat()

            self.targets_container.upsert_item(target)
            logging.info(f"Stored crawling target: {target['url']}")
            return True
        except AzureError as e:
            logging.error(f"Failed to store crawling target: {str(e)}")
            return False

    def get_crawling_targets(self, location: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get crawling targets, optionally filtered by location"""
        try:
            if location:
                query = "SELECT * FROM c WHERE c.location = @location"
                parameters = [{"name": "@location", "value": location}]
            else:
                query = "SELECT * FROM c"
                parameters = []

            return list(self.targets_container.query_items(
                query=query,
                parameters=parameters
            ))
        except AzureError as e:
            logging.error(f"Failed to get crawling targets: {str(e)}")
            return []

    def update_crawling_frequency(self, url: str, frequency: str, location: str) -> bool:
        """Update crawling frequency for a target"""
        try:
            # Get existing target
            target = self.targets_container.read_item(item=url, partition_key=location)
            target['frequency'] = frequency
            target['frequency_updated'] = datetime.utcnow().isoformat()

            self.targets_container.replace_item(item=target['id'], body=target)
            logging.info(f"Updated frequency for {url} to {frequency}")
            return True
        except AzureError as e:
            logging.error(f"Failed to update crawling frequency: {str(e)}")
            return False

    def add_to_editorial_queue(self, content: Dict[str, Any]) -> bool:
        """Add content to editorial queue"""
        try:
            queue_item = {
                'id': f"{content['source_url']}_{datetime.utcnow().isoformat()}",
                'location': content['location'],
                'content': content,
                'status': 'pending',
                'created_at': datetime.utcnow().isoformat(),
                'priority': content.get('priority', 'normal')
            }

            self.queue_container.create_item(queue_item)
            logging.info(f"Added item to editorial queue: {queue_item['id']}")
            return True
        except AzureError as e:
            logging.error(f"Failed to add to editorial queue: {str(e)}")
            return False

    def get_editorial_queue(self, location: str, status: str = 'pending') -> List[Dict[str, Any]]:
        """Get editorial queue items for a location"""
        try:
            query = "SELECT * FROM c WHERE c.location = @location AND c.status = @status ORDER BY c.created_at DESC"
            parameters = [
                {"name": "@location", "value": location},
                {"name": "@status", "value": status}
            ]

            return list(self.queue_container.query_items(
                query=query,
                parameters=parameters,
                partition_key=location
            ))
        except AzureError as e:
            logging.error(f"Failed to get editorial queue: {str(e)}")
            return []

    def update_queue_item_status(self, item_id: str, location: str, status: str,
                                editor_notes: Optional[str] = None) -> bool:
        """Update editorial queue item status"""
        try:
            item = self.queue_container.read_item(item=item_id, partition_key=location)
            item['status'] = status
            item['updated_at'] = datetime.utcnow().isoformat()

            if editor_notes:
                item['editor_notes'] = editor_notes

            self.queue_container.replace_item(item=item_id, body=item)
            logging.info(f"Updated queue item {item_id} status to {status}")
            return True
        except AzureError as e:
            logging.error(f"Failed to update queue item status: {str(e)}")
            return False