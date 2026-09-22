# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
import asyncio
from dataclasses import dataclass, field
from functools import partial, singledispatchmethod
from pathlib import Path

from omni.asset_validator.core import (
    AssetProgress,
    AssetType,
    FixStatus,
    Issue,
    IssueFixer,
    IssueGroupBy,
    IssueSeverity,
    IssuesList,
    RequirementsRegistry,
    Results,
)
from omni.ui import Button, HStack, Length, UnitType
from pxr import Sdf, Usd

from .model import ApplicationModel
from .options import OptionMode
from .results import AssetResultsModel, GroupResultsModel, IssueModel, ResultsModel

ICON_WIDTH: int = 20
CHARACTER_WIDTH: int = 8

__all__ = ["ValidatorCommandsWidget", "ValidateFn", "ClearFn", "FixFn", "ValidatorOptions"]


NOT_IMPLEMENTED_MESSAGE = "Not implemented. Consider validating manually."
"""Message to display for not implemented requirements."""


@dataclass(frozen=True)
class ValidatorOptions:
    mode: OptionMode
    group_by: IssueGroupBy
    enabled_rules: list
    enabled_requirements: list
    enabled_capabilities: list

    def _create_successful_groups(self, issues: IssuesList) -> list[GroupResultsModel]:
        group_results = []
        for group in issues.group_by(self.group_by):
            group_result = GroupResultsModel(group.name)
            group_result.issues = [IssueModel(issue) for issue in group.success]
            group_results.append(group_result)
        return group_results

    def _create_successful_rules(self, issues: IssuesList) -> list[GroupResultsModel]:
        enabled_rules = set(self.enabled_rules)
        failed_rules = set(issue.rule for issue in issues if issue.rule is not None)
        issues = [Issue(rule=rule, severity=IssueSeverity.NONE) for rule in enabled_rules - failed_rules]
        return self._create_successful_groups(IssuesList(issues))

    def _create_successful_requirements(self, issues: IssuesList) -> list[GroupResultsModel]:
        enabled_requirements = set(self.enabled_requirements)
        failed_requirements = set(issue.requirement for issue in issues if issue.requirement is not None)
        issues = [
            Issue(requirement=requirement, severity=IssueSeverity.NONE)
            for requirement in enabled_requirements - failed_requirements
        ]
        return self._create_successful_groups(IssuesList(issues))

    def _create_successful_capabilities(self, issues: IssuesList) -> list[GroupResultsModel]:
        requirements_registry = RequirementsRegistry()
        enabled_requirements = set(
            requirement
            for capability in self.enabled_capabilities
            for requirement in capability.requirements
            if requirements_registry.is_implemented(requirement)
        )
        failed_requirements = set(issue.requirement for issue in issues if issue.requirement is not None)
        issues = [
            Issue(requirement=requirement, severity=IssueSeverity.NONE)
            for requirement in enabled_requirements - failed_requirements
        ]
        return self._create_successful_groups(IssuesList(issues))

    def compute_successful_groups(self, issues: IssuesList) -> list[GroupResultsModel]:
        if self.mode is OptionMode.CATEGORIES:
            return self._create_successful_rules(issues)
        elif self.mode is OptionMode.FEATURES:
            return self._create_successful_requirements(issues)
        elif self.mode is OptionMode.CAPABILITIES:
            return self._create_successful_requirements(issues)
        else:
            return self._create_successful_capabilities(issues)

    def _create_not_implemented_groups(self, not_implemented_requirements: list) -> list[GroupResultsModel]:
        issues = [
            Issue(message=NOT_IMPLEMENTED_MESSAGE, requirement=requirement, severity=IssueSeverity.INFO)
            for requirement in not_implemented_requirements
        ]
        group_results = []
        for group in IssuesList(issues).group_by(self.group_by):
            group_result = GroupResultsModel(group.name)
            group_result.issues = [IssueModel(issue) for issue in group]
            group_results.append(group_result)
        return group_results

    def _create_not_implemented_requirements(self) -> list[GroupResultsModel]:
        registry = RequirementsRegistry()
        not_implemented_requirements = set(
            requirement for requirement in self.enabled_requirements if not registry.is_implemented(requirement)
        )
        return self._create_not_implemented_groups(list(not_implemented_requirements))

    def _create_not_implemented_capabilities(self) -> list[GroupResultsModel]:
        registry = RequirementsRegistry()
        not_implemented_requirements = set(
            requirement
            for capability in self.enabled_capabilities
            for requirement in capability.requirements
            if not registry.is_implemented(requirement)
        )
        return self._create_not_implemented_groups(list(not_implemented_requirements))

    def compute_not_implemented_groups(self, issues: IssuesList) -> list[GroupResultsModel]:
        if self.mode is OptionMode.CATEGORIES:
            return []
        elif self.mode is OptionMode.FEATURES:
            return self._create_not_implemented_requirements()
        elif self.mode is OptionMode.CAPABILITIES:
            return self._create_not_implemented_requirements()
        else:
            return self._create_not_implemented_capabilities()


