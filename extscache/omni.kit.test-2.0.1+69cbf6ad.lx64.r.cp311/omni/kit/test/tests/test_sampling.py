import urllib.error
from contextlib import suppress

import omni.kit.test

from ..nvdf import get_app_info
from ..sampling import Sampling


class TestSampling(omni.kit.test.AsyncTestCase):
    def setUp(self):
        self.sampling = Sampling(get_app_info())
        self.unittests = ["test_one", "test_two", "test_three", "test_four"]

    async def test_sampling_factor_zero(self):
        self.sampling.run_query("omni.foo", self.unittests, running_on_ci=False)
        samples = self.sampling.get_tests_to_skip(0.0)
        # will return the same list but with a different order
        self.assertEqual(len(samples), len(self.unittests))

    async def test_sampling_factor_one(self):
        self.sampling.run_query("omni.foo", self.unittests, running_on_ci=False)
        samples = self.sampling.get_tests_to_skip(1.0)
        self.assertListEqual(samples, [])

    async def test_sampling_factor_point_five(self):
        self.sampling.run_query("omni.foo", self.unittests, running_on_ci=False)
        samples = self.sampling.get_tests_to_skip(0.5)
        self.assertEqual(len(samples), len(self.unittests) / 2)

    async def test_with_fake_nvdf_query(self):
        with suppress(urllib.error.URLError):
            self.sampling.run_query("omni.foo", self.unittests, running_on_ci=True)
            samples = self.sampling.get_tests_to_skip(0.5)
            if self.sampling.query_result is True:
                self.assertEqual(len(samples), len(self.unittests) / 2)
            else:
                self.assertListEqual(samples, [])
