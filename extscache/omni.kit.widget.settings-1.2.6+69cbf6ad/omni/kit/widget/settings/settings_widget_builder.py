"""
Source for SettingsWidgetBuilder, AssetPicker.
"""
__all__ = ['LABEL_HEIGHT', 'HORIZONTAL_SPACING', 'LABEL_WIDTH', 'SettingsWidgetBuilder', 'AssetPicker']

import collections
from functools import partial
from pathlib import Path
from typing import Any, Optional, Tuple, Union

import carb
import carb.settings
import omni.kit.app
import omni.kit.commands
import omni.ui as ui

from .settings_model import SettingsComboItemModel, RadioButtonSettingModel

LABEL_HEIGHT = 18
HORIZONTAL_SPACING = 4
LABEL_WIDTH = 200


class SettingsWidgetBuilder:
    """
    Widget builder functions.
    """
    _checkbox_alignment = None
    _checkbox_alignment_set = False

    @staticmethod
    def _get_setting(setting_path: str, setting_name: str = "", default: Any = None) -> Any:
        """Get the configuration of an UI widget carb.settings. This method assumes the given "setting_path" points
        to a value that has the given "setting_name" setting lives aside with it as a sibling.

        Args:
            setting_path (str): The base setting path.
            setting_name (str): The setting name the query.
        Kwargs:
            default (Any): The value to return if the setting doesn't exist or is None.

        Return:
            (Any): Setting value.
        """
        # setting_path is pointing to the value of the setting, go one level up to get the other settings - e.g. itmes
        if setting_name:
            setting_path = setting_path.split("/")[:-1]
            setting_path.append(setting_name)
            setting_path = "/".join(setting_path)
        value = carb.settings.get_settings().get(setting_path)
        value = default if value is None else value
        return value

    @classmethod
    def get_checkbox_alignment(cls):
        """
        Get checkbox alignment from setting "/ext/omni.kit.window.property/checkboxAlignment" and return True/False
        """
        if not cls._checkbox_alignment_set:
            settings = carb.settings.get_settings()
            cls._checkbox_alignment = settings.get("/ext/omni.kit.window.property/checkboxAlignment")
            cls._checkbox_alignment_set = True
        return cls._checkbox_alignment

    _label_alignment = None
    _label_alignment_set = False

    @classmethod
    def get_label_alignment(cls):
        """
        Get label alignment from setting "/ext/omni.kit.window.property/labelAlignment" and return True/False
        """
        if not cls._label_alignment_set:
            settings = carb.settings.get_settings()
            cls._label_alignment = settings.get("/ext/omni.kit.window.property/labelAlignment")
            cls._label_alignment_set = True
        return cls._label_alignment

    @classmethod
    def _restore_defaults(cls, path: str, button=None) -> None:
        omni.kit.commands.execute("RestoreDefaultRenderSetting", path=path)
        if button:
            button.visible = False

    @classmethod
    def _build_reset_button(cls, path) -> ui.Rectangle:
        with ui.VStack(width=0, height=0):
            ui.Spacer()
            with ui.ZStack(width=15, height=15):
                with ui.HStack(style={"margin_width": 0}):
                    ui.Spacer()
                    with ui.VStack(width=0):
                        ui.Spacer()
                        ui.Rectangle(width=5, height=5, name="reset_invalid")
                        ui.Spacer()
                    ui.Spacer()
                btn = ui.Rectangle(width=12, height=12, name="reset", tooltip="Click to reset value", identifier=f"{path}_reset")
                btn.visible = False

            btn.set_mouse_pressed_fn(lambda x, y, m, w, p=path, b=btn: cls._restore_defaults(path, b))
            ui.Spacer()

        return btn

    @staticmethod
    def _create_multi_float_drag_with_labels(model, labels, comp_count, **kwargs) -> None:
        RECT_WIDTH = 13
        SPACING = 4
        with ui.ZStack():
            with ui.HStack():
                if labels:
                    ui.Spacer(width=RECT_WIDTH)
                    widget_kwargs = {"name": "multivalue", "h_spacing": RECT_WIDTH + SPACING}
                else:
                    widget_kwargs = {"name": "multivalue", "h_spacing": 3}

                widget_kwargs.update(kwargs)
                ui.MultiFloatDragField(model, **widget_kwargs)
            with ui.HStack():
                if labels:
                    for i in range(comp_count):
                        if i != 0:
                            ui.Spacer(width=SPACING)
                        label = labels[i]
                        with ui.ZStack(width=RECT_WIDTH + 1):
                            ui.Rectangle(name="vector_label", style={"background_color": label[1]})
                            ui.Label(label[0], name="vector_label", alignment=ui.Alignment.CENTER)
                        ui.Spacer()

    @staticmethod
    def _create_multi_int_drag_with_labels(model, labels, comp_count, **kwargs) -> None:
        RECT_WIDTH = 13
        SPACING = 4
        with ui.ZStack():
            with ui.HStack():
                if labels:
                    ui.Spacer(width=RECT_WIDTH)
                    widget_kwargs = {"name": "multivalue", "h_spacing": RECT_WIDTH + SPACING}
                else:
                    widget_kwargs = {"name": "multivalue", "h_spacing": 3}

                widget_kwargs.update(kwargs)
                ui.MultiIntDragField(model, **widget_kwargs)
            with ui.HStack():
                if labels:
                    for i in range(comp_count):
                        if i != 0:
                            ui.Spacer(width=SPACING)
                        label = labels[i]
                        with ui.ZStack(width=RECT_WIDTH + 1):
                            ui.Rectangle(name="vector_label", style={"background_color": label[1]})
                            ui.Label(label[0], name="vector_label", alignment=ui.Alignment.CENTER)
                        ui.Spacer()

    @classmethod
    def createColorWidget(cls, model, comp_count=3, additional_widget_kwargs: Optional[dict] = None) -> ui.HStack:
        """
        Create a three color floating-point widget.
        """
        with ui.HStack(spacing=HORIZONTAL_SPACING) as widget:
            widget_kwargs = {"min": 0.0, "max": 1.0}
            if additional_widget_kwargs:
                widget_kwargs.update(additional_widget_kwargs)

            # TODO probably need to support "A" if comp_count is 4, but how many assumptions can we make?
            with ui.HStack(spacing=4):
                cls._create_multi_float_drag_with_labels(
                    model=model,
                    labels=[("R", 0xFF5555AA), ("G", 0xFF76A371), ("B", 0xFFA07D4F)],
                    comp_count=comp_count,
                    **widget_kwargs,
                )
                ui.ColorWidget(model, width=30, height=0)
            # cls._create_control_state(model)
        return widget

    @classmethod
    def createVecWidget(cls, model, range_min, range_max, comp_count=3, additional_widget_kwargs: Optional[dict] = None):
        """
        Create a widget for multiple XYZW float values.
        """
        widget_kwargs = {"min": range_min, "max": range_max}
        if additional_widget_kwargs:
            widget_kwargs.update(additional_widget_kwargs)
        cls._create_multi_float_drag_with_labels(
            model=model,
            labels=[("X", 0xFF5555AA), ("Y", 0xFF76A371), ("Z", 0xFFA07D4F), ("W", 0xFFFFFFFF)],
            comp_count=comp_count,
            **widget_kwargs,
        )
        return model

    @classmethod
    def createDoubleArrayWidget(cls, model, range_min, range_max, comp_count=3, additional_widget_kwargs: Optional[dict] = None):
        """
        Create a widget for multiple double-precision floating-point numbers.
        """
        widget_kwargs = {"min": range_min, "max": range_max, "labels": None}
        if additional_widget_kwargs:
            widget_kwargs.update(additional_widget_kwargs)
        cls._create_multi_float_drag_with_labels(model=model, comp_count=comp_count, **widget_kwargs)
        return model

    @classmethod
    def createIntArrayWidget(cls, model, range_min, range_max, comp_count=3, additional_widget_kwargs: Optional[dict] = None):
        """
        Create a widget for multiple integer numbers.
        """
        widget_kwargs = {"min": range_min, "max": range_max, "labels": None}
        if additional_widget_kwargs:
            widget_kwargs.update(additional_widget_kwargs)
        cls._create_multi_int_drag_with_labels(model=model, comp_count=comp_count, **widget_kwargs)
        return model

    @staticmethod
    def _create_drag_or_slider(drag_widget, slider_widget, **kwargs):
        '''
        A drag_widget lets you click and drag (you can drag as far left or right on the screen as you like)
        You can double-click to manually enter a value

        A slider_widget lets you click and sets the value to where you clicked.
        You don't drag outside the screen space occupied by the widget.
        No double click support.
        You press Ctrl-Click to manually enter a value

        This method will use a slider_widget when the range is <100 and a slider otherwise
        '''
        if "min" in kwargs and "max" in kwargs:
            range_min = kwargs["min"]
            range_max = kwargs["max"]
            if range_max - range_min < 100:
                widget = slider_widget(name="value", **kwargs)
                if "hard_range" in kwargs and kwargs['hard_range']:
                    model = kwargs["model"]
                    model.set_range(range_min, range_max)
                return widget

            else:
                if "step" not in kwargs:
                    kwargs["step"] = max(0.1, (range_max - range_min) / 1000.0)
        else:
            if "step" not in kwargs:
                kwargs["step"] = 0.1

        # If range is too big or no range, don't use a slider
        widget = drag_widget(name="value", **kwargs)
        return widget

    @classmethod
    def _create_label(cls, attr_name, path, tooltip="", additional_label_kwargs=None):

        alignment = ui.Alignment.RIGHT if cls.get_label_alignment() == "right" else ui.Alignment.LEFT
        label_kwargs = {
            "name": "label",
            "word_wrap": True,
            "width": LABEL_WIDTH,
            "height": LABEL_HEIGHT,
            "alignment": alignment,
        }

        # Tooltip always contains setting name. If there's a user-defined one, add that too
        label_kwargs["tooltip"] = path
        if tooltip:
            label_kwargs["tooltip"] = f"{path} : {tooltip}"

        if additional_label_kwargs:
            label_kwargs.update(additional_label_kwargs)
        ui.Label(attr_name, **label_kwargs)
        ui.Spacer(width=5)

    @classmethod
    def createBoolWidget(cls, model, additional_widget_kwargs: Optional[dict] = None):
        """
        Create a boolean widget.
        """
        widget = None
        with ui.HStack():
            left_aligned = cls.get_checkbox_alignment() == "left"
            if not left_aligned:
                ui.Spacer(width=10)
                ui.Line(style={"color": 0x338A8777}, width=ui.Fraction(1))
                ui.Spacer(width=5)
            with ui.VStack(style={"margin_width": 0}, width=10):
                ui.Spacer()
                widget_kwargs = {"width": 10, "height": 0, "name": "greenCheck", "model": model}
                if additional_widget_kwargs:
                    widget_kwargs.update(additional_widget_kwargs)
                widget = ui.CheckBox(**widget_kwargs)
                ui.Spacer()
            if left_aligned:
                ui.Spacer(width=10)
                ui.Line(style={"color": 0x338A8777}, width=ui.Fraction(1))
        return widget

    @classmethod
    def createFloatWidget(cls, model, range_min, range_max, additional_widget_kwargs: Optional[dict] = None):
        """
        Create a floating point widget.
        """
        widget_kwargs = {"model": model}
        # only set range if range is valid (min < max)
        if range_min < range_max:
            widget_kwargs["min"] = range_min
            widget_kwargs["max"] = range_max
        if additional_widget_kwargs:
            widget_kwargs.update(additional_widget_kwargs)
        widget_kwargs.update(style={"secondary_color": 0xFF444444})
        return cls._create_drag_or_slider(ui.FloatDrag, ui.FloatSlider, **widget_kwargs)

    @classmethod
    def createIntWidget(cls, model, range_min, range_max, additional_widget_kwargs: Optional[dict] = None):
        """
        Create a integer widget.
        """
        widget_kwargs = {"model": model}  # This passes the model into the widget
        # only set range if range is valid (min < max)
        if range_min < range_max:
            widget_kwargs["min"] = range_min
            widget_kwargs["max"] = range_max
        if additional_widget_kwargs:
            widget_kwargs.update(additional_widget_kwargs)
        widget_kwargs.update(style={"secondary_color": 0xFF444444})
        return cls._create_drag_or_slider(ui.IntDrag, ui.IntSlider, **widget_kwargs)

    @classmethod
    def createAssetWidget(cls, model, additional_widget_kwargs: Optional[dict] = None):
        """
        Create widget for file asset with filepicker.
        """
        widget = AssetPicker(model)
        widget.build_ui(additional_widget_kwargs)
        return widget

    @classmethod
    def createRadiobuttonWidget(
            cls, model: RadioButtonSettingModel,
            setting_path: str = "", additional_widget_kwargs: Optional[dict] = None) -> omni.ui.RadioCollection:
        """
        Create a RadioButtons Setting widget.

        This function creates a Radio Buttons that shows a list of names that are connected with setting by path
        specified - "{setting_path}/items".

        Args:
            model: A RadioButtonSettingModel instance.
            setting_path: Path to the setting to show and edit.

        Return:
            (omni.ui.RadioCollection): A omni.ui.RadioCollection instance.
        """

        def _create_radio_button(_collection):
            extension_path = omni.kit.app.get_app().get_extension_manager().get_extension_path_by_module(__name__)
            icon_dir = Path(extension_path).joinpath("data").joinpath("icons").absolute()
            icon_style = {
                "image_url": str(Path(icon_dir, Path("radio_off.svg"))),
                ":checked": {"image_url": str(Path(icon_dir, Path("radio_on.svg")))},
            }
            kwargs = additional_widget_kwargs or {}
            radio_button = omni.ui.RadioButton(
                radio_collection=_collection,
                width=20,
                height=20,
                style=icon_style,
                **kwargs,
            )
            omni.ui.Label(f"{item}\t", alignment=omni.ui.Alignment.LEFT)
            return radio_button

        collection = omni.ui.RadioCollection(model=model)
        vertical = cls._get_setting(setting_path, "vertical", False)
        for item in model.items:
            stack = omni.ui.VStack() if vertical else omni.ui.HStack()
            with stack:
                _create_radio_button(collection)

        return collection

    @classmethod
    def createComboboxWidget(
            cls, setting_path: str, items: Union[list, dict, None] = None,
            setting_is_index: Optional[bool] = None, allow_non_items: Optional[bool] = False,
            additional_widget_kwargs: Optional[dict] = None
        ) -> Tuple[SettingsComboItemModel, ui.ComboBox]:
        """
        Create a Combo Setting widget.

        This function creates a combo box that shows a provided list of names and it is connected with setting by path
        specified. Underlying setting values are used from values of `items` dict.

        Args:
            setting_path: Path to the setting to show and edit.
            items: Can be either :py:obj:`dict` or :py:obj:`list`. For :py:obj:`dict` keys are UI displayed names, values are
                actual values set into settings. If it is a :py:obj:`list` UI displayed names are equal to setting values.
            setting_is_index:
                None - Detect type from setting_path value. If the type is int, set to True.
                True - setting_path value is index into items list (default)
                False - setting_path value is string in items list
            allow_non_items:
                False - Will log errors if the setting is changed to a value that is not in the items parameter.
                True  - Will allow values that are not in the items parameter.
        """
        name_to_value = None

        # Get items from toml settings
        if items is None:
            items = cls._get_setting(setting_path, "items",  [])

        # if we have a list, we want to synthesize a dict of type label: index
        if isinstance(items, list):
            # Auto detect if setting_is_index
            if setting_is_index is None:
                # This is default for backward compatibility
                setting_is_index = True

                # We don't use isinstance(setting_value, int) here - we need to consider bool case.
                if not type(cls._get_setting(setting_path)) is int:
                    setting_is_index = False

            # If the setting is index, we zip the key/value pairs as {key: index} in OrderedDict
            if setting_is_index:
                name_to_value = collections.OrderedDict(zip(items, range(0, len(items))))
            # otherwise the zip key/value pairs as {key: key} in regular dict (unordered)
            else:
                name_to_value = dict(zip(items, items))
        elif isinstance(items, dict):
            name_to_value = items
            # By definition dict is mapping a "MenuItem name" => "SettingValue" to control display order
            # If setting_is_index is True, warn as it must be turned off for SettingsComboItemModel to work.
            if setting_is_index:
                carb.log_info(f"createComboboxWidget(setting_path='{setting_path}', items, setting_is_index) called"
                              " with a dict for items and setting_is_index={setting_is_index}, forcing setting_is_index=False")
            setting_is_index = False
        else:
            carb.log_error(f"Unsupported type {type(items)} for items in create_setting_widget_combo")
            return None

        kwargs = additional_widget_kwargs or {}
        model = SettingsComboItemModel(setting_path, name_to_value, setting_is_index, allow_non_items=allow_non_items)
        widget = ui.ComboBox(model, **kwargs)
        # OM-91518: Fixed double slash in it's xpath as shown in inspector
        widget.identifier = setting_path.replace("/", "_")
        return widget, model


