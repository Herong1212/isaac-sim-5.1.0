import fnmatch
import glob
import json
import os
import pathlib
import platform
import shutil
import sys
import time
import xml.etree.ElementTree as ET
from collections import defaultdict, OrderedDict
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from functools import lru_cache
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import carb
import carb.settings
import carb.tokens
import omni.kit.test
import psutil

from .nvdf import post_coverage_to_nvdf, post_to_nvdf
from .teamcity import is_running_in_teamcity, teamcity_message, teamcity_publish_artifact, teamcity_status
from .test_coverage import generate_coverage_report
from .utils import (
    ext_id_to_fullname,
    get_ext_test_id,
    get_global_test_output_path,
    get_setting,
    get_test_output_path,
    is_running_on_ci,
)

CURRENT_PATH = Path(__file__).parent
HTML_PATH = CURRENT_PATH.parent.parent.parent.joinpath("html")

REPORT_FILENAME = "report.jsonl"
RESULTS_FILENAME = "results.xml"


@lru_cache()
def get_report_filepath():
    return os.path.join(get_test_output_path(), REPORT_FILENAME)


@lru_cache()
def get_results_filepath():
    return os.path.join(get_test_output_path(), RESULTS_FILENAME)


def _load_report_data(report_path):
    data = []
    with open(report_path, "r") as f:
        for line in f:
            data.append(json.loads(line))
    return data


def _get_tc_test_id(test_id):
    return test_id.replace(".", "+")


class TestReporter:
    """Combines TC reports to stdout and JSON lines report to a file"""

    def __init__(self, stream=sys.stdout):
        self._stream = stream
        self._timers = {}
        self._report_filepath = get_report_filepath()
        self.unreliable_tests = get_setting("/exts/omni.kit.test/unreliableTests", default=[])
        self.parallel_run = get_setting("/exts/omni.kit.test/parallelRun", default=False)

    def _get_duration_ns(self, test_id: str) -> int:
        end_time = time.perf_counter_ns()
        try:
            start_time = self._timers.pop(test_id)
            duration_ns = end_time - start_time
        except KeyError:
            duration_ns = 0
        return duration_ns

    def _get_duration_s(self, test_id: str) -> float:
        duration_ns = self._get_duration_ns(test_id)
        return round(duration_ns * (10**-9), 3)

    def _is_unreliable(self, test_id):
        return any(fnmatch.fnmatch(test_id, p) for p in self.unreliable_tests)

    def set_output_path(self, output_path: str):
        self._report_filepath = os.path.join(output_path, REPORT_FILENAME)

    def _write_report(self, data: dict):
        if self._report_filepath:
            with open(self._report_filepath, "a") as f:
                f.write(json.dumps(data))
                f.write("\n")

    def unittest_start(self, test_id, tc_test_id, captureStandardOutput="false"):
        teamcity_message(
            "testStarted", stream=self._stream, name=tc_test_id, captureStandardOutput=captureStandardOutput
        )
        self._timers[test_id] = time.perf_counter_ns()
        self._write_report(
            {
                "event": "start",
                "test_type": "unittest",
                "test_id": test_id,
                "ext_test_id": get_ext_test_id(),
                "unreliable": self._is_unreliable(test_id),
                "parallel_run": self.parallel_run,
                "start_time": time.time(),
            }
        )

    def unittest_stop(self, test_id, tc_test_id, passed=False, skipped=False, skip_reason="", ext_test_id: str = ""):
        duration_s = self._get_duration_s(test_id)
        if skipped:
            teamcity_message("testIgnored", stream=self._stream, name=tc_test_id, message=skip_reason)

        teamcity_message("testFinished", stream=self._stream, name=tc_test_id)
        self._write_report(
            {
                "event": "stop",
                "test_type": "unittest",
                "test_id": test_id,
                "ext_test_id": ext_test_id or get_ext_test_id(),
                "passed": passed,
                "skipped": skipped,
                "skip_reason": skip_reason,
                "stop_time": time.time(),
                "duration": duration_s,
            }
        )

    def unittest_fail(self, test_id, tc_test_id, fail_type: str, fail_message: str, ext_test_id: str = ""):
        teamcity_message("testFailed", stream=self._stream, name=tc_test_id, fail_type=fail_type, message=fail_message)
        self._write_report(
            {
                "event": "fail",
                "test_type": "unittest",
                "test_id": test_id,
                "ext_test_id": ext_test_id or get_ext_test_id(),
                "fail_type": fail_type,
                "message": fail_message,
            }
        )

    def exttest_start(self, test_id, tc_test_id, ext_id, ext_name, captureStandardOutput="false", report=True):
        teamcity_message(
            "testStarted", stream=self._stream, name=tc_test_id, captureStandardOutput=captureStandardOutput
        )
        if report:
            self._timers[test_id] = time.perf_counter_ns()
            self._write_report(
                {
                    "event": "start",
                    "test_type": "exttest",
                    "test_id": test_id,
                    "ext_id": ext_id,
                    "ext_name": ext_name,
                    "start_time": time.time(),
                }
            )

    def exttest_stop(self, test_id, tc_test_id, passed=False, skipped=False, report=True):
        duration_s = self._get_duration_s(test_id)
        if skipped:
            teamcity_message("testIgnored", stream=self._stream, name=tc_test_id, message="skipped")

        teamcity_message("testFinished", stream=self._stream, name=tc_test_id)
        if report:
            self._write_report(
                {
                    "event": "stop",
                    "test_type": "exttest",
                    "test_id": test_id,
                    "passed": passed,
                    "skipped": skipped,
                    "stop_time": time.time(),
                    "duration": duration_s,
                }
            )

    def exttest_fail(self, test_id, tc_test_id, fail_type: str, fail_message: str):
        teamcity_message("testFailed", stream=self._stream, name=tc_test_id, fail_type=fail_type, message=fail_message)
        self._write_report(
            {
                "event": "fail",
                "test_type": "exttest",
                "test_id": test_id,
                "fail_type": fail_type,
                "message": fail_message,
            }
        )

    def report_result(self, test):
        """Write tests results data we want to later show on the html report and in elastic"""
        res = defaultdict(dict)
        res["config"] = test.config
        res["retries"] = test.retries
        res["timeout"] = test.timeout if test.timeout else 0
        ext_info = test.ext_info
        ext_dict = ext_info.get_dict()
        res["state"]["enabled"] = ext_dict.get("state", {}).get("enabled", False)
        res["package"]["version"] = ext_dict.get("package", {}).get("version", "")
        res.update(vars(test.result))

        change = {}
        if test.change_analyzer_result:
            change["skip"] = test.change_analyzer_result.should_skip_test
            change["startup_sequence_hash"] = test.change_analyzer_result.startup_sequence_hash
            change["tested_ext_hash"] = test.change_analyzer_result.tested_ext_hash
            change["kernel_version"] = test.change_analyzer_result.kernel_version

        self._write_report(
            {
                "event": "result",
                "test_type": "exttest",
                "test_id": test.test_id,
                "ext_id": test.ext_id,
                "ext_name": test.ext_name,
                "test_bucket": test.bucket_name,
                "unreliable": test.config.get("unreliable", False),
                "parallel_run": get_setting("/exts/omni.kit.test/parallelRun", default=False),
                "change_analyzer": change,
                "result": res,
            }
        )


