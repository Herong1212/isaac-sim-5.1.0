# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

from collections import namedtuple

import omni.capabilities as cap
import omni.kit.test
from omni.asset_validator.core import (
    AssetProgress,
    Issue,
    IssueGroupsBy,
    IssueSeverity,
    IssuesList,
    Results,
    TypeChecker,
)
from omni.asset_validator.ui import (
    ApplicationModel,
    AssetResultsModel,
    ClearFn,
    FixFn,
    GroupResultsModel,
    IssueModel,
    OptionMode,
    ValidateFn,
    ValidatorOptions,
)
from pxr import Usd


class ValidatorOptionsTest(omni.kit.test.AsyncTestCase):

    def test_create_successful_rules_creates_groups_for_enabled_rules(self):
        options = ValidatorOptions(
            mode=OptionMode.CATEGORIES,
            group_by=IssueGroupsBy.rule(),
            enabled_rules=[TypeChecker],
            enabled_requirements=[],
            enabled_capabilities=[],
        )
        issues = IssuesList([])

        groups = options.compute_successful_groups(issues)

        self.assertEqual(len(groups), 1)
        self.assertEqual(groups[0].name, TypeChecker)
        self.assertEqual(len(groups[0].issues), 1)
        self.assertEqual(groups[0].issues[0].issue.severity, IssueSeverity.NONE)
        self.assertEqual(groups[0].issues[0].issue.rule, TypeChecker)

    def test_create_successful_requirements_creates_groups_for_enabled_requirements(self):
        options = ValidatorOptions(
            mode=OptionMode.CAPABILITIES,
            group_by=IssueGroupsBy.requirement(),
            enabled_rules=[],
            enabled_requirements=[cap.Requirements.AA_001],
            enabled_capabilities=[],
        )
        issues = IssuesList([])

        groups = options.compute_successful_groups(issues)

        self.assertEqual(len(groups), 1)
        self.assertEqual(groups[0].name, cap.Requirements.AA_001)
        self.assertEqual(len(groups[0].issues), 1)
        self.assertEqual(groups[0].issues[0].issue.severity, IssueSeverity.NONE)
        self.assertEqual(groups[0].issues[0].issue.requirement, cap.Requirements.AA_001)

    def test_create_successful_capabilities_creates_groups_for_enabled_capabilities(self):
        options = ValidatorOptions(
            mode=OptionMode.PROFILES,
            group_by=IssueGroupsBy.requirement(),
            enabled_rules=[],
            enabled_requirements=[],
            enabled_capabilities=[cap.Capabilities.ATOMIC_ASSET],
        )
        issues = IssuesList([])

        groups = options.compute_successful_groups(issues)

        self.assertEqual(len(groups), len(cap.Capabilities.ATOMIC_ASSET.requirements))
        self.assertEqual(len(groups[0].issues), 1)
        self.assertEqual(groups[0].issues[0].issue.severity, IssueSeverity.NONE)
        self.assertIn(groups[0].issues[0].issue.requirement, cap.Capabilities.ATOMIC_ASSET.requirements)

    def test_create_not_implemented_groups_returns_empty_for_categories(self):
        options = ValidatorOptions(
            mode=OptionMode.CATEGORIES,
            group_by=IssueGroupsBy.rule(),
            enabled_rules=[TypeChecker],
            enabled_requirements=[],
            enabled_capabilities=[],
        )
        issues = IssuesList([])

        groups = options.compute_not_implemented_groups(issues)

        self.assertEqual(len(groups), 0)

    def test_create_not_implemented_requirements_creates_groups_for_unimplemented_requirements(self):
        Requirement = namedtuple("Requirement", ["code", "display_name", "message", "path", "tags"])
        not_implemented_requirement = Requirement(
            code="TEST",
            display_name="TEST",
            message="Not implemented. Consider validating manually.",
            path="/requirements/test",
            tags=(),
        )
        options = ValidatorOptions(
            mode=OptionMode.CAPABILITIES,
            group_by=IssueGroupsBy.requirement(),
            enabled_rules=[],
            enabled_requirements=[not_implemented_requirement],
            enabled_capabilities=[],
        )
        issues = IssuesList([])

        groups = options.compute_not_implemented_groups(issues)

        self.assertEqual(len(groups), 1)
        self.assertEqual(groups[0].name, not_implemented_requirement)
        self.assertEqual(len(groups[0].issues), 1)
        self.assertEqual(groups[0].issues[0].issue.message, not_implemented_requirement.message)
        self.assertEqual(groups[0].issues[0].issue.requirement, not_implemented_requirement)
        self.assertEqual(groups[0].issues[0].issue.severity, IssueSeverity.INFO)

    def test_create_not_implemented_capabilities_creates_groups_for_unimplemented_requirements(self):
        Requirement = namedtuple("Requirement", ["code", "display_name", "message", "path", "tags"])
        not_implemented_requirement = Requirement(
            code="TEST",
            display_name="TEST",
            message="Not implemented. Consider validating manually.",
            path="/requirements/test",
            tags=(),
        )
        Capability = namedtuple("Capability", ["requirements"])
        not_implemented_capability = Capability(requirements=[not_implemented_requirement])
        options = ValidatorOptions(
            mode=OptionMode.PROFILES,
            group_by=IssueGroupsBy.requirement(),
            enabled_rules=[],
            enabled_requirements=[],
            enabled_capabilities=[not_implemented_capability],
        )
        issues = IssuesList([])

        groups = options.compute_not_implemented_groups(issues)

        self.assertEqual(len(groups), 1)
        self.assertEqual(groups[0].name, not_implemented_requirement)
        self.assertEqual(len(groups[0].issues), 1)
        self.assertEqual(groups[0].issues[0].issue.message, not_implemented_requirement.message)
        self.assertEqual(groups[0].issues[0].issue.requirement, not_implemented_requirement)
        self.assertEqual(groups[0].issues[0].issue.severity, IssueSeverity.INFO)


