# Copyright (c) 2021-2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

__all__ = ["SynthDataMenuContainer"]


from omni.kit.viewport.menubar.core import (
    ComboBoxModel,
    ComboBoxItem,
    ComboBoxMenuDelegate,
    CheckboxMenuDelegate,
    IconMenuDelegate,
    SliderMenuDelegate,
    ViewportMenuContainer,
    ViewportMenuItem,
    ViewportMenuSeparator
)
from .SyntheticData import SyntheticData
from .visualizer_window import VisualizerWindow

import carb
import omni.ui as ui

from pathlib import Path
import weakref


ICON_PATH = Path(carb.tokens.get_tokens_interface().resolve("${omni.syntheticdata}")).joinpath("data")
UI_STYLE = {"Menu.Item.Icon::SyntheticData": {"image_url": str(ICON_PATH.joinpath("sensor_icon.svg"))}}


class SensorAngleModel(ui.AbstractValueModel):
    def __init__(self, getter, setter, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__getter = getter
        self.__setter = setter

    def destroy(self):
        self.__getter = None
        self.__setter = None

    def get_value_as_float(self) -> float:
        return self.__getter()

    def get_value_as_int(self) -> int:
        return int(self.get_value_as_float())

    def set_value(self, value):
        value = float(value)
        if self.get_value_as_float() != value:
            self.__setter(value)
            self._value_changed()


class SensorVisualizationModel(ui.AbstractValueModel):
    def __init__(self, sensor: str, visualizer_window, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__sensor = sensor
        self.__visualizer_window = visualizer_window

    def get_value_as_bool(self) -> bool:
        try:
            return bool(self.__sensor in self.__visualizer_window.visualization_activation)
        except:
            return False

    def get_value_as_int(self) -> int:
        return 1 if self.get_value_as_bool() else 0

    def set_value(self, enabled):
        enabled = bool(enabled)
        if self.get_value_as_bool() != enabled:
            self.__visualizer_window.on_sensor_item_clicked(enabled, self.__sensor)
            self._value_changed()

    def sensor(self):
        return self.__sensor

class MenuContext:
    def __init__(self, viewport_api):
        self.__visualizer_window = VisualizerWindow(f"{viewport_api.id}", viewport_api)
        self.__hide_on_click = False
        self.__sensor_models = set()

    def destroy(self):
        self.__sensor_models = set()
        self.__visualizer_window.close()
    
    @property
    def hide_on_click(self) -> bool:
        return self.__hide_on_click

    def add_render_settings_items(self):
        render_product_combo_model = self.__visualizer_window.render_product_combo_model
        if render_product_combo_model:
            ViewportMenuItem(
                "RenderProduct",
                delegate=ComboBoxMenuDelegate(model=render_product_combo_model),
                hide_on_click=self.__hide_on_click,
            )

        render_var_combo_model = self.__visualizer_window.render_var_combo_model
        if render_var_combo_model:
            ViewportMenuItem(
                "RenderVar",
                delegate=ComboBoxMenuDelegate(model=render_var_combo_model),
                hide_on_click=self.__hide_on_click,
            )

    def add_angles_items(self):
        render_var_combo_model = self.__visualizer_window.render_var_combo_model
        if render_var_combo_model:
            ViewportMenuItem(
                name="Angle",
                hide_on_click=self.__hide_on_click,
                delegate=SliderMenuDelegate(
                    model=SensorAngleModel(render_var_combo_model.get_combine_angle,
                                           render_var_combo_model.set_combine_angle),
                    min=-100.0,
                    max=100.0,
                    tooltip="Set Combine Angle",
                ),
            )

            ViewportMenuItem(
                name="X",
                hide_on_click=self.__hide_on_click,
                delegate=SliderMenuDelegate(
                    model=SensorAngleModel(render_var_combo_model.get_combine_divide_x,
                                           render_var_combo_model.set_combine_divide_x),
                    min=-100.0,
                    max=100.0,
                    tooltip="Set Combine Divide X",
                ),
            )

            ViewportMenuItem(
                name="Y",
                hide_on_click=self.__hide_on_click,
                delegate=SliderMenuDelegate(
                    model=SensorAngleModel(render_var_combo_model.get_combine_divide_y,
                                           render_var_combo_model.set_combine_divide_y),
                    min=-100.0,
                    max=100.0,
                    tooltip="Set Combine Divide Y",
                ),
            )

    def add_sensor_selection(self):
        for sensor_label, sensor in SyntheticData.get_registered_visualization_template_names_for_display():
            model = SensorVisualizationModel(sensor, self.__visualizer_window)
            self.__sensor_models.add(model)
            ViewportMenuItem(
                name=sensor_label,
                hide_on_click=self.__hide_on_click,
                delegate=CheckboxMenuDelegate(model=model, tooltip=f'Enable "{sensor}" visualization')
            )
            if SyntheticData.get_visualization_template_name_default_activation(sensor):
                model.set_value(True)

    def clear_all(self, *args, **kwargs):
        for smodel in self.__sensor_models:
            smodel.set_value(False)
        
    def set_as_default(self, *args, **kwargs):
        for smodel in self.__sensor_models:
            SyntheticData.set_visualization_template_name_default_activation(smodel.sensor(), smodel.get_value_as_bool())

    def reset_to_default(self, *args, **kwargs):
        default_sensors = []
        for _, sensor in SyntheticData.get_registered_visualization_template_names_for_display():
            if SyntheticData.get_visualization_template_name_default_activation(sensor):
                    default_sensors.append(sensor)
        for smodel in self.__sensor_models:
            smodel.set_value(smodel.sensor() in default_sensors)
                
    def show_window(self, *args, **kwargs):
        self.__visualizer_window.toggle_enable_visualization()
        
class SynthDataMenuContainer(ViewportMenuContainer):
    def __init__(self):
        super().__init__(name="SyntheticData",
                         visible_setting_path="/exts/omni.syntheticdata/menubar/visible",
                         order_setting_path="/exts/omni.syntheticdata/menubar/order",
                         delegate=IconMenuDelegate("SyntheticData"), # tooltip="Synthetic Data Sensors"),
                         style=UI_STYLE)
        self.__menu_context: Dict[str, MenuContext] = {}
        
    def __del__(self):
        self.destroy()

    def destroy(self):
        for menu_ctx in self.__menu_context.values():
            menu_ctx.destroy()
        self.__menu_context = {}
        super().destroy()

    def build_fn(self, desc: dict):
        viewport_api = desc.get("viewport_api")
        if not viewport_api:
            return
        viewport_api_id = viewport_api.id
        menu_ctx = self.__menu_context.get(viewport_api_id)
        if menu_ctx:
            menu_ctx.destroy()
        menu_ctx = MenuContext(viewport_api)
        self.__menu_context[viewport_api_id] = menu_ctx
        
        with self:
            menu_ctx.add_render_settings_items()

            ViewportMenuSeparator()
            menu_ctx.add_angles_items()

            ViewportMenuSeparator()
            menu_ctx.add_sensor_selection()

            if carb.settings.get_settings().get_as_bool("/exts/omni.syntheticdata/menubar/showSensorDefaultButton"):
                ViewportMenuSeparator()
                ViewportMenuItem(name="Set as default", hide_on_click=menu_ctx.hide_on_click, onclick_fn=menu_ctx.set_as_default)
                ViewportMenuItem(name="Reset to default", hide_on_click=menu_ctx.hide_on_click, onclick_fn=menu_ctx.reset_to_default)

            ViewportMenuSeparator()
            ViewportMenuItem(name="Clear All", hide_on_click=menu_ctx.hide_on_click, onclick_fn=menu_ctx.clear_all)
            ViewportMenuItem(name="Show Window", hide_on_click=menu_ctx.hide_on_click, onclick_fn=menu_ctx.show_window)           

        super().build_fn(desc)

    def clear_all(self):
        for menu_ctx in self.__menu_context.values():
            menu_ctx.clear_all()
