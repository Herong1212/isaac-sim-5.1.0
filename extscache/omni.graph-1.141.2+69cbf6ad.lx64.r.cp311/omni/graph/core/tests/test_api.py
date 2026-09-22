"""Testing the stability of the API in this module"""

import omni.graph.core as og
import omni.graph.core._impl.commands as ogc
import omni.graph.core.types as ot
import omni.kit
from omni.graph.tools.tests.internal_utils import _check_module_api_consistency, _check_public_api_contents


# ======================================================================
class _TestOmniGraphApi(omni.kit.test.AsyncTestCase):
    _UNPUBLISHED = [
        "bindings",  # Bindings are picked up via a named import
        "omni",  # Picked up as part of the import namespace chain
        "commands",  # Commands are their own module
        "ogn",  # From the AutoNode test generation
        "types",  # Separate types module, not part of the main one
        "tests",  # From the AutoNode test definition
    ]

    async def test_api(self):
        _check_module_api_consistency(og.tests, [], is_test_module=True)  # noqa: PLW0212
        _check_module_api_consistency(ot)  # noqa: PLW0212
        _check_module_api_consistency(ogc, ogc._HIDDEN)  # noqa: PLW0212
        # Since the og module also contains all of the previously exposed objects for backward compatibility, they
        # have to be added to the list of unpublished elements here as they, rightly, do not appear in __all__
        all_unpublished = self._UNPUBLISHED + og._HIDDEN + ogc._HIDDEN  # noqa: PLW0212  # noqa: PLW0212
        _check_module_api_consistency(og, all_unpublished)  # noqa: PLW0212

    async def test_api_features(self):
        """Test that the known public API features continue to exist"""
        _check_public_api_contents(
            og,
            [  # noqa: PLW0212
                "attribute_value_as_usd",
                "AttributeDataValueHelper",
                "AttributeValueHelper",
                "Bundle",
                "BundleContainer",
                "BundleContents",
                "cmds",
                "Controller",
                "data_shape_from_type",
                "Database",
                "DataView",
                "DataWrapper",
                "Device",
                "Dtype",
                "DynamicAttributeAccess",
                "DynamicAttributeInterface",
                "ExtensionInformation",
                "get_global_orchestration_graphs",
                "get_graph_settings",
                "get_port_type_namespace",
                "GraphController",
                "GraphSettings",
                "in_compute",
                "is_attribute_plain_data",
                "is_in_compute",
                "MetadataKeys",
                "NodeController",
                "ObjectLookup",
                "OmniGraphError",
                "OmniGraphInspector",
                "OmniGraphValueError",
                "PerNodeKeys",
                "python_value_as_usd",
                "ReadOnlyError",
                "resolve_base_coupled",
                "resolve_fully_coupled",
                "RuntimeAttribute",
                "Settings",
                "ThreadsafetyTestUtils",
                "TypedValue",
                "typing",
                "WrappedArrayType",
            ],
            self._UNPUBLISHED,
            only_expected_allowed=False,
        )
