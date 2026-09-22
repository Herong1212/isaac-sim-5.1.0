from __future__ import annotations
from contextlib import suppress
from types import ModuleType
from typing import Dict, Tuple
import fnmatch
import sys
import unittest

import carb
import omni.kit.app

from .unittests import get_tests_to_remove_from_modules


# Type for collecting module information corresponding to extensions
ModuleMap_t = Dict[str, Tuple[str, bool]]


# ==============================================================================================================
def get_module_to_extension_map() -> ModuleMap_t:
    """Returns a dictionary mapping the names of Python modules in an extension to (OwningExtension, EnabledState)
    e.g. for this extension it would contain {"omni.kit.test": (["omni.kit.test", True])}
    It will be expanded to include the implicit test modules added by the test management.
    """
    module_map = {}
    manager = omni.kit.app.get_app().get_extension_manager()
    for extension in manager.fetch_extension_summaries():
        ext_id = None
        enabled = False
        with suppress(KeyError):
            if extension["enabled_version"]["enabled"]:
                ext_id = extension["enabled_version"]["id"]
                enabled = True
        if ext_id is None:
            try:
                ext_id = extension["latest_version"]["id"]
            except KeyError:
                # Silently skip any extensions that do not have enough information to identify them
                continue
        ext_dict = manager.get_extension_dict(ext_id)

        # Look for the defined Python modules, skipping processing of any extensions that have no Python modules
        try:
            module_list = ext_dict["python"]["module"]
        except (KeyError, TypeError):
            continue

        # Walk through the list of all modules independently as there is no guarantee they are related.
        for module in module_list:
            # Some modules do not have names, only paths - just ignore them
            with suppress(KeyError):
                module_map[module["name"]] = (ext_id, enabled)
                # Add the two test modules that are explicitly added by the testing system
                if not module["name"].endswith(".tests"):
                    module_map[module["name"] + ".tests"] = (ext_id, enabled)
                    module_map[module["name"] + ".ogn.tests"] = (ext_id, enabled)

    return module_map


# ==============================================================================================================
def extension_from_test_name(test_name: str, module_map: ModuleMap_t) -> tuple[str, bool, str, bool] | None:
    """Given a test name, return None if the extension couldn't be inferred from the name, otherwise a tuple
    containing the name of the owning extension, a boolean indicating if it is currently enabled, a string
    indicating in which Python module the test was found, and a boolean indicating if that module is currently
    imported, or None if it was not.

    Args:
        test_name: Full name of the test to look up
        module_map: Module to extension mapping. Passed in for sharing as it's expensive to compute.

    The algorithm walks backwards from the full name to find the maximum-length Python import module known to be
    part of an extension that is part of the test name. It does this because the exact import paths can be nested or
    not nested. e.g. omni.kit.window.tests is not part of omni.kit.window

    Extracting the extension from the test name is a little tricky but all of the information is available. Here is
    how it attempts to decompose a sample test name

    .. code-block:: text

        omni.graph.nodes.tests.tests_for_samples.TestsForSamples.test_for_sample
        +--------------+ +---+ +---------------+ +-------------+ +-------------+
        Import path      |     |                 |               |
                         Testing subdirectory    |               |
                               |                 |               |
                               Test File         Test Class      Test Name

    Each extension has a list of import paths of Python modules it explicitly defines, and in addition it will add
    implicit imports for .tests and .ogn.tests submodules that are not explicitly listed in the extension dictionary.

    With this structure the user could have done any of these imports:

    .. code-block:: python

        import omni.graph.nodes
        import omni.graph.nodes.tests
        import omni.graph.nodes.test_for_samples

    Each nested one may or may not have been exposed by the parent so it is important to do a greedy match.

    This is how the process of decoding works for this test:

    .. code-block:: text

        Split the test name on "."
            ["omni", "graph", "nodes", "tests", "tests_for_samples", "TestsForSamples", "test_for_sample"]
        Starting at the entire list, recursively remove one element until a match in the module dictionary is found
            Fail: "omni.graph.nodes.tests.tests_for_samples.TestsForSamples.test_for_sample"
            Fail: "omni.graph.nodes.tests.tests_for_samples.TestsForSamples"
            Fail: "omni.graph.nodes.tests.tests_for_samples"
            Succeed: "omni.graph.nodes.tests"
        If no success, of if sys.modules does not contain the found module:
            Return the extension id, enabled state, and None for the module
        Else:
            Check the module recursively for exposed attributes with the rest of the names. In this example:
                file_object = getattr(module, "tests_for_samples")
                class_object = getattr(file_object, "TestsForSamples")
                test_object = getattr(class_object, "test_for_sample")
                If test_object is valid:
                    Return the extension id, enabled state, and the found module
                Else:
                    Return the extension id, enabled state, and None for the module

    """
    class_elements = test_name.split(".")
    for el in range(len(class_elements), 0, -1):
        check_module = ".".join(class_elements[:el])
        # If the extension owned the module then process it, otherwise continue up to the parent element
        try:
            (ext_id, is_enabled) = module_map[check_module]
        except KeyError:
            continue

        # The module was found in an extension definition but not imported into the Python namespace yet
        try:
            module = sys.modules[check_module]
        except KeyError:
            return (ext_id, is_enabled, check_module, False)

        # This checks to make sure that the actual test is registered in the module that was found.
        # e.g. if the full name is omni.graph.nodes.tests.TestStuff.test_stuff then we would expect to find
        # a module named "omni.graph.nodes.tests" that contains "TestStuff", and the object "TestStuff" will
        # in turn contain "test_stuff".
        sub_module = module
        for elem in class_elements[el:]:
            sub_module = getattr(sub_module, elem, None)
            if sub_module is None:
                break
        return (ext_id, is_enabled, module, sub_module is not None)

    return None


