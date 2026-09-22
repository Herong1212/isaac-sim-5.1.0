# SPDX-FileCopyrightText: Copyright (c) 2022-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import re
from ast import literal_eval
from typing import Tuple, Union

import carb
import numpy as np
import omni.client
import omni.graph.core as og
import omni.replicator.core as rep
import yaml
from omni.replicator.core.utils import ReplicatorItem, ReplicatorWrapper, create_node, set_target_prims
from pxr import Gf, UsdGeom


class Visualizer:
    def __init__(
        self,
        input_file_path: str,
        output_dir: str = None,
        root_dir: str = None,
        nucleus_server: str = None,
        mount: str = None,
        overwrite: bool = False,
    ):
        """Visualizer for omni.replicator.replicator_yaml, which visualize the model loaded from the yaml files.

        Args:
            input_file_path: File path to the yaml file.
            output_dir: Output directory to store the output data. It will overwrite the ``output_dir`` param in the yaml
                file.
            root_dir: Root directory to resolve relative path.
            num_scenes: Number of scenes to generate. It will overwrite the number of scenes in the yaml file.
            nucleus_server: Nucleus Server URL. It will overwrite 'nucleus_server` param in yaml file.
            mount: Mount directory of workspace that user defines. It will be used for resolve any */ path prefix.
            overwrite: Whether to overwrite the output directory.
        """
        self.input_file_path = input_file_path
        self.root_dir = root_dir
        self.mount = mount
        self.default_nucleus = nucleus_server

        # Set subframes for materials to load
        carb.settings.get_settings().set("/omni/replicator/RTSubframes", 3)

        # Update output_dir to full path.
        if output_dir.startswith("/") or re.match("^[a-zA-Z]:\\\\", output_dir) is not None:
            self.output_dir = output_dir  # Absolute path
        elif output_dir.startswith("*"):
            self.output_dir = os.path.join(self.mount, output_dir[2:])  # Mount Path
        else:
            self.output_dir = os.path.join(self.root_dir, output_dir)  # Relative path

        asset_paths_dict = self.parse_assets_path(input_file_path)

        asset_paths_list = []

        for asset_paths_set in asset_paths_dict.values():
            asset_paths_list.extend(list(asset_paths_set))

        # Initialize writer
        self.writer = rep.WriterRegistry.get("VisualizerWriter")
        self.writer.initialize(output_dir=self.output_dir, asset_paths=asset_paths_list)

        self.construct_scene(asset_paths_list)

    def parse_assets_path(self, input_file_path):
        """Parse the yaml file and load the path for all assets that the yaml file contains.

        Args:
            input_file_path: File path to the yaml file.
        """

        # Determine parameter file path
        if input_file_path.startswith("/") or re.match("^[a-zA-Z]:\\\\", input_file_path) is not None:
            input_file_path = input_file_path
        elif input_file_path.startswith("*"):
            input_file_path = os.path.join(self.mount, input_file_path[2:])
        else:
            input_file_path = os.path.join(self.root_dir, input_file_path)

        with open(input_file_path, "r") as f:
            params = yaml.safe_load(f)

        # Set Nucleus server and check connection
        if "nucleus_server" not in params:
            params["nucleus_server"] = "localhost"
        # self.default_nucleus always overwrites yaml's nucleus server
        if self.default_nucleus:
            params["nucleus_server"] = self.default_nucleus

        if "://" not in params["nucleus_server"]:
            params["nucleus_server"] = "omniverse://" + params["nucleus_server"]

        self.nucleus_server = params["nucleus_server"]

        (result, _) = omni.client.stat(self.nucleus_server)

        if not result.name.startswith("OK"):
            carb.log_error(
                f"[omni.replicator.replicator_yaml] Could not connect to the Nucleus server: {self.nucleus_server}. Only local data will be fetched."
            )
            self.nucleus_server = None

        # Parse all profile asset paths
        profile_asset_paths = [self.parse_assets_path(profile) for profile in params.get("profiles", [])[::-1]]

        # Dict that maps group name (str) to set
        asset_paths = {}
        # Extract group
        for key, val in list(params.items()):
            if isinstance(val, dict):
                if "obj_model" not in val and "inherit" not in val:
                    continue

                if key not in asset_paths:
                    asset_paths[key] = set()

                if "obj_model" in val:
                    # Extract the path
                    path = val["obj_model"]

                    parsed_item_list = []
                    if path.startswith("Choice") or path.startswith("Sequence") or path.startswith("Walk"):
                        param_type = path.split("(")[0]
                        item_list = literal_eval(path[len(param_type) + 1 : -1])

                        # parse txt files and usd paths
                        for item in item_list:
                            if not isinstance(item, str):
                                raise ValueError(
                                    f"The value inside a item list for {key} must be a str, but got {type(item)}."
                                )
                            if item.endswith(".txt"):
                                parsed_item_list.extend(self.parse_text_file(item))
                            else:
                                parsed_item_list.append(item)
                    else:
                        parsed_item_list.append(path)

                    asset_paths[key].update(self._verify_paths(key, parsed_item_list))

                if "inherit" in val:
                    for profile_asset_path in profile_asset_paths:
                        if val["inherit"] in profile_asset_path:
                            asset_paths[key].update(profile_asset_path[val["inherit"]])

        return asset_paths

    def _verify_paths(self, key, paths):
        verified_paths = []
        for path in paths:
            if self.nucleus_server is not None:
                file_path_nucleus = self.nucleus_server + path
                (exists_result, _, _) = omni.client.read_file(file_path_nucleus)
                is_file_nucleus = exists_result.name.startswith("OK")

                (directory_result, entries) = omni.client.list(file_path_nucleus)
                is_dir_nucleus = directory_result.name.startswith("OK")

                if is_dir_nucleus:
                    for entry in entries:
                        if entry.relative_path.lower().endswith((".usd", ".usdz", ".usda", ".usdc")):
                            verified_paths.append(file_path_nucleus + "/" + entry.relative_path)
            else:
                is_file_nucleus = False
                is_dir_nucleus = False

            # TODO: Add a cache for it.
            is_file_local = False
            # Verify if the file exits locally
            if not (is_file_nucleus or is_dir_nucleus):
                if path.startswith("/") or re.match("^[a-zA-Z]:\\\\", path) is not None:
                    file_path_local = path
                elif path.startswith("*"):
                    file_path_local = os.path.join(self.mount, path[2:])
                else:
                    file_path_local = os.path.join(os.path.dirname(__file__), path)
                is_file_local = os.path.isfile(file_path_local)
                is_dir_local = os.path.isdir(file_path_local)

                if is_dir_local:
                    for file_name in os.listdir(file_path_local):
                        if file_name.lower().endswith((".usd", ".usdz", ".usda", ".usdc")):
                            verified_paths.append(os.path.join(file_path_local), file_name)

            # Update params with full nucleus or local path if we can find it.
            if is_file_nucleus:
                if file_path_nucleus and (not file_path_nucleus.endswith((".usd", ".usdz", ".usda", ".usdc"))):
                    raise ValueError(f"Parameter {key} has path {file_path_nucleus} with incorrect file type.")
                else:
                    verified_paths.append(file_path_nucleus)
            elif is_file_local:
                if file_path_local and (not file_path_local.endswith((".usd", ".usdz", ".usda", ".usdc"))):
                    raise ValueError(f"Parameter {key} has path {path} with incorrect file type.")
                else:
                    verified_paths.append(file_path_local)

            if not (is_file_nucleus or is_file_local or is_dir_nucleus):
                raise ValueError(f"Parameter {key} has path {path} not found on {self.nucleus_server} or locally.")

        return verified_paths

    def parse_text_file(self, txt_file_path):
        """Parse text file that contains a list of usd paths.

        Return:
            (list of str): list of usd paths.
        """
        if txt_file_path.startswith("/") or re.match("^[a-zA-Z]:\\\\", txt_file_path) is not None:
            input_file = txt_file_path
        elif txt_file_path.startswith("*"):
            input_file = os.path.join(self.mount, txt_file_path[2:])
        else:
            input_file = os.path.join(self.root_dir, txt_file_path)

        usd_paths = []
        with open(input_file, "r") as f:
            lines = f.readlines()

            for line in lines:
                # Get rid of new line character.
                usd_paths.append(line.strip())

        return usd_paths

    def construct_scene(self, asset_paths):
        """Construct the scene to visualize each loaded assets.

        Args:
            asset_paths (list): List of paths that points to the asset.

        """

        if len(asset_paths) == 0:
            carb.log_warn("The asset path is empty.")
            return

        # Create dome light
        light = rep.create.light(
            light_type="dome",
            texture=os.path.join(
                os.path.dirname(os.path.realpath(__file__)), "data/assets/textures/visualizer_texture.png"
            ),
            intensity=500,
        )
        num_asset = len(asset_paths)

        # Repeat each item in the asset four times
        repeated_asset_paths = []
        for asset_path in asset_paths:
            repeated_asset_paths.extend([asset_path] * 4)

        # Frame is 4 perspective per asset
        num_frames = num_asset * 4

        # create camera to look at the asset.
        camera = rep.create.camera(position=(0, 50, 0))
        render_product = rep.create.render_product(camera, resolution=(512, 512))

        # Attach writer to render product
        self.writer.attach([render_product])

        # Axes that the camera is aligned with.
        camera_axes = [[1, 1, 1.3], [-1, 1, 1.3], [1, 1, -1.3], [-1, 1, -1.3]]

        sequenced_asset_paths = rep.distribution.sequence(repeated_asset_paths)

        with rep.trigger.on_frame(max_execs=num_frames):
            instance = rep.randomizer.instantiate(paths=sequenced_asset_paths, size=1)

            with instance:
                rep.modify.pose(scale=10)

            camera_positions = calculate_camera_positions(
                focus_prim_path=instance, axes_to_move=rep.distribution.sequence(camera_axes), scale=3
            )

            with camera:
                rep.modify.pose(position=camera_positions, look_at=instance)


@ReplicatorWrapper
def calculate_camera_positions(
    focus_prim_path: Union[ReplicatorItem, str],
    axes_to_move: Union[Tuple[float, float, float], ReplicatorItem],
    scale: Union[float, int, ReplicatorItem] = 1.2,
):
    node = create_node("omni.replicator.replicator_yaml.OgnCameraPositionLookAtPrim")

    if isinstance(axes_to_move, (list, tuple)):
        og.AttributeValueHelper(node.get_attribute("inputs:axes")).set(axes_to_move, update_usd=True)
    else:
        rep.utils._setup_random_attribute(
            node, prim_path=focus_prim_path, attribute_value=axes_to_move, input_name="axes"
        )

    if isinstance(scale, (float, int)):
        og.AttributeValueHelper(node.get_attribute("inputs:scale")).set(scale, update_usd=True)
    else:
        rep.utils._setup_random_attribute(node, prim_path=focus_prim_path, attribute_value=scale, input_name="scale")

    set_target_prims(node, "inputs:targetPrim", focus_prim_path)

    if isinstance(focus_prim_path, ReplicatorItem):
        rep.utils.auto_connect(focus_prim_path.node, node)

    return node
