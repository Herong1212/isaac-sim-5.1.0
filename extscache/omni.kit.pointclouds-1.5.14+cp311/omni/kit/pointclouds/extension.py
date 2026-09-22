# Copyright (c) 2021-2024, NVIDIA CORPORATION. All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto. Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
from typing import Any

import carb
import omni.ext

from .e57_importer import E57Importer
from .lidar_bin_importer import LidarBINImporter
from .pts_importer import PTSImporter


class PointCloudsExtension(omni.ext.IExt):
    instance = None

    def on_startup(self, ext_id):
        PointCloudsExtension.instance = self
        manager = omni.kit.app.get_app().get_extension_manager()
        self._extension_path = manager.get_extension_path(ext_id)

        self._potree_delegate = None
        self._pointcloud_manager_hook = manager.subscribe_to_extension_enable(
            lambda *_: self._init_pointcloud_manager(),
            lambda *_: self._destroy_pointcloud_manager(),
            ext_name="omni.pointcloud.manager",
            hook_name="omni.kit.pointcloud listener for omni.pointcloud.manager",
        )

        self._e57_pointcloud_browser = None
        self._pointcloud_content_browser_hook = manager.subscribe_to_extension_enable(
            lambda *_: self._init_e57_pointcloud_browser(),
            lambda *_: self._destroy_e57_pointcloud_browser(),
            ext_name="omni.pointcloud.content_browser",
            hook_name="omni.kit.pointcloud listener for omni.pointcloud.content_browser",
        )

        self._pts_importer = None
        self._lidar_bin_importer = None
        self._flowusd_hook = manager.subscribe_to_extension_enable(
            lambda *_: self._init_flowusd(),
            lambda *_: self._destroy_flowusd(),
            ext_name="omni.flowusd",
            hook_name="omni.kit.pointcloud listener for omni.flowusd",
        )

        # default importers
        self._importers = [E57Importer(self._extension_path)]
        for importer in self._importers:
            omni.kit.tool.asset_importer.register_importer(importer)

        self._add_drop_handler()

    def on_shutdown(self):
        self._destroy_pointcloud_manager()
        self._destroy_e57_pointcloud_browser()
        for importer in self._importers:
            omni.kit.tool.asset_importer.remove_importer(importer)
            importer.destroy()
        self._e57_pointcloud_browser = None
        self._pointcloud_content_browser_hook = None
        self._importers = None
        PointCloudsExtension.instance = None
        self._remove_drop_handler()

    def _init_pointcloud_manager(self):
        if not self._potree_delegate:
            try:
                from omni.pointcloud.manager import register_potree_api_delegate
            except ImportError:
                carb.log_warn("Failed to import omni.pointcloud.manager")
                return

            try:
                from .e57_potree_api_delegate import E57PotreeApiDelegate

                self._potree_delegate = register_potree_api_delegate(E57PotreeApiDelegate)
            except ImportError:
                carb.log_warn("Failed to import PotreeApiDelegate")
                return

    def _destroy_pointcloud_manager(self):
        if self._potree_delegate:
            try:
                from omni.pointcloud.manager import unregister_potree_api_delegate
            except ImportError:
                carb.log_warn("Failed to import omni.pointcloud.manager")
                return

            unregister_potree_api_delegate(self._potree_delegate)
            self._potree_delegate = None

    def _init_e57_pointcloud_browser(self):
        if not self._e57_pointcloud_browser:
            from .e57_pointcloud_browser import E57PointCloudBrowser

            self._e57_pointcloud_browser = E57PointCloudBrowser()
            self._e57_pointcloud_browser.fetch_e57_files()

    def _destroy_e57_pointcloud_browser(self):
        if self._e57_pointcloud_browser:
            self._e57_pointcloud_browser.destroy()
            self._e57_pointcloud_browser = None

    def _init_flowusd(self):
        self._pts_importer = PTSImporter(self._extension_path)
        self._lidar_bin_importer = LidarBINImporter(self._extension_path)
        omni.kit.tool.asset_importer.register_importer(self._pts_importer)
        omni.kit.tool.asset_importer.register_importer(self._lidar_bin_importer)

    def _destroy_flowusd(self):
        if self._pts_importer:
            omni.kit.tool.asset_importer.remove_importer(self._pts_importer)
            self._pts_importer.destroy()
        self._pts_importer = None

        if self._lidar_bin_importer:
            omni.kit.tool.asset_importer.remove_importer(self._lidar_bin_importer)
            self._lidar_bin_importer.destroy()
        self._lidar_bin_importer = None

    def _add_drop_handler(self):
        try:
            from omni.kit.widget.stage import DragAndDropRegistry

            def filter_fn(source: Any) -> bool:
                return isinstance(source, str) and source.endswith(".e57")

            def handler_fn(source: Any, target_item: Any) -> None:
                try:
                    from omni.kit.window import popup_dialog

                    dialog = popup_dialog.MessageDialog(
                        title="Not supported feature",
                        message="Drag and drop of e57 files is not yet supported. Please use File/Import.",
                        disable_okay_button=True,
                        width=410,
                    )
                    dialog.show()
                except (ImportError, ModuleNotFoundError):
                    pass

            DragAndDropRegistry().register_drop_handler("omni.kit.pointclouds.e57_import", filter_fn, handler_fn)
        except (ImportError, ModuleNotFoundError):
            pass

    def _remove_drop_handler(self):
        try:
            from omni.kit.widget.stage import DragAndDropRegistry

            DragAndDropRegistry().deregister_drop_handler("omni.kit.pointclouds.e57_import")
        except (ImportError, ModuleNotFoundError):
            pass


def get_pointclouds_instance():
    return PointCloudsExtension.instance