# TODO: this function should be rewritten to avoid any guessing
def _get_extension_name(path: str, ext_id_to_name: dict):
    # if ext_id is in the path return that extension name
    for k, v in ext_id_to_name.items():
        if k in path:
            return v

    p = Path(path)
    for i, e in enumerate(p.parts):
        if e == "exts" or e == "extscore":
            if p.parts[i + 1][0:1].isdigit():
                return ext_id_to_fullname(p.parts[i + 2])
            else:
                return p.parts[i + 1]
        elif e == "extscache" or e == "extsPhysics" or e == "extsPhysicsRepo":
            # exts from cache will be named like this: omni.ramp-103.0.10+103.1.wx64.r.cp37
            # exts from physics will be named like this: omni.physx-1.5.0-5.1
            return ext_id_to_fullname(p.parts[i + 1])
        elif e == "extensions":
            # on linux we'll have paths from source/extensions/<ext_name>
            return p.parts[i + 1]

    carb.log_warn(f"Could not get extension name for {path}")
    return "_unsorted"


class ExtCoverage:
    def __init__(self):
        self.ext_id: str = ""
        self.ext_name: str = ""
        self.covered_lines = []
        self.num_statements = []
        self.test_result = {}

    def mean_cov(self):
        statements = self.sum_statements()
        if statements == 0:
            return 0
        return (self.sum_covered_lines() / statements) * 100.0

    def sum_covered_lines(self):
        return sum(self.covered_lines)

    def sum_statements(self):
        return sum(self.num_statements)


