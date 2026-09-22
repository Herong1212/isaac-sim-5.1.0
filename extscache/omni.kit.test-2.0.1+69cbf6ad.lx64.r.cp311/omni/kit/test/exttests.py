from __future__ import annotations

import asyncio
import fnmatch
import io
import multiprocessing
import os
import pprint
import random
import re
import subprocess
import sys
import time
from collections import defaultdict
from enum import IntEnum
from typing import Dict, List, Optional, Set, Tuple

import carb.dictionary
import carb.settings
import carb.tokens
import omni.kit.app
import omni.kit.async_engine
import psutil

from .async_unittest import KEY_FAILING_TESTS, STARTED_UNITTEST
from .code_change_analyzer import CodeChangeAnalyzer
from .crash_process import crash_process
from .flaky import FLAKY_TESTS_QUERY_DAYS, FlakyTestAnalyzer
from .repo_test_context import RepoTestContext
from .reporter import TestReporter
from .sampling import SamplingFactor
from .teamcity import is_running_in_teamcity, teamcity_message, teamcity_test_retry_support
from .test_coverage import read_coverage_collector_settings
from .test_reporters import TestRunStatus, _test_status_report
from .utils import (
    Colors,
    TestReturnCode,
    clamp,
    cleanup_folder,
    ext_id_to_fullname,
    get_argv,
    get_global_test_output_path,
    get_local_timestamp,
    get_setting,
    get_unprocessed_argv,
    is_running_on_ci,
    resolve_path,
    is_etm_run
)

BEGIN_SEPARATOR = "\n{0}  [EXTENSION TEST START: {{0}}]  {0}\n".format("|" * 30)
END_SEPARATOR = "\n{{2}}{0}  [EXTENSION TEST {{0}}: {{1}}]  {0}{{3}}\n".format("|" * 30)
DEFAULT_TEST_NAME = "default"
STARTUP_ONLY_TEST_MARKER = "_startup_only_test"


_debug_log = bool(os.getenv("OMNI_KIT_TEST_DEBUG", default=False))


def _error(stream, msg):
    stream.write(f"[error] [{__file__}] {msg}\n")


def _warning(stream, msg):
    stream.write(f"[warning] [{__file__}] {msg}\n")


def _debug(stream, msg):
    if _debug_log:
        stream.write(f"[info] [{__file__}] {msg}\n")


def matched_patterns(s: str, patterns: List[str]) -> List[str]:
    return [p for p in patterns if fnmatch.fnmatch(s, p)]


def match(s: str, patterns: List[str]) -> bool:
    return len(matched_patterns(s, patterns)) > 0


def escape_for_fnmatch(s: str) -> str:
    return s.replace("[", "[[]")


def unescape_fnmatch(s: str) -> str:
    return s.replace("[[]", "[")


class FailPatterns:
    def __init__(self, include=[], exclude=[]):
        self.include = [escape_for_fnmatch(s.lower()) for s in include]
        self.exclude = [escape_for_fnmatch(s.lower()) for s in exclude]

    def merge(self, patterns: FailPatterns):
        self.include += patterns.include
        self.exclude += patterns.exclude

    def match_line(self, line: str) -> Tuple[str, str, bool]:
        line_lower = line.lower()
        include_matched = match(line_lower, self.include)
        exclude_matched = match(line_lower, self.exclude)
        if include_matched and not exclude_matched:
            patterns = matched_patterns(line_lower, self.include)
            patterns = [unescape_fnmatch(p) for p in patterns]
            return ", ".join(patterns), line.strip(), exclude_matched
        return "", "", exclude_matched

    def __str__(self):
        return pprint.pformat(vars(self))


class RunExtTests(IntEnum):
    RELIABLE_ONLY = 0
    UNRELIABLE_ONLY = 1
    BOTH = 2


class RetryStrategy:
    NO_RETRY = "no-retry"
    RETRY_ON_FAILURE = "retry-on-failure"
    ITERATIONS = "iterations"
    RERUN_UNTIL_FAILURE = "rerun-until-failure"
    # CI strategy, default to no-retry when testing locally
    RETRY_ON_FAILURE_CI_ONLY = "retry-on-failure-ci-only"


class SamplingContext:
    ANY = "any"
    LOCAL = "local"
    CI = "ci"


class TestRunContext:
    def __init__(self):
        # Setup output path for test data
        self.output_path = get_global_test_output_path()
        os.makedirs(self.output_path, exist_ok=True)
        print("Test output path: {}".format(self.output_path))

        self.coverage_mode = get_setting("/exts/omni.kit.test/testExtGenerateCoverageReport", default=False) or (
            "--coverage" in get_argv()
        )

        # clean output folder?
        clean_output = get_setting("/exts/omni.kit.test/testExtCleanOutputPath", default=False)
        if clean_output:
            cleanup_folder(self.output_path)

        self.shared_patterns = FailPatterns(
            get_setting("/exts/omni.kit.test/stdoutFailPatterns/include", default=[]),
            get_setting("/exts/omni.kit.test/stdoutFailPatterns/exclude", default=[]),
        )

        self.trim_stdout_on_success = bool(get_setting("/exts/omni.kit.test/testExtTrimStdoutOnSuccess", default=False))
        self.trim_excluded_messages = bool(
            get_setting("/exts/omni.kit.test/stdoutFailPatterns/trimExcludedMessages", default=False)
        )

        self.retry_strategy = str(
            get_setting("/exts/omni.kit.test/testExtRetryStrategy", default=RetryStrategy.NO_RETRY)
        )
        self.max_test_run = int(get_setting("/exts/omni.kit.test/testExtMaxTestRunCount", default=1))
        if self.retry_strategy == RetryStrategy.RETRY_ON_FAILURE_CI_ONLY:
            if is_running_on_ci():
                self.retry_strategy = RetryStrategy.RETRY_ON_FAILURE
                self.max_test_run = 3
            else:
                self.retry_strategy = RetryStrategy.NO_RETRY
                self.max_test_run = 1

        self.run_unreliable_tests = RunExtTests(get_setting("/exts/omni.kit.test/testExtRunUnreliableTests", default=0))
        self.run_flaky_tests = get_setting("/exts/omni.kit.test/testExtRunFlakyTests", default=False)

        self.start_ts = get_local_timestamp()
        self.repo_test_context = RepoTestContext()

        self.change_analyzer = None
        if get_setting("/exts/omni.kit.test/testExtCodeChangeAnalyzerEnabled", default=False) and is_running_on_ci():
            self.change_analyzer = CodeChangeAnalyzer(self.repo_test_context)


def _prepare_ext_for_testing(ext_name, stream=sys.stdout):
    manager = omni.kit.app.get_app().get_extension_manager()

    ext_id = None
    ext_info_local = manager.get_extension_dict(ext_name)

    if ext_info_local:
        return ext_info_local

    ext_info_remote = manager.get_registry_extension_dict(ext_name)
    if ext_info_remote:
        ext_id = ext_info_remote["package/id"]
    else:
        versions = manager.fetch_extension_versions(ext_name)
        if len(versions) > 0:
            ext_id = versions[0]["id"]
        else:
            _error(stream, f"Can't find extension: {ext_name} to run extension test on.")
            return None

    ext_info_local = manager.get_extension_dict(ext_id)
    is_local = ext_info_local is not None
    if not is_local:
        if not manager.pull_extension(ext_id):
            _error(stream, f"Failed to pull extension: {ext_id} to run extension test on.")
            return None
        ext_info_local = manager.get_extension_dict(ext_id)

    if not ext_info_local:
        _error(stream, f"Failed to get extension dict: {ext_id} while preparing extension for testing.")

    return ext_info_local