class AssetPicker:
    """
    AssetPicker class.
    """
    def _on_file_pick(self, dialog, filename: str, dirname: str):
        """
        When a file or folder is selected in the dialog.
        """
        path = ""
        if dirname:
            if self.is_folder:
                path = dirname
            else:
                path = f"{dirname}{filename}"
        elif filename:
            path = filename
        self.model.set_value(path)
        dialog.hide()

    @classmethod
    def get_icon_path(cls):
        """
        Get icon path for extension
        """
        extension_path = omni.kit.app.get_app().get_extension_manager().get_extension_path_by_module(__name__)
        icon_path = Path(extension_path).joinpath("data").joinpath("icons")
        return icon_path

    def __init__(self, model):
        """
        AssetPicker init function.
        """
        self.model = model
        self.item_filter_options = ["All Files (*)"]
        self.is_folder = False

    def on_show_dialog(self, model, item_filter_options):
        """
        Browse button clicked function.
        """
        try:
            from omni.kit.window.filepicker import FilePickerDialog

            heading = "Select Folder..." if self.is_folder else "Select File.."
            dialog = FilePickerDialog(
                heading,
                apply_button_label="Select",
                click_apply_handler=lambda filename, dirname: self._on_file_pick(dialog, filename, dirname),
                item_filter_options=item_filter_options,
            )
            dialog.show()
        except:
            carb.log_warn(f"Failed to import omni.kit.window.filepicker")

            pass

    def build_ui(self, additional_widget_kwargs: Optional[dict] = None):
        """
        Build UI for asset picker.
        """
        with ui.HStack():

            def assign_value(model, path: omni.ui.WidgetMouseDropEvent):
                model.set_value(path.mime_data)

            def drop_accept(url: str):
                # TODO support filtering by file extension
                if "." not in url:
                    # TODO dragging from stage view also result in a drop, which is a prim path not an asset path
                    # For now just check if dot presents in the url (indicating file extension).
                    return False
                return True

            with ui.ZStack():
                widget_kwargs = {"name": "models", "model": self.model}
                if additional_widget_kwargs:
                    widget_kwargs.update(additional_widget_kwargs)
                value_widget = ui.StringField(**widget_kwargs)
                value_widget.identifier = "AssetPicker_path"

                # Drag and Drop behaviour
                value_widget.set_accept_drop_fn(drop_accept)
                assign_value_p = partial(assign_value, self.model)
                value_widget.set_drop_fn(assign_value_p)

            ui.Spacer(width=3)

            style = {"image_url": str(self.get_icon_path().joinpath("small_folder.png"))}

            heading = "Select Folder..." if self.is_folder else "Select File.."
            ui.Button(
                style=style,
                width=20,
                tooltip="Browse...",
                clicked_fn=lambda model=self.model: self.on_show_dialog(model, self.item_filter_options),
                identifier="AssetPicker_select"
            )
            ui.Spacer(width=3)

            # Button to jump to the file in Content Window
            def locate_file(model):
                carb.log_verbose("locate file")
                # omni.kit.window.content_browser is an optional dependency
                try:
                    url = model.get_resolved_path()
                    if len(url) == 0:
                        carb.log_verbose("Returning...")
                        return
                    from omni.kit.window.content_browser import get_content_window

                    instance = get_content_window()
                    if instance:
                        instance.navigate_to(url)
                    else:
                        carb.log_warn(f"Failed to import omni.kit.window.content_browser")
                except Exception as e:
                    carb.log_warn(f"Failed to locate file: {e}")

            style["image_url"] = str(self.get_icon_path().joinpath("find.png"))
            ui.Button(
                style=style, width=20, tooltip="Locate File", clicked_fn=lambda model=self.model: locate_file(model),
                identifier="AssetPicker_locate"

            )
