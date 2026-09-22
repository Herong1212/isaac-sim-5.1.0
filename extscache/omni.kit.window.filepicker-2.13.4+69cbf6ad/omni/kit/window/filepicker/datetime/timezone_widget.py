# Copyright (c) 2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
import omni.ui as ui
from .models import ZoneModel


class TimezoneWidget:
    """
    a combox for common timezones.
    Keyword Args:
    model (ZoneModel): Widget model.
    width (int): Widget width. Default 80.
    """
    def __init__(self, model: ZoneModel = None, **kwargs):
        if model:
            self._model = model
        else:
            self._model = ZoneModel()

        width = kwargs.get("width", 80)
        self._timezones = self._get_pytz_timezones()
        self._timezone_combo = ui.ComboBox(0, *self._timezones, name="timezone", width=width)
        self._on_zone_changed(None)
        self._model.add_value_changed_fn(self._on_zone_changed)
        self._timezone_combo.model.add_item_changed_fn(self._on_combo_selected)

    def __del__(self):
        self.destroy()

    def destroy(self):
        self._model = None
        self._timezone_combo = None

    @property
    def model(self):
        return self._model

    def _on_zone_changed(self, model):
        index = self._timezones.index(str(self._model.timezone))
        self._timezone_combo.model.get_item_value_model().set_value(index)

    def _on_combo_selected(self, model, item):
        index = model.get_item_value_model().as_int
        self._set_timezone(index)

    def _get_pytz_timezones(self):
        try:
            import pytz
            return pytz.common_timezones
        except Exception:
            return ["UTC"]
        
    def _set_timezone(self, index):
        try:
            import pytz
            self._model.set_value(pytz.timezone(self._timezones[index]))
        except Exception:
            return