def _prepare_app_for_testing(stream) -> Tuple[Optional[str], str]:
    """Returns path to app (kit file) and short name of an app."""
    test_app = get_setting("/exts/omni.kit.test/testExtApp", default=None)
    test_app = carb.tokens.get_tokens_interface().resolve(test_app)

    # Test app can be either path to kit file or extension id (to optionally download and use extension as an app)
    if test_app.endswith(".kit") or "/" in test_app:
        return (test_app, "")

    app_ext_info = _prepare_ext_for_testing(test_app, stream)
    if app_ext_info:
        return (app_ext_info["path"], test_app)

    return (None, test_app)


class ExtTestResult:
    def __init__(self):
        self.passed = True
        self.duration = 0.0
        self.kill_process_duration = 0.0
        self.test_count = 0
        self.unreliable = 0
        self.unreliable_fail = 0
        self.fail = 0


class TestApp:
    def __init__(self, stream):
        self.path, self.name = _prepare_app_for_testing(stream)
        self.is_empty = not self.name


class ExtTest:
    def __init__(
        self,
        ext_id: str,
        ext_info: carb.dictionary.Item,
        test_config: Dict,
        test_id: str,
        is_parallel_run: bool,
        run_context: TestRunContext,
        test_app: TestApp,
        valid=True,
    ):
        self.context = run_context
        self.ext_id = ext_id
        self.ext_name = ext_id_to_fullname(ext_id)
        self.test_id = test_id
        self.app_name = ""
        # TC treats dots are separators to filter tests in UI, replace them.
        self.tc_test_id = test_id.replace(".", "+") + ".[PROCESS CHECK]"
        self.bucket_name = get_setting("/exts/omni.kit.test/testExtTestBucket", default="")
        self.unreliable = False
        self.skip = False
        self.allow_sampling = True
        self.args: List[str] = []
        self.patterns = FailPatterns()
        self.timeout = -1
        self.result = ExtTestResult()
        self.retries = 0
        self.can_retry = True
        self.buffer_stdout = bool(is_parallel_run) or bool(self.context.trim_stdout_on_success)
        self.stdout = io.StringIO() if self.buffer_stdout else sys.stdout
        self.log_file = ""
        self.parallelizable = True
        self.reporter = TestReporter(self.stdout)
        self.test_app = test_app
        self.config = test_config
        self.ext_info = ext_info
        self.output_path = ""
        self.valid = bool(valid and self.ext_info)
        self.change_analyzer_result = None
        self.failed_tests = []
        self.test_dependencies = []
        if self.valid:
            self._fill_ext_test()

    def _fill_ext_test(self):
        self.args = [get_argv()[0]]

        self.app_name = "exttest_" + self.test_id.replace(".", "_").replace(":", "-")
        ui_mode = get_setting("/exts/omni.kit.test/testExtUIMode", default=False) or ("--dev" in get_argv())
        print_mode = get_setting("/exts/omni.kit.test/printTestsAndQuit", default=False)
        use_kit_file_as_app = get_setting("/exts/omni.kit.test/testExtUseKitFileAsApp", default=True)
        coverage_mode = self.context.coverage_mode

        self.ext_id = self.ext_info["package/id"]
        self.ext_name = self.ext_info["package/name"]

        is_kit_file = self.ext_info.get("isKitFile", False)

        # If extension is kit file just run startup test without using a test app
        ext_path = self.ext_info.get("path", "")
        if is_kit_file and use_kit_file_as_app:
            self.args += [ext_path]
        else:
            self.args += [self.test_app.path, "--enable", self.ext_id]

        # Allow debugging in the child process if debug extension is enabled
        if omni.kit.app.get_app().get_extension_manager().is_extension_enabled("omni.kit.debug.python"):
            settings = carb.settings.get_settings()
            # Only in connect mode multiple processes can be attached to the debugger
            if settings.get("/exts/omni.kit.debug.python/mode") == "connect":
                self.args += ["--enable", "omni.kit.debug.python", "--/exts/omni.kit.debug.python/mode='connect'"]
                host = settings.get("/exts/omni.kit.debug.python/host")
                if host:
                    self.args += [f"--/exts/omni.kit.debug.python/host='{host}'"]
                port = settings.get("/exts/omni.kit.debug.python/port")
                if port:
                    self.args += [f"--/exts/omni.kit.debug.python/port={port}"]

        # test output dir
        self.output_path = f"{self.context.output_path}/{self.app_name}"
        if not os.path.exists(self.output_path):
            os.makedirs(self.output_path)
        self.reporter.set_output_path(self.output_path)

        # current ts (not precise as test run can be delayed relative to this moment)
        ts = get_local_timestamp()
        if is_running_on_ci():
            self.log_file = f"{self.output_path}/{self.app_name}_0.log"
        else:
            self.log_file = f"{self.output_path}/{self.app_name}_{ts}_0.log"

        self.args += [
            "--/log/flushStandardStreamOutput=1",
            "--/app/name=" + self.app_name,
            f"--/log/file='{self.log_file}'",
            f"--/exts/omni.kit.test/testOutputPath='{self.output_path}'",
            f"--/exts/omni.kit.test/extTestId='{self.test_id}'",
            f"--/crashreporter/dumpDir='{self.output_path}'",
            "--/crashreporter/preserveDump=1",
            "--/crashreporter/gatherUserStory=0",  # don't pop up the GUI on crash
            "--/app/isTestRun=1", # a common flag to indicate that the app is running in a test context
            "--/rtx-transient/dlssg/enabled=false",  # OM-97205: Disable DLSS-G for now globally, so L40 tests will all pass. DLSS-G tests will have to enable it
        ]

        # Pass all exts folders
        ext_folders = list(get_setting("/app/exts/folders", default=[]))
        ext_folders += list(get_setting("/persistent/app/exts/userFolders", default=[]))
        for folder in ext_folders:
            self.args += ["--ext-folder", folder]

        # Profiler trace enabled ?
        default_profiling = get_setting("/exts/omni.kit.test/testExtEnableProfiler", default=False)
        profiling = self.config.get("profiling", default_profiling)
        if profiling:
            self.args += [
                "--/plugins/carb.profiler-cpu.plugin/saveProfile=1",
                "--/plugins/carb.profiler-cpu.plugin/compressProfile=1",
                "--/app/profileFromStart=1",
                f"--/plugins/carb.profiler-cpu.plugin/filePath='{self.output_path}/ct_{self.app_name}_{ts}.gz'",
            ]

        # Timeout for the process
        # Introduce a global timeout env var to workaround the fact that there is no way to set a global timeout that
        # overrides whatever an individual extension may set. See OVCC-1000. If global timeout is greater
        # than zero, will override any default, max or timeout setting. Please note that if using repo test, the timeout
        # of the test suite will cap the global timeout value.
        self.timeout = int(os.getenv("OMNI_KIT_TEST_GLOBAL_TIMEOUT", default=0))
        if self.timeout <= 0:
            default_timeout = int(get_setting("/exts/omni.kit.test/testExtDefaultTimeout", default=300))
            max_timeout = int(get_setting("/exts/omni.kit.test/testExtMaxTimeout", default=0))
            self.timeout = self.config.get("timeout", default_timeout)
            # Clamp timeout if needed
            if max_timeout > 0 and self.timeout > max_timeout:
                self.timeout = max_timeout

        # [[test]] can be marked as unreliable - meaning it will not run any of its tests unless unreliable tests are run
        self.unreliable = self.config.get("unreliable", self.config.get("flaky", False))

        # python tests to include
        include_tests = list(self.config.get("pythonTests", {}).get("include", []))
        exclude_tests = list(self.config.get("pythonTests", {}).get("exclude", []))
        unreliable_tests = list(self.config.get("pythonTests", {}).get("unreliable", []))

        # When running unreliable tests:
        # 1. if the [[test]] is set as unreliable run all python tests (override the `unreliable_tests` list)
        # 2. if running unreliable tests - set unreliable to true and disable sampling
        if self.unreliable:
            unreliable_tests = ["*"]
            self.allow_sampling = False
        elif unreliable_tests and self.context.run_unreliable_tests != RunExtTests.RELIABLE_ONLY:
            self.unreliable = True
            self.allow_sampling = False

        # Check if we run flaky tests - if we do grab the test list as a playlist
        if self.context.run_flaky_tests:
            self.allow_sampling = False
            query_days = int(get_setting("/exts/omni.kit.test/flakyTestsQueryDays", default=FLAKY_TESTS_QUERY_DAYS))
            flaky_test_analyzer = FlakyTestAnalyzer(self.test_id, query_days)
            if flaky_test_analyzer.should_skip_test():
                self.skip = True
            elif self.config.get("samplingFactor") == SamplingFactor.UPPER_BOUND:
                pass  # if an extension has disabled tests sampling we run all tests
            else:
                file = flaky_test_analyzer.generate_playlist()
                if file:
                    self.args += [f"--/exts/omni.kit.test/runTestsFromFile='{file}'"]

        def get_python_modules(ext_info: carb.dictionary.Item):
            python_dict = ext_info.get("python", {})
            if isinstance(python_dict, dict):
                python_modules = python_dict.get("module", []) + python_dict.get("modules", [])
                for m in python_modules:
                    module = m.get("name")
                    if module:
                        yield module

        # By default if extension has python modules use them to fill in tests mask. Can be overridden with explicit tests list.
        # Do that only for pure extensions tests, so that for tests inside an app extensions can opt in add more tests slowly.
        python_modules_names = []
        python_modules_names.extend(get_python_modules(self.ext_info))
        if len(include_tests) == 0 and self.test_app.is_empty:
            include_tests.extend(["{}.*".format(e) for e in python_modules_names])

        # Cpp test libraries
        test_libraries = self.config.get("cppTests", {}).get("libraries", [])
        test_libraries = [resolve_path(library, ext_path) for library in test_libraries]

        # If extension has tests -> run python (or cpp) tests, otherwise just do a startup test. We also have a special
        # automatically added startup test config.
        has_any_tests = (len(include_tests) > 0 or len(test_libraries) > 0)
        is_startup_only_test = self.config.get(STARTUP_ONLY_TEST_MARKER)
        if has_any_tests and not is_startup_only_test:
            # We need kit.test as a test runner then
            self.args += ["--enable", "omni.kit.test"]

            if ui_mode:
                self.args += [
                    "--enable",
                    "omni.kit.window.tests",
                    "--enable",
                    "omni.kit.window.extensions",
                    "--enable",
                    "omni.kit.renderer.core",
                    "--/exts/omni.kit.window.tests/openWindow=1",
                    "--/exts/omni.kit.test/testExtUIMode=1",
                ]
                self.timeout = None  # No timeout in that case
            elif print_mode:
                self.args += ["--/exts/omni.kit.test/printTestsAndQuit=true"]
            else:
                self.args += ["--/exts/omni.kit.test/runTestsAndQuit=true"]

            for i, test_mask in enumerate(include_tests):
                self.args += [f"--/exts/omni.kit.test/includeTests/{i}='{test_mask}'"]
            for i, test_mask in enumerate(exclude_tests):
                self.args += [f"--/exts/omni.kit.test/excludeTests/{i}='{test_mask}'"]
            for i, test_mask in enumerate(unreliable_tests):
                self.args += [f"--/exts/omni.kit.test/unreliableTests/{i}='{test_mask}'"]
            for i, test_library in enumerate(test_libraries):
                self.args += [f"--/exts/omni.kit.test/testLibraries/{i}='{test_library}'"]
        else:
            self.args += ["--/app/quitAfter=10", "--/crashreporter/gatherUserStory=0"]

        # Reduce output on TC to make log shorter. Mostly that removes long extension startup/shutdown lists. We have
        # that information in log files attached to artifacts anyway.
        if is_running_on_ci():
            self.args += ["--/app/enableStdoutOutput=0"]

        # Test filtering (support shorter version)
        argv = get_argv()
        filter_value = _parse_arg_shortcut(argv, "-f")
        if filter_value:
            self.args += [f"--/exts/omni.kit.test/runTestsFilter='{filter_value}'"]

        # Pass some args down the line:
        self.args += _propagate_args(argv, "--portable")
        self.args += _propagate_args(argv, "--portable-root", True)
        self.args += _propagate_args(argv, "--allow-root")
        self.args += _propagate_args(argv, "-d")
        self.args += _propagate_args(argv, "-v")
        self.args += _propagate_args(argv, "-vv")
        self.args += _propagate_args(argv, "--wait-debugger")
        self.args += _propagate_args(argv, "--/exts/omni.kit.test/runTestsFilter", starts_with=True)
        self.args += _propagate_args(argv, "--/exts/omni.kit.test/runTestsFromFile", starts_with=True)
        self.args += _propagate_args(argv, "--/exts/omni.kit.test/testExtRunUnreliableTests", starts_with=True)
        self.args += _propagate_args(argv, "--/exts/omni.kit.test/doNotQuit", starts_with=True)
        self.args += _propagate_args(argv, "--/exts/omni.kit.test/parallelRun", starts_with=True)
        self.args += _propagate_args(argv, "--benchmark")
        self.args += _propagate_args(argv, "--/exts/omni.kit.test/runAsBenchmark", starts_with=True)
        self.args += _propagate_args(argv, "--/exts/omni.kit.test/benchmarkFingerPrint", starts_with=True)
        self.args += _propagate_args(argv, "--/telemetry/mode", starts_with=True)
        self.args += _propagate_args(argv, "--/crashreporter/data/testName", starts_with=True)
        self.args += _propagate_args(argv, "--/apps/extensions/fsWatcherEnabled", starts_with=True)
        if not "--show-test-window" in argv:
            self.args += _propagate_args(argv, "--no-window")

        def is_arg_prefix_present(args, prefix: str):
            for arg in args:
                if arg.startswith(prefix):
                    return True
            return False

        # make sure to set the telemetry mode to 'test' if it hasn't explicitly been overridden
        # to something else.  This prevents structured log events generated from tests from
        # unintentionally polluting the telemetry analysis data.
        if not is_arg_prefix_present(self.args, "--/telemetry/mode"):
            self.args += ["--/telemetry/mode=test"]

        # make sure to pass on the test name that was given in the settings if it was not
        # explicitly given on the command line.
        if not is_arg_prefix_present(self.args, "--/crashreporter/data/testName"):
            test_name_setting = get_setting("/crashreporter/data/testName")
            if test_name_setting != None:
                self.args += [f'--/crashreporter/data/testName="{test_name_setting}"']

        # Read default coverage settings
        default_coverage_settings = read_coverage_collector_settings()
        # Sets if python test coverage enabled or disabled
        py_coverage_enabled = self.config.get("pyCoverageEnabled", default_coverage_settings.enabled or coverage_mode)
        # This must be set explicitly for the child test process:
        # if the main process gets this setting from the command line and it's different from
        # values in the configuration files then we must pass it to the child process but
        # there is no way to know whether or not the value were from the command line so
        # always set it explicitly for the child process
        self.args += [f"--/exts/omni.kit.test/pyCoverageEnabled={py_coverage_enabled}"]

        if py_coverage_enabled:
            self.allow_sampling = False
            py_coverage_filter = default_coverage_settings.filter or []
            py_coverage_deps_omit = []
            # If custom filter is specified, only use that list
            custom_filter = self.config.get("pyCoverageFilter", None)
            if custom_filter:
                py_coverage_filter = custom_filter
            else:
                # Append all python modules
                if self.config.get("pyCoverageIncludeModules", default_coverage_settings.include_modules):
                    for m in python_modules_names:
                        py_coverage_filter.append(m)

                # Append all python modules from the dependencies
                dependencies = [
                    {
                        "setting": "pyCoverageIncludeDependencies",
                        "default": default_coverage_settings.include_dependencies,
                        "config": self.ext_info,
                    },
                    {
                        "setting": "pyCoverageIncludeTestDependencies",
                        "default": default_coverage_settings.include_test_dependencies,
                        "config": self.config,
                    },
                ]
                for d in dependencies:
                    if not self.config.get(d["setting"], d["default"]):
                        continue
                    deps = d["config"].get("dependencies", [])
                    manager = omni.kit.app.get_app().get_extension_manager()
                    for ext_d in manager.get_extensions():
                        if ext_d["name"] not in deps:
                            continue
                        ext_info = manager.get_extension_dict(ext_d["id"])
                        py_coverage_filter.extend(get_python_modules(ext_info))
                        # also look for omit in dependencies
                        test_info = ext_info.get("test", None)
                        if isinstance(test_info, list) or isinstance(test_info, tuple):
                            for t in test_info:
                                for cov_omit in t.get("pyCoverageOmit", []):
                                    cov_omit = cov_omit.replace("\\", "/")
                                    if not os.path.isabs(cov_omit) and not cov_omit.startswith("*/"):
                                        cov_omit = "*/" + cov_omit
                                    py_coverage_deps_omit.append(cov_omit)

            if len(py_coverage_filter) > 0:
                for i, cov_filter in enumerate(py_coverage_filter):
                    self.args += [f"--/exts/omni.kit.test/pyCoverageFilter/{i}='{cov_filter}'"]

            # omit files/path for coverage
            default_py_coverage_omit = default_coverage_settings.omit or []
            py_coverage_omit = list(self.config.get("pyCoverageOmit", default_py_coverage_omit))
            py_coverage_omit.extend(py_coverage_deps_omit)
            if len(py_coverage_omit) > 0:
                for i, cov_omit in enumerate(py_coverage_omit):
                    cov_omit = cov_omit.replace("\\", "/")
                    if not os.path.isabs(cov_omit) and not cov_omit.startswith("*/"):
                        cov_omit = "*/" + cov_omit
                    self.args += [f"--/exts/omni.kit.test/pyCoverageOmit/{i}='{cov_omit}'"]

        # in coverage mode we generate a report at the end, need to set the settings on the parent process
        if coverage_mode:
            carb.settings.get_settings().set("/exts/omni.kit.test/pyCoverageEnabled", py_coverage_enabled)
            carb.settings.get_settings().set("/exts/omni.kit.test/testExtGenerateCoverageReport", True)

        # Extra extensions to run
        for ext in self.config.get("dependencies", []):
            self.args += ["--enable", ext]
            self.test_dependencies.append(ext)

        exts_to_enable = [self.ext_id] + self.test_dependencies

        # Check if skipped by code change analyzer based on extensions it is about to enable
        if self.context.change_analyzer:
            self.change_analyzer_result = self.context.change_analyzer.analyze(
                self.test_id, self.ext_name, exts_to_enable
            )
            if self.change_analyzer_result.should_skip_test:
                self.skip = True
            if not self.context.change_analyzer.allow_sampling():
                self.allow_sampling = False

        # Tests Sampling per extension
        default_sampling = float(
            get_setting("/exts/omni.kit.test/testExtSamplingFactor", default=SamplingFactor.UPPER_BOUND)
        )
        sampling_factor = clamp(
            self.config.get("samplingFactor", default_sampling), SamplingFactor.LOWER_BOUND, SamplingFactor.UPPER_BOUND
        )
        if sampling_factor == SamplingFactor.UPPER_BOUND:
            self.allow_sampling = False
        if self.allow_sampling and self._use_tests_sampling():
            self.args += [f"--/exts/omni.kit.test/samplingFactor={sampling_factor}"]

        # tests random order
        random_order = get_setting("/exts/omni.kit.test/testExtRandomOrder", default=False)
        if random_order:
            self.args += ["--/exts/omni.kit.test/testExtRandomOrder=1"]

        # Test Sampling Seed
        seed = int(get_setting("/exts/omni.kit.test/testExtSamplingSeed", default=-1))
        if seed >= 0:
            self.args += [f"--/exts/omni.kit.test/testExtSamplingSeed={seed}"]

        # Extra args
        self.args += list(get_setting("/exts/omni.kit.test/testExtArgs", default=[]))

        # Extra args
        self.args += self.config.get("args", [])

        # Build fail patterns
        self.patterns = FailPatterns(
            self.config.get("stdoutFailPatterns", {}).get("include", []),
            self.config.get("stdoutFailPatterns", {}).get("exclude", []),
        )
        self.patterns.merge(self.context.shared_patterns)

        # Pass all unprocessed argv down the line at the very end. They can also have another `--` potentially.
        unprocessed_argv = get_unprocessed_argv()
        if unprocessed_argv:
            self.args += unprocessed_argv

        # if in ui mode we need to remove --no-window
        if ui_mode:
            if "--no-window" in self.args:
                self.args.remove("--no-window")
        elif ("--no-window" not in self.args) and get_setting("/exts/omni.kit.test/autoAddNoWindow", default=True):
            if ("--show-test-window" not in argv) and ("--show-test-window" not in self.args):
                self.args.append("--no-window")

        # Other settings
        self.parallelizable = self.config.get("parallelizable", True)

    def _pre_test_run(self, test_run: int, retry_strategy: str):
        """Update arguments that must change between each test run"""
        if test_run > 0:
            for index, arg in enumerate(self.args):
                # make sure to use a different log file if we run tests multiple times
                if arg.startswith("--/log/file="):
                    ts = get_local_timestamp()
                    if is_running_on_ci():
                        self.log_file = f"{self.output_path}/{self.app_name}_{test_run}.log"
                    else:
                        self.log_file = f"{self.output_path}/{self.app_name}_{ts}_{test_run}.log"
                    self.args[index] = f"--/log/file='{self.log_file}'"
                # make sure to use a different random seed if present, only valid on some retry strategies
                if retry_strategy == RetryStrategy.ITERATIONS or retry_strategy == RetryStrategy.RERUN_UNTIL_FAILURE:
                    if arg.startswith("--/exts/omni.kit.test/testExtSamplingSeed="):
                        random_seed = random.randint(0, 2**16)
                        self.args[index] = f"--/exts/omni.kit.test/testExtSamplingSeed={random_seed}"

    def _use_tests_sampling(self) -> bool:
        # re-enable when is_app_external works
        # external_build = get_setting("/privacy/externalBuild")
        # if external_build:
        #     return False
        use_sampling = get_setting("/exts/omni.kit.test/useSampling", default=True)
        if not use_sampling:
            return False
        # getenv will return a string, so can't just use bool as bool("False") returns True
        use_sampling = os.getenv("OMNI_KIT_TEST_USE_SAMPLING", default="true").lower() in ("true", "1")
        if not use_sampling:
            return False
        sampling_context = get_setting("/exts/omni.kit.test/testExtSamplingContext")
        if sampling_context == SamplingContext.CI and is_running_on_ci():
            return True
        elif sampling_context == SamplingContext.LOCAL and not is_running_on_ci():
            return True
        return sampling_context == SamplingContext.ANY

    def get_cmd(self) -> str:
        return " ".join(self.args)

    def on_start(self):
        self.result = ExtTestResult()
        self.reporter.exttest_start(self.test_id, self.tc_test_id, self.ext_id, self.ext_name)
        self.stdout.write(BEGIN_SEPARATOR.format(self.test_id))

    def on_finish(self, test_result: bool):
        if test_result:
            self.stdout.write(END_SEPARATOR.format("PASSED", self.test_id, Colors.GREEN, Colors.RESET))
        else:
            self.stdout.write(END_SEPARATOR.format("FAILED", self.test_id, Colors.RED, Colors.RESET))
        self.reporter.exttest_stop(self.test_id, self.tc_test_id, passed=test_result)

    def on_fail(self, fail_message):
        # TC service messages can't match failure with a test start message when there are other tests in between.
        # As a work around in that case stop test and start again (send those messages). That makes it has 2 block
        # entries in the log, but gets reported as failed correctly.
        if is_running_in_teamcity():
            self.reporter.exttest_stop(self.test_id, self.tc_test_id, report=False)
            self.reporter.exttest_start(self.test_id, self.tc_test_id, self.ext_id, self.ext_name, report=False)

        self.reporter.exttest_fail(self.test_id, self.tc_test_id, "Error", fail_message)
        self.stdout.write(f"{Colors.RED}{fail_message}{Colors.RESET}\n")


