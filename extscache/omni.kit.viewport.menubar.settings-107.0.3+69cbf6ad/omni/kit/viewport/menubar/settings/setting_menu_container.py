# Copyright (c) 2021-2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

__all__ = ["SettingMenuContainer"]

from functools import partial
from typing import Any, Dict, List, Optional

import carb
import carb.settings
from omni.kit.viewport.menubar.core import (
    IconMenuDelegate,
    SliderMenuDelegate,
    CheckboxMenuDelegate,
    SettingModel,
    SettingModelWithDefaultValue,
    ViewportMenuContainer,
    FloatArraySettingColorMenuItem,
    menu_is_tearable,
)
import omni.ui as ui
from omni.ui import color as cl

from .menu_item.settings_renderer_menu_item import SettingsRendererMenuItem
from .menu_item.settings_transform_manipulator import SettingsTransformManipulator
from .style import UI_STYLE


class ViewportSetting:
    def __init__(self, key: str, default: Any, set_default: bool = True, read_incoming: bool = False):
        self.key = key

        self.__default = default
        self.__read_incoming = read_incoming
        self.__set_default = set_default

    @property
    def default(self) -> Any:
        if self.__read_incoming:
            settings = carb.settings.get_settings()
            incoming_default = settings.get(self.key)
            if incoming_default is not None:
                self.__default = incoming_default

            # Only read once
            self.__read_incoming = False
        return self.__default

    def set_default(self, settings):
        if self.__set_default:
            settings.set_default(self.key, self.default)

    def reset(self, settings):
        settings.set(self.key, self.default)


class SelectionColorSetting(ViewportSetting):
    OUTLINE = "/persistent/app/viewport/outline/color"
    INTERSECTION = "/persistent/app/viewport/outline/intersection/color"

    def __init__(self, default: Any):
        super().__init__(self.OUTLINE, default, False)
        self.index = 1020

    def reset(self, settings):
        float_array = settings.get(self.key)
        float_array = float_array[0 : self.index] + self.default + float_array[self.index + len(self.default) :]
        carb.settings.get_settings().set(self.OUTLINE, float_array)
        carb.settings.get_settings().set(self.INTERSECTION, self.default)


