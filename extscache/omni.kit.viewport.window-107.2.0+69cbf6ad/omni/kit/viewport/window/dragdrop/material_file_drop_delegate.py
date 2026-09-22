# Copyright (c) 2021-2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

__all__ = ['MaterialFileDropDelegate']

import os
import asyncio
from typing import List

import carb
from pxr import Sdf, Usd, UsdGeom
from .usd_prim_drop_delegate import UsdShadeDropDelegate


class MaterialFileDropDelegate(UsdShadeDropDelegate):
    def __init__(self, preview_setting: str = None, show_alert: bool = True, **kwargs):
        super().__init__(**kwargs)
        self.__mdl_future = None
        self.__show_alert = show_alert

    @property
    def honor_picking_mode(self):
        return True

    # Method to allow subclassers to test url and keep all other default behavior
    def accept_url(self, url: str) -> str:
        # Early out for protocols not understood
        if super().is_ignored_protocol(url):
            return False

        if super().is_ignored_extension(url):
            return False

        # Validate it's a USD file and there is a Stage or UsdContet to use
        _, ext = os.path.splitext(url)
        if ext not in ['.mdl']:
            return False

        return url

    def reset_state(self) -> None:
        self.__mdl_future = None
        super().reset_state()

    def accepted(self, drop_data: dict) -> bool:

        # Reset state (base-class implemented)
        self.reset_state()

        # Validate there is a UsdContext and Usd.Stage
        usd_context, _ = self.get_context_and_stage(drop_data)
        if not usd_context:
            return False

        # Test if this url should be accepted
        url = self.get_url(drop_data)
        url = self.accept_url(url)
        if (url is None) or (not url):
            return False

        # Queue any remote MDL parsing
        try:
            import omni.kit.material.library
            asyncio.ensure_future(omni.kit.material.library.get_subidentifier_from_mdl(mdl_file=url, show_alert=False))
        except ImportError:
            carb.log_error("Cannot import materials as omni.kit.material.library isn't loaded")

        return True

    def get_material_prim_location(self, stage: Usd.Stage) -> Sdf.Path:
        # Place material at /Looks under root or defaultPrim
        if stage.HasDefaultPrim():
            looks_path = stage.GetDefaultPrim().GetPath()
        else:
            looks_path = Sdf.Path.absoluteRootPath
        return looks_path.AppendChild('Looks')

    def get_material_name(self, url: str, need_result: bool) -> List[str]:
        try:
            import omni.kit.material.library

            # Get the material subid's
            subid_list = []

            def have_subids(id_list):
                nonlocal subid_list
                subid_list = id_list

            asyncio.get_event_loop().run_until_complete(omni.kit.material.library.get_subidentifier_from_mdl(mdl_file=url, on_complete_fn=have_subids, show_alert=self.__show_alert))

            # covert from SubIDEntry to str
            return [subid.name for subid in subid_list]
        except ImportError:
            carb.log_error("Cannot import materials as omni.kit.material.library isn't loaded")

        return []

    def dropped(self, drop_data: dict):
        # Validate there is still a UsdContext and Usd.Stage
        _, stage = self.get_context_and_stage(drop_data)
        if stage is None:
            return

        url_path = self.accept_url(drop_data.get('mime_data'))
        if (url_path is None) or (not url_path):
            return

        try:
            import omni.usd
            import omni.kit.commands

            omni.kit.undo.begin_group()

            looks_path = self.get_material_prim_location(stage)
            looks_prim = stage.GetPrimAtPath(looks_path)
            looks_prim_valid = looks_prim.IsValid()
            if (not looks_prim_valid) or (not UsdGeom.Scope(looks_prim)):
                if looks_prim_valid:
                    looks_path = omni.usd.get_stage_next_free_path(stage, looks_path, False)
                    looks_path = Sdf.Path(looks_path)
                omni.kit.commands.execute('CreatePrimCommand', prim_path=looks_path, prim_type='Scope', select_new_prim=False, context_name=drop_data.get('usd_context_name') or '')

            dropped_onto = drop_data.get('prim_path')

            dropped_onto_model = drop_data.get('model_path')

            mtl_name = self.get_material_name(url_path, True)
            num_materials = len(mtl_name) if mtl_name else 0
            if num_materials < 1:
                carb.log_warn(f'Could not get material name from "{url_path}"')
                return

            material_prim = self.make_prim_path(stage, url_path, looks_path, mtl_name[0])
            if material_prim is None:
                return

            try:
                from omni.kit.material.library import custom_material_dialog, multi_descendents_dialog

                if dropped_onto or dropped_onto_model:
                    # Dropped onto a Prim, use multi_descendents_dialog to choose subset or prim
                    def multi_descendent_chosen(prim_path):
                        if num_materials > 1:
                            custom_material_dialog(mdl_path=url_path, bind_prim_paths=[prim_path])
                        else:
                            with omni.kit.undo.group():
                                omni.kit.commands.execute('CreateMdlMaterialPrimCommand', mtl_url=url_path, mtl_name=mtl_name[0], mtl_path=material_prim, select_new_prim=False)
                                omni.kit.commands.execute('BindMaterialCommand', prim_path=prim_path, material_path=material_prim, strength=self.binding_strength)

                    multi_descendents_dialog(prim_paths=[dropped_onto_model if dropped_onto_model else dropped_onto], on_click_fn=multi_descendent_chosen)
                elif num_materials > 1:
                    # Get the sub-material required
                    custom_material_dialog(mdl_path=url_path, bind_prim_paths=[dropped_onto])
                else:
                    # One sub-material, not dropped onto a Prim, just create the material
                    omni.kit.commands.execute('CreateMdlMaterialPrimCommand', mtl_url=url_path, mtl_name=mtl_name[0], mtl_path=material_prim, select_new_prim=False)
                return
            except ImportError:
                pass

            # Fallback to UsdShadeDropDelegate.handle_prim_drop
            # Need to create the material first
            omni.kit.commands.execute('CreateMdlMaterialPrimCommand', mtl_url=url_path, mtl_name=mtl_name[0], mtl_path=material_prim, select_new_prim=False)
            material_prim = stage.GetPrimAtPath(material_prim)
            if not material_prim.IsValid():
                raise RuntimeError(f'Could not create material {material_prim} for "{url_path}"')

            # If the material was dropped onto nothing, its been created so done
            if not dropped_onto:
                return

            # handle_prim_drop expects Usd.Prims, not paths
            dropped_onto = stage.GetPrimAtPath(dropped_onto)
            dropped_onto_model = stage.GetPrimAtPath(dropped_onto_model) if dropped_onto_model else None

            self.handle_prim_drop(stage, material_prim, dropped_onto, dropped_onto_model)
        except Exception:  # noqa PLW0718
            import traceback
            carb.log_error(traceback.format_exc())
        finally:
            omni.kit.undo.end_group()
