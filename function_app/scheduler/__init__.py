import azure.functions as func
import logging
import json
import requests
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List
import sys
import os

# Add the function_app directory to the path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.storage_client import ContentStorageClient

def main(mytimer: func.TimerRequest) -> None:
    """
    Adaptive Crawling Scheduler Function
    Timer-triggered function (every 15 minutes) that manages crawling frequencies

    Implements adaptive frequency logic:
    - Weekly baseline (n)
    - Daily if changes detected (m)
    - Hourly if frequent changes (7am-12am)
    - Revert after 30 days of no changes
    """

    utc_timestamp = datetime.now(timezone.utc).replace(tzinfo=timezone.utc).isoformat()
    logging.info(f'Scheduler function ran at {utc_timestamp}')

    try:
        storage_client = ContentStorageClient()

        # Get all crawling targets
        targets = storage_client.get_crawling_targets()

        if not targets:
            logging.info("No crawling targets found")
            return

        schedule_updates = []
        crawl_triggers = []

        for target in targets:
            try:
                # Calculate new frequency based on adaptive logic
                new_frequency = calculate_adaptive_frequency(target)

                current_frequency = target.get('frequency', 'weekly')

                # Update frequency if changed
                if new_frequency != current_frequency:
                    success = storage_client.update_crawling_frequency(
                        target['url'],
                        new_frequency,
                        target['location']
                    )

                    if success:
                        schedule_updates.append({
                            'url': target['url'],
                            'old_frequency': current_frequency,
                            'new_frequency': new_frequency,
                            'reason': get_frequency_change_reason(target, new_frequency)
                        })

                        # Mark target as updated
                        target['frequency'] = new_frequency

                # Check if target should be crawled now
                if should_crawl_now(target):
                    crawl_triggers.append(target)

            except Exception as e:
                logging.error(f"Error processing target {target.get('url', 'unknown')}: {str(e)}")
                continue

        # Trigger crawling for targets that are due
        if crawl_triggers:
            trigger_crawling(crawl_triggers)

        # Log summary
        logging.info(f"Scheduler completed: {len(schedule_updates)} frequency updates, "
                    f"{len(crawl_triggers)} crawl triggers")

        if schedule_updates:
            logging.info(f"Frequency updates: {json.dumps(schedule_updates)}")

    except Exception as e:
        logging.error(f"Scheduler function failed: {str(e)}")

def calculate_adaptive_frequency(target: Dict[str, Any]) -> str:
    """Calculate adaptive frequency based on change detection history"""
    try:
        # Get change history from target metadata
        last_change_date = target.get('last_change_date')
        recent_changes = target.get('recent_changes', 0)
        consecutive_no_changes = target.get('consecutive_no_changes', 0)
        current_frequency = target.get('frequency', 'weekly')

        if not last_change_date:
            return 'weekly'  # Default baseline

        # Parse last change date
        last_change = datetime.fromisoformat(last_change_date.replace('Z', '+00:00'))
        days_since_change = (datetime.now(timezone.utc) - last_change).days

        # Adaptive logic implementation
        if recent_changes >= 2 and days_since_change <= 2:
            # Frequent recent changes -> hourly during active hours
            return 'hourly'
        elif days_since_change <= 7 and recent_changes >= 1:
            # Recent changes -> daily
            return 'daily'
        elif consecutive_no_changes >= 30:
            # No changes for 30+ days -> revert to less frequent
            if current_frequency == 'hourly':
                return 'daily'
            elif current_frequency == 'daily':
                return 'weekly'
            else:
                return 'weekly'
        else:
            # Maintain current frequency
            return current_frequency

    except Exception as e:
        logging.error(f"Error calculating frequency for {target.get('url')}: {str(e)}")
        return 'weekly'  # Safe default

