# Copyright (c) 2021-2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

# =================================== NOTE ====================================
# The APIs in this file are unfinished and may change in future releases
# Using these is at your own risk, and forward-compatability is not supported

from functools import partial
from pathlib import Path

import carb
import carb.settings
import omni.kit.commands
import omni.kit.ui
import omni.ui
import omni.usd
from omni.kit.window.filepicker import FilePickerDialog

LABEL_HEIGHT = 18
HORIZONTAL_SPACING = 4
LABEL_WIDTH = 200


class SettingsWidgetBuilder:

    checkbox_alignment = None
    checkbox_alignment_set = False

    @classmethod
    def get_checkbox_alignment(cls):
        if not cls.checkbox_alignment_set:
            settings = carb.settings.get_settings()
            cls.checkbox_alignment = settings.get("/ext/omni.kit.window.property/checkboxAlignment")
            cls.checkbox_alignment_set = True
        return cls.checkbox_alignment

    label_alignment = None
    label_alignment_set = False

    @classmethod
    def get_label_alignment(cls):
        if not cls.label_alignment_set:
            settings = carb.settings.get_settings()
            cls.label_alignment = settings.get("/ext/omni.kit.window.property/labelAlignment")
            cls.label_alignment_set = True
        return cls.label_alignment

    @classmethod
    def _restore_defaults(cls, path: str, button=None) -> None:
        omni.kit.commands.execute("RestoreDefaultXRSettingCommand", path=path)
        if button:
            button.visible = False

    @classmethod
    def _build_reset_button(cls, path) -> omni.ui.Rectangle:
        with omni.ui.VStack(width=0, height=0):
            omni.ui.Spacer()
            with omni.ui.ZStack(width=15, height=15):
                with omni.ui.HStack(style={"margin_width": 0}):
                    omni.ui.Spacer()
                    with omni.ui.VStack(width=0):
                        omni.ui.Spacer()
                        omni.ui.Rectangle(width=5, height=5, name="reset_invalid")
                        omni.ui.Spacer()
                    omni.ui.Spacer()
                btn = omni.ui.Rectangle(width=12, height=12, name="reset", tooltip="Click to reset value")
                btn.visible = False
                btn.set_mouse_pressed_fn(lambda x, y, m, w, p=path, b=btn: cls._restore_defaults(path, b))
            omni.ui.Spacer()

        return btn

    @staticmethod
    def _create_multi_float_drag_with_labels(model, labels, comp_count, **kwargs) -> None:
        RECT_WIDTH = 13
        SPACING = 4
        with omni.ui.ZStack():
            with omni.ui.HStack():
                omni.ui.Spacer(width=RECT_WIDTH)
                widget_kwargs = {"name": "multivalue", "h_spacing": RECT_WIDTH + SPACING}
                widget_kwargs.update(kwargs)
                omni.ui.MultiFloatDragField(model, **widget_kwargs)
            with omni.ui.HStack():
                for i in range(comp_count):
                    if i != 0:
                        omni.ui.Spacer(width=SPACING)
                    label = labels[i]
                    with omni.ui.ZStack(width=RECT_WIDTH + 1):
                        omni.ui.Rectangle(name="vector_label", style={"background_color": label[1]})
                        omni.ui.Label(label[0], name="vector_label", alignment=omni.ui.Alignment.CENTER)
                    omni.ui.Spacer()

    @staticmethod
    def _create_multi_int_drag_with_labels(model, labels, comp_count, **kwargs) -> None:
        RECT_WIDTH = 13
        SPACING = 4
        with omni.ui.ZStack():
            with omni.ui.HStack():
                omni.ui.Spacer(width=RECT_WIDTH)
                widget_kwargs = {"name": "multivalue", "h_spacing": RECT_WIDTH + SPACING}
                widget_kwargs.update(kwargs)
                omni.ui.MultiIntDragField(model, **widget_kwargs)
            with omni.ui.HStack():
                for i in range(comp_count):
                    if i != 0:
                        omni.ui.Spacer(width=SPACING)
                    label = labels[i]
                    with omni.ui.ZStack(width=RECT_WIDTH + 1):
                        omni.ui.Rectangle(name="vector_label", style={"background_color": label[1]})
                        omni.ui.Label(label[0], name="vector_label", alignment=omni.ui.Alignment.CENTER)
                    omni.ui.Spacer()

    @classmethod
    def createColorWidget(cls, model, comp_count=3, additional_widget_kwargs=None) -> omni.ui.HStack:
        with omni.ui.HStack(spacing=HORIZONTAL_SPACING) as widget:
            widget_kwargs = {"min": 0.0, "max": 1.0}
            if additional_widget_kwargs:
                widget_kwargs.update(additional_widget_kwargs)

            # TODO probably need to support "A" if comp_count is 4, but how many assumptions can we make?
            with omni.ui.HStack(spacing=4):
                cls._create_multi_float_drag_with_labels(
                    model=model,
                    labels=[("R", 0xFF5555AA), ("G", 0xFF76A371), ("B", 0xFFA07D4F)],
                    comp_count=comp_count,
                    **widget_kwargs,
                )
                omni.ui.ColorWidget(model, width=30, height=0)
            # cls._create_control_state(model)
        return widget

    @classmethod
    def createVecWidget(cls, model, range_min, range_max, comp_count=3, additional_widget_kwargs=None):
        widget_kwargs = {
            "min": range_min,
            "max": range_max,
            "labels": [("X", 0xFF5555AA), ("Y", 0xFF76A371), ("Z", 0xFFA07D4F), ("W", 0xFFFFFFFF)],
        }
        if additional_widget_kwargs:
            widget_kwargs.update(additional_widget_kwargs)
        cls._create_multi_float_drag_with_labels(
            model=model,
            comp_count=comp_count,
            **widget_kwargs,
        )
        return model

    @classmethod
    def createIVecWidget(cls, model, range_min, range_max, comp_count=3, additional_widget_kwargs=None):
        widget_kwargs = {
            "min": range_min,
            "max": range_max,
            "labels": [("X", 0xFF5555AA), ("Y", 0xFF76A371), ("Z", 0xFFA07D4F), ("W", 0xFFFFFFFF)],
        }
        if additional_widget_kwargs:
            widget_kwargs.update(additional_widget_kwargs)
        cls._create_multi_int_drag_with_labels(
            model=model,
            comp_count=comp_count,
            **widget_kwargs,
        )
        return model

    @classmethod
    def _create_label(cls, attr_name, path, tooltip="", additional_label_kwargs=None):

        alignment = omni.ui.Alignment.RIGHT if cls.get_label_alignment() == "right" else omni.ui.Alignment.LEFT
        label_kwargs = {
            "name": "label",
            "word_wrap": True,
            "width": LABEL_WIDTH,
            "height": LABEL_HEIGHT,
            "alignment": alignment,
        }

        # Tooltip always contains setting name. If there's a user-defined one, add that too
        if len(path):
            label_kwargs["tooltip"] = path
            if tooltip:
                label_kwargs["tooltip"] = f"{path}:\n {tooltip}"

        if additional_label_kwargs:
            label_kwargs.update(additional_label_kwargs)
        omni.ui.Label(attr_name, **label_kwargs)
        omni.ui.Spacer(width=5)

    @classmethod
    def createLabelMultiline(cls, text: str, **label_kwargs):
        """Create a new multiline label and populate it in the current UI context"""
        alignment = omni.ui.Alignment.LEFT
        label_kwargs = {"name": "label", "word_wrap": True, "alignment": alignment}
        omni.ui.Label(text, **label_kwargs)
        omni.ui.Spacer(width=5)

    @classmethod
    def createBoolWidget(cls, model, additional_widget_kwargs=None):
        widget = None
        with omni.ui.HStack():
            left_aligned = cls.get_checkbox_alignment() == "left"
            if not left_aligned:
                omni.ui.Spacer(width=10)
                omni.ui.Line(style={"color": 0x338A8777}, width=omni.ui.Fraction(1))
                omni.ui.Spacer(width=5)
            with omni.ui.VStack(style={"margin_width": 0}, width=10):
                omni.ui.Spacer()
                widget_kwargs = {"width": 10, "height": 0, "name": "greenCheck", "model": model}
                if additional_widget_kwargs:
                    widget_kwargs.update(additional_widget_kwargs)
                widget = omni.ui.CheckBox(**widget_kwargs)
                omni.ui.Spacer()
            if left_aligned:
                omni.ui.Spacer(width=10)
                omni.ui.Line(style={"color": 0x338A8777}, width=omni.ui.Fraction(1))
        return widget

    @classmethod
    def createFloatFieldWidget(cls, model, kwargs=None):

        widget_kwargs = {"model": model}
        if kwargs:
            widget_kwargs.update(kwargs)

        widget_kwargs.update(style={"secondary_color": 0xFF444444})
        widget = omni.ui.FloatField(name="models", **widget_kwargs)

        if "format" in widget_kwargs:
            widget.format = widget_kwargs["format"]
        return widget

    @classmethod
    def createFloatWidget(cls, model, range_min, range_max, step, kwargs=None):

        widget_kwargs = {"model": model}
        if kwargs:
            widget_kwargs.update(kwargs)
        widget_kwargs.update(style={"secondary_color": 0xFF444444})
        widget = omni.ui.FloatDrag(name="value", **widget_kwargs)

        if "format" in widget_kwargs:
            widget.format = widget_kwargs["format"]
        widget.min = range_min
        widget.max = range_max
        widget.step = step
        return widget

    @classmethod
    def createIntFieldWidget(cls, model, kwargs=None):

        widget_kwargs = {"model": model}
        if kwargs:
            widget_kwargs.update(kwargs)
        widget_kwargs.update(style={"secondary_color": 0xFF444444})
        widget = omni.ui.IntField(name="models", **widget_kwargs)

        return widget

    @classmethod
    def createIntWidget(cls, model, range_min, range_max, step, kwargs=None):
        widget_kwargs = {"model": model}
        if kwargs:
            widget_kwargs.update(kwargs)
        widget_kwargs.update(style={"secondary_color": 0xFF444444})
        widget = omni.ui.IntDrag(name="value", **widget_kwargs)
        widget.min = range_min
        widget.max = range_max
        widget.step = step

        return widget

    @classmethod
    def createAssetWidget(cls, model, additional_widget_kwargs=None):
        widget = AssetPicker(model)
        widget.build_ui(additional_widget_kwargs)
        return widget

    @classmethod
    def createPathWidget(cls, model, additional_widget_kwargs=None):
        widget = PathPicker(model)
        widget.build_ui(additional_widget_kwargs)
        return widget

    @classmethod
    def createPathOrAssetWidget(cls, model, additional_widget_kwargs=None):
        widget = PathOrAssetPicker(model)
        widget.build_ui(additional_widget_kwargs)
        return widget