@dataclass
class ValidateFn:
    model: ApplicationModel = field(default_factory=ApplicationModel.get)
    asset: AssetType | None = None
    status: dict[Issue, str] = field(default_factory=dict)

    def _asset_located_fn(self, asset: AssetType) -> None:
        results: ResultsModel = self.model.results
        if asset_results := results.get_asset(asset):
            asset_results.clear()  # Re calculation
            asset_results.apply_filter(self.model.filters_model.predicate)
        else:
            results.add_asset(AssetResultsModel(asset))

    def _asset_progress_fn(self, progress: AssetProgress) -> None:
        results: ResultsModel = self.model.results
        if asset_results := results.get_asset(progress.asset):
            asset_results.progress = progress.progress

    def _asset_validated_fn(self, results: Results, options: ValidatorOptions | None = None) -> None:
        issues_list: IssuesList = results.issues

        group_results = []
        for issues_group in issues_list.group_by(self.model.group_by):
            group_result = GroupResultsModel(issues_group.name)
            group_result.issues = [IssueModel(issue, self.status.get(issue)) for issue in issues_group]
            group_results.append(group_result)

        # UI can show successful groups
        if options:
            group_results.extend(options.compute_successful_groups(issues_list))
            group_results.extend(options.compute_not_implemented_groups(issues_list))

        model: ResultsModel = self.model.results
        if asset_results := model.get_asset(results.asset):
            group_results.sort(key=lambda group: group.name or "")
            asset_results.groups = group_results

    async def apply_async(self) -> None:
        engine = self.model.create_engine()
        if self.asset is None:
            self.model.results.clear()
            self.model.results.apply_filter(self.model.filters_model.predicate)
        options = ValidatorOptions(
            self.model.options_mode,
            self.model.group_by,
            engine.enabled_rules,
            engine.enabled_requirements,
            engine.enabled_capabilities,
        )
        await engine.validate_with_callbacks(
            asset=self.asset or self.model.asset,
            asset_located_fn=self._asset_located_fn,
            asset_progress_fn=self._asset_progress_fn,
            asset_validated_fn=partial(self._asset_validated_fn, options=options),
        )

    def apply(self) -> None:
        task: asyncio.Task = asyncio.ensure_future(self.apply_async())
        self.model.add_task(task)


@dataclass
class FixFn:
    model: ApplicationModel = field(default_factory=ApplicationModel.get)
    issue: Issue | None = None

    @singledispatchmethod
    @classmethod
    def _open_stage(cls, asset: AssetType) -> Usd.Stage:
        raise NotImplementedError(f"Unknown type {type(asset)}")

    @_open_stage.register
    @classmethod
    def _(cls, asset: Usd.Stage) -> Usd.Stage:
        return asset

    @_open_stage.register
    @classmethod
    def _(cls, asset: str) -> Usd.Stage:
        return Usd.Stage.Open(Sdf.Layer.FindOrOpen(asset))

    async def _fix_async(self, asset: AssetType, issues: list[IssueModel]) -> None:
        stage: Usd.Stage = self._open_stage(asset)
        status: dict[Issue, str] = {}

        fixer = IssueFixer(stage)
        for issue in issues:
            result = fixer.apply(issue.issue, issue.fix_at)
            if result.status is not FixStatus.SUCCESS:
                status[issue.issue] = f"Failed: {result.exception}"

        if self.model.settings_model.persist:
            try:
                fixer.save()
            except OSError as error:
                stage.Reload()
                for issue in issues:
                    status[issue.issue] = f"Exception: {error}"

        func = ValidateFn(self.model, asset, status)
        await func.apply_async()

    async def apply_async(self) -> None:
        results: ResultsModel = self.model.results
        for asset_result in results.assets:
            if self.issue:
                if model := asset_result.find_issue(self.issue):
                    await self._fix_async(asset_result.asset, [model])
            else:
                models: list[IssueModel] = asset_result.selected_issues
                if models:
                    await self._fix_async(asset_result.asset, models)

    def apply(self) -> None:
        task: asyncio.Task = asyncio.ensure_future(self.apply_async())
        self.model.add_task(task)


@dataclass
class ClearFn:
    model: ApplicationModel = field(default_factory=ApplicationModel.get)

    async def apply_async(self) -> None:
        results: ResultsModel = self.model.results
        results.clear()

    def apply(self) -> None:
        task: asyncio.Task = asyncio.ensure_future(self.apply_async())
        self.model.add_task(task)


class ValidatorCommandsWidget:
    ICON_PATH = Path(__file__).parents[3].joinpath("data/icons")

    def __init__(self):
        def resize_icon_width(button) -> None:
            """Resize the icon stack width in the given button"""
            # The button looks like this when the label text is long -
            # [      icon|long_text ]
            # We reduce the icon width in order to move left the text so the icon/text look like centered in the button.
            # The icon is about 20 pixels wide (ICON_WIDTH) and
            # a label character is about 8 pixel wide (CHARACTER_WIDTH). The formula is -
            # half of the width difference between icon and label text / icon_base_width
            icon_base_width = button.computed_content_width / 2
            yield_width = ((len(button.text) * CHARACTER_WIDTH) - ICON_WIDTH) / 2
            button.image_width = Length(1 - (yield_width / icon_base_width), UnitType.FRACTION)

        with HStack(height=30, spacing=10):
            run_button = Button(
                "Analyze",
                clicked_fn=ValidateFn().apply,
                image_url=str(self.ICON_PATH.joinpath("Analyze.svg")),
                name="action",
                spacing=4,
            )
            run_button.set_computed_content_size_changed_fn(lambda: resize_icon_width(run_button))

            fix_button = Button(
                "Fix Selected",
                clicked_fn=FixFn().apply,
                tooltip="Fix the selected errors based on suggestions.",
                image_url=str(self.ICON_PATH.joinpath("FixErrors.svg")),
                name="action",
                spacing=4,
            )
            fix_button.set_computed_content_size_changed_fn(lambda: resize_icon_width(fix_button))

            Button(
                "Clear Results",
                clicked_fn=ClearFn().apply,
                tooltip="Clear Results",
            )
