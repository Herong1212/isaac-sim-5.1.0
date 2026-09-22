import os
import asyncio
import copy
import logging
import time
import random
from typing import Dict, Tuple

import numpy as np
from PIL import Image
from pxr import UsdPhysics, PhysxSchema, Gf

import omni.physx
import omni.replicator.core as rep

from .camera import Camera_DEV, rgba_to_int
from .geometry import GBasic, GBottle, GMesh
from .light import Light_DEV
from ..constants import VERSION
from ..simple_writer import WorkerWriter  # noqa: WorkerWriter used by WriterRegistry
from ..utility.scene import (
    apply_settings,
    get_stage,
    new_stage_async,
    wait_frames,
    timeline_play,
    timeline_stop,
    observe_event,
)
from ..utility.metadata import (
    save_2dlabels_coco,
)
from ..utility.misc import (
    CHECK,
    ensure_folder,
    ensure_folder_recursive,
    ensured_retrieve,
    error,
    P,
    tentative_retrieve,
    to_array,
    write_yaml,
)
from ..utility.xform import get_total_xform

MAX_ASSET_LOADING_FRAMES = 10


def simulate_physics(elapsed_time: float, specified_num_simulation_frames: int = None, physics_dt: float = 1 / 30):
    physx_sim_interface = omni.physx.get_physx_simulation_interface()
    if specified_num_simulation_frames is None:
        num_steps = int(elapsed_time / physics_dt)
    else:
        num_steps = specified_num_simulation_frames
    for _ in range(num_steps):
        physx_sim_interface.simulate(physics_dt, 0)
        physx_sim_interface.fetch_results()


