# Copyright (c) 2021-2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = ["ViewportMenuSpacer"]

from typing import Dict

import omni.ui as ui

from .viewport_menu_item import ViewportMenuItem


class ViewportMenuSpacer(ViewportMenuItem):
    """A simple spacer in viewport menu bar"""
    def __init__(self):
        """Constructor"""
        self.__spacer: Dict[int, ui.Spacer] = {}
        super().__init__(order_setting_path="/exts/omni.kit.viewport.menubar.core/spacer/order")

    def build_fn(self, factory_args: Dict):
        """
        BUild a simple spacer.

        Args:
            factory_args (dict): Argument related to viewport.
        """
        viewport_api_id = factory_args['viewport_api'].id
        self.__spacer[viewport_api_id] = ui.Spacer()

    def get_computed_width(self, factory_args: Dict) -> float:
        """Retrieve the spacer computed width"""
        viewport_api_id = factory_args['viewport_api'].id
        return self.__spacer[viewport_api_id].computed_width if viewport_api_id in self.__spacer else 0
