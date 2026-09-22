from .pyro_event_manager import PyroEventManager

from .scene_tagging import SceneTaggingData, AttributeUSDTagger
from .pyro_event import PyroEvent

from ..incident_report import IncidentReport


class PyroDemonCompositionRoot:

    @staticmethod
    def create_scene_tagging_data():
        return SceneTaggingData()

    @staticmethod
    def create_attribute_usd_tagger():
        return AttributeUSDTagger()

    @staticmethod
    def create_pyro_event(name: str, selected_flammable_item: str, pyro_nearby_radius: float = 0.0):
        return PyroEvent(name, selected_flammable_item, pyro_nearby_radius)

    @staticmethod
    def create_pyro_event_manager(data_path: str, random_seed: int = 123456, report: IncidentReport = None):
        return PyroEventManager(
            PyroDemonCompositionRoot.create_scene_tagging_data,
            PyroDemonCompositionRoot.create_attribute_usd_tagger,
            PyroDemonCompositionRoot.create_pyro_event,
            data_path,
            random_seed,
            report,
        )
