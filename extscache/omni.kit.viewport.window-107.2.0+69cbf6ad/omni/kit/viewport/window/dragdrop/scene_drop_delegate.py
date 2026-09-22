# Copyright (c) 2021-2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

__all__ = ['SceneDropDelegate']

import os
from typing import Tuple

from pxr import Gf, Sdf, Usd, UsdGeom

import carb
import omni.usd
import omni.ui as ui
from omni.ui import scene as sc

from .delegate import DragDropDelegate


class SceneDropDelegate(DragDropDelegate):
    # XXX: We know these have a meanining that we don't handle, so early out
    __g_ignore_protocols = {"sky::", "material::"}
    __g_ignore_extensions = set()

    @staticmethod
    def add_ignored_protocol(protocol: str):
        """Add a protocol that should be ignored by default file-handlers"""
        SceneDropDelegate.__g_ignore_protocols.add(protocol)

    @staticmethod
    def remove_ignored_protocol(protocol: str):
        """Remove a protocol that should be ignored by default file-handlers"""
        SceneDropDelegate.__g_ignore_protocols.discard(protocol)

    @staticmethod
    def add_ignored_extension(extension: str):
        """Add a file extension that should be ignored by default file-handlers"""
        SceneDropDelegate.__g_ignore_extensions.add(extension)

    @staticmethod
    def remove_ignored_extension(extension: str):
        """Remove a file extension that should no longer be ignored by default file-handlers"""
        SceneDropDelegate.__g_ignore_extensions.discard(extension)

    @staticmethod
    def is_ignored_protocol(url: str):
        """Early out for other protocol handlers that claim the format"""
        return any(url.startswith(protocol) for protocol in SceneDropDelegate.__g_ignore_protocols)

    @staticmethod
    def is_ignored_extension(url: str):
        """Early out for other extension handlers that claim the format"""
        return any(url.endswith(extension) for extension in SceneDropDelegate.__g_ignore_extensions)

    def __init__(self, *args, **kw_args):
        super().__init__(*args, **kw_args)
        self.__ndc_z = None
        self.__color = None
        self.__transform = None
        self.__xf_to_screen = None
        self.__max_plane_dist = 0

        try:
            max_plane_dist = carb.settings.get_settings().get("/exts/omni.kit.viewport.window/dragDrop/maxPlaneDistance")
            max_plane_dist = float(max_plane_dist)
            self.__max_plane_dist = max_plane_dist if max_plane_dist >= 0 else 0
        except ValueError:
            pass

    @property
    def add_outline(self) -> bool:
        return True

    @property
    def honor_picking_mode(self) -> bool:
        return False

    def reset_state(self):
        # Reset any previous cached drag-drop info
        self.__ndc_z = None
        self.__color = None

    def accepted(self, drop_data: dict):
        self.reset_state()
        return True

    def update_drop_position(self, drop_data: dict):
        self.__color = drop_data['locator_color']
        world_space_pos = self._get_world_position(drop_data)
        if world_space_pos:
            self.add_drop_marker(drop_data, world_space_pos)
        return True

    def dropped(self, drop_data: dict):
        self.remove_drop_marker(drop_data)

    def cancel(self, drop_data: dict):
        self.remove_drop_marker(drop_data)

    # Helper methods to inspect drop_data
    def get_url(self, drop_data: dict):
        return drop_data.get('mime_data')

    def get_context_and_stage(self, drop_data: dict):
        usd_context = omni.usd.get_context(drop_data['usd_context_name'])
        return (usd_context, usd_context.get_stage()) if usd_context else (None, None)

    @property
    def color(self):
        return self.__color

    def make_prim_path(self, stage: Usd.Stage, url: str, prim_path: Sdf.Path = None, prim_name: str = None):
        """Make a new/unique prim path for the given url"""
        if prim_path is None:
            if stage.HasDefaultPrim():
                prim_path = stage.GetDefaultPrim().GetPath()
            else:
                prim_path = Sdf.Path.absoluteRootPath

        if prim_name is None:
            prim_name = omni.usd.make_valid_identifier(os.path.basename(os.path.splitext(url)[0]))

        return Sdf.Path(omni.usd.get_stage_next_free_path(stage, prim_path.AppendChild(prim_name).pathString, False))

    def create_instanceable_reference(self, usd_context, stage: Usd.Stage, url: str, prim_path: str) -> bool:
        """Return whether to create the reference as instanceable=True"""
        return carb.settings.get_settings().get('/persistent/app/stage/instanceableOnCreatingReference')

    def create_as_payload(self, usd_context, stage: Usd.Stage, url: str, prim_path: str):
        """Return whether to create as a reference or payload"""
        dd_import = carb.settings.get_settings().get('/persistent/app/stage/dragDropImport')
        return dd_import == 'payload'

    def normalize_sdf_path(self, sdf_layer_path: str):
        return sdf_layer_path.replace('\\', '/')

    def make_relative_to_layer(self, stage: Usd.Stage, url: str) -> str:
        # XXX: PyBind omni::usd::UsdUtils::makePathRelativeToLayer
        stage_layer = stage.GetEditTarget().GetLayer()
        if not stage_layer.anonymous and not Sdf.Layer.IsAnonymousLayerIdentifier(url):
            stage_layer_path = stage_layer.realPath
            if self.normalize_sdf_path(stage_layer_path) == url:
                carb.log_warn(f'Cannot reference {url} onto itself')
                return ""
            relative_url = omni.client.make_relative_url(stage_layer_path, url)
            if relative_url:
                # omniverse path can have '\'
                return relative_url.replace('\\', '/')
        return url

    def add_reference_to_stage(self, usd_context, stage: Usd.Stage, url: str) -> Tuple[str, Usd.EditContext, str]:
        """Add a Usd.Prim to an exiting Usd.Stage, pointing to the url"""
        # Get a realtive URL if possible
        relative_url = self.make_relative_to_layer(stage, url)

        # When in auto authoring mode, don't create it in the current edit target
        # as it will be cleared each time to be moved to default edit layer.
        edit_context = None
        try:
            import omni.kit.usd.layers as layers
            layers_interface = layers.get_layers()
            if layers_interface.get_edit_mode() == layers.LayerEditMode.AUTO_AUTHORING:
                default_identifier = layers_interface.get_auto_authoring().get_default_layer()
                edit_layer = Sdf.Layer.Find(default_identifier)
                if edit_layer is None:
                    edit_layer = stage.GetRootLayer()
                edit_context = Usd.EditContext(stage, edit_layer)
        except ImportError:
            pass

        new_prim_path = self.make_prim_path(stage, url)
        instanceable = self.create_instanceable_reference(usd_context, stage, url, new_prim_path)
        as_payload = self.create_as_payload(usd_context, stage, url, new_prim_path)
        cmd_name = 'CreatePayloadCommand' if as_payload else 'CreateReferenceCommand'
        omni.kit.commands.execute(cmd_name, usd_context=usd_context, path_to=new_prim_path, asset_path=url, instanceable=instanceable)

        return (new_prim_path, edit_context, relative_url)

    # Meant to be overriden by subclasses to draw drop information
    # Default draws a cross-hair in omni.ui.scene
    def add_drop_shape(self, world_space_pos: Gf.Vec3d, scale: float = 50, thickness: float = 1, color: ui.color = None):
        self.__xf_to_screen = sc.Transform(scale_to=sc.Space.SCREEN)
        with self.__xf_to_screen:
            sc.Line((-scale, 0, 0), (scale, 0, 0), color=color, thickness=thickness)
            sc.Line((0, -scale, 0), (0, scale, 0), color=color, thickness=thickness)
            sc.Line((0, 0, -scale), (0, 0, scale), color=color, thickness=thickness)

    def add_drop_marker(self, drop_data: dict, world_space_pos: Gf.Vec3d):
        if not self.__transform:
            scene_view = drop_data['scene_view']
            if scene_view:
                with scene_view.scene:
                    self.__transform = sc.Transform()
                    with self.__transform:
                        self.add_drop_shape(world_space_pos, color=self.color)

        if self.__transform:
            self.__transform.transform = [
                1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0,
                world_space_pos[0], world_space_pos[1], world_space_pos[2], 1
            ]

        return self.__transform

    def remove_drop_marker(self, drop_data: dict):
        if self.__xf_to_screen:
            self.__xf_to_screen.clear()
            self.__xf_to_screen = None
        if self.__transform:
            self.__transform.clear()
            self.__transform = None

    # Semi and fully private methods
    def __cache_screen_ndc(self, viewport_api, world_space_pos: Gf.Vec3d):
        screen_space_pos = viewport_api.world_to_ndc.Transform(world_space_pos)
        self.__ndc_z = screen_space_pos[2]

    def _get_world_position_object(self, viewport_api, world_space_pos: Gf.Vec3d, drop_data: dict) -> Tuple[Gf.Vec3d, bool]:
        """Return a world-space position that is located between two objects as mouse is dragged over them"""
        success = False
        # If previosuly dragged over an object, use that as the depth to drop onto
        if self.__ndc_z is None:
            # Otherwise use the camera's center-of-interest as the depth
            camera = viewport_api.stage.GetPrimAtPath(viewport_api.camera_path)
            coi_attr = camera.GetAttribute('omni:kit:centerOfInterest')
            if coi_attr:
                world_space_pos = viewport_api.transform.Transform(coi_attr.Get(viewport_api.time))
                self.__cache_screen_ndc(viewport_api, world_space_pos)
        # If we have depth (in NDC), move (x_ndc, y_ndz, z_ndc) to a world-space position
        if self.__ndc_z is not None:
            success = True
            mouse_ndc = drop_data['mouse_ndc']
            world_space_pos = viewport_api.ndc_to_world.Transform(Gf.Vec3d(mouse_ndc[0], mouse_ndc[1], self.__ndc_z))

        return (world_space_pos, success)

    def _get_world_position_plane(self, viewport_api, world_space_pos: Gf.Vec3d, drop_data: dict, mode: str) -> Tuple[Gf.Vec3d, bool]:
        test_one_plane = False

        # User can specify plane to test against explicitly
        if mode == "z":
            up_axis, test_one_plane = UsdGeom.Tokens.z, True
        elif mode == "x":
            up_axis, test_one_plane = UsdGeom.Tokens.x, True
        elif mode == "y":
            up_axis, test_one_plane = UsdGeom.Tokens.y, True
        else:
            # Otherwise test against multiple planes unless mode is 'ground' (single plane test based on scene-up)
            up_axis, test_one_plane = UsdGeom.GetStageUpAxis(viewport_api.stage), mode == "ground"

        if up_axis == UsdGeom.Tokens.z:
            normals = (Gf.Vec3d(0, 0, 1), Gf.Vec3d(0, 1, 0), Gf.Vec3d(1, 0, 0))
        elif up_axis == UsdGeom.Tokens.x:
            normals = (Gf.Vec3d(1, 0, 0), Gf.Vec3d(0, 1, 0), Gf.Vec3d(0, 0, 1))
        else:
            normals = (Gf.Vec3d(0, 1, 0), Gf.Vec3d(0, 0, 1), Gf.Vec3d(1, 0, 0))

        def create_ray(projection: Gf.Matrix4d, view: Gf.Matrix4d, ndx_x: float, ndc_y: float, ndc_z: float = 0):
            pv_imatrix = (view * projection).GetInverse()
            origin = pv_imatrix.Transform(Gf.Vec3d(ndx_x, ndc_y, ndc_z))

            if projection[3][3] == 1:
                # Orthographic is simpler than perspective
                ray_dir = Gf.Vec3d(view[0][2], view[1][2], view[2][2])
            else:
                ray_dir = pv_imatrix.Transform(Gf.Vec3d(ndx_x, ndc_y, 0.5))
                ray_dir = Gf.Vec3d(ray_dir[0] - origin[0], ray_dir[1] - origin[1], ray_dir[2] - origin[2])

            return (origin, ray_dir.GetNormalized())

        def intersect_plane(normal: Gf.Vec3d, ray_orig: Gf.Vec3d, ray_dir: Gf.Vec3d, epsilon: float = 1e-5):
            denom = Gf.Dot(normal, ray_dir)
            if abs(denom) < epsilon:
                return (None, None)

            distance = Gf.Dot(-ray_orig, normal) / denom
            if distance < epsilon:
                return (None, None)

            return (ray_orig + ray_dir * distance, distance)

        # Build ray origin and direction from mouse NDC co-ordinates
        mouse_ndc = drop_data['mouse_ndc']
        ray_origin, ray_dir = create_ray(viewport_api.projection, viewport_api.view, mouse_ndc[0], mouse_ndc[1])

        # Try normal-0, any hit on that plane wins (the Stage's ground normal)
        plane0_pos, plane0_dist = intersect_plane(normals[0], ray_origin, ray_dir)

        # Check that the hit distance is within tolerance (or no tolerance specified)
        def distance_in_bounds(distance: float) -> bool:
            if self.__max_plane_dist > 0:
                return distance < self.__max_plane_dist
            return True

        # Return a successful hit (caching the screen-ndc in case mode fallsback/transitions to object)
        def return_valid_position(position: Gf.Vec3d):
            self.__cache_screen_ndc(viewport_api, position)
            return (position, True)

        # If the hit exists and is within the max allowed distance (or no max allowed distance) it wins
        if plane0_pos and distance_in_bounds(plane0_dist):
            return return_valid_position(plane0_pos)

        # If testing more than one plane
        if not test_one_plane:
            # Check if other planes were hit, and if so use the best/closests
            plane1_pos, plane1_dist = intersect_plane(normals[1], ray_origin, ray_dir)
            plane2_pos, plane2_dist = intersect_plane(normals[2], ray_origin, ray_dir)
            if plane1_pos and distance_in_bounds(plane1_dist):
                # plane-1 hit and valid, check if plane-2 also hit and valid and use closest of the two
                if plane2_pos and distance_in_bounds(plane2_dist) and (plane2_dist < plane1_dist):
                    return return_valid_position(plane2_pos)
                # Return plane-1, plane-2 was either invalid, further, or above tolerance
                return return_valid_position(plane1_pos)
            if plane2_pos and distance_in_bounds(plane2_dist):
                # Return plane-2 it is valid and within tolerance
                return return_valid_position(plane2_pos)

        # Nothing worked, return input and False
        return (world_space_pos, False)

    def _get_world_position(self, drop_data: dict) -> Gf.Vec3d:
        prim_path = drop_data['prim_path']
        viewport_api = drop_data['viewport_api']
        world_space_pos = drop_data['world_space_pos']
        if world_space_pos:
            world_space_pos = Gf.Vec3d(*world_space_pos)
        # If there is no prim-path, deliver a best guess at world-position
        if not prim_path and viewport_api.stage:
            success = False
            # Can change within a drag-drop operation via hotkey
            mode = carb.settings.get_settings().get("/exts/omni.kit.viewport.window/dragDrop/intersectMode") or ""
            if mode != "object":
                world_space_pos, success = self._get_world_position_plane(viewport_api, world_space_pos, drop_data, mode)
            if not success:
                world_space_pos, success = self._get_world_position_object(viewport_api, world_space_pos, drop_data)
        else:
            self.__cache_screen_ndc(viewport_api, world_space_pos)
        return world_space_pos
