"""
Django middleware for automatic comment publishing.

This module provides middleware that processes the comment publishing queue
after each HTTP request. In production, this should be replaced with a
background task queue (e.g., Celery, Redis Queue).
"""

import logging

from .models import Comment

logger = logging.getLogger(__name__)


class AutoPublishQueueMiddleware:
    """
    Middleware that automatically publishes pending comments after
    each request.

    This middleware processes all comments with STATUS_PENDING status and
    updates them to STATUS_PUBLISHED after the response is sent to the client.

    Attributes:
        get_response: Django's get_response callable for middleware chain.

    Notes:
        - This is a development/demo implementation
        - For production, use a background worker (Celery, RQ, etc.)
        - Processing happens after response generation to avoid blocking
    """

    def __init__(self, get_response):
        """
        Initialize middleware with Django's get_response callable.

        Args:
            get_response: Callable that returns HttpResponse for
            the next middleware/view.
        """
        self.get_response = get_response

    def __call__(self, request):
        """
        Process request and publish pending comments after response.

        This method:
        1. Calls the next middleware/view to get response
        2. Queries all pending comments from the database
        3. Updates each comment status to PUBLISHED
        4. Logs the publishing actions

        Args:
            request: Django HTTP request object.

        Returns:
            HttpResponse: Response from the next middleware/view.

        Notes:
            - Uses update_fields for efficient database updates
            - Logs each published comment and total count
        """
        response = self.get_response(request)

        # Process queue after the response is generated (non-blocking)
        pending = Comment.objects.filter(
            status=Comment.STATUS_PENDING
        ).order_by("created_at")

        for comment in pending:
            comment.status = Comment.STATUS_PUBLISHED
            comment.save(update_fields=["status"])
            logger.info("Queue: published comment %s", comment.id)

        if pending.exists():
            logger.info("Queue: processed %d comment(s)", pending.count())

        return response
