from isaacsim.replicator.incident.pyro_demon.pyro_event_manager import PyroEventManager
import omni.kit.test
from isaacsim.replicator.incident.settings import GlobalValues
from isaacsim.replicator.incident.config_file_defines import IncidentEventSection, PyroEventProperty
import os
from isaacsim.replicator.incident.pyro_demon.scene_tagging import SceneTaggingData
from omni.metropolis.utils.triggers.core import TriggersManager
from unittest.mock import Mock, MagicMock, patch


class TestPyroEventManager(omni.kit.test.AsyncTestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    async def test_pyro_event_manager_initialization(self):
        file_path = os.path.join(os.path.dirname(__file__), "test_data", "incidents_config.yaml")
        config_file = GlobalValues.config_file_format.load_config_file(file_path)
        self.assertIsNotNone(config_file)

        # Get the incident section
        incident_section = config_file.get_section("event")

        scene_tagging_data = SceneTaggingData()
        scene_tagging_data.add_flammable_item("/World/pyro_object", "flammable_item")

        usd_tagger = Mock()
        usd_tagger.Read.return_value = scene_tagging_data
        usd_tagger_factory = Mock()
        usd_tagger_factory.return_value = usd_tagger

        pyro_event = Mock()
        pyro_event.selected_flammable_item_prim_path = "/World/pyro_object"
        pyro_event_factory = Mock()
        pyro_event_factory.return_value = pyro_event

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
        @patch("omni.usd")
        def test_function(mock_usd, mock_function):
            mock_stage = Mock()
            mock_usd.get_context.return_value.get_stage.return_value = mock_stage
            mock_function.return_value = triggers_manager

            stage = omni.usd.get_context().get_stage()
            assert stage is mock_stage

            pyro_event_manager = PyroEventManager(
                scene_tagging_data_factory=lambda: scene_tagging_data,
                attribute_usd_tagger_factory=usd_tagger_factory,
                pyro_event_factory=pyro_event_factory,
                data_path="/test/path",
                random_seed=1,
                report=None,
            )
            # Get the pyro event property
            incident_list = incident_section.get_property_group("event_list")
            for event_prop in incident_list.data_group:
                if isinstance(event_prop, PyroEventProperty):
                    pyro_event_manager.generate_pyro_event_from_property(event_prop)

            triggers_manager.create_trigger_by_dict.assert_called_once()
            trigger.add_callback.assert_called_once()
            pyro_event_factory.assert_called_once()

            # Call the callback that was passed to add_callback
            assert callback is not None
            callback(trigger)
            pyro_event.trigger_pyro_event.assert_called_once()

        test_function()