class VIEWPORT_SETTINGS:  # noqa: N801
    NAVIGATION_SPEED = ViewportSetting("/persistent/app/viewport/camMoveVelocity", 5.0)
    NAVIGATION_SPEED_MULTAMOUNT = ViewportSetting("/persistent/app/viewport/camVelocityScalerMultAmount", 1.1)
    SHOW_SPEED_ON_START = ViewportSetting("/persistent/app/viewport/camShowSpeedOnStart", True)
    ADAPTIVE_SPEED = ViewportSetting("/persistent/app/viewport/camVelocityCOINormalization", 0.0)
    GAMEPAD_CONTROL = ViewportSetting("/persistent/app/omniverse/gamepadCameraControl", True)
    CAMERA_STOP_ON_UP = ViewportSetting("/persistent/app/viewport/camStopOnMouseUp", True)
    CAM_UPDATE_CLAMPING = ViewportSetting("/ext/omni.kit.manipulator.camera/clampUpdates", 0.15, read_incoming=True)
    INERTIA_ENABLED = ViewportSetting("/persistent/app/viewport/camInertiaEnabled", False)
    INERTIA_ANOUNT = ViewportSetting("/persistent/app/viewport/camInertiaAmount", 0.55)
    ROTATION_SMOOTH_ENABLED = ViewportSetting("/persistent/app/viewport/camRotSmoothEnabled", True)
    ROTATION_SMOOTH_SCALE = ViewportSetting("/persistent/app/viewport/camRotSmoothScale", 20.0)
    ROTATION_SMOOTH_ALWAYS = ViewportSetting("/persistent/app/viewport/camRotSmoothAlways", False)
    GESTURE_ENABLED = ViewportSetting("/persistent/app/viewport/camGestureEnabled", False)
    GESTURE_TIME = ViewportSetting("/persistent/app/viewport/camGestureTime", 0.12)
    GESTURE_RADIUS = ViewportSetting("/persistent/app/viewport/camGestureRadius", 20)
    SELECTION_LINE_WIDTH = ViewportSetting("/persistent/app/viewport/outline/width", 2)
    GRID_LINE_WIDTH = ViewportSetting("/persistent/app/viewport/grid/lineWidth", 1)
    GRID_SCALE = ViewportSetting("/persistent/app/viewport/grid/scale", 100.0)
    GRID_FADE = ViewportSetting("/persistent/app/viewport/grid/lineFadeOutStartDistance", 10.0)
    GIZMO_LINE_WIDTH = ViewportSetting("/persistent/app/viewport/gizmo/lineWidth", 1.0)
    GIZMO_SCALE_ENABLED = ViewportSetting("/persistent/app/viewport/gizmo/constantScaleEnabled", True)
    GIZMO_SCALE = ViewportSetting("/persistent/app/viewport/gizmo/constantScale", 10.0)
    GIZMO_GLOBAL_SCALE = ViewportSetting("/persistent/app/viewport/gizmo/scale", 1.0)
    GIZMO_MIN_FADEOUT = ViewportSetting("/persistent/app/viewport/gizmo/minFadeOut", 1.0)
    GIZMO_MAX_FADEOUT = ViewportSetting("/persistent/app/viewport/gizmo/maxFadeOut", 50)
    UI_BACKGROUND_OPACITY = ViewportSetting("/persistent/app/viewport/ui/background/opacity", 1.0)
    UI_BRIGHTNESS = ViewportSetting("/persistent/app/viewport/ui/brightness", 0.84)
    OBJECT_CENTRIC = ViewportSetting("/persistent/app/viewport/objectCentricNavigation", 0)
    DOUBLE_CLICK_COI = ViewportSetting("/persistent/app/viewport/coiDoubleClick", False)
    BBOX_LINE_COLOR = ViewportSetting("/persistent/app/viewport/boundingBoxes/lineColor", [0.886, 0.447, 0.447])
    GRID_LINE_COLOR = ViewportSetting("/persistent/app/viewport/grid/lineColor", [0.3, 0.3, 0.3])
    OUTLINE_COLOR = SelectionColorSetting([1.0, 0.6, 0.0, 1.0])
    LOOK_SPEED_HORIZ = ViewportSetting("/persistent/exts/omni.kit.manipulator.camera/lookSpeed/0", 180.0)
    LOOK_SPEED_VERT = ViewportSetting("/persistent/exts/omni.kit.manipulator.camera/lookSpeed/1", 90.0)
    TUMBLE_SPEED = ViewportSetting("/persistent/exts/omni.kit.manipulator.camera/tumbleSpeed", 360.0)
    ZOOM_SPEED = ViewportSetting("/persistent/exts/omni.kit.manipulator.camera/moveSpeed/2", 1.0)
    FLY_IGNORE_VIEW_DIRECTION = ViewportSetting("/persistent/exts/omni.kit.manipulator.camera/flyViewLock", False)


class ViewportSettingModel(SettingModelWithDefaultValue):
    def __init__(self, viewport_setting: ViewportSetting, draggable: bool = False):
        super().__init__(viewport_setting.key, viewport_setting.default, draggable=draggable)


CAM_VELOCITY_MIN = "/persistent/app/viewport/camVelocityMin"
CAM_VELOCITY_MAX = "/persistent/app/viewport/camVelocityMax"
CAM_VELOCITY_SCALER_MIN = "/persistent/app/viewport/camVelocityScalerMin"
CAM_VELOCITY_SCALER_MAX = "/persistent/app/viewport/camVelocityScalerMax"

SETTING_UI_BRIGHTNESS_MIN = "/app/viewport/ui/minBrightness"
SETTING_UI_BRIGHTNESS_MAX = "/app/viewport/ui/maxBrightness"
BRIGHTNESS_VALUE_RANGE_MIN = 0.25
BRIGHTNESS_VALUE_RANGE_MAX = 1.0
OUTLINE_COLOR_INDEX = 1020


