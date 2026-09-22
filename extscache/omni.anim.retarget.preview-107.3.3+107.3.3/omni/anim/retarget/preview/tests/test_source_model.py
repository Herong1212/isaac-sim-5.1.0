# Copyright (c) 2021-2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

import omni.kit.app
import omni.kit.test
import omni.usd
import omni.ui as ui
import pathlib
from omni.usd.commands import MovePrimCommand, DeletePrimsCommand
from omni.kit.test_suite.helpers import open_stage
from functools import partial
from ..model.source_model import ObjectSource, SourceModel, SourceItemModel, SourceSetModel


EXTENSION_FOLDER_PATH = pathlib.Path(
    omni.kit.app.get_app().get_extension_manager().get_extension_path_by_module(__name__)
)
TEST_DATA_PATH = EXTENSION_FOLDER_PATH.joinpath("data/tests")


class TestSourceModel(omni.kit.test.AsyncTestCase):
    async def setUp(self):
        self._model_changed = False
        self._changed_item = None

        self.context = omni.usd.get_context()
        self.assertIsNotNone(self.context)

        usd_path = TEST_DATA_PATH.absolute()
        # Load any (preferably small) USD file, contents do not matter.
        test_file_path = str(usd_path.joinpath("file_loader_tests.usda").absolute())
        await open_stage(test_file_path, self.context)
        self.stage = self.context.get_stage()
        self.assertIsNotNone(self.stage)

    async def tearDown(self):
        self.context.close_stage()
        self.stage = None
        self.context = None

    async def test_model(self):
        ## Construct
        model = SourceModel()
        self.assertTrue(model.is_empty())
        self.assertFalse(model.exists_in_source_stage)
        self.assertFalse(model.is_external)
        self.assertIsNone(model.source_stage)

        ## Value changes
        value_changed_sub = model.add_value_changed_fn(self._on_source_changed)
        prim_name = 'MyPrim'
        prim_path = '/World/' + prim_name

        model.set_source_path_in_stage(prim_path)
        self.assertEqual(model.source_path_in_stage, prim_path)
        self.assertEqual(model.path_name, prim_name)
        self.assertFalse(model.is_external)
        self._assert_model_changed(True)

        model.set_source_path_in_stage(prim_path, self.stage)
        self.assertEqual(model.source_stage, self.stage)
        self._assert_model_changed(True)

        target_path = '/World/Some/Other/Path'
        model.target_path_in_stage = target_path
        self.assertEqual(model.target_path_in_stage, target_path)
        # Setting the target path does not trigger value_changed by design
        self._assert_model_changed(False)

        source_url = None
        model.set_source_url(source_url)
        self.assertFalse(model.is_external)
        self.assertFalse(model.is_read_only())
        self.assertTrue(model.exists_in_source_stage)
        self.assertIsNone(model.source_url)
        self.assertEqual(model.source_type, ObjectSource.MAIN_STAGE)
        self.assertFalse(model.is_empty())
        self._assert_model_changed(True)

        model.set_removed()
        self.assertFalse(model.exists_in_source_stage)
        self.assertTrue(model.is_read_only())
        self._assert_model_changed(True)

        source_url = 'omniverse://test.usd'  # Some arbitrary URL, no checks are made in SourceModel
        model.set_source_url(source_url, False)
        self.assertTrue(model.is_external)
        self.assertFalse(model.exists_in_source_stage)
        self.assertEqual(model.source_url, source_url)
        self.assertEqual(model.source_type, ObjectSource.URL)
        self._assert_model_changed(True)

        model.remove_value_changed_fn(value_changed_sub)

        item_model = SourceItemModel(model)
        self.assertEqual(item_model.model, model)
        item_model = SourceItemModel()
        self.assertIsNotNone(item_model.model)

    async def test_source_set_model_api(self):
        context_name = 'TestSourceModel test context'
        context = omni.usd.create_context(context_name)
        model_1 = SourceModel()
        path_1 = '/World/Path'
        model_1.set_source_path_in_stage(path_1)
        path_2 = '/World/Some/Other/Path'
        model_2 = SourceItemModel()
        model_2.model.set_source_path_in_stage(path_2)

        ## Construct
        set_model = SourceSetModel(context)
        self.assertIsNone(set_model.get_current_source())

        changed_sub = set_model.add_item_changed_fn(self._on_source_set_changed)

        ## Add item
        set_model.add_source(model_1)
        self._assert_item_changed(SourceItemModel(model_1))
        self.assertEqual(set_model.current_index, 0)
        self.assertEqual(set_model.get_current_source(), model_1)

        set_model.add_source(model_2)
        self._assert_item_changed(model_2)
        self.assertEqual(set_model.current_index, 1)
        self.assertEqual(set_model.get_current_source(), model_2.model)

        set_model.add_source(SourceItemModel(model_1), False)
        self._assert_item_changed(SourceItemModel(model_1))
        self.assertEqual(set_model.current_index, 1)
        self.assertEqual(set_model.get_current_source(), model_2.model)

        ## Change current
        success = set_model.set_current(-1)
        self._assert_item_changed(None, False)
        self.assertEqual(set_model.current_index, 1)
        self.assertFalse(success)

        success = set_model.set_current(3)
        self._assert_item_changed(None, False)
        self.assertEqual(set_model.current_index, 1)
        self.assertFalse(success)

        success = set_model.set_current(2)
        self._assert_item_changed(None, True)
        self.assertEqual(set_model.current_index, 2)
        self.assertTrue(success)

        ## Find
        def is_path_equal(path: str, model: SourceModel) -> bool:
            return model.source_path_in_stage == path

        def const_true(_) -> bool:
            return True

        sources_indices = set_model.find_source(const_true)
        self.assertEqual(len(sources_indices), 3)
        sources = [a[0] for a in sources_indices]
        indices = [a[1] for a in sources_indices]
        self.assertListEqual(indices, [0, 1, 2])
        self.assertListEqual(sources, [model_1, model_2.model, model_1])
        self._assert_item_changed(None, False)

        sources_indices = set_model.find_source(partial(is_path_equal, path_1))
        indices = [a[1] for a in sources_indices]
        sources = [a[0] for a in sources_indices]
        self.assertEqual(len(sources_indices), 2)
        self.assertListEqual(indices, [0, 2])
        self.assertListEqual(sources, [model_1, model_1])

        ## Change item property
        model_1.set_source_path_in_stage('dummy')
        self._assert_item_changed(SourceItemModel(model_1), True)

        ## Clear
        set_model.clear()
        self._assert_item_changed(None, True)
        self.assertIsNone(set_model.get_current_source())
        indices = set_model.find_source(const_true)
        self.assertEqual(len(indices), 0)

        set_model.remove_item_changed_fn(changed_sub)

    async def test_source_set_model_usd_snyc(self):
        stage = self.stage
        prim_path_orig = '/World/prim'

        stage.DefinePrim(prim_path_orig)

        model = SourceModel()
        model.set_source_path_in_stage(prim_path_orig, stage)
        model.set_source_url(None, True)

        set_model = SourceSetModel()
        set_model.add_source(model)
        current_model = set_model.get_current_source()
        changed_sub = set_model.add_item_changed_fn(self._on_source_set_changed)

        ## Rename prim
        prim_path_new = '/World/prim_new'
        MovePrimCommand(prim_path_orig, prim_path_new).do()
        await omni.kit.app.get_app().next_update_async()
        self._assert_item_changed(SourceItemModel(model))
        self.assertEqual(current_model.source_path_in_stage, prim_path_new)
        self.assertTrue(current_model.exists_in_source_stage)

        ## Delete prim
        DeletePrimsCommand([prim_path_new]).do()
        await omni.kit.app.get_app().next_update_async()
        self._assert_item_changed(SourceItemModel(model))
        self.assertFalse(current_model.exists_in_source_stage)
        self.assertEqual(current_model.source_path_in_stage, prim_path_new)

        # Change source stage, Rename/Delete has no effect when the stage is different
        stage.DefinePrim(prim_path_orig)
        model.set_source_path_in_stage(prim_path_orig, None)
        self._assert_item_changed(SourceItemModel(model))

        MovePrimCommand(prim_path_orig, prim_path_new).do()
        await omni.kit.app.get_app().next_update_async()
        self._assert_item_changed(None, False)

        DeletePrimsCommand([prim_path_new]).do()
        await omni.kit.app.get_app().next_update_async()
        self._assert_item_changed(None, False)

        set_model.remove_item_changed_fn(changed_sub)

    def _on_source_changed(self, model: ui.AbstractValueModel):
        self._model_changed = True

    def _on_source_set_changed(self, item_model: ui.AbstractItemModel, item: ui.AbstractItem):
        self._model_changed = True
        self._changed_item = item

    def _assert_model_changed(self, changed: bool = True):
        self.assertEqual(changed, self._model_changed)
        self._model_changed = False

    def _assert_item_changed(self, item, changed: bool = True):
        self.assertEqual(changed, self._model_changed)
        if item is not None:
            self.assertEqual(item.model, self._changed_item.model)
        else:
            self.assertIsNone(self._changed_item)
        self._model_changed = False
        self._changed_item = None
