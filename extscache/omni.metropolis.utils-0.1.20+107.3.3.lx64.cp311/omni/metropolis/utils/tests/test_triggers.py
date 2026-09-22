from dataclasses import dataclass
import omni.kit
import carb
import omni.kit.test
import omni.usd
import omni.timeline
from omni.metropolis.utils.triggers.core import TriggerBase, TriggersManager  # noqa: F401
from omni.metropolis.utils.triggers.time_trigger import TimeTrigger
from omni.metropolis.utils.triggers.carb_event_trigger import CarbEventTrigger


def get_curr_time_frame(t: omni.timeline.ITimeline) -> int:
    return round(t.time_to_time_code(t.get_current_time()) * t.get_ticks_per_frame())


class TestTriggers(omni.kit.test.AsyncTestCase):
    async def setUp(self):
        pass

    async def tearDown(self):
        pass

    async def test_triggers_manager(self):
        """
        Test if trigger manager can register and deregister a trigger class as well as creating trigger instances.
        """

        @dataclass
        class MockTrigger(TriggerBase):
            type_name = "mock_trigger"
            mock_int: int = 5

        # Register
        manager = TriggersManager.get_instance()
        manager.register_trigger_type([MockTrigger])
        self.assertTrue(MockTrigger in manager.registered_trigger_types)

        # Create trigger instance
        dict_data = {"trigger": MockTrigger.default_dict()}
        mock_trigger = manager.create_trigger_by_dict(dict_data)
        self.assertTrue(mock_trigger)
        self.assertEqual(mock_trigger.to_dict(), dict_data)

        # Deregister
        manager.deregister_trigger_type([MockTrigger])
        self.assertTrue(MockTrigger not in manager.registered_trigger_types)

    async def test_time_trigger(self):
        """
        Test if TimeTrigger can be created and triggered properly.
        """
        await omni.usd.get_context().new_stage_async()
        await omni.kit.app.get_app().next_update_async()

        # Set up timeline in new scene
        timeline = omni.timeline.get_timeline_interface()
        timeline.set_time_codes_per_second(30)
        timeline.set_end_time(100.0)
        timeline.commit_silently()

        # Check if TimeTrigger is registered
        manager = TriggersManager.get_instance()
        self.assertTrue(TimeTrigger in manager.registered_trigger_types)

        # Create TimeTrigger instance
        dict_data = {"trigger": {"type": "time", "time": 3}}
        time_trigger = manager.create_trigger_by_dict(dict_data)
        self.assertTrue(time_trigger)

        # Add callback
        is_triggered = False
        triggered_frame_num = -1

        def callback_fn(t):
            nonlocal is_triggered
            is_triggered = True
            nonlocal triggered_frame_num
            t = omni.timeline.get_timeline_interface()
            triggered_frame_num = get_curr_time_frame(t)

        time_trigger.add_callback(callback_fn)

        # Play timeline
        while not timeline.is_playing():
            timeline.play()
            await omni.kit.app.get_app().next_update_async()

        # Wait for 5 seconds
        frame_num = get_curr_time_frame(timeline)
        while frame_num < 150 and not is_triggered:
            frame_num = get_curr_time_frame(timeline)
            await omni.kit.app.get_app().next_update_async()

        # Check trigger result
        self.assertTrue(is_triggered)
        self.assertEqual(int(triggered_frame_num), 90)

        # Clean up
        timeline.stop()
        await omni.usd.get_context().close_stage_async()
        del time_trigger
        time_trigger = None

    async def test_carb_event_trigger(self):
        """
        Test if CarbEventTrigger can be created and triggered properly.
        """
        # Check if CarbEventTrigger is registered
        manager = TriggersManager.get_instance()
        self.assertTrue(CarbEventTrigger in manager.registered_trigger_types)

        # Creat CarbEventTrigger instance
        event_name = "omni.metropolis.utils/test/test_carb_event_trigger"
        dict_data = {"trigger": {"type": "carb_event", "event_name": event_name}}
        carb_event_trigger = manager.create_trigger_by_dict(dict_data)
        self.assertTrue(carb_event_trigger)

        # Add callback
        is_triggered = False

        def callback_fn(t):
            nonlocal is_triggered
            is_triggered = True
            print("test carb event trigger callback is called.")

        carb_event_trigger.add_callback(lambda t: callback_fn(None))

        for i in range(5):
            await omni.kit.app.get_app().next_update_async()

        # Dispatch carb event
        carb.eventdispatcher.get_eventdispatcher().dispatch_event(
            event_name=event_name, payload={"Payload": {"test_int": 5}}
        )

        for i in range(5):
            await omni.kit.app.get_app().next_update_async()

        # Check trigger result
        self.assertTrue(is_triggered)
        self.assertEqual(carb_event_trigger.payload, {"test_int": 5})

        # Clean up
        del carb_event_trigger
        carb_event_trigger = None
