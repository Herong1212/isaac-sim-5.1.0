import os
import re
from datetime import datetime
from typing import List, Dict

import numpy as np
import PIL.Image as Image
import Semantics
from scipy.spatial.transform import Rotation

from omni.metropolis.utils.rotation_util import RotationUtil

from .misc import to_array, write_json
from ..constants import SEMANTIC_CLASS_STRING

# from skimage import measure


def enable_semantics(prim, semantic_label, semantic_class=SEMANTIC_CLASS_STRING):
    if not prim.HasAPI(Semantics.SemanticsAPI):
        sem = Semantics.SemanticsAPI.Apply(prim, "Semantics")
        sem.CreateSemanticTypeAttr()
        sem.CreateSemanticDataAttr()
    else:
        sem = Semantics.SemanticsAPI.Get(prim, "Semantics")
    sem.GetSemanticTypeAttr().Set(semantic_class)
    sem.GetSemanticDataAttr().Set(semantic_label)


def labels_to_string(name=None, labels=None):
    res = f"{name}||" if name is not None else ""
    for k, v in labels.items():
        res += f"{k}:{v}|"
    res = res[:-1]
    return res


def save_bbox_2d_to_kitti(bboxes_2d, path, occlusion_threshold, pixel_max_area_threshold, pixel_min_area_threshold):
    lbl_txt = ""
    visible_labeled_set = {}
    for name, data in bboxes_2d.items():
        if data["occlusion"] > occlusion_threshold:
            continue
        # area threshold filtering
        if pixel_min_area_threshold is not None or pixel_max_area_threshold is not None:
            # TODO: Ideally we should have this precalcuated using the GPU
            area = (data["x_max"] - data["x_min"]) * (data["y_max"] - data["y_min"])
            if pixel_max_area_threshold is not None and area > pixel_max_area_threshold:
                continue
            if pixel_min_area_threshold is not None and area < pixel_min_area_threshold:
                continue

        name_label_string = labels_to_string(name, data["labels"])
        lbl_txt += f"{name_label_string} 0 {data['occlusion']} 0 {data['x_min']} {data['y_min']} {data['x_max']} {data['y_max']} 0 0 0 0 0 0 0\n"  # noqa
        visible_labeled_set[name] = name_label_string

    with open(path, "w") as f:
        f.write(lbl_txt)
    return visible_labeled_set


def camera_ov_to_standard(camera_parameters):
    standard_camera_parameters = {}
    for key, value in camera_parameters.items():
        if key not in ["focal_length", "horizontal_aperture"]:
            standard_camera_parameters[key] = value
    standard_camera_parameters["pinhole_ratio"] = (
        2
        * camera_parameters["focal_length"]
        / camera_parameters["horizontal_aperture"]
        * camera_parameters["screen_width"]
        / camera_parameters["screen_height"]
    )
    return standard_camera_parameters


def get_projection_matrix(camera_intrinsics):
    n, f = camera_intrinsics["near_clip"], camera_intrinsics["far_clip"]
    p = (n + f) / (n - f)
    q = 2 * n * f / (n - f)
    screen_width, screen_height = camera_intrinsics["screen_width"], camera_intrinsics["screen_height"]
    pinhole_ratio = camera_intrinsics["pinhole_ratio"]
    return np.transpose(
        np.array(
            [
                [pinhole_ratio / screen_width * screen_height, 0, 0, 0],
                [0, pinhole_ratio, 0, 0],
                [0, 0, p, q],
                [0, 0, -1, 0],
            ]
        )
    )


def model_to_2d(pt, obj_xform, camera_xform, camera_intrinsics):
    model_space = np.array([pt[0], pt[1], pt[2], 1])
    world_space = model_space @ obj_xform
    camera_space = world_space @ np.linalg.inv(camera_xform)

    proj_mat = get_projection_matrix(camera_intrinsics)
    ndc_space = camera_space @ proj_mat
    ndc_space /= ndc_space[3]

    screen_width, screen_height = camera_intrinsics["screen_width"], camera_intrinsics["screen_height"]
    x = (1 + ndc_space[0]) / 2 * screen_width
    y = (1 - ndc_space[1]) / 2 * screen_height
    return {"2d": (int(x), int(y)), "3d": (camera_space[:3] @ RotationUtil.rot_z(90))}


