# comments/queue.py
import logging
from collections import deque
from dataclasses import dataclass
from typing import Deque

logger = logging.getLogger(__name__)

@dataclass
class Task:
    task_type: str
    payload: dict

# In-memory queue (for demonstration)
task_queue: Deque[Task] = deque()

def enqueue_comment_created(comment_id: int, author_name: str, author_email: str):
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
    """Process all tasks in the queue (worker simulation)."""
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