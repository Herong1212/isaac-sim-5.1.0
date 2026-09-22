from ast import literal_eval

import numpy as np
from PIL import Image
from pxr import UsdGeom, Usd

from omni.metropolis.utils.rotation_util import RotationUtil
import omni.replicator.core as rep
from copy import deepcopy
from .mutable import Mutable_DEV
from ..constants import SEMANTIC_CLASS_STRING
from ..utility.misc import ensured_retrieve_dict, error
from ..utility.scene import create_xform_prim, get_prim, get_stage
from ..utility.xform import get_total_xform, get_xform_op
from ..utility.metadata import labels_to_string


def get_replicator_annotators(name, camera_parameters, output_switches):
    camera = rep.create.camera(
        name=f"Camera_{name}",
        position=(0, 0, 0),
        rotation=(0, 0, 0),
        horizontal_aperture=camera_parameters["horizontal_aperture"],
        focal_length=camera_parameters["focal_length"],
        clipping_range=(camera_parameters["near_clip"], camera_parameters["far_clip"]),
    )
    replicator_param = {}

    rp = rep.create.render_product(camera, (camera_parameters["screen_width"], camera_parameters["screen_height"]))

    # to-do: solve dependency between switches
    # rp.hydra_texture.set_updates_enabled(False)

    if output_switches["caption"]:
        bbox_2d_tight = rep.AnnotatorRegistry.get_annotator("bounding_box_2d_tight_fast")
        bbox_2d_tight.attach(rp)
        replicator_param["bbox_2d_unfiltered"] = bbox_2d_tight

        bbox_3d_cap = rep.AnnotatorRegistry.get_annotator("bounding_box_3d_fast")
        bbox_3d_cap.attach(rp)
        replicator_param["bbox_3d_unfiltered"] = bbox_3d_cap

        if output_switches["labels"]:
            replicator_param["bbox_2d"] = bbox_2d_tight

        if output_switches["3d_labels"]:
            replicator_param["bbox_3d"] = bbox_3d_cap

        camera_params = rep.AnnotatorRegistry.get_annotator("CameraParams")
        camera_params.attach(rp)
        replicator_param["camera_params"] = camera_params

    else:
        # you should filter the prims or you never do it.
        # If you want to recover the full scene prims, you need to reopen the isaac sim.
        if output_switches["labels"]:
            bbox_2d_tight = rep.AnnotatorRegistry.get_annotator(
                # "bounding_box_2d_tight_fast", init_params={"semanticTypes": [SEMANTIC_CLASS_STRING]}
                "bounding_box_2d_tight_fast"
            )
            bbox_2d_tight.attach(rp)
            replicator_param["bbox_2d"] = bbox_2d_tight

        if output_switches["3d_labels"]:
            bbox_3d = rep.AnnotatorRegistry.get_annotator(
                # "bounding_box_3d_fast", init_params={"semanticTypes": [SEMANTIC_CLASS_STRING]}
                "bounding_box_3d_fast"
            )
            bbox_3d.attach(rp)
            replicator_param["bbox_3d"] = bbox_3d

    if output_switches["images"]:
        rgb = rep.AnnotatorRegistry.get_annotator("rgb")
        rgb.attach(rp)
        replicator_param["rgb"] = rgb

    if output_switches["segmentation"]:
        segmentation = rep.AnnotatorRegistry.get_annotator("semantic_segmentation", init_params={"colorize": True})
        segmentation.attach(rp)
        replicator_param["segmentation"] = segmentation

    if output_switches["instance_id_segmentation"]:
        instance_id_segmentation = rep.AnnotatorRegistry.get_annotator(
            "instance_id_segmentation", init_params={"colorize": True}
        )
        instance_id_segmentation.attach(rp)
        replicator_param["instance_id_segmentation"] = instance_id_segmentation

    if output_switches["depth"]:
        depth = rep.AnnotatorRegistry.get_annotator("distance_to_image_plane")  # was distance_to_camera
        depth.attach(rp)
        replicator_param["depth"] = depth

    if output_switches["normal"]:
        normal = rep.AnnotatorRegistry.get_annotator("SmoothNormal")
        normal.attach(rp)
        replicator_param["normal"] = normal

    replicator_param["rp"] = rp

    return replicator_param


def update_perspective_camera_with_xform(xform):
    _xlate, _xyz = RotationUtil.get_xlate_and_xyz_from_xform(xform)
    with Usd.EditContext(get_stage(), Usd.EditTarget(get_stage().GetSessionLayer())):
        camera_prim = get_prim("/OmniverseKit_Persp")
        get_xform_op(camera_prim, "translate").Set(_xlate)
        get_xform_op(camera_prim, "rotateXYZ").Set(_xyz)


def update_camera_with_proxy(camera_name, camera_proxy):
    camera_prim = get_prim(f"/Replicator/Camera_{camera_name}_Xform")
    _xform = get_total_xform(camera_proxy)
    _xlate, _xyz = RotationUtil.get_xlate_and_xyz_from_xform(_xform)
    get_xform_op(camera_prim, "translate").Set(_xlate)
    get_xform_op(camera_prim, "rotateXYZ").Set(_xyz)

    # also, update perspective view so user sees
    with Usd.EditContext(get_stage(), Usd.EditTarget(get_stage().GetSessionLayer())):
        camera_prim = get_prim("/OmniverseKit_Persp")
        get_xform_op(camera_prim, "translate").Set(_xlate)
        get_xform_op(camera_prim, "rotateXYZ").Set(_xyz)


