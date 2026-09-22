# SPDX-FileCopyrightText: Copyright (c) 2022-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
import omni.kit.test
from omni.asset_validator.core import Issue, IssueSeverity
from omni.asset_validator.ui import (
    AssetItem,
    AssetResultsModel,
    GroupByItem,
    GroupResultsModel,
    IssueItem,
    IssueModel,
    ReportStyle,
)
from omni.kit import ui_test
from omni.ui import HStack, Window


class AssetItemTest(omni.kit.test.AsyncTestCase):
    async def test_init(self):
        # Given
        asset = "omniverse://localhost/NVIDIA/Samples/Astronaut/Astronaut.usd"
        # When
        item = AssetItem(AssetResultsModel(asset))
        # Then
        self.assertEqual(item._model.asset, asset)
        self.assertEqual(item._model.selected, False)
        self.assertEqual(item.style, ReportStyle.WAITING)
        self.assertEqual(item.stats.errors, 0)
        self.assertEqual(item.stats.warnings, 0)
        self.assertEqual(item.stats.failures, 0)

    async def test_set_style(self):
        # Given
        asset = "omniverse://localhost/NVIDIA/Samples/Astronaut/Astronaut.usd"
        # When
        item = AssetItem(AssetResultsModel(asset))
        item.style = ReportStyle.SUCCESS
        # Then
        self.assertEqual(item.style, ReportStyle.SUCCESS)

    async def test_on_value_changed_fn_success(self):
        # Given
        asset = "omniverse://localhost/NVIDIA/Samples/Astronaut/Astronaut.usd"
        # When
        model = AssetResultsModel(asset)
        model.progress = 1
        model.groups = []
        item = AssetItem(model)
        # Then
        self.assertEqual(item.style, ReportStyle.SUCCESS)

    async def test_build_widget(self):
        # Given
        asset = "omniverse://localhost/NVIDIA/Samples/Astronaut/Astronaut.usd"
        # When
        item = AssetItem(AssetResultsModel(asset))
        # Then
        window = Window(__name__)
        with window.frame:
            with HStack():
                item.build_widget(0)
                item.build_widget(1)
                item.build_widget(2)

            await ui_test.human_delay()


class IssueItemTest(omni.kit.test.AsyncTestCase):
    async def setUp(self):
        super().setUp()
        self.base_url = "base.usda"
        self.issue = Issue(
            message="message",
            severity=IssueSeverity.FAILURE,
        )

    async def test_init(self):
        # Given / When
        item = IssueItem(IssueModel(self.issue))
        # Then
        self.assertEqual(item.issue, self.issue)
        self.assertEqual(item._model.selected, False)

    async def test_set_selected(self):
        # Given / When
        item = IssueItem(IssueModel(self.issue))
        item._model.selected = True
        # Then
        self.assertEqual(item._model.selected, True)

    async def test_severity_warning(self):
        # Given
        issue = Issue(message="message", severity=IssueSeverity.WARNING)
        # When
        item = IssueItem(IssueModel(issue))
        # Then
        self.assertEqual(item.style, ReportStyle.WARNING)

    async def test_severity_failed(self):
        # Given
        issue = Issue(message="message", severity=IssueSeverity.FAILURE)
        # When
        item = IssueItem(IssueModel(issue))
        # Then
        self.assertEqual(item.style, ReportStyle.FAILED)

    async def test_severity_info(self):
        # Given
        issue = Issue(message="message", severity=IssueSeverity.INFO)
        # When
        item = IssueItem(IssueModel(issue))
        # Then
        self.assertEqual(item.style, ReportStyle.INFO)

    async def test_build_widget(self):
        # Given
        item = IssueItem(IssueModel(self.issue))
        # Then
        window = Window(__name__)
        with window.frame:
            with HStack():
                item.build_widget(0)
                item.build_widget(1)
                item.build_widget(2)
                item.build_widget(3)
                item.build_widget(4)
                item.build_widget(5)

            await ui_test.human_delay()


class GroupByItemTest(omni.kit.test.AsyncTestCase):
    async def test_on_value_changed_fn_failure(self):
        # Given
        issue = Issue(message="message", severity=IssueSeverity.FAILURE)
        model = GroupResultsModel("group")
        model.issues = [IssueModel(issue)]
        # When
        item = GroupByItem(model)
        # Then
        self.assertEqual(item.get_children()[0].issue, issue)

    async def test_on_value_changed_fn_success(self):
        # Given
        issue = Issue(message="message", severity=IssueSeverity.NONE)
        model = GroupResultsModel("group")
        model.issues = [IssueModel(issue)]
        # When
        item = GroupByItem(model)
        # Then
        self.assertEqual(item.get_children()[0].issue, issue)

    async def test_build_widget(self):
        # Given
        item = GroupByItem(GroupResultsModel("group"))
        # Then
        window = Window(__name__)
        with window.frame:
            with HStack():
                item.build_widget(0)
                item.build_widget(1)

            await ui_test.human_delay()
