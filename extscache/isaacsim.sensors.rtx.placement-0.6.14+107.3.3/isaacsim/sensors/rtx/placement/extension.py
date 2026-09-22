import asyncio
import gc
import logging
import os

import carb
import omni.ext
import omni.ui as ui

##from .widget_info_scene import WidgetInfoScene
from omni.kit.menu.utils import MenuItemDescription, MenuHelperExtensionFull
from isaacsim.sensors.rtx.placement.camera_calibration.camera_calibration_manager import (
    CameraCalibrationManager,
)
from isaacsim.sensors.rtx.placement.ui.camera_calibration_window import CameraCalibrationWindow
from isaacsim.sensors.rtx.placement.ui.camera_placement_window import CameraPlacementWindow
from omni.metropolis.utils.ui_util import UIUtil


class Extension(omni.ext.IExt):
    def on_startup(self, ext_id):
        self._ext_id = ext_id
        self._menu_helper = MenuHelperExtensionFull()
        # build ui panel
        # initialize the camera_calibraiton manager:
        self.camera_calibration_manager = CameraCalibrationManager.get_instance()
        self.start_extension()

    def on_shutdown(self):
        async def shutdown_menu_helper(menu_helper):
            # First make sure all windows are closed
            for i in range(len(menu_helper._window_list)):
                menu_helper.show_window(None, False, i)
            # Wait for MenuHelperExtensionFull._destroy_window_async to trigger
            await omni.kit.app.get_app().next_update_async()
            # Wait for MenuHelperExtensionFull._destroy_window_async to finish
            await omni.kit.app.get_app().next_update_async()
            # Finally we shutdown the menu
            menu_helper.menu_shutdown()

        asyncio.ensure_future(shutdown_menu_helper(self._menu_helper))

        # Clean variables
        self.camera_calibration_manager = None

    def start_extension(self):
        idx_calibration_window = self._menu_helper.menu_startup(
            lambda: CameraCalibrationWindow(self._ext_id), "Camera Calibration", "Camera Calibration", "Tools/Sensors"
        )
        idx_camera_placement = self._menu_helper.menu_startup(
            lambda: CameraPlacementWindow(), "Camera Placement", "Camera Placement", "Tools/Sensors"
        )
        self._menu_helper.show_window("", False, idx_calibration_window)
        self._menu_helper.show_window("", False, idx_camera_placement)

        # Temporary solution to trigger menu refresh
        # since menu helper doest not trigger it at start
        import omni.kit.menu.utils

        omni.kit.menu.utils.rebuild_menus()
