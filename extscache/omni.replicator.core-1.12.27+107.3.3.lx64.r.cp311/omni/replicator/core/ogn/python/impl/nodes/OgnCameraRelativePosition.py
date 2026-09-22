# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
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

import math

import numpy as np
import omni.graph.core as og
import omni.replicator.core as rep
import omni.timeline
import omni.usd
from omni.replicator.core import utils
from omni.usd._impl.utils import get_prim_at_path
from pxr import Sdf, UsdGeom


def _fish_eye_map_to_sphere(screen, screen_norm, theta, max_fov):
    """Utility function to map a sample from a disk on the image plane to a sphere."""
    direction = np.array([[0, 0, -1]] * screen.shape[0], dtype=np.float)
    extent = np.zeros(screen.shape[0], dtype=np.float)
    # A real fisheye have some maximum FOV after which the lens clips.
    # Map to a disk: screen / R normalizes the polar direction in screen space.
    # valid_mask = theta <= max_fov
    # Scale theta to max field of view
    theta = theta[:-1] * max_fov / theta[-1]
    screen = screen[:-1]
    screen_norm = screen_norm[:-1]

    xy = screen
    screen_norm_mask = screen_norm > 1e-5
    xy[screen_norm_mask] = xy[screen_norm_mask] / screen_norm[:, None]

    # Map disk to a sphere
    cos_theta = np.cos(theta)
    sin_theta = np.sqrt(1.0 - cos_theta**2)

    # Todo: is this right? Do we assume z is negative (RH coordinate system)?
    z = -cos_theta
    xy = xy * sin_theta[:, None]
    direction = np.stack([xy[:, 0], xy[:, 1], z], axis=1)
    extent = 1.0  # < far clip is not a plane, it's a sphere!

    return direction, extent


def get_view_params(camera_path, width, height):
    """Get view parameters.
    Args:
        viewport (omni.kit.viewport_legacy._viewport.IViewportWindow): Viewport from which to retrieve/create sensor.

    Returns:
        (dict): Dictionary containing view parameters.
    """
    stage = omni.usd.get_context().get_stage()
    camera = stage.GetPrimAtPath(str(camera_path))
    if camera.HasAttribute("replicatorXform"):
        camera = camera.GetChildren()[0]

    current_time = omni.timeline.get_timeline_interface().get_current_time()
    view_to_world = UsdGeom.Imageable(camera).ComputeLocalToWorldTransform(current_time)

    world_to_view = view_to_world.GetInverse()

    projection_type = camera.GetAttribute("cameraProjectionType").Get()
    if projection_type is None:
        projection_type = "pinhole"

    if projection_type == "fisheyePolynomial":
        ftheta = {
            "width": camera.GetAttribute("fthetaWidth").Get(),
            "height": camera.GetAttribute("fthetaHeight").Get(),
            "cx": camera.GetAttribute("fthetaCx").Get(),
            "cy": camera.GetAttribute("fthetaCy").Get(),
            "poly_a": camera.GetAttribute("fthetaPolyA").Get(),
            "poly_b": camera.GetAttribute("fthetaPolyB").Get(),
            "poly_c": camera.GetAttribute("fthetaPolyC").Get(),
            "poly_d": camera.GetAttribute("fthetaPolyD").Get(),
            "poly_e": camera.GetAttribute("fthetaPolyE").Get(),
            "poly_f": camera.GetAttribute("fthetaPolyF").Get(),
            "max_fov": camera.GetAttribute("fthetaMaxFov").Get(),
            "aspect_ratio": width / height,
        }
        ftheta["edge_fov"] = ftheta_distortion(ftheta, ftheta["width"] / 2)
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
        "aperture_h": camera.GetAttribute("horizontalAperture").Get(),
        "focal_length": camera.GetAttribute("focalLength").Get(),
        "aspect_ratio": width / height,
    }
    return view_params  # noqa R504


def ftheta_distortion(ftheta, x):
    """F-Theta distortion."""
    return ftheta["poly_a"] + x * (
        ftheta["poly_b"]
        + x * (ftheta["poly_c"] + x * (ftheta["poly_d"] + x * (ftheta["poly_e"] + x * ftheta["poly_f"])))
    )


def get_projection_matrix(fov, aspect_ratio, z_near, z_far):
    """
    Calculate the camera projection matrix.

    Args:
        fov (float): Field of View (in radians)
        aspect_ratio (float): Image aspect ratio (Width / Height)
        z_near (float): distance to near clipping plane
        z_far (float): distance to far clipping plane

    Returns:
        (numpy.ndarray): View projection matrix with shape `(4, 4)`
    """
    a = -1.0 / math.tan(fov / 2)
    b = -a * aspect_ratio
    c = z_far / (z_far - z_near)
    d = z_near * z_far / (z_far - z_near)
    return np.array([[a, 0.0, 0.0, 0.0], [0.0, b, 0.0, 0.0], [0.0, 0.0, c, 1.0], [0.0, 0.0, d, 0.0]])


