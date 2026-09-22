# SPDX-FileCopyrightText: Copyright (c) 2022-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field

import omni.client
import omni.ui
import omni.usd
import pyperclip
from omni.asset_validator.core import (
    Issue,
    IssueCSVData,
    IssuePredicates,
    IssueSeverity,
    IssuesList,
    LayerId,
    PrimId,
    PropertyId,
    StageId,
    VariantIdMixin,
)
from omni.kit.window.file_exporter import get_file_exporter
from pxr import Sdf

from .asset import AssetMode
from .commands import FixFn
from .filters import FilterWidget
from .fix import FixAtItemModel
from .model import ApplicationModel
from .results import AssetResultsModel, GroupResultsModel, HasSelectedModel, IssueModel, ResultsModel
from .style import STYLE, ReportStyle

__all__ = [
    "AssetItem",
    "IssueItem",
    "GroupByItem",
    "SuccessfulItem",
    "ReportModel",
    "ResultsWidget",
]

LEVEL_WIDTH = 20
EMPTY_LOCATION = "None"

SELECT_COLUMN = ""
ASSET_COLUMN = "Asset"
INFO_COLUMN = "Info"
SUGGEST_COLUMN = "Suggestion"
LOCATION_COLUMN = "Location"
FIX_RESULT_COLUMN = "Fix Result"

TREEVIEW_COLUMNS = [SELECT_COLUMN, ASSET_COLUMN, INFO_COLUMN, SUGGEST_COLUMN, LOCATION_COLUMN, FIX_RESULT_COLUMN]


@dataclass
class AssetStats:
    errors: int
    warnings: int
    failures: int

    def reset(self) -> None:
        self.errors = 0
        self.warnings = 0
        self.failures = 0


class TreeItem(omni.ui.AbstractItem):
    """
    A super class of all items in the tree. It adds selected, expanded and dumps.
    """

    def __init__(self, model: HasSelectedModel):
        super().__init__()
        self._model = model
        self._on_selected_id = model.selected_model.subscribe_value_changed_fn(self._on_selected_fn)
        self._children: list[TreeItem] = []

    def _on_selected_fn(self, _) -> None:
        for child in self.get_children():
            child._model.selected = self._model.selected

    def has_children(self) -> bool:
        return bool(self._children)

    def get_children(self) -> list[TreeItem]:
        return self._children

    def add_child(self, child: TreeItem) -> None:
        self._children.append(child)

    def clear_children(self) -> None:
        self._children.clear()

    def build_checkbox(self, enabled: bool = True) -> None:
        with omni.ui.VStack(width=12):
            omni.ui.Spacer(height=4)
            if enabled:
                omni.ui.CheckBox(self._model.selected_model)
            else:
                omni.ui.CheckBox(enabled=enabled)
            omni.ui.Spacer(height=4)

    def dumps(self) -> str:
        raise NotImplementedError()

    def build_branch(self, level: int, expanded: bool) -> None:
        with omni.ui.HStack(width=0, height=0):
            omni.ui.Spacer(width=level * LEVEL_WIDTH)
            if self.has_children():
                alignment = omni.ui.Alignment.CENTER_BOTTOM if expanded else omni.ui.Alignment.RIGHT_CENTER
                omni.ui.Spacer(width=3)
                omni.ui.Triangle(alignment=alignment, width=10, height=10, name="branch")
                omni.ui.Spacer(width=7)

    def build_widget(self, column_id: int) -> None:
        raise NotImplementedError()


class ResultItem(TreeItem):
    def __init__(self, model: IssueModel):
        super().__init__(model)

    @property
    def issue(self) -> Issue | None:
        return self._model.issue

    @property
    def fix_status(self) -> str | None:
        return self._model.fix_status

    @property
    def style(self) -> ReportStyle:
        return ReportStyle.from_issue(self.issue)


class GroupByItem(TreeItem):
    def __init__(self, model: GroupResultsModel):
        super().__init__(model)
        self._on_value_changed_id = model.subscribe_value_changed_fn(self._on_value_changed_fn)
        self._on_value_changed_fn(model)

    def _on_value_changed_fn(self, _):
        self.clear_children()
        if self._model.issues:
            for model in self._model.issues:
                if model.issue.severity is IssueSeverity.NONE:
                    self.add_child(SuccessfulItem(model))
                else:
                    self.add_child(IssueItem(model))

    def build_widget(self, column_id: int) -> None:
        if TREEVIEW_COLUMNS[column_id] == SELECT_COLUMN:
            self.build_checkbox()
        elif TREEVIEW_COLUMNS[column_id] == ASSET_COLUMN:
            omni.ui.Label(
                self._model.name or "",
                word_wrap=True,
                name=ReportStyle.SUCCESS.style,
            )

    def dumps(self) -> str:
        return f"GroupBy: {self._model.name}"


