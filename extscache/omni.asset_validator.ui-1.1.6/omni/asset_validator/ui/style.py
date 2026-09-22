# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
from __future__ import annotations

from enum import Enum
from pathlib import Path

from omni.asset_validator.core import Issue, IssuePredicates, IssueSeverity, IssuesList
from omni.ui import Alignment, CornerFlag, Direction, color

__all__ = ["STYLE", "ReportStyle"]

STYLE = {
    "ScrollingFrame": {"background_color": 0xFF333332},
    "Triangle::branch": {"background_color": 0xFFFFFFFF},
    "Line::border-bottom": {"color": 0xFFE0E0E0, "alignment": Alignment.V_CENTER},
    "Label::waiting": {"color": 0xFFFFFFFF},
    "Image::waiting": {"color": 0xFFFFFFFF},
    "Label::success": {"color": 0x60B0FFFF},
    "Image::success": {"color": 0x60B0FFFF},
    "Label::warning": {"color": 0xFF4ACBDF},
    "Image::warning": {"color": 0xFF4ACBDF},
    "Label::info": {"color": 0xFFE8A200},
    "Image::info": {"color": 0xFFE8A200},
    "Label::failed": {"color": 0xFF6060FF, "alignment": Alignment.LEFT_TOP},
    "Image::failed": {"color": 0xFF6060FF},
    "Label::suggestion": {"alignment": Alignment.CENTER, "color": 0xFFBBBBBB, "margin": 4},
    "CheckBox": {"alignment": Alignment.V_CENTER},
    "TreeView": {"background_selected_color": 0x55555453, "secondary_color": 0xFF909090, "border_width": 1.5},
    "Rectangle::suggestion": {
        "background_color": 0xFF202020,
        "border_width": 1,
        "border_radius": 5,
    },
    "Rectangle::suggestion:hovered": {"background_color": 0xFF888888, "border_color": 0xFF353535},
}

TAB_GROUP_STYLE = {
    "TabGroupBorder": {"background_color": color.transparent, "border_color": color(25), "border_width": 1},
    "Rectangle::TabGroupHeader": {
        "background_color": color(20),
    },
    "ZStack::TabGroupHeader": {"margin_width": 1},
}

TAB_STYLE = {
    "": {"background_color": color(31), "corner_flag": CornerFlag.TOP, "border_radius": 4, "color": color(127)},
    ":selected": {"background_color": color(56), "color": color(203)},
    "Label": {"margin_width": 5, "margin_height": 3},
}
PANEL_STYLE = {
    "Rectangle::splitter": {"background_color": 0x00000000, "margin": 0, "padding": 0},
    "Rectangle::splitter:hovered": {"background_color": 0xFFB0703B},
    "Rectangle::splitter:pressed": {"background_color": 0xFFB0703B},
}
FRAME_STYLE = {
    "Rectangle::splitter": {"background_color": 0x00000000, "margin": 0, "padding": 0},
    "Rectangle::splitter:hovered": {"background_color": 0xFFB0703B},
    "Rectangle::splitter:pressed": {"background_color": 0xFFB0703B},
    "Button::action": {"stack_direction": Direction.LEFT_TO_RIGHT},
    "Button.Label::action": {"alignment": Alignment.LEFT_CENTER},
    "Button.Image::action": {"alignment": Alignment.RIGHT_CENTER},
}

_ICON_PATH = Path(__file__).parents[3].joinpath("data/icons")


class ReportStyle(Enum):
    WAITING = ("waiting", f"{_ICON_PATH.joinpath('assetValidatorDark.18x18.png')}")
    SUCCESS = ("success", f"{_ICON_PATH.joinpath('assetValidatorActive.18x18.png')}")
    WARNING = ("warning", "${glyphs}/Warning_Log.svg")
    FAILED = ("failed", "${glyphs}/Error_Log.svg")
    INFO = ("info", "${glyphs}/Info_Log.svg")

    def __init__(self, style, icon):
        self._style = style
        self._icon = icon

    @property
    def style(self) -> str:
        return self._style

    @property
    def icon(self) -> str:
        return self._icon

    @property
    def usd_icon(self) -> str:
        return f"{_ICON_PATH.joinpath('USDLogoUnsized.svg')}"

    @classmethod
    def from_issue(cls, issue: Issue | None) -> ReportStyle:
        if issue is None:
            return ReportStyle.WAITING
        elif issue.severity is IssueSeverity.NONE:
            return ReportStyle.SUCCESS
        elif issue.severity is IssueSeverity.WARNING:
            return ReportStyle.WARNING
        elif issue.severity is IssueSeverity.FAILURE:
            return ReportStyle.FAILED
        elif issue.severity is IssueSeverity.ERROR:
            return ReportStyle.FAILED
        elif issue.severity is IssueSeverity.INFO:
            return ReportStyle.INFO

    @classmethod
    def from_issue_list(cls, issues: IssuesList) -> ReportStyle:
        if issues.filter_by(IssuePredicates.Or(IssuePredicates.IsError(), IssuePredicates.IsFailure())):
            return ReportStyle.FAILED
        elif issues.filter_by(IssuePredicates.IsWarning()):
            return ReportStyle.WARNING
        else:
            return ReportStyle.SUCCESS
