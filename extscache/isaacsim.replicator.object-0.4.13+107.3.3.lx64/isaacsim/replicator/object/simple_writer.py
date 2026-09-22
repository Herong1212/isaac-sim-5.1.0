import copy
import logging
import json

import numpy as np
from PIL import Image

import omni.usd
import omni.kit
import omni.replicator.core as rep
from omni.replicator.core import Writer, AnnotatorRegistry, BackendDispatch
from .constants import SEMANTIC_CLASS_STRING, VERSION
from .mutables.camera import Camera_DEV, rgba_to_int, serialize_bbox
from .utility.metadata import save_bbox_2d_to_kitti, save_to_3d_labels, save_to_caption_like, florance2_like_captions
from .utility.misc import (
    resolve_mutable_name,
    tentative_retrieve,
    write_yaml,
    P,
)


class WorkerWriter(Writer):
    def __init__(self):
        self._backend = BackendDispatch({"paths": {"out_dir": ""}})
        self.annotators = [
            AnnotatorRegistry.get_annotator("rgb"),
            AnnotatorRegistry.get_annotator(
                "bounding_box_2d_tight_fast"  # , init_params={"semanticTypes": [SEMANTIC_CLASS_STRING]}
            ),
            AnnotatorRegistry.get_annotator(
                "bounding_box_3d_fast"  # , init_params={"semanticTypes": [SEMANTIC_CLASS_STRING]}
            ),
            AnnotatorRegistry.get_annotator("semantic_segmentation", init_params={"colorize": True}),
            AnnotatorRegistry.get_annotator("instance_id_segmentation", init_params={"colorize": True}),
            AnnotatorRegistry.get_annotator("distance_to_image_plane"),
            AnnotatorRegistry.get_annotator("SmoothNormal"),
        ]

        self.scene = None
        self.oro_metadata = None
        self.oro_index = None
        self._frame_id = 0
        self.global_metadata = {}
        self.is_multi_camera = False
        self.camera_name_to_rp_name = None

    def write_inner(
        self,
        image,
        segmentation,
        instance_id_segmentation,
        depth,
        normal,
        visible_labeled_set,
        filtered_bboxes_2d,
        output_name,
    ):
        def is_label_visible(label, visible_labeled_set):
            for str in visible_labeled_set.values():
                if label == str.split("||")[1]:
                    return True
            return False

        if self.scene.output_switches["depth"]:
            with open(f"{self.scene.output_path}/depth/{output_name}.npy", "wb") as f:
                np.save(f, depth)

        if self.scene.output_switches["normal"]:
            with open(f"{self.scene.output_path}/normal/{output_name}.npy", "wb") as f:
                np.save(f, normal)

        if self.scene.output_switches["segmentation"]:
            color_map = segmentation[0]
            updated_color_list = copy.deepcopy(segmentation[1])
            for key, value in segmentation[1].items():
                if not is_label_visible(value, visible_labeled_set):
                    updated_color_list.pop(key)
                    color_int = rgba_to_int(eval(key))
                    color_map[color_map == color_int] = 0

            segmentation_image = Image.fromarray(segmentation[0], "RGBA").convert("RGB")
            segmentation_image.save(f"{self.scene.output_path}/segmentation/{output_name}.png")
            write_yaml(updated_color_list, f"{self.scene.output_path}/segmentation/{output_name}.yaml")

        if self.scene.output_switches["instance_id_segmentation"]:
            instance_id_segmentation[0].save(f"{self.scene.output_path}/instance_id_segmentation/{output_name}.png")
            write_yaml(
                instance_id_segmentation[1],
                f"{self.scene.output_path}/instance_id_segmentation/{output_name}.yaml",
            )

        if self.scene.output_switches["florance2"]:
            florance_like_labels = florance2_like_captions(
                filtered_bboxes_2d, segmentation_image, image, updated_color_list
            )

            with open(f"{self.scene.output_path}/florance2/{output_name}.json", "w") as f:
                for fl_label in florance_like_labels:
                    # print(fl_label)
                    # some labels are empty from ORO output
                    if fl_label["suffix"] != "":
                        json_line = {
                            "image": f"{output_name}.jpg",
                            "prefix": fl_label["prefix"],
                            "suffix": fl_label["suffix"],
                        }
                        f.write(json.dumps(json_line) + "\n")
                # f.write(lbl_txt)

    def mutable_save(
        self,
        mutable,
        data,
        output_name,
        occlusion_threshold,
        pixel_max_area_threshold,
        pixel_min_area_threshold,
        bboxes_3d=None,
    ):
        image, bboxes_2d, segmentation, instance_id_segmentation, depth, normal = mutable.capture(
            self.scene.output_switches, data
        )

        # calculate bbox2d first to filter occlusion
        bboxes_2d = (
            serialize_bbox(data[mutable.resolve_annotator_key("bounding_box_2d_tight_fast")], False)
            if self.scene.output_switches["labels"]
            else None
        )

        if len(bboxes_2d) == 0 and tentative_retrieve(
            "skip_frames_with_no_visible_tracked_mutables", self.oro_metadata, bool, False
        ):
            return True, bboxes_3d

        self.oro_metadata[mutable.name]["bounding_boxes_2d"] = {hash(k): v for k, v in bboxes_2d.items()}
        visible_labeled_set = set()
        if self.scene.output_switches["labels"]:
            # output
            visible_labeled_set = save_bbox_2d_to_kitti(
                bboxes_2d,
                f"{self.scene.output_path}/labels/{output_name}.txt",
                occlusion_threshold,
                pixel_max_area_threshold,
                pixel_min_area_threshold,
            )
            filtered_bboxes_2d = {name: bboxes_2d[name] for name in visible_labeled_set}
            if self.scene.coco_2dlabels is not None:
                self.scene.coco_2dlabels[output_name] = filtered_bboxes_2d

        if self.scene.output_switches["3d_labels"]:
            if not bboxes_3d:  # one for all
                bboxes_3d = mutable.capture_global_space(self.scene.output_switches, data)
                for name, box in bboxes_3d.items():
                    if SEMANTIC_CLASS_STRING in box["labels"]:
                        mutable_name = box["labels"][SEMANTIC_CLASS_STRING]
                        self.oro_metadata[resolve_mutable_name(mutable_name, False)]["bounding_box_3d"] = box
                    else:
                        self.oro_metadata[f"unnamed_{hash(name)}"] = {}
                        self.oro_metadata[f"unnamed_{hash(name)}"]["bounding_box_3d"] = box

            # output
            save_to_3d_labels(
                self.oro_metadata[mutable.name],
                bboxes_3d,
                f"{self.scene.output_path}/3d_labels/{output_name}.json",
                visible_labeled_set,
            )

        if self.scene.output_switches["caption_like"]:
            save_to_caption_like(
                self.oro_metadata[mutable.name],
                bboxes_2d,
                bboxes_3d,
                f"{self.scene.output_path}/caption_like/{output_name}.json",
                visible_labeled_set,
            )

        # segmentation mask filter based on occlusion; output, can be queued
        self._backend.schedule(
            lambda: self.write_inner(
                image,
                segmentation,
                instance_id_segmentation,
                depth,
                normal,
                visible_labeled_set,
                filtered_bboxes_2d,
                output_name,
            )
        )
        return False, bboxes_3d

    def save_global_results(self):
        output_name_global = tentative_retrieve("output_name", self.oro_metadata, str, f'{self.oro_metadata["seed"]}')
        output_name_global = output_name_global.replace("$(camera_name)", "GLOBAL").replace("$(camera_index)", "GLOBAL")
        metadata_with_header = {
            "isaacsim.replicator.object": {
                "version": VERSION,
            }
        }

        metadata_with_header["isaacsim.replicator.object"].update(self.oro_metadata)
        if self.scene.output_switches["descriptions"]:
            metadata_with_header["isaacsim.replicator.object"]["output_path"] += "__NEXT"  # convenience for restoration
            write_yaml(metadata_with_header, f"{self.scene.output_path}/descriptions/{output_name_global}.yaml")

        if self.scene.output_switches["usd"]:
            omni.usd.get_context().export_as_stage(f"{self.scene.output_path}/usd/{output_name_global}.usd")

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

                    if self.scene.output_switches["images"]:
                        output_path = f"{self.scene.output_path}/images/{output_name}.jpg"
                        message = (
                            f"[METROPERF]: frame saved at {output_path}, [{self.oro_index + 1}/{self.scene.num_frames}]"
                        )
                        logging.info(message)
                        print(message)
                        self._backend.write_image(f"{output_path}", data[mutable.resolve_annotator_key("rgb")])

                    if self.scene.progress_bar is not None:
                        self.scene.progress_bar.model.set_value((self.oro_index + 1) / self.scene.num_frames)

            # if nothing is tracked, don't write  xxx
            if tentative_retrieve("skip_frames_with_no_visible_tracked_mutables", self.oro_metadata, bool, False):
                if not at_least_one_visible_tracked_mutable:
                    self._frame_id += 1
                    return

            self.save_global_results()

        self._frame_id += 1


if WorkerWriter in rep.WriterRegistry._writers:
    rep.WriterRegistry.unregister(WorkerWriter)
rep.WriterRegistry.register(WorkerWriter)
