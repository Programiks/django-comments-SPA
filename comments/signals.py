"""
Django signals for comment events.

This module handles post-save events for the Comment model, including:
- Logging comment creation events
- Enqueuing tasks for asynchronous processing
- Broadcasting WebSocket events to connected clients
"""

import logging

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Comment
from .queue import enqueue_comment_created

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Comment)
def comment_created_event(sender, instance, created, **kwargs):
    """
    Handle Comment creation events.

    This signal is triggered after a Comment instance is saved. If the comment
    is newly created (not updated), it performs the following actions:
    1. Logs the event for monitoring and analytics
    2. Enqueues a task for asynchronous processing (e.g., email notifications)
    3. Broadcasts a WebSocket event to all connected clients for real-time
        updates

    Args:
        sender: The model class (Comment)
        instance: The Comment instance that was saved
        created: Boolean indicating if this is a new instance
        **kwargs: Additional signal arguments

    Returns:
        None: Side effects include logging, queueing, and WebSocket broadcast.
    """
    if created:
        # Log the comment creation event
        logger.info(
            "Event: comment_created",
            extra={
                "comment_id": instance.id,
                "author_name": instance.author_name,
                "author_email": instance.email,
            },
        )

        # Enqueue task for asynchronous processing (e.g., background worker)
        enqueue_comment_created(
            comment_id=instance.id,
            author_name=instance.author_name,
            author_email=instance.email,
        )

        # Broadcast WebSocket event to all connected clients
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "comments",
            {
                "type": "comment.created",
                "comment_id": instance.id,
                "author_name": instance.author_name,
                "text": instance.text,
            },
        )