async def kill_process_recursive(pid, stream):
    def _output(msg: str):
        teamcity_message("message", text=msg)
        stream.write(msg)

    def _terminate(proc: psutil.Process):
        try:
            proc.terminate()
        except psutil.AccessDenied as e:
            _warning(stream, f"Access denied: {e}")
        except psutil.ZombieProcess as e:
            _warning(stream, f"Encountered a zombie process: {e}")
        except psutil.NoSuchProcess as e:
            _warning(stream, f"Process no longer exists: {e}")
        except (psutil.Error, Exception) as e:
            _warning(stream, f"An error occurred: {str(e)}")

    try:
        process = psutil.Process(pid)
        # kill all children of test process (if any)
        for proc in process.children(recursive=True):
            if await crash_process(proc, stream):
                _output(
                    f"\nTest Process Timed out, crashing child test process to collect callstack, PID: {proc.pid}\n\n"
                )
            else:
                _output(
                    f"\nAttempt to crash child test process to collect callstack failed. Killing child test process, PID: {proc.pid}\n\n"
                )
                _terminate(proc)

        # kill the test process itself
        if await crash_process(process, stream):
            _output(f"\nTest Process Timed out, crashing test process to collect callstack, PID: {process.pid}\n\n")
        else:
            _output(
                f"\nAttempt to crash test process to collect callstack failed. Killing test process, PID: {process.pid}\n\n"
            )
            _terminate(process)
    except psutil.NoSuchProcess as e:
        _warning(stream, f"Process no longer exists: {e}")


