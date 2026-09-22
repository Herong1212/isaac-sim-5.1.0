## Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##
import omni.usd
from omni.kit import ui_test
from omni.kit.test_suite.helpers import arrange_windows

from .test_base import MaterialPropertiesTestBase
from .utils import time_logger


@time_logger
class PropertyMaterialGotoMDL(MaterialPropertiesTestBase):
    # Before running each test
    async def setUp(self):
        await super().setUp()
        await arrange_windows("Stage", 256)

    async def test_l1_mesh_goto_material_button(self):
        scene_file_path = self._get_scene_path("material_binding_inherited.usda")
        await self._load_scene(scene_file_path)

        await ui_test.find("Stage").focus()

        context = omni.usd.get_context()

        # goto single prims
        for prim_list, expected in [
            ("/World/Xform/Cone", ["/World/Looks/OmniSurface"]),
            ("/World/Xform/Cone_01", ["/World/Looks/OmniPBR"]),
            ("/World/Xform_Inherited/Cone_02", ["/World/Looks/OmniSurface_Blood"]),
            ("/World/Xform_Inherited/Cone_03", ["/World/Looks/OmniSurface_Blood"]),
            ("/World/Xform_Unbound/Sphere", ["/World/Xform_Unbound/Sphere"]),
        ]:

            await self._select_prims([prim_list])

            thumb_widget = ui_test.find("Property//Frame/**/Button[*].identifier=='preview_drop_target'")
            await thumb_widget.click()
            await ui_test.human_delay(50)

            # verify
            self.assertEqual(context.get_selection().get_selected_prim_paths(), expected)

        # goto multiple prims
        for index, expected in enumerate(
            [
                ["/World/Looks/OmniPBR", "/World/Looks/OmniSurface"],
                ["/World/Looks/OmniSurface"],
                ["/World/Looks/OmniPBR"],
            ]
        ):
            await self._select_prims(["/World/Xform/Cone", "/World/Xform/Cone_01"])

            thumb_widget = ui_test.find_all("Property//Frame/**/Button[*].identifier=='preview_drop_target'")
            await thumb_widget[index].click()
            await ui_test.human_delay(50)

            # verify
            self.assertEqual(context.get_selection().get_selected_prim_paths(), expected)

        # goto multiple selected inherited prims
        await self._select_prims(["/World/Xform_Inherited/Cone_02", "/World/Xform_Inherited/Cone_03"])

        thumb_widget = ui_test.find("Property//Frame/**/Button[*].identifier=='preview_drop_target'")
        await thumb_widget.click()
        await ui_test.human_delay(50)

        # verify
        self.assertEqual(context.get_selection().get_selected_prim_paths(), ["/World/Looks/OmniSurface_Blood"])