# Note that the combined coverage data will 'merge' (or 'lose') the test config because the coverage is reported
# at the filename level. For example an extension with 2 configs, omni.kit.renderer.core [default, compatibility]
# will produce 2 .pycov files, but in the combined report (json) it will be merged per source file, so no way to know
# what was the coverage for default vs compatibility, we'll get to coverage for all of omni.kit.renderer.core tests
def _build_ext_coverage(coverage_data: dict, ext_id_to_name: dict) -> Dict[str, ExtCoverage]:
    exts = defaultdict(ExtCoverage)
    for file, info in coverage_data["files"].items():
        ext_name = _get_extension_name(file, ext_id_to_name)
        exts[ext_name].ext_name = ext_name
        exts[ext_name].covered_lines.append(info["summary"]["covered_lines"])
        exts[ext_name].num_statements.append(info["summary"]["num_statements"])
    return exts


def _report_unreliable_tests(report_data):
    # Dummy tests to group all "unreliable" tests and report (convenience for TC UI)
    unreliable_failed = [r for r in report_data if r["event"] == "result" and r["result"]["unreliable_fail"] == 1]
    reporter = TestReporter()
    total = len(unreliable_failed)
    if total > 0:
        dummy_test_id = "UNRELIABLE_TESTS"
        summary = ""
        for r in unreliable_failed:
            test_result = r["result"]
            summary += " [{0:5.1f}s] {1} (Count: {2})\n".format(
                test_result["duration"], r["test_id"], test_result["test_count"]
            )
        reporter.unittest_start(dummy_test_id, dummy_test_id)
        message = f"There are {total} tests that fail, but marked as unreliable:\n{summary}"
        reporter.unittest_fail(dummy_test_id, dummy_test_id, "Error", message)
        print(message)
        reporter.unittest_stop(dummy_test_id, dummy_test_id)


def _build_test_data_html(report_data):
    # consider retries: start, fail, start, (nothing) -> success
    # for each fail look back and add extra data that this test will pass or fail.
    # it is convenient for the next code to know ahead of time if test will pass.
    started_tests = {}
    for e in report_data:
        if e["event"] == "start":
            started_tests[e["test_id"]] = e
        elif e["event"] == "fail":
            started_tests[e["test_id"]]["will_pass"] = False

    results = {item["test_id"]: item["result"] for item in report_data if item["event"] == "result"}

    RESULT_EMOJI = {True: "&#9989;", False: "&#10060;"}
    COLOR_CLASS = {True: "add-green-color", False: "add-red-color"}

    unreliable = False
    html_data = '<ul class="test_list">\n'
    depth = 0

    for e in report_data:
        if e["event"] == "start":
            # reset depth if needed (missing stop event)
            if e["test_type"] == "exttest" and depth > 0:
                depth -= 1
                while depth > 0:
                    html_data += "</ul>\n"
                    depth -= 1

            depth += 1
            if depth > 1:
                html_data += "<ul>\n"

            test_id = e["test_id"]
            passed = e.get("will_pass", True)

            extra = ""
            attr = ""

            # Root test ([[test]] entry)
            # Reset unreliable marker
            if depth == 1:
                unreliable = False
                # Get more stats about the whole [[test]] run
                if test_id in results:
                    test_result = results[test_id]
                    extra += " [{0:5.1f}s]".format(test_result["duration"])
                    unreliable = bool(test_result["unreliable"])
                    passed = test_result["passed"]

            style_class = COLOR_CLASS[passed]

            if unreliable:
                extra += " <b>[unreliable]</b>"
                style_class = "add-yellow-color unreliable"

            html_data += '<li class="{0}" {4}>{3} {1} {2}</li>\n'.format(
                style_class, extra, test_id, RESULT_EMOJI[passed], attr
            )

        if e["event"] == "stop":
            depth -= 1
            if depth > 0:
                html_data += "</ul>\n"

    html_data += "</ul>\n"

    return html_data


def _post_build_status(report_data: list):
    exts = {item["ext_id"] for item in report_data if item["event"] == "result"}

    # there could be retry events, so only count unique tests:
    tests_started = {item["test_id"] for item in report_data if item["event"] == "start"}
    tests_passed = {item["test_id"] for item in report_data if item["event"] == "stop" and item["passed"]}

    total_count = len(tests_started)
    fail_count = total_count - len(tests_passed)

    if fail_count:
        status = "failure"
        text = f"{fail_count} tests failed out of {total_count}"
    else:
        status = "success"
        text = f"All {total_count} tests passed"

    text += " (extensions tested: {}).".format(len(exts))

    if is_running_in_teamcity():
        teamcity_status(text=text, status=status)

    print(text)
    if fail_count:
        print(f"Failed tests: {tests_started - tests_passed}")