class Scene_DEV:  # noqa
    default_output_switches = {
        "images": True,
        "labels": True,
        "descriptions": True,
        "3d_labels": True,
        "segmentation": True,
        "depth": True,
        "normal": True,
        "instance_id_segmentation": True,
        "usd": False,
        "caption": False,
        "florance2": False,
        "object_caption": False,
        "caption_like": True,
    }

    def __init__(self, binary_obj_det=None, progress_bar=None):
        self.coco_2dlabels = {}
        self.binary_obj_det = binary_obj_det
        self.progress_bar = progress_bar
        self.num_frames = 1
        self._is_loading = True

    # copied from omni.replicator.core
    def on_stage_event(self, e):
        stage_event = omni.usd.StageEventType(e.type)
        if stage_event == omni.usd.StageEventType.ASSETS_LOADING:
            self._is_loading = True
        elif stage_event in [
            omni.usd.StageEventType.ASSETS_LOADED,
            omni.usd.StageEventType.ASSETS_LOAD_ABORTED,
            omni.usd.StageEventType.CLOSED,
        ]:
            self._is_loading = False

    async def initialize_embedded(self, metadata):
        await self.initialize_scene(metadata, False)
        self.create_mutables(metadata, True)

    async def initialize(self, metadata):
        await self.initialize_scene(metadata)
        self.create_folders(metadata)
        self.create_mutables(metadata)

        # from omni.replicator.core
        self._loading_event_sub = observe_event(
            omni.usd.get_context().stage_event_name(omni.usd.StageEventType.ASSETS_LOADING),
            lambda e: setattr(self, '_is_loading', True),
            observer_name="isaacsim.replicator.object"
        )
        self._loaded_event_sub = observe_event(
            omni.usd.get_context().stage_event_name(omni.usd.StageEventType.ASSETS_LOADED),
            lambda e: setattr(self, '_is_loading', False),
            observer_name="isaacsim.replicator.object"
        )
        self._loaded_aborted_event_sub = observe_event(
            omni.usd.get_context().stage_event_name(omni.usd.StageEventType.ASSETS_LOAD_ABORTED),
            lambda e: setattr(self, '_is_loading', False),
            observer_name="isaacsim.replicator.object"
        )
        self._closed_event_sub = observe_event(
            omni.usd.get_context().stage_event_name(omni.usd.StageEventType.CLOSED),
            lambda e: setattr(self, '_is_loading', False),
            observer_name="isaacsim.replicator.object"
        )

        if self.output_switches["object_caption"]:  # suppress other outputs
            default_caption_configs = {"model_name": "gpt-4o"}  # reserve for additional parameters
            read_obj_caption_configs = tentative_retrieve(
                "obj_caption_configs", metadata, dict, default_caption_configs
            )
            default_caption_configs.update(read_obj_caption_configs)
            obj_caption_configs = default_caption_configs
            writer = rep.WriterRegistry.get("IRObjectCaptionWriter")  # The only writer for object caption
            render_products = []
            for mutable in self.mutables.values():
                if isinstance(mutable, Camera_DEV):
                    render_products.append(mutable.replicator_annotators["rp"])

            writer.initialize(obj_caption_configs=obj_caption_configs, scene=self)
            if len(render_products) > 1:
                writer.is_multi_camera = True
            writer.attach(render_products, trigger=None)
            self.writer = writer

        elif self.output_switches["caption"]:
            default_caption_configs = {
                # output parameters
                "save_full_scene_graph": True,
                "save_pruned_scene_graph": True,
                "export_world": True,
                "export_point_cloud": False,
                "export_depth": False,
                # scene graph parameters
                "export_edges": True,
                "pruning_ratio": 1.0,
                "global_caption": True,
                "qa_caption": True,
                "brief_caption": True,
                "visualize_caption": True,
                "max_object_capacity": 100,
                "attach_label_to_usd": False,
                "use_ai_label": False,
                "verbose": True,
                "random_seed": 0,
                "caption_only": True,
                # writer options
                "caption_writer": "IROSceneGraphWriter",
            }
            read_caption_configs = tentative_retrieve("caption_configs", metadata, dict, default_caption_configs)
            default_caption_configs.update(read_caption_configs)
            caption_configs = default_caption_configs
            writer = rep.WriterRegistry.get(caption_configs["caption_writer"])

            # TODO: merge code with CUSTOM_WRITER
            render_products = []
            for mutable in self.mutables.values():
                if isinstance(mutable, Camera_DEV):
                    render_products.append(mutable.replicator_annotators["rp"])

            writer.initialize(caption_configs=caption_configs, scene=self)
            if len(render_products) > 1:
                writer.is_multi_camera = True
            writer.attach(render_products, trigger=None)
            self.writer = writer

        else:
            if WorkerWriter in rep.WriterRegistry._writers:
                rep.WriterRegistry.unregister(WorkerWriter)
            rep.WriterRegistry.register(WorkerWriter)
            writer = rep.WriterRegistry.get("WorkerWriter")

            render_products = []
            for mutable in self.mutables.values():
                if isinstance(mutable, Camera_DEV):
                    render_products.append(mutable.replicator_annotators["rp"])

            if len(render_products) > 0:
                writer.initialize()
                writer.attach(render_products, trigger=None)
                writer.scene = self
                if len(render_products) > 1:
                    writer.is_multi_camera = True
                self.writer = writer
            else:
                self.writer = None

    async def initialize_scene(self, metadata, new_stage=True):
        with CHECK("init usdrt stage"):
            while not omni.kit.app.get_app().is_app_ready() or not omni.usd.get_context().get_stage():
                await wait_frames()
            settings = {
                "/app/renderer/resolution/width": ensured_retrieve("screen_width", metadata, int),
                "/app/renderer/resolution/height": ensured_retrieve("screen_height", metadata, int),
                "/persistent/app/stage/upAxis": "Y",
                "/persistent/simulation/defaultMetersPerUnit": 0.01,
                "/omni/replicator/captureOnPlay": False,
                "/persistent/app/primCreation/DefaultXformOpType": "Scale, Rotate, Translate",
                "/app/viewport/grid/enabled": False,
                "/app/viewport/show/camera": False,
                "/app/viewport/show/light": False,
                "/persistent/app/viewport/displayOptions": 0,  # remove light icon
            }
            apply_settings(settings)
            # await wait_seconds(2) see if we can remove this without texture error
            if new_stage:
                await new_stage_async()  # 1s
            if tentative_retrieve("path_tracing", metadata, bool, False):
                total_spp = tentative_retrieve("total_spp", metadata, int, 64)
                settings = {
                    "/rtx/rendermode": "PathTracing",
                    "/rtx/pathtracing/totalSpp": total_spp,
                    "/rtx/pathtracing/spp": total_spp,
                    "/rtx/pathtracing/clampSpp": 0,
                }
                apply_settings(settings)

            scene = UsdPhysics.Scene.Define(get_stage(), "/World/physicsScene")
            gravity_direction = tentative_retrieve("gravity_direction", metadata, list, [0, -1, 0])
            scene.CreateGravityDirectionAttr().Set(Gf.Vec3f(tuple(gravity_direction)))
            gravity = tentative_retrieve("gravity", metadata, (int, float), 0)
            scene.CreateGravityMagnitudeAttr().Set(gravity)

            physx_scene_api = PhysxSchema.PhysxSceneAPI.Apply(scene.GetPrim())
            physx_scene_api.CreateGpuCollisionStackSizeAttr().Set(1e9)
            await wait_frames()

            settings = {
                "/app/viewport/show/camera": False,
                "/app/viewport/show/light": False,
                "/persistent/app/viewport/displayOptions": 0,  # remove light icon
            }
            apply_settings(settings)

            rep.orchestrator.set_capture_on_play(False)
            with rep.trigger.on_frame():
                pass

    # TODO in progress, performance boost on inter frame rendering
    def turn_off_render_products(self):
        for mutable in self.mutables.values():
            if isinstance(mutable, Camera_DEV):
                mutable.replicator_annotators["rp"].hydra_texture.set_updates_enabled(False)

    def turn_on_render_products(self):
        for mutable in self.mutables.values():
            if isinstance(mutable, Camera_DEV):
                mutable.replicator_annotators["rp"].hydra_texture.set_updates_enabled(True)

    async def step_embedded(self, metadata, index, seed):
        self.seed = seed
        random.seed(self.seed)
        for key, mutable in self.mutables.items():
            mutable.step(metadata[key])

    # TODO in progress, performance boost on custom writer
    async def step(self, metadata, index, seed):
        with CHECK(f"process frame {index}"):
            await wait_frames()  # for the isaac-kit mismatching
            with P("step before write"):
                self.seed = seed
                random.seed(self.seed)

                # record global transforms used to be here
                for key, mutable in self.mutables.items():
                    mutable.step(metadata[key])

                inter_frame_time = tentative_retrieve("inter_frame_time", metadata, (int, float), 0)
                if inter_frame_time < 0:
                    error("inter_frame_time should be non-negative")
                simulation_time = tentative_retrieve(
                    "simulation_time", metadata, (int, float), None
                )  # overriding legacy value
                if simulation_time is not None:
                    if simulation_time < 0:
                        error("simulation_time should be non-negative")
                    inter_frame_time = simulation_time

                number_of_simulation_frames = tentative_retrieve("number_of_simulation_frames", metadata, int, None)
                simulation_seconds_per_frame = tentative_retrieve(
                    "simulation_seconds_per_frame", metadata, (int, float), 1 / 30
                )

                if tentative_retrieve("enable_physics", metadata, bool, True):
                    simulate_physics(inter_frame_time, number_of_simulation_frames, simulation_seconds_per_frame)  # xxx
                await wait_frames()

                extra_rendering_time = tentative_retrieve("extra_rendering_time", metadata, (int, float), 0)
                if extra_rendering_time < 0:
                    error("extra_rendering_time should be non-negative")
                number_of_extra_rendering_frames = tentative_retrieve(
                    "number_of_extra_rendering_frames", metadata, int, None
                )
                if number_of_extra_rendering_frames is not None:
                    if number_of_extra_rendering_frames < 0:
                        error("number_of_extra_rendering_frames should be non-negative")
                    await wait_frames(number_of_extra_rendering_frames)
                else:
                    extra_rendering_start = time.time()
                    while time.time() - extra_rendering_start < extra_rendering_time:
                        await wait_frames()

                asset_loading_cnt = 0
                while self._is_loading and asset_loading_cnt < MAX_ASSET_LOADING_FRAMES:
                    await asyncio.sleep(0.01)
                    await wait_frames()
                    asset_loading_cnt += 1

                # record after resolution, before step_async
                for key, mutable in self.mutables.items():
                    if mutable.prim is not None:
                        steady_transform = to_array(get_total_xform(mutable.prim))
                        metadata[key]["global_transform"] = copy.deepcopy(steady_transform)  # TODO: provide options
                        metadata[key]["transform_operators"] = [
                            {"transform": copy.deepcopy(steady_transform)}
                        ]  # get before capturing
                    if "physics" in metadata[key]:
                        metadata[key].pop("physics")

                for key in metadata:
                    if isinstance(metadata[key], dict) and "count" in metadata[key]:
                        ref_count = metadata[key].pop("count")
                        metadata[key]["ref_count"] = ref_count  # to avoid multiple spawning during scene restoration

                # detect 3d space - may mess with scene, remove created recorder
                for detector in self.detectors.values():
                    detector.initialize(metadata)  # detect, and pass info to output description
                await wait_frames()
                for detector in self.detectors.values():
                    detector.detect()
                await wait_frames()

                metadata["num_frames"] = 1
                metadata["inter_frame_time"] = 0.01  # in the restored scene, there's no physics needed

                if self.writer is not None:
                    self.writer.global_metadata[index] = metadata
                    self.writer.schedule_write()
                else:
                    if self.output_switches["descriptions"]:
                        metadata_with_header = {
                            "isaacsim.replicator.object": {
                                "version": VERSION,
                            }
                        }
                        metadata_with_header["isaacsim.replicator.object"].update(metadata)
                        output_name_global = tentative_retrieve("output_name", metadata, str, f'{metadata["seed"]}')
                        metadata_with_header["isaacsim.replicator.object"][
                            "output_path"
                        ] += "__NEXT"  # convenience for restoration
                        write_yaml(metadata_with_header, f"{self.output_path}/descriptions/{output_name_global}.yaml")


    def create_folders(self, metadata):
        self.output_switches = copy.deepcopy(Scene_DEV.default_output_switches)
        output_switches = tentative_retrieve("output_switches", metadata, dict)

        if output_switches is not None:
            for key in output_switches:
                if key not in self.output_switches:
                    error(f"unrecognized output switch: {key}")
                self.output_switches[key] = ensured_retrieve(key, output_switches, bool)

        self.output_path = str(os.path.abspath(ensured_retrieve("output_path", metadata, str)))

        dependent_switches = [
            "labels",
            "3d_labels",
            "segmentation",
            "instance_id_segmentation",
            "depth",
            "normal",
            "caption",
            "object_caption",
            "caption_like",
        ]
        if any(self.output_switches[_] for _ in dependent_switches):
            if not self.output_switches["images"]:
                logging.info(
                    "[METROPERF]: When label, 3d_labels, segmentation, instance_id_segmentation, depth, normal, "
                    "caption, object_caption is turned on, switching on images so that images are saved."
                )
                self.output_switches["images"] = True

        if self.output_switches["object_caption"]:
            # shut down all other switches and turn on the image switch
            for switch in dependent_switches:
                self.output_switches[switch] = False
            self.output_switches["object_caption"] = True
            self.output_switches["images"] = True
            self.output_switches["descriptions"] = True

            logging.info(
                "[METROPERF]: When object_caption is turned on, all other switches are turned off and images are saved."
            )

        if self.output_switches["florance2"]:
            self.output_switches["labels"] = True
            self.output_switches["segmentation"] = True
            self.output_switches["images"] = True

        with CHECK("create folders"):
            ensure_folder_recursive(self.output_path)
            for key, value in self.output_switches.items():
                if value:
                    ensure_folder(f"{self.output_path}/{key}")

    def create_mutables(self, metadata, is_embedded=False):
        self.physics_global = {
            "friction": tentative_retrieve("friction", metadata, (int, float), 1),
            "linear_damping": tentative_retrieve("linear_damping", metadata, (int, float), 0),
            "angular_damping": tentative_retrieve("angular_damping", metadata, (int, float), 0),
        }

        self.mutables = {}
        self.detectors = {}
        for key, value in metadata.items():
            if isinstance(value, dict):
                if "type" in value:
                    mutable_type = value["type"]
                    with CHECK(f"initialize {key}({mutable_type})"):
                        if mutable_type == "light":
                            self.mutables[key] = Light_DEV(key, value, self)
                        elif mutable_type == "geometry":
                            shape = ensured_retrieve("subtype", value, str)
                            if shape in ["cone", "cube", "cylinder", "disk", "torus", "plane", "sphere", "torus"]:
                                self.mutables[key] = GBasic(key, value, self)
                            elif shape == "mesh":
                                self.mutables[key] = GMesh(key, value, self)
                            elif shape == "bottle":
                                self.mutables[key] = GBottle(key, value, self)
                        elif mutable_type == "camera":
                            self.mutables[key] = Camera_DEV(key, value, self, is_embedded)
                        else:
                            error(f"unrecognized mutable type: {mutable_type}")

    async def clean_up(self, metadata):
        if self.writer is not None:
            last_frame_id = -1
            while self.writer._frame_id < self.num_frames:  # noqa: acess to protected member
                if self.writer._frame_id != last_frame_id:  # noqa
                    print(f"simulation finished, pending frame {self.writer._frame_id} write")  # noqa
                    last_frame_id = self.writer._frame_id  # noqa
                await wait_frames()
        save_2dlabels_coco(
            self.coco_2dlabels,
            metadata["output_path"],
            metadata["screen_height"],
            metadata["screen_width"],
            self.binary_obj_det,
        )
