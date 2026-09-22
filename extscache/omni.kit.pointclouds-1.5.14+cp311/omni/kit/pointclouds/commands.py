# Copyright (c) 2020-2024, NVIDIA CORPORATION. All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto. Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
import asyncio
import os
from pathlib import Path

import carb
import omni.kit.commands
from omni.kit.asset_converter import OmniClientWrapper
from pxr import Sdf, Tf

from .potree_utils import create_point_cloud_prim
from .task_runner import submit_task

CACHE_PATH_SETTINGS_KEY = "/persistent/exts/omni.pointcloud.manager/cache_path"
FARM_URI_SETTINGS_KEY = "/exts/omni.pointcloud.manager/service_farm_uri"


class ConvertE57FilesCommand(omni.kit.commands.Command):
    def __init__(self, paths: list, out_dir="", combine_scans=True, center_pointcloud=False, to_usd=False):
        """
        Covert E57 files.

        Args:
            paths: list of file paths, both local or remote files are supported
            out_dir: where to put the output USD files, same directory as an input is the default
            combine_scans: True if scans should be combined into single one, True is default
            center_pointcloud: option to center pointcloud to the scene origin
            to_usd: True to create and reference USD files, False to import Points to the scene
        """

        self._paths = paths
        self._output_dir = out_dir
        self._combine_scans = combine_scans
        self._center_pointcloud = center_pointcloud
        self._to_usd = to_usd

    def do(self):

        if len(self._paths) == 0:
            return

        export_path = ""

        if self._to_usd:
            absolute_path = self._paths[0]
            relative_path = os.path.basename(absolute_path)

            dirname = os.path.dirname(relative_path)
            basename = os.path.basename(relative_path)
            file_name, _ = os.path.splitext(basename)
            file_name_with_ext = file_name + ".usd"

            output_dir = self._output_dir

            if not output_dir:
                output_dir = os.path.dirname(absolute_path)

        async def check_export_path(path):
            if await OmniClientWrapper.exists(path):
                carb.log_warn(f"Warning '{path}' already exists, overwriting.")

            if not await OmniClientWrapper.exists(os.path.dirname(path)):
                await OmniClientWrapper.create_folder(os.path.dirname(path))

        stage = omni.usd.get_context().get_stage()
        prim_path = ""  # specifying empty path not import to current stage

        for path in self._paths:
            if not path.endswith(".e57"):
                carb.log_error("Input file is not e57")
                continue

            if stage:
                new_path = Path(path)
                stem = Tf.MakeValidIdentifier(new_path.stem)
                prim_path = omni.usd.get_stage_next_free_path(stage, "/" + stem, True)

            # Create the parent xform
            xform_prim = stage.DefinePrim(prim_path, "Xform")
            if not xform_prim:
                carb.log_error("Cannot create parent xform where to import the selected file.")

            if self._to_usd:
                export_path = os.path.join(output_dir, dirname, file_name_with_ext)
                export_path = export_path.replace("\\", "/")

                asyncio.ensure_future(check_export_path(export_path))

            merge_arg = "1" if self._combine_scans else "0"
            center_arg = "1" if self._center_pointcloud else "0"
            to_usd = "1" if self._to_usd else "0"
            args = {
                "merge": merge_arg,
                "usd": to_usd,
                "path": str(prim_path),
                "export": str(export_path),
                "center": str(center_arg),
                "rtx": "0",
            }
            Sdf.Layer.FindOrOpen(path, args)

    def undo(self):
        pass


class RunVdbTaskCommand(omni.kit.commands.Command):
    def __init__(self, path: str, out_dir="", local_farm=False, farm_worker_count=0, neural_vdb=False, render_mode=""):
        self._path = path
        self._out_dir = out_dir
        self._local_farm = local_farm
        self._farm_worker_count = farm_worker_count
        self._neural_vdb = neural_vdb
        self._render_mode = render_mode

    def do(self):
        settings = carb.settings.get_settings()
        if not self._out_dir or self._out_dir == "":
            out_dir = settings.get(CACHE_PATH_SETTINGS_KEY)
        else:
            out_dir = self._out_dir

        if out_dir is None:
            out_dir = ""

        if self._local_farm:
            farm_uri = "http://localhost:8222"
        else:
            settings = carb.settings.get_settings()
            farm_uri = settings.get(FARM_URI_SETTINGS_KEY)

        # start service task
        task_function_args = {
            "event_name": "request_potree_cache",
            "event_data": {
                "path": self._path,
                "kwargs": {
                    "ConvertToPotreeCommand": {
                        "out_dir": out_dir,
                        "neural_vdb": self._neural_vdb,
                    },
                    "VdbPotreeCommand": {
                        "neural_vdb": self._neural_vdb,
                        "worker_count": self._farm_worker_count,
                    },
                },
            },
        }

        file_name = os.path.basename(self._path)

        result = submit_task(
            farm_uri,
            "potree-cache-request",  # if self._neural_vdb else "potree-cache-request-nvdb",
            "command_runner.handle_programmatic_event",
            task_function_args,
            file_name,
            "runs pointcloud to potree conversion",
            lambda: create_point_cloud_prim(self._path, self._render_mode),
        )
        return result

    def undo(self):
        pass


omni.kit.commands.register_all_commands_in_module(__name__)