def get_intrinsics(camera_intrinsics):
    screen_width, screen_height = camera_intrinsics["screen_width"], camera_intrinsics["screen_height"]
    pinhole_ratio = camera_intrinsics["pinhole_ratio"]
    aspect_ratio = screen_width / screen_height
    fx = screen_width * pinhole_ratio / aspect_ratio / 2
    fy = screen_height * pinhole_ratio / 2
    cx = screen_width / 2
    cy = screen_height / 2
    return fx, fy, cx, cy


def save_to_3d_labels(camera_info, bboxes_3d, path, visible_labeled_set):
    camera_xform = np.array(camera_info["global_transform"])
    camera_parameters = camera_info["camera_parameters"]
    camera_intrinsics = camera_ov_to_standard(camera_parameters)

    proj_mat_output = np.transpose(get_projection_matrix(camera_intrinsics))
    proj_mat_output[0][0], proj_mat_output[1][1] = proj_mat_output[1][1], proj_mat_output[0][0]
    fx, fy, cx, cy = get_intrinsics(camera_intrinsics)

    objects_metadata = []
    for name, bbox_3d in bboxes_3d.items():
        if name in visible_labeled_set:
            model_pts = [
                (
                    (bbox_3d["x_min"] + bbox_3d["x_max"]) / 2,
                    (bbox_3d["y_min"] + bbox_3d["y_max"]) / 2,
                    (bbox_3d["z_min"] + bbox_3d["z_max"]) / 2,
                ),
                (bbox_3d["x_min"], bbox_3d["y_min"], bbox_3d["z_min"]),
                (bbox_3d["x_min"], bbox_3d["y_min"], bbox_3d["z_max"]),
                (bbox_3d["x_min"], bbox_3d["y_max"], bbox_3d["z_min"]),
                (bbox_3d["x_min"], bbox_3d["y_max"], bbox_3d["z_max"]),
                (bbox_3d["x_max"], bbox_3d["y_min"], bbox_3d["z_min"]),
                (bbox_3d["x_max"], bbox_3d["y_min"], bbox_3d["z_max"]),
                (bbox_3d["x_max"], bbox_3d["y_max"], bbox_3d["z_min"]),
                (bbox_3d["x_max"], bbox_3d["y_max"], bbox_3d["z_max"]),
            ]
            screen_camera_pts = [
                model_to_2d(pt, np.array(bbox_3d["transform"]), camera_xform, camera_intrinsics) for pt in model_pts
            ]
            scale = [
                float(bbox_3d["x_max"] - bbox_3d["x_min"]),
                float(bbox_3d["y_max"] - bbox_3d["y_min"]),
                float(bbox_3d["z_max"] - bbox_3d["z_min"]),
            ]
            object_metadata = {
                "name": name,  # used to be resolve_mutable_name(name, True) as above
                "keypoints_3d": [list(pt["3d"]) for pt in screen_camera_pts],
                "quaternion_xyzw": list(
                    Rotation.from_matrix(
                        np.transpose(
                            np.array(bbox_3d["transform"])[:3, :3]
                            @ np.linalg.inv(camera_xform[:3, :3])
                            @ RotationUtil.rot_z(90)
                        )
                    ).as_quat()
                ),
                "location": list(screen_camera_pts[0]["3d"]),
                "projected_cuboid": [list(pt["2d"]) for pt in screen_camera_pts],
                "scale": scale,
            }
            objects_metadata.append(object_metadata)

    metadata = {
        "camera_data": {
            "camera_projection_matrix": to_array(proj_mat_output),
            "intrinsics": {"cx": cx, "cy": cy, "fx": fx, "fy": fy},
        },
        "objects": objects_metadata,
    }

    write_json(metadata, path)


def bbox_to_corners(bbox_3d):
    return (
        (bbox_3d["x_min"], bbox_3d["y_min"], bbox_3d["z_min"]),
        (bbox_3d["x_min"], bbox_3d["y_min"], bbox_3d["z_max"]),
        (bbox_3d["x_min"], bbox_3d["y_max"], bbox_3d["z_min"]),
        (bbox_3d["x_min"], bbox_3d["y_max"], bbox_3d["z_max"]),
        (bbox_3d["x_max"], bbox_3d["y_min"], bbox_3d["z_min"]),
        (bbox_3d["x_max"], bbox_3d["y_min"], bbox_3d["z_max"]),
        (bbox_3d["x_max"], bbox_3d["y_max"], bbox_3d["z_min"]),
        (bbox_3d["x_max"], bbox_3d["y_max"], bbox_3d["z_max"]),
    )


