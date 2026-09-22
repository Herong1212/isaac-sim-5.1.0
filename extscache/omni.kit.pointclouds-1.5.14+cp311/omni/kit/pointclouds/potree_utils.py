# Copyright (c) 2023-2024, NVIDIA CORPORATION. All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto. Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
import asyncio
import os

import carb
import omni.client
import omni.usd
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from .singleton import Singleton


@staticmethod
def create_point_cloud_prim(src_path, render_mode="", pointcloud_path=""):
    # Dependency on omni.pointcloud.manager is optional
    try:
        from omni.pointcloud.manager import get_pointcloud_cache_path
    except ImportError:
        carb.log_warn("omni.pointcloud.manager is not loaded, cannot create point cloud prim!")
        return

    stage = omni.usd.get_context().get_stage()
    if pointcloud_path == "":
        pointcloud_path = omni.usd.get_stage_next_free_path(path="/pointcloud", prepend_default_prim=True, stage=stage)

    prim = stage.GetPrimAtPath(pointcloud_path)
    if not prim:
        # Command from omni.pointcloud.manager
        omni.kit.commands.execute("CreatePointCloudPrim", prim_path=pointcloud_path, stage=stage)

    if prim and prim.IsValid():
        prim.GetAttribute("omni:pointcloud:renderMode").Set(render_mode)
        prim.GetAttribute("omni:pointcloud:source").Set(src_path)

    return pointcloud_path, src_path


async def update_point_cloud_prim(src_path="", render_mode="", pointcloud_path=""):
    """Async version of above function"""

    # Dependency on omni.pointcloud.manager is optional
    try:
        from omni.pointcloud.manager import get_pointcloud_cache_path
    except ImportError:
        carb.log_warn("omni.pointcloud.manager is not loaded, cannot create point cloud prim!")
        return

    stage = omni.usd.get_context().get_stage()
    if pointcloud_path == "":
        pointcloud_path = omni.usd.get_stage_next_free_path(path="/pointcloud", prepend_default_prim=True, stage=stage)

    prim = stage.GetPrimAtPath(pointcloud_path)
    if not prim:
        # Command from omni.pointcloud.manager
        omni.kit.commands.execute("CreatePointCloudPrim", prim_path=pointcloud_path, stage=stage)
        for i in range(10):
            await omni.kit.app.get_app().next_update_async()

    if prim and prim.IsValid():
        if render_mode != "":
            prim.GetAttribute("omni:pointcloud:renderMode").Set(render_mode)

        # Force reset of the source path
        current_src = prim.GetAttribute("omni:pointcloud:source").Get()
        await omni.kit.app.get_app().next_update_async()
        prim.GetAttribute("omni:pointcloud:source").Set("")

        if src_path != "":
            prim.GetAttribute("omni:pointcloud:source").Set(src_path)
        else:
            prim.GetAttribute("omni:pointcloud:source").Set(current_src)

    return pointcloud_path, src_path


class PotreeWatchItem(FileSystemEventHandler):
    def __init__(self, path, voxelize, out_vdb_dir):
        super().__init__()

        self.__observer = Observer()
        self.__observer.schedule(self, path=path, recursive=False)
        self.__observer.start()

        self._voxelize = voxelize

        self.__build_task = None
        self.__loop = asyncio.get_event_loop()

        self._out_vdb_dir = out_vdb_dir
        self._pointcloiud_path = ""

    def destroy(self):
        if self.__observer:
            self.__observer.stop()
            self.__observer.join()
            self.__observer = None

    def on_created(self, event):
        if not event.is_directory and "cloud.js" in event.src_path:
            stage = omni.usd.get_context().get_stage()
            self._pointcloud_path = omni.usd.get_stage_next_free_path(
                path="/pointcloud", prepend_default_prim=True, stage=stage
            )

            # Watchdog calls callback from different thread and USD doesn't like it. We need to import USDA from the main thread.
            if self.__build_task:
                self.__build_task.cancel()
            self.__build_task = asyncio.ensure_future(self._on_created(), loop=self.__loop)

    def on_modified(self, event):
        # check if data directory has been already created to read the r.hrc file
        if event.is_directory:
            return

        if "cloud.js" in event.src_path:
            path = os.path.dirname(event.src_path)
            # Watchdog calls callback from different thread and USD doesn't like it. We need to import USDA from the main thread.
            if self.__build_task:
                self.__build_task.cancel()
            self.__build_task = asyncio.ensure_future(self._on_modified(path), loop=self.__loop)

    async def _on_created(self):
        # wait few updates until the USD files are completely written
        for i in range(10):
            await omni.kit.app.get_app().next_update_async()

        representation = "Volume" if self._voxelize else "Points"
        await update_point_cloud_prim("", representation, self._pointcloud_path)

        # if self._voxelize:
        #     omni.kit.commands.execute("VoxelizePotree", path=out_vdb_dir, neural_vdb=False)

    async def _on_modified(self, src_path):
        # wait few updates until the USD files are completely written
        for i in range(10):
            await omni.kit.app.get_app().next_update_async()

        representation = "Volume" if self._voxelize else "Points"
        await update_point_cloud_prim(src_path, representation, self._pointcloud_path)


class PotreeWatch(metaclass=Singleton):
    def __init__(self):
        self.__items = {}

    def start_watch(self, identifier, voxelize, out_vdb_dir):
        watch_item = self.__items.get(identifier, None)
        if not watch_item:
            watch_item = PotreeWatchItem(identifier, voxelize, out_vdb_dir)
            self.__items[identifier] = watch_item

    def stop_watch(self, identifier):
        if identifier in self.__items:
            self.__items[identifier].destroy()
            del self.__items[identifier]

    def has_watch(self, identifier):
        return identifier in self.__items

    def stop_all(self):
        for _, watch in self.__items.items():
            watch.destroy()

        self.__items = {}
