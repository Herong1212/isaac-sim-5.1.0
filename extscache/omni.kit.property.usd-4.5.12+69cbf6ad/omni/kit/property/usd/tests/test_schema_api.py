# pylint: disable=missing-function-docstring, missing-class-docstring
from pathlib import Path

import carb
import omni.ui as ui
import omni.usd
from omni.kit import ui_test
from omni.kit.test_suite.helpers import (
    arrange_windows,
    get_test_data_path,
    open_stage,
    select_prims,
    wait_stage_loading,
)
from omni.ui.tests.test_base import OmniUiTest


class TestSchemaAPI(OmniUiTest):
    # Before running each test
    async def setUp(self):
        self._golden_img_dir = Path(get_test_data_path(__name__, "golden_img"))

        omni.kit.window.property.managed_frame.reset_collapsed_state()
        await arrange_windows("Stage", 64)
        await open_stage(get_test_data_path(__name__, "usd/bound_shapes.usda"))

        manager = omni.kit.app.get_app().get_extension_manager()
        manager.set_extension_enabled_immediate("omni.kit.property.light", True)

    # After running each test
    async def tearDown(self):
        omni.kit.window.property.managed_frame.reset_collapsed_state()
        await wait_stage_loading()
        manager = omni.kit.app.get_app().get_extension_manager()
        manager.set_extension_enabled_immediate("omni.kit.property.light", False)

    def _get_settings_codes(self):
        c1 = int(carb.settings.get_settings().get("ext/omni.kit.property.usd/showSchemaAPI"))
        c2 = int(carb.settings.get_settings().get("ext/omni.kit.property.usd/removeSchemaAPI"))
        return f"{c1}{c2}"

    async def test_schema_api_locked(self):
        carb.settings.get_settings().set("ext/omni.kit.property.usd/showSchemaAPI", True)
        carb.settings.get_settings().set("ext/omni.kit.property.usd/removeSchemaAPI", True)
        await self._test_schema_api()
        carb.settings.get_settings().set("ext/omni.kit.property.usd/showSchemaAPI", True)
        carb.settings.get_settings().set("ext/omni.kit.property.usd/removeSchemaAPI", False)
        await self._test_schema_api()
        carb.settings.get_settings().set("ext/omni.kit.property.usd/showSchemaAPI", False)
        carb.settings.get_settings().set("ext/omni.kit.property.usd/removeSchemaAPI", False)
        await self._test_schema_api()
        carb.settings.get_settings().set("ext/omni.kit.property.usd/showSchemaAPI", True)
        carb.settings.get_settings().set("ext/omni.kit.property.usd/removeSchemaAPI", True)

    async def _test_schema_api(self):
        import omni.kit.window.property as p

        def get_golden_image_name(fname, codes):
            golden_image_name = f"schema_api_{fname}-{codes}.png".replace(":", "-")

            duplicate_lookup = {
                "schema_api_CollectionAPI-shadowLink-00.png": "schema_api_CollectionAPI-lightLink-00.png",
                "schema_api_LightAPI-00.png": "schema_api_CollectionAPI-lightLink-00.png",
                "schema_api_ShapingAPI-00.png": "schema_api_CollectionAPI-lightLink-00.png",
                "schema_api_CollectionAPI-lightLink-10.png": "schema_api_CollectionAPI-lightLink-11.png",
                "schema_api_CollectionAPI-shadowLink-10.png": "schema_api_CollectionAPI-shadowLink-11.png",
                "schema_api_LightAPI-10.png": "schema_api_LightAPI-11.png",
            }

            if golden_image_name in duplicate_lookup:
                return duplicate_lookup[golden_image_name]
            return golden_image_name

        codes = self._get_settings_codes()

        stage_window = ui_test.find("Stage")
        await stage_window.focus()
        await wait_stage_loading()

        await select_prims(["/World/defaultLight"])
        await ui_test.human_delay()

        w = p.get_window()
        for fname in ["LightAPI", "CollectionAPI:lightLink", "CollectionAPI:shadowLink", "ShapingAPI"]:
            await self.docked_test_window(
                window=w._window,
                width=450,
                height=500,
                restore_window=ui.Workspace.get_window("Layer") or ui.Workspace.get_window("Stage"),
                restore_position=ui.DockPosition.BOTTOM,
            )

            # collapse unwanted frames
            for widget_ref in ui_test.find_all("Property//Frame/**/CollapsableFrame[*]"):
                widget_ref.widget.collapsed = True

                if widget_ref.widget.title in ["Light", fname]:
                    widget_ref.widget.visible = True
                    widget_ref.widget.collapsed = False
                else:
                    widget_ref.widget.visible = False

            await ui_test.human_delay(10)
            await self.finalize_test(
                golden_img_dir=self._golden_img_dir, golden_img_name=get_golden_image_name(fname, codes)
            )
            await ui_test.human_delay(50)

        await select_prims([])

    async def test_remove_schema_api_ui(self):
        await arrange_windows("Stage", 128)

        usd_context = omni.usd.get_context()
        stage = usd_context.get_stage()

        # Get the property window
        property_window = omni.ui.Workspace.get_window("Property")
        self.assertTrue(property_window)

        # select prim
        await select_prims(["/World/defaultLight"])
        prim = stage.GetPrimAtPath("/World/defaultLight")
        await ui_test.human_delay()

        # collapse unwanted frames to make sure "remove" button is visible
        for widget_ref in ui_test.find_all("Property//Frame/**/CollapsableFrame[*]"):
            widget_ref.widget.collapsed = True

            if widget_ref.widget.title in ["Light"]:
                widget_ref.widget.visible = True
                widget_ref.widget.collapsed = False
            elif widget_ref.widget.title in [
                "LightAPI",
                "CollectionAPI:lightLink",
                "CollectionAPI:shadowLink",
                "ShapingAPI",
            ]:
                widget_ref.widget.visible = True
                widget_ref.widget.collapsed = True
            else:
                widget_ref.widget.visible = False

        # verify default state
        applied_schemas = prim.GetAppliedSchemas()
        self.assertIn("ShapingAPI", applied_schemas)

        # Find and button the remove API schema button
        await ui_test.human_delay()
        remove_buttons = ui_test.find("Property//Frame/**/Button[*].identifier=='ShapingAPI.remove_api_schema_button'")
        await remove_buttons.click()

        # Verify the API schema was removed
        await ui_test.human_delay()
        applied_schemas = prim.GetAppliedSchemas()
        self.assertNotIn("ShapingAPI", applied_schemas)

        # Test undo
        omni.kit.undo.undo()
        # Verify the API schema was restored
        applied_schemas = prim.GetAppliedSchemas()
        self.assertIn("ShapingAPI", applied_schemas)

        # Test redo
        omni.kit.undo.redo()
        # Verify the API schema was removed again
        applied_schemas = prim.GetAppliedSchemas()
        self.assertNotIn("ShapingAPI", applied_schemas)
        applied_schemas = prim.GetAppliedSchemas()