def to_vec3(v):
    return np.array([v[0], v[1], v[2]])


def to_vec4(v):
    return np.array([v[0], v[1], v[2], 1])


def save_to_caption_like(camera_info, bboxes_2d, bboxes_3d, path, visible_labeled_set):
    metadata = {}
    view_matrix = np.linalg.inv(np.array(camera_info["global_transform"]))
    for name, data in bboxes_2d.items():
        if name in visible_labeled_set and name in bboxes_3d:
            label_str = labels_to_string(name, data["labels"])
            prim_path, class_str = label_str.split("||")
            corners_global = [
                to_vec3(to_vec4(np.array(i)) @ np.array(bboxes_3d[name]["transform"])).tolist()
                for i in bbox_to_corners(bboxes_3d[name])
            ]
            corners_camera = [to_vec3(to_vec4(np.array(i)) @ view_matrix).tolist() for i in corners_global]
            centroid_camera = (sum([np.array(i) for i in corners_camera]) / 8).tolist()
            metadata[prim_path] = {
                "class": class_str,
                "3d_bbox_world_space": corners_global,
                "3d_bbox_camera_space": corners_camera,
                "2d_bbox": [data["x_min"], data["y_min"], data["x_max"], data["y_max"]],
                "3d_bbox_centroid_camera_space": centroid_camera,
                "id": hash(prim_path),
            }

    write_json(metadata, path)


def save_2dlabels_coco(coco_labels, output_path, height, width, binary_obj_det=None):
    images = []
    annotations = []
    categories_dict = {}
    images_count = 1
    annotations_count = 1
    categories_count = 1

    for k, v in coco_labels.items():

        annotation_for_this_image = 0
        for cn, details in v.items():
            if "~~~" in cn:
                sp = cn.split("~~~")
                if len(sp) == 2:
                    class_name = sp[1]
                else:
                    class_name = cn
            else:
                class_name = cn

            if class_name in categories_dict:
                cid = categories_dict[class_name]
            else:
                categories_dict[class_name] = categories_count
                cid = categories_count
                categories_count += 1

            bbox_x = max(details["x_min"], 0)
            bbox_y = max(details["y_min"], 0)
            if bbox_x > width:
                bbox_x = width - 1
            if bbox_y > height:
                bbox_y = height - 1
            bbox_w = details["x_max"] - bbox_x
            bbox_h = details["y_max"] - bbox_y
            if 0 < bbox_w < width and 0 < bbox_h < height:
                if binary_obj_det is not None and binary_obj_det:
                    annotations.append(
                        {
                            "id": annotations_count,
                            "category_id": 1,
                            "image_id": images_count,
                            "iscrowd": 0,
                            "area": (bbox_w * bbox_h),
                            "bbox": [bbox_x, bbox_y, bbox_w, bbox_h],
                        }
                    )
                else:
                    annotations.append(
                        {
                            "id": annotations_count,
                            "category_id": cid,
                            "image_id": images_count,
                            "iscrowd": 0,
                            "area": (bbox_w * bbox_h),
                            "bbox": [bbox_x, bbox_y, bbox_w, bbox_h],
                        }
                    )
                annotations_count += 1
                annotation_for_this_image += 1

        if annotation_for_this_image > 0:
            images.append(
                {
                    "id": images_count,
                    "date_captured": str(datetime.utcnow()),
                    "width": width,
                    "height": height,
                    "file_name": f"{k}.jpg",
                }
            )
            images_count += 1

        categories = []
        if binary_obj_det is not None and binary_obj_det:
            categories.append({"id": 1, "name": "retail_object"})
        else:
            for k, v in categories_dict.items():
                categories.append({"id": v, "name": k})

        data = {"categories": categories, "annotations": annotations, "images": images}

        write_json(data, os.path.join(output_path, "annotations.json"), no_sort=True)


