# comments/signals.py
import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from .queue import enqueue_comment_created
from .models import Comment

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Comment)
def comment_created_event(sender, instance, created, **kwargs):
    if created:
        # Existing event logging
        logger.info(
            "Event: comment_created",
            extra={
                "comment_id": instance.id,
                "author_name": instance.author_name,
                "author_email": instance.email,
            },
        )

        # Enqueue task for async processing
        enqueue_comment_created(
            comment_id=instance.id,
            author_name=instance.author_name,
            author_email=instance.email,
        )

        # Send WebSocket event
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
