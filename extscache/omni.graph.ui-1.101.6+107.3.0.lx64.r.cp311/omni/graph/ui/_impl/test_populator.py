"""Implementation of a test populator that reads from a file with tests listed in it.
See also the omni.graph.core/tools/log_to_tests.py script, which takes a build log as input and provides a list of
tests contained within it as output.
"""

from __future__ import annotations

import os
import sys
import unittest
from collections import defaultdict
from contextlib import suppress
from pathlib import Path

import carb
import omni.kit.app
from omni.kit.test import TestPopulator, get_tests_from_modules
from omni.kit.widget.filebrowser import FileBrowserItem
from omni.kit.window.filepicker import FilePickerDialog

# Type for collecting module information corresponding to extensions
ModuleMap_t = dict[str, tuple[str, bool]]

_LOG = bool(os.getenv("TESTS_DEBUG"))  # Environment variable to enable debugging of the test registration


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
    # This method was originally copied from omni.kit.test.exec_utils. If the version there is ever made public then
    # we can use it directly from there instead.

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


def get_module_to_extension_map() -> ModuleMap_t:
    """Returns a dictionary mapping the names of Python modules in an extension to (OwningExtension, EnabledState)
    e.g. for this extension it would contain {"omni.kit.test": (["omni.kit.test", True])}
    It will be expanded to include the implicit test modules added by the test management.
    """
    # This method was originally copied from omni.kit.test.exec_utils. If the version there is ever made public then
    # we can use it directly from there instead.

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


def get_tests_to_remove_from_modules(modules, log=_LOG):
    """Return the list of tests to be removed when a module is unloaded.
    This includes all tests registered or dynamically discovered from the list of modules and their .tests or
    .ogn.tests submodules. Keeping this separate from get_tests_from_modules() allows the import of all three related
    modules, while preventing duplication of their tests when all extension module tests are requested.

    Args:
        modules: List of modules to
    """
    # This method was originally copied from omni.kit.test.unittests. If the version there is ever made public then
    # we can use it directly from there instead.

    all_modules = modules
    all_modules += [module.tests for module in modules if hasattr(module, "tests")]
    all_modules += [module.ogn.tests for module in modules if hasattr(module, "ogn") and hasattr(module.ogn, "tests")]
    return get_tests_from_modules(all_modules, log)


def decompose_test_list(
    test_list: list[str],
) -> tuple[list[unittest.TestCase], set[str], set[str], defaultdict[str, set[str]]]:
    """Read in the given log file and return the list of tests that were run, in the order in which they were run.

    If any modules containing the tests in the log are not currently available then they are reported for the user
    to intervene and most likely enable the owning extensions.

    Args:
        test_list: List of tests to decompose and find modules and extensions for

    Returns:
        Tuple of (tests, not_found, extensions, modules) gleaned from the log file
            tests: List of unittest.TestCase for all tests named in the log file, in the order they appeared
            not_found: Name of tests whose location could not be determined, or that did not exist
            extensions: Name of extensions containing modules that look like they contain tests from "not_found"
            modules: Map of extension to list of modules where the extension is enabled but the module potentially
            containing the tests from "not_found" has not been imported.

    """
    module_map = get_module_to_extension_map()

    not_found = set()  # The set of full names of tests whose module was not found
    # Map of enabled extensions to modules in them that contain tests in the log but which are not imported
    modules_not_imported = defaultdict(set)
    test_names = []
    modules_found = set()  # Modules matching the tests
    extensions_to_enable = set()

    # Walk the test list and parse out all of the test run information
    for test_name in test_list:
        test_info = extension_from_test_name(test_name, module_map)
        if test_info is None:
            not_found.add(test_name)
        else:
            (ext_id, ext_enabled, module, module_imported) = test_info
            if ext_enabled:
                if module is None:
                    not_found.add(test_name)
                elif not module_imported:
                    modules_not_imported[ext_id].add(module)
                else:
                    test_names.append(test_name)
                    modules_found.add(module)
            else:
                extensions_to_enable.add(ext_id)

    # Carefully find all of the desired test cases, preserving the order in which they were encountered since that is
    # a key feature of reading tests from a log
    test_mapping: dict[str, unittest.TestCase] = {}  # Mapping of test name onto discovered test case for running
    for module in modules_found:
        # Find all of the individual tests in the TestCase classes and add those that match any of the disabled patterns
        # Uses get_tests_to_remove_from_modules because it considers possible tests and ogn.tests submodules
        test_cases = get_tests_to_remove_from_modules([module])
        for test_case in test_cases:
            if test_case.id() in test_names:
                test_mapping[test_case.id()] = test_case
    tests: list[unittest.TestCase] = []
    for test_name in test_names:
        if test_name in test_mapping:
            tests.append(test_mapping[test_name])

    return (tests, not_found, extensions_to_enable, modules_not_imported)