# def kitti_dict_to_list(kitti_labels):
#     kitti_labels_list = []
#     for name, data in kitti_labels.items():
#         kitti_labels_list.append(f"{name} 0 {data['occlusion']} 0 {data['x_min']} {data['y_min']} {data['x_max']} {data['y_max']} 0 0 0 0 0 0 0")  # noqa
#     return kitti_labels_list
#
# def parse_od_suffix(suffix):
#     pattern = r'([^<]+)(<loc_(\d+)>){4}'
#     matches = re.findall(pattern, suffix)
#     objects = []
#     for match in matches:
#         class_name = match[0]
#         coords = re.findall(r'<loc_(\d+)>', suffix[suffix.index(class_name):])
#         objects.append((class_name, list(map(int, coords[:4]))))  # Take only the first 4 coordinates
#     return objects
#
# def generate_object_detection_labels(image: Image.Image, kitti_labels: List[str]) -> List[Dict]:
#     # Generate object detection labels from ORO into Florence 2 format
#     labels = []
#     prefix = "<OD>"
#     suffix = ""
#
#     # Get image dimensions
#     img_width, img_height = image.size
#
#     # Read KITTI format label file
#     #with open(kitti_label_path, 'r') as f:
#     #    lines = f.readlines()
#
#     for line in kitti_labels:
#         parts = line.strip().split()
#         if len(parts) < 9:  # Ensure the line has enough parts
#             continue
#
#         # Extract class name and bounding box coordinates
#         if '~~~' in parts[0]:
#             class_name = parts[0].split('~~~')[1]  # Get class name after '~~~'
#         else:
#             class_name = parts[0]
#         x1, y1, x2, y2 = map(float, parts[4:8])  # KITTI format uses 0-based index for bbox
#
#         # Normalize coordinates to 0-999 range
#         norm_x1 = int((x1 / img_width) * 999)
#         norm_y1 = int((y1 / img_height) * 999)
#         norm_x2 = int((x2 / img_width) * 999)
#         norm_y2 = int((y2 / img_height) * 999)
#
#         # Append to suffix
#         suffix += f"{class_name}<loc_{norm_x1}><loc_{norm_y1}><loc_{norm_x2}><loc_{norm_y2}>"
#
#     labels.append({"prefix": prefix, "suffix": suffix})
#
#     return labels
#
# def generate_referring_expression_segmentation_labels(image: Image.Image, mask: Image.Image, color_list: Dict) -> List[Dict]:  # noqa
#     # Generate referring expression to segmentation labels in Florence 2 format
#     labels = []
#     # Load the mask image
#     #mask = Image.open(mask_path)
#     mask_array = np.array(mask)
#
#     # Load the YAML file
#     #with open(yaml_path, 'r') as f:
#     #    yaml_data = yaml.safe_load(f)
#
#
#     # Get image dimensions
#     img_width, img_height = image.size
#
#     # Process each object in the YAML file
#     for color_str, class_info in color_list.items():
#         if class_info in ['BACKGROUND', 'UNLABELLED']:
#             continue
#
#         # Parse color and class name
#         r, g, b, a = map(int, color_str.strip('()').split(','))
#         class_name = class_info.split('~~~')[1]
#
#         # Create a binary mask for this object
#         object_mask = np.all(mask_array == [r, g, b], axis=-1)
#
#         # Find contours
#         contours = measure.find_contours(object_mask, 0.5)
#
#         if contours:
#             # Use the largest contour
#             contour = max(contours, key=len)
#
#             # Simplify the contour to at most 120 points (maybe more?)
#             if len(contour) > 120:
#                 step = len(contour) // 120
#                 contour = contour[::step][:120]
#
#             # Normalize coordinates to 0-999 range
#             normalized_contour = []
#             for y, x in contour:
#                 norm_x = int((x / img_width) * 999)
#                 norm_y = int((y / img_height) * 999)
#                 normalized_contour.extend([norm_x, norm_y])
#
#             # Create the label
#             prefix = f"<REFERRING_EXPRESSION_SEGMENTATION>{class_name}"
#             suffix = ''.join(f"<loc_{x}><loc_{y}>" for x, y in zip(normalized_contour[::2], normalized_contour[1::2]))
#
#             labels.append({"prefix": prefix, "suffix": suffix})
#
#     return labels
#
# def generate_region_to_segmentation_labels(od_labels, seg_labels) -> List[Dict]:
#     # Generate region to segmentation labels
#     # there may be fewer bounding boxes than segmentation labels (from ORO)
#     labels = []
#     for od_label in od_labels:
#         objects = parse_od_suffix(od_label['suffix'])
#         for class_name, bbox in objects:
#             for seg_label in seg_labels:
#                 # if the segmentation class name exists in the bounding boxes
#                 if seg_label['prefix'].split(">")[1] == class_name:
#                     labels.append({
#                         "prefix": f"<REGION_TO_SEGMENTATION><loc_{bbox[0]}><loc_{bbox[1]}><loc_{bbox[2]}><loc_{bbox[3]}>",  # noqa
#                         "suffix": seg_label['suffix']})
#     return labels
#
# def florance2_like_captions(filtered_bboxes_2d, segmentation_image, image, updated_color_list):
#
#     kitti_labels = kitti_dict_to_list(filtered_bboxes_2d)
#     od_labels = generate_object_detection_labels(image, kitti_labels)
#
#     seg_labels = generate_referring_expression_segmentation_labels(image, segmentation_image, updated_color_list)
#
#     reg_to_seg = generate_region_to_segmentation_labels(od_labels, seg_labels)
#
#     return od_labels + seg_labels + reg_to_seg