def _calculate_durations(report_data: list):
    """
    Calculate startup time of each extension and time taken by each individual test
    We count the time between the extension start_time to the start_time of the first test
    """
    ext_startup_time = {}
    ext_startup_time_found = {}
    ext_tests_time = {}
    for d in report_data:
        test_id = d["test_id"]
        test_type = d["test_type"]
        ext_test_id = d.get("ext_test_id", None)
        if d["event"] == "start":
            if test_type == "exttest":
                if not ext_startup_time_found.get(test_id):
                    start_time = d["start_time"]
                    ext_startup_time[test_id] = start_time
            else:
                if not ext_startup_time_found.get(ext_test_id):
                    t = ext_startup_time.get(ext_test_id, 0.0)
                    ext_startup_time[ext_test_id] = round(d["start_time"] - t, 2)
                    ext_startup_time_found[ext_test_id] = True
        elif d["event"] == "stop":
            if test_type == "unittest":
                t = ext_tests_time.get(ext_test_id, 0.0)
                t += d.get("duration", 0.0)
                ext_tests_time[ext_test_id] = t
        elif d["event"] == "result":
            test_result = d.get("result", None)
            if test_result:
                # it's possible an extension has no tests, so we set startup_duration = duration
                if ext_startup_time_found.get(test_id, False) is True:
                    t = ext_startup_time.get(test_id, 0.0)
                    test_result["startup_duration"] = t
                else:
                    test_result["startup_duration"] = test_result.get("duration", 0.0)
                # update duration of all tests
                test_result["tests_duration"] = ext_tests_time.get(test_id, 0.0)
                # ratios
                test_result["startup_ratio"] = 0.0
                test_result["tests_ratio"] = 0.0
                if test_result["tests_duration"] != 0.0:
                    test_result["startup_ratio"] = (test_result["startup_duration"] / test_result["duration"]) * 100.0
                    test_result["tests_ratio"] = (test_result["tests_duration"] / test_result["duration"]) * 100.0


def generate_report():
    """After running tests this function will generate html report / post to nvdf / publish artifacts"""
    # at this point all kit processes should be finished
    if is_running_on_ci():
        _kill_kit_processes()

    try:
        print("\nGenerating a Test Report...")
        _generate_report_internal()
    except Exception as e:
        import traceback

        print(f"Exception while running generate_report(): {e}, callstack: {traceback.format_exc()}")


def _kill_kit_processes():
    """Kill all Kit processes except self"""
    kit_process_name = carb.tokens.get_tokens_interface().resolve("${exe-filename}")
    for proc in psutil.process_iter():
        if proc.pid == os.getpid():
            continue
        try:
            if proc.name() == kit_process_name:
                carb.log_warn(
                    "Killing a Kit process that is still running:\n"
                    f"    PID: {proc.pid}\n"
                    f"    Command line: {proc.cmdline()}"
                )
                proc.terminate()
        except psutil.AccessDenied as e:
            carb.log_warn(f"Access denied: {e}")
        except psutil.ZombieProcess as e:
            carb.log_warn(f"Encountered a zombie process: {e}")
        except psutil.NoSuchProcess as e:
            carb.log_warn(f"Process no longer exists: {e}")
        except (psutil.Error, Exception) as e:
            carb.log_warn(f"An error occurred: {str(e)}")


