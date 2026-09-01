# comments/management/commands/process_queue.py
from django.core.management.base import BaseCommand
from comments.models import Comment

class Command(BaseCommand):
    help = "Publish pending comments from the queue"

    def handle(self, *args, **options):
        pending = Comment.objects.filter(status=Comment.STATUS_PENDING).order_by("created_at")

        for comment in pending:
            comment.status = Comment.STATUS_PUBLISHED
            comment.save(update_fields=["status"])
            self.stdout.write(f"Published comment {comment.id}")

        if not pending.exists():
            self.stdout.write("No pending comments.")