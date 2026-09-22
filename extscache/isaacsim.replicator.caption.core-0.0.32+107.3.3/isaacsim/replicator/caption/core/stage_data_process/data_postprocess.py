from typing import Any

import numpy as np
import omni.usd
from omni.syntheticdata.scripts import helpers

from ..utils import Utils


class DataPostProcessor:
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

    def get_world_space_vertices(Max_Vertex: tuple, Min_Vertex: tuple):
        x_max, y_max, z_max = Max_Vertex
        x_min, y_min, z_min = Min_Vertex
        """get vertex in the world space"""
        corners = np.array(
            [
                [x_max, y_min, z_min],
                [x_min, y_min, z_min],
                [x_min, y_max, z_min],
                [x_max, y_max, z_min],
                [x_min, y_min, z_max],
                [x_max, y_min, z_max],
                [x_min, y_max, z_max],
                [x_max, y_max, z_max],
            ]
        )
        return corners

    def world_to_image_helper(points, view_params):
        """helper method to project point in 3d space to 2d image coordinate"""
        projected = helpers.world_to_image(viewport=None, points=points, view_params=view_params)
        # get the projected point in space
        proj_i2w = projected
        # calculate the 2d image coordinate.
        proj_i2w[..., 0] *= view_params["width"]
        proj_i2w[..., 1] *= view_params["height"]
        return proj_i2w.astype(int)

    def get_bbox_3d_data(prim, view_params: Any):
        """post process the bounding box 3d data"""

        if prim is None:
            return None

        # get bounding box corners:
        corners = Utils.get_prim_corners(prim)
        # if the number of vertex is not 8, pause post process
        if corners.shape[0] != 8:
            # corner vertexs num is not 8. discard the info
            return None
        # create a dictionary to record current bounding box information.
        object_transform = np.reshape(omni.usd.get_world_transform_matrix(prim), (4, 4))
        # get corner's 2d coordinate
        processed_data = {}
        processed_data["transform"] = object_transform
        processed_data["scale"] = Utils.get_prim_bbox_scale(prim)
        processed_data["vertex"] = {}
        processed_data["vertex"]["translations_3d"] = corners
        if view_params:
            # get camera's view matrix
            camera_view_matrix = view_params["world_to_view"]
            # get object's 2d coordination.
            corner_2d_coordinates = DataPostProcessor.world_to_image_helper(corners.reshape(-1, 3), view_params)
            processed_data["vertex"]["translations_2d"] = [
                (coordinate[0], coordinate[1]) for coordinate in corner_2d_coordinates
            ]
            # get objects view space transform
            processed_data["view_transform"] = Utils.convert_to_camera_space(object_transform, camera_view_matrix)
            # get view space point's coodrinate
            view_translation_homo_list = np.array(
                [Utils.world_translate_to_camera(pt, camera_view_matrix) for pt in corners]
            )
            processed_data["vertex"]["view_translations_3d"] = [
                (translation_homo[0], translation_homo[1], translation_homo[2])
                for translation_homo in view_translation_homo_list
            ]

        return processed_data

    def get_all_valid_objects():
        """iterate though the stage and fetch captioned objects"""
        # get all captioned props/usd files list
        captioned_usd_list = Utils.get_captioned_props_list()
        target_prim_path_list = []
        stage = omni.usd.get_context().get_stage()
        # iterate through the object in the stage
        for prim in stage.Traverse():
            prim_path = str(prim.GetPrimPath())
            # get current object's reference path, check whether the obejct is captioned (currently we just fetch the referenced usd path)
            object_reference_path = str(Utils.get_object_reference(prim_path=prim_path, stage=stage))
            # if the object has been captioned.
            if object_reference_path in captioned_usd_list:
                target_prim_path_list.append(prim_path)

        return target_prim_path_list
