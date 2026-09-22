## Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##
from ..search_engine_registry import SearchEngineRegistry
from ..abstract_search_model import AbstractSearchItem
from ..abstract_search_model import AbstractSearchModel
import omni.kit.test
from unittest.mock import Mock


class TestSearchItem(AbstractSearchItem):
    pass


class TestSearchModel(AbstractSearchModel):
    running_search = None

    def __init__(self, **kwargs):
        super().__init__()
        self.__items = [TestSearchItem()]

    def destroy(self):
        self.__items = []

    @property
    def items(self):
        return self.__items


class TestSearchCore(omni.kit.test.AsyncTestCase):
    async def test_registry(self):
        test_name = "TEST_SEARCH"
        self._subscription = SearchEngineRegistry().register_search_model(test_name, TestSearchModel)

        self.assertIn(test_name, SearchEngineRegistry().get_search_names())
        self.assertIn(test_name, SearchEngineRegistry().get_available_search_names("DummyServer"))

        self.assertIs(TestSearchModel, SearchEngineRegistry().get_search_model(test_name))

        self._subscription = None

        self.assertNotIn(test_name, SearchEngineRegistry().get_search_names())

    async def test_event_subscription(self):
        mock_callback = Mock()

        self._sub = SearchEngineRegistry().subscribe_engines_changed(mock_callback)
        self._added_model = SearchEngineRegistry().register_search_model("dummy", TestSearchModel)
        mock_callback.assert_called_once()

        mock_callback.reset_mock()
        self._added_model = None
        mock_callback.assert_called_once()

    async def test_item_changed_subscription(self):
        mock_callback = Mock()

        model = TestSearchModel()
        self._sub = model.subscribe_item_changed(mock_callback)

        model._item_changed()
        mock_callback.assert_called_once()