def kitti_dict_to_list(kitti_labels):
    kitti_labels_list = []
    for name, data in kitti_labels.items():
        kitti_labels_list.append(
            f"{labels_to_string(name, data['labels'])} 0 {data['occlusion']} 0 {data['x_min']} {data['y_min']} {data['x_max']} {data['y_max']} 0 0 0 0 0 0 0"  # noqa
        )
    return kitti_labels_list


def parse_od_suffix(suffix):
    pattern = r"([^<]+)(<loc_(\d+)>){4}"
    matches = re.findall(pattern, suffix)
    objects = []
    for match in matches:
        class_name = match[0]
        coords = re.findall(r"<loc_(\d+)>", suffix[suffix.index(class_name) :])
        objects.append((class_name, list(map(int, coords[:4]))))  # Take only the first 4 coordinates
    return objects


def import_cv2():
    import cv2  # noqa

    return cv2


def simplify_polygon(polygon, max_points):
    cv2 = import_cv2()

    if len(polygon) <= max_points:
        return polygon

    epsilon = 0.005
    while len(polygon) > max_points:
        epsilon *= 1.1
        polygon = cv2.approxPolyDP(polygon, epsilon, True)
    return polygon


def generate_object_detection_labels(image: Image.Image, kitti_labels: List[str]) -> List[Dict]:
    # Generate object detection labels from ORO into Florence 2 format
    labels = []

    # Get image dimensions
    img_width, img_height = image.size
    img_width -= 1
    img_height -= 1

    # Read KITTI format label file
    # with open(kitti_label_path, 'r') as f:
    #    lines = f.readlines()

    # Get the class labels, map the class string to the correct label
    # This deals with multiple object detections of the same class
    class_suffix_map = {}
    for line in kitti_labels:
        parts = line.strip().split()

        if len(parts) < 9:  # Ensure the line has enough parts
            continue

        # Extract class name and bounding box coordinates
        if "~~~" in parts[0]:
            class_string = parts[0].split("~~~")[1].split("|")[0]  # Get class name after '~~~'
        else:
            class_string = parts[0].split("||")[0].split("/")[-1]

        # Remove the trailing numberic ID from some class labels
        class_split = class_string.split("_")
        if class_split[-1].isdigit():
            class_name = class_string[:-4].replace("_", " ")
        else:
            class_name = class_string.replace("_", " ")

        x1, y1, x2, y2 = map(float, parts[4:8])  # KITTI format uses 0-based index for bbox

        # Normalize coordinates to 0-999 range
        norm_x1 = int((x1 / img_width) * 999)
        norm_y1 = int((y1 / img_height) * 999)
        norm_x2 = int((x2 / img_width) * 999)
        norm_y2 = int((y2 / img_height) * 999)

        if class_name in class_suffix_map:
            class_suffix_map[class_name] += f"instance<loc_{norm_x1}><loc_{norm_y1}><loc_{norm_x2}><loc_{norm_y2}>"
        else:
            class_suffix_map[class_name] = f"instance<loc_{norm_x1}><loc_{norm_y1}><loc_{norm_x2}><loc_{norm_y2}>"

    # Assemble the labels
    for class_name, suffix in class_suffix_map.items():
        prefix = f"<OD_CLASS>{class_name}"
        labels.append({"prefix": prefix, "suffix": suffix})

    return labels


