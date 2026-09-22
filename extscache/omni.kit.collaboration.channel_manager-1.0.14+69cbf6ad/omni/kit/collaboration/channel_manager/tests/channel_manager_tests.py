import unittest
from unittest.mock import patch, Mock
from threading import Timer
import omni.client
import omni.kit.test
import omni.kit.app
import omni.kit.collaboration.channel_manager as cm

from omni.kit.collaboration.channel_manager.manager import _build_message_in_bytes


class TestChannelManager(omni.kit.test.AsyncTestCase):  # pragma: no cover
    BASE_URL = "omniverse://localhost/Projects/tests/omni.kit.collaboration.channel_manger/"

    # Before running each test
    async def setUp(self):
        self.previous_retry_values = omni.client.set_retries(0, 0, 0)
        self.app = omni.kit.app.get_app()
        self.current_message = None

    async def tearDown(self):
        omni.client.set_retries(*self.previous_retry_values)

    async def _wait(self, frames=10):
        for i in range(frames):
            await self.app.next_update_async()

    async def test_join_invalid_omniverse_url(self):
        channel = await cm.join_channel_async("file://c/invalid_url.channel")
        self.assertFalse(channel)
        channel = await cm.join_channel_async("fake-domain://invalid/invalid_url.channel")
        self.assertFalse(channel)

    async def test_peer_user_and_message_api(self):
        peer_user = cm.PeerUser("test_id", "test", "Create")
        self.assertEqual(peer_user.user_id, "test_id")
        self.assertEqual(peer_user.user_name, "test")
        self.assertEqual(peer_user.from_app, "Create")

        content = {"key" : "value"}
        message = cm.Message(peer_user, cm.MessageType.HELLO, content=content)
        self.assertEqual(message.from_user, peer_user)
        self.assertEqual(message.message_type, cm.MessageType.HELLO)
        self.assertEqual(message.content, content)

    def __mock_join_channel_with_callback(self, url, callback):
        callback(omni.client.Result.OK, omni.client.ChannelEvent.JOIN, None, None)

        return Mock(is_finished=lambda: False, id=1000)

    @patch("omni.client.send_message_async")
    @patch("omni.client.join_channel_with_callback")
    @patch("omni.client.get_server_info_async")
    async def test_api(self, get_server_info_async, join_channel_with_callback, send_message_async):
        test_url = self.BASE_URL + "test.channel"

        def subscriber(message: cm.Message):
            self.current_message = message

        # Simulate join failure
        get_server_info_async.return_value = (omni.client.Result.ERROR, None)
        channel = await cm.join_channel_async(test_url)
        self.assertTrue(channel is None)
        get_server_info_async.assert_called_once()

        mock_server_info = Mock(username="test", connection_id="test")
        get_server_info_async.return_value = (omni.client.Result.OK, mock_server_info)
        join_channel_with_callback.side_effect = self.__mock_join_channel_with_callback
        send_message_async.return_value = omni.client.Result.OK
        channel = await cm.join_channel_async(test_url)
        self.assertTrue(channel)
        handle = channel.add_subscriber(subscriber)
        self.assertTrue(channel is not None)
        self.assertEqual(channel.url, test_url)
        self.assertEqual(channel.logged_user_name, "test")
        self.assertEqual(channel.logged_user_id, "test")
        self.assertTrue(channel.stopped is False)

        # Send empty message
        result = await channel.send_message_async({})
        self.assertTrue(result == omni.client.Result.OK)

        # Send more
        result = await channel.send_message_async({"test": "message_content"})
        self.assertTrue(result == omni.client.Result.OK)

        # Simulates multi-users
        user_id = 0
        for message_type in [cm.MessageType.JOIN, cm.MessageType.HELLO, cm.MessageType.LEFT]:
            self.current_message = None
            content = _build_message_in_bytes("test", message_type, {})
            channel._handler()._handle_message(omni.client.ChannelEvent.MESSAGE, str(user_id), content)
            self.assertTrue(self.current_message is not None)
            self.assertEqual(self.current_message.message_type, message_type)
            self.assertEqual(self.current_message.from_user.user_id, str(user_id))
            self.assertEqual(self.current_message.from_user.user_name, "test")

            # Don't increment user id for LEFT message as LEFT message will not be handled if user is not logged.
            if message_type == cm.MessageType.JOIN:
                user_id += 1

        # Simulates customized message
        self.current_message = None
        content = {"test_key": "content"}
        message = _build_message_in_bytes("test", cm.MessageType.MESSAGE, content)
        channel._handler()._handle_message(omni.client.ChannelEvent.MESSAGE, str(user_id), message)

        self.assertTrue(self.current_message)
        self.assertEqual(self.current_message.message_type, cm.MessageType.MESSAGE)
        self.assertEqual(self.current_message.content, content)

        # Channel's LEFT message will be treated as left too.
        self.current_message = None
        channel._handler()._handle_message(omni.client.ChannelEvent.LEFT, str(user_id), None)
        self.assertEqual(self.current_message.message_type, cm.MessageType.LEFT)

        handle.unsubscribe()

    @patch("omni.client.send_message_async")
    @patch("omni.client.join_channel_with_callback")
    @patch("omni.client.get_server_info_async")
    async def test_synchronization(self, get_server_info_async, join_channel_with_callback, send_message_async):
        mock_server_info = Mock(username="test", connection_id="test")
        get_server_info_async.return_value = (omni.client.Result.OK, mock_server_info)
        join_channel_with_callback.side_effect = self.__mock_join_channel_with_callback
        send_message_async.return_value = omni.client.Result.OK

        test_url = self.BASE_URL + "test.channel"
        for i in range(20):
            channel = await cm.join_channel_async(test_url)
            self.assertTrue(not not channel)

    @patch("omni.client.send_message_async")
    @patch("omni.client.join_channel_with_callback")
    @patch("omni.client.get_server_info_async")
    async def test_error_connection(self, get_server_info_async, join_channel_with_callback, send_message_async):
        def __mock_join_channel_with_callback_error(url, callback):
            def delayed_function():
                callback(omni.client.Result.ERROR_CONNECTION, omni.client.ChannelEvent.ERROR, None, None)
            callback(omni.client.Result.OK, omni.client.ChannelEvent.JOIN, None, None)
            Timer(0.001, delayed_function).start()
            return Mock(is_finished=lambda: False, id=1000)

        def subscriber(message: cm.Message):
            self.current_message = message

        # Simulates a normal/successful join
        test_url = self.BASE_URL + "test.channel"
        mock_server_info = Mock(username="test", connection_id="test")
        get_server_info_async.return_value = (omni.client.Result.OK, mock_server_info)
        join_channel_with_callback.side_effect = __mock_join_channel_with_callback_error
        send_message_async.return_value = omni.client.Result.OK
        channel = await cm.join_channel_async(test_url)
        self.assertTrue(channel is not None)
        self.assertEqual(channel.url, test_url)
        self.assertEqual(channel.logged_user_name, "test")
        self.assertEqual(channel.logged_user_id, "test")
        self.assertTrue(channel.stopped is False)

        # Simulates capturing connection error
        handle = channel.add_subscriber(subscriber)
        await self._wait(3)
        self.assertEqual(self.current_message.message_type, cm.MessageType.ERROR)
        handle.unsubscribe()
