## Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##
import os, shutil
import random
import omni.kit.test
import omni.appwindow
import omni.kit.app

from typing import List
from omni.kit import ui_test
from omni.ui.tests.test_base import OmniUiTest
from omni.kit.search_core import SearchEngineRegistry, AbstractSearchModel, AbstractSearchItem
from ..dialog import FilePickerDialog
from .test_utils import time_logger


class MockSearchItem(AbstractSearchItem):
    def __init__(self, name: str, path: str):
        self._name = name
        self._path = path

    @property
    def name(self):
        return self._name

    @property
    def path(self):
        return self._path


class MockSearchModel(AbstractSearchModel):
    """SearchModel class for the mock search engine."""
    def __init__(self, **kwargs):
        super().__init__()
        self._items = []
        search_text = kwargs['search_text']
        current_dir = kwargs['current_dir']

        with os.scandir(current_dir) as it:
            for entry in it:
                if search_text in entry.name:
                    self._items.append(MockSearchItem(entry.name, entry.path))

    def destroy(self):
        self._items = []

    @property
    def items(self):
        return self._items


@time_logger
class TestSearchField(omni.kit.test.AsyncTestCase):
    """Testing omni.kit.window.filepicker.SearchField"""
    async def setUp(self):
        self._search_engine = "mock_search_model"
        self._search_sub = SearchEngineRegistry().register_search_model(self._search_engine, MockSearchModel)

    async def tearDown(self):
        self._search_sub = None

    def _create_test_dir(self, temp_files: List[str] = []):
        # Create test dir in temp area
        temp_path = os.path.join(omni.kit.test.get_test_output_path(), f"tmp{random.randint(0, int('0xffff', 16))}")
        temp_path = temp_path.replace("\\", "/")
        if os.path.exists(temp_path):
            os.rmdir(temp_path)
        os.mkdir(temp_path)

        for temp_file in temp_files:
            with open(f'{temp_path}/{temp_file}', 'w') as fp:
                pass
        return temp_path

    async def test_search_returns_expected(self):
        """Testing SearchField returns expected results"""
        # Create test dir and populate with test files
        temp_files = ["foo.usd", "foo.mdl", "foo_2.usd", "bar.usd", "bar.png", "foo_3.usd", "baz.png"]
        temp_path = self._create_test_dir(temp_files=temp_files)
        await ui_test.human_delay(2)

        # Create dialog and navigate to to test dir
        under_test = FilePickerDialog(
            "test_search_returns_expected",
            current_directory=temp_path,
            show_grid_view=True,
            show_only_collections=["my-computer"])
        await ui_test.human_delay(10)

        # Search for files using the search text, update the grid view.
        search_delegate = under_test._widget._default_search_delegate
        search_delegate._search_engine = self._search_engine

        search_text = "foo"
        search_delegate._search_field.model.set_value(search_text)
        search_delegate._on_end_edit(search_delegate._search_field.model)
        await ui_test.human_delay(20)

        # Confirm number of found files (should == 4)
        expected_result = [f for f in temp_files if search_text in f]
        search_model = under_test._widget._view._filebrowser._currently_visible_model
        self.assertEqual(len(expected_result), len(search_model.get_item_children(None)))

        # Cleanup
        shutil.rmtree(temp_path)
        under_test.destroy()

    async def test_changing_directory_while_searching(self):
        """Testing SearchField updates results when changing directory"""
        # Create test dirs
        temp_files = ["foo.usd", "foo.mdl", "foo_2.usd", "bar.usd", "bar.png", "foo_3.usd", "baz.png"]
        temp_path = self._create_test_dir(temp_files=temp_files)
        temp_path2 = self._create_test_dir(temp_files=[])
        await ui_test.human_delay(2)

        # Create dialog and navigate to to test dir
        under_test = FilePickerDialog(
            "test_changing_directory_while_searching",
            current_directory=temp_path,
            show_grid_view=True,
            show_only_collections=["my-computer"])
        await ui_test.human_delay(10)

        # Search for files using the search text, update the view.
        search_delegate = under_test._widget._default_search_delegate
        search_delegate._search_engine = self._search_engine

        search_text = "foo"
        search_delegate._on_begin_edit(search_delegate._search_field.model)
        search_delegate._search_field.model.set_value(search_text)
        search_delegate._on_text_edit(search_delegate._search_field.model)
        await ui_test.human_delay(20)

        # Confirm number of found files (should == 4).
        expected_result = [f for f in temp_files if search_text in f]
        search_model = under_test._widget._view._filebrowser._currently_visible_model
        self.assertEqual(len(expected_result), len(search_model.get_item_children(None)))

        # Change to second directory.  Wait a few frames, then confirm that search results have changed (0)
        under_test.set_current_directory(temp_path2)
        await ui_test.human_delay(20)
        search_model = under_test._widget._view._filebrowser._currently_visible_model
        self.assertEqual(0, len(search_model.get_item_children(None)))

        # Change back to first directory.  Wait a few frames, then confirm search results again.
        under_test.set_current_directory(temp_path)
        await ui_test.human_delay(20)
        search_model = under_test._widget._view._filebrowser._currently_visible_model
        self.assertEqual(len(expected_result), len(search_model.get_item_children(None)))

        # Cleanup
        shutil.rmtree(temp_path)
        shutil.rmtree(temp_path2)
        under_test.destroy()
