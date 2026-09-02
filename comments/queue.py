"""
In-memory task queue for comment events.

This module provides a simple FIFO queue for processing comment-related tasks.
Currently used for demonstration; can be replaced with Celery or Redis
in production.
"""

import logging
from collections import deque
from dataclasses import dataclass
from typing import Deque

logger = logging.getLogger(__name__)


@dataclass
class Task:
    """
    Represents a queued task.

    Attributes:
        task_type: Type of task (e.g., 'comment_created').
        payload: Dictionary containing task-specific data.
    """
    task_type: str
    payload: dict


# In-memory queue for demonstration purposes
# In production, replace with Celery, Redis, or RabbitMQ
task_queue: Deque[Task] = deque()


def enqueue_comment_created(comment_id: int,
                            author_name: str,
                            author_email: str):
    """
    Enqueue a 'comment_created' task for asynchronous processing.

    Args:
        comment_id: The ID of the newly created comment.
        author_name: The name of the comment author.
        author_email: The email of the comment author.
    """
    task = Task(
        task_type="comment_created",
        payload={
            "comment_id": comment_id,
            "author_name": author_name,
            "author_email": author_email,
        },
    )
    task_queue.append(task)
    logger.info("Task enqueued: comment_created (id=%s)", comment_id)


def process_queue():
    """
    Process all pending tasks in the queue (worker simulation).

    Iterates through the queue, processes each task, and logs the results.
    In production, this would be handled by a background worker (e.g., Celery).

    Returns:
        None: Logs the number of processed tasks.
    """
    processed = 0
    while task_queue:
        task = task_queue.popleft()
        if task.task_type == "comment_created":
            payload = task.payload
            logger.info(
                "Worker processed: comment_created",
                extra={
                    "comment_id": payload["comment_id"],
                    "author_name": payload["author_name"],
                    "author_email": payload["author_email"],
                },
            )
            processed += 1
    if processed:
        logger.info("Queue processed %d task(s)", processed)
