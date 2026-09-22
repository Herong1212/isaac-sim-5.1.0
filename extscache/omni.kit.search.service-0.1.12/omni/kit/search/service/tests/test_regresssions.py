from unittest.mock import Mock, patch

import omni.kit.test
from omni.kit.search_core import SearchLifetimeObject

from ..scripts.searchservice_model import NGSearchServiceModel


class TestSearchPlugin(omni.kit.test.AsyncTestCase):
    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)
        self.url = "omniverse://test_nucleus_server/Projects/DeepSearch/"
        self.query = "blue car"

    def get_search_model(self) -> NGSearchServiceModel:
        mock_callback = Mock()
        obj = SearchLifetimeObject(callback=mock_callback)
        model = NGSearchServiceModel(search_text=self.query, current_dir=self.url, search_lifetime=obj)
        obj = None
        return model

    async def test_get_prefixes(self) -> None:
        """Regression test for: https://omniverse-jirasw.nvidia.com/browse/OMFP-3284"""
        model = self.get_search_model()
        response = await model.get_prefixes(self.url)
        self.assertEqual(response, [])

    async def test_list(self) -> None:
        """Regression test for: https://omniverse-jirasw.nvidia.com/browse/OMFP-3284"""
        model = self.get_search_model()
        with patch.object(NGSearchServiceModel, "_search", autospec=True) as mock_search, patch.object(
            NGSearchServiceModel, "_ngsearch", autospec=True
        ) as mock_ngsearch:
            await model._NGSearchServiceModel__list()
            mock_search.assert_called()
            mock_search.assert_awaited()
            mock_ngsearch.assert_not_called()
