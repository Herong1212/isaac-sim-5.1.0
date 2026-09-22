"""
Explicitly import the test utilities that will be part of the public interface
This way you can do things like:
    import omni.graph.nodes.tests as ognt
    new_prim = ognt.bundle_inspector_output()
"""

from .bundle_test_utils import (
    BundleInspectorResults_t,
    BundleResultKeys,
    bundle_inspector_results,
    enable_debugging,
    filter_bundle_inspector_results,
    get_bundle_with_all_results,
    prim_with_everything_definition,
    verify_bundles_are_equal,
)

__all__ = [
    "BundleInspectorResults_t",
    "BundleResultKeys",
    "bundle_inspector_results",
    "enable_debugging",
    "filter_bundle_inspector_results",
    "get_bundle_with_all_results",
    "prim_with_everything_definition",
    "verify_bundles_are_equal",
]

scan_for_test_modules = True
"""The presence of this object causes the test runner to automatically scan the directory for unit test cases"""
