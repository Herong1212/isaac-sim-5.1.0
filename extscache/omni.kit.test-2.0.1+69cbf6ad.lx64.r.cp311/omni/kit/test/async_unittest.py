"""Async version of python unittest module.

AsyncTestCase, AsyncTestSuite and AsyncTextTestRunner classes were copied from python unittest source and async/await
keywords were added.

There are two ways of registering tests, which must all be in the 'tests' submodule of your python module.

    1. 'from X import *" from every file containing tests
    2. Add the line 'scan_for_test_modules = True' in your __init__.py file to pick up tests in every file starting
       with 'test_'
"""

import asyncio
import time
import unittest
import warnings
from unittest.case import _Outcome
from typing import Callable, Any
import sys

import carb
from carb.eventdispatcher import get_eventdispatcher, Event
import omni.kit.app

from .reporter import TestReporter
from .test_reporters import TestRunStatus
from .utils import Colors, get_ext_test_id, is_running_on_ci

KEY_FAILING_TESTS = "Failing tests"
STARTED_UNITTEST = "started "

# Python 3.11 changed details of unit-test modules, and this file uses some "private/protected" things.
# Better solution would be to conform to public API and avoid conditionals.
#
PY_311 = sys.version_info.minor >= 11 if sys.version_info.major == 3 else False

async def await_or_call(func):
    """
    Awaits on function if it is a coroutine, calls it otherwise.
    """
    if asyncio.iscoroutinefunction(func):
        await func()
    else:
        func()


class LogErrorChecker:
    """Automatically subscribes to logging events and monitors if error were produced during the test."""

    def __init__(self):
        # Setup this test case to fail if any error is produced
        self._error_count = 0

        def on_log_event(e: Event):
            if e["level"] >= carb.logging.LEVEL_ERROR:
                self._error_count = self._error_count + 1

        self._log_sub = get_eventdispatcher().observe_event(
            event_name=omni.kit.app.GLOBAL_EVENT_ERROR_LOG_IMMEDIATE,
            on_event=on_log_event, observer_name="test log event"
        )

    def shutdown(self):
        self._log_sub = None

    def get_error_count(self):
        return self._error_count


