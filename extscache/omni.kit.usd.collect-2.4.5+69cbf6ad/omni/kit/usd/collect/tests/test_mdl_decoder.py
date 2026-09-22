# Copyright (c) 2018-2024, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = ["TestMdlUrlDecoder"]

import omni.kit.test
from ..mdl_parser import (
    MdlUrlDecoder
)


class TestMdlUrlDecoder(omni.kit.test.AsyncTestCase):
    async def setUp(self):
        pass

    async def tearDown(self):
        pass

    async def test_mdl_url_decoder(self):
        # OMPE-41571: should remove ZD6_3 in path
        self.assertEqual(
            MdlUrlDecoder.decode("..::ZD6_305_5FSTELLANTIS_5FXRITE_5Fmaterials::A030_ELA"),
            "../05_STELLANTIS_XRITE_materials/A030_ELA"
        )