def _generate_report_internal():
    # Get Test report and publish it
    report_data = []

    # combine report from various test runs (each process has own file, for parallel run)
    for report_file in glob.glob(get_global_test_output_path() + "/*/" + REPORT_FILENAME):
        report_data.extend(_load_report_data(report_file))
    # for ETM test, parent process will have the report.jsonl file in root test folder
    # (ex: get_global_test_output_path()). The result.jsonl file will contain extension test
    # which had error to run test (ex: sync_registry fail)
    for report_file in glob.glob(get_global_test_output_path() + "/" + REPORT_FILENAME):
        report_data.extend(_load_report_data(report_file))

    if not report_data:
        return

    # generate combined file
    combined_report_path = get_global_test_output_path() + "/report_combined.jsonl"
    with open(combined_report_path, "w") as f:
        f.write(json.dumps(report_data))
        teamcity_publish_artifact(combined_report_path)

    # TC Build status
    _post_build_status(report_data)

    # Dummy test report
    _report_unreliable_tests(report_data)

    # Prepare output path
    output_path = get_global_test_output_path()
    os.makedirs(output_path, exist_ok=True)

    # calculate durations (startup, total, etc)
    _calculate_durations(report_data)

    # post to elasticsearch
    post_to_nvdf(report_data)

    # write junit xml
    _write_junit_results(report_data)

    # get coverage results and generate html report
    merged_results, coverage_results = _load_coverage_results(report_data)
    html = _generate_html_report(report_data, merged_results)

    # post coverage results
    post_coverage_to_nvdf(_get_coverage_for_nvdf(merged_results, coverage_results))

    # write and publish html report
    _write_html_report(html, output_path)

    # publish all test output to TC in the end:
    teamcity_publish_artifact(f"{output_path}/**/*")


def _load_coverage_results(report_data, read_coverage=True) -> tuple[dict[str, ExtCoverage], dict]:
    # build a map of extension id to extension name
    ext_id_to_name = {}
    for item in report_data:
        if item["event"] == "result":
            ext_id_to_name[item["ext_id"]] = item["ext_name"]

    # Get data coverage per extension (configs are merged)
    coverage_results = defaultdict(ExtCoverage)
    if read_coverage:
        coverage_result = generate_coverage_report()
        if coverage_result and coverage_result.json_path:
            coverage_data = json.load(open(coverage_result.json_path))
            coverage_results = _build_ext_coverage(coverage_data, ext_id_to_name)

    # combine test results and coverage data, key is the test_id (separates extensions per config)
    merged_results = defaultdict(ExtCoverage)
    for item in report_data:
        if item["event"] == "result":
            test_id = item["test_id"]
            ext_id = item["ext_id"]
            ext_name = item["ext_name"]
            merged_results[test_id].ext_id = ext_id
            merged_results[test_id].ext_name = ext_name
            merged_results[test_id].test_result = item["result"]
            cov = coverage_results.get(ext_name)
            if cov:
                merged_results[test_id].covered_lines = cov.covered_lines
                merged_results[test_id].num_statements = cov.num_statements

    return merged_results, coverage_results


def _get_test_result(ext_name: str, merged_results: dict[str, ExtCoverage]) -> ExtCoverage | None:
    # grab the matching result
    if result := merged_results.get(ext_name):
        return result

    ret = None
    total_count = 0
    for r in merged_results.values():
        if r.ext_name == ext_name:
            # In rare cases the default name of a test config can be different,
            # search of the extension name and use the one the maximum test count.
            # Because we'll need the total count in the report, patch the test count as the total count.
            test_count = r.test_result.get("test_count", 0)
            if not ret or test_count > ret.test_result.get("test_count", 0):
                ret = r
            total_count += test_count
    if ret and ret.test_result:
        ret.test_result["test_count"] = total_count
    return ret


def _get_coverage_for_nvdf(merged_results: dict, coverage_results: dict) -> dict:
    json_data = {}
    for ext_name, _ in coverage_results.items():
        # grab the matching result
        result = _get_test_result(ext_name, merged_results)
        if not result or not result.test_result:
            continue
        test_data = {
            "ext_id": result.ext_id,
            "ext_name": ext_name,
        }
        test_data.update(result.test_result)
        json_data.update({ext_name: {"test": test_data}})

    return json_data