def generate_referring_expression_segmentation_labels(
    image: Image.Image, mask: Image.Image, color_list: Dict, max_tokens: int = 1000
) -> List[Dict]:
    cv2 = import_cv2()

    # Generate referring expression to segmentation labels in Florence 2 format
    labels = []
    # Load the mask image
    # mask = Image.open(mask_path)
    mask_array = np.array(mask)

    # Load the YAML file
    # with open(yaml_path, 'r') as f:
    #    yaml_data = yaml.safe_load(f)

    class_suffix_map = {}
    class_token_map = {}

    # Get image dimensions
    img_width, img_height = image.size
    img_width -= 1
    img_height -= 1

    # Process each object in the segmentation map, combining same class names and dealing with max length annotations
    for color_str, class_info in color_list.items():
        if class_info in ["BACKGROUND", "UNLABELLED"]:
            continue

        # Parse color and class name
        r, g, b, _a = map(int, color_str.strip("()").split(","))
        # class_name = class_info.split('~~~')[1]
        if "~~~" in class_info:
            class_string = class_info.split("~~~")[1]  # Get class name after '~~~'
        else:
            class_string = class_info

        # Remove the trailing numberic ID from some class labels
        class_split = class_string.split("_")
        if class_split[-1].isdigit():
            class_name = class_string[:-4].replace("_", " ")
        else:
            class_name = class_string.replace("_", " ")

        # Create a binary mask for this object
        object_mask = np.all(mask_array == [r, g, b], axis=-1).astype(np.uint8)

        # Find contours
        contours, _ = cv2.findContours(object_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Save all of the object contours
        for contour in contours:
            simplified_polygon = simplify_polygon(contour, 80).squeeze()
            if len(simplified_polygon) >= 3:
                simplified_polygon[:, 0] = np.round((simplified_polygon[:, 0] / img_width) * 999).astype(int)
                simplified_polygon[:, 1] = np.round((simplified_polygon[:, 1] / img_height) * 999).astype(int)
                if class_name in class_suffix_map:
                    class_suffix_map[class_name] += "instance"
                    class_token_map[class_name] += 2 * len(simplified_polygon) + 1
                else:
                    class_suffix_map[class_name] = "instance"
                    class_token_map[class_name] = 2 * len(simplified_polygon) + 1
                class_suffix_map[class_name] += "".join(
                    f"<loc_{x}><loc_{y}>" for x, y in zip(simplified_polygon[:, 0], simplified_polygon[:, 1])
                )

    # Assemble the labels
    for class_name, suffix in class_suffix_map.items():
        if class_token_map[class_name] <= max_tokens:
            prefix = f"<REFERRING_EXPRESSION_SEGMENTATION>{class_name}"
            labels.append({"prefix": prefix, "suffix": suffix})

    return labels


def generate_region_to_segmentation_labels(od_labels: List[Dict], seg_labels: List[Dict]) -> List[Dict]:
    # Generate region to segmentation labels
    # there may be fewer bounding boxes than segmentation labels (from ORO)
    labels = []
    # We will limit this type of label to when there is only a single bounding box for a class
    for od_label in od_labels:
        n_od_labels = len(od_label["suffix"].split("instance"))
        if n_od_labels > 2:
            continue
        class_name = od_label["prefix"].strip("<OD_CLASS>")
        bbox = re.findall(r"<loc_(\d+)>", od_label["suffix"].strip("instance"))
        for seg_label in seg_labels:
            if seg_label["prefix"].split(">")[1] == class_name:
                # Ensure that the object only has one segmentation mask
                n_seg_labels = len(seg_label["suffix"].split("instance"))
                if n_seg_labels == 2:
                    labels.append(
                        {
                            "prefix": f"<REGION_TO_SEGMENTATION><loc_{bbox[0]}><loc_{bbox[1]}><loc_{bbox[2]}><loc_{bbox[3]}>",  # noqa
                            "suffix": seg_label["suffix"].split("instance")[1],
                        }
                    )

    return labels


def florance2_like_captions(filtered_bboxes_2d, segmentation_image, image, updated_color_list):

    kitti_labels = kitti_dict_to_list(filtered_bboxes_2d)
    labels = []
    od_labels = generate_object_detection_labels(image, kitti_labels)
    for od_label in od_labels:
        if (od_label["suffix"] == "") or (od_label["suffix"] == "instance"):
            continue
        labels.append(od_label)

    seg_labels = generate_referring_expression_segmentation_labels(image, segmentation_image, updated_color_list)
    for seg_label in seg_labels:
        if (seg_label["suffix"] == "") or (seg_label["suffix"] == "instance"):
            continue
        labels.append(seg_label)

    reg_to_seg_labels = generate_region_to_segmentation_labels(od_labels, seg_labels)
    for reg_to_seg_label in reg_to_seg_labels:
        labels.append(reg_to_seg_label)

    return labels
