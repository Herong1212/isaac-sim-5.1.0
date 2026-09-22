## Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##
from ..stage_icons_extension import StageIconsExtension
import omni.kit.test


class TestStageIcons(omni.kit.test.AsyncTestCase):
    async def test_registry(self):
        icons = StageIconsExtension.get_registered_icons()
        self.assertIsInstance(icons, list)
        self.assertIn("Camera", icons)
        self.assertIn("GeomSubset", icons)
        self.assertIn("Instance", icons)
        self.assertIn("Light", icons)
        self.assertIn("Material", icons)
        self.assertIn("Prim", icons)
        self.assertIn("Reference", icons)
        self.assertIn("Scope", icons)
        self.assertIn("Shader", icons)
        self.assertIn("SkelJoint", icons)
        self.assertIn("Xform", icons)