class AsyncTestCase(unittest.TestCase):
    """Base class for all async test cases.

    Derive from it to make your tests auto discoverable. Test methods must start with `test_` prefix.

    Test cases allow for generation and/or adaptation of tests at runtime. See testing_exts_python.md for more details.
    """

    # If true test will check for Carbonite logging messages and fail if any error level or higher was produced during the test.
    fail_on_log_error = False

    def __addSkip(self, result, test, reason):
        if PY_311:
            from unittest.case import _addSkip
            _addSkip(result, test, reason)
        else:
            super()._addSkip(result, test, reason)

    async def run(self, result=None):
        # Log error checker
        self._log_error_checker = None
        if self.fail_on_log_error:
            carb.log_warn(
                "[DEPRECATION WARNING] `AsyncTestCaseFailOnLogError` is deprecated. Replace with `AsyncTestCase`. Errors are captured from stdout by an external test runner process now."
            )

            # Make sure log buffer pumped:
            await omni.kit.app.get_app().next_update_async()
            self._log_error_checker = LogErrorChecker()

        orig_result = result
        if result is None:
            result = self.defaultTestResult()
            startTestRun = getattr(result, "startTestRun", None)
            if startTestRun is not None:
                startTestRun()

        result.startTest(self)

        testMethod = getattr(self, self._testMethodName)
        if getattr(self.__class__, "__unittest_skip__", False) or getattr(testMethod, "__unittest_skip__", False):
            # If the class or method was skipped.
            try:
                skip_why = getattr(self.__class__, "__unittest_skip_why__", "") or getattr(
                    testMethod, "__unittest_skip_why__", ""
                )
                self.__addSkip(result, self, skip_why)
            finally:
                getattr(result, "testMethodEnd", lambda x: None)(self)
                result.stopTest(self)
            return
        expecting_failure_method = getattr(testMethod, "__unittest_expecting_failure__", False)
        expecting_failure_class = getattr(self, "__unittest_expecting_failure__", False)
        expecting_failure = expecting_failure_class or expecting_failure_method
        outcome = _Outcome(result)

        try:
            self._outcome = outcome
            executor_args = {} if PY_311 else {'isTest': True}
            with outcome.testPartExecutor(self):
                await await_or_call(self.setUp)
            if outcome.success:
                outcome.expecting_failure = expecting_failure
                with outcome.testPartExecutor(self, **executor_args):
                    getattr(result, "testMethodBegin", lambda x: None)(self)
                    await await_or_call(testMethod)
                getattr(result, "testMethodEnd", lambda x: None)(self)
                outcome.expecting_failure = False

                with outcome.testPartExecutor(self):
                    await await_or_call(self.tearDown)

                    # Log error checks
                    if self._log_error_checker:
                        await omni.kit.app.get_app().next_update_async()
                        error_count = self._log_error_checker.get_error_count()
                        if error_count > 0:
                            self.fail(f"Test failure because of {error_count} error message(s) logged during it.")

            self.doCleanups()

            if not PY_311:
                for test, reason in outcome.skipped:
                    self.__addSkip(result, test, reason)

            if hasattr(outcome, 'errors'):
                self._feedErrorsToResult(result, outcome.errors)

            if outcome.success:
                if expecting_failure:
                    if outcome.expectedFailure:
                        self._addExpectedFailure(result, outcome.expectedFailure)
                    else:
                        self._addUnexpectedSuccess(result)
                else:
                    result.addSuccess(self)
            return result
        finally:
            if self._log_error_checker:
                self._log_error_checker.shutdown()

            result.stopTest(self)
            if orig_result is None:
                stopTestRun = getattr(result, "stopTestRun", None)
                if stopTestRun is not None:
                    stopTestRun()

            # explicitly break reference cycles:
            # outcome.errors -> frame -> outcome -> outcome.errors
            # outcome.expectedFailure -> frame -> outcome -> outcome.expectedFailure
            if hasattr(outcome, 'errors'):
                outcome.errors.clear()
            outcome.expectedFailure = None

            # clear the outcome, no more needed
            self._outcome = None

    async def wait_n_updates(self, n_frames: int = 3):
        app = omni.kit.app.get_app()
        for _ in range(n_frames):
            await app.next_update_async()

    async def retry_until_success(self, operation: Callable[[], Any], wait_frames: int = 2, max_retries: int = 50) -> Any:
        """Retry the operation until it returns a truthy value or exceeds the max retries.

        Parameters:
        * operation: a function that takes no arguments and returns a value.
        * wait_frames: the number of frames to wait after a failed call of `operation`.
        * max_retries: the maximum number of retries.

        Return:
        The first truthy value returned by `operation`.

        The function will keep calling `operation` until it returns a truthy value
        (e.g., True, non-empty collection, and non-zero number).
        If the maximum number of retries is reached, make a failed assertion to stop the test.

        Please use this function to wrap your operation and minimize waiting time instead of using
        `wait_n_updates()` directly.
        """
        ret = None
        for _ in range(max_retries):
            ret = operation()
            if ret:
                return ret
            await self.wait_n_updates(wait_frames)
        self.fail(f"operation failed to get a truthy value after {max_retries} retries")

    async def assertTrueWithRetry(self, operation: Callable[[], Any], wait_frames: int = 2, max_retries: int = 50):
        """Like assertTrue except it retries `operation` until it returns a truthy value or the retry limit is reached.

        Parameters:
        * operation: a function that takes no arguments and returns a value.
        * wait_frames: the number of frames to wait after a failed call of `operation`.
        * max_retries: the maximum number of retries.

        The function will keep calling `operation` until it returns a truthy value
        (e.g., True, non-empty collection, and non-zero number).
        If the maximum number of retries is reached, make a failed assertion to stop the test.

        Please use this function to wrap your operation and minimize waiting time instead of using
        `wait_n_updates()` directly.
        """
        for _ in range(max_retries):
            ret = operation()
            if ret:
                break
            await self.wait_n_updates(wait_frames)
        self.assertTrue(ret, f"operation failed to get a truthy value after {max_retries} retries")

    async def assertEqualWithRetry(self, operation: Callable[[], Any], expected: Any, wait_frames: int = 2, max_retries: int = 50):
        """Like assertEqual except it retries `operation` until it returns an equivalent value to `expected`
        or the retry limit is reached.

        Parameters:
        * operation: a function that takes no arguments and returns a value.
        * expected: the expected value.
        * wait_frames: the number of frames to wait after a failed call of `operation`.
        * max_retries: the maximum number of retries.

        The function will keep calling `operation` until the returned value equals to `expected`.
        If the maximum number of retries is reached, make a failed assertion to show the last returned
        value and the expected value.

        Please use this function to wrap your operation and minimize waiting time instead of using
        `wait_n_updates()` directly.
        """
        for _ in range(max_retries):
            ret = operation()
            if ret == expected:
                break
            await self.wait_n_updates(wait_frames)
        self.assertEqual(ret, expected, f"operation failed to get the expected value after {max_retries} retries: {ret} != {expected}")

    def assertEquals(self, *args, **kwargs):
        """
        Deprecated stub for deprecated method on base unittest.TestCase class.
        Python 3.12 removed assertEquals (which was already deprecated).
        This stub is present to provide a warning to consumers and will
        ultimately be removed.
        """
        carb.log_warn(
                "[DEPRECATION WARNING] `assertEquals` is deprecated. Replace with `assertEqual`."
            )

        self.assertEqual(*args, **kwargs)

