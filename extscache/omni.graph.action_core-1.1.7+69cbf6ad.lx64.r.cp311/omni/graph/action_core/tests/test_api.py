"""Testing the stability of the API in this module"""

import omni.graph.action_core as ogac
import omni.graph.core.tests as ogts
from omni.graph.tools.tests.internal_utils import _check_module_api_consistency, _check_public_api_contents


# ======================================================================
class _TestOmniGraphActionApi(ogts.OmniGraphTestCase):
    _UNPUBLISHED = ["bindings", "ogn", "tests", "omni"]

    async def test_api(self):
        _check_module_api_consistency(ogac, self._UNPUBLISHED)  # noqa: PLW0212
        _check_module_api_consistency(ogac.tests, is_test_module=True)  # noqa: PLW0212

    async def test_api_features(self):
        """Test that the known public API features continue to exist"""
        _check_public_api_contents(
            ogac, ["get_interface"], self._UNPUBLISHED, only_expected_allowed=True
        )  # noqa: PLW0212
        _check_public_api_contents(ogac.tests, [], [], only_expected_allowed=True)  # noqa: PLW0212