class SelectionColorMenuItem(FloatArraySettingColorMenuItem):
    def __init__(self):
        setting = VIEWPORT_SETTINGS.OUTLINE_COLOR
        super().__init__(
            setting.key, setting.default, name="Selection Color", start_index=setting.index, has_reset=True
        )

    def on_color_changed(self, colors: List[float]) -> None:
        # Set the default exterior color
        super().on_color_changed(colors)
        # Set the interior intersection color too
        carb.settings.get_settings().set(VIEWPORT_SETTINGS.OUTLINE_COLOR.INTERSECTION, colors)


class BoundingColorMenuItem(FloatArraySettingColorMenuItem):
    def __init__(self):
        setting = VIEWPORT_SETTINGS.BBOX_LINE_COLOR
        super().__init__(setting.key, setting.default, name="Bounding Box Color", has_reset=True)


class GridColorMenuItem(FloatArraySettingColorMenuItem):
    def __init__(self):
        setting = VIEWPORT_SETTINGS.GRID_LINE_COLOR
        super().__init__(setting.key, setting.default, name="Grid Color", has_reset=True)


class MenuContext:
    def __init__(self):
        self.__renderer_menu_item: Optional[SettingsRendererMenuItem] = None
        self.__settings = carb.settings.get_settings()
        self.__carb_subscriptions = []

    @property
    def settings(self):
        return self.__settings

    @property
    def renderer_menu_item(self) -> Optional[SettingsRendererMenuItem]:
        return self.__renderer_menu_item

    @renderer_menu_item.setter
    def renderer_menu_item(self, render_menu_item: Optional[SettingsRendererMenuItem]) -> None:
        if self.__renderer_menu_item:
            self.__renderer_menu_item.destroy()
        self.__renderer_menu_item = render_menu_item

    def add_carb_subscription(self, carb_sub: carb.settings.SubscriptionId):
        self.__carb_subscriptions.append(carb_sub)

    def destroy(self):
        self.renderer_menu_item = None
        for sub in self.__carb_subscriptions:
            sub.unsubscribe()
        self.__carb_subscriptions = []


