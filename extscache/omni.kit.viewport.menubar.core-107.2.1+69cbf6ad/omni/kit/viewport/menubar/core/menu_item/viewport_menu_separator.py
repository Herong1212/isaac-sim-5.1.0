# Copyright (c) 2021-2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = ["ViewportMenuSeparator"]

from typing import Dict

import omni.ui as ui

from .viewport_menu_item import ViewportMenuItem


class ViewportMenuSeparator(ViewportMenuItem):
    """A simple separator in viewport menu bar"""

    def build_fn(self, factory_args: Dict):
        """
        Build a simple separator

        Args:
            factory_args (dict): Argument related to viewport.
        """
        ui.Separator(
            delegate=ui.MenuDelegate(
                on_build_item=lambda _: ui.Line(
                    height=0, alignment=ui.Alignment.V_CENTER, style_type_name_override="Menu.Separator"
                )
            )
        )