PRAGMA_REGEX = re.compile(r"^##omni\.kit\.test\[(.*)\]")


def _extract_metadata_pragma(line, metadata):
    """
    Test subprocs can print specially formatted pragmas, that get picked up here as extra fields
    that get printed into the status report. Pragmas must be at the start of the line, and should
    be the only thing on that line.

    Format:
    ##omni.kit.test[op, key, value]
      op = operation type, either "set", "append" or "del" (str)
      key = name of the key (str)
      value = string value (str)

    Examples:
        # set a value
        ##omni.kit.test[set, foo, this is a message and spaces are allowed]

        # append a value to a list
        ##omni.kit.test[append, bah, test-13]
    """
    match = PRAGMA_REGEX.match(line)
    if not match:
        return False

    body = match.groups()[0]
    args = body.split(",")
    args = [x.strip() for x in args]
    if not args:
        return False

    op = args[0]
    args = args[1:]

    if op in ("set", "append"):
        if len(args) != 2:
            return False
        key, value = args
        if op == "set":
            metadata[key] = value
        elif op == "append":
            metadata.setdefault(key, []).append(value)
    elif op == "del":
        if len(args) != 1:
            return False
        key = args[0]
        del metadata[key]
    else:
        return False  # unsupported pragma op

    return True


async def _run_test_process(test: ExtTest) -> Tuple[int, List[str], Dict]:
    """Run test process and read stdout (use PIPE)."""

    returncode = 0
    fail_messages = []
    fail_patterns = defaultdict(list)
    test_run_metadata = {}
    proc = None
    try:
        test.stdout.write(f">>> running process: {test.get_cmd()}\n")
        _debug(test.stdout, f"fail patterns: {test.patterns}")

        async def run_proc():
            nonlocal proc
            proc = await asyncio.create_subprocess_exec(
                *test.args,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                bufsize=0,
            )

            while True:
                try:
                    async for line in proc.stdout:
                        suppress_line = False

                        line = line.decode(errors="replace").replace("\r\n", "\n").replace("\r", "\n")
                        # Check for failure on certain stdout message (like log errors)
                        nonlocal fail_messages
                        pattern_str, messages, exclude_matched = test.patterns.match_line(line)
                        if pattern_str and messages:
                            fail_patterns[pattern_str].append(messages)

                        # Check for special pragmas printed by the child proc that tell us to add custom
                        # fields to the formatted status report
                        try:
                            if _extract_metadata_pragma(line, test_run_metadata):
                                suppress_line = True
                        except:  # noqa
                            pass

                        # grab the number of tests
                        m = re.match(r"(?:Running|Printing All) Tests \(count: (\d+)\)", line, re.M)
                        if m:
                            try:
                                test.result.test_count = int(m.group(1))
                            except:  # noqa
                                pass

                        # replace with some generic message to avoid confusion when people search for [error] etc.
                        if exclude_matched and test.context.trim_excluded_messages:
                            line = "[...line contained error that was excluded by omni.kit.test...]\n"

                        if not suppress_line:
                            test.stdout.write("|| " + line)
                except ValueError:
                    # asyncio.streams._DEFAULT_LIMIT = 65536
                    line = "[...line with over 65536 characters raised an exception - PLEASE FIX!]\n"
                    test.stdout.write("|| " + line)
                else:
                    break

            await proc.wait()

            nonlocal returncode
            returncode = proc.returncode

            proc = None

        await asyncio.wait_for(run_proc(), timeout=test.timeout)

    except subprocess.CalledProcessError as e:
        returncode = e.returncode
        fail_messages.append(f"subprocess.CalledProcessError was raised: {e.output}")
    except asyncio.TimeoutError:
        returncode = TestReturnCode.UNIT_TEST_TIMEOUT
        fail_messages.append(
            f"Process timed out (timeout: {test.timeout} seconds), terminating. Check artifacts for .dmp files."
        )
        if proc:
            start_time = time.monotonic()
            await kill_process_recursive(proc.pid, test.stdout)
            test.result.kill_process_duration = time.monotonic() - start_time
    except NotImplementedError as e:
        fail_messages.append(
            f"The asyncio loop does not implement subprocess. This is known to happen when using SelectorEventLoop on Windows, exception {e}"
        )

    # loop all pattern matches and put them on top of the fail messages
    pattern_messages = []
    for pattern, messages in fail_patterns.items():
        pattern_messages.append(f"Matched {len(messages)} fail pattern '{pattern}' in stdout: ")
        for msg in messages:
            pattern_messages.append(f"    '{msg}'")
    fail_messages = pattern_messages + fail_messages

    # return code failure check.
    if returncode == TestReturnCode.UNIT_TESTS_FAILED:
        failing_tests_cnt = max(len(test_run_metadata.get(KEY_FAILING_TESTS, [])), 1)
        fail_messages.append(f"{failing_tests_cnt} test(s) failed.")
    elif returncode == TestReturnCode.UNIT_TEST_TIMEOUT:
        # fail_message already added, skip
        pass
    elif returncode == 1:
        # doctest will exit with return code 1 (EXIT_FAILURE)
        fail_messages.append("Tests failures detected, see log for details.")
    elif returncode != 0:
        # other return codes usually mean crash
        fail_messages.append("Process might have crashed or timed out.")

    # Check if any unittests were started but never completed (crashed/timed out/etc.)
    # When a test crash the 'stop' message is missing making test results harder to read, add them manually.
    for key, value in test_run_metadata.items():
        if type(value) == str and value.startswith(STARTED_UNITTEST):
            test_id = key
            tc_test_id = value.replace(STARTED_UNITTEST, "", 1)
            test.reporter.unittest_fail(
                test_id,
                tc_test_id,
                "Error",
                f"Test started but never finished, test: {tc_test_id}. Test likely crashed or timed out.",
                ext_test_id=test.test_id,
            )
            test.reporter.unittest_stop(test_id, tc_test_id, ext_test_id=test.test_id)

    return (returncode, fail_messages, test_run_metadata)


