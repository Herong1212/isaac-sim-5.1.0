# Copyright (c) 2024, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
import carb.settings
import omni.ui as ui
from omni.kit.window.preferences import PreferenceBuilder, show_file_importer

DEFAULT_PREVIEW_SKELETON_SETTING_PATH = "/persistent/exts/omni.anim.retarget.preview/preview_stage"


def build_preview_preferences(pref_builder: PreferenceBuilder):

    def on_browse_button_fn(path, widget):
        """ Called when the user picks the Browse button. """
        show_file_importer(
        "Select skeleton stage",
        file_exts=[("*.usd, *.usda", "USD Files"), ("*", "All Files")],
        filename_url=path,
        click_apply_fn=lambda p=path, w=widget: on_file_pick(p, widget=w))

    def on_file_pick(full_path, widget):
        """ Called when the user accepts path in the Select dialog. """
        resolve_path = pref_builder.cleanup_slashes(full_path)
        settings = carb.settings.get_settings()
        settings.set(DEFAULT_PREVIEW_SKELETON_SETTING_PATH, resolve_path)
        widget.model.set_value(full_path)

    with ui.VStack():
        with ui.HStack(height=24):
            pref_builder.label("Default Skeleton")
            widget = ui.StringField(height=20)
            path = carb.settings.get_settings().get(DEFAULT_PREVIEW_SKELETON_SETTING_PATH)
            widget.model.set_value(path)
            resolve_path = pref_builder.cleanup_slashes(carb.tokens.get_tokens_interface().resolve(path))
            ui.Button(style={"image_url": "resources/icons/folder.png"},
                clicked_fn=lambda p=resolve_path, w=widget: on_browse_button_fn(p, w),
                width=24)
