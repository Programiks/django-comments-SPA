# comments/middleware.py
import logging
from .models import Comment

logger = logging.getLogger(__name__)

class AutoPublishQueueMiddleware:
    """
    Automatically publish pending comments after each request.
    In a real project, this would be replaced by a background worker.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Process queue after the response is generated
        pending = Comment.objects.filter(status=Comment.STATUS_PENDING).order_by("created_at")
        for comment in pending:
            comment.status = Comment.STATUS_PUBLISHED
            comment.save(update_fields=["status"])
            logger.info("Queue: published comment %s", comment.id)

        if pending.exists():
            logger.info("Queue: processed %d comment(s)", pending.count())

        return response