# Copyright (c) 2024, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

"""USD File interaction for Omniverse Kit.

:mod:`omni.kit.window.file` provides util functions to new/open/save/close USD files. It handles file picking dialog and prompt
for unsaved stage.
"""
__all__ = ["DialogOptions", "SaveOptionsDelegate", "OpenOptionsDelegate", "AppUI"]
import os
import carb.settings
import omni.ui as ui
from enum import Enum
from typing import List, Callable
from omni.kit.window.file_exporter import get_file_exporter, ExportOptionsDelegate
from omni.kit.window.file_importer import ImportOptionsDelegate
try:
    from omni.kit.widget.versioning import CheckpointHelper
    have_versioning = True
except ModuleNotFoundError:
    have_versioning = False
from .prompt_ui import Prompt
from .save_stage_ui import StageSaveDialog
from .style import get_style

SHOW_SAVE_OPTIONS = "/persistent/app/file/save/showSaveOptionsAutomatically"


class DialogOptions(Enum):
    """Enum for dialog options."""
    NONE = 0,
    """Show dialog using is-required logic"""
    FORCE = 1,
    """Force dialog to show and ignore is-required logic"""
    HIDE = 2,
    """Never show dialog"""


class SaveOptionsDelegate(ExportOptionsDelegate):
    """ Delegate class managing save options. """
    def __init__(self):
        super().__init__(
            build_fn=self._build_ui_impl,
            selection_changed_fn=lambda *_: self._build_ui_impl(),
            filename_changed_fn=lambda *_: self._build_ui_impl(),
            destroy_fn=self._destroy_impl
        )
        self._widget = None
        self._comment_model = ui.SimpleStringModel()
        self._include_session_layer_checkbox = None
        self._hint_container = None
        self._sub_begin_edit = None
        self._sub_end_edit = None
        self._show_include_session_layer_option = False
        self._other_options_widget = None

        settings = carb.settings.get_settings()
        self._versioning_enabled = settings.get_as_bool("exts/omni.kit.window.file/enable_versioning") or False

    def get_comment(self) -> str:
        """
        Return:
            str: Return the comment text.
        """
        if self._comment_model:
            return self._comment_model.get_value_as_string()
        return ""

    def include_session_layer(self) -> bool:
        """
        When doing save-as or save-flattened-as, this option
        can tell if it needs to keep session layers's change or
        flatten session layer's change also.
        Return:
            bool: Return whether to include session layer or not.
        """

        if self._include_session_layer_checkbox:
            return self._include_session_layer_checkbox.model.get_value_as_bool()

        return True

    @property
    def show_include_session_layer_option(self):
        """Get/set whether to show the include session layer option or not."""
        return self._show_include_session_layer_option

    @show_include_session_layer_option.setter
    def show_include_session_layer_option(self, value):
        self._show_include_session_layer_option = value
        if self._other_options_widget:
            self._other_options_widget.visible = value

    def _build_ui_impl(self):
        if not self._versioning_enabled:
            return

        folder_url = ""
        file_exporter = get_file_exporter()
        if file_exporter and file_exporter._dialog:
            folder_url = file_exporter._dialog.get_current_directory()

        self._widget = ui.Frame()
        if have_versioning:
            CheckpointHelper.is_checkpoint_enabled_with_callback(folder_url, self._build_options_box)

    def _build_option_checkbox(self, text, default_value, tooltip, identifier):
        with ui.VStack():
            ui.Spacer()
            with ui.HStack(height=0):
                checkbox = ui.CheckBox(width=14, height=14, style={"font_size": 16}, identifier=identifier)
                checkbox.model.set_value(default_value)
                ui.Spacer(width=4)
                label = ui.Label(text, alignment=ui.Alignment.LEFT)
                label.set_tooltip(tooltip)
            ui.Spacer()

        return checkbox

    def _build_options_box(self, server_url: str, checkpoint_enabled: bool):
        with self._widget:
            with ui.VStack(height=0, style=get_style()):
                if checkpoint_enabled:
                    ui.Label("Checkpoint comments:", height=20, alignment=ui.Alignment.LEFT_CENTER)
                    ui.Separator(height=5)
                    ui.Spacer(height=2)
                    with ui.ZStack():
                        with ui.HStack():
                            ui.StringField(self._comment_model, multiline=True, height=64, style_type_name_override="Field")
                        self._hint_container = ui.VStack()
                        with self._hint_container:
                            with ui.HStack():
                                ui.Label("Add checkpoint comments here.", height=20, style_type_name_override="Field.Hint")
                            ui.Spacer()
                        self._hint_container.visible = False

                    self._sub_begin_edit = self._comment_model.subscribe_begin_edit_fn(self._on_begin_edit)
                    self._sub_end_edit = self._comment_model.subscribe_end_edit_fn(self._on_end_edit)
                else:
                    ui.Label("This server does not support checkpoints.", height=20, alignment=ui.Alignment.CENTER, word_wrap=True)

                # OM-55838: Add option to support excluding session layer from flattening.
                self._other_options_widget = ui.VStack(height=0)
                with self._other_options_widget:
                    ui.Spacer(height=5)
                    ui.Separator(height=5)
                    ui.Label("Other Options:", height=20, alignment=ui.Alignment.LEFT_CENTER)
                    ui.Spacer(height=5)
                    self._include_session_layer_checkbox = self._build_option_checkbox(
                        "Include Session Layer", False,
                        "When this option is checked, it means it will include content\n"
                        "of session layer into the flattened stage.",
                        "include_session_layer"
                    )

                self._other_options_widget.visible = self.show_include_session_layer_option

    def _on_begin_edit(self, model):
        self._hint_container.visible = False

    def _on_end_edit(self, model: ui.AbstractValueModel):
        if self.get_comment():
            self._hint_container.visible = False
        else:
            self._hint_container.visible = True

    def _destroy_impl(self, _):
        self._comment_model = None
        self._hint_container = None
        self._widget = None
        self._sub_begin_edit = None
        self._sub_end_edit = None
        self._include_session_layer_checkbox = None