# ==============================================================================================================
class TestPopulateFromFile(TestPopulator):
    """Implementation of the TestUiPopulator that returns a list of all tests listed, one per line, in a text file
    Args:
        _test_file_path: Text file chosen for populating the test list
        _test_file_picker: UI Widget with a file picker for selecting the file containing the tests
    """

    def __init__(self):
        super().__init__(
            "From File",
            "Read tests, one per line containing their fully qualified name, from a text file",
        )
        self._test_file_picker: FilePickerDialog = None
        self._test_file_path: Path = None
        self.tests = {}

    # --------------------------------------------------------------------------------------------------------------
    def destroy(self):
        self._test_file_path = None
        if self._test_file_picker is not None:
            del self._test_file_picker
            self._test_file_picker = None

    # --------------------------------------------------------------------------------------------------------------
    def get_tests(self, call_when_done: callable):
        def __on_click_cancel(file_name: str, directory_name: str):
            """Callback executed when the user cancels the text file open dialog"""
            self._test_file_picker.hide()
            call_when_done(canceled=True)

        def __on_text_file_chosen(filename: str, dirname: str):
            """Callback executed when the user has selected a new text file from which to extract tests"""
            self._test_file_picker.hide()
            if dirname is None or filename is None:
                return
            self._test_file_path = Path(dirname) / filename
            try:
                test_list = []
                with open(self._test_file_path, "r", encoding="utf-8") as test_fd:
                    for line in test_fd:
                        if line.find(".") > 0:
                            test_list.append(line.rstrip())
            except IOError:
                carb.log_warn(f"Test file {self._test_file_path} could not be read to look for tests - ignoring")
                return

            (self.tests, not_found, disabled_extensions, missing_modules) = decompose_test_list(test_list)
            # Inform the user if any tests could not be interpreted according to known extensions.
            if not_found:
                carb.log_warn(f"No information available for {len(not_found)} tests")

            # Inform the user if tests come from known locations in disabled extensions
            if disabled_extensions:
                carb.log_warn(f"Found tests that belong to {len(disabled_extensions)} disabled extensions")

            # Inform the user that although they have extensions enabled containing tests, their tests module has not
            # been imported.
            if missing_modules:
                carb.log_warn(f"Found tests in modules from {len(missing_modules)} extensions that are not imported")

            call_when_done()

        def __on_filter_item(item: FileBrowserItem) -> bool:
            """Filter helper that makes only .txt files show in the text file picker dialog"""
            if not item or item.is_folder:
                return True
            if self._test_file_picker.current_filter_option == 0:
                # Show only files with listed extensions
                return item.path.endswith(".txt")
            # Show All Files (*)
            return True

        if self._test_file_picker is None:
            self._test_file_picker = FilePickerDialog(
                "Select Test File",
                apply_button_label="Select",
                allow_multi_selection=False,
                click_apply_handler=__on_text_file_chosen,
                click_cancel_handler=__on_click_cancel,
                item_filter_options=["All Test Files (*.txt)", "All Files (*.*)"],
                item_filter_fn=__on_filter_item,
                error_handler=carb.log_error,
            )
        else:
            self._test_file_picker.show()
