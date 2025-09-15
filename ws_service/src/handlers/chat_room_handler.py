import json

import websockets
from database import redis_context_manager
from websockets.legacy.server import WebSocketServerProtocol

rooms_local: dict[str, set[WebSocketServerProtocol]] = {}


class ChatRoomHandler:
    pub_sub_type = "chats_rooms"

    def __init__(self, ws: WebSocketServerProtocol, path: str) -> None:
        self._ws = ws
        self._path = path
        self._room_id = self._path.split("/")[-1]

    async def handle(self) -> None:
        await self.register_ws_in_room()

        try:
            async with redis_context_manager() as redis_client:
                async for msg in self._ws:
                    encoded_msg = json.dumps(
                        {
                            "room_id": self._room_id,
                            "message": msg,
                        }
                    )
                    await redis_client.client.publish(
                        self.pub_sub_type,
                        encoded_msg,
                    )

        finally:
            await self.unregister_ws(self._ws)

    async def register_ws_in_room(self) -> None:
        if self._room_id not in rooms_local.keys():
            rooms_local[self._room_id] = set()

        rooms_local[self._room_id].add(self._ws)

    @staticmethod
    async def unregister_ws(ws: WebSocketServerProtocol) -> None:
        for room_id, set_ws in rooms_local.items():
            set_ws.discard(ws)

            if not set_ws:
                del rooms_local[room_id]


class ChatRoomBroadcaster:

    async def broadcast(self) -> None:
        async with redis_context_manager() as redis_client:
            pubsub = redis_client.client.pubsub()
            await pubsub.subscribe(ChatRoomHandler.pub_sub_type)

            async for msg in pubsub.listen():
                if msg["type"] == "message":
                    ws_to_remove = list()

                    msg_data = json.loads(msg["data"])
                    room_id: str = msg_data["room_id"]
                    text: str = msg_data["message"]

                    for ws in rooms_local.get(room_id, []):
                        try:
                            await ws.send(text)

                        except websockets.exceptions.ConnectionClosed:
                            ws_to_remove.append(ws)

                    await self._remove_ws(ws_to_remove)

    @staticmethod
    async def _remove_ws(ws_lst: list[WebSocketServerProtocol]) -> None:
        for ws in ws_lst:
            await ChatRoomHandler.unregister_ws(ws)
