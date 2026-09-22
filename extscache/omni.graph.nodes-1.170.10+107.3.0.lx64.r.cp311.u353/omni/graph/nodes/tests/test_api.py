"""Testing the stability of the API in this module"""

import omni.graph.core.tests as ogts
import omni.graph.nodes as ognd
from omni.graph.tools.tests.internal_utils import _check_module_api_consistency, _check_public_api_contents


# ======================================================================
class _TestOmniGraphNodesApi(ogts.OmniGraphTestCase):
    _UNPUBLISHED = ["bindings", "ogn", "tests"]

    async def test_api(self):
        _check_module_api_consistency(ognd, self._UNPUBLISHED)  # noqa: PLW0212
        _check_module_api_consistency(  # noqa: PLW0212
            ognd.tests, ["create_prim_with_everything", "bundle_test_utils", "fsd_helpers"], is_test_module=True
        )

    async def test_api_features(self):
        """Test that the known public API features continue to exist"""
        _check_public_api_contents(ognd, [], self._UNPUBLISHED, only_expected_allowed=True)  # noqa: PLW0212
        _check_public_api_contents(  # noqa: PLW0212
            ognd.tests,
            [
                "BundleInspectorResults_t",
                "BundleResultKeys",
                "bundle_inspector_results",
                "enable_debugging",
                "filter_bundle_inspector_results",
                "get_bundle_with_all_results",
                "prim_with_everything_definition",
                "verify_bundles_are_equal",
            ],
            [],
            only_expected_allowed=False,
        )
