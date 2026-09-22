import carb
import omni.ext
import omni.kit.commands
import omni.kit.ui
import omni.ui as ui
from omni.kit.menu.utils import MenuHelperWindow
from isaacsim.sensors.rtx.placement.ui.camera_placement_panel import CameraPlacementPanel


class CameraPlacementWindow(MenuHelperWindow):
    def __init__(self):
        super().__init__(
            title="Camera Placement",
            width=300,
            height=200,
            dockPreference=ui.DockPreference.RIGHT,
        )
        # Build out the scene
        self.frame.set_build_fn(self._build_ui)

    def destroy(self) -> None:
        self._camera_placement_panel = None

    def _build_ui(self):
        self.deferred_dock_in("Stage", ui.DockPolicy.CURRENT_WINDOW_IS_ACTIVE)
        self.dock_order = 4
        with self.frame:
            with ui.ScrollingFrame():
                with ui.VStack(spacing=0):
                    self._camera_placement_panel = CameraPlacementPanel()
                    self._camera_placement_panel.build_ui_frame()
