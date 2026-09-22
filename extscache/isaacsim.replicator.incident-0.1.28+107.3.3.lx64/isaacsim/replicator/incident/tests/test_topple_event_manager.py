from isaacsim.replicator.incident.topple_demon.topple_demon import ToppleEventManager
import omni.kit.test
from isaacsim.replicator.incident.settings import GlobalValues
from isaacsim.replicator.incident.config_file_defines import IncidentEventSection, ToppleEventProperty
import os
from isaacsim.replicator.incident.topple_demon.scene_tagging import SceneTaggingData
from omni.metropolis.utils.triggers.core import TriggersManager
from unittest.mock import Mock, MagicMock, patch


class TestToppleEventManager(omni.kit.test.AsyncTestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    async def test_topple_event_manager_initialization(self):
        file_path = os.path.join(os.path.dirname(__file__), "test_data", "incidents_config.yaml")
        config_file = GlobalValues.config_file_format.load_config_file(file_path)
        self.assertIsNotNone(config_file)

        # Get the incident section
        incident_section = config_file.get_section("event")

        scene_tagging_data = SceneTaggingData()
        scene_tagging_data.add_loose_item("/World/topple_object", "loose_item")
        usd_tagger = Mock()
        usd_tagger.Read.return_value = scene_tagging_data
        usd_tagger_factory = Mock()
        usd_tagger_factory.return_value = usd_tagger
        topple_event_observer_manager = Mock()
        topple_event_setup_factory = Mock()
        topple_event_setup = Mock()
        topple_event_setup.selected_loose_items = ["/World/topple_object"]
        topple_event_setup_factory.return_value = topple_event_setup
        topple_event_manager = ToppleEventManager(
            usd_tagger_factory, topple_event_observer_manager, topple_event_setup_factory, 1, None
        )

        trigger = MagicMock()
        trigger.__bool__.return_value = True
        triggers_manager = Mock()
        triggers_manager.create_trigger_by_dict = Mock(return_value=trigger)

        # Store the callback that was passed to add_callback
        callback = None

        def capture_callback(cb):
            nonlocal callback
            callback = cb

        trigger.add_callback.side_effect = capture_callback

        @patch("omni.metropolis.utils.triggers.core.TriggersManager.get_instance")
        def test_function(mock_function):
            mock_function.return_value = triggers_manager

            # Get the pyro event property
            incident_list = incident_section.get_property_group("event_list")
            for event_prop in incident_list.data_group:
                if isinstance(event_prop, ToppleEventProperty):
                    topple_event_manager.generate_topple_event_from_property(event_prop)

            triggers_manager.create_trigger_by_dict.assert_called_once()
            trigger.add_callback.assert_called_once()
            topple_event_setup_factory.assert_called_once()

            # Call the callback that was passed to add_callback
            assert callback is not None
            callback(trigger)
            topple_event_setup.trigger_topple_event.assert_called_once()

        test_function()
