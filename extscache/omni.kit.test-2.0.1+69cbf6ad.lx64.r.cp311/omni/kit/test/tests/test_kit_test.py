import unittest
import json

import carb
import omni.kit.app
import omni.kit.test

from omni.kit.test.reporter import get_report_filepath

# uncomment for dev work
# import unittest


# All tests in format: test id, passed, skipped
ALL_TESTS = [
    ("omni.kit.test.tests.test_kit_test.TestKitTest.test_are_async", True, False),
    ("omni.kit.test.tests.test_kit_test.TestKitTest.test_can_be_skipped_1", True, True),
    ("omni.kit.test.tests.test_kit_test.TestKitTest.test_can_be_skipped_2", True, True),
    ("omni.kit.test.tests.test_kit_test.TestKitTest.test_can_be_sync", True, False),
    ("omni.kit.test.tests.test_kit_test.TestKitTest.test_get_test", True, False),
    ("omni.kit.test.tests.test_kit_test.TestKitTest.test_test_settings", True, False),
    ("omni.kit.test.tests.test_kit_test.TestKitTest.test_with_metadata", True, False),
    ("omni.kit.test.tests.test_kit_test.TestKitTest.test_with_subtest", True, False),
    ("omni.kit.test.tests.test_kit_test.TestKitTest.test_zzz_report_is_correct", True, False),
    ("omni.kit.test.tests.test_lookups.TestLookups.test_lookups", True, False),
    ("omni.kit.test.tests.test_lookups.TestLookups.test_find_latest_valid_ext_id", True, False),
    ("omni.kit.test.tests.test_nvdf.TestNVDF.test_convert_advanced_types", True, False),
    ("omni.kit.test.tests.test_nvdf.TestNVDF.test_convert_basic_types", True, False),
    ("omni.kit.test.tests.test_nvdf.TestNVDF.test_convert_reserved_types", True, False),
    ("omni.kit.test.tests.test_nvdf.TestNVDF.test_convert_nested", True, False),
    ("omni.kit.test.tests.test_reporter.TestReporter.test_get_test_result", True, False),
    ("omni.kit.test.tests.test_reporter.TestReporter.test_fail_report_data", True, False),
    ("omni.kit.test.tests.test_reporter.TestReporter.test_html_report", True, False),
    ("omni.kit.test.tests.test_reporter.TestReporter.test_success_report_data", True, False),
    ("omni.kit.test.tests.test_reporter.TestReporter.test_duplicated_report_data", True, False),
    ("omni.kit.test.tests.test_reporter.TestReporter.test_missing_result_event", True, False),
    ("omni.kit.test.tests.test_sampling.TestSampling.test_sampling_factor_one", True, False),
    ("omni.kit.test.tests.test_sampling.TestSampling.test_sampling_factor_point_five", True, False),
    ("omni.kit.test.tests.test_sampling.TestSampling.test_sampling_factor_zero", True, False),
    ("omni.kit.test.tests.test_sampling.TestSampling.test_with_fake_nvdf_query", True, False),
    ("omni.kit.test.tests.test_utilities.TestUtilities.test_assert_true_with_retry", True, False),
    ("omni.kit.test.tests.test_utilities.TestUtilities.test_assert_equal_with_retry", True, False),
]

class TestKitTest(omni.kit.test.AsyncTestCase):
    async def test_test_settings(self):
        # See [[test]] section
        carb.log_error("This message will not fail the test because it is excluded in [[test]]")
        self.assertEqual(carb.settings.get_settings().get("/extra_arg_passed/param"), 123)

    async def test_test_other_settings(self):
        self.assertEqual(carb.settings.get_settings().get("/extra_arg_passed/param"), 456)

    async def test_that_is_excluded(self):
        self.fail("Should not be called")

    async def test_get_test(self):
        if any("test_that_is_unreliable" in t.id() for t in omni.kit.test.get_tests()):
            self.skipTest("Skipping if test_that_is_unreliable ran")

        all_test_ids = {t[0] for t in ALL_TESTS}
        self.assertSetEqual({t.id() for t in omni.kit.test.get_tests()}, all_test_ids)
        self.assertListEqual(
            [t.id() for t in omni.kit.test.get_tests(tests_filter="test_settings")],
            [
                "omni.kit.test.tests.test_kit_test.TestKitTest.test_test_settings",
            ],
        )

    async def test_are_async(self):
        app = omni.kit.app.get_app()
        update = app.get_update_number()
        await app.next_update_async()
        self.assertEqual(app.get_update_number(), update + 1)

    def test_can_be_sync(self):
        self.assertTrue(True)

    @unittest.skip("Skip test with @unittest.skip")
    async def test_can_be_skipped_1(self):
        self.assertTrue(False)

    async def test_can_be_skipped_2(self):
        self.skipTest("Skip test with self.skipTest")
        self.assertTrue(False)

    # subTest will get fixes in python 3.11, see https://bugs.python.org/issue25894
    async def test_with_subtest(self):
        with self.subTest(msg="subtest example"):
            self.assertTrue(True)

    async def test_with_metadata(self):
        """This is an example to use metadata"""
        print("##omni.kit.test[set, my_key, This line will be printed if the test fails]")
        self.assertTrue(True)

    async def test_that_is_unreliable(self):
        """This test will not run unless we run unreliable tests"""
        self.assertTrue(True)  # we don't make it fail when running unreliable tests

    async def test_zzz_report_is_correct(self):
        """Read the report.jsonl and check that data for this class is correct. This test should be the last one to run,
        so it is named with 'zzz'."""

        # Load report
        report_path = get_report_filepath()
        print(f"path: {report_path}")
        with open(report_path, "r") as f:
            data = [json.loads(line) for line in f]

        # Extract data
        skipped_tests = set()
        passed_tests = set()
        failed_tests = set()

        for d in data:
            if d["event"] == "stop" and d["test_type"] == "unittest":
                if d["skipped"]:
                    skipped_tests.add(d["test_id"])
                if d["passed"]:
                    passed_tests.add(d["test_id"])
                else:
                    failed_tests.add(d["test_id"])


        # Get tests from only this file
        all_tests_filtered = {t for t in ALL_TESTS if t[0].startswith("omni.kit.test.tests.test_kit_test")}
        # Remove ourself
        all_tests_filtered = {t for t in all_tests_filtered if t[0] != "omni.kit.test.tests.test_kit_test.TestKitTest.test_zzz_report_is_correct"}

        # Check against source of truth:
        self.assertEqual(skipped_tests, {t[0] for t in all_tests_filtered if t[2]})
        self.assertEqual(passed_tests, {t[0] for t in all_tests_filtered if t[1]})
        self.assertEqual(failed_tests, {t[0] for t in all_tests_filtered if not t[1]})


    # Development tests - uncomment when doing dev work to test all ways a test can succeed / fail
    # async def test_success(self):
    #     self.assertTrue(True)

    # async def test_fail_1(self):
    #     self.assertTrue(False)

    # async def test_fail_2(self):
    #     raise Exception("fuff")
    #     self.assertTrue(False)

    # will crash with stack overflow
    # async def test_fail_3(self):
    #     __import__("sys").setrecursionlimit(100000000)

    #     def crash():
    #         crash()
    #     crash()
