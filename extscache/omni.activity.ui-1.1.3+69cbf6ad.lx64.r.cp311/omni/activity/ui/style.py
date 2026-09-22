# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = ["activity_window_style"]

from omni.ui import color as cl
from omni.ui import constant as fl
from omni.ui import url
import omni.kit.app
import omni.ui as ui
import pathlib


EXTENSION_FOLDER_PATH = pathlib.Path(
    omni.kit.app.get_app().get_extension_manager().get_extension_path_by_module(__name__)
)

# Pre-defined constants. It's possible to change them runtime.
cl.activity_window_attribute_bg = cl("#1f2124")
cl.activity_window_attribute_fg = cl("#0f1115")
cl.activity_window_hovered = cl("#FFFFFF")
cl.activity_text = cl("#9e9e9e")

cl.activity_green = cl("#4FA062")
cl.activity_usd_blue = cl("#2091D0")
cl.activity_progress_blue = cl("#4F7DA0")
cl.activity_purple = cl("#8A6592")
fl.activity_window_attr_hspacing = 10
fl.activity_window_attr_spacing = 1
fl.activity_window_group_spacing = 2

# The main style dict
activity_window_style = {
    "Label::attribute_name": {
        "alignment": ui.Alignment.RIGHT_CENTER,
        "margin_height": fl.activity_window_attr_spacing,
        "margin_width": fl.activity_window_attr_hspacing,
    },
    "Label::attribute_name:hovered": {"color": cl.activity_window_hovered},
    "Label::collapsable_name": {"alignment": ui.Alignment.LEFT_CENTER},
    "Label::time": {"font_size": 12, "color": cl.activity_text, "alignment": ui.Alignment.LEFT_CENTER},
    "Label::selection_time": {"font_size": 12, "color": cl("#34C7FF")},
    "Line::timeline": {"color": cl(0.22)},
    "Rectangle::selected_area": {"background_color": cl(1.0, 1.0, 1.0, 0.1)},
    "Slider::attribute_int:hovered": {"color": cl.activity_window_hovered},
    "Slider": {
        "background_color": cl.activity_window_attribute_bg,
        "draw_mode": ui.SliderDrawMode.HANDLE,
    },
    "Slider::attribute_float": {
        "draw_mode": ui.SliderDrawMode.FILLED,
        "secondary_color": cl.activity_window_attribute_fg,
    },
    "Slider::attribute_float:hovered": {"color": cl.activity_window_hovered},
    "Slider::attribute_vector:hovered": {"color": cl.activity_window_hovered},
    "Slider::attribute_color:hovered": {"color": cl.activity_window_hovered},
    "CollapsableFrame::group": {"margin_height": fl.activity_window_group_spacing},

    "Button::options": {"background_color": 0x0, "margin": 0},
    "Button.Image::options": {"image_url": f"{EXTENSION_FOLDER_PATH}/data/options.svg", "color": cl.activity_text},
    "RadioButton": {"background_color": cl.transparent},
    "RadioButton.Label": {"font_size": 14, "color": cl("#A1A1A1")},
    "RadioButton.Label:checked": {"font_size": 14, "color": cl("#34C7FF")},
    "RadioButton:checked": {"background_color": cl.transparent},
    "RadioButton:hovered": {"background_color": cl.transparent},
    "RadioButton:pressed": {"background_color": cl.transparent},
    "Rectangle::separator": {"background_color": cl("#707070"), "border_radius": 1.5},

    "TreeView.Label": {"color": cl.activity_text},
    "TreeView.Label.Right": {"color": cl.activity_text, "alignment": ui.Alignment.RIGHT_CENTER},

    "Rectangle::spacer": {"background_color": cl("#1F2123")},
    "ScrollingFrame": {"background_color": cl("#1F2123")},

    "Label::USD": {"color": cl.activity_usd_blue},
    "Label::progress": {"color": cl.activity_progress_blue},
    "Label::material": {"color": cl.activity_purple},
    "Label::undefined": {"color": cl.activity_text},
    "Label::unfinished": {"color": cl.lightsalmon},

    "Icon::USD": {"image_url": f"{EXTENSION_FOLDER_PATH}/data/USD.svg"},
    "Icon::progress": {"image_url": f"{EXTENSION_FOLDER_PATH}/data/progress.svg", "color": cl.activity_progress_blue},
    "Icon::material": {"image_url": f"{EXTENSION_FOLDER_PATH}/data/Material.png"},
    "Icon::texture": {"image_url": f"{EXTENSION_FOLDER_PATH}/data/Texture.svg"},
    "Icon::file": {"image_url": f"{EXTENSION_FOLDER_PATH}/data/file.svg"},
}