class AssetItem(TreeItem):
    def __init__(self, model: AssetResultsModel):
        super().__init__(model)
        self._on_value_changed_id = model.subscribe_value_changed_fn(self._on_value_changed_fn)
        self._on_value_changed_fn(model)

    def _on_value_changed_fn(self, model: AssetResultsModel) -> None:
        self.clear_children()
        if model.progress < 1:
            self.style = ReportStyle.WAITING
            self.stats = AssetStats(0, 0, 0)
        elif not model.groups:
            self.style = ReportStyle.SUCCESS
            self.stats = AssetStats(0, 0, 0)
            self.add_child(SuccessfulItem(IssueModel(Issue.none())))
        else:
            issues = IssuesList([issue_model.issue for issue_model in model.issues])
            self.style = ReportStyle.from_issue_list(issues)
            self.stats = AssetStats(
                errors=len(issues.filter_by(IssuePredicates.IsError())),
                warnings=len(issues.filter_by(IssuePredicates.IsWarning())),
                failures=len(issues.filter_by(IssuePredicates.IsFailure())),
            )
            for group_model in model.groups:
                self.add_child(GroupByItem(group_model))

    def build_widget(self, column_id: int) -> None:
        if TREEVIEW_COLUMNS[column_id] == SELECT_COLUMN:
            self.build_checkbox()
        elif TREEVIEW_COLUMNS[column_id] == ASSET_COLUMN:
            if self.style is ReportStyle.WAITING:
                tooltip = "Waiting"
            else:
                tooltip = f"{self.stats.errors} errors, {self.stats.failures} failures, {self.stats.warnings} warnings"

            with omni.ui.HStack():
                omni.ui.Spacer(width=5)
                omni.ui.Image(self.style.usd_icon, width=12)
                omni.ui.Spacer(width=5)
                omni.ui.Label(
                    self._model.asset_name,
                    tooltip=tooltip,
                    word_wrap=True,
                    name=self.style.style,
                )
        elif TREEVIEW_COLUMNS[column_id] == INFO_COLUMN:
            omni.ui.ProgressBar(self._model.as_progress, style={"color": 0xFFFF9E3D, "margin_width": 8})

    def dumps(self) -> str:
        return f"Asset: {self._model.asset_id}"


class IssueItem(ResultItem):
    def __init__(self, model: IssueModel):
        super().__init__(model)
        self.fix_at_model = FixAtItemModel(model)

    def build_widget(self, column_id: int) -> None:
        if TREEVIEW_COLUMNS[column_id] == SELECT_COLUMN:
            enabled: bool = self.issue.suggestion
            self.build_checkbox(enabled=enabled)
        elif TREEVIEW_COLUMNS[column_id] == ASSET_COLUMN:
            if self.issue.at:
                with omni.ui.HStack(style={"margin": 2}):
                    if isinstance(self.issue.at, PrimId | PropertyId):
                        label = omni.ui.Label(f"{self.issue.at.path}")
                    elif isinstance(self.issue.at, LayerId | StageId):
                        label = omni.ui.Label(f"@{self.issue.at.identifier}@")
                    else:
                        label = omni.ui.Label(self.issue.at.as_str())

                    # Add the long path to the tooltip
                    if isinstance(self.issue.at, VariantIdMixin):
                        label.set_tooltip(self.issue.at.variant_selection_path.pathString)

        elif TREEVIEW_COLUMNS[column_id] == INFO_COLUMN:
            with omni.ui.HStack(style={"margin": 2}):
                omni.ui.Label(
                    self.issue.message,
                    word_wrap=True,
                    name=self.style.style,
                )
        elif TREEVIEW_COLUMNS[column_id] == LOCATION_COLUMN:
            if self.issue.at:
                with omni.ui.HStack(style={"margin": 2}):
                    omni.ui.ComboBox(self.fix_at_model, tooltip="Select the location to fix")
        elif TREEVIEW_COLUMNS[column_id] == SUGGEST_COLUMN:
            handler: Callable[[float, float, int, ...], None] | None = None
            message: str = "Fix Manually"
            if self.issue.suggestion:
                handler = self._fix_click
                message = self.issue.suggestion.message
            elif ApplicationModel.get().mode is AssetMode.Stage and self.issue.at:
                handler = self._select_prim_in_stage
                message = "Select in stage"

            with omni.ui.ZStack(style={"margin": 2}, content_clipping=True):
                if handler:
                    # OMPE-3322: We make a button-like rectangle if there is an Issue Action (handler) available.
                    omni.ui.Rectangle(
                        name="suggestion",
                        mouse_released_fn=handler,
                        tooltip=message,
                    )
                with omni.ui.VStack():
                    omni.ui.Spacer(height=2)
                    omni.ui.Label(
                        message,
                        word_wrap=True,
                        name="suggestion",
                    )
                    omni.ui.Spacer(height=2)

        elif TREEVIEW_COLUMNS[column_id] == FIX_RESULT_COLUMN:
            if self.fix_status:
                with omni.ui.HStack(style={"marging": 2}):
                    omni.ui.Label(self.fix_status, word_wrap=True, name="suggestion")

    def _select_prim_in_stage(self, x, y, button, mod) -> None:
        if button != 0:
            return
        selection = omni.usd.get_context().get_selection()
        if isinstance(self.issue.at, PrimId):
            selection.set_selected_prim_paths([f"{self.issue.at.path}"], False)
        elif isinstance(self.issue.at, PropertyId):
            # OMPE-3326 - Kit doesn't support mesh component level selection,
            # we should still provide prim level selection when pressing the "Select in stage" button
            selection.set_selected_prim_paths([f"{self.issue.at.prim_id.path}"], False)
        else:
            selection.set_selected_prim_paths([f"{Sdf.Path.absoluteRootPath.pathString}"], False)

    def _fix_click(self, x, y, button, mod) -> None:
        if button != 0:
            return
        FixFn(issue=self.issue).apply()

    def dumps(self) -> str:
        return f"{self.rule}, {self.issue.message}, {self.issue.at.as_str() if self.issue.at else EMPTY_LOCATION}"