def _generate_html_report(report_data, merged_results):
    html = ""
    with open(os.path.join(HTML_PATH, "template.html"), "r") as f:
        html = f.read()

    class Color(Enum):
        RED = 0
        GREEN = 1
        YELLOW = 2

    def get_color(var, threshold: tuple, inverse=False, warning_only=False) -> Color | None:
        if var == "":
            return None
        if inverse is True:
            if float(var) >= threshold[0]:
                return Color.RED
            elif float(var) >= threshold[1]:
                return Color.YELLOW
            elif not warning_only:
                return Color.GREEN
        else:
            if float(var) <= threshold[0]:
                return Color.RED
            elif float(var) <= threshold[1]:
                return Color.YELLOW
            elif not warning_only:
                return Color.GREEN

    def get_td(var, color: Color | None = None) -> str:
        if color is Color.RED:
            return f"<td ov-red>{var}</td>\n"
        elif color is Color.GREEN:
            return f"<td ov-green>{var}</td>\n"
        elif color is Color.YELLOW:
            return f"<td ov-yellow>{var}</td>\n"
        else:
            return f"<td>{var}</td>\n"

    coverage_enabled = get_setting("/exts/omni.kit.test/pyCoverageEnabled", default=False)
    coverage_threshold = get_setting("/exts/omni.kit.test/pyCoverageThreshold", default=75)

    # disable coverage button when not needed
    if not coverage_enabled:
        html = html.replace(
            """<button class="tablinks" onclick="openTab(event, 'Coverage')">Coverage</button>""",
            """<button disabled class="tablinks" onclick="openTab(event, 'Coverage')">Coverage</button>""",
        )

    # Build test run data
    html = html.replace("%%test_data%%", _build_test_data_html(report_data))

    # Build extension table
    html_data = ""
    for test_id, info in sorted(merged_results.items()):
        r = info.test_result
        waiver = True if r.get("config", {}).get("waiver") else False
        passed = r.get("passed", False)
        test_count = r.get("test_count", 0)
        duration = round(r.get("duration", 0.0), 1)
        startup_duration = round(r.get("startup_duration", 0.0), 1)
        startup_ratio = round(r.get("startup_ratio", 0.0), 1)
        tests_duration = round(r.get("tests_duration", 0.0), 1)
        tests_ratio = round(r.get("tests_ratio", 0.0), 1)
        timeout = round(r.get("timeout", 0), 0)
        timeout_ratio = 0
        if timeout != 0:
            timeout_ratio = round((duration / timeout) * 100.0, 0)
        # an extension can override pyCoverageEnabled / pyCoverageThreshold
        ext_coverage_enabled = bool(r.get("config", {}).get("pyCoverageEnabled", coverage_enabled))
        ext_coverage_threshold = int(r.get("config", {}).get("pyCoverageThreshold", coverage_threshold))
        ext_coverage_threshold_low = int(ext_coverage_threshold * (2 / 3))
        # coverage data
        num_statements = info.sum_statements()
        num_covered_lines = info.sum_covered_lines()
        cov_percent = round(info.mean_cov(), 2)
        # add those calculated values to our results
        py_coverage = {
            "lines_total": num_statements,
            "lines_tested": num_covered_lines,
            "cov_percent": float(cov_percent),
            "cov_threshold": ext_coverage_threshold,
            "enabled": bool(coverage_enabled and ext_coverage_enabled),
        }
        info.test_result["pyCoverage"] = py_coverage

        html_data += "<tr>\n"
        html_data += get_td(test_id)
        html_data += get_td(r.get("package", {}).get("version", ""))
        html_data += get_td(waiver, Color.GREEN if waiver is True else None)
        html_data += get_td(passed, Color.GREEN if bool(passed) is True else Color.RED)
        html_data += get_td(test_count, Color.GREEN if waiver is True else get_color(test_count, (0, 5)))
        # color code tests duration: >=60 seconds is red and >=30 seconds is yellow
        html_data += get_td(str(duration), get_color(duration, (60, 30), inverse=True, warning_only=True))
        html_data += get_td(str(startup_duration))
        html_data += get_td(str(startup_ratio))
        html_data += get_td(str(tests_duration))
        html_data += get_td(str(tests_ratio))
        html_data += get_td(str(timeout))
        html_data += get_td(str(timeout_ratio), get_color(timeout_ratio, (90, 75), inverse=True, warning_only=True))
        html_data += get_td(bool(coverage_enabled and ext_coverage_enabled))
        if coverage_enabled and ext_coverage_enabled:
            html_data += get_td(ext_coverage_threshold)
            html_data += get_td(num_statements)
            html_data += get_td(num_covered_lines)
            html_data += get_td(
                cov_percent,
                Color.GREEN
                if waiver is True
                else get_color(cov_percent, (ext_coverage_threshold_low, ext_coverage_threshold)),
            )
            print(f"  > Coverage for {test_id} is {cov_percent}%")
        else:
            for _ in range(4):
                html_data += get_td("-")
        html_data += "</tr>\n"
    html = html.replace("%%table_data%%", html_data)
    return html


