# Copyright (c) 2024, NVIDIA CORPORATION. All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
import carb
import omni.kit.test
import omni.kit.app
import pathlib

from pathlib import Path

# Retrieve the folder of the 'carb.ocio.python' extension:
EXTENSION_FOLDER_PATH = pathlib.Path(carb.tokens.get_tokens_interface().resolve("${carb.ocio.python}"))

# The directory for texture data.
# Note this data points originally to the "rendering" folder.
TEX_DIR = EXTENSION_FOLDER_PATH.joinpath("data/textures")

# importing the omniverse ocio python bindings
import omni.ocio as ocio

# Given an OpenColorIo Context, this will return the (displays, views, looks) from the configuration
# The views is a list of lists, where the n-th list corresponds to the views of the n-th display.
def get_displays_views_and_looks(ocio_ctx):
    displays = []
    views = []
    looks = []

    display_count = ocio.get_display_count(ocio_ctx)
    for i in range(display_count):
        display_name = str(ocio.get_display_name(ocio_ctx, i))
        displays.append(display_name)
        disp_views = []

        view_count = ocio.get_view_count(ocio_ctx, i)
        for k in range(view_count):
            view_name = str(ocio.get_view_name(ocio_ctx, i, k))
            disp_views.append(view_name)

        views.append(disp_views)

    look_count = ocio.get_look_count(ocio_ctx)
    for j in range(look_count):
        look_name = str(ocio.get_look_name(ocio_ctx, j))
        looks.append(look_name)

    return displays, views, looks

# This test covers the python bindings for omni.ocio that are exposed
# via the .cpp -> python bindings.
#
class TestCarbOcio(omni.kit.test.AsyncTestCase):


    # tests OpenColorIo built-in configurations and the omni.ocio python bindings
    async def test_builtin_configs(self):
        '''
        Test python bindings for omni.ocio and the built-in configurations of ocio.
        '''

        # Studio Config Test
        cfg_file = "ocio://studio-config-latest"
        ocio_ctx = ocio.get_context(cfg_file)
        self.assertTrue(True if ocio_ctx is not None else False)

        displays, views, looks = get_displays_views_and_looks(ocio_ctx)
        expected_displays = ['sRGB - Display', 'Display P3 - Display', 'Rec.1886 Rec.709 - Display', 'Rec.1886 Rec.2020 - Display', 'Rec.2100-HLG - Display', 'Rec.2100-PQ - Display', 'ST2084-P3-D65 - Display', 'P3-D60 - Display', 'P3-D65 - Display', 'P3-DCI - Display']
        expected_views = [['ACES 1.0 - SDR Video', 'ACES 1.0 - SDR Video (D60 sim on D65)', 'Un-tone-mapped', 'Raw'], ['ACES 1.0 - SDR Video', 'ACES 1.0 - SDR Video (D60 sim on D65)', 'Un-tone-mapped', 'Raw'], ['ACES 1.0 - SDR Video', 'ACES 1.0 - SDR Video (D60 sim on D65)', 'Un-tone-mapped', 'Raw'], ['ACES 1.0 - SDR Video', 'ACES 1.1 - SDR Video (P3 lim)', 'ACES 1.1 - SDR Video (Rec.709 lim)', 'Un-tone-mapped', 'Raw'], ['ACES 1.1 - HDR Video (1000 nits & Rec.2020 lim)', 'Un-tone-mapped', 'Raw'], ['ACES 1.1 - HDR Video (1000 nits & Rec.2020 lim)', 'ACES 1.1 - HDR Video (2000 nits & Rec.2020 lim)', 'ACES 1.1 - HDR Video (4000 nits & Rec.2020 lim)', 'Un-tone-mapped', 'Raw'], ['ACES 1.1 - HDR Video (1000 nits & P3 lim)', 'ACES 1.1 - HDR Video (2000 nits & P3 lim)', 'ACES 1.1 - HDR Video (4000 nits & P3 lim)', 'ACES 1.1 - HDR Cinema (108 nits & P3 lim)', 'Un-tone-mapped', 'Raw'], ['ACES 1.0 - SDR Cinema', 'Un-tone-mapped', 'Raw'], ['ACES 1.0 - SDR Cinema', 'ACES 1.1 - SDR Cinema (Rec.709 lim)', 'ACES 1.1 - SDR Cinema (D60 sim on D65)', 'Un-tone-mapped', 'Raw'], ['ACES 1.0 - SDR Cinema (D60 sim on DCI)', 'ACES 1.1 - SDR Cinema (D65 sim on DCI)', 'Un-tone-mapped', 'Raw']]
        expected_looks = ['ACES 1.3 Reference Gamut Compression']

        self.assertEqual(displays, expected_displays)
        self.assertEqual(views, expected_views)
        self.assertEqual(looks, expected_looks)
        ocio.release_context(ocio_ctx)
        ocio_ctx = None

        # CG Config Test
        cfg_file = "ocio://cg-config-latest"
        ocio_ctx = ocio.get_context(cfg_file)
        self.assertTrue(True if ocio_ctx is not None else False)

        displays, views, looks = get_displays_views_and_looks(ocio_ctx)
        expected_displays = ['sRGB - Display', 'Display P3 - Display', 'Rec.1886 Rec.709 - Display', 'Rec.2100-PQ - Display', 'ST2084-P3-D65 - Display', 'P3-D65 - Display']
        expected_views = [['ACES 1.0 - SDR Video', 'Un-tone-mapped', 'Raw'], ['ACES 1.0 - SDR Video', 'Un-tone-mapped', 'Raw'], ['ACES 1.0 - SDR Video', 'Un-tone-mapped', 'Raw'], ['ACES 1.1 - HDR Video (1000 nits & Rec.2020 lim)', 'Un-tone-mapped', 'Raw'], ['ACES 1.1 - HDR Video (1000 nits & P3 lim)', 'Un-tone-mapped', 'Raw'], ['ACES 1.0 - SDR Cinema', 'Un-tone-mapped', 'Raw']]
        expected_looks = ['ACES 1.3 Reference Gamut Compression']

        self.assertEqual(displays, expected_displays)
        self.assertEqual(views, expected_views)
        self.assertEqual(looks, expected_looks)
        ocio.release_context(ocio_ctx)
        ocio_ctx = None