progress_window_style = {
    "RadioButton": {"background_color": cl.transparent},
    "RadioButton.Label": {"font_size": 14, "color": cl("#A1A1A1")},
    "RadioButton.Label:checked": {"font_size": 14, "color": cl("#34C7FF")},
    "RadioButton:checked": {"background_color": cl.transparent},
    "RadioButton:hovered": {"background_color": cl.transparent},
    "RadioButton:pressed": {"background_color": cl.transparent},
    "Rectangle::separator": {"background_color": cl("#707070"), "border_radius": 1.5},
    "ProgressBar::texture": {"border_radius": 0, "color": cl.activity_green, "background_color": cl("#606060")},
    "ProgressBar::USD": {"border_radius": 0, "color": cl.activity_usd_blue, "background_color": cl("#606060")},
    "ProgressBar::material": {"border_radius": 0, "color": cl.activity_purple, "background_color": cl("#606060")},
    "ProgressBar::progress": {"border_radius": 0, "color": cl.activity_progress_blue, "background_color": cl("#606060"), "secondary_color": cl.transparent},

    "Button::options": {"background_color": 0x0, "margin": 0},
    "Button.Image::options": {"image_url": f"{EXTENSION_FOLDER_PATH}/data/options.svg", "color": cl.activity_text},

    "TreeView.Label": {"color": cl.activity_text},
    "TreeView.Label.Right": {"color": cl.activity_text, "alignment": ui.Alignment.RIGHT_CENTER},

    "Label::USD": {"color": cl.activity_usd_blue},
    "Label::progress": {"color": cl.activity_progress_blue},
    "Label::material": {"color": cl.activity_purple},
    "Label::undefined": {"color": cl.activity_text},
    "Label::unfinished": {"color": cl.lightsalmon},

    "ScrollingFrame": {"background_color": cl("#1F2123")},
    "Icon::USD": {"image_url": f"{EXTENSION_FOLDER_PATH}/data/USD.svg"},
    "Icon::progress": {"image_url": f"{EXTENSION_FOLDER_PATH}/data/progress.svg", "color": cl.activity_progress_blue},
    "Icon::material": {"image_url": f"{EXTENSION_FOLDER_PATH}/data/Material.png"},
    "Icon::texture": {"image_url": f"{EXTENSION_FOLDER_PATH}/data/Texture.svg"},
    "Icon::file": {"image_url": f"{EXTENSION_FOLDER_PATH}/data/file.svg"},
    "Tree.Branch::Minus": {"image_url": f"{EXTENSION_FOLDER_PATH}/data/Minus.svg", "color": cl("#707070")},
    "Tree.Branch::Plus": {"image_url": f"{EXTENSION_FOLDER_PATH}/data/Plus.svg", "color": cl("#707070")},
}


def get_shade_from_name(name: str):
    #---------------------------------------
    if name == "USD":
        return cl("#2091D0")
    elif name == "Read":
        return cl("#1A75A8")
    elif name == "Resolve":
        return cl("#16648F")
    elif name.endswith((".usd", ".usda", ".usdc", ".usdz")):
        return cl("#13567B")
    #---------------------------------------
    elif name == "Stage":
        return cl("#d43838")
    elif name.startswith("Opening"):
        return cl("#A12A2A")
    #---------------------------------------
    elif name == "Render Thread":
        return cl("#d98927")
    elif name == "Execute":
        return cl("#A2661E")
    elif name == "Post Sync":
        return cl("#626262")
    #----------------------------------------
    elif name == "Textures":
        return cl("#4FA062")
    elif name == "Load":
        return cl("#3C784A")
    elif name == "Queue":
        return cl("#31633D")
    elif name.endswith(".hdr"):
        return cl("#34A24E")
    elif name.endswith(".png"):
        return cl("#2E9146")
    elif name.endswith(".jpg") or name.endswith(".JPG"):
        return cl("#2B8741")
    elif name.endswith(".ovtex"):
        return cl("#287F3D")
    elif name.endswith(".dds"):
        return cl("#257639")
    elif name.endswith(".exr"):
        return cl("#236E35")
    elif name.endswith(".wav"):
        return cl("#216631")
    elif name.endswith(".tga"):
        return cl("#1F5F2D")
    #---------------------------------------------
    elif name == "Materials":
        return cl("#8A6592")
    elif name.endswith(".mdl"):
        return cl("#76567D")
    elif "instance)" in name:
        return cl("#694D6F")
    elif name == "Compile":
        return cl("#5D4462")
    elif name == "Create Shader Variations":
        return cl("#533D58")
    elif name == "Load Textures":
        return cl("#4A374F")
    #---------------------------------------------
    elif name == "Meshes":
        return cl("#626262")
    #---------------------------------------------
    elif name == "Ray Tracing Pipeline":
        return cl("#8B8000")
    else:
        return cl("#555555")
