```{csv-table}
**Extension**: {{ extension_version }},**Documentation Generated**: {sub-ref}`today`
```

# Introduction
Extension `omni.kit.collaboration.channel_manager` provides interfaces for creating/managing the Nucleus Channel easily and defines standard protocol for multiple users to do communication in the same channel. At the same time, users can be aware of each other.

# Goal
The Nucleus Channel only provides a way to pub/sub messages from the channel. It does not provide APIs to manage user states, nor complete
application protocol for all clients to understand each other. It's transient and stateless, so that messages that were sent before user has
joined will not be sent again. It does not support P2P message, so that messages sent to the channel are broadcasted to
all users. Therefore, we made the following extensions:

* It's able to query user states from the API, and gets notified when users joined/left.
* It defines application protocol for all clients that support it to communicate with each other.

Currently, no P2P communication is supported still.

# Programming Guide
Here is an async function that joins a channel and sends a string message `hello, world` to the channel.
```python
import omni.kit.collaboration.channel_manager as cm

async join_channel_async(channel_url, on_message: Callable[[cm.Message], None]):
    # Joins the channel, and adds subscriber to subsribe messages.
    channel = await cm.join_channel_async(channel_url)
    if channel:
        channel.add_subscriber(on_message)

        # Sends message in dict
        await channel.send_message_async({"test" : "hello world"})
```
As you can see, the first step is to join a channel with {py:func}`omni.kit.collaboration.channel_manager.join_channel_async`, which will return a handle of the
channel, through which you can query its connection states, other users that joined the same channel, and send messages (see {py:func}`omni.kit.collaboration.channel_manager.Channel.send_message_async`) specific to your applicaton in the format of `Python dict`. Also, it supports adding subscribers through {py:func}`omni.kit.collaboration.channel_manager.Channel.add_subscriber` to subscribe to messages received from the channel. Messages received from other users are in type {py:class}`omni.kit.collaboration.channel_manager.Message`, and depends on the value of its `message_type` property, message can be catagorized into the following types (see {py:class}`omni.kit.collaboration.channel_manager.MessageType` for details):

* `JOIN`: New user joined this channel.
* `HELLO`: Someone said hello to me. Normally, it's received when a new user joined the channel, and other users exist in the channel will reply HELLO so new user could be aware of them.
* `LEFT`: Someone left the channel.
* `GET_USERS`: Ping message to find out who joined this channel. Clients received this message should reply HELLO.
* `MESSAGE`: Application specific message sent through API {py:func}`omni.kit.collaboration.channel_manager.Channel.send_message_async`.
