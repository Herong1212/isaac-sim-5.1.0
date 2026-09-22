# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
"""This module defines UI styles and functions to retrieve style dictionaries for various UI components in the omni.kit.window.extensions package."""

__all__ = []

from functools import lru_cache
from typing import Dict

import carb
import omni.ui as ui
from omni.ui import color as cl

from .common import get_icons_path

# Common size constants:
EXT_ICON_SIZE = (70, 70)
EXT_ICON_SIZE_LARGE = (100, 100)
CATEGORY_ICON_SIZE = (70, 70)
EXT_LIST_ITEM_H = 106
EXT_LIST_ITEMS_MARGIN_H = 3
EXT_ITEM_TITLE_BAR_H = 27
EXT_LIST_ITEM_ICON_ZONE_W = 87


@lru_cache()
def get_styles() -> Dict:
    icons_path = get_icons_path()
    font_path = carb.tokens.get_tokens_interface().resolve("${omni.kit.window.extensions}/data/fonts")

    styles = {
        "ExtensionToggle": {
            "Image::Failed": {"image_url": f"{icons_path}/exclamation.svg", "color": 0xFF2222DD, "margin": 5},
            "Button": {"margin": 0, "padding": 0, "background_color": 0x0},
            "Button:checked": {"background_color": 0x0},
            "Button.Image::nonclickable": {"color": 0x60FFFFFF, "image_url": f"{icons_path}/toggle-off.svg"},
            "Button.Image::nonclickable:checked": {"color": 0x60FFFFFF, "image_url": f"{icons_path}/toggle-on.svg"},
            "Button.Image::clickable": {"image_url": f"{icons_path}/toggle-off.svg", "color": 0xFFFFFFFF},
            "Button.Image::clickable:checked": {"image_url": f"{icons_path}/toggle-on.svg"},
            "Label::EnabledLabel": {"font_size": 16, "color": 0xFF71A376},
            "Label::DisabledLabel": {"font_size": 16, "color": 0xFFB9B9B9},
            "Button::InstallButton": {"background_color": 0xFF00B976, "border_radius": 4},
            "Button::InstallButton:checked": {"background_color": 0xFF06A66B},
            "Button.Label::InstallButton": {"color": 0xFF3E3E3E, "font_size": 14},
            "Button::DownloadingButton": {"background_color": 0xFF008253, "border_radius": 4},
            "Button.Label::DownloadingButton": {"color": 0xFF3E3E3E, "font_size": 8},
            "Button::LaunchButton": {"background_color": 0xFF00B976, "border_radius": 4},
            "Button.Label::LaunchButton": {"color": 0xFF3E3E3E, "font_size": 14},
        },
        "SimpleCheckBox": {
            "Button": {"margin": 0, "padding": 0, "background_color": 0x0},
            "Button:hovered": {"background_color": 0x0},
            "Button:checked": {"background_color": 0x0},
            "Button:pressed": {"background_color": 0x0},
            "Button.Image": {"image_url": f"{icons_path}/checkbox-off.svg", "color": 0xFFA8A8A8},
            "Button.Image:hovered": {"color": 0xFF929292},
            "Button.Image:pressed": {"color": 0xFFA4A4A4},
            "Button.Image:checked": {"image_url": f"{icons_path}/checkbox-on.svg", "color": 0xFFA8A8A8},
            "Image::disabled_checked": {"image_url": f"{icons_path}/checkbox-on.svg", "color": 0x3FA8A8A8},
            "Image::disabled_unchecked": {"image_url": f"{icons_path}/checkbox-off.svg", "color": 0x3FA8A8A8},
            "Label::disabled": {"font_size": 12, "color": 0xFF444444},
            "Label": {"font_size": 16, "color": 0xFFC4C4C4},
        },
        "SearchWidget": {
            "SearchField": {
                "background_color": 0xFF212121,
                "color": 0xFFA2A2A2,
                "border_radius": 0,
                "font_size": 16,
                "margin": 0,
                "padding": 5,
            },
            "Image::SearchIcon": {"image_url": f"{icons_path}/search.svg", "color": 0xFF646464},
            "Label::Search": {"color": 0xFF646464},
            "Button.Image::ClearSearch": {
                "image_url": f"{icons_path}/close.svg",
                "color": 0xFF646464,
            },
            "Button.Image::ClearSearch:hovered": {
                "image_url": f"{icons_path}/close.svg",
                "color": 0xFF929292,
            },
            "Button.Image::ClearSearch:pressed": {
                "image_url": f"{icons_path}/close.svg",
                "color": 0xFFC4C4C4,
            },
            "Button::ClearSearch": {
                "margin": 0,
                "border_radius": 0,
                "border_width": 0,
                "padding": 3,
                "background_color": 0x00000000,
            },
            "Button::ClearSearch:hovered": {
                "background_color": 0x00000000,
            },
            "Button::ClearSearch:pressed": {
                "background_color": 0x00000000,
            },
        },
        "MarkdownText": {
            "Label": {"font_size": 16, "color": 0xFFCCCCCC},
            "Label::text": {"font_size": 16, "color": 0xFFCCCCCC},
            "Label::codeblock": {"font": f"{font_path}/RobotoMono-SemiBold.ttf", "font_size": 18, "color": 0xFFAAAAAA},
            "Label::H1": {"font_size": 32, "color": 0xFFCCCCCC},
            "Label::H2": {"font_size": 28, "color": 0xFFCCCCCC},
            "Label::H3": {"font_size": 24, "color": 0xFFCCCCCC},
            "Label::H4": {"font_size": 20, "color": 0xFFCCCCCC},
            "Label::H5": {"font_size": 20, "color": 0xFFCCCCCC},
            "Label::H6": {"font_size": 20, "color": 0xFFCCCCCC},
        },
        "ExtsWindow": {
            "ExtensionDescription.Button": {"background_color": 0xFF090969},
            "ExtensionDescription.Title": {"font_size": 18, "color": 0xFFCCCCCC, "margin": 5},
            "ExtensionDescription.Header": {"font_size": 20, "color": 0xFF409656},
            "ExtensionDescription.Content": {"font_size": 16, "color": 0xFFCCCCCC, "margin": 5},
            "ExtensionDescription.ContentError": {"font_size": 16, "color": 0xFF4056C6, "margin": 5},
            "ExtensionDescription.ContentValue": {"font_size": 16, "color": 0xFF409656},
            "ExtensionDescription.ContentLink": {"font_size": 16, "color": 0xFF82C994},
            "ExtensionDescription.ContentLink:hovered": {"color": 0xFFB8E0C2},
            "ExtensionDescription.DeprecatedTitle": {"font_size": 24, "color": ui.color(199, 123, 36), "margin": 5},
            "ExtensionDescription.DeprecatedBody": {"font_size": 18, "color": ui.color(199, 123, 36), "margin": 5},
            "ExtensionList.Label::Description": {"font_size": 16},
            "ExtensionList.Label::Name": {"font_size": 12},
            "ExtensionDescription.Background": {"background_color": 0xFF363636, "border_radius": 4},
            "ExtensionDescription.ContentBackground": {"background_color": 0xFF23211F},
            "ExtensionList.Background": {
                "background_color": 0xFF212121,
                "border_radius": 0,
                "corner_flag": ui.CornerFlag.BOTTOM,
            },
            "Rectangle::ExtensionListGroup": {
                "background_color": 0xFF303030,
            },
            "Rectangle::ExtensionListGroup:hovered": {
                "background_color": 0xFF404040,
            },
            "Rectangle::ExtensionListGroup:pressed": {
                "background_color": 0xFF303030,
            },
            "ExtensionList.Group.Label": {"font_size": 16, "color": 0xFFC0C0C0},
            "ExtensionList.Group.Icon::expanded": {"image_url": f"{icons_path}/expanded.svg"},
            "ExtensionList.Group.Icon": {"image_url": f"{icons_path}/collapsed.svg"},
            "ExtensionList.Separator": {"background_color": 0xFF000000},
            # "ExtensionList.Background:hovered": {"background_color": 0xFF191919},
            "ExtensionList.Background:selected": {"background_color": 0xFF8A8777},
            "ExtensionList.Foreground": {
                "background_color": 0xFF2F2F2F,
                "border_width": 0,
                "border_radius": 0,
                "corner_flag": ui.CornerFlag.BOTTOM_RIGHT,
            },
            "ExtensionList.Foreground:selected": {"background_color": 0xFF9F9B8A},
            "ExtensionList.Label": {
                "font_size": 16,
                "margin": 2,
                "color": ui.color(147, 147, 147),
            },
            "ExtensionList.Label::Title": {
                "font_size": 19,
            },
            "ExtensionList.Label::Title:selected": {
                "color": ui.color(218, 220, 221),
            },
            "ExtensionList.Label::Category": {"font_size": 16, "margin_width": 10},
            "ExtensionList.Label::Id": {"font_size": 16, "margin_width": 10},
            "ExtensionList.Label::Version": {
                "alignment": ui.Alignment.RIGHT_CENTER,
            },
            "TreeView": {
                "background_color": 0xFF23211F,
                "background_selected_color": 0xFF23211F,
                "secondary_color": 0xFF989898,  # Scroll knob
                "alignment": ui.Alignment.RIGHT,
                "margin_height": 4.0,
            },
            "TreeView.ScrollingFrame": {"background_color": 0xFF4A4A4A},
            "ComboBox": {
                "background_color": 0xFF212121,
                "border_radius": 0,
                "font_size": 16,
                "margin": 0,
                "color": 0xFF929292,
                "padding": 0,
            },
            "ComboBox:hovered": {"background_color": 0xFF2F2F2F},
            "ComboBox:selected": {"background_color": 0xFF2F2F2F},
            "ExtensionDescription.Label": {"color": 0xFFC4C4C4, "margin": 2, "font_size": 16},
            "ExtensionDescription.Id::Name": {"background_color": 0xFF000000, "color": 0xFFC4C4C4, "font_size": 14},
            "ExtensionDescription.Rectangle::Name": {"background_color": 0xFF24211F, "border_radius": 2},
            "ExtensionDescription.UpdateButton": {"background_color": 0xFF00B976, "border_radius": 4},
            "ExtensionDescription.UpdateButton.Label": {"color": 0xFF3E3E3E, "font_size": 18},
            "ExtensionDescription.RestartButton": {"background_color": 0xFF00B976, "border_radius": 4},
            "ExtensionDescription.RestartButton.Label": {"color": 0xFF3E3E3E, "font_size": 18},
            "ExtensionDescription.UpToDateButton": {"background_color": 0xFF747474, "border_radius": 4},
            "ExtensionDescription.UpToDateButton.Label": {"color": 0xFF3E3E3E, "font_size": 18},
            "ExtensionDescription.InstallButton": {"background_color": 0xFF00B976, "border_radius": 4},
            "ExtensionDescription.InstallButton.Label": {"color": 0xFF3E3E3E, "font_size": 18},
            "ExtensionDescription.DownloadingButton": {"background_color": 0xFF00754A, "border_radius": 4},
            "ExtensionDescription.DownloadingButton.Label": {"color": 0xFF3E3E3E, "font_size": 18},
            "ExtensionDescription.CommunityRectangle": {"background_color": 0xFF1F1F1F, "border_radius": 2},
            "ExtensionDescription.CommunityImage": {
                "image_url": f"{icons_path}/community.svg",
                "color": cl(180, 180, 180),
            },
            "ExtensionDescription.CommunityLabel": {"color": 0xFFA4A4A4, "font_size": 16},
            "ExtensionDescription.UnverifiedRectangle": {"background_color": 0xFF000038, "border_radius": 2},
            "ExtensionDescription.UnverifiedLabel": {"color": 0xFFC4C4C4, "margin_width": 30, "font_size": 16},
            "Button::create": {"background_color": 0x0, "margin": 0},
            "Button.Image::create": {"image_url": f"{icons_path}/plus.svg", "color": 0xFF00B976},
            "Button.Image::create:hovered": {"color": 0xFF00D976},
            "Button::options": {"background_color": 0x0, "margin": 0},
            "Button.Image::options": {"image_url": f"{icons_path}/options.svg", "color": 0xFF989898},
            "Button.Image::options:hovered": {"color": 0xFFC2C2C2},
            "Button::locked": {"background_color": 0x0, "margin": 0},
            "Button.Image::locked": {"image_url": f"{icons_path}/lock.svg", "color": 0xFF989898},
            "Button.Image::locked:hovered": {"color": 0xFF989898},
            "Button::filter": {"background_color": 0x0, "margin": 0},
            "Button.Image::filter": {"image_url": f"{icons_path}/filter_grey.svg", "color": 0xFF989898},
            "Button.Image::filter:hovered": {"color": 0xFFC2C2C2},
            "Button::filter_on": {"background_color": 0x0, "margin": 0},
            "Button.Image::filter_on": {"image_url": f"{icons_path}/filter.svg", "color": 0xFF989898},
            "Button.Image::filter_on:hovered": {"color": 0xFFC2C2C2},
            "Button::sortby": {"background_color": 0x0, "margin": 0},
            "Button.Image::sortby": {"image_url": f"{icons_path}/sort_by_grey.svg", "color": 0xFF989898},
            "Button.Image::sortby:hovered": {"color": 0xFFC2C2C2},
            "Button::sortby_on": {"background_color": 0x0, "margin": 0},
            "Button.Image::sortby_on": {"image_url": f"{icons_path}/sort_by.svg", "color": 0xFF989898},
            "Button.Image::sortby_on:hovered": {"color": 0xFFC2C2C2},
            "ExtensionDescription.Tab": {"background_color": 0x0},
            "ExtensionDescription.Tab.Label": {"color": 0xFF8D8D8D, "font_size": 16},
            "ExtensionDescription.Tab.Label:pressed": {"color": 0xFFF3F2EC},
            "ExtensionDescription.Tab.Label:selected": {"color": 0xFFF3F2EC},
            "ExtensionDescription.Tab.Label:hovered": {"color": 0xFFADADAD},
            "ExtensionDescription.TabLine": {"color": 0xFF00B976, "border_width": 1},
            "ExtensionDescription.TabLineFull": {"color": 0xFF707070},
            "ExtensionVersionMenu.MenuItem": {"color": 0x0, "margin": 0},
            "IconButton": {"margin": 0, "padding": 0, "background_color": 0x0},
            "IconButton:hovered": {"background_color": 0x0},
            "IconButton:checked": {"background_color": 0x0},
            "IconButton:pressed": {"background_color": 0x0},
            "IconButton.Image": {"color": 0xFFA8A8A8},
            "IconButton.Image:hovered": {"color": 0xFF929292},
            "IconButton.Image:pressed": {"color": 0xFFA4A4A4},
            "IconButton.Image:checked": {"color": 0xFFFFFFFF},
            "IconButton.Image::OpenDoc": {"image_url": f"{icons_path}/question.svg"},
            "IconButton.Image::OpenFolder": {"image_url": f"{icons_path}/open-folder.svg"},
            "IconButton.Image::OpenConfig": {"image_url": f"{icons_path}/open-config.svg"},
            "IconButton.Image::OpenInVSCode": {"image_url": f"{icons_path}/vscode.svg"},
            "IconButton.Image::Export": {"image_url": f"{icons_path}/export.svg"},
            "IconButton.Image::Copy": {"image_url": f"{icons_path}/copy.svg"},
            "Image::UpdateAvailable": {
                "image_url": f"{icons_path}/update-available.svg",
                "color": 0xFFFFFFFF,
            },
            "Label::UpdateAvailable": {"color": 0xFF00B977, "margin": 2},
            "Label::LocationTag": {"color": 0xFF00B977, "margin": 10, "font_size": 16},
            "Image::Community": {"image_url": f"{icons_path}/Community.svg"},
            "Label::Community": {"color": 0xFFA4A4A4, "margin": 10, "font_size": 16},
            "Rectangle::Splitter": {"background_color": 0x0, "margin": 3, "border_radius": 2},
            "Rectangle::Splitter:hovered": {"background_color": 0xFFB0703B},
            "Rectangle::Splitter:pressed": {"background_color": 0xFFB0703B},
            "Image::UNKNOWN": {"color": 0xFFFFFFFF, "image_url": f"{icons_path}/question.svg"},
            "Image::RUNNING": {"color": 0xFFFF7D7D, "image_url": f"{icons_path}/spinner.svg"},
            "Image::PASSED": {"color": 0xFF00FF00, "image_url": f"{icons_path}/check_solid.svg"},
            "Image::FAILED": {"color": 0xFF0000FF, "image_url": f"{icons_path}/exclamation.svg"},
            "TreeView:selected": {
                "background_color": 0xFF212121,
                "background_selected_color": 0xFF212121,
            },
            "ExtensionList.Image::Icon": {"margin": 4.0},
            "ExtInfoBackgroundRect": {
                "border_radius": 4.0,
                "background_color": ui.color(47, 47, 47),
            },
            "ExtInfoBackgroundRect:selected": {
                "background_color": ui.color(102, 112, 114),
            },
            "ExtInfoBackgroundRect:hovered": {
                "background_color": ui.color(56, 61, 63),
            },
            "ExtensionList.Label::Core": {
                "color": ui.color(66, 129, 187),
            },
            "ExtensionList.Label::Example": {
                "color": ui.color(142, 117, 155),
            },
            "ExtensionList.Label::Internal": {
                "color": ui.color(117, 117, 117),
            },
            "ExtensionList.Label::Community": {
                "color": ui.color(51, 166, 137),
            },
            "ExtensionList.Label::Deprecation": {
                "alignment": ui.Alignment.RIGHT_CENTER,
                "color": ui.color(199, 123, 36),
            },
            "ExtInfoFooter": {"border_radius": 4.0, "padding": 2.0},
            "ExtInfoFooter.Rectangle": {
                "border_radius": 4.0,
                "background_color": ui.color(31, 33, 35),
            },
            "ExtensionItem.Frame": {
                "padding": 2.0,
            },
            "Button::InstallButton": {
                "background_color": 0xFF00B976,
                "border_radius": 4.0,
            },
            "Button.Label::InstallButton": {"color": 0xFF3E3E3E},
        },
        "ExtsPropertiesWidget": {
            "Properies.Background": {"background_color": 0xFF24211F, "border_radius": 4},
        },
        "ExtsRegistriesWidget": {
            "TreeView": {
                "background_color": 0xFF23211F,
                "background_selected_color": 0xFF444444,
            },
            "TreeView.Item": {"margin": 14, "color": 0xFF000055},
            "Field": {"background_color": 0xFF333322},
            "Label::header": {"margin": 4},
            "Label": {"margin": 5},
            "Label::builtin": {"color": 0xFF909090},
            "Label::config": {"color": 0xFFDDDDDD},
            "ItemButton": {"padding": 2, "background_color": 0xFF444444, "border_radius": 4},
            "ItemButton.Image::add": {"image_url": f"{icons_path}/plus.svg", "color": 0xFF06C66B},
            "ItemButton.Image::remove": {"image_url": f"{icons_path}/trash.svg", "color": 0xFF1010C6},
            "ItemButton:hovered": {"background_color": 0xFF333333},
            "ItemButton:pressed": {"background_color": 0xFF222222},
        },
        "ExtsPathsWidget": {
            "TreeView": {
                "background_color": 0xFF23211F,
                "background_selected_color": 0xFF444444,
            },
            "TreeView.Item": {"margin": 14, "color": 0xFF000055},
            "Field": {"background_color": 0xFF333322},
            "Label::header": {"margin": 4},
            "Label": {"margin": 5},
            "Label::builtin": {"color": 0xFF909090},
            "Label::config": {"color": 0xFFDDDDDD},
            "ItemButton": {"padding": 2, "background_color": 0xFF444444, "border_radius": 4},
            "ItemButton.Image::add": {"image_url": f"{icons_path}/plus.svg", "color": 0xFF06C66B},
            "ItemButton.Image::remove": {"image_url": f"{icons_path}/trash.svg", "color": 0xFF1010C6},
            "ItemButton.Image::clean": {"image_url": f"{icons_path}/broom.svg", "color": 0xFF5EDAFA},
            "ItemButton.Image::update": {"image_url": f"{icons_path}/refresh.svg", "color": 0xFF5EDAFA},
            "ItemButton:hovered": {"background_color": 0xFF333333},
            "ItemButton:pressed": {"background_color": 0xFF222222},
        },
    }
    return styles


def get_style(instance):
    """Fetches the style definition for the given instance's class.

    Args:
        instance (Any): The instance whose class style is to be fetched.

    Returns:
        Dict: The style dictionary associated with the instance's class."""
    return get_styles()[instance.__class__.__name__]
