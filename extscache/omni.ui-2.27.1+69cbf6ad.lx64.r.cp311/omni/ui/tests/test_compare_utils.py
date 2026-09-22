import os
from pathlib import Path

import omni.kit.test

from .compare_utils import GOLDEN_DIR, OUTPUTS_DIR, CompareMetric, compare
from .test_base import OmniUiTest


class TestCompareUtils(omni.kit.test.AsyncTestCase):
    async def setUp(self):
        self.test_name = "omni.ui.tests.test_compare_utils.TestCompareUtils"

    def cleanupTestFile(self, target: str):
        try:
            os.remove(target)
        except FileNotFoundError:
            pass

    async def test_compare_rgb(self):
        image1 = GOLDEN_DIR.joinpath(f"{self.test_name}.test_compare_rgb_golden.png")
        image2 = GOLDEN_DIR.joinpath(f"{self.test_name}.test_compare_rgb_modified.png")
        image_diffmap = OUTPUTS_DIR.joinpath(f"{Path(image1).stem}.diffmap.png")
        # mean error
        diff = compare(image1, image2, image_diffmap, threshold=None, cmp_metric=CompareMetric.MEAN_ERROR)
        self.assertAlmostEqual(diff, 40.4879, places=3)
        # mean error squared
        diff = compare(image1, image2, image_diffmap, threshold=None, cmp_metric=CompareMetric.MEAN_ERROR_SQUARED)
        self.assertAlmostEqual(diff, 0.031937, places=5)
        # pixel count
        diff = compare(image1, image2, image_diffmap, threshold=None, cmp_metric=CompareMetric.PIXEL_COUNT)
        self.assertEqual(diff, 262144)

    async def test_compare_rgba(self):
        image1 = GOLDEN_DIR.joinpath(f"{self.test_name}.test_compare_rgba_golden.png")
        image2 = GOLDEN_DIR.joinpath(f"{self.test_name}.test_compare_rgba_modified.png")
        image_diffmap = OUTPUTS_DIR.joinpath(f"{Path(image1).stem}.diffmap.png")
        # mean error
        diff = compare(image1, image2, image_diffmap, threshold=None, cmp_metric=CompareMetric.MEAN_ERROR)
        self.assertAlmostEqual(diff, 0.4000, places=3)
        # mean error squared
        diff = compare(image1, image2, image_diffmap, threshold=None, cmp_metric=CompareMetric.MEAN_ERROR_SQUARED)
        self.assertAlmostEqual(diff, 0.001466, places=5)
        # pixel count
        diff = compare(image1, image2, image_diffmap, threshold=None, cmp_metric=CompareMetric.PIXEL_COUNT)
        self.assertEqual(diff, 1961)

    async def test_compare_rgb_itself(self):
        image1 = GOLDEN_DIR.joinpath(f"{self.test_name}.test_compare_rgb_golden.png")
        image2 = image1
        image_diffmap = OUTPUTS_DIR.joinpath(f"{Path(image1).stem}.diffmap.png")
        # mean error
        diff = compare(image1, image2, image_diffmap, threshold=None, cmp_metric=CompareMetric.MEAN_ERROR)
        self.assertEqual(diff, 0)
        # mean error squared
        diff = compare(image1, image2, image_diffmap, threshold=None, cmp_metric=CompareMetric.MEAN_ERROR_SQUARED)
        self.assertEqual(diff, 0)
        # pixel count
        diff = compare(image1, image2, image_diffmap, threshold=None, cmp_metric=CompareMetric.PIXEL_COUNT)
        self.assertEqual(diff, 0)

    async def test_compare_grayscale(self):
        image1 = GOLDEN_DIR.joinpath(f"{self.test_name}.test_compare_grayscale_golden.png")
        image2 = GOLDEN_DIR.joinpath(f"{self.test_name}.test_compare_grayscale_modified.png")
        image_diffmap = OUTPUTS_DIR.joinpath(f"{Path(image1).stem}.diffmap.png")
        # mean error
        diff = compare(image1, image2, image_diffmap, threshold=None, cmp_metric=CompareMetric.MEAN_ERROR)
        self.assertAlmostEqual(diff, 39.3010, places=3)
        # mean error squared
        diff = compare(image1, image2, image_diffmap, threshold=None, cmp_metric=CompareMetric.MEAN_ERROR_SQUARED)
        self.assertAlmostEqual(diff, 0.030923, places=5)
        # pixel count
        diff = compare(image1, image2, image_diffmap, threshold=None, cmp_metric=CompareMetric.PIXEL_COUNT)
        self.assertEqual(diff, 260827)

    async def test_compare_rgb_black_to_white(self):
        image1 = GOLDEN_DIR.joinpath(f"{self.test_name}.test_compare_rgb_black.png")
        image2 = GOLDEN_DIR.joinpath(f"{self.test_name}.test_compare_rgb_white.png")
        image_diffmap = OUTPUTS_DIR.joinpath(f"{Path(image1).stem}.diffmap.png")
        # mean error
        diff = compare(image1, image2, image_diffmap, threshold=None, cmp_metric=CompareMetric.MEAN_ERROR)
        self.assertEqual(diff, 255.0)
        # mean error squared
        diff = compare(image1, image2, image_diffmap, threshold=None, cmp_metric=CompareMetric.MEAN_ERROR_SQUARED)
        self.assertEqual(diff, 1.0)
        # pixel count
        diff = compare(image1, image2, image_diffmap, threshold=None, cmp_metric=CompareMetric.PIXEL_COUNT)
        self.assertEqual(diff, 4096)

    async def test_compare_rgba_black_to_white(self):
        image1 = GOLDEN_DIR.joinpath(f"{self.test_name}.test_compare_rgba_black.png")
        image2 = GOLDEN_DIR.joinpath(f"{self.test_name}.test_compare_rgba_white.png")
        image_diffmap = OUTPUTS_DIR.joinpath(f"{Path(image1).stem}.diffmap.png")
        # mean error
        diff = compare(image1, image2, image_diffmap, threshold=None, cmp_metric=CompareMetric.MEAN_ERROR)
        self.assertEqual(diff, 191.25)
        # mean error squared
        diff = compare(image1, image2, image_diffmap, threshold=None, cmp_metric=CompareMetric.MEAN_ERROR_SQUARED)
        self.assertEqual(diff, 0.75)
        # pixel count
        diff = compare(image1, image2, image_diffmap, threshold=None, cmp_metric=CompareMetric.PIXEL_COUNT)
        self.assertEqual(diff, 4096)

    async def test_compare_rgb_gray(self):
        image1 = GOLDEN_DIR.joinpath(f"{self.test_name}.test_compare_rgb_gray.png")
        image2 = GOLDEN_DIR.joinpath(f"{self.test_name}.test_compare_rgb_gray_modified.png")
        image_diffmap = OUTPUTS_DIR.joinpath(f"{Path(image1).stem}.diffmap.png")
        # mean error
        diff = compare(image1, image2, image_diffmap, threshold=None, cmp_metric=CompareMetric.MEAN_ERROR)
        self.assertEqual(diff, 48)
        # mean error squared
        diff = compare(image1, image2, image_diffmap, threshold=None, cmp_metric=CompareMetric.MEAN_ERROR_SQUARED)
        self.assertAlmostEqual(diff, 0.094486, places=5)
        # pixel count
        diff = compare(image1, image2, image_diffmap, threshold=None, cmp_metric=CompareMetric.PIXEL_COUNT)
        self.assertEqual(diff, 2048)

    async def test_compare_rgb_gray_pixel(self):
        image1 = GOLDEN_DIR.joinpath(f"{self.test_name}.test_compare_rgb_gray_pixel.png")
        image2 = GOLDEN_DIR.joinpath(f"{self.test_name}.test_compare_rgb_gray_pixel_modified.png")
        image_diffmap = OUTPUTS_DIR.joinpath(f"{Path(image1).stem}.diffmap.png")
        # mean error
        diff = compare(image1, image2, image_diffmap, threshold=None, cmp_metric=CompareMetric.MEAN_ERROR)
        self.assertAlmostEqual(diff, 0.0468, places=3)
        # mean error squared
        diff = compare(image1, image2, image_diffmap, threshold=None, cmp_metric=CompareMetric.MEAN_ERROR_SQUARED)
        self.assertAlmostEqual(diff, 0.000092, places=5)
        # pixel count
        diff = compare(image1, image2, image_diffmap, threshold=None, cmp_metric=CompareMetric.PIXEL_COUNT)
        self.assertEqual(diff, 2)

    async def test_compare_threshold(self):
        image1 = GOLDEN_DIR.joinpath(f"{self.test_name}.test_compare_grayscale_golden.png")
        image2 = GOLDEN_DIR.joinpath(f"{self.test_name}.test_compare_grayscale_modified.png")
        image_diffmap = OUTPUTS_DIR.joinpath(f"{Path(image1).stem}.diffmap.png")
        expected_diff = 39.30104446411133

        # diff is below threshold (39.301 < 40) -> image_diffmap saved to disk
        diff = compare(image1, image2, image_diffmap, threshold=40)
        self.assertAlmostEqual(diff, expected_diff, places=3)
        self.assertTrue(os.path.exists(image_diffmap))
        self.cleanupTestFile(image_diffmap)

        # diff is below threshold but threshold is above by 2 order of magnitude (39.301 < 4000/10) -> no image_diffmap
        diff = compare(image1, image2, image_diffmap, threshold=4000)
        self.assertAlmostEqual(diff, expected_diff, places=3)
        self.assertFalse(os.path.exists(image_diffmap))
        # no file cleanup to do here

        # diff is above threshold (39.301 > 39) -> image_diffmap saved to disk
        diff = compare(image1, image2, image_diffmap, threshold=39)
        self.assertAlmostEqual(diff, expected_diff, places=3)
        self.assertTrue(os.path.exists(image_diffmap))
        self.cleanupTestFile(image_diffmap)

        # diff is above threshold but threshold is below by 2 order of magnitude (39.301 > 3900/10) -> image_diffmap saved to disk
        diff = compare(image1, image2, image_diffmap, threshold=3900)
        self.assertAlmostEqual(diff, expected_diff, places=3)
        self.assertTrue(os.path.exists(image_diffmap))
        self.cleanupTestFile(image_diffmap)

    async def test_default_threshold(self):
        """This test will give an example of an image comparison just above the default threshold"""
        image1 = GOLDEN_DIR.joinpath(f"{self.test_name}.test_compare_threshold.png")
        image2 = GOLDEN_DIR.joinpath(f"{self.test_name}.test_compare_threshold_modified.png")
        image_diffmap = OUTPUTS_DIR.joinpath(f"{Path(image1).stem}.diffmap.png")
        # mean error default threshold is 0.01
        diff = compare(image1, image2, image_diffmap, threshold=None, cmp_metric=CompareMetric.MEAN_ERROR)
        self.assertAlmostEqual(diff, OmniUiTest.MEAN_ERROR_THRESHOLD, places=2)
        # mean error squared default threshold is 1e-5 (0.00001)
        diff = compare(image1, image2, image_diffmap, threshold=None, cmp_metric=CompareMetric.MEAN_ERROR_SQUARED)
        self.assertAlmostEqual(diff, OmniUiTest.MEAN_ERROR_SQUARED_THRESHOLD, places=5)
