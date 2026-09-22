from .topple_demon.composition_root import ToppleDemonCompositionRoot
from .pyro_demon.composition_root import PyroDemonCompositionRoot
from .spill_demon.composition_root import SpillDemonCompositionRoot
from .incident_manager import IncidentManager


class CompositionRoot:
    def __init__(self, data_path: str):
        self.data_path = data_path
        self.spill_demon_composition_root = SpillDemonCompositionRoot(data_path)

    def create_incident_manager(self):
        return IncidentManager(
            ToppleDemonCompositionRoot.create_topple_event_manager,
            PyroDemonCompositionRoot.create_pyro_event_manager,
            self.spill_demon_composition_root.create_spill_event_manager,
            self.data_path,
        )
