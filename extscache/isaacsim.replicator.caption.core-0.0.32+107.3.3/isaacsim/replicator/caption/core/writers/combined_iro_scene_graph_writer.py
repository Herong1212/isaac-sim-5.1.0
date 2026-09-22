"""
This writer only works for IsaacSim.replicator.object. The writer class is inherited from the WorkerWriter class in the replicator core.
"""

import logging

from omni.replicator.core import AnnotatorRegistry, BackendDispatch
from omni.replicator.core.scripts import functional as F
from omni.replicator.core import WriterRegistry
from isaacsim.replicator.object.mutables.camera import Camera_DEV
from isaacsim.replicator.object.utility.misc import tentative_retrieve, P

from .iro_scene_graph_writer import IROSceneGraphWriter

class CombinedIROSceneGraphWriter(IROSceneGraphWriter):
    """
    Combines the functionalities of IROSceneGraphWriter with the default SimpleWriter of IsaacSim.replicator.object.

    attributes:
        caption_configs (dict): The configurations for object caption generation.
        scene (Scene): The scene object.
        annotators (list): The list of annotators to use for writing the scene.
        oro_metadata (dict): The metadata for the current frame.
        oro_index (int): The index of the current frame.
        global_metadata (dict): The global metadata for the scene.
        is_multi_camera (bool): Whether the scene has multiple cameras.
        camera_name_to_rp_name (dict): The mapping of camera names to replicator product names.
    """

    def __init__(self, caption_configs, scene):
        self._backend = BackendDispatch({"paths": {"out_dir": ""}})
        self.caption_configs = caption_configs
        self.scene = scene
        self.annotators = [
            AnnotatorRegistry.get_annotator("rgb"),
            AnnotatorRegistry.get_annotator(
                "bounding_box_2d_tight_fast",
            ),
            AnnotatorRegistry.get_annotator(
                "bounding_box_3d_fast",
            ),
            AnnotatorRegistry.get_annotator("camera_params"),
        ]

        if self.scene.output_switches["depth"] or self.caption_configs["export_depth"]:
            self.annotators.append(AnnotatorRegistry.get_annotator("distance_to_image_plane"))

            # shut down depth save in caption to avoid redundancy
            if self.scene.output_switches["depth"]:
                self.caption_configs["export_depth"] = False
        if self.scene.output_switches["normal"]:
            self.annotators.append(AnnotatorRegistry.get_annotator("SmoothNormal"))
        if self.scene.output_switches["segmentation"]:
            self.annotators.append(
                AnnotatorRegistry.get_annotator("semantic_segmentation", init_params={"colorize": True})
            )
        if self.scene.output_switches["instance_id_segmentation"]:
            self.annotators.append(
                AnnotatorRegistry.get_annotator("instance_id_segmentation", init_params={"colorize": True})
            )

        if self.caption_configs["export_point_cloud"]:
            self.annotators.append(AnnotatorRegistry.get_annotator("pointcloud"))

        self.oro_metadata = None
        self.oro_index = None

        self._frame_id = 0
        self.global_metadata = {}
        self.is_multi_camera = False
        self.camera_name_to_rp_name = None

    def write(self, data):
        self.oro_metadata = self.global_metadata.pop(self._frame_id)
        self.oro_index = self._frame_id

        # in multi-camera case, match rp names with camera names
        if self.is_multi_camera and self.camera_name_to_rp_name is None:
            self.camera_name_to_rp_name = {}
            for key in data:
                if key.startswith("rp_Replicator"):
                    rp_name = key[3:]
                    replicator_camera_path = data[key]["camera"]
                    camera_name = replicator_camera_path[
                        len("/Replicator/Camera_") : replicator_camera_path.find("_Xform/Camera_")
                    ]
                    self.camera_name_to_rp_name[camera_name] = rp_name

        with P(f"write {self.oro_index}"):
            bboxes_3d = None
            at_least_one_visible_tracked_mutable = False
            occlusion_threshold = tentative_retrieve("occlusion_threshold", self.oro_metadata, float, 1)
            max_area_threshold = tentative_retrieve("max_area_threshold", self.oro_metadata, float, None)
            min_area_threshold = tentative_retrieve("min_area_threshold", self.oro_metadata, float, None)
            for mutable in self.scene.mutables.values():
                if isinstance(mutable, Camera_DEV):
                    if self.is_multi_camera:
                        mutable.rp_name = self.camera_name_to_rp_name[mutable.name]

                    pixel_max_area_threshold, pixel_min_area_threshold = mutable.calculate_pixel_thresholds(
                        max_area_threshold, min_area_threshold
                    )

                    output_name = tentative_retrieve(
                        "output_name", self.oro_metadata, str, f'{self.oro_metadata["seed"]}_{mutable.name}'
                    )
                    output_name = output_name.replace("$(camera_name)", mutable.name).replace(
                        "$(camera_index)", str(mutable.ref_index)
                    )

                    continue_flag, bboxes_3d = self.mutable_save(
                        mutable,
                        data,
                        output_name,
                        occlusion_threshold,
                        pixel_max_area_threshold,
                        pixel_min_area_threshold,
                        bboxes_3d,
                    )
                    if continue_flag:
                        continue
                    at_least_one_visible_tracked_mutable = True

                    # caption generation
                    image = self.save_caption_results(mutable, data, output_name)

                    if self.scene.output_switches["images"]:
                        output_path = f"{self.scene.output_path}/images/{output_name}.jpg"
                        message = f"[METROPERF]: frame saved at {output_path}, [{self.oro_index + 1}/{self.scene.num_frames}]"
                        logging.info(message)
                        print(message)
                        self._backend.write_image(f"{output_path}", image)

                    if self.scene.progress_bar is not None:
                        self.scene.progress_bar.model.set_value((self.oro_index + 1) / self.scene.num_frames)

            # if nothing is tracked, don't write  xxx
            if tentative_retrieve("skip_frames_with_no_visible_tracked_mutables", self.oro_metadata, bool, False):
                if not at_least_one_visible_tracked_mutable:
                    self._frame_id += 1
                    return

            self.save_global_results()
        self._frame_id += 1

print("[INFO] Register CombinedIROSceneGraphWriter to the WriterRegistry")
# registry
WriterRegistry.register(CombinedIROSceneGraphWriter)
