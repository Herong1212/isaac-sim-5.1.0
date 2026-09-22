import pathlib
import asyncio

import carb
import carb.settings
import carb.tokens
import omni.kit.app
import omni.kit.test
from  omni.kit.hydra_texture import create_hydra_texture
import omni.usd
import omni.ui as ui
from omni.ui import scene as sc
from typing import Callable

from .._camera_model import SceneCameraModel

# Establishing extension and data directories.
EXTENSION_FOLDER_PATH = pathlib.Path(
    omni.kit.app.get_app().get_extension_manager().get_extension_path_by_module(__name__)
)
DATA_DIR = EXTENSION_FOLDER_PATH.joinpath("data/tests")


class SceneCameraModelTest(omni.kit.test.AsyncTestCase):
    """
    This class defines setup, teardown and test methods for SceneCameraModel using an async IO context, required when
    working with libraries like omni.kit.
    """

    async def setUp(self):
        """
        Setting up before each test.
        """
        self._settings = carb.settings.acquire_settings_interface()

        self._usd_context_name = ""
        self._usd_context = omni.usd.get_context(self._usd_context_name)
        await self._usd_context.new_stage_async()

    async def tearDown(self):
        """
        Clean up after each test.
        """
        self._settings = None

        wait_iterations = 6
        for i in range(wait_iterations):
            await omni.kit.app.get_app().next_update_async()

    async def _create_hydra_texture_test(
        self,
        filename: str,
        texture_test: Callable,
        renderer: str = "pxr",
        res_x: int = 320,
        res_y: int = 320,
        engine_options: dict = None,
    ):
        """
        Helper method to create hydra texture test using provided parameters.
        """
        wait_iterations = 6
        try:
            if renderer not in self._usd_context.get_attached_hydra_engine_names():
                omni.usd.create_hydra_engine(renderer, self._usd_context)

            test_usd_asset = DATA_DIR.joinpath(filename)
            print("Opening '%s'" % (test_usd_asset))

            await self._usd_context.open_stage_async(str(test_usd_asset))

            if engine_options is None:
                engine_options = {"is_async": False}

            hydra_texture = create_hydra_texture(
                "test_viewport", res_x, res_y, self._usd_context_name, "/test_cam", renderer, **engine_options
            )

            return await texture_test(hydra_texture)
        finally:
            for i in range(wait_iterations):
                await omni.kit.app.get_app().next_update_async()

    async def test_simple_matrix(self):
        """
        Defines simple matrix test.
        """
        drawable_result = asyncio.Future()
        viewport_handle = []

        def _on_drawable_changed(event: carb.events.IEvent):
            """
            Handles drawable change event.
            """
            if event.type != omni.hydratexture.EVENT_TYPE_DRAWABLE_CHANGED:
                carb.log_error("Wrong event captured for DRAWABLE_CHANGED!")
                return

            viewport_handle.append(event.payload["viewport_handle"])

            nonlocal drawable_result
            if not drawable_result.done():
                drawable_result.set_result(True)

        async def _test(hydra_texture):
            """
            Returns hydra_texture.
            """
            return hydra_texture

        hydra_texture = await self._create_hydra_texture_test("simple_cubes_mat.usda", _test)

        drawable_changed_sub = hydra_texture.get_event_stream().create_subscription_to_push_by_type(
            omni.hydratexture.EVENT_TYPE_DRAWABLE_CHANGED,
            _on_drawable_changed,
            name="Test Drawable Change",
        )

        result = await drawable_result
        self.assertTrue(result)

        drawable_result = asyncio.Future()

        model = SceneCameraModel(self._usd_context_name, viewport_handle[-1])

        result = await drawable_result
        self.assertTrue(result)

        required_matrix = sc.Matrix44(1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, -35, -25, -140, 1)
        self.assertEqual(model.view, required_matrix)