def _propagate_args(argv, arg_name, has_value=False, starts_with=False):
    args = []
    for i, arg in enumerate(argv):
        if arg == arg_name or (starts_with and arg.startswith(arg_name)):
            args += [arg]
            if has_value:
                args += [argv[i + 1]]
    return args


def _parse_arg_shortcut(argv, arg_name):
    for i, arg in enumerate(argv):
        if arg == arg_name:
            return argv[i + 1]
    return None


def _get_test_configs_for_ext(ext_info, name_filter=None) -> List[Dict]:
    test_config = ext_info.get("test", None)

    configs = []

    if not test_config:
        # no [[test]] entry
        configs.append({})
    elif isinstance(test_config, dict):
        # [test] entry
        configs.append(test_config)
    elif isinstance(test_config, list) or isinstance(test_config, tuple):
        # [[test]] entry
        if len(test_config) == 0:
            configs.append({})
        else:
            configs.extend(test_config)

    # Auto-add a special config for startup only test (not test dependencies). If already defined a test named "startup"
    # then just mark it as startup only. That allows to customize the startup-only test (like exclude certain errors).
    # (do not do it on ETM yet, as it will lead to a lot of failures)
    startup_config = next((c for c in configs if c.get("name") == "startup"), None)
    autoadd_startup_test = not is_etm_run()
    if not startup_config and autoadd_startup_test:
        startup_config = {
            "name": "startup",
        }
        configs.insert(0, startup_config)
    if startup_config:
        startup_config[STARTUP_ONLY_TEST_MARKER] = True
        startup_config["pythonTests"] = { "include": [""] }

    # Filter those matching the name filter
    configs = [t for t in configs if not name_filter or match(t.get("name", DEFAULT_TEST_NAME), [name_filter])]

    # Filter out disabled
    configs = [t for t in configs if t.get("enabled", True)]

    return configs


