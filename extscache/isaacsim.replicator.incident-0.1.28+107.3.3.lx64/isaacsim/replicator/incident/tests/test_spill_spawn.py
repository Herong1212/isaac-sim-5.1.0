import omni.kit.test
import omni.usd
import carb
import os
from isaacsim.replicator.incident.spill_demon.spill_event_from_asset import SpillEventFromAsset
from isaacsim.replicator.incident.spill_demon.spill_event_manager import SpillEventManager
from unittest.mock import Mock, MagicMock, patch
from pxr import Usd, Sdf, UsdGeom, Gf

from isaacsim.replicator.incident.spill_demon.scene_tagging import SceneTaggingData
from isaacsim.replicator.incident.settings import GlobalValues
from isaacsim.replicator.incident.config_file_defines import IncidentEventSection, SpillEventProperty
from omni.metropolis.utils.triggers.core import TriggersManager


class TestSpillEventManager(omni.kit.test.AsyncTestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    async def test_spill_event_manager_initialization(self):
        file_path = os.path.join(os.path.dirname(__file__), "test_data", "incidents_config.yaml")
        config_file = GlobalValues.config_file_format.load_config_file(file_path)
        self.assertIsNotNone(config_file)

        # Get the incident section
        incident_section = config_file.get_section("event")

        scene_tagging_data = SceneTaggingData()
        scene_tagging_data.add_leakable_item("/World/spill_object", "leakable_item")
        scene_tagging_data.add_spillable_area("/World/spill_area", "spillable_area")

        usd_tagger = Mock()
        usd_tagger.Read.return_value = scene_tagging_data
        usd_tagger_factory = Mock()
        usd_tagger_factory.return_value = usd_tagger

        spill_event = Mock()
        spill_event_factory = Mock()
        spill_event_factory.return_value = spill_event

        spill_event_manager = SpillEventManager(usd_tagger_factory, spill_event_factory, 1, None)

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

            # Get the spill event property
            incident_list = incident_section.get_property_group("event_list")
            for event_prop in incident_list.data_group:
                if isinstance(event_prop, SpillEventProperty):
                    spill_event_manager.generate_spill_event_from_property(event_prop)

            triggers_manager.create_trigger_by_dict.assert_called_once()
            trigger.add_callback.assert_called_once()
            spill_event_factory.assert_called_once()

            # Call the callback that was passed to add_callback
            assert callback is not None
            callback(trigger)
            spill_event.on_trigger_spill.assert_called_once()

        test_function()
