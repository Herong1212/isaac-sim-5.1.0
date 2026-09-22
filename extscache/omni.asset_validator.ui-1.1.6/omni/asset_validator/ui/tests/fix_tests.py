# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
import unittest.mock as mock

import omni.kit.test
from omni.asset_validator.core import Issue, LayerId, PrimId, PropertyId, SpecId, SpecIdList, StageId
from omni.asset_validator.ui import FixAtItem, FixAtModel
from pxr import Sdf


class FixAtModelTest(omni.kit.test.AsyncTestCase):
    def test_set_value(self):
        path = Sdf.Path("/test")
        spec_id = SpecId(layer_id=None, path=path)
        fix_sites = [spec_id]

        model = FixAtModel(fix_sites)
        self.assertEqual(model.get_value_as_int(), 0)

    def test_fix_site(self):
        path = Sdf.Path("/test")
        spec_id = SpecId(layer_id=None, path=path)
        fix_sites = [spec_id]

        model = FixAtModel(fix_sites)
        self.assertEqual(model.fix_site, spec_id)

    def test_value_changed_notification(self):
        path1 = Sdf.Path("/test1")
        path2 = Sdf.Path("/test2")
        spec_id1 = SpecId(layer_id=None, path=path1)
        spec_id2 = SpecId(layer_id=None, path=path2)
        fix_sites = [spec_id1, spec_id2]

        model = FixAtModel(fix_sites)

        on_value_changed = mock.Mock()
        _subscription = model.subscribe_value_changed_fn(on_value_changed)
        model.set_value(1)

        self.assertTrue(on_value_changed.called)
        self.assertEqual(model.get_value_as_int(), 1)
        self.assertEqual(model.fix_site, spec_id2)


class FixAtItemTest(omni.kit.test.AsyncTestCase):
    def test_format_layer_id(self):
        layer_id = LayerId(identifier="/test/layer.usd")
        spec_id = SpecId(layer_id=layer_id, path=Sdf.Path("/test"))
        issue = Issue(at=layer_id)

        item = FixAtItem(issue, spec_id)
        self.assertEqual(item.model.get_value_as_string(), "Prim(/test) at Layer(./layer.usd)")

    def test_format_prim_id(self):
        layer_id = LayerId(identifier="/test/layer.usd")
        stage_id = StageId(root_layer=layer_id)
        prim_id = PrimId(
            stage_id=stage_id,
            spec_ids=SpecIdList(
                root_path=Sdf.Path("/test"), spec_ids=[SpecId(layer_id=layer_id, path=Sdf.Path("/test"))]
            ),
        )
        spec_id = SpecId(layer_id=layer_id, path=Sdf.Path("/test"))
        issue = Issue(at=prim_id)

        item = FixAtItem(issue, spec_id)
        self.assertEqual(item.model.get_value_as_string(), "Prim(/test) at Layer(./layer.usd)")

    def test_format_property_id(self):
        layer_id = LayerId(identifier="/test/layer.usd")
        stage_id = StageId(root_layer=layer_id)
        prim_id = PrimId(
            stage_id=stage_id,
            spec_ids=SpecIdList(
                root_path=Sdf.Path("/test"), spec_ids=[SpecId(layer_id=layer_id, path=Sdf.Path("/test"))]
            ),
        )
        property_id = PropertyId(prim_id=prim_id, path=Sdf.Path("/test.prop"))
        spec_id = SpecId(layer_id=layer_id, path=Sdf.Path("/test.prop"))
        issue = Issue(at=property_id)

        item = FixAtItem(issue, spec_id)
        self.assertEqual(item.model.get_value_as_string(), "Property(/test.prop) at Layer(./layer.usd)")

    def test_format_relative_path(self):
        layer_id = LayerId(identifier="/test/dir/layer.usd")
        spec_id = SpecId(layer_id=LayerId(identifier="/test/other/fix.usd"), path=Sdf.Path("/test"))
        issue = Issue(at=layer_id)

        item = FixAtItem(issue, spec_id)
        self.assertEqual(item.model.get_value_as_string(), "Prim(/test) at Layer(../other/fix.usd)")
