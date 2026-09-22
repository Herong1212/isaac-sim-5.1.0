from ..incident_report import IncidentReport

from .topple_event_setup import ToppleEventSetup
from .scripts.loose_item_mono_b_script import LooseItemMonoBScript

from .topple_event_observer import ToppleEventObserverManager

from .scene_tagging import SceneTaggingData, AttributeUSDTagger

from .topple_demon import ToppleEventManager  # , DebugDrawToppleEventManager


class ToppleDemonCompositionRoot:

    @staticmethod
    def create_loose_item_mono_b_script(prim_path):
        return LooseItemMonoBScript(prim_path)

    @staticmethod
    def create_topple_event_setup(scene_tagging_data, event_name, topple_prim_path, random, topple_nearby_radius=0.0):
        return ToppleEventSetup(
            ToppleDemonCompositionRoot.create_loose_item_mono_b_script,
            scene_tagging_data,
            event_name,
            topple_prim_path,
            random,
            topple_nearby_radius,
        )

    @staticmethod
    def create_topple_event_observer_manager():
        return ToppleEventObserverManager()

    @staticmethod
    def create_scene_tagging_data():
        return SceneTaggingData()

    @staticmethod
    def create_attribute_usd_tagger():
        return AttributeUSDTagger()

    @staticmethod
    def create_topple_event_manager(random_seed=123456, report: IncidentReport = None):
        return ToppleEventManager(
            ToppleDemonCompositionRoot.create_attribute_usd_tagger,
            ToppleDemonCompositionRoot.create_topple_event_observer_manager,
            ToppleDemonCompositionRoot.create_topple_event_setup,
            random_seed,
            report,
        )