class SuccessfulItem(ResultItem):
    """No issues found message."""

    def __init__(self, model: IssueModel):
        super().__init__(model)

    def build_widget(self, column_id: int) -> None:
        if TREEVIEW_COLUMNS[column_id] == SELECT_COLUMN:
            self.build_checkbox(enabled=True)
        elif TREEVIEW_COLUMNS[column_id] == ASSET_COLUMN:
            omni.ui.Label(self.dumps(), word_wrap=True, name=self.style.style)

    def dumps(self) -> str:
        return "No issues found"


ItemType = AssetItem | GroupByItem | IssueItem | SuccessfulItem
"""Alias of Asset, GroupBy and Issue items."""


class ReportModel(omni.ui.AbstractItemModel):
    """
    Data Model of Results, i.e. Assets and Issues.
    """

    def __init__(self, model: ResultsModel):
        super().__init__()
        self._model = model
        self._on_value_changed_id = model.subscribe_value_changed_fn(self._on_value_changed_fn)
        self._on_selected_id = model.selected_model.subscribe_value_changed_fn(self._on_selected_fn)
        self._assets = {}
        self._on_asset_changed_ids = []
        self._on_value_changed_fn(model)

    def _on_value_changed_fn(self, model: ResultsModel):
        updated: bool = False
        if not model.assets:
            updated = True
            self._assets.clear()
            self._on_asset_changed_ids.clear()
        else:
            for asset_model in model.assets:
                if asset_model.asset_id not in self._assets:
                    updated = True
                    item = AssetItem(asset_model)
                    self._assets[asset_model.asset_id] = item
                    self._on_asset_changed_ids.append(asset_model.subscribe_value_changed_fn(self._on_asset_changed))
        if updated:
            self._item_changed(None)

    def _on_asset_changed(self, asset: AssetResultsModel):
        if item := self._assets.get(asset.asset_id):
            self._item_changed(item)

    def _on_selected_fn(self, _) -> None:
        for asset_model in self._model.assets:
            asset_model.selected = self._model.selected

    def get_item_children(self, item: ItemType | None) -> list[ItemType]:
        """
        Override. Get the items at specific hierarchy.
        """
        if item is None:
            return list(self._assets.values())
        else:
            return item.get_children()

    @classmethod
    def get_item_value_model_count(cls, _: ItemType | None) -> int:
        """
        Override. Returns the number of columns.
        """
        return len(TREEVIEW_COLUMNS)

    def get_item_value_model(self, item, column_id):
        """
        Return value model.
        """
        if item is None:
            return self._model
        else:
            return None


