"""Testing the stability of the API in this module"""

import omni.graph.tools as ogt
import omni.graph.tools.ogn as ogn
import omni.kit
from omni.graph.tools.tests.internal_utils import _check_module_api_consistency, _check_public_api_contents


# ======================================================================
class _TestOmniGraphToolsApi(omni.kit.test.AsyncTestCase):
    _UNPUBLISHED = ["bindings", "ogn", "tests", "node_generator"]

    async def test_api(self):
        _check_module_api_consistency(
            ogt.tests,
            # make_docs_toc is enabled when tests run but not otherwise so its status is not helpful
            ["internal_utils", "deprecated_import", "make_docs_toc"],
            is_test_module=True,
        )
        _check_module_api_consistency(ogn, ogn._HIDDEN)  # noqa: PLW0212

        # Since the ogt module also contains all of the previously exposed objects for backward compatibility, they
        # have to be added to the list of unpublished elements here as they, rightly, do not appear in __all__.
        # There is also the rogue published deprecated function that is being used downstream and so has to be
        # omitted from the "in ogn but not ogt" list.
        all_unpublished = (
            self._UNPUBLISHED
            + [
                module_object
                for module_object in dir(ogn)
                if not module_object.startswith("_") and module_object not in ["supported_attribute_type_names"]
            ]
            + ["make_docs_toc"]
        )
        _check_module_api_consistency(ogt, all_unpublished)

    async def test_api_features(self):
        """Test that the known public API features continue to exist.
        Add any new symbols here that have been intentionally exposed as part of the omni.graph.tools module API.
        """
        _check_public_api_contents(
            ogt,
            [
                "build_directory_metadata",
                "dbg",
                "dbg_eval",
                "dbg_gc",
                "dbg_ui",
                "deprecated_constant_object",
                "deprecated_function",
                "DeprecatedClass",
                "DeprecatedDictConstant",
                "DeprecatedImport",
                "DeprecatedStringConstant",
                "DeprecateMessage",
                "DeprecationLevel",
                "destroy_property",
                "function_trace",
                "get_node_type_names_from_metadata",
                "import_tests_in_directory",
                "IndentedOutput",
                "make_nice_name",
                "RenamedClass",
                "shorten_string_lines_to",
                "supported_attribute_type_names",
            ],
            self._UNPUBLISHED,
            only_expected_allowed=False,
        )
