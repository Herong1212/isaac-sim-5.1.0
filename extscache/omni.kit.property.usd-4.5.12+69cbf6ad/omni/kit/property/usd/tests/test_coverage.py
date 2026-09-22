# pylint: disable=missing-function-docstring, missing-class-docstring
import omni.kit.test
import omni.kit.undo
import omni.kit.usd.layers as layers
import omni.usd
from omni.kit import ui_test
from omni.kit.test_suite.helpers import (
    arrange_windows,
    get_prims,
    get_test_data_path,
    open_stage,
    select_prims,
    wait_stage_loading,
)
from omni.ui.tests.test_base import OmniUiTest


class TestCoverage(OmniUiTest):
    # Before running each test
    async def setUp(self):
        import omni.kit.app

        await arrange_windows("Stage", 200)

        # enable omni.kit.property.transform so GfMatrixAttributeModel, GfQuatEulerAttributeModel, GfQuatAttributeModel can be used
        manager = omni.kit.app.get_app().get_extension_manager()
        manager.set_extension_enabled_immediate("omni.kit.property.transform", True)

        from omni.kit.property.transform import TransformPropertyExtension

        self.__transform = TransformPropertyExtension()
        self.__transform.on_startup(manager.get_enabled_extension_id("omni.kit.property.transform"))

        # enable omni.kit.property.transform so SchemaPropertiesWidget can be used
        manager = omni.kit.app.get_app().get_extension_manager()
        manager.set_extension_enabled_immediate("omni.kit.property.audio", True)

        from omni.kit.property.audio import AudioPropertyExtension

        self.__transform = AudioPropertyExtension()
        self.__transform.on_startup(manager.get_enabled_extension_id("omni.kit.property.audio"))

    # After running each test
    async def tearDown(self):
        await wait_stage_loading()

        # disable omni.kit.property.transform
        self.__transform.on_shutdown()
        del self.__transform
        omni.kit.app.get_app().get_extension_manager().set_extension_enabled_immediate(
            "omni.kit.property.transform", False
        )

    async def test_code_coverage_transform(self):
        await open_stage(get_test_data_path(__name__, "usd/cube.usda"))
        await wait_stage_loading()

        stage = omni.usd.get_context().get_stage()

        prim_list = [prim.GetPath().pathString for prim in get_prims(stage) if not omni.usd.is_hidden_type(prim)]
        for prim in prim_list:
            await select_prims([prim])
            await ui_test.human_delay(10)

    async def test_code_coverage_contextmenu(self):
        await open_stage(get_test_data_path(__name__, "usd/bound_shapes.usda"))
        await wait_stage_loading()

        await select_prims(["/World/Looks/OmniPBR"])
        await ui_test.human_delay(10)

        for widget_ref in ui_test.find_all("Property//Frame/**/CollapsableFrame[*]"):
            widget_ref.widget.collapsed = False

        mdl_widget = ui_test.find("Property//Frame/**/CollapsableFrame[*].title=='Material and Shader'")
        self.assertIsNotNone(mdl_widget)
        widget = mdl_widget.find("**.identifier=='float_slider_inputs:albedo_desaturation'")
        self.assertIsNotNone(widget)

        widget.widget.scroll_here_y(0.5)
        await ui_test.human_delay(10)
        await widget.click(right_click=True)
        await ui_test.human_delay(10)
        await ui_test.select_context_menu("Copy")
        await ui_test.human_delay(10)

        usd_context = omni.usd.get_context()
        try:
            layers_interface = layers.get_layers(usd_context)
            layers_interface.set_edit_mode(layers.LayerEditMode.SPECS_LINKING)

            # trigger context LayerEditMode.SPECS_LINKING code
            mdl_widget = ui_test.find("Property//Frame/**/CollapsableFrame[*].title=='Material and Shader'")
            self.assertIsNotNone(mdl_widget)

            widget = mdl_widget.find("**.identifier=='float_slider_inputs:albedo_desaturation'")
            self.assertIsNotNone(widget)

            widget.widget.scroll_here_y(0.5)
            await ui_test.human_delay(10)
            await widget.click(right_click=True)
            await ui_test.human_delay(10)
            await ui_test.select_context_menu(
                "Layers/Root Layer/Unlink", offset=ui_test.Vec2(10, 10), human_delay_speed=5
            )
            await ui_test.human_delay(10)

            # undo change
            omni.kit.undo.undo()
        finally:
            layers_interface = layers.get_layers(usd_context)
            layers_interface.set_edit_mode(layers.LayerEditMode.NORMAL)

    async def test_code_coverage_examples(self):
        import omni.kit.window.property as p
        from omni.kit.property.usd import Examples

        examples = Examples(p.get_window())

        await open_stage(get_test_data_path(__name__, "usd/cube.usda"))
        await wait_stage_loading()

        stage = omni.usd.get_context().get_stage()

        prim_list = [prim.GetPath().pathString for prim in get_prims(stage) if not omni.usd.is_hidden_type(prim)]
        for prim in prim_list:
            await select_prims([prim])
            await ui_test.human_delay(10)

        await select_prims([])
        await ui_test.human_delay(10)

        del examples

    async def test_code_coverage_audio(self):
        await open_stage(get_test_data_path("omni.kit.property.audio.tests.test_coverage", "audio_test.usda"))
        await wait_stage_loading()

        stage = omni.usd.get_context().get_stage()

        prim_list = [prim.GetPath().pathString for prim in get_prims(stage) if not omni.usd.is_hidden_type(prim)]
        for prim in prim_list:
            await select_prims([prim])
            await ui_test.human_delay(10)
