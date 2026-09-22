## Copyright (c) 2023, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##
import omni.kit.test
import json
import carb.events
import carb.settings
import omni.kit.livestream.messaging as messaging
import omni.kit.app


class TestLivestreamMessaging(omni.kit.test.AsyncTestCase):
    async def setUp(self):
        pass

    async def tearDown(self):
        pass

    async def test_message_received(self):

        event: carb.events.IEvent = None

        def on_message_received(e):
            nonlocal event
            event = e

        message = """
        {
            "event_type": "SetColor",
            "payload": { "diffuse": [0.0, 1.0, 0.0]}
        }
        """

        message_dict = json.loads(message)

        event_name = carb.settings.get_settings().get("exts/omni.kit.livestream.messaging/receive_message_event")
        event_type = carb.events.type_from_string(event_name)
        message_bus = omni.kit.app.get_app().get_message_bus_event_stream()

        new_event_type = carb.events.type_from_string("SetColor")
        sub = message_bus.create_subscription_to_pop_by_type(new_event_type, on_message_received)

        message_bus.dispatch(event_type, payload={"message": message})
        message_bus.pump()

        self.assertIsNotNone(event)
        self.assertEqual(event.type, carb.events.type_from_string("SetColor"))
        # IDictionary turns the list into tuple
        self.assertEqual(list(event.payload.get_dict()["diffuse"]), message_dict["payload"]["diffuse"])

        sub.unsubscribe()

    async def test_message_send(self):
        # Setup listening for generic send event
        event = None

        def on_message_received(e):
            nonlocal event
            event = e

        new_event_name = carb.settings.get_settings().get("exts/omni.kit.livestream.messaging/send_message_event")
        new_event_type = carb.events.type_from_string(new_event_name)
        message_bus = omni.kit.app.get_app().get_message_bus_event_stream()
        sub = message_bus.create_subscription_to_pop_by_type(new_event_type, on_message_received)

        # Send custom event_type, it should be converted to raw event.
        messaging.register_event_type_to_send("SetColor")
        event_type = carb.events.type_from_string("SetColor")
        payload = {"diffuse": [0.0, 1.0, 0.0]}
        message_bus.dispatch(event_type, payload=payload)
        message_bus.pump()

        self.assertIsNotNone(event)
        self.assertEqual(event.type, new_event_type)
        expected_payload = '{"event_type": "SetColor", "payload": {"diffuse": [0.0, 1.0, 0.0]}}'
        self.assertEqual(event.payload["message"], expected_payload)

        sub.unsubscribe()
        messaging.unregister_event_type_to_send("SetColor")
