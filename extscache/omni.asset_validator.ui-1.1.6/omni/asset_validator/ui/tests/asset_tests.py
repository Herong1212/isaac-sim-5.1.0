# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
import unittest.mock as mock

import omni.kit.test
from omni.asset_validator.ui import AssetMode
from omni.asset_validator.ui.asset import ModeModel, StageModel, UriModel
from pxr import Usd


class UriModelTest(omni.kit.test.AsyncTestCase):
    def test_set_value(self):
        model = UriModel()
        model.set_value("test/path")
        self.assertEqual(model.get_value_as_string(), "test/path")

    def test_value_changed_notification(self):
        model = UriModel()
        on_value_changed = mock.Mock()
        _subscription = model.subscribe_value_changed_fn(on_value_changed)

        model.set_value("new/path")
        self.assertTrue(on_value_changed.called)
        self.assertEqual(model.get_value_as_string(), "new/path")


class StageModelTest(omni.kit.test.AsyncTestCase):
    def test_set_value(self):
        model = StageModel()
        model.stage = omni.usd.get_context().get_stage()

        self.assertEqual(model.stage, omni.usd.get_context().get_stage())

    def test_value_changed_notification(self):
        model = StageModel()
        model.stage = omni.usd.get_context().get_stage()

        on_value_changed = mock.Mock()
        _subscription = model.subscribe_value_changed_fn(on_value_changed)

        stage = Usd.Stage.CreateInMemory()
        model.stage = stage
        self.assertTrue(on_value_changed.called)
        self.assertEqual(model.stage, stage)

    def test_get_value_as_string(self):
        model = StageModel()
        model.stage = Usd.Stage.CreateInMemory()
        self.assertRegex(model.get_value_as_string(), r".*Anonymous Stage.*")


class ModeModelTest(omni.kit.test.AsyncTestCase):
    def test_set_value(self):
        model = ModeModel()
        model.set_value(AssetMode.Stage.value)
        self.assertEqual(model.get_value_as_int(), AssetMode.Stage.value)

    def test_value_changed_notification(self):
        model = ModeModel()
        on_value_changed = mock.Mock()
        _subscription = model.subscribe_value_changed_fn(on_value_changed)

        model.set_value(AssetMode.Uri.value)
        self.assertTrue(on_value_changed.called)
        self.assertEqual(model.get_value_as_int(), AssetMode.Uri.value)
