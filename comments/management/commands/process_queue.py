"""
Django management command to publish pending comments.

This command processes the comment publishing queue by updating all
comments with STATUS_PENDING to STATUS_PUBLISHED. In production, this
should be run periodically via cron or a task scheduler.

Example usage:
    python manage.py process_queue
"""

from django.core.management.base import BaseCommand

from comments.models import Comment


class Command(BaseCommand):
    """
    Management command to publish pending comments from the queue.

    This command queries all comments with pending status and updates
    them to published status. It outputs a log of processed comments
    to stdout.

    Attributes:
        help: Short description of the command (shown in manage.py help).

    Notes:
        - This is an alternative to the middleware-based approach
        - Suitable for cron jobs or manual execution
        - For production, consider using Celery or similar task queue
    """

    help = "Publish pending comments from the queue"

    def handle(self, *args, **options):
        """
        Execute the command to publish pending comments.

        This method:
        1. Queries all comments with STATUS_PENDING status
        2. Updates each comment to STATUS_PUBLISHED
        3. Outputs progress messages to stdout

        Args:
            *args: Positional arguments (unused).
            **options: Keyword arguments from command parser (unused).

        Notes:
            - Uses update_fields for efficient database updates
            - Orders by created_at to process oldest first (FIFO)
        """
        # Query all pending comments ordered by creation date (FIFO)
        pending = Comment.objects.filter(
            status=Comment.STATUS_PENDING
        ).order_by("created_at")

        for comment in pending:
            comment.status = Comment.STATUS_PUBLISHED
            comment.save(update_fields=["status"])
            self.stdout.write(f"Published comment {comment.id}")

        if not pending.exists():
            self.stdout.write("No pending comments.")
