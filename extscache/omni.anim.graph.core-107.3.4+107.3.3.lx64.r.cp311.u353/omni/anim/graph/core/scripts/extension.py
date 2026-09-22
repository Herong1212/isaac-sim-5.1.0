from .command import *
from .variables_service import VariablesService

import omni.ext
import omni.anim.graph.core as ag
from pathlib import Path


class PublicExtension(omni.ext.IExt):
    def _regist_animationgraph_stage_icon(self):
        try:
            import omni.kit.widget.stage
        except ImportError:
            return
        stage_icons = omni.kit.widget.stage.StageIcons()
        current_path = Path(__file__).parent
        icon_path = current_path.parent.parent.parent.parent.parent.joinpath("icons")
        file_path = icon_path.joinpath("animation_graph.svg")
        stage_icons.set("AnimationGraph", file_path)

    def on_startup(self):
        self._plugin = ag.acquire_interface()
        self._variable_service = VariablesService()
        self._regist_animationgraph_stage_icon()

    def on_shutdown(self):
        if self._variable_service:
            self._variable_service.destroy()
            self._variable_service = None
        ag.release_interface(self._plugin)
