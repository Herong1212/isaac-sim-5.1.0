# Copyright (c) 2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
from typing import Optional

from omni import ui
from omni.kit.environment.core import ENVIRONMENT_PRIM_ROOT, PlaySettings, SettingModel
from omni.kit.property.usd import PrimSelectionPayload
from omni.kit.window.property import PropertyWidget

from .groups import DateTimeGroup, EnvironmentOptionsGroup, LocationGroup, NotificationGroup, WeatherGroup


class EnvironmentPropertyWidget(PropertyWidget):
    def __init__(self):
        super().__init__("Environment")
        self._payload: Optional[PrimSelectionPayload] = None
        self._env_group = None
        self._date_time_group = None
        self._location_group = None
        self._weather_group = None
        self._notification_group = NotificationGroup()

        self._env_group = EnvironmentOptionsGroup(self._payload)
        self._date_time_group = DateTimeGroup()
        self._location_group = LocationGroup()
        self._weather_group = WeatherGroup()

        self._current_sky_type_model = SettingModel(PlaySettings.CURRENT_SKY_TYPE)
        self._current_sky_type_model.add_value_changed_fn(self._on_sky_type_changed)

    def destroy(self):
        self._env_group.destroy()
        self._date_time_group.destroy()
        self._location_group.destroy()
        self._weather_group.destroy()
        self._notification_group.destroy()

    def clean(self):
        pass

    def reset(self):
        pass

    def on_new_payload(self, payload: PrimSelectionPayload) -> bool:
        self._payload = payload
        if not self._payload or len(self._payload) == 0:
            return False

        # Only Environment prim selected, show property widgets
        used = True
        for prim_path in self._payload:
            if prim_path != ENVIRONMENT_PRIM_ROOT:
                used = False

        if used:
            self._env_group.on_new_payload(self._payload)

        return used

    def build_impl(self) -> None:
        with ui.VStack(height=0, spacing=10):
            # Called when creating prim property widgets
            self._env_group.build()
            self._date_time_group.build()
            self._location_group.build()
            self._weather_group.build()
            self._notification_group.build()

        self._on_sky_type_changed(self._current_sky_type_model)

    def _on_sky_type_changed(self, model: SettingModel) -> None:
        sky_type = model.as_string
        is_dynamic_sky = sky_type == "Dynamic"
        if self._date_time_group:
            self._date_time_group.visible = is_dynamic_sky
            self._location_group.visible = is_dynamic_sky
            self._weather_group.visible = is_dynamic_sky
            self._notification_group.visible = not is_dynamic_sky
