import asyncio
import fnmatch
import os
import random
import sys
import traceback
import unittest
from contextlib import suppress
from glob import glob
from importlib import import_module
from itertools import islice
from os.path import basename, dirname, isfile, join, splitext
from types import ModuleType
from typing import Callable, List

import carb
import carb.tokens
import omni.kit.app
import omni.kit.async_engine

from .async_unittest import AsyncTestSuite, AsyncTextTestRunner, OmniTestResult, AsyncTestCase
from .benchmark import BenchmarkResult
from .exttests import RunExtTests
from .reporter import TestReporter
from .sampling import SamplingFactor, get_tests_sampling_to_skip
from .teamcity import teamcity_message
from .test_reporters import _test_status_report
from .utils import get_ext_test_id, get_setting, get_test_output_path, get_argv


_extra_tests = []

def add_test_case_to_tested_extension(test_case: AsyncTestCase, phony_submodule: str = ""):
    ext_test_id = get_ext_test_id()
    test_case.__module__ = f"{ext_test_id}.tests.{phony_submodule}" if phony_submodule else f"{ext_test_id}.tests"
    for t in unittest.TestLoader().loadTestsFromTestCase(test_case):
        _extra_tests.append(t)


def _import_if_exist(module: str):
    try:
        return import_module(module)
    except ModuleNotFoundError as e:
        # doesn't exist if that is what we trying to import or namespace
        if e.name == module or module.startswith(e.name + "."):
            return None
        carb.log_error(
            f"Failed to import python module with tests: {module}. Error: {e}. Traceback:\n{traceback.format_exc()}"
        )
    except Exception as e:
        carb.log_error(
            f"Failed to import python module with tests: {module}. Error: {e}. Traceback:\n{traceback.format_exc()}"
        )


def _get_enabled_extension_modules(filter_fn: Callable[[str], bool] = None):
    manager = omni.kit.app.get_app().get_extension_manager()

    # For each extension get each python module it declares
    module_names = manager.get_enabled_extension_module_names()

    sys_modules = set()
    for name in module_names:
        if name in sys.modules:
            if filter_fn and not filter_fn(name):
                continue
            sys_modules.add(sys.modules[name])

        # Automatically look for and import '[some_module].tests' and '[some_module].ogn.tests' so that extensions
        # don't have to put tests into config files and import them all the time.
        for test_submodule in [f"{name}.tests", f"{name}.ogn.tests"]:
            if filter_fn and not filter_fn(test_submodule):
                continue
            if test_submodule in sys.modules:
                sys_modules.add(sys.modules[test_submodule])
            else:
                test_module = _import_if_exist(test_submodule)
                if test_module:
                    sys_modules.add(test_module)

    return sys_modules


# ----------------------------------------------------------------------
SCANNED_TEST_MODULES = {}  # Dictionary of moduleName: [dynamicTestModules]
_EXTENSION_DISABLED_HOOK = None  # Hook for monitoring extension state changes, to keep the auto-populated list synced
_LOG = bool(os.getenv("TESTS_DEBUG"))  # Environment variable to enable debugging of the test registration


# ----------------------------------------------------------------------
def remove_from_dynamic_test_cache(module_root):
    """Get the list of tests dynamically added to the given module directory (via "scan_for_test_modules")"""
    global SCANNED_TEST_MODULES
    for module_suffix in ["", ".tests", ".ogn.tests"]:
        module_name = module_root + module_suffix
        tests_to_remove = SCANNED_TEST_MODULES.get(module_name, [])
        if tests_to_remove:
            if _LOG:
                print(f"Removing {len(tests_to_remove)} tests from {module_name}")
            del SCANNED_TEST_MODULES[module_name]


# ----------------------------------------------------------------------
def _on_ext_disabled(ext_id, *_):
    """Callback executed when an extension has been disabled - scan for tests to remove"""
    config = omni.kit.app.get_app().get_extension_manager().get_extension_dict(ext_id)
    for node in ("module", "modules"):
        with suppress(KeyError):
            for module in config["python"][node]:
                remove_from_dynamic_test_cache(module["name"])