class ReportTableDelegate(omni.ui.AbstractItemDelegate):
    """
    UI delegate to render `ReportModel` as a table.
    """

    def __init__(self, model: ResultsModel):
        super().__init__()
        self._model = model

    def build_branch(self, model, item, column_id, level, expanded) -> None:
        """
        Override. Build expand/collapse if applies.
        """
        if item and TREEVIEW_COLUMNS[column_id] == ASSET_COLUMN:
            item.build_branch(level, expanded)

    def build_widget(self, model, item, column_id, level, expanded) -> None:
        """
        Override. Build widgets for specific item.
        """
        if item:
            item.build_widget(column_id)

    def build_header(self, column_id: int) -> None:
        """
        Override. Build headers.
        """
        with omni.ui.ZStack():
            omni.ui.Rectangle(style={"background_color": 0xFF555453})
            if column_id == 0:
                with omni.ui.VStack():
                    omni.ui.Spacer(height=4)
                    omni.ui.CheckBox(self._model.selected_model)
                    omni.ui.Spacer()
            else:
                omni.ui.Label(
                    TREEVIEW_COLUMNS[column_id],
                    height=25,
                    alignment=omni.ui.Alignment.CENTER,
                )


# Actions


@dataclass
class CopyAction:
    """
    Class used to copy the selected issues in the model to the clipboard in CSV format.
    It's invoked from a context menu in the ReportSectionreport section of the UI.
    """

    model: ResultsModel = field(default_factory=lambda: ApplicationModel.get().results)

    def __call__(self):
        """Copies the selected issues in the model to the clipboard."""
        # Create CSV data out of the selected issues
        csv_data = IssueCSVData.from_([model.issue for model in self.model.selected_issues])
        # Add the fix status/result column to the CSV data
        csv_data.append_column(
            FIX_RESULT_COLUMN,
            [model.fix_status or "None" for model in self.model.selected_issues],
        )
        # Copy the CSV data to the clipboard
        pyperclip.copy(csv_data.get_csv_as_str())


@dataclass
class SaveCSVAction:
    """
    Class used to save the selected issues in the model to a CSV file.
    It's invoked from a context menu in the ReportSectionreport section of the UI.
    """

    model: ResultsModel = field(default_factory=lambda: ApplicationModel.get().results)

    def export_csv(self, file_name: str, dir_name: str, extension: str, selections: list[str]):
        """
        Exports the selected issues in the model to a CSV file.

        Args:
            file_name (str): The name of the CSV file.
            dir_name (str): The directory where the CSV file will be saved.
            extension (str): The file extension.
            selections (List[str]): The files selected in the file export dialog.
        """
        extension = extension or ".csv"
        file_url = omni.client.combine_urls(dir_name, f"{file_name}{extension}")
        # Create CSV data out of the selected issues
        csv_data = IssueCSVData.from_([model.issue for model in self.model.selected_issues])
        # Add the fix status/result column to the CSV data
        csv_data.append_column(
            FIX_RESULT_COLUMN,
            [model.fix_status or "None" for model in self.model.selected_issues],
        )
        # Save the CSV data to a file
        csv_data.export_csv(file_url)

    def __call__(self):
        """Shows a dialog to save the selected issues in the model to a CSV file."""
        file_exporter = get_file_exporter()
        if file_exporter:
            file_exporter.show_window(
                title="Save as CSV",
                export_button_label="Save",
                export_handler=self.export_csv,
                file_extension_types=[(".csv", "CSV Files")],
                show_only_folders=False,
                enable_filename_input=True,
            )


# Report


class ResultsWidget:
    def __init__(self):
        self._model: ResultsModel = ApplicationModel.get().results
        self._item_model = ReportModel(self._model)
        self._item_delegate = ReportTableDelegate(self._model)
        with omni.ui.VStack():
            FilterWidget()
            with omni.ui.ScrollingFrame(style=STYLE):
                omni.ui.TreeView(
                    self._item_model,
                    delegate=self._item_delegate,
                    root_visible=False,
                    column_widths=[
                        20,  # checkbox
                        omni.ui.Fraction(2),  # asset
                        omni.ui.Fraction(2),  # info
                        omni.ui.Fraction(1),  # suggestion
                        omni.ui.Fraction(1),  # location
                        omni.ui.Fraction(1),  # fix result
                    ],
                    columns_resizable=True,
                    header_visible=True,
                    mouse_pressed_fn=self._show_report_context_menu,
                )

    def _show_report_context_menu(self, x: int, y: int, button: int, modifier: int) -> None:
        """Build and show Context menu when mouse right click"""
        # Display context menu only if the right button is pressed
        if button != 1:
            return

        # Reset the previous context popup
        self._report_context_menu = omni.ui.Menu()
        with self._report_context_menu:
            omni.ui.MenuItem(
                "Copy Selected Issue Items",
                tooltip="Copy selected issue items",
                triggered_fn=CopyAction(self._model),
                enabled=bool(self._model.selected_issues),
            )
            omni.ui.MenuItem(
                "Save Selected Issue Items",
                tooltip="Save selected issue items to csv file",
                triggered_fn=SaveCSVAction(self._model),
                enabled=bool(self._model.selected_issues),
            )
        self._report_context_menu.show()