def serialize_bbox(bbox_3d_data, is_3d):
    res = {}
    id_to_labels = bbox_3d_data["info"]["idToLabels"]
    primPaths = bbox_3d_data["info"]["primPaths"]
    for i, data in enumerate(bbox_3d_data["data"]):
        if is_3d:
            res[primPaths[i]] = {
                "x_min": float(data["x_min"]),
                "y_min": float(data["y_min"]),
                "z_min": float(data["z_min"]),
                "x_max": float(data["x_max"]),
                "y_max": float(data["y_max"]),
                "z_max": float(data["z_max"]),
                "transform": [[float(item) for item in row] for row in data["transform"]],
                "labels": deepcopy(id_to_labels[data["semanticId"]]),
                "prim_path": primPaths[i],
            }
        else:
            res[primPaths[i]] = {
                "x_min": int(data["x_min"]),
                "y_min": int(data["y_min"]),
                "x_max": int(data["x_max"]),
                "y_max": int(data["y_max"]),
                "occlusion": float(data["occlusionRatio"]),
                "labels": deepcopy(id_to_labels[data["semanticId"]]),
                "prim_path": primPaths[i],
            }
    return res


def serialize_segmentation(segmentation_data):
    id_to_labels = segmentation_data["info"]["idToLabels"]
    color_to_object = {}
    for k, v in id_to_labels.items():
        color_to_object[k] = labels_to_string(None, v)
    return segmentation_data["data"], color_to_object


def serialize_instance_id_segmentation(segmentation_data):
    return Image.fromarray(segmentation_data["data"], "RGBA").convert("RGB"), segmentation_data["info"]["idToLabels"]


def rgba_to_int(rgba):
    return (rgba[3] << 24) + (rgba[2] << 16) + (rgba[1] << 8) + rgba[0]


