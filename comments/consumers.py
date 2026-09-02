from channels.generic.websocket import AsyncWebsocketConsumer


class CommentConsumer(AsyncWebsocketConsumer):
    group_name = "comments"

    async def connect(self):
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name,
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name,
        )

    async def comment_created(self, event):
        await self.send(text_data="new_comment")