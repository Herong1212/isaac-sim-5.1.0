import asyncio

import omni.ext
import omni.kit.app
import omni.kit.async_engine

from . import unittests
from .async_unittest import AsyncTestCase, AsyncTestCaseFailOnLogError, AsyncTestSuite
from .benchmark import BenchmarkTestCase
from .exttests import ExtTest, ExtTestResult, run_ext_tests
from .reporter import generate_report
from .test_coverage import _PyCoverageCollector
from .test_populators import DEFAULT_POPULATOR_NAME, TestPopulateAll, TestPopulateDisabled, TestPopulator
from .test_reporters import TestRunStatus, add_test_status_report_cb
from .unittests import (
    get_tests,
    get_tests_from_modules,
    run_tests,
    add_test_case_to_tested_extension,
)
from .utils import TestReturnCode, get_global_test_output_path, get_setting, get_test_output_path, is_etm_run
from .gitlab import is_running_in_gitlab
from carb.eventdispatcher import get_eventdispatcher


async def _auto_run_tests(run_tests_and_exit: bool):
    # Skip 2 updates to make sure all extensions loaded and initialized
    await omni.kit.app.get_app().next_update_async()
    await omni.kit.app.get_app().next_update_async()

    # Run Extension tests?
    # This part runs on the parent Kit Process that triggers all extension tests
    test_exts = list(get_setting("/exts/omni.kit.test/testExts", default=[]))
    if len(test_exts) > 0:
        # Quit on finish:
        def on_finish(result: bool):
            # generate coverage report at the end?
            if get_setting("/exts/omni.kit.test/testExtGenerateCoverageReport", default=False):
                generate_report()
            returncode = 0 if result else TestReturnCode.EXT_TESTS_FAILED
            omni.kit.app.get_app().post_quit(returncode)

        exclude_exts = list(get_setting("/exts/omni.kit.test/excludeExts", default=[]))
        run_ext_tests(test_exts, on_finish_fn=on_finish, exclude_exts=exclude_exts)
        return

    # Print tests?
    # This part runs on the child Kit Process to print the number of extension tests
    if len(test_exts) == 0 and get_setting("/exts/omni.kit.test/printTestsAndQuit", default=False):
        unittests.print_tests()
        omni.kit.app.get_app().post_quit(0)
        return

    # Run python tests?
    # This part runs on the child Kit Process that performs the extension tests
    if run_tests_and_exit:
        tests_filter = get_setting("/exts/omni.kit.test/runTestsFilter", default="")

        from unittest.result import TestResult

        # Quit on finish:
        def on_finish(result: TestResult):
            returncode = 0 if result.wasSuccessful() else TestReturnCode.UNIT_TESTS_FAILED
            cpp_test_res = get_setting("/exts/omni.kit.test/~cppTestResult", default=None)
            if cpp_test_res is not None:
                returncode += cpp_test_res
            if not get_setting("/exts/omni.kit.test/doNotQuit", default=False):
                omni.kit.app.get_app().post_quit(returncode)

        unittests.run_tests(unittests.get_tests(tests_filter), on_finish)


class _TestAutoRunner(omni.ext.IExt):
    """Automatically run tests based on setting"""

    def __init__(self):
        super().__init__()
        self._py_coverage = _PyCoverageCollector()

    def on_startup(self):
        # Report generate mode?
        if get_setting("/exts/omni.kit.test/testExtGenerateReport", default=False):
            generate_report()
            omni.kit.app.get_app().post_quit(0)
            return

        # Otherwise: regular test run
        run_tests_and_exit = get_setting("/exts/omni.kit.test/runTestsAndQuit", default=False)
        ui_mode = get_setting("/exts/omni.kit.test/testExtUIMode", default=False)

        # If launching a Python test then start test coverage subsystem (might do nothing depending on the settings)
        if run_tests_and_exit or ui_mode:
            self._py_coverage.startup()

        def on_app_ready(_):
            omni.kit.async_engine.run_coroutine(_auto_run_tests(run_tests_and_exit))

        self._app_ready_sub = (
            get_eventdispatcher()
            .observe_event(
                event_name=omni.kit.app.GLOBAL_EVENT_APP_READY, on_event=on_app_ready, observer_name="omni.kit.test start tests"
            )
        )

    def on_shutdown(self):
        # Stop coverage and generate report if it's started.
        self._py_coverage.shutdown()


__all__ = [
    "AsyncTestCase",
    "AsyncTestCaseFailOnLogError",
    "AsyncTestSuite",
    "BenchmarkTestCase",
    "DEFAULT_POPULATOR_NAME",
    "ExtTest",
    "ExtTestResult",
    "TestPopulateAll",
    "TestPopulateDisabled",
    "TestPopulator",
    "TestReturnCode",
    "TestRunStatus",
    "add_test_status_report_cb",  # Used by omni.kit.etm.runner
    "add_test_case_to_tested_extension",
    # "generate_report",  # Not used outside of this module, but it's used in this script.
    "get_global_test_output_path",
    "get_setting",
    "get_test_output_path",
    "get_tests",
    "get_tests_from_modules",
    "is_etm_run",
    "run_tests",
]