class AsyncTestCaseFailOnLogError(AsyncTestCase):
    """Test Case which automatically subscribes to logging events and fails if any error were produced during the test.

    This class is for backward compatibility, you can also just change value of `fail_on_log_error`.
    """

    # Enable failure on error
    fail_on_log_error = True


class OmniTestResult(unittest.TextTestResult):
    def __init__(self, stream, descriptions, verbosity):
        # If we are running under CI we will use default unittest reporter with higher verbosity.
        if not is_running_on_ci():
            verbosity = 2
        super(OmniTestResult, self).__init__(stream, descriptions, verbosity)
        self.reporter = TestReporter(stream)
        self.on_status_report_fn = None

    def _report_status(self, *args, **kwargs):
        if self.on_status_report_fn:
            self.on_status_report_fn(*args, **kwargs)

    @staticmethod
    def get_tc_test_id(test):
        if isinstance(test, str):
            return test
        # Use dash as a clear visual separator of 3 parts:
        test_id = "%s - %s - %s" % (test.__class__.__module__, test.__class__.__qualname__, test._testMethodName)
        # Dots have special meaning in TC, replace with /
        test_id = test_id.replace(".", "/")
        ext_test_id = get_ext_test_id()
        if ext_test_id:
            # In the context of extension test it has own test id. Convert to TC form by getting rid of dots.
            ext_test_id = ext_test_id.replace(".", "+")
            test_id = f"{ext_test_id}.{test_id}"
        return test_id

    def addSuccess(self, test):
        super(OmniTestResult, self).addSuccess(test)

    def addError(self, test, err, *k):
        super(OmniTestResult, self).addError(test, err)
        fail_message = self._get_error_message(test, "Error", self.errors)
        self.report_fail(test, "Error", err, fail_message)

    def addFailure(self, test, err, *k):
        super(OmniTestResult, self).addFailure(test, err)
        fail_message = self._get_error_message(test, "Fail", self.failures)
        self.report_fail(test, "Failure", err, fail_message)

    def printErrorList(self, flavour, errors):
        # Same code as in TextTestResult.printErrorList from python/Lib/unittest/runner.py
        # Except we add ANSI coloring to easily spot errors on CI and TTY.
        for test, err in errors:
            self.stream.write(Colors.RED)
            self.stream.writeln(self.separator1)
            self.stream.writeln("%s: %s" % (flavour, self.getDescription(test)))
            self.stream.writeln(self.separator2)
            self.stream.writeln("%s" % err)
            self.stream.write(Colors.RESET)
            self.stream.flush()

    def report_fail(self, test, fail_type: str, err, fail_message: str):
        tc_test_id = self.get_tc_test_id(test)
        test_id = test.id()
        # pass the failing test info back to the ext testing framework in parent proc
        self.stream.write(f"##omni.kit.test[append, {KEY_FAILING_TESTS}, {test_id}]\n")

        self.reporter.unittest_fail(test_id, tc_test_id, fail_type, fail_message)
        self._report_status(test_id, TestRunStatus.FAILED, fail_message=fail_message)

    def _get_error_message(self, test, fail_type: str, errors: list) -> str:
        # In python/Lib/unittest/result.py the failures are reported with _exc_info_to_string() that is private.
        # To get the same result we grab the latest errors/failures from `self.errors[-1]` or `self.failures[-1]`
        # In python/Lib/unittest/runner.py from the `printErrorList` function we also copied the logic here.
        exc_info = errors[-1][1] if errors[-1] else ""
        error_msg = []
        error_msg.append(self.separator1)
        error_msg.append(f"{fail_type.upper()}: {self.getDescription(test)}")
        error_msg.append(self.separator2)
        error_msg.append(exc_info)
        return "\n".join(error_msg)

    def startTest(self, test):
        super(OmniTestResult, self).startTest(test)
        tc_test_id = self.get_tc_test_id(test)
        test_id = test.id()
        self.stream.write("\n")
        # python tests can start but never finish (crash, time out, etc)
        # track it from the parent proc with a pragma message (see _extract_metadata_pragma in exttests.py)
        self.stream.write(f"##omni.kit.test[set, {test_id}, {STARTED_UNITTEST}{tc_test_id}]\n")

        self.reporter.unittest_start(test_id, tc_test_id, captureStandardOutput="true")
        self._report_status(test_id, TestRunStatus.RUNNING)

    def stopTest(self, test):
        super(OmniTestResult, self).stopTest(test)
        tc_test_id = self.get_tc_test_id(test)
        test_id = test.id()
        # test finished, delete it from the metadata
        self.stream.write(f"##omni.kit.test[del, {test_id}]\n")

        if PY_311:
            skipped = any(test == t for t, _ in self.skipped)
        else:
            # When skipped using self.skipTest() it contains list of skipped test cases
            # test._outcome is None when test is skipped using decorator.
            skipped = test._outcome is None or bool(test._outcome.skipped)

        # self.skipped last index contains the current skipped test, name is at index 0, reason at index 1
        skip_reason = self.skipped[-1][1] if skipped and self.skipped else ""
        # skipped tests are marked as "passed" not to confuse reporting down the line
        passed = test._outcome.success if test._outcome and not skipped else True
        self.reporter.unittest_stop(test_id, tc_test_id, passed=passed, skipped=skipped, skip_reason=skip_reason)
        if passed:
            self._report_status(test_id, TestRunStatus.PASSED)


