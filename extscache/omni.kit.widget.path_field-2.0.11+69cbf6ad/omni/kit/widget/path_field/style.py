# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
import omni.ui as ui


UI_STYLES = {}

UI_STYLES["NvidiaLight"] = {
    "Window": {"secondary_background_color": 0},
    "ScrollingFrame": {"background_color": 0xFF535354, "margin": 0, "padding": 0},
    "Rectangle": {"background_color": 0xFF535354},
    "InputField": {"background_color": 0xFF535354, "color": 0xFFD6D6D6, "padding": 0},
    "BreadCrumb": {"background_color": 0x0, "padding": 0},
    "BreadCrumb.Label": {"color": 0xFFD6D6D6},
    "BreadCrumb:hovered": {"background_color": 0xFFCFCCBF},
    "BreadCrumb.Label:hovered": {"color": 0xFF2A2825},
    "BreadCrumb:selected": {"background_color": 0xFF535354},
    "Tooltips.Menu": {"background_color": 0xFFE0E0E0, "border_color": 0xFFE0E0E0, "border_width": 0.5},
    "Tooltips.Item": {"background_color": 0xFF535354, "padding": 4},
    "Tooltips.Item:hovered": {"background_color": 0xFF6E6E6E},
    "Tooltips.Item:checked": {"background_color": 0xFF6E6E6E},
    "Tooltips.Item.Label": {"color": 0xFFD6D6D6, "alignment": ui.Alignment.LEFT},
    "Tooltips.Spacer": {"background_color": 0x0, "color": 0x0, "alignment": ui.Alignment.LEFT, "padding": 0},
}

UI_STYLES["NvidiaDark"] = {
    "Window": {"secondary_background_color": 0},
    "ScrollingFrame": {"background_color": 0xFF23211F, "margin": 0, "padding": 0},
    "InputField": {"background_color": 0x0, "color": 0xFF9E9E9E, "padding": 0, "margin": 0},
    "BreadCrumb": {"background_color": 0x0, "padding": 0},
    "BreadCrumb:hovered": {"background_color": 0xFF8A8777},
    "BreadCrumb:selected": {"background_color": 0xFF8A8777},
    "BreadCrumb.Label": {"color": 0xFF9E9E9E},
    "BreadCrumb.Label:hovered": {"color": 0xFF2A2825},
    "Tooltips.Menu": {"background_color": 0xDD23211F, "border_color": 0xAA8A8777, "border_width": 0.5},
    "Tooltips.Item": {"background_color": 0x0, "padding": 4},
    "Tooltips.Item:hovered": {"background_color": 0xFF8A8777},
    "Tooltips.Item:checked": {"background_color": 0xFF8A8777},
    "Tooltips.Item.Label": {"color": 0xFF9E9E9E, "alignment": ui.Alignment.LEFT},
    "Tooltips.Item.Label:hovered": {"color": 0xFF2A2825},
    "Tooltips.Item.Label:checked": {"color": 0xFF2A2825},
    "Tooltips.Spacer": {
        "background_color": 0x0,
        "color": 0x0,
        "alignment": ui.Alignment.LEFT,
        "padding": 0,
        "margin": 0,
    },
}