def _write_html_report(html, output_path):
    REPORT_NAME = "index.html"
    REPORT_FOLDER_NAME = "test_report"
    report_dir = os.path.join(output_path, REPORT_FOLDER_NAME)
    os.makedirs(report_dir, exist_ok=True)

    with open(os.path.join(report_dir, REPORT_NAME), "w") as f:
        f.write(html)
        print(f"  > Full report available here {f.name}")
        if not is_running_on_ci():
            import webbrowser

            webbrowser.open(f.name)

    # copy javascript/css files
    shutil.copyfile(os.path.join(HTML_PATH, "script.js"), os.path.join(report_dir, "script.js"))
    shutil.copyfile(os.path.join(HTML_PATH, "style.css"), os.path.join(report_dir, "style.css"))

    if is_running_in_teamcity():
        shutil.make_archive(os.path.join(output_path, REPORT_FOLDER_NAME), "zip", report_dir)
        teamcity_publish_artifact(os.path.join(output_path, "*.zip"))


@dataclass
class Stats:
    passed: int = 0
    failure: int = 0
    error: int = 0
    skipped: int = 0

    def get_total(self):
        return self.passed + self.failure + self.error + self.skipped


def _write_html_artifact(base_path: pathlib.Path, testcase: ET.Element):
    broken_html = ""
    project_dir_error_reported = False

    def cleanupPath(p: str | pathlib.Path) -> str:
        def fixSeparators(p: str | pathlib.Path) -> str:
            return str(p).replace("\\", "/")
        p = pathlib.Path(p)

        project_dir = os.getenv("CI_PROJECT_DIR")
        if not project_dir:
            # avoid spamming this message
            nonlocal project_dir_error_reported
            if not project_dir_error_reported:
                nonlocal broken_html
                broken_html += "CI_PROJECT_DIR is not defined - unable to write artifact paths. "
                carb.log_error("CI_PROJECT_DIR not defined - image comparison HTML will be broken")
            project_dir_error_reported = True
            return fixSeparators(p)

        try:
            # Replace windows path components with POSIX because the XML encoder doesn't like backslashes
            return fixSeparators(p.relative_to(project_dir))
        except Exception as e:
            carb.log_error(f"failed to clean up path '{p}': {e}")
            broken_html += f"Artifact path '{p}' is not relative to CI_PROJECT_DIR '{project_dir}' - image link will be broken. "
            return fixSeparators(p)

    if not os.getenv("GITLAB_CI"):
        carb.log_info("GITLAB_CI is not defined - skipping writing HTML image comparison")
        return

    json_path = base_path / "image_comparison.jsonl"
    if not os.path.exists(json_path):
        carb.log_info(f"{json_path} does not exist - skipping HTML image comparison generation")
        return

    html_path = base_path / "test_results.html"

    root = ET.Element("html")
    body = ET.SubElement(root, "body")

    with open(json_path, "r") as f:
        job_id = os.getenv("CI_JOB_ID")
        if job_id is None:
            broken_html += "CI_JOB_ID is not defined - unable to write artifact paths. "
            carb.log_error("CI_JOB_ID is not defined - image comparison HTML will be broken")
        artifactDir = f"https://gitlab-master.nvidia.com/omniverse/kit/-/jobs/{job_id}/artifacts/raw/"
        viewableArtifactDir = f"https://gitlab-master.nvidia.com/omniverse/kit/-/jobs/{job_id}/artifacts/browse/"


        # set of the tests that were run to ignore retries
        tests = set()
        for line in f.readlines():
            json_data = json.loads(line)

            if json_data["name"] in tests:
                continue
            else:
                tests.add(json_data["name"])

            div = ET.SubElement(body, "div")

            ET.SubElement(div, "center").text = json_data["name"]
            span = ET.SubElement(div, "span")

            def image_display(image_path, labelText):
                div = ET.SubElement(span, "div", style="width:33%;display:inline-block;vertical-align:top")
                ET.SubElement(div, "center").text = f"{labelText}:"
                center = ET.SubElement(div, "center")
                rel_path = cleanupPath(image_path)
                ET.SubElement(center, "img", src=f"{artifactDir}{rel_path}", style="max-width:100%")
                label = ET.SubElement(div, "center")
                label.text = f"{pathlib.Path(rel_path).name} in "
                ET.SubElement(label, "a", href=f"{viewableArtifactDir}{pathlib.Path(rel_path).parent}").text = "artifacts"

            image_display(json_data['reference'], "Reference")
            image_display(json_data['generated'], "Generated")
            image_display(json_data['diff'], "Difference")

        if broken_html != "":
            ET.SubElement(div, "center", style="font-size:40;font-weight:bold;color:red").text = f"HTML writer reported an error: {broken_html}"

    with open(html_path, "w") as f:
        f.write(ET.tostring(root, encoding="unicode", xml_declaration=False))

    system_out = ET.SubElement(testcase, "system-out")
    system_out.text = f"[[ATTACHMENT|{cleanupPath(str(html_path))}]]"