class PathPicker:
    def __init__(self, model):
        self._model = model

    def build_ui(self, additional_widget_kwargs=None):
        with omni.ui.HStack():
            widget_kwargs = {"name": "models", "model": self._model}
            if additional_widget_kwargs:
                widget_kwargs.update(additional_widget_kwargs)
            self._path = omni.ui.StringField(**widget_kwargs)

            omni.ui.Spacer(width=3)

            def _set_primitive(model):
                selected = list(set(omni.usd.get_context().get_selection().get_selected_prim_paths()))
                if len(selected) == 1:
                    model.set_value(selected[0])

            omni.ui.Button(
                "Set",
                width=40,
                tooltip="Set from selected primitive",
                clicked_fn=lambda model=self._model: _set_primitive(model),
            )


class AssetPicker:
    def __init__(self, model):
        self.model = model
        self.item_filter_options = ["All Files (*)"]
        self.is_folder = False

    def _on_file_pick(self, dialog: FilePickerDialog, filename: str, dirname: str) -> None:
        """
        when a file or folder is selected in the dialog
        """
        path = ""
        if dirname:
            if self.is_folder:
                path = f"{dirname}"
            else:
                path = f"{dirname}/{filename}"
        elif filename:
            path = filename
        self.model.set_value(path)
        dialog.hide()

    def get_icon_path(self) -> Path:
        extension_path = (
            omni.kit.app.get_app().get_extension_manager().get_extension_path_by_module("omni.kit.xr.ui.window.profile")
        )
        icon_path = Path(extension_path).joinpath("icons")
        return icon_path

    def on_show_dialog(self, model, item_filter_options) -> None:
        heading = "Select Folder..." if self.is_folder else "Select File.."
        dialog: FilePickerDialog = FilePickerDialog(
            heading,
            apply_button_label="Select",
            click_apply_handler=lambda filename, dirname: self._on_file_pick(dialog, filename, dirname),
            item_filter_options=item_filter_options,
        )
        dialog.show()

    def build_ui(self, additional_widget_kwargs=None) -> None:
        with omni.ui.HStack():

            def assign_value(model, path: omni.ui.WidgetMouseDropEvent):
                model.set_value(path.mime_data)

            def drop_accept(url: str):
                # TODO support filtering by file extension
                if "." not in url:
                    # TODO dragging from stage view also result in a drop, which is a prim path not an asset path
                    # For now just check if dot presents in the url (indicating file extension).
                    return False
                return True

            with omni.ui.ZStack():
                widget_kwargs = {"name": "models", "model": self.model}
                if additional_widget_kwargs:
                    widget_kwargs.update(additional_widget_kwargs)
                value_widget = omni.ui.StringField(**widget_kwargs)

                # Drag and Drop behavior
                value_widget.set_accept_drop_fn(drop_accept)
                assign_value_p = partial(assign_value, self.model)
                value_widget.set_drop_fn(assign_value_p)

            style = {"image_url": str(self.get_icon_path().joinpath("small_folder.png")), "border_radius": 0}

            if "is_folder" in additional_widget_kwargs:
                self.is_folder = additional_widget_kwargs["is_folder"]

            omni.ui.Button(
                style=style,
                width=24,
                height=24,
                tooltip="Browse...",
                clicked_fn=lambda model=self.model: self.on_show_dialog(model, self.item_filter_options),
            )
            omni.ui.Spacer(width=3)


