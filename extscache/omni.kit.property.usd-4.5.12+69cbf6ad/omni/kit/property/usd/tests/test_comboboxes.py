# pylint: disable=missing-function-docstring, missing-class-docstring
import omni.kit.test
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
from pxr import Kind


class TestComboboxes(OmniUiTest):
    # Before running each test
    async def setUp(self):
        import omni.kit.app

        await arrange_windows("Stage", 200)
        await open_stage(get_test_data_path(__name__, "usd/cube.usda"))
        await wait_stage_loading()

        # enable omni.kit.property.geometry so PrimKindWidget can be registered
        manager = omni.kit.app.get_app().get_extension_manager()
        manager.set_extension_enabled_immediate("omni.kit.property.geometry", True)

        from omni.kit.property.geometry import GeometryPropertyExtension

        self.__geom = GeometryPropertyExtension()
        self.__geom.on_startup(manager.get_enabled_extension_id("omni.kit.property.geometry"))

    # After running each test
    async def tearDown(self):
        await wait_stage_loading()

        # disable omni.kit.property.geometry
        self.__geom.on_shutdown()
        del self.__geom
        omni.kit.app.get_app().get_extension_manager().set_extension_enabled_immediate(
            "omni.kit.property.geometry", False
        )

    async def test_combobox_change_kind(self):
        await wait_stage_loading()

        await select_prims(["/Xform/Cube"])
        await ui_test.human_delay(10)

        kind_widget = ui_test.find("Property//Frame/**/CollapsableFrame[*].title=='Kind'")
        kind_cbox = kind_widget.find("**/ComboBox[*]")
        model = kind_cbox.model

        # get Kinds
        all_kinds = Kind.Registry.GetAllKinds()
        all_kinds.insert(0, "")
        all_kinds.remove(Kind.Tokens.model)

        for index, kind in enumerate(all_kinds):
            # change selection
            model.set_value(index)
            await ui_test.human_delay(10)
            self.assertEqual(model.get_value(), kind)