def is_matching_list(ext_id, ext_name, ext_list):
    return any(fnmatch.fnmatch(ext_id, p) or fnmatch.fnmatch(ext_name, p) for p in ext_list)


def get_registry_extensions(max_attempts: int, delay: float, backoff_factor: float):
    manager = omni.kit.app.get_app().get_extension_manager()
    attempt = 0
    current_delay = delay

    while attempt < max_attempts:
        manager.sync_registry()
        exts = manager.get_registry_extensions()
        if exts:
            return exts
        else:
            attempt += 1
            if attempt == max_attempts:
                return exts
            print(f"Attempt {attempt} failed. Retrying in {current_delay} seconds...")
            time.sleep(current_delay)
            current_delay *= backoff_factor
    return []


def _find_latest_valid_ext_id(ext_def: str, match_version_as_string: bool, use_registry: bool, manager) -> str | None:
    # Use extension manager to get matching version and pick highest one (they are sorted)
    ext_ids = [v["id"] for v in manager.fetch_extension_versions(ext_def)]
    if match_version_as_string:
        ext_ids = [v for v in ext_ids if v.startswith(ext_def)]

    # Take highest version, but if we are not using registry skip remote local one:
    for ext_id in ext_ids:
        metadata = None
        if use_registry:
            remote_info = manager.get_registry_extension_dict(ext_id)
            if remote_info is not None:
                metadata = remote_info.get_dict()
        if metadata is None:
            local_info = manager.get_extension_dict(ext_id)
            if local_info is not None:
                metadata = local_info.get_dict()
        # Check if extension is not yanked
        if metadata is not None and not metadata.get("package", {}).get("yanked", False):
            return ext_id
    return None

def _build_exts_set(
    exts: List[str], exclude: List[str], use_registry: bool, match_version_as_string: bool
) -> List[str]:
    manager = omni.kit.app.get_app().get_extension_manager()

    all_exts = manager.get_extensions()

    if use_registry:
        all_exts += get_registry_extensions(max_attempts=3, delay=30.0, backoff_factor=2.0)

    def is_match_ext(ext_id, ext_name, ext_def):
        return (fnmatch.fnmatch(ext_id, ext_def) or fnmatch.fnmatch(ext_name, ext_def)) and not is_matching_list(
            ext_id, ext_name, exclude
        )

    exts_to_test = set()
    for ext_def in exts:
        # Empty string is same as "all"
        if ext_def == "":
            ext_def = "*"

        # If wildcard is used, match all
        if "*" in ext_def:
            exts_to_test.update([e["id"] for e in all_exts if is_match_ext(e["id"], e["name"], ext_def)])
        else:
            ext_id = _find_latest_valid_ext_id(ext_def, match_version_as_string, use_registry, manager)
            if ext_id:
                exts_to_test.add(ext_id)
    return sorted(exts_to_test)


def _format_cmdline(cmdline: str) -> str:
    """Format commandline printed from CI so that we can run it locally"""
    cmdline = cmdline.replace("\\", "/").replace("//", "/")
    if is_running_on_ci():
        exe_path = cmdline.split(" ")[0]
        index = exe_path.find("/_build/")
        if index != -1:
            path_to_remove = exe_path[:index]
            cmdline = (
                cmdline.replace(path_to_remove, ".")
                .replace(path_to_remove.lower(), ".")
                .replace(path_to_remove.replace("/", "\\"), ".")
            )
    return cmdline


def _get_test_cmdline(ext_name: str, failed_tests: list = []) -> list:
    """Return an example cmdline to run extension tests or a single unittest"""
    cmdline = []
    try:
        shell_ext = carb.tokens.get_tokens_interface().resolve("${shell_ext}")
        kit_exe = carb.tokens.get_tokens_interface().resolve("${kit}")
        path_to_kit = _format_cmdline(os.path.relpath(kit_exe, os.getcwd()))
        if not path_to_kit.startswith("./"):
            path_to_kit = f"./{path_to_kit}"
        test_file = f"{path_to_kit}/tests-{ext_name}{shell_ext}"
        if failed_tests:
            test_name = failed_tests[0].rsplit(".")[-1]
            cmdline.append(f"    Cmdline to run a single unittest: {test_file} -f *{test_name}")
        cmdline.append(f"    Cmdline to run the extension tests: {test_file}")
    except:  # noqa
        pass
    return cmdline


async def gather_with_concurrency(n, *tasks):
    semaphore = asyncio.Semaphore(n)

    async def sem_task(task):
        async with semaphore:
            return await task

    return await asyncio.gather(*(sem_task(task) for task in tasks))


async def run_serial_and_parallel_tasks(parallel_tasks, serial_tasks, max_parallel_tasks: int):
    for r in serial_tasks:
        yield await r

    for r in await gather_with_concurrency(max_parallel_tasks, *parallel_tasks):
        yield r


async def _run_ext_test(run_context: TestRunContext, test: ExtTest, on_status_report_fn):
    def _print_result(strategy: str, result_str: Optional[str] = None):
        if result_str is None:
            result_str = "succeeded" if test.result.passed else "failed"
        print(f"{test.test_id} test {result_str} ({strategy} {test_run + 1} out of {run_context.max_test_run})")

    teamcity_test_retry_support(run_context.retry_strategy == RetryStrategy.RETRY_ON_FAILURE)

    # Allow retrying tests multiple times:
    for test_run in range(run_context.max_test_run):
        is_last_try = (test_run == run_context.max_test_run - 1) or (
            run_context.retry_strategy == RetryStrategy.NO_RETRY
        )
        retry_failed_tests = run_context.retry_strategy == RetryStrategy.RETRY_ON_FAILURE

        test._pre_test_run(test_run, run_context.retry_strategy)
        test = await _run_ext_test_once(test, on_status_report_fn, is_last_try, retry_failed_tests)
        # depending on the retry strategy we might continue or exit the loop
        if run_context.retry_strategy == RetryStrategy.NO_RETRY:
            # max_test_run is ignored in no-retry strategy
            break
        elif run_context.retry_strategy == RetryStrategy.RETRY_ON_FAILURE:
            # retry on failure - stop at first success otherwise continue
            result_str = "succeeded"
            if not test.result.passed:
                result_str = "failed" if is_last_try or not test.can_retry else "failed, retrying..."

            # when it succeeds on first try we don't print 'attempt 1 of 3'
            if test.result.passed and test_run == 0:
                print(f"{test.test_id} test {result_str}")
            else:
                _print_result("attempt", result_str)

            # exit loop if we succeeded or can't retry
            if test.result.passed or not test.can_retry:
                break
            else:
                test.retries += 1
        elif run_context.retry_strategy == RetryStrategy.ITERATIONS:
            # iterations - continue until the end
            _print_result("iteration")
        elif run_context.retry_strategy == RetryStrategy.RERUN_UNTIL_FAILURE:
            # rerun until failure - stop at first failure otherwise continue
            _print_result("rerun")
            if not test.result.passed:
                break
        else:
            _error(sys.stderr, f"Invalid retry strategy '{run_context.retry_strategy}'")

    return test

