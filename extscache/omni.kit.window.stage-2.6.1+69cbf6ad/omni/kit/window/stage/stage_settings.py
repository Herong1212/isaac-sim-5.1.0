# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
# Selection Watch implementation has been moved omni.kit.widget.stage.
# Import it here for keeping back compatibility.
import carb.settings
import omni.kit.usd.layers as layers

from .singleton import Singleton


SETTINGS_SHOW_UNDEFINED_PRIMS = "/persistent/ext/omni.kit.widget.stage/show_undefined_prims"
SETTINGS_SHOW_ABSTRACT_PRIMS = "/persistent/ext/omni.kit.widget.stage/show_abstract_prims"
SETTINGS_SHOW_PRIM_DISPLAYNAME = "/persistent/ext/omni.kit.widget.stage/show_prim_displayname"
SETTINGS_SHOW_INACTIVE_PRIMS = "/persistent/ext/omni.kit.widget.stage/show_inactive_prims"
SETTINGS_KEEP_CHILDREN_ORDER = "/persistent/ext/omni.usd/keep_children_order"


@Singleton
class StageSettings:
    def __init__(self):
        super().__init__()
        self._settings = carb.settings.get_settings()
        self._settings.set_default_bool(SETTINGS_SHOW_PRIM_DISPLAYNAME, False)
        self._settings.set_default_bool(layers.SETTINGS_AUTO_RELOAD_NON_SUBLAYERS, False)
        self._settings.set_default_bool(SETTINGS_KEEP_CHILDREN_ORDER, False)

    @property
    def show_prim_displayname(self):
        return self._settings.get_as_bool(SETTINGS_SHOW_PRIM_DISPLAYNAME)

    @show_prim_displayname.setter
    def show_prim_displayname(self, enabled: bool):
        self._settings.set(SETTINGS_SHOW_PRIM_DISPLAYNAME, enabled)

    @property
    def auto_reload_prims(self):
        return self._settings.get_as_bool(layers.SETTINGS_AUTO_RELOAD_NON_SUBLAYERS)

    @auto_reload_prims.setter
    def auto_reload_prims(self, enabled: bool):
        self._settings.set(layers.SETTINGS_AUTO_RELOAD_NON_SUBLAYERS, enabled)

    @property
    def should_keep_children_order(self):
        return self._settings.get_as_bool(SETTINGS_KEEP_CHILDREN_ORDER)

    @should_keep_children_order.setter
    def should_keep_children_order(self, value):
        self._settings.set(SETTINGS_KEEP_CHILDREN_ORDER, value)

    @property
    def show_undefined_prims(self):
        return self._settings.get_as_bool(SETTINGS_SHOW_UNDEFINED_PRIMS)

    @show_undefined_prims.setter
    def show_undefined_prims(self, value):
        self._settings.set(SETTINGS_SHOW_UNDEFINED_PRIMS, value)

    @property
    def show_abstract_prims(self):
        show_abstract_prims = self._settings.get(SETTINGS_SHOW_ABSTRACT_PRIMS)
        # Default value should be True if the persistent setting is not set by user
        if show_abstract_prims is None:
            return True
        return bool(show_abstract_prims)
    @show_abstract_prims.setter
    def show_abstract_prims(self, value):
        self._settings.set(SETTINGS_SHOW_ABSTRACT_PRIMS, value)

    @property
    def show_inactive_prims(self):
        show_inactive_prims = self._settings.get(SETTINGS_SHOW_INACTIVE_PRIMS)
        # Default value should be True if the persistent setting is not set by user
        if show_inactive_prims is None:
            return True
        return bool(show_inactive_prims)

    @show_inactive_prims.setter
    def show_inactive_prims(self, value):
        self._settings.set(SETTINGS_SHOW_INACTIVE_PRIMS, value)