def get_view_proj_mat(view_params):
    """
    Get View Projection Matrix.

    Args:
        view_params (dict): dictionary containing view parameters
    """
    z_near, z_far = view_params["clipping_range"]
    view_matrix = np.linalg.inv(view_params["view_to_world"])
    fov = 2 * math.atan(view_params["aperture_h"] / (2 * view_params["focal_length"]))
    projection_mat = get_projection_matrix(fov, view_params["aspect_ratio"], z_near, z_far)
    return np.dot(view_matrix, projection_mat)


def project_pinhole(points, view_params, distance):
    """
    Project 2D points in image space to 3D points in world using a pinhole camera model.

    Args:
        points (numpy.ndarray): Array of points in world frame of shape (num_points, 3).
        viewport (omni.kit.viewport_legacy._viewport.IViewportWindow): Viewport from which to retrieve/create sensor.

    Returns:
        (numpy.ndarray): Image-space points of shape (num_points, 3)
    """
    horiz_fov = 2 * np.arctan(view_params["aperture_h"] / (2 * view_params["focal_length"]))
    vert_fov = horiz_fov * (view_params["height"] / view_params["width"])

    radius = distance
    theta = horiz_fov * points[:, 0] / 2
    phi = vert_fov * points[:, 1] / 2

    # Convert from polar to cartesian
    y = radius * np.sin(phi)
    h = radius * np.cos(phi)
    x = h * np.sin(theta)
    z = -h * np.cos(theta)  # -Z is camera forward

    position_cam = np.stack([x, y, z], axis=1)
    position_world = np.pad(position_cam, ((0, 0), (0, 1)), constant_values=1) @ view_params["view_to_world"]
    return position_world[:, :3]


def fish_eye_polynomial(ndc, view_params, distance):
    """FTheta camera model based on DW src/rigconfiguration/CameraModelsNoEigen.hpp"""

    # Convert NDC pixel position to screen space... well almost. It is screen space but the extent of x is [-0.5, 0.5]
    # and the extent of y is [-0.5/aspectRatio, 0.5/aspectRatio].
    ndc = np.append(ndc, [[1, 1]], axis=0)  # Add this to determine theta at the limits of the FOV
    screen = ndc * 0.5
    # aspect_ratio = view_params["aspect_ratio"]
    # screen[:, 1] /= -aspect_ratio

    # The FTheta polynomial works at a nominal resolution. So far we have done calculations in NDC to be
    # resolution independent. Here we scale by the nominal resolution in X.
    screen = (screen - view_params["ftheta"]["c_ndc"]) * view_params["ftheta"]["width"]

    # Compute the radial distance on the screen from its center point
    r = np.sqrt(screen[:, 0] ** 2 + screen[:, 1] ** 2)
    theta = ftheta_distortion(view_params["ftheta"], r)
    max_fov = math.radians(view_params["ftheta"]["max_fov"] / 2)
    direction, _extent = _fish_eye_map_to_sphere(screen, r, theta, max_fov)
    position_cam = direction * distance[..., np.newaxis]
    position_world = np.pad(position_cam, ((0, 0), (0, 1)), constant_values=1) @ view_params["view_to_world"]
    return position_world[:, :3]


def image_to_world(image_coordinates, view_params, distance):
    """Map each image coordinate to a corresponding direction vector.
    Args:
        pixel (numpy.ndarray): Pixel coordinates of shape (num_pixels, 2) normalized between -1 and 1
        view_params (dict): dictionary containing view parameters
    Returns
        (numpy.ndarray): Direction vectors of shape (num_pixels, 3)
    """
    projection_type = view_params["projection_type"]
    if projection_type == "pinhole":
        return project_pinhole(image_coordinates, view_params, distance)
    elif projection_type == "fisheyePolynomial":
        return fish_eye_polynomial(image_coordinates, view_params, distance)
    else:
        raise NotImplementedError(f"Camera projection type {projection_type} is not supported.")


# ======================================================================
class OgnCameraRelativePosition:
    @staticmethod
    def compute(db) -> bool:
        hori_location = db.inputs.horizontalLocation
        vert_location = db.inputs.verticalLocation
        distance = db.inputs.distance

        camera_prim_path = db.inputs.cameraPrim

        if camera_prim_path:
            camera_prim_path = camera_prim_path[0]
        else:
            db.outputs.execOut = og.ExecutionAttributeState.DISABLED
            return False

        width = db.inputs.width
        height = db.inputs.height

        view_params = get_view_params(camera_prim_path, width, height)

        if view_params["projection_type"] is None:
            db.outputs.execOut = og.ExecutionAttributeState.DISABLED
            return False

        position_world = image_to_world(np.stack([hori_location, vert_location], 1), view_params, distance)

        db.outputs.samples = position_world.tolist()
        db.outputs.execOut = og.ExecutionAttributeState.ENABLED
