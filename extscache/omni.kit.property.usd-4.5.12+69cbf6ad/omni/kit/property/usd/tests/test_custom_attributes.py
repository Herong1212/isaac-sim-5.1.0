# pylint: disable=missing-function-docstring, missing-class-docstring, invalid-overridden-method, protected-access
from pathlib import Path

import omni.kit.test
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


class TestCustomAttributes(OmniUiTest):
    # Before running each test
    async def setUp(self):
        import omni.kit.app

        await arrange_windows("Stage", 200)
        await open_stage(get_test_data_path(__name__, "usd/cube.usda"))
        await wait_stage_loading()

        omni.kit.window.property.managed_frame.reset_collapsed_state()
        omni.kit.window.property.managed_frame.set_collapsed_state("Camera/Lens", True)
        omni.kit.window.property.managed_frame.set_collapsed_state("Camera/Horizontal Aperture", True)
        omni.kit.window.property.managed_frame.set_collapsed_state("Camera/Vertical Aperture", True)
        omni.kit.window.property.managed_frame.set_collapsed_state("Camera/Clipping", True)
        omni.kit.window.property.managed_frame.set_collapsed_state("Camera/Fisheye Lens", False)
        omni.kit.window.property.managed_frame.set_collapsed_state("Camera/Extra Properties", True)

        # enable omni.kit.property.geometry so PrimKindWidget can be registered
        manager = omni.kit.app.get_app().get_extension_manager()
        manager.set_extension_enabled_immediate("omni.kit.property.camera", True)

        from omni.kit.property.camera import CameraPropertyExtension

        self.__camera = CameraPropertyExtension()
        self.__camera.on_startup(manager.get_enabled_extension_id("omni.kit.property.camera"))

        import omni.kit.window.property as p

        self._w = p.get_window()

    # After running each test
    async def tearDown(self):
        await wait_stage_loading()

        omni.kit.window.property.managed_frame.reset_collapsed_state()

        # disable omni.kit.property.geometry
        self.__camera.on_shutdown()
        del self.__camera
        omni.kit.app.get_app().get_extension_manager().set_extension_enabled_immediate(
            "omni.kit.property.camera", False
        )

    async def test_custom_attributes(self):
        await wait_stage_loading()

        omni.kit.commands.execute(
            "CreatePrimWithDefaultXform",
            prim_path="/Xform/Camera",
            prim_type="Camera",
            attributes={"focalLength": 10, "focusDistance": 32},
        )
        await select_prims(["/Xform/Camera"])
        await ui_test.human_delay(10)

        # screen-shot to verify custom properties are correct
        await self.docked_test_window(
            window=self._w._window,
            width=450,
            height=900,
            restore_window=ui.Workspace.get_window("Layer") or ui.Workspace.get_window("Stage"),
            restore_position=ui.DockPosition.BOTTOM,
        )

        await ui_test.human_delay(10)
        golden_img_dir = Path(get_test_data_path(__name__, "golden_img"))
        await self.finalize_test(golden_img_dir=golden_img_dir, golden_img_name="test_camera_ui.png", zero_mouse=True)
        # await ui_test.human_delay(500)