def _test_sanity_check(test: ExtTest):
    manager = omni.kit.app.get_app().get_extension_manager()

    solve_result, ext_deps, err = manager.solve_extensions(
        [test.ext_id], add_enabled=False, return_only_disabled=False
    )
    if not solve_result:
        # try enabling registry and trying again:
        manager.sync_registry()
        solve_result, ext_deps, err = manager.solve_extensions(
            [test.ext_id], add_enabled=False, return_only_disabled=False
        )
        if not solve_result:
            return [f"Can't solve extensions for {test.ext_id}. Error: {err}"]

    ext_deps = {e["name"] for e in ext_deps}
    err_messages = []
    for test_dep in test.test_dependencies:
        if test_dep in ext_deps:
            err_messages.append(f"[[test]] definition sanity check failure: test dependency {test_dep} is already a dependency of {test.ext_id}, remove it from test dependencies.")

    return err_messages


async def _run_ext_test_once(test: ExtTest, on_status_report_fn, is_last_try: bool, retry_failed_tests: bool):
    ext = test.ext_id
    if on_status_report_fn:
        on_status_report_fn(test.test_id, TestRunStatus.RUNNING)

    # Starting test
    test.on_start()

    err_messages = []
    metadata = {}
    cmd = ""
    returncode = 0
    if test.valid:
        cmd = test.get_cmd()
        start_time = time.monotonic()

        # Sanity checks are new and a lot of extensions would fail them on ETM. Can enable them later.
        sanity_checks_enabled = get_setting("/exts/omni.kit.test/testExtSanityChecksEnabled", default=True)
        if sanity_checks_enabled and not is_etm_run():
            err_messages += _test_sanity_check(test)

        # Run test process
        returncode, run_err_messages, metadata = await _run_test_process(test)
        err_messages += run_err_messages

        test.result.duration = round(time.monotonic() - start_time - test.result.kill_process_duration, 2)
        test.result.unreliable = 1 if test.unreliable else 0
    else:
        err_messages.append(f"Failed to run process for extension testing (ext: {ext}).")

    if returncode != 0:
        # Grab failed tests
        test.failed_tests = list(metadata.pop(KEY_FAILING_TESTS, []))
        for key, value in list(metadata.items()):
            if type(value) == str and value.startswith(STARTED_UNITTEST):
                test_id = key
                test.failed_tests.append(test_id + " (started but never finished)")
                del metadata[key]

        if retry_failed_tests:
            # remove failed tests from previous run if any
            test.args = [item for item in test.args if not item.startswith("--/exts/omni.kit.test/retryFailedTests")]

            # Only retry failed tests if all conditions are met:
            # - retry-on-failure strategy selected
            # - metadata with failing tests is present
            # - extension tests reported failures but no crash
            # - at least on retry left to do (ie: not last retry)
            if test.failed_tests and returncode == TestReturnCode.UNIT_TESTS_FAILED and not is_last_try:
                # add new failed tests as args for the next run
                for i, test_id in enumerate(test.failed_tests):
                    test.args.append(f"--/exts/omni.kit.test/retryFailedTests/{i}='{test_id}'")
            else:
                # disable retries if duration is above max duration
                max_duration = int(get_setting("/exts/omni.kit.test/testExtMaxDurationForRetry", default=0))
                if max_duration != 0 and test.result.duration > max_duration:
                    err_messages.append(
                        f"Note: retries were disabled for this extension since its tests duration "
                        f"of {test.result.duration:0.1f}s exceeds testExtMaxDurationForRetry set to {max_duration}s"
                    )
                    test.can_retry = False
                    is_last_try = True

    if len(err_messages) == 0:
        test.result.passed = True
        test.stdout.write("[ ok ] Extension test passed.\n")
    else:
        # Report failure and mark overall run as failure
        test.result.passed = False

        spaces_8 = " " * 8
        spaces_12 = " " * 12
        messages_str = f"\n{spaces_8}".join([""] + err_messages)

        fail_message_lines = [
            "",
            "[fail] Extension Test failed. Details:",
            f"    Cmdline: {_format_cmdline(cmd)}",
        ]
        fail_message_lines += _get_test_cmdline(test.ext_name, test.failed_tests)
        fail_message_lines += [
            f"    Return code: {returncode} ({returncode & (2**31-1):#010x})",
            f"    Failure reason(s): {messages_str}",
        ]

        details_message_lines = ["    Details:"]

        if metadata:
            details_message_lines.append(f"{spaces_8}Metadata:")
            for key, value in sorted(metadata.items()):
                details_message_lines.append(f"{spaces_12}{key}: {value}")

        if test.failed_tests:
            messages_str = f"\n{spaces_12}".join([""] + test.failed_tests)
            details_message_lines.append(f"{spaces_8}{KEY_FAILING_TESTS}: {messages_str}")

        if not omni.kit.app.get_app().is_app_external():
            url = f"http://omnitests.nvidia.com/?query={test.test_id}"
            details_message_lines.append(f"{spaces_8}Test history:")
            details_message_lines.append(f"{spaces_12}{url}")

        fail_message = "\n".join(fail_message_lines + details_message_lines)

        if test.unreliable:
            test.result.unreliable_fail = 1
            test.stdout.write("[fail] Extension test failed, but marked as unreliable.\n")
        else:
            test.result.fail = 1
            test.stdout.write("[fail] Extension test failed.\n")

        if is_last_try:
            test.on_fail(fail_message)
        if on_status_report_fn:
            on_status_report_fn(test.test_id, TestRunStatus.FAILED, fail_message=fail_message, ext_test=test)

    test.on_finish(test.result.passed)
    if test.result.passed and on_status_report_fn:
        on_status_report_fn(test.test_id, TestRunStatus.PASSED, ext_test=test)

    # dump stdout, acts as stdout sync point for parallel run
    if test.stdout != sys.stdout:
        if test.context.trim_stdout_on_success and test.result.passed:
            for line in test.stdout.getvalue().splitlines():
                # We still want to print all service messages to correctly output number of tests on TC and all that.
                if "##teamcity[" in line:
                    sys.stdout.write(line)
                    sys.stdout.write("\n")
            sys.stdout.write(
                f"[omni.kit.test] Stdout was trimmed. Look for the Kit log file '{test.log_file}' in TC artifacts for the full output.\n"
            )
        else:
            sys.stdout.write(test.stdout.getvalue())

        sys.stdout.flush()
        # reset test.stdout (io.StringIO)
        test.stdout.truncate(0)
        test.stdout.seek(0)

    return test


def _build_test_id(test_type: str, ext: str, app: str = "", test_name: str = "") -> str:
    s = ""
    if test_type:
        s += f"{test_type}:"
    s += ext_id_to_fullname(ext)
    if test_name and test_name != DEFAULT_TEST_NAME:
        s += f"-{test_name}"
    if app:
        s += f"_app:{app}"
    return s