class ValidateFnTest(omni.kit.test.AsyncTestCase):
    async def setUp(self):
        self.model = ApplicationModel.create()

        self.model.categories_model.get(TypeChecker).selected = True
        self.model.asset = Usd.Stage.CreateInMemory()
        self.model.asset.DefinePrim("/World", "Xform")

    async def test_validate_fn_adds_task(self):
        validate_fn = ValidateFn(model=self.model)

        validate_fn.apply()

        self.assertTrue(self.model.has_tasks())
        await self.model.wait_tasks()

    async def test_asset_located_fn_clears_existing_asset(self):
        validate_fn = ValidateFn(model=self.model)
        asset_results = AssetResultsModel(self.model.asset)
        self.model.results.add_asset(asset_results)

        group = GroupResultsModel("test_group")
        asset_results.groups = [group]
        asset_results.progress = 1.0

        validate_fn._asset_located_fn(self.model.asset)

        self.assertEqual(len(asset_results.groups), 0)
        self.assertEqual(asset_results.progress, 0)

    async def test_asset_located_fn_adds_new_asset(self):
        validate_fn = ValidateFn(model=self.model)

        validate_fn._asset_located_fn(self.model.asset)

        self.assertEqual(len(self.model.results.assets), 1)
        self.assertEqual(self.model.results.assets[0].asset, self.model.asset)

    async def test_asset_progress_fn_updates_progress(self):
        validate_fn = ValidateFn(model=self.model)
        asset_results = AssetResultsModel(self.model.asset)
        self.model.results.add_asset(asset_results)

        progress = AssetProgress(self.model.asset, 0.5)
        validate_fn._asset_progress_fn(progress)

        self.assertEqual(asset_results.progress, 0.5)

    async def test_asset_validated_fn_no_issues(self):
        validate_fn = ValidateFn(model=self.model)
        asset_results = AssetResultsModel(self.model.asset)
        self.model.results.add_asset(asset_results)

        results = Results(self.model.asset, [])
        validate_fn._asset_validated_fn(results)

        self.assertEqual(len(asset_results.groups), 0)

    async def test_asset_validated_fn_updates_groups(self):
        validate_fn = ValidateFn(model=self.model)
        asset_results = AssetResultsModel(self.model.asset)
        self.model.results.add_asset(asset_results)

        issue = Issue(message="Hi", severity=IssueSeverity.FAILURE, rule=TypeChecker)
        results = Results(self.model.asset, [issue])
        validate_fn._asset_validated_fn(results)

        self.assertEqual(len(asset_results.groups), 1)
        self.assertIsInstance(asset_results.groups[0], GroupResultsModel)

    async def test_asset_validated_fn_with_status(self):
        status = {}
        issue = Issue(message="Hi", severity=IssueSeverity.FAILURE, rule=TypeChecker)
        status[issue] = "Failed: Some error"

        validate_fn = ValidateFn(model=self.model, status=status)
        asset_results = AssetResultsModel(self.model.asset)
        self.model.results.add_asset(asset_results)

        results = Results(self.model.asset, [issue])
        validate_fn._asset_validated_fn(results)

        self.assertEqual(len(asset_results.groups), 1)
        self.assertEqual(len(asset_results.groups[0].issues), 1)
        self.assertEqual(asset_results.groups[0].issues[0].fix_status, "Failed: Some error")


class FixFnTest(omni.kit.test.AsyncTestCase):
    async def setUp(self):
        self.model = ApplicationModel.create()

        self.test_asset = Usd.Stage.CreateInMemory()
        self.test_asset.DefinePrim("/World", "Xform")
        self.asset_results = AssetResultsModel(self.test_asset)
        self.model.results.add_asset(self.asset_results)

        self.issue = Issue(message="Test issue", severity=IssueSeverity.FAILURE, rule=TypeChecker)
        self.issue_model = IssueModel(self.issue)

        self.group = GroupResultsModel("Test Group")
        self.group.issues = [self.issue_model]
        self.asset_results.groups = [self.group]

    async def test_fix_fn_fixes_single_issue(self):
        fix_fn = FixFn(model=self.model, issue=self.issue)
        await fix_fn.apply_async()

        self.assertEqual(len(self.model.results.assets), 1)
        self.assertEqual(len(self.asset_results.groups), 0)

    async def test_fix_fn_fixes_selected_issue(self):
        self.issue_model.selected = True

        fix_fn = FixFn(model=self.model)
        await fix_fn.apply_async()

        self.assertEqual(len(self.model.results.assets), 1)
        self.assertEqual(len(self.asset_results.groups), 0)


class ClearFnTest(omni.kit.test.AsyncTestCase):
    async def setUp(self):
        self.model = ApplicationModel.create()

    async def test_clear_fn_clears_results(self):
        test_asset = Usd.Stage.CreateInMemory()
        asset_results = AssetResultsModel(test_asset)
        self.model.results.add_asset(asset_results)

        self.assertEqual(len(self.model.results.assets), 1)

        clear_fn = ClearFn(model=self.model)
        await clear_fn.apply_async()

        self.assertIsNotNone(self.model.results)
        self.assertEqual(len(self.model.results.assets), 0)
