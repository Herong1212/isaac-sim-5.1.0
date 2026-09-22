import omni.kit.undo
from omni.kit import ui_test
from omni.kit.test_suite.helpers import arrange_windows
from pxr import UsdShade

from .test_base import MaterialPropertiesTestBase
from .utils import time_logger


@time_logger
class TestMaterialThumbContextMenu(MaterialPropertiesTestBase):
    async def setUp(self):
        await super().setUp()
        await arrange_windows("Stage", 200)

        scene_file_path = self._get_scene_path("material_context.usda")
        await self._load_scene(scene_file_path)

    async def _validate_no_binding(self, num_prims: int) -> None:
        for i in range(num_prims):
            prim_path = f"/World/Sphere_{i:02d}"
            prim = self._get_prim_at_path(prim_path)
            self._get_bound_material(prim, False)

    async def _validate_binding(self, num_prims: int, material_path="/World/Looks/PreviewSurface") -> None:
        for i in range(num_prims):
            prim_path = f"/World/Sphere_{i:02d}"
            prim = self._get_prim_at_path(prim_path)
            bound_material, _ = self._get_bound_material(prim)
            self.assertEqual(bound_material.GetPrim().GetPrimPath().pathString, material_path)

    async def test_material_thumb_context_menu_copy_1_to_1(self):
        # test copy single material from Cone_01 to Sphere_00
        await self._validate_no_binding(1)

        await self._select_prims(["/World/Cone_01"])

        # right click and "copy"
        await ui_test.find("Property//Frame/**/Button[*].identifier=='preview_drop_target'").click(right_click=True)
        await ui_test.select_context_menu("Copy", offset=ui_test.Vec2(10, 10))

        await self._select_prims(["/World/Sphere_00"])

        # right click and "paste"
        await ui_test.find("Property//Frame/**/Button[*].identifier=='preview_drop_target'").click(right_click=True)
        await ui_test.select_context_menu("Paste", offset=ui_test.Vec2(10, 10))

        # verify binding
        await self._validate_binding(1)

    async def test_material_thumb_context_menu_copy_2_to_1(self):
        # test copy single material from Cone_01 to Sphere_00
        await self._validate_no_binding(1)

        # select source prim
        await self._select_prims(["/World/Cone_01", "/World/Cone_02"])

        # right click and "copy"
        await ui_test.find("Property//Frame/**/Button[*].identifier=='preview_drop_target'").click(right_click=True)
        await ui_test.select_context_menu("Copy", offset=ui_test.Vec2(10, 10))

        # select target prim
        await self._select_prims(["/World/Sphere_00"])

        # right click and "paste"
        await ui_test.find("Property//Frame/**/Button[*].identifier=='preview_drop_target'").click(right_click=True)
        await ui_test.select_context_menu("Paste (2 Materials)", offset=ui_test.Vec2(10, 10))

        # verify binding
        await self._validate_binding(1)

    async def test_material_thumb_context_menu_copy_4_to_2(self):
        # test copy single material from Cone_01 to Sphere_00
        await self._validate_no_binding(2)

        # select source prim
        await self._select_prims(["/World/Cone_01", "/World/Cone_02"])

        # right click and "copy"
        await ui_test.find("Property//Frame/**/Button[*].identifier=='preview_drop_target'").click(right_click=True)
        await ui_test.select_context_menu("Copy", offset=ui_test.Vec2(10, 10))

        # select target prim
        await self._select_prims(["/World/Sphere_00", "/World/Sphere_01"])

        # right click and "paste"
        await ui_test.find("Property//Frame/**/Button[*].identifier=='preview_drop_target'").click(right_click=True)
        await ui_test.select_context_menu("Paste (2 Materials)", offset=ui_test.Vec2(10, 10))

        # verify binding
        await self._validate_binding(2)

    async def test_material_thumb_context_menu_copy_4211_to_2(self):
        def get_bindings(prim_paths, expected_res: bool = True):
            bindings = []
            for prim_path in prim_paths:
                prim = self._get_prim_at_path(prim_path)
                api = UsdShade.MaterialBindingAPI(prim)
                mat, _ = api.ComputeBoundMaterial()
                bindings.append(mat.GetPath().pathString if mat else "None")

            # fixme - due to get_binding_from_prims using sets which are not ordered
            return sorted(bindings)

        for index, data in enumerate(
            [
                (
                    "Paste (4 Materials)",
                    [
                        "/World/Looks/OmniGlass_Opacity",
                        "/World/Looks/OmniPBR_ClearCoat",
                        "/World/Looks/PreviewSurface",
                        "/World/Looks/PreviewSurface",
                    ],
                ),
                ("Paste (2 Materials)", ["/World/Looks/PreviewSurface", "/World/Looks/PreviewSurface", "None", "None"]),
                ("Paste", ["/World/Looks/OmniPBR_ClearCoat", "None", "None", "None"]),
                ("Paste", ["/World/Looks/OmniGlass_Opacity", "None", "None", "None"]),
            ]
        ):

            # select source prims
            await self._select_prims(["/World/Cone_01", "/World/Cone_02", "/World/Cube_01", "/World/Cube_02"])

            # verify copy material
            sphere_prim_paths = [f"/World/Sphere_{i:02d}" for i in range(0, 4)]
            materials = get_bindings(sphere_prim_paths)
            self.assertEqual(materials, ["None", "None", "None", "None"])

            # right click and "copy"
            widgets = ui_test.find_all("Property//Frame/**/Button[*].identifier=='preview_drop_target'")
            await widgets[index].click(right_click=True)
            await ui_test.select_context_menu("Copy", offset=ui_test.Vec2(10, 10))

            # select target prim
            await self._select_prims(sphere_prim_paths)

            # right click and "paste"
            await ui_test.find("Property//Frame/**/Button[*].identifier=='preview_drop_target'").click(right_click=True)
            await ui_test.select_context_menu(data[0], offset=ui_test.Vec2(10, 10))

            materials = get_bindings(sphere_prim_paths)
            self.assertEqual(materials, data[1])

            omni.kit.undo.undo()

    async def test_material_thumb_context_menu_copy_1_to_many(self):
        # test copy single material from Cone_01 to Sphere_*
        await self._validate_no_binding(64)

        # select source prim
        await self._select_prims(["/World/Cone_01"])

        # right click and "copy"
        await ui_test.find("Property//Frame/**/Button[*].identifier=='preview_drop_target'").click(right_click=True)
        await ui_test.select_context_menu("Copy", offset=ui_test.Vec2(10, 10))

        # select target prims
        to_select = [f"/World/Sphere_{i:02d}" for i in range(0, 64)]
        await self._select_prims(to_select)

        # right click in frame to "paste"
        widget = ui_test.find("Property//Frame/**/CollapsableFrame[*].title=='Materials on selected models'")
        await widget.click(
            pos=widget.position + ui_test.Vec2(widget.widget.computed_content_width / 2, 10), right_click=True
        )
        await ui_test.select_context_menu("Paste To All", offset=ui_test.Vec2(10, 10))

        # verify binding
        await self._validate_binding(64)

    async def test_material_thumb_context_menu_copy_2_to_many(self):
        # test copy 2 materials from Cone_01, Cone_02 to Sphere_*
        await self._validate_no_binding(64)

        # select source prim
        await self._select_prims(["/World/Cone_01", "/World/Cone_02"])

        # right click and "copy"
        await ui_test.find("Property//Frame/**/Button[*].identifier=='preview_drop_target'").click(right_click=True)
        await ui_test.select_context_menu("Copy", offset=ui_test.Vec2(10, 10))

        # select target prims
        to_select = [f"/World/Sphere_{i:02d}" for i in range(0, 64)]
        await self._select_prims(to_select)

        # right click in frame to "paste"
        widget = ui_test.find("Property//Frame/**/CollapsableFrame[*].title=='Materials on selected models'")
        await widget.click(
            pos=widget.position + ui_test.Vec2(widget.widget.computed_content_width / 2, 10), right_click=True
        )
        await ui_test.select_context_menu("Paste To All", offset=ui_test.Vec2(10, 10))

        # verify binding
        await self._validate_binding(64)
