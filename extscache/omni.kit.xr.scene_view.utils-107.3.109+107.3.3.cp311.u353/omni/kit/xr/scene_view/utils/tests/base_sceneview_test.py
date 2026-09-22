# Copyright (c) 2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

__all__ = ["BaseSceneViewTest", "BaseUiTest", "_LabelWithBackground"]

from omni import ui
from omni.kit.xr.core.test_utils import XRTestVR
from omni.kit.xr.core.test_utils.xr_usd_stage import XRUsdStage
from omni.kit.xr.scene_view.utils import TransformableManipulator, WidgetComponent
from omni.kit.xr.scene_view.utils.transformable_manipulator import TransformableManipulatorModel
from omni.kit.xr.scene_view.utils.ui_container import UiContainer
from omni.ui import color
from pxr.Gf import Vec3d


class _LabelWithBackground(ui.Widget):
    def __init__(self, text: str = "TEXT", background=color(1.0)):
        super().__init__()
        self._text = text
        self._background = background
        self._do_layout()

    def _do_layout(self):
        with ui.ZStack():
            ui.Rectangle(style={"background_color": self._background})
            ui.Label(self._text)


class BaseSceneViewTest(XRTestVR):
    ACCEPTABLE_GOLDEN_THRESHOLD: float = 6e-4
    WINDOW_SIZE = (1024, 1024)
    TEX_SYNC_FRAMES = 80
    UI_APPEARANCE_DELAY = 7

    async def setUp(self):
        await super().setUp()

        self._test_widget = None

        from omni.kit.viewport.utility import get_active_viewport_window

        viewport_window = get_active_viewport_window()
        if viewport_window:
            viewport_window.position_x = 0  # type: ignore
            viewport_window.position_y = 0  # type: ignore
            viewport_window.width = self.WINDOW_SIZE[0]  # type: ignore
            viewport_window.height = self.WINDOW_SIZE[1]  # type: ignore
            viewport_window.viewport_api.resolution = (
                self.WINDOW_SIZE[0],
                self.WINDOW_SIZE[1],
            )

        async with XRUsdStage(keep_stage=True):
            self._set_camera_for_test()

    async def tearDown(self):
        if self._test_widget is not None:
            self._test_widget = None

        await super().tearDown()

    def _set_camera_for_test(self):
        self.set_viewport_camera(Vec3d(25, 25, 150), Vec3d(0, 0, 0))


class BaseUiTest(BaseSceneViewTest):
    WIDGET_TYPE = ui.Widget

    async def setUp(self):
        await super().setUp()
        self.__widget_component = WidgetComponent(self.WIDGET_TYPE)
        self.__container = UiContainer(self.__widget_component)
        self.__manipulator = self.__container.manipulator
        self.__model = self.__manipulator.transform_model

    async def tearDown(self):
        self._drop_members()
        await super().tearDown()

    def _drop_members(self) -> None:
        self.__container = None
        self.__model = None
        self.__manipulator = None
        self.__widget_component = None

    @property
    def widget_component(self) -> WidgetComponent:
        return self.__widget_component  # type: ignore

    @property
    def container(self) -> UiContainer:
        return self.__container  # type: ignore

    @property
    def manipulator(self) -> TransformableManipulator:
        return self.__manipulator  # type: ignore

    @property
    def model(self) -> TransformableManipulatorModel:
        return self.__model  # type: ignore
