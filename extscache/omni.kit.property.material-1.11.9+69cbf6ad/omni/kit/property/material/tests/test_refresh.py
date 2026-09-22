from omni.kit import ui_test
from omni.kit.test_suite.helpers import arrange_windows

from .test_base import MaterialPropertiesTestBase
from .utils import time_logger


@time_logger
class TestMaterialRefreshWidget(MaterialPropertiesTestBase):
    async def setUp(self):
        await super().setUp()
        await arrange_windows()

    async def test_material_refresh_ui(self):
        scene_file_path = self._get_scene_path("thumbnail_test.usda")
        await self._load_scene(scene_file_path)
        await self._select_prims(["/World/Sphere"])

        # get raw frame & open
        raw_frame = ui_test.find("Property//Frame/**/CollapsableFrame[*].title=='Raw USD Properties'")
        raw_frame.widget.collapsed = False
        await ui_test.human_delay(10)

        # get material:binding label & scroll to it
        raw_frame.find("**/Label[*].text=='material:binding'").widget.scroll_here_y(0.5)
        await ui_test.human_delay(10)

        # get raw relationship widget
        widget = ui_test.find("Property//Frame/**/*.identifier=='sdf_relationship_material:binding[0].remove'")
        self.assertTrue(widget)

        # verify material binding in material widget
        self.assertEqual(
            ui_test.find("Property//Frame/**/StringField[*].identifier=='combo_drop_target'").widget.model.as_string,
            "/World/Looks/Material",
        )

        # remove raw material binding
        await widget.click()
        await ui_test.human_delay(10)

        # verify material binding updated in material widget
        self.assertEqual(
            ui_test.find("Property//Frame/**/StringField[*].identifier=='combo_drop_target'").widget.model.as_string,
            "None",
        )
