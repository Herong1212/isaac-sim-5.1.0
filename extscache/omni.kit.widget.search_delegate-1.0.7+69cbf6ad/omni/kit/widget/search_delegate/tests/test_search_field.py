## Copyright (c) 2018-2019, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##
from unittest.mock import patch, MagicMock
import omni.kit.ui_test as ui_test
from omni.kit.ui_test.query import MenuRef
from omni.ui.tests.test_base import OmniUiTest
from omni.kit.search_core import AbstractSearchModel, AbstractSearchItem, SearchEngineRegistry
from ..widget import SearchField
from ..model import SearchResultsModel


class MockSearchEngineRegistry(MagicMock):
    def get_search_names():
        return "test_search"

    def get_search_model(_: str):
        return MockSearchModel


class MockSearchItem(AbstractSearchItem):
    def __init__(self, name: str, path: str):
        super().__init__()
        self._name = name
        self._path = path

    @property
    def name(self):
        return self._name

    @property
    def path(self):
        return self._path


class MockSearchModel(AbstractSearchModel):
    def __init__(self, search_text: str, current_dir: str):
        super().__init__()
        self._items = []
        search_words = search_text.split(" ")
        # Return mock results from input search text
        for search_word in search_words:
            name = f"{search_word}.usd"
            self._items.append(MockSearchItem(name, f"{current_dir}/{name}"))

    @property
    def items(self):
        return self._items


class TestSearchField(OmniUiTest):
    async def setUp(self):
        self._search_results = None

    async def tearDown(self):
        if self._search_results:
            self._search_results.destroy()
        self._search_results = None

    def _on_search(self, search_results: SearchResultsModel):
        self._search_results = search_results

    async def test_search_succeeds(self):
        """Testing search function successfully returns search results"""
        window = await self.create_test_window()
        with window.frame:
            under_test = SearchField(self._on_search)
            under_test.build_ui()

        search_words = ["foo", "bar"]
        with patch("omni.kit.widget.search_delegate.widget.SearchEngineRegistry", return_value=MockSearchEngineRegistry):
            under_test.search_dir = "C:/my_search_dir"
            under_test.search(search_words)

        # Assert the the search generated the expected results
        results = self._search_results.get_item_children(None)
        self.assertEqual(
            [f"{under_test.search_dir}/{w}.usd" for w in search_words],
            [result.path for result in results]
        )

        for result in results:
            thumbnail = await result.get_custom_thumbnails_for_folder_async()
            self.assertEqual(thumbnail, {})

        self.assertTrue(under_test.visible)
        under_test.destroy()

    async def test_setting_search_dir_triggers_search(self):
        """Testing that when done editing the search field, executes the search"""
        window = await self.create_test_window()
        mock_search = MagicMock()
        with window.frame:
            with patch.object(SearchField, "search") as mock_search:
                under_test = SearchField(None)
                under_test.build_ui()
                # Procedurally set search directory and search field
                search_words = ["foo", "bar"]
                under_test.search_dir = "C:/my_search_dir"
                under_test._on_begin_edit(None)
                under_test._search_field.model.set_value(" ".join(search_words))
                under_test._on_end_edit(None)

        # Assert that the search is executed
        mock_search.assert_called_once_with(search_words)

        under_test.destroy()

    async def test_engine_menu(self):
        window = await self.create_test_window(block_devices=False)
        with window.frame:
            under_test = SearchField(None)
            under_test.build_ui()
        
        self._subscription = SearchEngineRegistry().register_search_model("TEST_SEARCH", MockSearchModel)
        window_ref = ui_test.WindowRef(window, "")
        button_ref = window_ref.find_all("**/Button[*].identifier=='show_engine_menu'")[0]
        await button_ref.click()

        self.assertTrue(under_test.enabled)

        self.assertIsNotNone(under_test._search_engine_menu)
        self.assertTrue(under_test._search_engine_menu.shown)

        menu_ref = MenuRef(under_test._search_engine_menu, "")
        menu_items = menu_ref.find_all("**/")
        self.assertEqual(len(menu_items), 1)
        self.assertEqual(menu_items[0].widget.text, "TEST_SEARCH")

        under_test.destroy()
        self._subscription = None

    async def test_edit_search(self):
        window = await self.create_test_window(block_devices=False)
        with window.frame:
            under_test = SearchField(self._on_search)
            under_test.build_ui()
        
        self._subscription = SearchEngineRegistry().register_search_model("TEST_SEARCH", MockSearchModel)
        search_words = ["foo", "bar"]
        under_test.search_dir = "C:/my_search_dir"
        under_test._on_begin_edit(None)
        under_test._search_field.model.set_value(" ".join(search_words))
        under_test._on_end_edit(None)
        results = self._search_results.get_item_children(None)
        self.assertEqual(len(results), 2)

        # Remove first search
        window_ref = ui_test.WindowRef(window, "")
        close_ref = window_ref.find_all(f"**/Button[*].identifier=='search_word_button'")[0]
        await close_ref.click()
        results = self._search_results.get_item_children(None)
        self.assertEqual(len(results), 1)

        # Clear search
        await self.wait_n_updates()
        clear_ref = ui_test.WidgetRef(under_test._clear_button, "", window=window)
        await clear_ref.click()
        self.assertIsNone(self._search_results)

        self._subscription = None
        under_test.destroy()
