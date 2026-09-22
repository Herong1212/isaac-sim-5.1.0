# Copyright (c) 2021-2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

__all__ = ['SelectionManipulatorItem']

from typing import Sequence
import omni.usd
from omni.kit.manipulator.selection import SelectionManipulator, SelectionMode


class SelectionManipulatorItem:
    def __init__(self, desc: dict, *args, **kwargs):
        self.__viewport_api = desc.get('viewport_api')
        self.__manipulator = SelectionManipulator()
        model = self.__manipulator.model
        self.__model_changed_sub = model.subscribe_item_changed_fn(self.__model_changed)
        self.__initial_selection = None
        self.__selection_args = None

    def __reset_state(self) -> None:
        self.__initial_selection = None
        self.__selection_args = None

    def __handle_selection(self, model, ndc_rect, mode, viewport_api):
        # Attempt to support live-selection for add and invert modes
        # usd_context = viewport_api.usd_context
        # if not self.__initial_selection:
        #     # Save the initial selection
        #     self.__initial_selection = usd_context.get_selection().get_selected_prim_paths()
        # elif mode != omni.usd.PickingMode.RESET_AND_SELECT:
        #     # Restore the initial selection so that add & invert do the right thing
        #     usd_context.get_selection().set_selected_prim_paths(self.__initial_selection, True)

        # Map the NDC screen coordinates into texture space
        box_start, start_in = viewport_api.map_ndc_to_texture_pixel((ndc_rect[0], ndc_rect[1]))  # noqa PLW0612
        box_end, end_in = viewport_api.map_ndc_to_texture_pixel((ndc_rect[2], ndc_rect[3]))  # noqa PLW0612
        # Clamp selection box to texture in pixel-space
        resolution = viewport_api.resolution
        box_start = (max(0, min(resolution[0], box_start[0])), max(0, min(resolution[1], box_start[1])))
        box_end = (max(0, min(resolution[0], box_end[0])), max(0, min(resolution[1], box_end[1])))
        # If the selection box overlaps the Viewport, save the state; otherwise clear it
        if (box_start[0] < resolution[0]) and (box_end[0] > 0) and (box_start[1] > 0) and (box_end[1] < resolution[1]):
            self.__selection_args = box_start, box_end, mode
        else:
            self.__selection_args = None

    def __request_pick(self) -> None:
        # If not selection state (pick is 100% outside of the viewport); clear the UsdContext's selection
        if self.__selection_args is None:
            usd_context = self.__viewport_api.usd_context
            if usd_context:
                usd_context.get_selection().set_selected_prim_paths([], False)
            return

        args = self.__selection_args
        if hasattr(self.__viewport_api, 'request_pick'):
            self.__viewport_api.request_pick(*args)
            return

        self.__viewport_api.pick(args[0][0], args[0][1], args[1][0], args[1][1], args[2])

    def __model_changed(self, model, item) -> None:
        # https://gitlab-master.nvidia.com/omniverse/kit/-/merge_requests/13725
        if not hasattr(omni.usd, 'PickingMode'):
            import carb
            carb.log_error('No picking support in omni.hydratexture')
            return None

        # We only care about rect and mode changes
        if item != model.get_item('ndc_rect') and item != model.get_item('mode'):
            return None

        live_select = False
        ndc_rect = model.get_as_floats('ndc_rect')
        if not ndc_rect:
            if not live_select:
                self.__request_pick()
            return self.__reset_state()

        # Convert the mode into an omni.usd.PickingMode
        mode = model.get_as_ints('mode')
        if not mode:
            return self.__reset_state()
        mode = {
            SelectionMode.REPLACE: omni.usd.PickingMode.RESET_AND_SELECT,
            SelectionMode.APPEND: omni.usd.PickingMode.MERGE_SELECTION,
            SelectionMode.REMOVE: omni.usd.PickingMode.INVERT_SELECTION
        }.get(mode[0], None)
        if mode is None:
            return self.__reset_state()

        self.__handle_selection(model, ndc_rect, mode, self.__viewport_api)

        # For reset selection, we can live-select as the drag occurs
        # live_select = mode == omni.usd.PickingMode.RESET_AND_SELECT
        if live_select:
            self.__request_pick()

        return None

    def destroy(self):
        self.__model_changed_sub = None
        self.__manipulator = None
        self.__viewport_api = None

    @property
    def categories(self) -> Sequence:
        return ("manipulator",)

    @property
    def name(self) -> str:
        return "Selection"

    @property
    def visible(self) -> bool:
        return self.__manipulator.visible

    @visible.setter
    def visible(self, value: bool):
        self.__manipulator.visible = bool(value)
