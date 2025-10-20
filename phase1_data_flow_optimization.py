"""
Data Flow Optimization Module
==============================

This module implements Pub/Sub messaging and Webhooks to ensure real-time
data synchronization between different system components.

Features:
- Event-driven architecture using Pub/Sub pattern
- Webhook support for external integrations
- Redis-based message queue for high performance
- Automatic retry mechanism for failed deliveries

Author: Manus AI
Date: 2025-10-20
"""

import json
import redis
import logging
from typing import Dict, Any, Callable, List
from datetime import datetime
from abc import ABC, abstractmethod
import requests
from enum import Enum

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EventType(Enum):
    """Enumeration of system events."""
    PROJECT_CREATED = "project.created"
    PROJECT_UPDATED = "project.updated"
    PROJECT_DELETED = "project.deleted"
    TASK_CREATED = "task.created"
    TASK_UPDATED = "task.updated"
    TASK_COMPLETED = "task.completed"
    USER_REGISTERED = "user.registered"
    USER_UPDATED = "user.updated"
    COMMENT_ADDED = "comment.added"
    FILE_UPLOADED = "file.uploaded"


class Event:
    """Represents a system event."""

    def __init__(self, event_type: EventType, data: Dict[str, Any], source: str = "system"):
        """
        Initialize an event.

        Args:
            event_type: Type of event
            data: Event payload data
            source: Source system that triggered the event
        """
        self.event_type = event_type
        self.data = data
        self.source = source
        self.timestamp = datetime.utcnow().isoformat()
        self.event_id = self._generate_event_id()

    def _generate_event_id(self) -> str:
        """Generate a unique event ID."""
        import uuid
        return str(uuid.uuid4())

    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary."""
        return {
            "event_id": self.event_id,
            "event_type": self.event_type.value,
            "data": self.data,
            "source": self.source,
            "timestamp": self.timestamp
        }

    def to_json(self) -> str:
        """Convert event to JSON string."""
        return json.dumps(self.to_dict())


class EventSubscriber(ABC):
    """Base class for event subscribers."""

    @abstractmethod
    def handle(self, event: Event) -> bool:
        """
        Handle an event.

        Args:
            event: Event to handle

        Returns:
            True if handled successfully, False otherwise
        """
        pass

    @abstractmethod
    def get_event_types(self) -> List[EventType]:
        """
        Get list of event types this subscriber handles.

        Returns:
            List of EventType enums
        """
        pass


class PubSubManager:
    """
    Manages publish/subscribe messaging for real-time data synchronization.
    Uses Redis as the message broker.
    """

    def __init__(self, redis_host: str = "localhost", redis_port: int = 6379, redis_db: int = 0):
        """
        Initialize the Pub/Sub manager.

        Args:
            redis_host: Redis server host
            redis_port: Redis server port
            redis_db: Redis database number
        """
        self.redis_client = redis.Redis(
            host=redis_host,
            port=redis_port,
            db=redis_db,
            decode_responses=True
        )
        self.subscribers: Dict[str, List[Callable]] = {}
        self.event_history: List[Event] = []

    def subscribe(self, event_type: EventType, callback: Callable) -> None:
        """
        Subscribe to an event type.

        Args:
            event_type: Type of event to subscribe to
            callback: Function to call when event is published
        """
        channel = event_type.value
        if channel not in self.subscribers:
            self.subscribers[channel] = []
        self.subscribers[channel].append(callback)
        logger.info(f"Subscribed to event: {channel}")

    def unsubscribe(self, event_type: EventType, callback: Callable) -> None:
        """
        Unsubscribe from an event type.

        Args:
            event_type: Type of event to unsubscribe from
            callback: Function to remove
        """
        channel = event_type.value
        if channel in self.subscribers and callback in self.subscribers[channel]:
            self.subscribers[channel].remove(callback)
            logger.info(f"Unsubscribed from event: {channel}")

    def publish(self, event: Event) -> bool:
        """
        Publish an event to all subscribers.

        Args:
            event: Event to publish

        Returns:
            True if published successfully
        """
        try:
            channel = event.event_type.value
            message = event.to_json()

            # Store in Redis for persistence
            self.redis_client.publish(channel, message)

            # Store in event history
            self.event_history.append(event)

            # Call local subscribers
            if channel in self.subscribers:
                for callback in self.subscribers[channel]:
                    try:
                        callback(event)
                    except Exception as e:
                        logger.error(f"Error calling subscriber: {e}")

            logger.info(f"Published event: {event.event_id} of type {channel}")
            return True

        except Exception as e:
            logger.error(f"Error publishing event: {e}")
            return False

    def get_event_history(self, event_type: EventType = None, limit: int = 100) -> List[Event]:
        """
        Get event history.

        Args:
            event_type: Filter by event type (optional)
            limit: Maximum number of events to return

        Returns:
            List of events
        """
        if event_type:
            return [e for e in self.event_history[-limit:] if e.event_type == event_type]
        return self.event_history[-limit:]


class WebhookManager:
    """
    Manages webhooks for external system integrations.
    Allows external systems to receive real-time event notifications.
    """

    def __init__(self, max_retries: int = 3, timeout: int = 10):
        """
        Initialize the Webhook manager.

        Args:
            max_retries: Maximum number of retry attempts
            timeout: Request timeout in seconds
        """
        self.webhooks: Dict[str, List[str]] = {}
        self.max_retries = max_retries
        self.timeout = timeout

    def register_webhook(self, event_type: EventType, webhook_url: str) -> bool:
        """
        Register a webhook for an event type.

        Args:
            event_type: Type of event to listen for
            webhook_url: URL to send webhook requests to

        Returns:
            True if registered successfully
        """
        try:
            channel = event_type.value
            if channel not in self.webhooks:
                self.webhooks[channel] = []

            if webhook_url not in self.webhooks[channel]:
                self.webhooks[channel].append(webhook_url)
                logger.info(f"Registered webhook for {channel}: {webhook_url}")
                return True

            return False

        except Exception as e:
            logger.error(f"Error registering webhook: {e}")
            return False

    def unregister_webhook(self, event_type: EventType, webhook_url: str) -> bool:
        """
        Unregister a webhook.

        Args:
            event_type: Type of event
            webhook_url: URL to remove

        Returns:
            True if unregistered successfully
        """
        try:
            channel = event_type.value
            if channel in self.webhooks and webhook_url in self.webhooks[channel]:
                self.webhooks[channel].remove(webhook_url)
                logger.info(f"Unregistered webhook for {channel}: {webhook_url}")
                return True

            return False

        except Exception as e:
            logger.error(f"Error unregistering webhook: {e}")
            return False

    def trigger_webhooks(self, event: Event) -> Dict[str, bool]:
        """
        Trigger all webhooks for an event.

        Args:
            event: Event that triggered webhooks

        Returns:
            Dictionary mapping webhook URLs to success status
        """
        channel = event.event_type.value
        results = {}

        if channel not in self.webhooks:
            return results

        for webhook_url in self.webhooks[channel]:
            results[webhook_url] = self._send_webhook(webhook_url, event)

        return results

    def _send_webhook(self, webhook_url: str, event: Event) -> bool:
        """
        Send a webhook request with retry logic.

        Args:
            webhook_url: URL to send webhook to
            event: Event to send

        Returns:
            True if successful
        """
        payload = event.to_dict()

        for attempt in range(self.max_retries):
            try:
                response = requests.post(
                    webhook_url,
                    json=payload,
                    timeout=self.timeout,
                    headers={"Content-Type": "application/json"}
                )

                if response.status_code == 200:
                    logger.info(f"Webhook sent successfully to {webhook_url}")
                    return True

            except requests.exceptions.RequestException as e:
                logger.warning(f"Webhook attempt {attempt + 1} failed for {webhook_url}: {e}")

        logger.error(f"Webhook failed after {self.max_retries} attempts: {webhook_url}")
        return False


class DataFlowOrchestrator:
    """
    Orchestrates data flow between system components using Pub/Sub and Webhooks.
    """

    def __init__(self):
        """Initialize the data flow orchestrator."""
        self.pubsub = PubSubManager()
        self.webhooks = WebhookManager()

    def on_project_created(self, project_data: Dict[str, Any]) -> None:
        """Handle project creation event."""
        event = Event(EventType.PROJECT_CREATED, project_data, "project_service")
        self.pubsub.publish(event)
        self.webhooks.trigger_webhooks(event)

    def on_project_updated(self, project_id: str, updates: Dict[str, Any]) -> None:
        """Handle project update event."""
        event = Event(
            EventType.PROJECT_UPDATED,
            {"project_id": project_id, "updates": updates},
            "project_service"
        )
        self.pubsub.publish(event)
        self.webhooks.trigger_webhooks(event)

    def on_task_created(self, task_data: Dict[str, Any]) -> None:
        """Handle task creation event."""
        event = Event(EventType.TASK_CREATED, task_data, "task_service")
        self.pubsub.publish(event)
        self.webhooks.trigger_webhooks(event)

    def on_task_updated(self, task_id: str, updates: Dict[str, Any]) -> None:
        """Handle task update event."""
        event = Event(
            EventType.TASK_UPDATED,
            {"task_id": task_id, "updates": updates},
            "task_service"
        )
        self.pubsub.publish(event)
        self.webhooks.trigger_webhooks(event)

    def on_task_completed(self, task_id: str) -> None:
        """Handle task completion event."""
        event = Event(
            EventType.TASK_COMPLETED,
            {"task_id": task_id},
            "task_service"
        )
        self.pubsub.publish(event)
        self.webhooks.trigger_webhooks(event)


# Global orchestrator instance
data_flow = DataFlowOrchestrator()


if __name__ == "__main__":
    # Example usage
    print("Data Flow Optimization Module")
    print("=" * 50)

    # Create and publish an event
    project_data = {
        "project_id": "proj_123",
        "name": "New Project",
        "description": "A test project"
    }

    data_flow.on_project_created(project_data)

    # Register a webhook
    data_flow.webhooks.register_webhook(
        EventType.PROJECT_CREATED,
        "https://example.com/webhooks/project-created"
    )

    # Subscribe to events
    def handle_project_created(event: Event):
        print(f"Project created: {event.data}")

    data_flow.pubsub.subscribe(EventType.PROJECT_CREATED, handle_project_created)

    # Publish another event
    data_flow.on_project_created(project_data)

    print("\nEvent history:")
    for event in data_flow.pubsub.get_event_history():
        print(f"- {event.event_type.value}: {event.event_id}")