class Camera_DEV(Mutable_DEV):  # noqa
    def __init__(self, name, metadata, scene, is_embedded=False):
        super().__init__(name)
        self.ref_index = metadata.get("index", 0)
        self.rp_name = None
        camera_parameters = ensured_retrieve_dict(
            "camera_parameters",
            metadata,
            {
                "screen_width": int,
                "screen_height": int,
                "horizontal_aperture": (int, float),
                "focal_length": (int, float),
                "near_clip": (int, float),
                "far_clip": (int, float),
            },
        )
        self.camera_parameters = camera_parameters
        if not is_embedded:
            self.replicator_annotators = get_replicator_annotators(name, camera_parameters, scene.output_switches)
            self.prim = create_xform_prim(f"/World/CameraProxies/camera_proxy_{name}")
        else:
            self.prim = UsdGeom.Camera.Define(get_stage(), f"/World/Cameras/camera_{name}").GetPrim()
        self.initialize_prim(metadata, scene)
        self.is_embedded = is_embedded

    def step(self, metadata):
        super().step(metadata)
        if not self.is_embedded:
            update_camera_with_proxy(self.name, self.prim)
        else:
            xform = get_total_xform(self.prim)
            update_perspective_camera_with_xform(xform)

    def resolve_annotator_key(self, key):
        if self.rp_name is not None:
            return f"{key}-{self.rp_name}"
        return key

    def capture(self, output_switches, writer_data):
        rgb = (
            Image.fromarray(writer_data[self.resolve_annotator_key("rgb")], "RGBA").convert("RGB")
            if output_switches["images"]
            else None
        )
        # segmentation = (
        #     serialize_segmentation(writer_data["semantic_segmentation"]) if output_switches["segmentation"] else None
        # )
        instance_id_segmentation = (
            serialize_instance_id_segmentation(writer_data[self.resolve_annotator_key("instance_id_segmentation")])
            if output_switches["instance_id_segmentation"]
            else None
        )
        depth = (
            np.nan_to_num(writer_data[self.resolve_annotator_key("distance_to_image_plane")], posinf=0)
            if output_switches["depth"]
            else None
        )
        normal = (
            np.nan_to_num(writer_data[self.resolve_annotator_key("SmoothNormal")], posinf=0)
            if output_switches["normal"]
            else None
        )

        if output_switches["caption"]:
            filtered_bbox_2d = self.filter_bbox("bbox_2d", writer_data)
            bbox_2d = serialize_bbox(filtered_bbox_2d, False) if output_switches["labels"] else None
            filtered_segmentation = self.filter_segmentation_data(writer_data)
            segmentation = serialize_segmentation(filtered_segmentation) if output_switches["segmentation"] else None
        else:
            bbox_2d = (
                serialize_bbox(writer_data[self.resolve_annotator_key("bounding_box_2d_tight_fast")], False)
                if output_switches["labels"]
                else None
            )
            segmentation = (
                serialize_segmentation(writer_data[self.resolve_annotator_key("semantic_segmentation")])
                if output_switches["segmentation"]
                else None
            )

        return rgb, bbox_2d, segmentation, instance_id_segmentation, depth, normal

    def capture_caption(self, caption_configs, writer_data):
        rgb = Image.fromarray(writer_data[self.resolve_annotator_key("rgb")], "RGBA").convert("RGB")
        depth = (
            np.nan_to_num(writer_data[self.resolve_annotator_key("distance_to_image_plane")], posinf=0)
            if caption_configs["export_depth"]
            else None
        )
        pointcloud = (
            writer_data[self.resolve_annotator_key("pointcloud")] if caption_configs["export_point_cloud"] else None
        )

        caption_dict = {}
        annotation_names = ["bbox_2d_unfiltered", "bbox_3d_unfiltered", "camera_params"]

        for annotation_name in annotation_names:
            caption_dict[annotation_name] = self.replicator_annotators[annotation_name].get_data()

        return rgb, depth, pointcloud, caption_dict

    def capture_image_only(self, writer_data):
        return Image.fromarray(writer_data[self.resolve_annotator_key("rgb")], "RGBA").convert("RGB")

    def capture_global_space(self, output_switches, writer_data):
        if output_switches["caption"]:
            return serialize_bbox(self.filter_bbox("bbox_3d", writer_data), True)
        return serialize_bbox(writer_data[self.resolve_annotator_key("bounding_box_3d_fast")], True)

    def filter_bbox(self, bbox_name, writer_data):
        if bbox_name == "bbox_2d":
            bbox_data = writer_data[self.resolve_annotator_key("bounding_box_2d_tight_fast")]
        elif bbox_name == "bbox_3d":
            bbox_data = writer_data[self.resolve_annotator_key("bounding_box_3d_fast")]
        else:
            error(f"invalid bbox_name {bbox_name}")
        filtered_data = {}
        prim_paths = []
        bbox_ids = []
        data_list = []
        id_to_labels = {}
        preserved_ids = []
        for data_id, prim_path in enumerate(bbox_data["info"]["primPaths"]):
            data = bbox_data["data"][data_id]
            semantic_id = data["semanticId"]
            sem_class_dict = bbox_data["info"]["idToLabels"][semantic_id]
            sem_type = list(sem_class_dict.keys())[0]
            if sem_type == SEMANTIC_CLASS_STRING:
                prim_paths.append(prim_path)
                bbox_ids.append(bbox_data["info"]["bboxIds"][data_id])
                data_list.append(data)
                id_to_labels[semantic_id] = sem_class_dict
                preserved_ids.append(data_id)

        filtered_data["info"] = {"bboxIds": np.array(bbox_ids), "idToLabels": id_to_labels, "primPaths": prim_paths}
        filtered_data["data"] = bbox_data["data"][preserved_ids]

        return filtered_data

    def filter_segmentation_data(self, writer_data):
        filtered_data = {}
        id_to_labels = {}
        id_to_labels_dict = writer_data[self.resolve_annotator_key("semantic_segmentation")]["info"]["idToLabels"]
        any_object = False
        for _data_id, idx in enumerate(id_to_labels_dict):
            sem_type, sem_value = list(id_to_labels_dict[idx].items())[0]
            if sem_type == SEMANTIC_CLASS_STRING:
                any_object = True
                id_to_labels[idx] = id_to_labels_dict[idx]
                semantic_class_color = np.array(list(literal_eval(idx)))
            if sem_value in ["BACKGROUND", "UNLABELLED"]:
                id_to_labels[idx] = id_to_labels_dict[idx]
                if sem_value == "BACKGROUND":
                    background_color = np.array(list(literal_eval(idx)))

        seg_data = writer_data[self.resolve_annotator_key("semantic_segmentation")]["data"]
        updated_data = seg_data.copy()
        # for np array data, update all pixels not background or semantic_class_color to background
        # Create a mask for pixels matching the target color
        if any_object:
            mask = np.all(seg_data == semantic_class_color, axis=-1)
        else:
            mask = np.zeros(seg_data.shape[:-1], dtype=bool)

        # Replace non-target pixels with the background color
        updated_data[~mask] = background_color

        filtered_data["info"] = {"idToLabels": id_to_labels}
        filtered_data["data"] = updated_data

        return filtered_data

    def calculate_pixel_thresholds(self, max_area_threshold: float | None, min_area_threshold: float | None):
        """
        Convert max/min area threshold values from percentages (if given) to pixel area values
        relative to the camera's resolution
        """
        # If no thresholds are given, return None
        if self.camera_parameters.get("screen_width") is None or self.camera_parameters.get("screen_height") is None:
            return None, None

        # Calculate the total number of pixels in the camera
        camera_area = self.camera_parameters["screen_width"] * self.camera_parameters["screen_height"]

        # Convert min/max area threshold values from percentages to pixel area values
        pixel_max_area_threshold = None if max_area_threshold is None else max_area_threshold * camera_area
        pixel_min_area_threshold = None if min_area_threshold is None else min_area_threshold * camera_area

        return pixel_max_area_threshold, pixel_min_area_threshold