class PathOrAssetPicker:
    def _on_file_pick(self, dialog: FilePickerDialog, filename: str, dirname: str) -> None:
        """
        when a file or folder is selected in the dialog
        """
        path = ""
        if dirname:
            if self.is_folder:
                path = f"{dirname}"
            else:
                path = f"{dirname}/{filename}"
        elif filename:
            path = filename
        self.model.set_value(path)
        dialog.hide()

    def get_icon_path(self) -> Path:
        extension_path = (
            omni.kit.app.get_app().get_extension_manager().get_extension_path_by_module("omni.kit.xr.ui.window.profile")
        )
        icon_path = Path(extension_path).joinpath("icons")

        return icon_path

    def __init__(self, model):
        self.model = model
        self.item_filter_options = ["All Files (*)"]
        self.is_folder = False

    def on_show_dialog(self, model, item_filter_options) -> None:
        heading = "Select Folder..." if self.is_folder else "Select File.."
        dialog: FilePickerDialog = FilePickerDialog(
            heading,
            apply_button_label="Select",
            click_apply_handler=lambda filename, dirname: self._on_file_pick(dialog, filename, dirname),
            item_filter_options=item_filter_options,
        )
        dialog.show()

    def build_ui(self, additional_widget_kwargs=None) -> None:
        with omni.ui.HStack():

            def assign_value(model, path: omni.ui.WidgetMouseDropEvent):
                model.set_value(path.mime_data)

            def drop_accept(url: str):
                # TODO support filtering by file extension
                if "." not in url:
                    # TODO dragging from stage view also result in a drop, which is a prim path not an asset path
                    # For now just check if dot presents in the url (indicating file extension).
                    return False
                return True

            with omni.ui.ZStack():
                widget_kwargs = {"name": "models", "model": self.model}
                if additional_widget_kwargs:
                    widget_kwargs.update(additional_widget_kwargs)
                value_widget = omni.ui.StringField(**widget_kwargs)

                # Drag and Drop behavior
                value_widget.set_accept_drop_fn(drop_accept)
                assign_value_p = partial(assign_value, self.model)
                value_widget.set_drop_fn(assign_value_p)

            style = {"image_url": str(self.get_icon_path().joinpath("small_folder.png")), "border_radius": 0}

            if "is_folder" in additional_widget_kwargs:
                self.is_folder = additional_widget_kwargs["is_folder"]

            omni.ui.Button(
                style=style,
                width=24,
                height=24,
                tooltip="Browse...",
                clicked_fn=lambda model=self.model: self.on_show_dialog(model, self.item_filter_options),
            )

            omni.ui.Spacer(width=3)

            def _set_primitive(model):
                selected = list(set(omni.usd.get_context().get_selection().get_selected_prim_paths()))
                if len(selected) == 1:
                    model.set_value(selected[0])

            omni.ui.Button(
                "Set",
                width=40,
                tooltip="Set from selected primitive",
                clicked_fn=lambda model=self.model: _set_primitive(model),
            )
