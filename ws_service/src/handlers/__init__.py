from .chat_room_handler import ChatRoomBroadcaster, ChatRoomHandler

handlers_type = {
    "/chat_room/\\d": ChatRoomHandler,
}

__all__ = ["handlers_type", "ChatRoomBroadcaster"]