class TeamcityTestResult(OmniTestResult):
    def __init__(self, stream, descriptions, verbosity):
        carb.log_warn("[DEPRECATION WARNING] `TeamcityTestResult` is deprecated. Replace with `OmniTestResult`.")
        super(TeamcityTestResult, self).__init__(stream, descriptions, verbosity)


class AsyncTextTestRunner(unittest.TextTestRunner):
    """A test runner class that displays results in textual form.

    It prints out the names of tests as they are run, errors as they
    occur, and a summary of the results at the end of the test run.
    """

    async def run(self, test, on_status_report_fn=None):
        "Run the given test case or test suite."
        result = self._makeResult()
        unittest.signals.registerResult(result)
        result.failfast = self.failfast
        result.buffer = self.buffer
        result.tb_locals = self.tb_locals
        result.on_status_report_fn = on_status_report_fn
        with warnings.catch_warnings():
            if self.warnings:
                # if self.warnings is set, use it to filter all the warnings
                warnings.simplefilter(self.warnings)
                # if the filter is 'default' or 'always', special-case the
                # warnings from the deprecated unittest methods to show them
                # no more than once per module, because they can be fairly
                # noisy.  The -Wd and -Wa flags can be used to bypass this
                # only when self.warnings is None.
                if self.warnings in ["default", "always"]:
                    warnings.filterwarnings(
                        "module", category=DeprecationWarning, message=r"Please use assert\w+ instead."
                    )
            startTime = time.monotonic()
            startTestRun = getattr(result, "startTestRun", None)
            if startTestRun is not None:
                startTestRun()
            try:
                await test(result)
            finally:
                stopTestRun = getattr(result, "stopTestRun", None)
                if stopTestRun is not None:
                    stopTestRun()
            stopTime = time.monotonic()
        timeTaken = stopTime - startTime
        result.printErrors()
        if hasattr(result, "separator2"):
            self.stream.writeln(result.separator2)
        run = result.testsRun
        self.stream.writeln("Ran %d test%s in %.3fs" % (run, run != 1 and "s" or "", timeTaken))
        self.stream.writeln()

        expectedFails = unexpectedSuccesses = skipped = 0
        try:
            results = map(len, (result.expectedFailures, result.unexpectedSuccesses, result.skipped))
        except AttributeError:
            pass
        else:
            expectedFails, unexpectedSuccesses, skipped = results

        infos = []
        if not result.wasSuccessful():
            self.stream.write("FAILED")
            failed, errored = len(result.failures), len(result.errors)
            if failed:
                infos.append("failures=%d" % failed)
            if errored:
                infos.append("errors=%d" % errored)
        else:
            self.stream.write("OK")
        if skipped:
            infos.append("skipped=%d" % skipped)
        if expectedFails:
            infos.append("expected failures=%d" % expectedFails)
        if unexpectedSuccesses:
            infos.append("unexpected successes=%d" % unexpectedSuccesses)
        if infos:
            self.stream.writeln(" (%s)" % (", ".join(infos),))
        else:
            self.stream.write("\n")
        self.stream.flush()
        return result


