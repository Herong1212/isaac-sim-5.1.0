# Copyright (c) 2021-2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

__all__ = ['DragDropHandler']

from cmath import isfinite
import traceback
from typing import Sequence

from pxr import Usd, UsdGeom, Sdf, Kind

import carb
import omni.ui as ui

from .delegate import DragDropDelegate
from ..raycast import perform_raycast_query


class DragDropHandler:
    @staticmethod
    def picking_mode():
        mode = carb.settings.get_settings().get('/persistent/app/viewport/pickingMode')
        return mode or 'models'  # 'models' is equivalent to 'kind:model.ALL'

    @staticmethod
    def drag_drop_colors():
        try:
            # Use the selection-outline color or the color below it for selection differentiation
            outline_colors = carb.settings.get_settings().get('/persistent/app/viewport/outline/color')
            if outline_colors and len(outline_colors) >= 4:
                locator_color = None
                outline_color = (outline_colors[-4], outline_colors[-3], outline_colors[-2], outline_colors[-1])
                if len(outline_colors) >= 8:
                    secondary_lcolor = carb.settings.get_settings().get('/app/viewport/dragdrop/useSecondaryColorLocator')
                    secondary_ocolor = carb.settings.get_settings().get('/app/viewport/dragdrop/useSecondaryColorOutline')
                    if secondary_lcolor:
                        locator_color = (outline_colors[-8], outline_colors[-7], outline_colors[-6], outline_colors[-5])
                    elif secondary_ocolor:
                        locator_color = outline_color
                    if secondary_ocolor:
                        outline_color = (outline_colors[-8], outline_colors[-7], outline_colors[-6], outline_colors[-5])
                return outline_color, locator_color or outline_color
        except Exception:  # noqa PLW0718
            carb.log_error(f'Traceback:\n{traceback.format_exc()}')

        return (1.0, 0.6, 0.0, 1.0), (1.0, 0.6, 0.0, 1.0)

    def get_enclosing_model(self, prim_path: str):
        stage = self.viewport_api.stage
        if stage:
            kind_reg = Kind.Registry()
            prim = stage.GetPrimAtPath(prim_path)
            while prim:
                model = Usd.ModelAPI(prim)
                kind = model and model.GetKind()
                if kind and kind_reg.IsA(kind, Kind.Tokens.model):
                    return prim.GetPath()
                prim = prim.GetParent()
        return None

    def __init__(self, payload: dict):
        self.__valid_drops = None
        self.__add_outline = False
        self.__payload = payload or {}
        self.__payload['mime_data'] = None
        self.__payload['usd_context_name'] = self.viewport_api.usd_context_name
        self.__last_prim_path = Sdf.Path()
        self.__dropped = False
        colors = self.drag_drop_colors()
        self.__payload['outline_color'] = colors[0]
        self.__payload['locator_color'] = colors[1]
        self.__last_prim_collection = set()
        self.setup_outline(colors[0])

    @property
    def viewport_api(self):
        return self.__payload['viewport_api']

    def setup_outline(self, outline_color: Sequence[float], shade_color: Sequence[float] = (0, 0, 0, 0), sel_group: int = 254):
        self.__sel_group = sel_group
        usd_context = self.viewport_api.usd_context
        self.__selected_prims = set(usd_context.get_selection().get_selected_prim_paths())
        usd_context.set_selection_group_outline_color(sel_group, outline_color)
        usd_context.set_selection_group_shade_color(sel_group, shade_color)

    def __set_prim_outline(self, prim_path: Sdf.Path = None):
        if not self.__add_outline:
            return
        # Save the current prim for clering later and save off the previous prim locally
        last_prim_path, self.__last_prim_path = self.__last_prim_path, prim_path
        usd_context = self.viewport_api.usd_context
        new_path = prim_path != last_prim_path
        # Restore any previous
        if self.__dropped or new_path:
            for sdf_path in self.__last_prim_collection:
                usd_context.set_selection_group(0, sdf_path.pathString)
            self.__last_prim_collection = set()
        # If over a prim and not dropped, set the outline
        if prim_path and new_path:
            prim = usd_context.get_stage().GetPrimAtPath(prim_path)
            if prim.IsA(UsdGeom.Gprim):
                self.__last_prim_collection.add(prim_path)
            for cur_prim in Usd.PrimRange(prim, Usd.TraverseInstanceProxies(Usd.PrimAllPrimsPredicate)):
                if cur_prim.IsA(UsdGeom.Gprim):
                    self.__last_prim_collection.add(cur_prim.GetPath())
            for sdf_path in self.__last_prim_collection:
                usd_context.set_selection_group(self.__sel_group, sdf_path.pathString)

    def __query_complete(self, is_drop: bool, prim_path: str, world_space_pos: Sequence[float], *args):
        if prim_path:
            if not isfinite(world_space_pos[0]) or not isfinite(world_space_pos[1]) or not isfinite(world_space_pos[2]):
                # XXX: RTX is passing inf or nan in some cases...
                prim_path, world_space_pos = Sdf.Path(), (0, 0, 0)
            else:
                prim_path = Sdf.Path(prim_path)
        else:
            prim_path = Sdf.Path()

        updated_drop = []
        outline_path = prim_path
        pick_mode = self.picking_mode()
        model_path = None
        if prim_path and (pick_mode in ('kind:model.ALL', 'models')):
            for drop_obj in self.__valid_drops:
                instance = drop_obj[0]
                if hasattr(instance, 'honor_picking_mode') and instance.honor_picking_mode:
                    model_path = self.get_enclosing_model(prim_path)
                    outline_path = model_path or prim_path
                    break

        self.__set_prim_outline(outline_path)

        for drop_obj in self.__valid_drops:
            instance, drop_data = drop_obj
            drop_data['prim_path'] = prim_path
            drop_data['model_path'] = model_path
            drop_data['world_space_pos'] = world_space_pos
            drop_data['picking_mode'] = pick_mode
            # Update common ui data changed in _perform_query
            drop_data['pixel'] = self.__payload.get('pixel')
            drop_data['mouse_ndc'] = self.__payload.get('mouse_ndc')
            drop_data['viewport_ndc'] = self.__payload.get('viewport_ndc')
            try:
                if is_drop:
                    instance.dropped(drop_data)
                elif instance.update_drop_position(drop_data):
                    updated_drop.append((instance, drop_data))
            except Exception:  # noqa PLW0718
                carb.log_error(f'Traceback:\n{traceback.format_exc()}')

        # If it is a drop, then the action is done and clear any cached data
        # otherwise store the updated list of valid drops
        self.__valid_drops = None if is_drop else updated_drop

    def _perform_query(self, ui_obj: ui.Widget, mouse: Sequence[float], is_drop: bool = False):
        if not self.__valid_drops:
            return
        viewport_api = self.viewport_api
        if not viewport_api:
            return
        # Move from screen to local space
        mouse = (mouse[0] - ui_obj.screen_position_x, mouse[1] - ui_obj.screen_position_y)
        # Move from ui to normalized space (0-1)
        mouse = (mouse[0] / ui_obj.computed_width, mouse[1] / ui_obj.computed_height)
        # Move from normalized space to normalized device space (-1, 1)
        mouse = ((mouse[0] - 0.5) * 2.0, (mouse[1] - 0.5) * -2.0)
        self.__payload['mouse_ndc'] = mouse
        mouse, valid = viewport_api.map_ndc_to_texture_pixel(mouse)
        resolution = viewport_api.resolution
        vp_ndc = (mouse[0] / resolution[0], mouse[1] / resolution[1])
        vp_ndc = ((vp_ndc[0] - 0.5) * 2.0, (vp_ndc[1] - 0.5) * -2.0)
        self.__payload['pixel'] = mouse
        self.__payload['viewport_ndc'] = vp_ndc

        if valid and viewport_api.stage:
            perform_raycast_query(
                viewport_api=viewport_api,
                mouse_ndc=self.__payload['mouse_ndc'],
                mouse_pixel=mouse,
                on_complete_fn=lambda *args: self.__query_complete(is_drop, *args),
                query_name='omni.kit.viewport.dragdrop.DragDropHandler'
            )
        else:
            self.__query_complete(is_drop, '', (0, 0, 0))

    def accepted(self, ui_obj: ui.Widget, url_data: str):
        self.__dropped = False
        self.__valid_drops = None
        add_outline = False
        drops = []
        for instance in DragDropDelegate.get_instances():
            for url in url_data.splitlines():
                try:
                    # Copy the master payload so no delegates can change it
                    payload = self.__payload.copy()
                    # Push current url into the local payload
                    payload['mime_data'] = url
                    if instance.accepted(payload):
                        drops.append((instance, payload))
                        add_outline = add_outline or instance.add_outline
                except Exception:  # noqa PLW0718
                    carb.log_error(f'Traceback:\n{traceback.format_exc()}')

        if drops:
            self.__valid_drops = drops
            self.__add_outline = add_outline
            # Save this for comparison later (mime_data should be constant across the drg-drop event)
            self.__payload['accepted_mime_data'] = url_data
            return True

        return False

    def dropped(self, ui_obj: ui.Widget, event: ui._ui.WidgetMouseDropEvent):
        # Save this off now
        if self.__payload.get('accepted_mime_data') != event.mime_data:
            carb.log_error(
                "Mime data changed between accepeted and dropped\n"
                + f" accepted: {self.__payload.get('accepted_mime_data')}\n"
                + f"  dropped: {event.mime_data}"
            )
            return

        self.__dropped = True
        self._perform_query(ui_obj, (event.x, event.y), True)

    def cancel(self, ui_obj: ui.Widget):
        prev_drops, self.__valid_drops = self.__valid_drops, []
        self.__set_prim_outline()
        for drop_obj in prev_drops:
            try:
                drop_obj[0].cancel(drop_obj[1])
            except Exception:  # noqa PLW0718
                carb.log_error(f'Traceback:\n{traceback.format_exc()}')
