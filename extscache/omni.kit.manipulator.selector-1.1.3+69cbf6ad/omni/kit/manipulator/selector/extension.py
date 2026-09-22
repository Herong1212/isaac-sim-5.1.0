# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

from typing import Dict

import omni.ext

from .manipulator_order_manager import ManipulatorOrderManager
from .manipulator_selector import ManipulatorSelector

_selectors: Dict[str, ManipulatorSelector] = {}
_order_manager: ManipulatorOrderManager = None


# Each UsdContext has a ManipulatorSelector to subscribe to selection event
def get_manipulator_selector(usd_context_name: str) -> ManipulatorSelector:
    """
    Factory function that returns an instance of the ManipulatorSelector for a given usd context.

    Args:
        usd_context_name (str): The name of the USD context for which to return a ManipulatorSelector object.

    Returns:
        :obj: 'ManipulatorSelector'
    """
    global _selectors
    global _order_manager
    if usd_context_name not in _selectors:
        selector = ManipulatorSelector(_order_manager, usd_context_name)
        _selectors[usd_context_name] = selector
        return selector

    return _selectors[usd_context_name]


class ManipulatorPrim(omni.ext.IExt):
    def on_startup(self, ext_id):
        global _order_manager
        assert _order_manager is None
        _order_manager = ManipulatorOrderManager()

    def on_shutdown(self):
        global _selectors
        global _order_manager
        for selector in _selectors.values():
            selector.destroy()
        _selectors.clear()

        if _order_manager:
            _order_manager.destroy()
            _order_manager = None