# ----------------------------------------------------------------------
def dynamic_test_modules(module_root: str, module_file: str) -> List[ModuleType]:
    """Import all of the test modules and return a list of the imports so that automatic test recognition works

    The normal test recognition mechanism relies on knowing all of the file names at build time. This function is
    used to support automatic recognition of all test files in a certain directory at run time.

    Args:
        module_root: Name of the module for which tests are being imported, usually just __name__ of the caller
        module_file: File from which the import is happening, usually just __file__ of the caller

    Usage:
        In the directory containing your tests add this line to the __init__.py file (creating the file if necessary):
            scan_for_test_modules = True
        It will pick up any Python files names testXXX.py or TestXXX.py and scan them for tests when the extension
        is loaded.

    Important:
        The __init__.py file must be imported with the extension. If you have a .tests module or .ogn.tests module
        underneath your main module this will happen automatically for you.

    Returns:
        List of modules that were added, each pointing to a file in which tests are contained
    """
    global _EXTENSION_DISABLED_HOOK
    global SCANNED_TEST_MODULES
    if module_root in SCANNED_TEST_MODULES:
        return SCANNED_TEST_MODULES[module_root]
    modules_imported = []
    for module_name in [basename(f) for f in glob(join(dirname(module_file), "*.py")) if isfile(f)]:
        if module_name != "__init__" and module_name.lower().startswith("test"):
            imported_module = f"{module_root}.{splitext(module_name)[0]}"
            modules_imported.append(import_module(imported_module))
    SCANNED_TEST_MODULES[module_root] = modules_imported

    # This is a singleton initialization. If ever any test modules are scanned then from then on monitor for an
    # extension being disabled so that the cached list can be cleared for rebuilding on the next run.
    if _EXTENSION_DISABLED_HOOK is None:
        hooks = omni.kit.app.get_app().get_extension_manager().get_hooks()
        _EXTENSION_DISABLED_HOOK = hooks.create_extension_state_change_hook(
            _on_ext_disabled,
            omni.ext.ExtensionStateChangeType.BEFORE_EXTENSION_DISABLE,
            ext_dict_path="python",
            hook_name="python.unit_tests",
        )

    return modules_imported


# ==============================================================================================================
def get_tests_to_remove_from_modules(modules, log=_LOG):
    """Return the list of tests to be removed when a module is unloaded.
    This includes all tests registered or dynamically discovered from the list of modules and their .tests or
    .ogn.tests submodules. Keeping this separate from get_tests_from_modules() allows the import of all three related
    modules, while preventing duplication of their tests when all extension module tests are requested.

    Args:
        modules: List of modules to
    """
    all_modules = modules
    all_modules += [module.tests for module in modules if hasattr(module, "tests")]
    all_modules += [module.ogn.tests for module in modules if hasattr(module, "ogn") and hasattr(module.ogn, "tests")]
    return get_tests_from_modules(all_modules, log)


# ==============================================================================================================
def get_tests_from_modules(modules, log=_LOG):
    """Return the list of tests registered or dynamically discovered from the list of modules"""
    loader = unittest.TestLoader()
    loader.suiteClass = AsyncTestSuite
    is_benchmark = get_setting("/exts/omni.kit.test/runAsBenchmark", False) or "--benchmark" in get_argv()
    # switch default prefix to benchmark if runAsBenchmark or benchmark is enabled
    loader.testMethodPrefix = "benchmark" if is_benchmark else "test"
    tests = []

    for module in modules:
        if log:
            carb.log_warn(f"Getting tests from module {module.__name__}")
        suite = loader.loadTestsFromModule(module)
        test_count = suite.countTestCases()
        if test_count > 0:
            if log:
                carb.log_warn(f"Found {test_count} tests in {module.__name__}")
            for t in suite:
                tests += t._tests
        if "scan_for_test_modules" in module.__dict__:
            if log:
                carb.log_warn(f"Scanning for test modules in {module.__name__} loaded from {module.__file__}")
            for extra_module in dynamic_test_modules(module.__name__, module.__file__):
                if log:
                    carb.log_warn(f"   Processing additional module {extra_module}")
                extra_suite = loader.loadTestsFromModule(extra_module)
                extra_count = extra_suite.countTestCases()
                if extra_count > 0:
                    if log:
                        carb.log_warn(f"Found {extra_count} additional tests added through {extra_module.__name__}")
                    for extra_test in extra_suite:
                        tests += extra_test._tests

    # Some tests can be generated at runtime out of discovered ones. For example, we can leverage that to duplicate
    # tests for different configurations.
    for t in islice(tests, 0, len(tests)):
        generate_extra = getattr(t, "generate_extra_tests", None)
        if callable(generate_extra):
            generated = generate_extra()
            if generated:
                tests += generated

    # allow global test callbacks to add tests
    tests += _extra_tests
    return tests


