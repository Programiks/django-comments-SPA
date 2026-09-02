"""
Django Channels WebSocket consumers for real-time comment updates.

This module provides WebSocket consumers that handle:
- Client connections to the comment group
- Real-time notifications when new comments are created
- Client disconnections and cleanup
"""

from channels.generic.websocket import AsyncWebsocketConsumer


class CommentConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time comment notifications.

    This consumer manages WebSocket connections for the comment system,
    allowing clients to receive real-time notifications when new comments
    are created.

    Attributes:
        group_name: Name of the channel group for broadcasting
        (default: "comments").

    Notes:
        - Uses Django Channels for async WebSocket handling
        - Clients join a group to receive broadcast notifications
        - Notifications are sent as plain text messages
    """

    group_name = "comments"

    async def connect(self):
        """
        Handle WebSocket connection.

        This method is called when a client connects to the WebSocket endpoint.
        It adds the client's channel to the comments group for broadcasting
        and accepts the connection.

        Notes:
            - Client is added to the group before accepting connection
            - All clients in the group receive broadcast messages
        """
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name,
        )
        await self.accept()

    async def disconnect(self, close_code):
        """
        Handle WebSocket disconnection.

        This method is called when a client disconnects from the WebSocket
        endpoint. It removes the client's channel from the comments group
        to prevent sending messages to disconnected clients.

        Args:
            close_code: WebSocket close code indicating reason for disconnect.

        Notes:
            - Cleanup is automatic via group_discard
            - Prevents memory leaks from stale channel references
        """
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name,
        )

    async def comment_created(self, event):
        """
        Handle comment.created events from the channel layer.

        This method is called when a new comment is created and a
        comment.created event is broadcast to the comments group.
        It sends a notification message to the connected client.

        Args:
            event: Dictionary containing event data (e.g., 'message' key).

        Notes:
            - Event type matches the 'type' field in group_send calls
            - Message format should match client-side expectations
        """
        await self.send(text_data="new_comment")
