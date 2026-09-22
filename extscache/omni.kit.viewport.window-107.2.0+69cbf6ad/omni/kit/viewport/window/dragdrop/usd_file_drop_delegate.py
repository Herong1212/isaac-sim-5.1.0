# Copyright (c) 2021-2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

__all__ = ['UsdFileDropDelegate']

import os
from pxr import Gf, Sdf, Usd, UsdGeom

import carb
import omni.usd
import omni.kit.commands

from .scene_drop_delegate import SceneDropDelegate


class UsdFileDropDelegate(SceneDropDelegate):
    def __init__(self, preview_setting: str = None, **kwargs):
        super().__init__(**kwargs)
        self.__drag_to_open = False
        self.__world_space_pos = None
        self.__alternate_drop_marker = False
        self.__pickable_collection = None
        self.__preview_setting = preview_setting

    # Method to allow subclassers to test url and keep all other default behavior
    def ignore_url(self, url: str):
        # Validate it's a USD file and there is a Stage or UsdContet to use
        if not omni.usd.is_usd_readable_filetype(url):
            return True

        # Early out for other .usda handlers that claim the protocol
        if super().is_ignored_protocol(url):
            return True

        if super().is_ignored_extension(url):
            return True

        return False

    # Test if the drop should do a full preview or just a cross-hair
    def drop_should_disable_preview(self):
        # The case with no Usd.Stage in the UsdContext, cannot preview anything
        if self.__drag_to_open:
            return True
        # Test if there is a seting holding whether to preview or not, and invert it
        if self.__preview_setting:
            return not bool(carb.settings.get_settings().get(self.__preview_setting))
        return False

    # Subclasses can override to provide a different -alternate- behavior. Default is to fallback to crosshairs
    def add_alternate_drop_marker(self, drop_data: dict, world_space_pos: Gf.Vec3d):
        self.__alternate_drop_marker = True
        self.__world_space_pos = world_space_pos
        super().add_drop_marker(drop_data, world_space_pos)

    # Subclasses can override to clean out their -alternate- behavior.
    def remove_alternate_drop_marker(self, drop_data: dict):
        if self.__alternate_drop_marker:
            self.__world_space_pos = None
            super().remove_drop_marker(drop_data)

    def reset_state(self):
        self.__pickable_collection = None
        return super().reset_state()

    def accepted(self, drop_data: dict):
        # Reset self's state
        self.__drag_to_open = False
        self.__world_space_pos = None
        # Reset super's state
        self.reset_state()

        url = self.get_url(drop_data)
        if self.ignore_url(url):
            return False

        usd_context, stage = self.get_context_and_stage(drop_data)
        if not usd_context:
            return False

        try:
            import omni.kit.window.file  # noqa F401
        except ImportError:
            carb.log_warn('omni.kit.window.file must be present to drop and load a USD file without a stage')
            return False

        # Validate not dropping a cyclical reference
        if stage:
            root_layer = stage.GetRootLayer()
            if url == self.normalize_sdf_path(root_layer.realPath):
                return False
        else:
            self.__drag_to_open = True
        return True

    def add_drop_marker(self, drop_data: dict, world_space_pos: Gf.Vec3d):
        # Try and add the USD reference, this will invoke super.add_drop_marker
        # In the case it can't be accomplished, fallback to an alternate marker.
        usd_prim_droped = drop_data.get('usd_prim_droped')
        if usd_prim_droped is None:
            if self.drop_should_disable_preview():
                self.add_alternate_drop_marker(drop_data, world_space_pos)
                return
            if self.__alternate_drop_marker:
                self.remove_alternate_drop_marker(drop_data)

            usd_prim_droped = self.add_usd_drop_marker(drop_data, world_space_pos, True)
            if usd_prim_droped is None:
                return
            drop_data['usd_prim_droped'] = usd_prim_droped
        elif self.drop_should_disable_preview():
            # If preview was diabled mid-drag, undo the reference operation and add simple cross-hairs
            self.remove_drop_marker(drop_data)
            self.add_alternate_drop_marker(drop_data, world_space_pos)
            return

        # Constantly update the Prim's position, but avoid undo so that the reference/drop is what's undoable
        omni.kit.commands.create('TransformPrimSRTCommand', path=usd_prim_droped, new_translation=world_space_pos).do()
        self.update_pickability(drop_data, False)

    def update_pickability(self, drop_data: dict, pickable: bool):
        if self.__pickable_collection:
            usd_context, _ = self.get_context_and_stage(drop_data)
            for sdf_path in self.__pickable_collection:
                usd_context.set_pickable(sdf_path.pathString, pickable)

    def remove_drop_marker(self, drop_data: dict):
        # If usd_prim_droped is None, fallback to super which may have added cross-hair in no-stage case
        if drop_data.get('usd_prim_droped'):
            omni.kit.undo.undo()
            del drop_data['usd_prim_droped']
        self.remove_alternate_drop_marker(drop_data)

    def dropped(self, drop_data: dict):
        # If usd_prim_droped is None, but drop occured fallback to super which may have added cross-hair in no-stage case
        usd_prim_droped = drop_data.get('usd_prim_droped')
        if usd_prim_droped is not None:
            self.update_pickability(drop_data, True)
            self.__pickable_collection = None
        elif self.drop_should_disable_preview():
            super().remove_drop_marker(drop_data)
            if self.__drag_to_open:
                omni.kit.window.file.open_stage(self.get_url(drop_data).replace(os.sep, '/'))
            elif self.__world_space_pos:
                usd_prim_path = self.add_usd_drop_marker(drop_data, self.__world_space_pos)
                if usd_prim_path:
                    omni.kit.commands.create('TransformPrimSRTCommand', path=usd_prim_path, new_translation=self.__world_space_pos).do()

    def add_usd_drop_marker(self, drop_data: dict, world_space_pos: Gf.Vec3d, pickable_collection: bool = False):
        url = self.get_url(drop_data)
        # OMPE-37291: Check if crate file version is supported
        if omni.usd.is_usd_crate_file_version_supported(url) is False:
            return None

        usd_context, stage = self.get_context_and_stage(drop_data)
        sdf_layer = Sdf.Layer.FindOrOpen(url)
        if not sdf_layer:
            carb.log_warn(f'Could not get Sdf layer for {url}')
            return None

        if not sdf_layer.HasDefaultPrim():
            message = f"Cannot reference {url} as it has no default prim."
            try:
                import omni.kit.notification_manager as nm
                nm.post_notification(message, status=nm.NotificationStatus.WARNING)
            except ImportError:
                pass
            finally:
                carb.log_warn(message)
            return None

        new_prim_path, edit_context, relative_url = self.add_reference_to_stage(usd_context, stage, url)  # noqa PLW0612

        if pickable_collection:
            self.__pickable_collection = set()
            self.__pickable_collection.add(new_prim_path)
            for prim in Usd.PrimRange(usd_context.get_stage().GetPrimAtPath(new_prim_path), Usd.TraverseInstanceProxies(Usd.PrimAllPrimsPredicate)):
                if prim.IsA(UsdGeom.Gprim):
                    self.__pickable_collection.add(prim.GetPath())

        return new_prim_path