def _write_junit_results(report_data: list):
    """Write a JUnit XML from our report data"""
    testsuites = _report_data_to_junit_report(report_data)
    # write our file
    ET.indent(testsuites)
    with open(get_results_filepath(), "w", encoding="utf-8") as f:
        f.write(ET.tostring(testsuites, encoding="unicode", xml_declaration=True))


def _report_data_to_junit_report(report_data: list) -> ET.Element:
    # Reserve the order.
    testsuites = OrderedDict()
    testcases = []
    start_time = datetime.now()
    prev_ext_test_id = ""
    prev_test_id = ""
    last_failure = {"message": "", "fail_type": ""}
    stats = Stats()

    for data in report_data:
        test_id = data["test_id"]
        test_type = data["test_type"]
        ext_test_id = data.get("ext_test_id", test_id)
        def _append_incomplete_testsuite():
            # previous test did not get finished, it may killed by repo_test due to timed out.
            nonlocal last_failure
            nonlocal stats
            nonlocal testcases
            nonlocal testsuites
            # add incomplete testcase entry with outer testsuite
            testcase = ET.Element("testcase", name=prev_test_id, classname=prev_ext_test_id, time=f"0.000")
            stats.error += 1
            node = ET.SubElement(testcase, "error")
            node.text = "Killed due to test process timeout. The remaining test cases of the same extension are skipped"
            testcases.append(testcase)
            testsuite = ET.Element(
                "testsuite",
                name=prev_ext_test_id,
                failures=str(stats.failure),
                errors=str(stats.error),
                skipped=str(stats.skipped),
                tests=str(stats.get_total()),
                time=f"0.000",
                timestamp=start_time.isoformat(),
                hostname=platform.node(),
            )
            testsuite.extend(testcases)
            # always overwrite the old one if it exists since there may be auto reruns.
            testsuites[prev_ext_test_id] = testsuite
            # reset things between test suites
            testcases = []
            last_failure = {"message": "", "fail_type": ""}
            stats = Stats()

        if data["event"] == "start":
            if test_type == "exttest":
                if prev_ext_test_id != "":
                    _append_incomplete_testsuite()
                start_time = datetime.fromtimestamp(data["start_time"])
                prev_ext_test_id = test_id
            elif test_type == "unittest":
                prev_test_id = test_id
        elif data["event"] == "fail":
            last_failure = data
        elif data["event"] == "stop":
            # create a testcase for each stop event (for both exttest and unittest)
            testcase = ET.Element("testcase", name=test_id, classname=ext_test_id, time=f"{data['duration']:.3f}")
            if data.get("skipped"):
                stats.skipped += 1
                node = ET.SubElement(testcase, "skipped")
                node.text = data.get("skip_reason", "")
            elif data.get("passed"):
                stats.passed += 1
            else:
                if last_failure["fail_type"] == "Failure":
                    stats.failure += 1
                    node = ET.SubElement(testcase, "failure")
                else:
                    stats.error += 1
                    node = ET.SubElement(testcase, "error")
                node.text = last_failure["message"]

                _write_html_artifact(pathlib.Path(omni.kit.test.get_global_test_output_path()) / test_id, testcase)

            testcases.append(testcase)

            # extension test stop - gather all testcases and add test suite
            if test_type == "exttest":
                testsuite = ET.Element(
                    "testsuite",
                    name=test_id,
                    failures=str(stats.failure),
                    errors=str(stats.error),
                    skipped=str(stats.skipped),
                    tests=str(stats.get_total()),
                    time=f"{data['duration']:.3f}",
                    timestamp=start_time.isoformat(),
                    hostname=platform.node(),
                )
                testsuite.extend(testcases)
                # always overwrite the old one if it exists since there may be auto reruns.
                testsuites[test_id] = testsuite
                # reset things between test suites
                testcases = []
                last_failure = {"message": "", "fail_type": ""}
                stats = Stats()
                prev_ext_test_id = ""
            elif test_type == "unittest":
                prev_test_id = ""

    if prev_ext_test_id != "":
        _append_incomplete_testsuite()

    ret = ET.Element("testsuites")
    for t in testsuites.values():
        ret.append(t)
    return ret
