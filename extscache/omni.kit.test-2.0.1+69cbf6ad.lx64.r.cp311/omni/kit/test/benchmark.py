import json
import os
import sys
from time import perf_counter_ns
from typing import List, Optional, Tuple, Union

import omni.kit.app

from .async_unittest import AsyncTestCase, OmniTestResult
from .reporter import TestReporter
from .test_reporters import TestRunStatus
from .utils import get_ext_test_id, get_global_test_output_path, get_setting


class BenchmarkReporter(TestReporter):
    """
    Benchmark reporter class to generate the JSON report for reggie.
    * Collects default metrics such as `duration`, `passed` and `skipped`.
    * Collects custom metrics from `BenchmarkTestCase`
    * Collects fingerprints that are passed by CLI arguments.
    * Detects platorm and config and sets it as fingerprint.
    """

    def __init__(self, stream=sys.stdout):
        super().__init__(stream=stream)
        self._bm_timers = {}

    def _get_bm_duration_ns(self, test_id: str) -> int:
        end_time = perf_counter_ns()
        try:
           start_time = self._bm_timers.pop(test_id)
           duration_ns = end_time-start_time
        except KeyError:
            duration_ns = 0
        return duration_ns

    @staticmethod
    def _collect_fingerprints():
        """
        Internal method to collect benchmark finger prints for reggie.
        Detects platform and config at runtime.
        Collects custom fingerprints from CLI and merges them with the detected ones.
        """
        platform_info = omni.kit.app.get_app().get_platform_info()
        from_settings = get_setting("/exts/omni.kit.test/benchmarkFingerPrint", default={})
        from_info = {"config": platform_info.get("config", "N/A"), "platform": platform_info.get("platform", "N/A")}
        # let user settings overwrite detected fingerprints
        from_info.update(from_settings)
        return from_info

    @staticmethod
    def _get_benchmark_and_suite(test_id: str, ext_test_id: str) -> Tuple[str, str]:
        """
        Generates slightly shorter benchmark and benchmark_suite names for reggie
        from the strings found in test_id and ext_test_id.
        They are for example used in reggie's HTML reports (drop-down list)

        Example:
            input:
            test_id = "example.python_ext.tests.test_benchmarks.TestBenchmarks.benchmark_sleepy_with_custom_metrics"
            ext_test_id = "example.python_ex"

            output:
            benchmark = "TestBenchmarks.benchmark_sleepy_with_custom_metrics"
            benchmark_suite = "tests.test_benchmarks"
        """
        removed_ext = test_id.replace(ext_test_id + ".", "")
        split_names = removed_ext.split(".")
        benchmark = ".".join(split_names[-2:])
        benchmark_suite = removed_ext.replace("." + benchmark, "")

        return benchmark, benchmark_suite

    @staticmethod
    def _add_samples_from_benchmark(samples: dict, test):
        """
        Collect custom metric samples from `BenchmarkTestCase`.
        """
        # skip if used test class is not derived from BenchmarkTestCase
        if isinstance(test, BenchmarkTestCase):
            samples.update(test._get_metric_samples_dict())

    def _write_bm_report(self, test_id, test, passed, skipped):
        """
        Generate the JSON report for reggie.
        """
        duration_ns = self._get_bm_duration_ns(test_id)
        ext_test_id = get_ext_test_id()
        bm_fingerprints = BenchmarkReporter._collect_fingerprints()
        benchmark, benchmark_suite = BenchmarkReporter._get_benchmark_and_suite(test_id, ext_test_id)
        samples = {
            "duration": {"value": round(duration_ns / 1000), "unit": "us"},
            "passed": {"value": passed},
            "skipped": {"value": skipped},
        }
        BenchmarkReporter._add_samples_from_benchmark(samples, test)
        report = {
            "project": f"Extension Benchmark for {ext_test_id}",
            "benchmark_suite": benchmark_suite,
            "benchmark": benchmark,
            "fingerprint": bm_fingerprints,
            "samples": samples,
        }

        out_path = os.path.join(get_global_test_output_path(), f"benchmark.{test_id}.json")
        with open(out_path, "w") as f:
            json.dump(report, f)

    def benchmark_begin(self, test_id):
        self._bm_timers[test_id] = perf_counter_ns()

    def benchmark_end(self, test_id, test, passed=False, skipped=False, skip_reason=""):
        self._write_bm_report(test_id=test_id, test=test, passed=passed, skipped=skipped)
        if isinstance(test, BenchmarkTestCase):
            # clean-up metrics after each test run
            test._clear_metric_samples()


class BenchmarkResult(OmniTestResult):
    """
    Base class for benchmark results.
    """

    def __init__(self, stream, descriptions, verbosity):
        super().__init__(stream=stream, descriptions=descriptions, verbosity=verbosity)
        self.reporter = BenchmarkReporter(stream)

    def testMethodBegin(self, test):
        self.reporter.benchmark_begin(test.id())

    def testMethodEnd(self, test):
        test_id = test.id()
        # In Python 3.11+, test outcomes are handled differently
        # We need to check the test result differently
        if test._outcome and hasattr(test._outcome, 'skipped'):  # Python 3.10 and earlier
            skipped = test._outcome is None or bool(test._outcome.skipped)
            passed = test._outcome.success if test._outcome and not skipped else True
        else:  # Python 3.11+
            result = self._current_result()
            skipped = bool(result.skipped)
            passed = not (result.failures or result.errors) or skipped

        skip_reason = self.skipped[-1][1] if skipped and self.skipped else ""
        self.reporter.benchmark_end(test_id=test_id, test=test, passed=passed, skipped=skipped, skip_reason=skip_reason)

    def _current_result(self):
        """Helper method to get current test result in Python 3.11+"""
        return self


class BenchmarkTestCase(AsyncTestCase):
    """
    Base class for benchmark tests.
    Benchmarks have to derive from this class to be able to set samples for custom metrics.
    """

    def __init__(self, tests=(), methodName="runTest"):
        super().__init__(tests)
        self.metric_samples = {}

    def _clear_metric_samples(self):
        """
        Cleanup metrics dict.
        Has to run before or after each benchmark run to ensure no leakage of metrics to another benchmark.
        """
        self.metric_samples.clear()

    def _get_metric_samples_dict(self) -> dict:
        """
        Expose the custom metric samples. Used to generate the final reports.
        """
        return self.metric_samples

    def set_metric_sample(self, name: str, value: Union[int, float, bool], unit: Optional[str] = None):
        """
        Set a sample for a custom metric. Providing the unit is optional.
        """
        self.metric_samples[name] = {"value": value, "unit": unit} if unit else {"value": value}

    def set_metric_sample_array(
        self, name: str, values: Union[List[int], List[float]], unit: Optional[str] = None
    ):
        """
        Set a sample array for a custom metric. Providing the unit is optional.
        """
        self.metric_samples[name] = {"values": values, "unit": unit} if unit else {"values": values}
