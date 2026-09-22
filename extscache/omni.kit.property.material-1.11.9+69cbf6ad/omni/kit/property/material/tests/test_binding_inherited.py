import omni.usd
from omni.kit import ui_test
from pxr import UsdShade

from .test_base import MaterialPropertiesTestBase
from .utils import time_logger


@time_logger
class TestMaterialInherited(MaterialPropertiesTestBase):
    async def test_material_override_inherited(self):
        scene_file_path = self._get_scene_path("material_binding_inherited.usda")
        await self._load_scene(scene_file_path)

        await ui_test.find("Stage").focus()

        # change strength of parent material
        prim = self._get_prim_at_path("/World/Xform_Inherited")
        mat, rel = self._get_bound_material(prim)
        omni.kit.commands.execute("SetMaterialStrength", rel=rel, strength=UsdShade.Tokens.weakerThanDescendants)
        await ui_test.human_delay(10)

        # Select the prim
        await self._select_prims(["/World/Xform_Inherited/Cone_02"])

        prim = self._get_prim_at_path("/World/Xform_Inherited/Cone_02")

        # clear bound material
        await ui_test.find_first(
            "Property//Frame/**/CollapsableFrame[*].title=='Materials on selected models'"
        ).find_first("**/Button[*].identifier=='clear_field'").click()
        await ui_test.human_delay(10)

        # verify inherited binding
        mat, rel = self._get_bound_material(prim)
        self.assertEqual(mat.GetPath().pathString, "/World/Looks/OmniSurface_Blood")

        # open material combobox
        topmost_button = sorted(
            ui_test.find_all("Property//Frame/**/Button[*].identifier=='combo_open_button'"), key=lambda f: f.position.y
        )[0]
        await topmost_button.click(human_delay_speed=4)
        await ui_test.human_delay(10)

        # select OmniPBR
        await ui_test.find_first("MaterialPropertyPopupWindow//Frame/**/Label[*].text=='/World/Looks/OmniPBR'").click(
            human_delay_speed=4
        )
        await ui_test.human_delay(10)

        # verify binding is OmniPBR
        mat, rel = self._get_bound_material(prim)
        self.assertEqual(mat.GetPath().pathString, "/World/Looks/OmniPBR")