class OpenOptionsDelegate(ImportOptionsDelegate):
    """ Delegate class managing open options. """
    def __init__(self):
        super().__init__(
            build_fn=self._build_ui_impl,
            destroy_fn=self._destroy_impl
        )
        self._widget = None
        self._load_payload_checkbox = None

    def should_load_payload(self) -> bool:
        """
        Return:
            bool: Return True if payload should be loaded.
        """
        if self._load_payload_checkbox:
            return self._load_payload_checkbox.model.get_value_as_bool()
        return False

    def _build_ui_impl(self):
        self._widget = ui.Frame()
        with self._widget:
            with ui.VStack(height=0, style=get_style()):
                ui.Separator(height=5)
                ui.Spacer(height=2)
                with ui.HStack():
                    ui.Spacer(width=2)
                    self._load_payload_checkbox = ui.CheckBox(width=20, style_type_name_override="CheckBox")
                    self._load_payload_checkbox.model.set_value(True)
                    ui.Spacer(width=4)
                    ui.Label("Open Payloads", width=0, height=20, style_type_name_override="Label")
                    ui.Spacer()

    def _destroy_impl(self, _):
        self._load_payload_checkbox = None
        self._widget = None


class AppUI:
    """ Wrapper class for open/save prompts."""
    def __init__(self):
        self._open_stage_failed_prompt = None
        self._save_layers_failed_prompt = None
        self._save_stage_prompt = None

    def destroy(self):
        """Destructor."""
        if self._open_stage_failed_prompt:
            self._open_stage_failed_prompt.destroy()
        self._open_stage_failed_prompt = None
        if self._save_layers_failed_prompt:
            self._save_layers_failed_prompt.destroy()
        self._save_layers_failed_prompt = None
        if self._save_stage_prompt:
            self._save_stage_prompt.destroy()
        self._save_stage_prompt = None

    def save_root_and_sublayers(
        self, new_root_path: str,
        dirty_sublayers: List[str],
        on_save_done: Callable = None,
        dialog_options: int = DialogOptions.NONE,
        save_comment: str = "",
        allow_skip_sublayers: bool = False):
        """
        Save root and sub layers.

        Args:
            new_root_path (str): path to set the root layer.
            dirty_layers (List[str]): layer identifiers to save.
        Keyword Args:
            on_save_done (Callable): function to call after saving. Function Signature:
                on_save_done(result: bool, url: str) -> None
            dialog_options (:obj:`DialogOptions`): dialog options to prompt or not.
            save_comment (str): comment on the created checkpoint.
            allow_skip_sublayers (bool): True to skip sublayers.
        """
        import omni.usd

        stage = omni.usd.get_context().get_stage()
        if not stage:
            if on_save_done:
                on_save_done(False, "Save Failed: no stage opened")
            return

        def save_with_dialog():
            if self._save_stage_prompt:
                self._save_stage_prompt.destroy()
            self._save_stage_prompt = StageSaveDialog(
                enable_dont_save=allow_skip_sublayers,
                on_save_fn=lambda layers, comment: self._save_layers(
                    new_root_path, layers, on_save_done=on_save_done, checkpoint_comment=comment),
                on_dont_save_fn=lambda comment: self._dont_save_layers(
                    new_root_path, on_save_done=on_save_done, checkpoint_comment=comment),
                on_cancel_fn=lambda comment: self._cancel_save(new_root_path, checkpoint_comment=comment),
            )
            self._save_stage_prompt.show(dirty_sublayers)

        settings = carb.settings.get_settings()
        settings.set_default_bool(SHOW_SAVE_OPTIONS, False)
        show_stage_save_dialog = settings.get(SHOW_SAVE_OPTIONS)
        if dialog_options == DialogOptions.HIDE and not show_stage_save_dialog:
            self._save_layers(new_root_path, dirty_sublayers, on_save_done=on_save_done)
            return

        if len(dirty_sublayers) == 0:
            self._save_layers(new_root_path, [], on_save_done=on_save_done, checkpoint_comment=save_comment)
            return

        if dialog_options == DialogOptions.NONE:
            save_with_dialog()
            return

        if dialog_options == DialogOptions.FORCE \
             or (dialog_options == DialogOptions.HIDE and show_stage_save_dialog):
               save_with_dialog()
        else:
            self._save_layers(new_root_path, dirty_sublayers, on_save_done=on_save_done)

    def _save_layers(
        self, new_root_path, dirty_layers, on_save_done=None, create_checkpoint=True, checkpoint_comment=""
    ):
        import omni.client

        settings = carb.settings.get_settings()
        versioning_enabled = settings.get_as_bool("exts/omni.kit.window.file/enable_versioning") or False
        if versioning_enabled and create_checkpoint:
            omni.client.create_checkpoint(new_root_path, checkpoint_comment)

        def save_done_fn(result, err):
            if result:
                if versioning_enabled and create_checkpoint:
                    omni.client.create_checkpoint(new_root_path, checkpoint_comment)
            if on_save_done:
                on_save_done(result, err)

        omni.kit.window.file.save_layers(
            new_root_path, dirty_layers, save_done_fn, create_checkpoint, checkpoint_comment
        )

    def _dont_save_layers(self, new_root_path, on_save_done=None, checkpoint_comment=""):
        if new_root_path:
            self._save_layers(new_root_path, [], on_save_done=on_save_done, checkpoint_comment=checkpoint_comment)
        elif on_save_done:
            on_save_done(True, "")

    def _cancel_save(self, new_root_path, checkpoint_comment=""):
        if new_root_path:
            self._save_layers(new_root_path, [], None, checkpoint_comment=checkpoint_comment)

    def show_open_stage_failed_prompt(self, path):
        """
        Show open stage failed prompt with the given path.
        Args:
            path(str): The path to show the failed prompt with.
        """
        if not self._open_stage_failed_prompt:
            self._open_stage_failed_prompt = Prompt(
                f'{ui.get_custom_glyph_code("${glyphs}/exclamation.svg")} Open Stage Failed',
                "",
                ["OK"],
                [None],
            )
        self._open_stage_failed_prompt.set_text(
            f"Failed to open stage {os.path.basename(path)}. Please check console for error."
        )
        self._open_stage_failed_prompt.show()
        return self._open_stage_failed_prompt

    def show_save_layers_failed_prompt(self):
        """ Show save layers failed prompt. """
        if not self._save_layers_failed_prompt:
            self._save_layers_failed_prompt = Prompt(
                f'{ui.get_custom_glyph_code("${glyphs}/exclamation.svg")} Save Layer(s) Failed',
                "Failed to save layers. Please check console for error.",
                ["OK"],
                [None],
            )
        self._save_layers_failed_prompt.show()
        return self._save_layers_failed_prompt
