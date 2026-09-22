from .scripts.spill_animator import SpillAnimator
from .spill_event_from_asset import SpillEventFromAsset
from .spill_event_manager import SpillEventManager
from ..incident_report import IncidentReport
from .scene_tagging import SceneTaggingData, AttributeUSDTagger
from pxr import Sdf


class SpillDemonCompositionRoot:
    def __init__(self, data_path: str):
        self.data_path = data_path

    def create_spill_animator(self, prim_path: Sdf.Path, target_size: float = 1.0, leak_duration: float = 5.0):
        return SpillAnimator(prim_path, target_size, leak_duration)

    def create_spill_event(
        self,
        name: str,
        selected_leakable_item: str,
        spillable_area_prim_paths: list[str],
        target_size: float = 1.0,
        leak_duration: float = 1.0,
    ):
        return SpillEventFromAsset(
            self.create_spill_animator,
            self.data_path,
            name,
            selected_leakable_item,
            spillable_area_prim_paths,
            target_size,
            leak_duration,
        )

    def create_scene_tagging_data(self):
        return SceneTaggingData()

    def create_attribute_usd_tagger(self):
        return AttributeUSDTagger()

    def create_spill_event_manager(self, random_seed=123456, report: IncidentReport = None):
        return SpillEventManager(
            self.create_attribute_usd_tagger,
            self.create_spill_event,
            random_seed,
            report,
        )