class SettingMenuContainer(ViewportMenuContainer):
    """The menu with the viewport settings"""

    def __init__(self):
        super().__init__(
            name="Settings",
            delegate=IconMenuDelegate("Settings"),
            visible_setting_path="/exts/omni.kit.viewport.menubar.settings/visible",
            order_setting_path="/exts/omni.kit.viewport.menubar.settings/order",
            style=UI_STYLE,
        )
        self.__menu_context: Dict[str, MenuContext] = {}

        settings = carb.settings.get_settings()
        settings.set_default(CAM_VELOCITY_MIN, 0.01)
        settings.set_default(CAM_VELOCITY_MAX, 50)
        settings.set_default(CAM_VELOCITY_SCALER_MIN, 1)
        settings.set_default(CAM_VELOCITY_SCALER_MAX, 10)
        for value in VIEWPORT_SETTINGS.__dict__.values():
            if isinstance(value, ViewportSetting):
                value.set_default(settings)

    def destroy(self):
        for menu_ctx in self.__menu_context.values():
            menu_ctx.destroy()
        self.__menu_context = {}
        super().destroy()

    def build_fn(self, factory: Dict):
        ui.Menu(self.name, delegate=self._delegate, on_build_fn=partial(self._build_menu, factory), style=self._style)

    def _build_menu(self, factory: Dict) -> None:
        viewport_api = factory.get("viewport_api")
        if not viewport_api:
            return
        viewport_api_id = viewport_api.id
        menu_ctx = self.__menu_context.get(viewport_api_id)
        if menu_ctx:
            menu_ctx.destroy()
        menu_ctx = MenuContext()
        self.__menu_context[viewport_api_id] = menu_ctx

        ui.Menu(
            "Navigation",
            on_build_fn=lambda: self.__build_navigation_menu_items(menu_ctx),
            tearable=menu_is_tearable("omni.kit.viewport.menubar.settings.Navigation"), identifier='Navigation'
        )
        ui.Menu(
            "Selection",
            on_build_fn=lambda: self.__build_selection_menu_items(menu_ctx),
            tearable=menu_is_tearable("omni.kit.viewport.menubar.settings.Selection"), identifier='Selection'
        )
        ui.Menu(
            "Grid",
            on_build_fn=lambda: self.__build_grid_menu_items(menu_ctx),
            tearable=menu_is_tearable("omni.kit.viewport.menubar.settings.Grid"), identifier='Grid'
        )
        ui.Menu(
            "Gizmos",
            on_build_fn=lambda: self.__build_gizmo_menu_items(menu_ctx),
            tearable=menu_is_tearable("omni.kit.viewport.menubar.settings.Gizmos"), identifier='Gizmos'
        )
        menu_ctx.renderer_menu_item = SettingsRendererMenuItem(
            "Viewport", factory=factory, tearable=menu_is_tearable("omni.kit.viewport.menubar.settings.Viewport"), identifier='Viewport'
        )
        ui.Menu(
            "Viewport UI",
            on_build_fn=lambda: self.__build_ui_menu_items(menu_ctx),
            tearable=menu_is_tearable("omni.kit.viewport.menubar.settings.ViewportUI"), identifier='ViewportUI'
        )
        SettingsTransformManipulator(
            "Manipulator Transform",
            factory=factory,
            tearable=menu_is_tearable("omni.kit.viewport.menubar.settings.ManipulatorTransform"), identifier='ManipulatorTransform'
        )

        ui.Separator()
        ui.MenuItem(
            "Reset To Defaults",
            hide_on_click=False,
            triggered_fn=lambda vid=viewport_api_id: self.__reset_settings(vid), identifier='ResetToDefaults'
        )
        ui.Separator()
        ui.MenuItem("Preferences", hide_on_click=False, triggered_fn=self._show_viewport_preference, identifier='Preferences')

    def __build_navigation_menu_items(self, menu_ctx: MenuContext) -> None:
        settings = carb.settings.get_settings()
        ui.MenuItem(
            "Navigation Speed",
            hide_on_click=False,
            delegate=SliderMenuDelegate(
                model=ViewportSettingModel(VIEWPORT_SETTINGS.NAVIGATION_SPEED, draggable=True),
                min=settings.get(CAM_VELOCITY_MIN),
                max=settings.get(CAM_VELOCITY_MAX),
                tooltip="Set the Fly Mode navigation speed",
                has_reset=True,
            ),
            identifier='NavigationSpeed'
        )

        ui.MenuItem(
            "Navigation Speed Scalar",
            hide_on_click=False,
            delegate=SliderMenuDelegate(
                model=ViewportSettingModel(VIEWPORT_SETTINGS.NAVIGATION_SPEED_MULTAMOUNT, draggable=True),
                min=settings.get(CAM_VELOCITY_SCALER_MIN),
                max=settings.get(CAM_VELOCITY_SCALER_MAX),
                tooltip="Change the Fly Mode navigation speed by this amount",
                has_reset=True,
            ),
            identifier='NavigationSpeedScalar'
        )

        ui.MenuItem(
            "Lock Navigation Height",
            hide_on_click=False,
            delegate=CheckboxMenuDelegate(
                model=ViewportSettingModel(VIEWPORT_SETTINGS.FLY_IGNORE_VIEW_DIRECTION),
                tooltip="Whether forward/backward and up/down movements ignore camera-view direction (similar to left/right strafe)",
                has_reset=True,
            ),
            identifier='LockNavigationHeight'
        )

        ui.MenuItem(
            "Gamepad Camera Control",
            hide_on_click=False,
            delegate=CheckboxMenuDelegate(
                model=ViewportSettingModel(VIEWPORT_SETTINGS.GAMEPAD_CONTROL),
                tooltip="Enable gamepad navigation for this Viewport",
                has_reset=True,
            ),
            identifier='GamepadCameraControl'
        )

        ui.Separator()
        ui.MenuItem(
            "Object Centric Navigation",
            hide_on_click=False,
            delegate=CheckboxMenuDelegate(
                model=ViewportSettingModel(VIEWPORT_SETTINGS.OBJECT_CENTRIC),
                tooltip="Set camera's center of interest to center of object under mouse when camera manipulation begins",
                has_reset=True,
            ),
            identifier='ObjectCentricNavigation'
        )

        ui.MenuItem(
            "Double Click Sets Interest",
            hide_on_click=False,
            delegate=CheckboxMenuDelegate(
                model=ViewportSettingModel(VIEWPORT_SETTINGS.DOUBLE_CLICK_COI),
                tooltip="Double click will set the center of interest to the object under mouse." +
                "\nEnabling this may make click-to-select less responsive.",
                has_reset=True,
            ),
            identifier='DoubleClicksetsInterest'
        )

        ui.Separator()
        self.__build_advanced_navigation_items(menu_ctx)

        ui.Separator()
        self.__build_navigation_speed_items(menu_ctx)

        self.__build_debug_settings(menu_ctx)

    def __build_navigation_speed_items(self, menu_ctx: MenuContext):
        ui.MenuItem(
            "Look Speed Horizontal",
            hide_on_click=False,
            delegate=SliderMenuDelegate(
                model=ViewportSettingModel(VIEWPORT_SETTINGS.LOOK_SPEED_HORIZ, draggable=True),
                min=0,
                max=360,
                step=1,
                tooltip="Set the Look Mode navigation speed as degrees rotated over a drag across the Viepwort horizonatally.",
                has_reset=True,
            ),
            identifier='LookSpeedHorizontal'
        )
        ui.MenuItem(
            "Look Speed Vertical",
            hide_on_click=False,
            delegate=SliderMenuDelegate(
                model=ViewportSettingModel(VIEWPORT_SETTINGS.LOOK_SPEED_VERT, draggable=True),
                min=0,
                max=180,
                step=1,
                tooltip="Set the Look Mode navigation speed as degrees rotated over a drag across the Viepwort vertically.",
                has_reset=True,
            ),
            identifier='LookSpeedVertical'
        )
        ui.MenuItem(
            "Tumble Speed",
            hide_on_click=False,
            delegate=SliderMenuDelegate(
                model=ViewportSettingModel(VIEWPORT_SETTINGS.TUMBLE_SPEED, draggable=True),
                min=0,
                max=720,
                step=1,
                tooltip="Set the Tumble Mode navigation speed as degrees rotated over a drag across the Viepwort.",
                has_reset=True,
            ),
            identifier='TumbleSpeed'
        )
        ui.MenuItem(
            "Zoom Speed",
            hide_on_click=False,
            delegate=SliderMenuDelegate(
                model=ViewportSettingModel(VIEWPORT_SETTINGS.ZOOM_SPEED, draggable=True),
                min=0,
                max=2,
                tooltip="Set the Zoom Mode navigation speed",
                has_reset=True,
            ),
            identifier='ZoomSpeed'
        )

    def __build_advanced_navigation_items(self, menu_ctx: MenuContext):
        settings = menu_ctx.settings
        inertia_enable_model = ViewportSettingModel(VIEWPORT_SETTINGS.INERTIA_ENABLED)
        ui.MenuItem(
            "Inertia Mode",
            hide_on_click=False,
            delegate=CheckboxMenuDelegate(
                model=inertia_enable_model,
                tooltip="Enable advanced settings to control camera inertia and gestures for mouse manipulation",
                has_reset=True,
            ),
            identifier='InertiaMode'
        )

        inertia_menu_item = ui.MenuItem(
            "Camera Inertia",
            hide_on_click=False,
            delegate=SliderMenuDelegate(
                model=ViewportSettingModel(VIEWPORT_SETTINGS.INERTIA_ANOUNT, draggable=True),
                tooltip="Seconds the inertia is active for",
                min=0.0,
                max=4.0,
                has_reset=True,
            ),
            identifier='CameraInertia'
        )

        # Show an entry for enabling disabling inertia on all modes if this value is set
        inertia_modes = settings.get("/exts/omni.kit.manipulator.camera/inertiaModesEnabled")
        inertia_modes_menu_item = None
        if inertia_modes:
            # Odd setting to control inertai always, but its what View was using, so preserve as it is persistant
            legacy_all_interia_model = ViewportSettingModel(VIEWPORT_SETTINGS.ROTATION_SMOOTH_ALWAYS)
            inertia_modes_menu_item = ui.MenuItem(
                "Inertia For Other Movements",
                hide_on_click=False,
                delegate=CheckboxMenuDelegate(
                    model=legacy_all_interia_model,
                    tooltip="Apply inertia to other camera movements or only WASD navigation",
                    has_reset=True,
                ),
                identifier='InertiaForOtherMovements'
            )

            def _toggle_inertia_always(model: ui.AbstractValueModel):
                if model.as_bool:
                    # Allow a user specified preference to enable ceratin modes only, otherwise default to all
                    inertia_modes = settings.get("/app/viewport/inertiaModesEnabled")
                    inertia_modes = inertia_modes or [1, 1, 1, 1]
                else:
                    inertia_modes = [1, 0, 0, 0]
                settings.set("/exts/omni.kit.manipulator.camera/inertiaModesEnabled", inertia_modes)

            _toggle_inertia_always(legacy_all_interia_model)

            menu_ctx.add_carb_subscription(
                legacy_all_interia_model.subscribe_value_changed_fn(_toggle_inertia_always)
            )

        def __on_inertial_changed(model: ui.AbstractValueModel):
            inertia_enabled = model.as_bool
            inertia_menu_item.visible = inertia_enabled
            if inertia_modes_menu_item:
                inertia_modes_menu_item.visible = inertia_enabled

        # Sync the state now
        __on_inertial_changed(inertia_enable_model)

        menu_ctx.add_carb_subscription(
            inertia_enable_model.subscribe_value_changed_fn(__on_inertial_changed)
        )

    def __build_debug_settings(self, menu_ctx: MenuContext):
        settings = menu_ctx.settings
        _added_initial_separator = False

        def add_initial_separator():
            nonlocal _added_initial_separator
            if not _added_initial_separator:
                _added_initial_separator = True
                ui.Separator()

        if settings.get("/exts/omni.kit.viewport.menubar.settings/show/camera/clamping"):
            add_initial_separator()
            ui.MenuItem(
                "Animation clamp",
                hide_on_click=False,
                delegate=SliderMenuDelegate(
                    model=ViewportSettingModel(VIEWPORT_SETTINGS.CAM_UPDATE_CLAMPING),
                    tooltip="Clamp animation to this maximum number of seconds",
                    min=0.0001,
                    max=1.0,
                    has_reset=True,
                ),
                identifier='AnimationClamp'
            )

    def __build_selection_menu_items(self, menu_ctx: MenuContext):
        SelectionColorMenuItem()

        ui.MenuItem(
            "Selection Line Width",
            hide_on_click=False,
            delegate=SliderMenuDelegate(
                model=ViewportSettingModel(VIEWPORT_SETTINGS.SELECTION_LINE_WIDTH, draggable=True),
                min=1,
                max=15,
                slider_class=ui.IntSlider,
                has_reset=True,
            ),
            identifier="SelectionLineWidth"
        )

        BoundingColorMenuItem()

    def __build_grid_menu_items(self, menu_ctx: MenuContext):
        GridColorMenuItem()

        ui.MenuItem(
            "Grid Line Width",
            hide_on_click=False,
            delegate=SliderMenuDelegate(
                model=ViewportSettingModel(VIEWPORT_SETTINGS.GRID_LINE_WIDTH, draggable=True),
                min=1,
                max=10,
                slider_class=ui.IntSlider,
                has_reset=True,
            ),
            identifier='GridLineWidth'
        )

        ui.MenuItem(
            "Grid Size",
            hide_on_click=False,
            delegate=SliderMenuDelegate(
                model=ViewportSettingModel(VIEWPORT_SETTINGS.GRID_SCALE, draggable=True),
                min=1.0,
                max=1000.0,
                has_reset=True,
            ),
            identifier='GridSize'
        )

        fadeout_model = ViewportSettingModel(VIEWPORT_SETTINGS.GRID_FADE, draggable=True)

        def __on_fadeout_changed(model: ui.AbstractValueModel):
            carb.settings.get_settings().set("/persistent/app/viewport/grid/lineFadeOutEndDistance", model.as_float * 4)

        ui.MenuItem(
            "Grid Fade",
            hide_on_click=False,
            delegate=SliderMenuDelegate(model=fadeout_model, min=0.5, max=50.0, has_reset=True),
            identifier='GridFade'
        )

        menu_ctx.add_carb_subscription(
            fadeout_model.subscribe_value_changed_fn(__on_fadeout_changed)
        )

    def __build_ui_menu_items(self, menu_ctx: MenuContext):
        def __ui_background_opacity_changed(model: ui.AbstractValueModel) -> None:
            alpha = int(model.as_float * 255)
            name = "viewport_menubar_background"
            color = cl._find(name)  # noqa: PLW0212
            color = (color & 0x00FFFFFF) + (alpha << 24)
            cl._store(name, color)  # noqa: PLW0212

        ui_background_opacity_model = ViewportSettingModel(VIEWPORT_SETTINGS.UI_BACKGROUND_OPACITY, draggable=True)
        ui.MenuItem(
            "UI Background Opacity",
            hide_on_click=False,
            delegate=SliderMenuDelegate(model=ui_background_opacity_model, min=0.0, max=1.0, has_reset=True),
            identifier='UIBackgroundOpacity'
        )
        __ui_background_opacity_changed(ui_background_opacity_model)

        settings = carb.settings.get_settings()
        min_brightness = settings.get(SETTING_UI_BRIGHTNESS_MIN)
        max_brightness = settings.get(SETTING_UI_BRIGHTNESS_MAX)

        def __ui_brightness_changed(model: ui.AbstractValueModel) -> None:
            def __gray_to_color(gray: int):
                return 0xFF000000 + (gray << 16) + (gray << 8) + gray

            value = (model.as_float - BRIGHTNESS_VALUE_RANGE_MIN) / (
                BRIGHTNESS_VALUE_RANGE_MAX - BRIGHTNESS_VALUE_RANGE_MIN
            )
            light_gray = int(value * 255)
            color = __gray_to_color(light_gray)
            cl._store("viewport_menubar_light", color)  # noqa: PLW0212

            medium_gray = int(light_gray * 0.539)
            color = __gray_to_color(medium_gray)
            cl._store("viewport_menubar_medium", color)  # noqa: PLW0212

        ui_brightness_model = ViewportSettingModel(VIEWPORT_SETTINGS.UI_BRIGHTNESS, draggable=True)
        ui.MenuItem(
            "UI Control Brightness",
            hide_on_click=False,
            delegate=SliderMenuDelegate(model=ui_brightness_model, min=min_brightness, max=max_brightness, has_reset=True),
            identifier='UIControlBrightness'
        )
        __ui_brightness_changed(ui_brightness_model)

        menu_ctx.add_carb_subscription(
            ui_background_opacity_model.subscribe_value_changed_fn(__ui_background_opacity_changed)
        )
        menu_ctx.add_carb_subscription(
            ui_brightness_model.subscribe_value_changed_fn(__ui_brightness_changed)
        )

    def __build_gizmo_menu_items(self, menu_ctx: MenuContext):
        ui.MenuItem(
            "Gizmo Line Width",
            hide_on_click=False,
            delegate=SliderMenuDelegate(
                model=ViewportSettingModel(VIEWPORT_SETTINGS.GIZMO_LINE_WIDTH, draggable=True),
                min=1.0,
                max=25.0,
                has_reset=True,
            ),
            identifier='GizmoLineWidth'
        )

        scale_enabled_model = ViewportSettingModel(VIEWPORT_SETTINGS.GIZMO_SCALE_ENABLED)
        ui.MenuItem(
            "Gizmo Constant Scale Enabled",
            hide_on_click=False,
            delegate=CheckboxMenuDelegate(model=scale_enabled_model, has_reset=True),
            identifier='GizmoConstantScaleEnabled'
        )

        constant_scale_menu_item = ui.MenuItem(
            "Gizmo Constant Scale",
            hide_on_click=False,
            delegate=SliderMenuDelegate(
                model=ViewportSettingModel(VIEWPORT_SETTINGS.GIZMO_SCALE, draggable=True),
                min=0.5,
                max=100.0,
                has_reset=True,
            ),
            identifier='GizmoConstantScale'
        )

        global_scale_menu_item = ui.MenuItem(
            "Gizmo Camera Scale" if scale_enabled_model.as_bool else "Gizmo Global Scale",
            hide_on_click=False,
            delegate=SliderMenuDelegate(
                model=ViewportSettingModel(VIEWPORT_SETTINGS.GIZMO_GLOBAL_SCALE, draggable=True),
                min=0.01,
                max=4.0,
                has_reset=True,
            ),
            identifier='GizmoCameraScale'
        )

        def __on_gizmo_enabled_changed(model: SettingModel):
            is_constant_scale = model.as_bool
            constant_scale_menu_item.visible = is_constant_scale
            global_scale_menu_item.text = "Gizmo Camera Scale" if is_constant_scale else "Gizmo Global Scale"

        __on_gizmo_enabled_changed(scale_enabled_model)

        menu_ctx.add_carb_subscription(
            scale_enabled_model.subscribe_value_changed_fn(__on_gizmo_enabled_changed)
        )

        ui.MenuItem(
            "Gizmo Min FadeOut",
            hide_on_click=False,
            delegate=SliderMenuDelegate(
                model=ViewportSettingModel(VIEWPORT_SETTINGS.GIZMO_MIN_FADEOUT, draggable=True),
                min=1.0,
                max=1000.0,
                has_reset=True,
            ),
            identifier='GizmoMinFadeOut'
        )

        ui.MenuItem(
            "Gizmo Max FadeOut",
            hide_on_click=False,
            delegate=SliderMenuDelegate(
                model=ViewportSettingModel(VIEWPORT_SETTINGS.GIZMO_MAX_FADEOUT, draggable=True),
                min=1.0,
                max=1000.0,
                has_reset=True,
            ),
            identifier='GizmoMaxFadeOut'
        )

    def __reset_settings(self, viewport_api_id: str):
        settings = carb.settings.get_settings()
        for value in VIEWPORT_SETTINGS.__dict__.values():
            if isinstance(value, ViewportSetting):
                value.reset(settings)

        # Only reset renderer settings of current viewport
        menu_ctx = self.__menu_context.get(viewport_api_id)
        renderer_menu_item = menu_ctx.renderer_menu_item if menu_ctx else None
        if renderer_menu_item:
            renderer_menu_item.reset()

    def _show_viewport_preference(self) -> None:
        try:
            import omni.kit.window.preferences as preferences
            import asyncio

            async def focus_async():
                pref_window = ui.Workspace.get_window("Preferences")
                if pref_window:
                    pref_window.focus()

            page_title = "Viewport"
            inst = preferences.get_instance()
            if not inst:  # pragma: no cover
                carb.log_error("Preferences extension is not loaded yet")
                return None

            pages = preferences.get_page_list()
            for page in pages:
                if page.get_title() == page_title:
                    inst.select_page(page)
                    # Show the Window
                    inst.show_preferences_window()
                    # Force the tab to be the active/focused tab (this currently needs to be done in async)
                    asyncio.ensure_future(focus_async())
                    return page
            carb.log_error("Viewport Preferences page not found!")  # pragma: no cover
        except ImportError:  # pragma: no cover
            carb.log_error("omni.kit.window.preferences not enabled!")

        return None
