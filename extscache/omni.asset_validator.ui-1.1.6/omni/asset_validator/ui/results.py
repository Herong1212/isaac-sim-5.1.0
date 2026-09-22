# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

from omni.asset_validator.core import (
    AssetType,
    Issue,
    IssuePredicate,
    IssuePredicates,
    Results,
    ResultsList,
    SpecId,
    ValidationEngine,
)
from omni.ui import AbstractValueModel, SimpleBoolModel

from .fix import FixAtModel
from .progress import ProgressModel

__all__ = [
    "HasSelectedModel",
    "IssueModel",
    "GroupResultsModel",
    "AssetResultsModel",
    "ResultsModel",
]


class HasSelectedModel(AbstractValueModel):
    def __init__(self):
        super().__init__()
        self._selected = SimpleBoolModel(False)

    @property
    def selected(self) -> bool:
        return self._selected.as_bool

    @selected.setter
    def selected(self, value) -> None:
        self._selected.as_bool = value

    @property
    def selected_model(self) -> SimpleBoolModel:
        return self._selected


class IssueModel(HasSelectedModel):
    def __init__(self, issue: Issue, fix_status: str | None = None):
        super().__init__()
        self._issue = issue
        self._fix_status = fix_status or ""
        self._fix_at = FixAtModel(issue.all_fix_sites)

    @property
    def issue(self) -> Issue:
        return self._issue

    @property
    def fix_status(self) -> str:
        return self._fix_status

    @property
    def fix_at(self) -> SpecId | None:
        return self._fix_at.fix_site

    @property
    def as_fix(self) -> FixAtModel:
        return self._fix_at


class GroupResultsModel(HasSelectedModel):
    def __init__(self, name):
        super().__init__()
        self._name = name
        self._issues = []
        self._predicate = IssuePredicates.Any()

    @property
    def name(self) -> AssetType:
        return self._name

    @property
    def issues(self) -> list[IssueModel]:
        return [issue for issue in self._issues if self._predicate(issue.issue)]

    @issues.setter
    def issues(self, issues: list[IssueModel]) -> None:
        self._issues = issues
        self._value_changed()

    def apply_filter(self, predicate: IssuePredicate) -> None:
        if self._predicate is not predicate:
            self._predicate = predicate
            self._value_changed()

    @property
    def selected_issues(self) -> list[IssueModel]:
        selected = []
        for issue in self.issues:
            if issue.selected:
                selected.append(issue)
        return selected

    def find_issue(self, issue: Issue) -> IssueModel | None:
        for model in self.issues:
            if model.issue == issue:
                return model
        return None


class AssetResultsModel(HasSelectedModel):
    def __init__(self, asset: AssetType):
        super().__init__()
        self._asset = asset
        self._progress = ProgressModel()
        self._groups = []
        self._predicate = IssuePredicates.Any()

    @property
    def asset(self) -> AssetType:
        return self._asset

    @property
    def asset_id(self) -> str:
        return ValidationEngine.describe(self.asset)

    @property
    def asset_name(self) -> str:
        asset_name: str = self.asset_id

        # url
        start = asset_name.rfind("/")
        if start > 0:
            return asset_name[start + 1 :]

        # stage
        splits = asset_name.split("@")
        name = splits[1]

        if len(name) > 0:
            return name

        return asset_name

    @property
    def progress(self) -> float:
        return self._progress.get_value_as_float()

    @progress.setter
    def progress(self, value) -> None:
        self._progress.set_value(value)

    @property
    def as_progress(self) -> ProgressModel:
        return self._progress

    @property
    def groups(self) -> list[GroupResultsModel]:
        return [group for group in self._groups if group.issues]

    @groups.setter
    def groups(self, groups: list[GroupResultsModel]) -> None:
        self._groups = groups
        for group in self._groups:
            group.apply_filter(self._predicate)
        self._value_changed()

    def apply_filter(self, predicate: IssuePredicate) -> None:
        if self._predicate is not predicate:
            self._predicate = predicate
            for group in self._groups:
                group.apply_filter(self._predicate)
            self._value_changed()

    def clear(self) -> None:
        self.selected = False
        self._progress.set_value(0)
        self._groups.clear()
        self._predicate = IssuePredicates.Any()
        self._value_changed()

    @property
    def issues(self) -> list[IssueModel]:
        issues = []
        for group in self.groups:
            issues.extend(group.issues)
        return issues

    @property
    def selected_issues(self) -> list[IssueModel]:
        issues = []
        for group in self.groups:
            issues.extend(group.selected_issues)
        return issues

    def find_issue(self, issue: Issue) -> IssueModel | None:
        for group in self.groups:
            if model := group.find_issue(issue):
                return model
        return None


class ResultsModel(HasSelectedModel):
    def __init__(self):
        super().__init__()
        self._assets = {}
        self._predicate = IssuePredicates.Any()

    @property
    def assets(self) -> list[AssetResultsModel]:
        return list(self._assets.values())

    def add_asset(self, model: AssetResultsModel) -> None:
        model.apply_filter(self._predicate)
        self._assets[model.asset_id] = model
        self._value_changed()

    def get_asset(self, asset: AssetType) -> AssetResultsModel | None:
        asset_id = ValidationEngine.describe(asset)
        return self._assets.get(asset_id)

    def apply_filter(self, predicate: IssuePredicate) -> None:
        if self._predicate is not predicate:
            self._predicate = predicate
            for asset in self.assets:
                asset.apply_filter(predicate)
            self._value_changed()

    def clear(self) -> None:
        self._assets.clear()
        self._predicate = IssuePredicates.Any()
        self._value_changed()

    @property
    def issues(self) -> list[IssueModel]:
        issues = []
        for asset in self.assets:
            issues.extend(asset.issues)
        return issues

    @property
    def as_results(self) -> list[Results]:
        results = []
        for asset in self.assets:
            results.append(Results.create(asset.asset, [issue.issue for issue in asset.issues]))
        return ResultsList(results)

    @property
    def selected_issues(self) -> list[IssueModel]:
        issues = []
        for asset in self.assets:
            issues.extend(asset.selected_issues)
        return issues

    def find_issue(self, issue: Issue) -> IssueModel | None:
        for asset in self.assets:
            if model := asset.find_issue(issue):
                return model
        return None
