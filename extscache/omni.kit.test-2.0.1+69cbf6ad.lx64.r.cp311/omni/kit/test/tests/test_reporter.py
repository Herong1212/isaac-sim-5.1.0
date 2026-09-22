from pathlib import Path

import omni.kit.test

from ..reporter import _calculate_durations, _load_report_data, _load_coverage_results, _generate_html_report, _report_data_to_junit_report, _get_test_result, ExtCoverage

CURRENT_PATH = Path(__file__).parent
DATA_TESTS_PATH = CURRENT_PATH.parent.parent.parent.parent.joinpath("data/tests")


class TestReporter(omni.kit.test.AsyncTestCase):
    async def test_success_report_data(self):
        """
        omni_kit_test_success_report.jsonl contains the report.jsonl of a successful run testing omni.kit.test
        """
        path = DATA_TESTS_PATH.joinpath("omni_kit_test_success_report.jsonl")
        report_data = _load_report_data(path)
        self.assertEqual(len(report_data), 11)
        result = report_data[10]
        test_result = result.get("result", None)
        self.assertNotEqual(test_result, None)
        # make sure durations are good
        _calculate_durations(report_data)
        startup_duration = test_result["startup_duration"]
        tests_duration = test_result["tests_duration"]
        self.assertAlmostEqual(startup_duration, 1.040, places=3)
        self.assertAlmostEqual(tests_duration, 0.007, places=3)
        # make sure our ratio are good
        duration = test_result["duration"]
        startup_ratio = test_result["startup_ratio"]
        tests_ratio = test_result["tests_ratio"]
        self.assertAlmostEqual(startup_ratio, 100 * (startup_duration / duration), places=3)
        self.assertAlmostEqual(tests_ratio, 100 * (tests_duration / duration), places=3)

    async def test_fail_report_data(self):
        """
        omni_kit_test_fail_report.jsonl contains the report.jsonl of a failed run of testing omni.kit.test
        with a few failed tests and also a test that crash
        """
        path = DATA_TESTS_PATH.joinpath("omni_kit_test_fail_report.jsonl")
        report_data = _load_report_data(path)
        self.assertEqual(len(report_data), 18)
        result = report_data[17]
        test_result = result.get("result", None)
        self.assertNotEqual(test_result, None)
        # make sure durations are good
        _calculate_durations(report_data)
        startup_duration = test_result["startup_duration"]
        tests_duration = test_result["tests_duration"]
        self.assertAlmostEqual(startup_duration, 0.950, places=3)
        self.assertAlmostEqual(tests_duration, 0.006, places=3)
        # make sure our ratio are good
        duration = test_result["duration"]
        startup_ratio = test_result["startup_ratio"]
        tests_ratio = test_result["tests_ratio"]
        self.assertAlmostEqual(startup_ratio, 100 * (startup_duration / duration), places=3)
        self.assertAlmostEqual(tests_ratio, 100 * (tests_duration / duration), places=3)

    async def test_html_report(self):
        path = DATA_TESTS_PATH.joinpath("omni_kit_test_success_report.jsonl")
        report_data = _load_report_data(path)
        _calculate_durations(report_data)
        merged_results, _ = _load_coverage_results(report_data, read_coverage=False)
        html = _generate_html_report(report_data, merged_results)
        # total duration is 1.32 seconds, in the hmtl report we keep 1 decimal so it will be shown as 1.3
        self.assertTrue(html.find("<td>1.3</td>") != -1)
        # startup duration will be 78.8 %
        self.assertTrue(html.find("<td>78.8</td>") != -1)

    async def test_duplicated_report_data(self):
        report_data = [
            {"event": "start", "test_type": "exttest", "test_id": "omni.kit.window.file", "ext_id": "omni.kit.window.file-1.3.53", "ext_name": "omni.kit.window.file", "start_time": 1717072891.152321},
            {"event": "fail", "test_type": "exttest", "test_id": "omni.kit.window.file", "fail_type": "Error", "message": "\n[fail] Extension Test failed. Details:\n    Cmdline: ./_build/windows-x86_64/release/kit.exe ./_build/windows-x86_64/release/apps/omni.app.test_ext_kit_sdk.kit --enable omni.kit.window.file-1.3.53 --/log/flushStandardStreamOutput=1 --/app/name=exttest_omni_kit_window_file --/log/file='./_testoutput/exttest_omni_kit_window_file/exttest_omni_kit_window_file_2024-05-30T05-41-31_0.log' --/exts/omni.kit.test/testOutputPath='./_testoutput/exttest_omni_kit_window_file' --/exts/omni.kit.test/extTestId='omni.kit.window.file' --/crashreporter/dumpDir='./_testoutput/exttest_omni_kit_window_file' --/crashreporter/preserveDump=1 --/crashreporter/gatherUserStory=0 --/rtx-transient/dlssg/enabled=false --ext-folder ./_build/windows-x86_64/release/extsPhysics --ext-folder ./_build/windows-x86_64/release/exts --ext-folder ./_build/windows-x86_64/release/extscache --ext-folder ./_build/windows-x86_64/release/apps --enable omni.kit.test --/exts/omni.kit.test/runTestsAndQuit=true --/exts/omni.kit.test/includeTests/0='omni.kit.window.file.*' --/app/enableStdoutOutput=0 --portable --portable-root ./_build/windows-x86_64/release/ --/exts/omni.kit.test/parallelRun=true --/telemetry/mode=test --/crashreporter/data/testName=ext-test-omni.kit.window.file --/exts/omni.kit.test/pyCoverageEnabled=False --enable omni.hydra.pxr --enable omni.timeline --enable omni.kit.mainwindow --enable omni.kit.menu.file --enable omni.kit.material.library --enable omni.kit.ui_test --enable omni.kit.test_suite.helpers --enable omni.kit.renderer.capture --enable omni.kit.viewport.window --enable omni.kit.widget.versioning --/exts/omni.kit.test/testExtSamplingSeed=31007 --/renderer/warnOnRtxInit=true --/renderer/enabled=pxr --/renderer/active=pxr --/app/window/dpiScaleOverride=1.0 --/app/window/scaleToMonitor=false --/app/file/ignoreUnsavedOnExit=true --/persistent/app/omniverse/filepicker/options_menu/show_details=false --/exts/omni.kit.test/testExtRandomOrder=true --/exts/omni.kit.test/testExtRetryStrategy='iterations' --/exts/omni.kit.test/testExtMaxTestRunCount=1 --no-window\n    Cmdline to run a single unittest: ./_build/windows-x86_64/release/tests-omni.kit.window.file.bat -f *test_file_saveas\n    Cmdline to run the extension tests: ./_build/windows-x86_64/release/tests-omni.kit.window.file.bat\n    Return code: 13 (0x0000000d)\n    Failure reason(s): \n        Matched 1 fail pattern '*[error]*' in stdout: \n            '2024-05-30 12:41:46 [14,684ms] [Error] [omni.usd] Stage busy or another saving task is in progress!!'\n        1 test(s) failed.\n    Details:\n        Failing tests: \n            omni.kit.window.file.tests.test_file_save.TestFileSave.test_file_saveas"},
            {"event": "stop", "test_type": "exttest", "test_id": "omni.kit.window.file", "passed": False, "skipped": False, "stop_time": 1717072926.6537817, "duration": 35.502},
            {"event": "result", "test_type": "exttest", "test_id": "omni.kit.window.file", "ext_id": "omni.kit.window.file-1.3.53", "ext_name": "omni.kit.window.file", "test_bucket": "unit", "unreliable": False, "parallel_run": True, "change_analyzer": {"skip": False, "startup_sequence_hash": "5cde483b3e0bd587", "tested_ext_hash": "f19a7d083c27e91c", "kernel_version": "170.0+170.5611.576b794e.gl"}, "result": {"config": {"args": ["--/renderer/enabled=pxr", "--/renderer/active=pxr", "--/app/window/dpiScaleOverride=1.0", "--/app/window/scaleToMonitor=false", "--/app/file/ignoreUnsavedOnExit=true", "--/persistent/app/omniverse/filepicker/options_menu/show_details=false", "--/exts/omni.kit.test/testExtRandomOrder=true", "--/exts/omni.kit.test/testExtRetryStrategy='iterations'", "--/exts/omni.kit.test/testExtMaxTestRunCount=1", "--no-window"], "dependencies": ["omni.hydra.pxr", "omni.timeline", "omni.kit.mainwindow", "omni.kit.menu.file", "omni.kit.material.library", "omni.kit.ui_test", "omni.kit.test_suite.helpers", "omni.kit.renderer.capture", "omni.kit.viewport.window", "omni.kit.widget.versioning"], "stdoutFailPatterns": {"exclude": ["*Stage opening or closing already in progress*", "*Task exception was never retrieved*", "*wait_for_stage_event timeout waiting for StageEventType.SAVED*"]}}, "retries": 0, "timeout": 300, "state": {"enabled": False}, "package": {"version": "1.3.53"}, "passed": False, "duration": 35.5, "kill_process_duration": 0.0, "test_count": 31, "unreliable": 0, "unreliable_fail": 0, "fail": 1}},

            {"event": "start", "test_type": "exttest", "test_id": "omni.kit.window.file", "ext_id": "omni.kit.window.file-1.3.53", "ext_name": "omni.kit.window.file", "start_time": 1717073141.4042816},
            {"event": "stop", "test_type": "exttest", "test_id": "omni.kit.window.file", "passed": True, "skipped": False, "stop_time": 1717073171.2023504, "duration": 29.799},
            {"event": "result", "test_type": "exttest", "test_id": "omni.kit.window.file", "ext_id": "omni.kit.window.file-1.3.53", "ext_name": "omni.kit.window.file", "test_bucket": "unit", "unreliable": False, "parallel_run": False, "change_analyzer": {"skip": False, "startup_sequence_hash": "5cde483b3e0bd587", "tested_ext_hash": "f19a7d083c27e91c", "kernel_version": "170.0+170.5611.576b794e.gl"}, "result": {"config": {"args": ["--/renderer/enabled=pxr", "--/renderer/active=pxr", "--/app/window/dpiScaleOverride=1.0", "--/app/window/scaleToMonitor=false", "--/app/file/ignoreUnsavedOnExit=true", "--/persistent/app/omniverse/filepicker/options_menu/show_details=false", "--/exts/omni.kit.test/testExtRandomOrder=true", "--/exts/omni.kit.test/testExtRetryStrategy='iterations'", "--/exts/omni.kit.test/testExtMaxTestRunCount=1", "--no-window"], "dependencies": ["omni.hydra.pxr", "omni.timeline", "omni.kit.mainwindow", "omni.kit.menu.file", "omni.kit.material.library", "omni.kit.ui_test", "omni.kit.test_suite.helpers", "omni.kit.renderer.capture", "omni.kit.viewport.window", "omni.kit.widget.versioning"], "stdoutFailPatterns": {"exclude": ["*Stage opening or closing already in progress*", "*Task exception was never retrieved*", "*wait_for_stage_event timeout waiting for StageEventType.SAVED*"]}}, "retries": 0, "timeout": 300, "state": {"enabled": False}, "package": {"version": "1.3.53"}, "passed": True, "duration": 29.8, "kill_process_duration": 0.0, "test_count": 31, "unreliable": 0, "unreliable_fail": 0, "fail": 0}},

            {"event": "start", "test_type": "exttest", "test_id": "omni.kit.documentation.ui.style", "ext_id": "omni.kit.documentation.ui.style-1.0.6", "ext_name": "omni.kit.documentation.ui.style", "start_time": 1717073107.8081782},
            {"event": "stop", "test_type": "exttest", "test_id": "omni.kit.documentation.ui.style", "passed": True, "skipped": False, "stop_time": 1717073110.3185227, "duration": 2.51},
            {"event": "result", "test_type": "exttest", "test_id": "omni.kit.documentation.ui.style", "ext_id": "omni.kit.documentation.ui.style-1.0.6", "ext_name": "omni.kit.documentation.ui.style", "test_bucket": "unit", "unreliable": False, "parallel_run": False, "change_analyzer": {"skip": False, "startup_sequence_hash": "5e750430d2c0f9b2", "tested_ext_hash": "ecba3efcd0c82adb", "kernel_version": "170.0+170.5611.576b794e.gl"}, "result": {"config": {}, "retries": 0, "timeout": 300, "state": {"enabled": False}, "package": {"version": "1.0.6"}, "passed": True, "duration": 2.51, "kill_process_duration": 0.0, "test_count": 0, "unreliable": 0, "unreliable_fail": 0, "fail": 0}},

            {"event": "start", "test_type": "exttest", "test_id": "omni.kit.documentation.ui.style", "ext_id": "omni.kit.documentation.ui.style-1.0.6", "ext_name": "omni.kit.documentation.ui.style", "start_time": 1717072680.3050964},
            {"event": "fail", "test_type": "exttest", "test_id": "omni.kit.documentation.ui.style", "fail_type": "Error", "message": "\n[fail] Extension Test failed. Details:\n    Cmdline: ./_build/windows-x86_64/release/kit.exe ./_build/windows-x86_64/release/apps/omni.app.test_ext_kit_sdk.kit --enable omni.kit.documentation.ui.style-1.0.6 --/log/flushStandardStreamOutput=1 --/app/name=exttest_omni_kit_documentation_ui_style --/log/file='./_testoutput/exttest_omni_kit_documentation_ui_style/exttest_omni_kit_documentation_ui_style_2024-05-30T05-38-00_0.log' --/exts/omni.kit.test/testOutputPath='./_testoutput/exttest_omni_kit_documentation_ui_style' --/exts/omni.kit.test/extTestId='omni.kit.documentation.ui.style' --/crashreporter/dumpDir='./_testoutput/exttest_omni_kit_documentation_ui_style' --/crashreporter/preserveDump=1 --/crashreporter/gatherUserStory=0 --/rtx-transient/dlssg/enabled=false --ext-folder ./_build/windows-x86_64/release/extsPhysics --ext-folder ./_build/windows-x86_64/release/exts --ext-folder ./_build/windows-x86_64/release/extscache --ext-folder ./_build/windows-x86_64/release/apps --enable omni.kit.test --/exts/omni.kit.test/runTestsAndQuit=true --/exts/omni.kit.test/includeTests/0='omni.kit.documentation.ui.style.*' --/app/enableStdoutOutput=0 --portable --portable-root ./_build/windows-x86_64/release/ --/exts/omni.kit.test/parallelRun=true --/telemetry/mode=test --/crashreporter/data/testName=ext-test-omni.kit.documentation.ui.style --/exts/omni.kit.test/pyCoverageEnabled=False --/exts/omni.kit.test/testExtSamplingSeed=31007 --/renderer/warnOnRtxInit=true\n    Cmdline to run the extension tests: ./_build/windows-x86_64/release/tests-omni.kit.documentation.ui.style.bat\n    Return code: 15 (0x0000000f)\n    Failure reason(s): \n        Process timed out (timeout: 300 seconds), terminating. Check artifacts for .dmp files.\n    Details:"},
            {"event": "stop", "test_type": "exttest", "test_id": "omni.kit.documentation.ui.style", "passed": False, "skipped": False, "stop_time": 1717073036.8369477, "duration": 356.532},
            {"event": "result", "test_type": "exttest", "test_id": "omni.kit.documentation.ui.style", "ext_id": "omni.kit.documentation.ui.style-1.0.6", "ext_name": "omni.kit.documentation.ui.style", "test_bucket": "unit", "unreliable": False, "parallel_run": True, "change_analyzer": {"skip": False, "startup_sequence_hash": "5e750430d2c0f9b2", "tested_ext_hash": "ecba3efcd0c82adb", "kernel_version": "170.0+170.5611.576b794e.gl"}, "result": {"config": {}, "retries": 0, "timeout": 300, "state": {"enabled": False}, "package": {"version": "1.0.6"}, "passed": False, "duration": 299.97, "kill_process_duration": 56.554648876190186, "test_count": 0, "unreliable": 0, "unreliable_fail": 0, "fail": 1}},
        ]

        actual = _report_data_to_junit_report(report_data)

        it = iter(actual)
        first = next(it, None)
        self.assertTrue(first)
        self.assertEqual(first.attrib.get("name"), "omni.kit.window.file")
        self.assertEqual(first.attrib.get("failures"), "0")
        self.assertEqual(first.attrib.get("errors"), "0")
        self.assertEqual(first.attrib.get("skipped"), "0")
        self.assertEqual(first.attrib.get("tests"), "1")

        second = next(it, None)
        self.assertTrue(second)
        self.assertEqual(second.attrib.get("name"), "omni.kit.documentation.ui.style")
        self.assertEqual(second.attrib.get("failures"), "0")
        self.assertEqual(second.attrib.get("errors"), "1")
        self.assertEqual(second.attrib.get("skipped"), "0")
        self.assertEqual(second.attrib.get("tests"), "1")

        self.assertFalse(next(it, None))

    async def test_missing_result_event(self):
        report_data = [
            {"event": "start", "test_type": "exttest", "test_id": "omni.materialx.libs-render_rtx", "ext_id": "omni.materialx.libs-1.0.4", "ext_name": "omni.materialx.libs", "start_time": 1720054022.8089926},
            {"event": "start", "test_type": "unittest", "test_id": "omni.materialx.libs.tests.rtx.MtlxRenderTestRtx.test_amd_composition", "ext_test_id": "omni.materialx.libs-render_rtx", "unreliable": False, "parallel_run": False, "start_time": 1720054024.9268878},
            {"event": "stop", "test_type": "unittest", "test_id": "omni.materialx.libs.tests.rtx.MtlxRenderTestRtx.test_amd_composition", "ext_test_id": "omni.materialx.libs-render_rtx", "passed": True, "skipped": False, "skip_reason": "", "stop_time": 1720054111.739904, "duration": 86.813},
            {"event": "start", "test_type": "unittest", "test_id": "omni.materialx.libs.tests.rtx.MtlxRenderTestRtx.test_open_chess_set", "ext_test_id": "omni.materialx.libs-render_rtx", "unreliable": False, "parallel_run": False, "start_time": 1720054111.7409022},
        ]
        actual = _report_data_to_junit_report(report_data)

        first = actual[0]
        self.assertTrue(first)
        self.assertEqual(first.attrib.get("name"), "omni.materialx.libs-render_rtx")
        self.assertEqual(first.attrib.get("failures"), "0")
        self.assertEqual(first.attrib.get("errors"), "1")
        self.assertEqual(first.attrib.get("skipped"), "0")
        self.assertEqual(first.attrib.get("tests"), "2")
        self.assertEqual(first[0].tag, "testcase")
        self.assertEqual(first[0].get("name"), "omni.materialx.libs.tests.rtx.MtlxRenderTestRtx.test_amd_composition")
        self.assertEqual(len(first[0]), 0)
        self.assertEqual(first[1].tag, "testcase")
        self.assertEqual(first[1].get("name"), "omni.materialx.libs.tests.rtx.MtlxRenderTestRtx.test_open_chess_set")
        self.assertEqual(first[1][0].tag, "error")
        self.assertEqual(first[1][0].text, "Killed due to test process timeout. The remaining test cases of the same extension are skipped")

        report_data2 = [
            {"event": "start", "test_type": "exttest", "test_id": "omni.materialx.libs-render_rtx", "ext_id": "omni.materialx.libs-1.0.4", "ext_name": "omni.materialx.libs", "start_time": 1720054022.8089926},
        ]
        actual2 = _report_data_to_junit_report(report_data2)
        second = actual2[0]
        self.assertTrue(second)
        self.assertEqual(second.attrib.get("name"), "omni.materialx.libs-render_rtx")
        self.assertEqual(second.attrib.get("failures"), "0")
        self.assertEqual(second.attrib.get("errors"), "1")
        self.assertEqual(second.attrib.get("skipped"), "0")
        self.assertEqual(second.attrib.get("tests"), "1")
        self.assertEqual(second[0].tag, "testcase")
        self.assertEqual(second[0].get("name"), "")
        self.assertEqual(second[0][0].tag, "error")
        self.assertEqual(second[0][0].text, "Killed due to test process timeout. The remaining test cases of the same extension are skipped")

    async def test_get_test_result(self):

        def create_ext_coverage(ext_name, ext_id, test_result):
            ext_coverage = ExtCoverage()
            ext_coverage.ext_id = ext_id
            ext_coverage.ext_name = ext_name
            ext_coverage.test_result = test_result
            return ext_coverage

        # Copied from real logs.
        test_result_main = {
            'config': {
                'name': 'main',
                'timeout': 600,
                'args': [
                    '--/renderer/enabled=rtx', '--/renderer/active=rtx', '--/renderer/multiGpu/enabled=false',
                ],
                'dependencies': [
                    'omni.kit.mainwindow', 'omni.kit.window.status_bar', 'omni.hydra.rtx', 'omni.kit.material.library',
                ],
                'stdoutFailPatterns': {'exclude': {}},
                'pythonTests': {'unreliable': {}}
            },
            'retries': 0,
            'timeout': 600,
            'state': {'enabled': False},
            'package': {'version': '1.0.13'},
            'passed': True,
            'duration': 113.51,
            'kill_process_duration': 0.0,
            'test_count': 7,
            'unreliable': 0,
            'unreliable_fail': 0,
            'fail': 0,
            'startup_duration': 2.37,
            'tests_duration': 110.22099999999999,
            'startup_ratio': 2.087921769007136,
            'tests_ratio': 97.10245793322173
        }

        # Copied from real logs.
        test_result_startup = {
            'config': {
                'name': 'startup',
                '_startup_only_test': True,
                'pythonTests': {'include': ['']}
            },
            'retries': 0,
            'timeout': 300,
            'state': {'enabled': False},
            'package': {'version': '1.0.13'},
            'passed': True,
            'duration': 3.3,
            'kill_process_duration': 0.0,
            'test_count': 0,
            'unreliable': 0,
            'unreliable_fail': 0,
            'fail': 0,
            'startup_duration': 3.3,
            'tests_duration': 0.0,
            'startup_ratio': 0.0,
            'tests_ratio': 0.0
        }

        # Dummy test result.
        test_result_another = {
            'test_count': 3,
        }

        # Create example ExtCoverage objects
        ext_name = "omni.kit.example"
        ext_id = f"{ext_name}-1.0.0"
        ext_coverage_main = create_ext_coverage(ext_name, ext_id, test_result_main)
        ext_coverage_startup = create_ext_coverage(ext_name, ext_id, test_result_startup)
        ext_coverage_another = create_ext_coverage(ext_name, ext_id, test_result_another)

        # Create merged_results dictionary
        merged_results = {
            f"{ext_name}-main": ext_coverage_main,
            f"{ext_name}-startup": ext_coverage_startup,
            f"{ext_name}-another": ext_coverage_another,
        }

        # Test _get_test_result function
        result = _get_test_result(ext_name, merged_results)
        self.assertIsNotNone(result)
        self.assertEqual(result.ext_id, "omni.kit.example-1.0.0")
        self.assertEqual(result.ext_name, "omni.kit.example")
        self.assertEqual(result.test_result, test_result_main)
        self.assertEqual(result.test_result.get("test_count", 0), 7 + 3)

        # Test case where ext_name is not found
        result_not_found = _get_test_result("nonexistent", merged_results)
        self.assertIsNone(result_not_found)