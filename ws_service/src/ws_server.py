import asyncio
import re

from core.app_config import config
from handlers import ChatRoomBroadcaster, handlers_type
from websockets.asyncio.server import serve
from websockets.legacy.server import WebSocketServerProtocol


async def main_handler(ws: WebSocketServerProtocol) -> None:
    path = ws.request.path

    try:
        handler_gen = (p for p in handlers_type.keys() if re.search(p, path))
        handler_key = next(handler_gen)
        handler = handlers_type[handler_key](ws, path)
        await handler.handle()

    except (KeyError, StopIteration):
        await ws.send(f"[!] Error: path '{path}' unknown...")


async def main() -> None:
    server = await serve(main_handler, config.ws_host, config.ws_port)
    asyncio.create_task(ChatRoomBroadcaster().broadcast())
    await server.wait_closed()