def _isnotsuite(test):
    "A crude way to tell apart testcases and suites with duck-typing"
    try:
        iter(test)
    except TypeError:
        return True
    return False


class AsyncTestSuite(unittest.TestSuite):
    """A test suite is a composite test consisting of a number of TestCases.

    For use, create an instance of TestSuite, then add test case instances.
    When all tests have been added, the suite can be passed to a test
    runner, such as TextTestRunner. It will run the individual test cases
    in the order in which they were added, aggregating the results. When
    subclassing, do not forget to call the base class constructor.
    """

    async def run(self, result, debug=False):
        topLevel = False
        if getattr(result, "_testRunEntered", False) is False:
            result._testRunEntered = topLevel = True

        for index, test in enumerate(self):
            if result.shouldStop:
                break

            if _isnotsuite(test):
                self._tearDownPreviousClass(test, result)
                self._handleModuleFixture(test, result)
                self._handleClassSetUp(test, result)
                result._previousTestClass = test.__class__

                if getattr(test.__class__, "_classSetupFailed", False) or getattr(result, "_moduleSetUpFailed", False):
                    continue

            if not debug:
                await test(result)
            else:
                await test.debug()

            if self._cleanup:
                self._removeTestAtIndex(index)

        if topLevel:
            self._tearDownPreviousClass(None, result)
            self._handleModuleTearDown(result)
            result._testRunEntered = False
        return result
