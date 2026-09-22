# Public API for module omni.kit.collaboration.channel_manager:

## Classes

- class Channel
  - def __init__(self, handler: weakref, channel_manager: weakref)
  - [property] def stopped(self)
  - [property] def logged_user_name(self)
  - [property] def logged_user_id(self)
  - [property] def peer_users(self) -> Dict[str, PeerUser]
  - [property] def url(self)
  - def stop(self) -> asyncio.Future
  - def add_subscriber(self, on_message: Callable[[Message], None]) -> ChannelSubscriber
  - async def send_message_async(self, content: dict) -> omni.client.Request

- class ChannelSubscriber
  - def __init__(self, message_handler: Callable[[Message], None], channel: weakref)
  - def unsubscribe(self)

- class PeerUser
  - def __init__(self, user_id: str, user_name: str, from_app: str)
  - [property] def user_id(self)
  - [property] def user_name(self)
  - [property] def from_app(self)

- class Message
  - def __init__(self, from_user: PeerUser, message_type: MessageType, content: dict)
  - [property] def from_user(self) -> PeerUser
  - [property] def message_type(self) -> MessageType
  - [property] def content(self) -> dict

- class MessageType
  - JOIN: str
  - HELLO: str
  - GET_USERS: str
  - LEFT: str
  - MESSAGE: str
  - ERROR: str

## Functions

- async def join_channel_async(url: str, get_users_only = False) -> Channel