def get_tests_from_enabled_extensions():
    # NOTE: This function requires pythonTests.include values to be prefixed with the module itself
    include_tests = get_setting("/exts/omni.kit.test/includeTests", default=[])
    exclude_tests = get_setting("/exts/omni.kit.test/excludeTests", default=[])

    def include_test(test_id: str) -> bool:
        return any(fnmatch.fnmatch(test_id, p) for p in include_tests) and not any(
            fnmatch.fnmatch(test_id, p) for p in exclude_tests
        )

    # Filter modules before importing. That allows having test-only modules and dependencies, they will fail to import
    # in non-test environment. Tricky part is filtering itself. For includeTests = "omni.foo.test_abc_def_*" we want to
    # match `omni.foo` module, but not `omni.foo_test_abc` test id. Thus module filtering is more permissive and
    # checks "starts with" too.
    def include_module(module: str) -> bool:
        def match_module(module, pattern):
            return fnmatch.fnmatch(module, pattern) or pattern.startswith(module)

        return any(match_module(module, p) for p in include_tests)

    modules = _get_enabled_extension_modules(filter_fn=include_module)
    return (t for t in get_tests_from_modules(modules) if include_test(t.id()))


def _get_tests_from_file(filepath: str) -> list:
    test_list = []
    try:
        with open(filepath) as f:
            test_list = f.read().splitlines()
    except IOError as e:
        carb.log_warn(f"Error opening file {filepath} -> {e}")
    return test_list


def _get_tests_override(tests: list) -> list:
    """Apply some override/modifiers to get the proper list of tests in that order:
    1. Add/Remove unreliable tests depending on testExtRunUnreliableTests value
    2. Get list of failed tests if present (if enabled, used with retry-on-failure)
    3. Get list of tests from a file (if enabled, generated when running tests)
    4. Get list of tests from sampling (if enabled)
    5. Shuffle (random order) is applied last
    """

    def is_unreliable_test(test_id: str) -> bool:
        return any(fnmatch.fnmatch(test_id, p) for p in unreliable_tests)

    unreliable_tests = get_setting("/exts/omni.kit.test/unreliableTests", default=[])
    run_unreliable_tests = get_setting("/exts/omni.kit.test/testExtRunUnreliableTests", default=0)

    if run_unreliable_tests == RunExtTests.RELIABLE_ONLY:
        tests = [t for t in tests if not is_unreliable_test(t.id())]
    elif run_unreliable_tests == RunExtTests.UNRELIABLE_ONLY:
        tests = [t for t in tests if is_unreliable_test(t.id())]

    failed_tests = get_setting("/exts/omni.kit.test/retryFailedTests", default=[])
    tests_filepath = get_setting("/exts/omni.kit.test/runTestsFromFile", default="")
    sampling_factor = float(get_setting("/exts/omni.kit.test/samplingFactor", default=SamplingFactor.UPPER_BOUND))
    shuffle_tests = bool(get_setting("/exts/omni.kit.test/testExtRandomOrder", default=False))

    if failed_tests:
        tests = [t for t in tests if t.id() in failed_tests]
    elif tests_filepath:
        tests_from_file = _get_tests_from_file(tests_filepath)
        tests = [t for t in tests if t.id() in tests_from_file]
        tests.sort(key=lambda x: tests_from_file.index(x.id()))
    elif tests and sampling_factor != SamplingFactor.UPPER_BOUND:
        sampling = get_tests_sampling_to_skip(get_ext_test_id(), sampling_factor, [t.id() for t in tests])
        skipped_tests = [t for t in tests if t.id() in sampling]
        print(
            "----------------------------------------\n"
            f"Tests Sampling Factor set to {int(sampling_factor * 100)}% "
            f"(each test should run every ~{int(1.0 / sampling_factor)} runs)\n"
        )
        teamcity_message("message", text=f"Tests Sampling Factor set to {int(sampling_factor * 100)}%")
        # Add unittest.skip function (decorator) to all skipped tests if not skipped already.
        # It will provide an explicit reason why the test was skipped.
        for t in skipped_tests:
            test_method = getattr(t, t._testMethodName)
            if not getattr(test_method, "__unittest_skip__", False):
                setattr(t, t._testMethodName, unittest.skip("Skipped by Sampling")(test_method))

    if shuffle_tests:
        seed = int(get_setting("/exts/omni.kit.test/testExtSamplingSeed", default=-1))
        if seed >= 0:
            random.seed(seed)
        random.shuffle(tests)
    return tests


