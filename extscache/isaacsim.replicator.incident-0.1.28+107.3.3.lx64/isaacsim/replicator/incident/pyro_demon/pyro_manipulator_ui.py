# flake8: noqa

import omni
import omni.ui as ui
from omni.kit.menu.utils import MenuHelperWindow
import carb

from ..sceneview_ui_helper import BBoxDrawerHelper
from omni.ui import color as cl
from pxr import UsdGeom, Gf, Usd, UsdPhysics

from .scene_tagging import SceneTaggingData, AttributeUSDTagger
from .pyro_event_manager import PyroEventManager

from .composition_root import PyroDemonCompositionRoot

import os
import omni.kit.commands
from pxr import Sdf


class PyroManipulatorUI(MenuHelperWindow):

    def __init__(self, data_path: str):
        super().__init__(title="PyroManipulator", width=250, height=500, dockPreference=ui.DockPreference.RIGHT)
        self.canvas = None
        self.scene_view = None

        self._scene_tagging_data: SceneTaggingData = None
        self._USDTagger: AttributeUSDTagger = None

        self.pyro_event_manager = PyroDemonCompositionRoot.create_pyro_event_manager(data_path)
        self.load_scene()
        self.setup()

    def load_scene(self):
        self._scene_tagging_data = SceneTaggingData()
        self._USDTagger = AttributeUSDTagger()
        self._scene_tagging_data = self._USDTagger.Read()

    def destroy(self):
        self.pyro_event_manager = None
        self._scene_tagging_data = None
        self._USDTagger = None

    def setup(self):
        with self.frame:
            with ui.VStack():

                def on_generate_pyro_event():
                    selection = omni.usd.get_context().get_selection().get_selected_prim_paths()
                    if len(selection) == 0:
                        carb.log_error("No selection found")
                        return

                    self.pyro_event_manager.generate_pyro_event("pyro_event", selection[0])
                    self.pyro_event_manager.add_time_trigger("pyro_event", 1.0)

                ui.Button("Generate Pyro Event", clicked_fn=on_generate_pyro_event)
