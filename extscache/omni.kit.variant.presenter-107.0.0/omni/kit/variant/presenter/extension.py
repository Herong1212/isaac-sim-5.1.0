## Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##

import weakref
from functools import partial

import carb.settings
import omni.ext
import omni.kit.ui
import omni.ui as ui

from .window import VariantPresenterWindow

SETTING_SHOW_STARTUP = "/exts/omni.kit.variant.presenter/showStartup"
_variant_presenter_model = None
_variant_presenter_window = None


def get_model():
    return _variant_presenter_model if not _variant_presenter_model else _variant_presenter_model()


def get_window():
    return _variant_presenter_window if not _variant_presenter_window else _variant_presenter_window()


class VariantPresenterExtension(omni.ext.IExt):
    """The entry point for the extension"""

    WINDOW_NAME = "Variant Presenter"
    MENU_PATH = f"Tools/Variants/{WINDOW_NAME}"

    def on_startup(self):
        self._presenter_window = None
        self._menu = None
        ui.Workspace.set_show_window_fn(self.WINDOW_NAME, partial(self.show_window, None))
        show_startup = carb.settings.get_settings().get(SETTING_SHOW_STARTUP)
        editor_menu = omni.kit.ui.get_editor_menu()
        self._menu = None
        if editor_menu:
            self._menu = editor_menu.add_item(
                f"{self.MENU_PATH}",
                self.show_window,
                priority=21,
                toggle=True,
                value=show_startup,
            )
        if show_startup:
            ui.Workspace.show_window(self.WINDOW_NAME)

    def on_shutdown(self):
        ui.Workspace.set_show_window_fn(self.WINDOW_NAME, None)
        if self._menu:
            editor_menu = omni.kit.ui.get_editor_menu()
            if editor_menu:
                editor_menu.remove_item(f"{self.MENU_PATH}")
        self._menu = None
        if self._presenter_window:
            self._presenter_window.set_visibility_changed_listener(None)
            self._presenter_window.destroy()
        self._presenter_window = None

    def show_window(self, menu, value):
        global _variant_presenter_model
        global _variant_presenter_window
        if value:
            self._presenter_window = VariantPresenterWindow()
            self._presenter_window.set_visibility_changed_listener(self._visibility_changed_fn)
            self._presenter_window._load_model()
            _variant_presenter_model = weakref.ref(self._presenter_window._model)
            _variant_presenter_window = weakref.ref(self._presenter_window)
        else:
            if self._presenter_window:
                self._presenter_window.destroy()
            self._presenter_window = None

    def _visibility_changed_fn(self, visible):
        if self._menu:
            omni.kit.ui.get_editor_menu().set_value(f"{self.MENU_PATH}", visible)
