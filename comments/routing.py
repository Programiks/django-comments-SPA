"""
WebSocket routing configuration for the comment system.

This module defines URL patterns for WebSocket connections.
Maps '/ws/comments/' to the CommentConsumer for real-time comment updates.
"""

from django.urls import path

from .consumers import CommentConsumer

# WebSocket URL patterns
# Clients connect to 'ws/comments/' to receive real-time comment events
websocket_urlpatterns = [
    path("ws/comments/", CommentConsumer.as_asgi()),
]
