# Copyright (c) 2021-2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

__all__ = ['create_drop_helper']

from typing import Callable

from .delegate import DragDropDelegate


class _LegacyDragDropObject(DragDropDelegate):
    def __init__(self, add_outline: bool, test_accepted_fn: Callable, drop_fn: Callable, pick_complete: Callable):
        super().__init__()
        self.__add_outline = add_outline
        self.__test_accepted_fn = test_accepted_fn
        self.__dropped = drop_fn
        self.__pick_complete = pick_complete

    @property
    def add_outline(self):
        return self.__add_outline

    def accepted(self, drop_data: dict):
        url = drop_data['mime_data']
        return self.__test_accepted_fn(url) if self.__test_accepted_fn else False

    def dropped(self, drop_data: dict):
        url = drop_data['mime_data']
        if (self.__dropped is not None) and url and self.accepted(drop_data):
            prim_path = drop_data.get('prim_path')
            prim_path = prim_path.pathString if prim_path else ''
            usd_context_name = drop_data.get('usd_context_name', '')
            payload = self.__dropped(url, prim_path, '', usd_context_name)
            if payload and self.__pick_complete:
                self.__pick_complete(payload, prim_path, usd_context_name)


def create_drop_helper(pickable: bool = False, add_outline: bool = True, on_drop_accepted_fn: Callable = None, on_drop_fn: Callable = None, on_pick_fn: Callable = None):
    """Add a viewport drop handler.

    Args:
        pickable (bool): Deprecated, use on_pick_fn to signal you want picking.
        add_outline (False): True to add outline to picked prim when dropping.
        on_drop_accepted_fn (Callable): Callback function to check if drop helper could handle the dragging payload.
                                        Return True if payload accepted by this drop helper and will handle dropping later.
    Args:
        url (str): url in the payload.
        on_drop_fn (Callable): Callback function to handle dropping. Return a payload that evaluates to True in order to block other drop handlers.
    Args:
        url (str): url in the payload.
        target (str): picked prim path to drop.
        viewport_name (str): name of viewport window.
        usd_context_name (str): name of dropping usd context.
        on_pick_fn (Callable): Callback function to handle pick.
    Args:
        payload (Any): Return value from from on_drop_fn.
        target (str): picked prim path.
        usd_context_name (str): name of picked usd context.
    """
    if pickable:
        import carb
        carb.log_warn('pickable argument to create_drop_helper is deprecated, use on_pick_fn')
    return _LegacyDragDropObject(add_outline, on_drop_accepted_fn, on_drop_fn, on_pick_fn)