def should_crawl_now(target: Dict[str, Any]) -> bool:
    """Determine if a target should be crawled now based on its frequency"""
    try:
        frequency = target.get('frequency', 'weekly')
        last_crawl_str = target.get('last_crawl_time')

        if not last_crawl_str:
            return True  # Never crawled before

        last_crawl = datetime.fromisoformat(last_crawl_str.replace('Z', '+00:00'))
        now = datetime.now(timezone.utc)
        time_since_crawl = now - last_crawl

        # Check based on frequency
        if frequency == 'hourly':
            # Only crawl during active hours (7am-12am local time)
            # For simplicity, using UTC. In production, convert to local timezone
            current_hour = now.hour
            if 7 <= current_hour <= 23:  # 7am to 11pm UTC
                return time_since_crawl >= timedelta(hours=1)
            else:
                return False

        elif frequency == 'daily':
            return time_since_crawl >= timedelta(days=1)

        elif frequency == 'weekly':
            return time_since_crawl >= timedelta(weeks=1)

        else:
            return False

    except Exception as e:
        logging.error(f"Error checking crawl timing for {target.get('url')}: {str(e)}")
        return False

def get_frequency_change_reason(target: Dict[str, Any], new_frequency: str) -> str:
    """Get human-readable reason for frequency change"""
    recent_changes = target.get('recent_changes', 0)
    consecutive_no_changes = target.get('consecutive_no_changes', 0)

    if new_frequency == 'hourly':
        return f"Increased to hourly due to {recent_changes} recent changes"
    elif new_frequency == 'daily':
        return "Increased to daily due to recent activity"
    elif consecutive_no_changes >= 30:
        return f"Reduced frequency after {consecutive_no_changes} days without changes"
    else:
        return "Frequency maintained based on activity pattern"

def trigger_crawling(targets: List[Dict[str, Any]]) -> None:
    """Trigger crawling for the specified targets"""
    try:
        # Get the crawl_content function URL
        function_app_url = os.environ.get('CRAWL_FUNCTION_URL', 'http://localhost:7071/api/crawl_content')

        # Prepare sources for crawling
        sources = []
        for target in targets:
            sources.append({
                'url': target['url'],
                'location': target['location'],
                'category': target.get('category', 'general')
            })

        if not sources:
            return

        # Call the crawl_content function
        payload = {
            'sources': sources,
            'force_crawl': False
        }

        headers = {'Content-Type': 'application/json'}

        response = requests.post(
            function_app_url,
            json=payload,
            headers=headers,
            timeout=300  # 5 minute timeout for crawling
        )

        if response.status_code == 200:
            result = response.json()
            logging.info(f"Successfully triggered crawling for {len(sources)} sources. "
                        f"Processed: {result.get('processed_items', 0)} items")

            # Update last crawl times
            storage_client = ContentStorageClient()
            for target in targets:
                target['last_crawl_time'] = datetime.now(timezone.utc).isoformat()
                storage_client.store_crawling_target(target)

        else:
            logging.error(f"Failed to trigger crawling: {response.status_code} - {response.text}")

    except requests.RequestException as e:
        logging.error(f"Failed to trigger crawling via HTTP: {str(e)}")
    except Exception as e:
        logging.error(f"Unexpected error triggering crawling: {str(e)}")

def initialize_default_targets() -> None:
    """Initialize some default crawling targets for testing"""
    try:
        storage_client = ContentStorageClient()

        default_targets = [
            {
                'url': 'https://vancouver.ca/news-calendar.aspx',
                'location': 'Vancouver',
                'category': 'government',
                'frequency': 'weekly',
                'created_at': datetime.now(timezone.utc).isoformat()
            },
            {
                'url': 'https://www.cbc.ca/news/canada/british-columbia',
                'location': 'Vancouver',
                'category': 'news',
                'frequency': 'weekly',
                'created_at': datetime.now(timezone.utc).isoformat()
            }
        ]

        for target in default_targets:
            storage_client.store_crawling_target(target)

        logging.info(f"Initialized {len(default_targets)} default crawling targets")

    except Exception as e:
        logging.error(f"Failed to initialize default targets: {str(e)}")