def get_tests(tests_filter="") -> List:
    """Default function to get all current tests.

    It gets tests from all enabled extensions, but also included include and exclude settings to filter them

    Args:
        tests_filter(str): Additional filter string to apply on list of tests.

    Returns:
        List of tests.
    """
    if "*" not in tests_filter:
        tests_filter = f"*{tests_filter}*"

    # Find all tests in loaded extensions and filter with patterns using settings above:
    tests = [t for t in get_tests_from_enabled_extensions() if fnmatch.fnmatch(t.id(), tests_filter)]
    tests = _get_tests_override(tests)

    return tests


def _setup_output_path(test_output_path: str):
    tokens = carb.tokens.get_tokens_interface()
    os.makedirs(test_output_path, exist_ok=True)
    tokens.set_value("test_output", test_output_path)


def _write_tests_playlist(test_output_path: str, tests: list):
    n = 1
    filepath = test_output_path
    app_name = get_setting("/app/name", "exttest")
    while os.path.exists(filepath):
        filepath = os.path.join(test_output_path, f"{app_name}_playlist_{n}.log")
        n += 1

    try:
        with open(filepath, "w") as f:
            for t in tests:
                f.write(f"{t.id()}\n")
    except IOError as e:
        carb.log_warn(f"Error writing to {filepath} -> {e}")


def run_tests_in_modules(modules, on_finish_fn=None):
    run_tests(get_tests_from_modules(modules, True), on_finish_fn)


def run_tests(tests=None, on_finish_fn=None, on_status_report_fn=None):
    if tests is None:
        tests = get_tests()

    test_output_path = get_test_output_path()
    _setup_output_path(test_output_path)
    _write_tests_playlist(test_output_path, tests)

    loader = unittest.TestLoader()
    loader.suiteClass = AsyncTestSuite
    suite = AsyncTestSuite()
    suite.addTests(tests)

    def on_status_report(*args, **kwargs):
        if on_status_report_fn:
            on_status_report_fn(*args, **kwargs)
        _test_status_report(*args, **kwargs)

    # Use our own reporter:
    # Select reporter based on benchmark flag
    is_benchmark = get_setting("/exts/omni.kit.test/runAsBenchmark", default=False) or "--benchmark" in get_argv()
    AsyncTextTestRunner.resultclass = BenchmarkResult if is_benchmark else OmniTestResult
    runner = AsyncTextTestRunner(verbosity=2, stream=sys.stdout)

    async def run():
        result = await runner.run(suite, on_status_report)
        if on_finish_fn:
            on_finish_fn(result)
        print("========================================")

    print("========================================")
    print(f"Running Tests (count: {len(tests)}):")
    print("========================================")

    omni.kit.async_engine.run_coroutine(run())


def print_tests():
    tests = get_tests()
    print("========================================")
    print(f"Printing All Tests (count: {len(tests)}):")
    print("========================================")
    reporter = TestReporter()
    for t in tests:
        reporter.unittest_start(t.id(), t.id())
        print(t.id())
        reporter.unittest_stop(t.id(), t.id())
    print("========================================")