# ==============================================================================================================
def test_only_extension_dependencies(ext_id: str) -> set[str]:
    """Returns a set of extensions with test-only dependencies on the given one.
    Not currently used as dynamically enabling random extensions is not stable enough to use here yet.
    """
    test_only_extensions = set()  # Set of extensions that are enabled only in testing mode
    manager = omni.kit.app.get_app().get_extension_manager()
    ext_dict = manager.get_extension_dict(ext_id)

    # Find the test-only dependencies that may also not be enabled yet
    if ext_dict and "test" in ext_dict:
        for test_info in ext_dict["test"]:
            try:
                new_extensions = test_info["dependencies"]
            except (KeyError, TypeError):
                new_extensions = []
            for new_extension in new_extensions:
                with suppress(KeyError):
                    test_only_extensions.add(new_extension)
    return test_only_extensions


# ==============================================================================================================
def find_disabled_tests() -> list[unittest.TestCase]:
    """Scan the existing tests and the extension.toml to find all tests that are currently disabled"""
    manager = omni.kit.app.get_app().get_extension_manager()

    # Find the per-extension list of (python_modules, disabled_patterns).
    def __get_disabled_patterns() -> list[tuple[list[ModuleType], list[str]]]:
        disabled_patterns = []
        summaries = manager.fetch_extension_summaries()
        for extension in summaries:
            try:
                if not extension["enabled_version"]["enabled"]:
                    continue
            except KeyError:
                carb.log_info(f"Could not find enabled state of extension {extension}")
                continue
            ext_id = extension["enabled_version"]["id"]
            ext_dict = manager.get_extension_dict(ext_id)

            # Look for the defined Python modules
            modules = []
            with suppress(KeyError, TypeError):
                modules += [sys.modules[module_info["name"]] for module_info in ext_dict["python"]["module"]]

            # Look for unreliable tests
            regex_list = []
            with suppress(KeyError, TypeError):
                test_info = ext_dict["test"]
                for test_details in test_info or []:
                    with suppress(KeyError):
                        regex_list += test_details["pythonTests"]["unreliable"]

            if regex_list:
                disabled_patterns.append((modules, regex_list))

        return disabled_patterns

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def _match(to_match: str, pattern: str) -> bool:
        """Match that supports wildcards and '!' to invert it"""
        should_match = True
        if pattern.startswith("!"):
            pattern = pattern[1:]
            should_match = False
        return should_match == fnmatch.fnmatch(to_match, pattern)

    tests = []
    for modules, regex_list in __get_disabled_patterns():
        # Find all of the individual tests in the TestCase classes and add those that match any of the disabled patterns
        # Uses get_tests_to_remove_from_modules because it considers possible tests and ogn.tests submodules
        test_cases = get_tests_to_remove_from_modules(modules)
        for test_case in test_cases:
            for regex in regex_list:
                if _match(test_case.id(), regex):
                    tests.append(test_case)
                    break

    return tests