async def _run_ext_tests(exts, on_status_report_fn, exclude_exts, only_list=False) -> bool:
    run_context = TestRunContext()

    use_registry = get_setting("/exts/omni.kit.test/testExtUseRegistry", default=False)

    match_version_as_string = get_setting("/exts/omni.kit.test/testExtMatchVersionAsString", default=False)

    test_type = get_setting("/exts/omni.kit.test/testExtTestType", default="exttest")

    # Test Name filtering (support shorter version)
    test_name_filter = _parse_arg_shortcut(get_argv(), "-n")
    if not test_name_filter:
        test_name_filter = get_setting("/exts/omni.kit.test/testExtTestNameFilter", default="")

    max_parallel_procs = int(get_setting("/exts/omni.kit.test/testExtMaxParallelProcesses", default=-1))
    if max_parallel_procs <= 0:
        max_parallel_procs = multiprocessing.cpu_count()

    exts_to_test = _build_exts_set(exts, exclude_exts, use_registry, match_version_as_string)

    # Prepare an app:
    test_app = TestApp(sys.stdout)

    def fail_all(fail_message):
        reporter = TestReporter(sys.stdout)
        for ext in exts:
            message = fail_message.format(ext)
            test_id = _build_test_id(test_type, ext, test_app.name)
            tc_test_id = test_id.replace(".", "+") + ".[PROCESS CHECK]"
            _error(sys.stderr, message)
            # add start / fail / stop messages for TC + our own reporter
            reporter.exttest_start(test_id, tc_test_id, ext, ext)
            reporter.exttest_fail(test_id, tc_test_id, fail_type="Error", fail_message=message)
            reporter.exttest_stop(test_id, tc_test_id, passed=False)
            if on_status_report_fn:
                on_status_report_fn(test_id, TestRunStatus.FAILED, fail_message=message)

    # If no extensions found report query entries as failures
    if len(exts_to_test) == 0:
        fail_all("Can't find any extension matching: '{0}'.")

    # If no app found report query entries as failures
    if not test_app.path:
        fail_all(f"Can't find app: {test_app.name}")
        exts_to_test = []

    # Prepare test run tasks, put into separate serial and parallel queues
    parallel_tasks = []
    serial_tasks = []
    is_parallel_run = max_parallel_procs > 1 and len(exts_to_test) > 1
    exts_issues = []
    total = 0
    for ext in exts_to_test:
        ext_info = _prepare_ext_for_testing(ext)
        if ext_info:
            test_configs = _get_test_configs_for_ext(ext_info, test_name_filter)
            unique_test_names = set()
            for test_config in test_configs:
                valid = True
                test_name = test_config.get("name", DEFAULT_TEST_NAME)
                if test_name in unique_test_names:
                    _error(
                        sys.stderr,
                        f"Extension {ext} has multiple [[test]] entry with the same 'name' attribute. It should be unique, default is '{DEFAULT_TEST_NAME}'",
                    )
                    valid = False
                else:
                    unique_test_names.add(test_name)
                    total += 1

                # Build test id.
                test_id = _build_test_id(test_type, ext, test_app.name, test_name)

                if only_list:
                    print(f"test_id: '{test_id}'")
                    continue

                test = ExtTest(
                    ext,
                    ext_info,
                    test_config,
                    test_id,
                    is_parallel_run,
                    run_context=run_context,
                    test_app=test_app,
                    valid=valid,
                )

                # fmt: off
                # both means we run all tests (reliable and unreliable)
                # otherwise we either run reliable tests only or unreliable tests only, so we skip accordingly
                if run_context.run_unreliable_tests != RunExtTests.BOTH and int(run_context.run_unreliable_tests) != int(test.unreliable):
                    test_unreliable = "unreliable" if test.unreliable else "reliable"
                    run_unreliable = "unreliable" if run_context.run_unreliable_tests == RunExtTests.UNRELIABLE_ONLY else "reliable"
                    print(f"[INFO] {test_id} skipped because it's marked as {test_unreliable} and we currently run all {run_unreliable} tests")
                    total -= 1
                    continue
                # fmt: on

                # Test skipped itself? (it should have explained it already by now)
                if test.skip:
                    total -= 1
                    continue

                task = _run_ext_test(run_context, test, on_status_report_fn)
                if test.parallelizable:
                    parallel_tasks.append(task)
                else:
                    serial_tasks.append(task)
        else:
            exts_issues.append(ext)

    intro = f"Running {total} Extension Test Process(es)."
    if run_context.run_unreliable_tests == RunExtTests.UNRELIABLE_ONLY:
        intro = "[Unreliable Tests Run] " + intro
    print(intro)

    # Actual test run:
    finished_tests: List[ExtTest] = []
    fail_count = 0
    unreliable_fail_count = 0
    unreliable_total = 0
    async for test in run_serial_and_parallel_tasks(parallel_tasks, serial_tasks, max_parallel_procs):
        unreliable_total += test.result.unreliable
        unreliable_fail_count += test.result.unreliable_fail
        fail_count += test.result.fail
        finished_tests.append(test)

    if only_list:
        print(f"Found {total} tests processes to run.")
        return True

    return_result = True

    def generate_summary():
        for test in finished_tests:
            if test.result.passed:
                if test.retries > 0:
                    res_str = "[retry ok]"
                else:
                    res_str = "[   ok   ]"
            else:
                res_str = "[  fail  ]"
            if test.result.unreliable:
                res_str += " [unreliable]"
            res_str += f" [{test.result.duration:5.1f}s]"
            res_str += f" {test.test_id}"
            res_str += f" (Count: {test.result.test_count})"
            yield f"{res_str}"
        for ext in exts_issues:
            res_str = f"[  fail  ] {ext} (extension registry issue)"
            yield f"{res_str}"

    def get_failed_tests():
        all_failed_tests = [t for test in finished_tests for t in test.failed_tests]
        if all_failed_tests:
            yield f"\nFailing tests (Count: {len(all_failed_tests)}) :"
            for test_name in all_failed_tests:
                yield f"  - {test_name}"

    # Print summary
    test_results_file = os.path.join(run_context.output_path, "ext_test_results.txt")
    with open(test_results_file, "a") as f:

        def report(line):
            print(line)
            f.write(line + "\n")

        report("\n")
        report("=" * 60)
        report(f"Extension Tests Run Summary (Date: {run_context.start_ts})")
        report("=" * 60)
        report(" app: {}".format(test_app.name if not test_app.is_empty else "[empty]"))
        report(f" retry strategy: {run_context.retry_strategy}," f" max test run: {run_context.max_test_run}")
        report("=" * 60)
        for line in generate_summary():
            report(line)
        for line in get_failed_tests():
            report(line)
        report("=" * 60)
        report("=" * 60)

        if unreliable_total > 0:
            report(
                f"UNRELIABLE TESTS REPORT: {unreliable_fail_count} unreliable tests processes failed out of {unreliable_total}."
            )

        # Exit with non-zero code on failure
        if fail_count > 0 or len(exts_issues) > 0:
            if fail_count > 0:
                report(f"[ERROR] {fail_count} tests processes failed out of {total}.")
            if len(exts_issues) > 0:
                report(f"[ERROR] {len(exts_issues)} extension registry issue.")
            return_result = False
        else:
            report(f"[OK] All {total} tests processes returned 0.")

    # Report all results
    for test in finished_tests:
        test.reporter.report_result(test)

    return return_result


def run_ext_tests(test_exts, on_finish_fn=None, on_status_report_fn=None, exclude_exts=[]):
    def on_status_report(*args, **kwargs):
        if on_status_report_fn:
            on_status_report_fn(*args, **kwargs)
        _test_status_report(*args, **kwargs)

    async def run():
        result = await _run_ext_tests(test_exts, on_status_report, exclude_exts)
        if on_finish_fn:
            on_finish_fn(result)

    return omni.kit.async_engine.run_coroutine(run())
