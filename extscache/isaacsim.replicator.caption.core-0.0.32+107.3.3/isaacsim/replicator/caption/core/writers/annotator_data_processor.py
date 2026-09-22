##container used to store skeleton information
from typing import Any

import numpy as np

from omni.syntheticdata.scripts import helpers

from .object_info_manager import ObjectInfo


# make IRC independent from IRA.
class AnnotatorDataProcessor:
    """
    Copied from isaacsim.replicator.agent.core.data_generator.annotator_data_processor.
    """

    # def evaluate_box_within_viewport(character_box, viewport_box):
    #     """check whether character 2d bounding box is within image, trancated with image boundary or out of viewport"""

    #     def is_within_tolerance(a, b, tolerance=4):
    #         """helper method, check whether character is on the boundary"""
    #         return abs(a - b) <= tolerance

    #     is_within_bound, adjusted_box = AnnotatorDataProcessor.check_bounding_box_relationship(
    #         character_box, viewport_box, is_within_tolerance
    #     )
    #     return is_within_bound, adjusted_box

    def numpy_to_dictionary(target_numpy: np.void, target_key_list: list | None = None):
        """convert a numpy.void type to dictionary"""
        record_dict = {}
        if target_key_list is None:
            record_dict = {name: target_numpy[name] for name in target_numpy.dtype.names}
        else:
            record_dict = {
                name: target_numpy[name] for name in target_numpy.dtype.names if str(name) in target_key_list
            }
        return record_dict

    # calculate character's scale
    def get_scale(bbox_3d_data):
        """calculate bbox 3d's scale information"""
        x_min = bbox_3d_data["x_min"]
        x_max = bbox_3d_data["x_max"]
        y_min = bbox_3d_data["y_min"]
        y_max = bbox_3d_data["y_max"]
        z_min = bbox_3d_data["z_min"]
        z_max = bbox_3d_data["z_max"]

        scale_x = x_max - x_min
        scale_y = y_max - y_min
        scale_z = z_max - z_min

        return (scale_x, scale_y, scale_z)

    # def calculate_2d_bounding_box(points):
    #     """
    #     calculate the bounding box that contains target 2d points set
    #     """
    #     # use numpy 's min/max func to calculate the boundary that contains all points
    #     x_min = np.min(points[:, 0])
    #     y_min = np.min(points[:, 1])
    #     x_max = np.max(points[:, 0])
    #     y_max = np.max(points[:, 1])

    #     return x_min, y_min, x_max, y_max

    def convert_to_camera_space(world_transform, camera_view_matrix):
        camera_view_transform = np.matmul(world_transform, camera_view_matrix)
        return camera_view_transform

    # def check_bounding_box_relationship(inner_box, outer_box, comparison_fn):
    #     """Check the relationship between two bounding boxes."""

    #     # Adjusting to the new input order: (x_min, y_min, x_max, y_max)
    #     inner_x_min, inner_y_min, inner_x_max, inner_y_max = inner_box
    #     outer_x_min, outer_y_min, outer_x_max, outer_y_max = outer_box

    #     # Check if the inner box is completely out of bounds of the outer box
    #     if (
    #         comparison_fn(outer_x_min, inner_x_max)
    #         or comparison_fn(inner_x_min, outer_x_max)
    #         or comparison_fn(outer_y_min, inner_y_max)
    #         or comparison_fn(inner_y_min, outer_y_max)
    #     ):
    #         return WriterSetting.AgentStatus.OUTSIDE, [-1, -1, -1, -1]

    #     status = WriterSetting.AgentStatus.INSIDE

    #     # Adjust bounding box if it's truncated on the edges
    #     if inner_x_max > outer_x_max:
    #         status = WriterSetting.AgentStatus.TRUNCATED
    #         inner_x_max = outer_x_max

    #     if inner_x_min < outer_x_min:
    #         status = WriterSetting.AgentStatus.TRUNCATED
    #         inner_x_min = outer_x_min

    #     if inner_y_max > outer_y_max:
    #         status = WriterSetting.AgentStatus.TRUNCATED
    #         inner_y_max = outer_y_max

    #     if inner_y_min < outer_y_min:
    #         status = WriterSetting.AgentStatus.TRUNCATED
    #         inner_y_min = outer_y_min

    #     return status, (inner_x_min, inner_y_min, inner_x_max, inner_y_max)

    # def extract_2d_box_information(bbox_data):
    #     """extract 2d box informatin as tuple"""
    #     return (bbox_data["x_min"], bbox_data["y_min"], bbox_data["x_max"], bbox_data["y_max"])

    # def model_to_world(pt, obj_xform, camera_xform, proj_mat, screen_width, screen_height):
    #     """This model generate the 3d space point and 2d projection of each point on the cuboid vertex and the central point"""
    #     model_space = np.array([pt[0], pt[1], pt[2], 1])
    #     # calculate the world space position by cross product those two
    #     world_space = model_space @ obj_xform

    #     camera_space = world_space @ camera_xform
    #     ndc_space = camera_space @ proj_mat
    #     ndc_space /= ndc_space[3]
    #     x = (1 + ndc_space[0]) / 2 * screen_width
    #     y = (1 - ndc_space[1]) / 2 * screen_height
    #     return (int(x), int(y)), world_space

    def extent_dimension(extents):
        """extend the demension of input data to fit the format of helper method parameter"""
        extents_batch = {
            "x_min": np.expand_dims(extents["x_min"], axis=0),
            "x_max": np.expand_dims(extents["x_max"], axis=0),
            "y_min": np.expand_dims(extents["y_min"], axis=0),
            "y_max": np.expand_dims(extents["y_max"], axis=0),
            "z_min": np.expand_dims(extents["z_min"], axis=0),
            "z_max": np.expand_dims(extents["z_max"], axis=0),
            "transform": np.expand_dims(extents["transform"], axis=0),
        }
        return extents_batch

    def reformat_camera_params(camera_params: Any):
        """helper method to reformat the camera params array"""

        projection_type = camera_params["cameraModel"]
        world_to_view = np.reshape(camera_params["cameraViewTransform"], (4, 4))
        view_to_world = np.linalg.inv(world_to_view)
        width, height = camera_params["renderProductResolution"][0], camera_params["renderProductResolution"][1]
        if projection_type == "fisheyePolynomial":
            ftheta = {
                "width": camera_params["cameraFisheyeNominalWidth"],
                "height": camera_params["cameraFisheyeNominalHeight"],
                "cx": camera_params["cameraFisheyeOpticalCentre"][0],
                "cy": camera_params["cameraFisheyeOpticalCentre"][1],
                "poly_a": camera_params["cameraFisheyePolynomial"][0],
                "poly_b": camera_params["cameraFisheyePolynomial"][1],
                "poly_c": camera_params["cameraFisheyePolynomial"][2],
                "poly_d": camera_params["cameraFisheyePolynomial"][3],
                "poly_e": camera_params["cameraFisheyePolynomial"][4],
                "poly_f": camera_params["cameraFisheyePolynomial"][5],
                "max_fov": camera_params["cameraFisheyeMaxFOV"],
            }
            ftheta["edge_fov"] = helpers.ftheta_distortion(ftheta, ftheta["width"] / 2)
            ftheta["c_ndc"] = np.array(
                [
                    (ftheta["cx"] - ftheta["width"] / 2) / ftheta["width"],
                    (ftheta["height"] / 2 - ftheta["cy"]) / ftheta["width"],
                ]
            )
        else:
            ftheta = None

        view_params = {
            "view_to_world": np.array(view_to_world),
            "world_to_view": np.array(world_to_view),
            "projection_type": projection_type,
            "ftheta": ftheta,
            "width": width,
            "height": height,
            "aspect_ratio": width / height,
            "clipping_range": camera_params["cameraNearFar"],
            "horizontal_aperture": camera_params["cameraAperture"][0],
            "focal_length": camera_params["cameraFocalLength"],
        }
        return view_params

    def world_to_image_helper(points, view_params):
        """helper method to project point in 3d space to 2d image coordinate"""
        projected = helpers.world_to_image(viewport=None, points=points, view_params=view_params)
        # get the projected point in space
        proj_i2w = projected
        # calculate the 2d image coordinate.
        proj_i2w[..., 0] *= view_params["width"]
        proj_i2w[..., 1] *= view_params["height"]
        return proj_i2w.astype(int)

    def validate_and_process_bbox_3d_data(object_info: ObjectInfo, camera_params: Any):
        """post process the bounding box 3d data"""
        if True:

            bbox_3d_annotator_name = "bounding_box_3d_fast"
            bbox_data = object_info.get_annotator_info(bbox_3d_annotator_name)

            if not bbox_data:
                return False
            # reformat the view params
            view_params = AnnotatorDataProcessor.reformat_camera_params(camera_params)
            # post process the 3d bounding box information
            corners = helpers.get_bbox_3d_corners(AnnotatorDataProcessor.extent_dimension(bbox_data))
            # if the number of vertex is not 8, pause post process
            if corners.shape[1] != 8:
                # carb.log_info("corner vertex is not 8. discard the info")
                return False

            # convert the bounding box to dictionary to include new values.
            processed_data = AnnotatorDataProcessor.numpy_to_dictionary(bbox_data)
            processed_data["scale"] = AnnotatorDataProcessor.get_scale(bbox_data)
            processed_data["vertex"] = {}
            processed_data["vertex"]["translations_3d"] = corners
            processed_data["vertex"]["translations_2d"] = AnnotatorDataProcessor.world_to_image_helper(
                corners.reshape(-1, 3), view_params
            )
            object_info.update_annotator_data(bbox_3d_annotator_name, processed_data)

            return True
