import carb
import omni.ext
import omni.kit.commands
import omni.kit.ui
import omni.ui as ui
from omni.kit.menu.utils import MenuHelperWindow
from omni.kit.viewport.utility import get_active_viewport_window
from isaacsim.sensors.rtx.placement.ui.camera_calibration_panel import CameraCalibrationPanel
from isaacsim.sensors.rtx.placement.ui.viewport_scene import ViewportScene


class CameraCalibrationWindow(MenuHelperWindow):
    def __init__(self, ext_id):
        super().__init__(
            title="Camera Calibration",
            width=300,
            height=200,
            dockPreference=ui.DockPreference.RIGHT,
        )
        viewport_window = get_active_viewport_window()
        if not viewport_window:
            carb.log_error("No activated viewport window detected. This must be run within the GUI app.")
            return
        # Build out the scene
        self._viewport = ViewportScene(viewport_window, ext_id)
        self.frame.set_build_fn(self._build_ui)

    def destroy(self) -> None:
        self._calibration_panel = None
        self._viewport.destroy()
        self._viewport = None

    def _build_ui(self):
        self.deferred_dock_in("Stage", ui.DockPolicy.CURRENT_WINDOW_IS_ACTIVE)
        self.dock_order = 4
        with self.frame:
            with ui.ScrollingFrame():
                with ui.VStack(spacing=0):
                    self._calibration_panel = CameraCalibrationPanel(self._viewport)
                    self._calibration_panel.build_ui_frame()
