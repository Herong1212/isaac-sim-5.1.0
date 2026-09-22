import omni.ext
from omni.physics.stageupdate.bindings._physicsStageUpdateNode import (
    release_physics_stage_update_node_interface,
    release_physics_stage_update_node_scripting,
)

from .. import get_physics_stage_update_node_interface
from .live_sync import StageUpdateLiveSync


class OmniPhysXStageUpdateExtension(omni.ext.IExt):
    def on_startup(self):
        self._physics_stage_update_node_interface = get_physics_stage_update_node_interface()
        self._live_sync = StageUpdateLiveSync()
        self._live_sync.startup(self._physics_stage_update_node_interface)

    def on_shutdown(self):
        self._live_sync.shutdown()
        self._live_sync = None
        release_physics_stage_update_node_interface(self._physics_stage_update_node_interface)
        release_physics_stage_update_node_scripting(self._physics_stage_update_node_interface)  # OM-60917
        self._physics_stage_update_node_interface = None
