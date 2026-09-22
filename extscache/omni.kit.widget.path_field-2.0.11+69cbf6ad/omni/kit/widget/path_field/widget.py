# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
import platform
import sys, os
import omni.ui as ui

from .model import PathFieldModel
from .style import UI_STYLES


class PathField:
    """
    Main class for the PathField widget. This widget is a UI alternative to omni.ui.StringField
    for navigating tree views with the keyboard. As the user navigates the tree using TAB,
    Backspace, and Arrow keys, they are constantly provided branching options via auto-filtered
    tooltips.

    Args:
        None

    Keyword Args:
        apply_path_handler (Callable): This function is called when the user hits Enter on the input
            field, signaling that they want to apply the path. This handler is expected to update
            the caller's app accordingly. Function signature: void apply_path_handler(path: str)
        branching_options_handler (Callable): This function is required to provide a list of possible
            branches whenever prompted with a path.  For example, if path = "C:", then the list of values
            produced might be ["Program Files", "temp", ..., "Users"]. Function signature:
            list(str) branching_options_provider(path: str, callback: func)
        separator (str): Character used to split a path into list of branches. Default '/'.
        modal (bool): Used for modal window. Default False.
        begin_edit_handler (callable): A callback for path string field begin edit. Default None.

    """

    def __init__(self, **kwargs):
        """Constructor for the PathField class."""
        import carb.settings

        self._scrolling_frame = None
        self._input_frame = None
        self._path = None
        self._path_model = None
        # OM-49484: Add subscription to begin edit and apply callback, for example we could add callback to cancel
        #   initial navigation upon user edit
        self._sub_begin_edit = None
        self._breadcrumbs = []

        self._theme = carb.settings.get_settings().get_as_string("/persistent/app/window/uiStyle") or "NvidiaDark"
        self._style = UI_STYLES[self._theme]
        self._apply_path_handler = kwargs.get("apply_path_handler", None)
        self._branching_options_handler = kwargs.get("branching_options_handler", None)
        self._begin_edit_handler = kwargs.get("begin_edit_handler", None)
        self._branching_options_provider = kwargs.get("branching_options_provider", None)  # OBSOLETE
        self._separator = kwargs.get("separator", "/")
        self._prefix_separator = kwargs.get("prefix_separator", None)
        self._modal = kwargs.get("modal", False)
        self._build_ui()

    @property
    def path(self) -> str:
        """Gets the current path as entered in the field box.

        Returns:
            str: The current path."""
        return self._path

    def _parse_path(self, full_path: str):
        if not full_path:
            return None, None
        prefix, path = "", full_path
        if self._prefix_separator:
            splits = full_path.split(self._prefix_separator, 1)
            if len(splits) == 2:
                prefix = f"{splits[0]}{self._prefix_separator}"
                path = splits[1]
        return prefix, path

    def set_path(self, full_path: str):
        """Sets the path.

        Args:
            full_path (str): The full path name to set."""
        if not full_path:
            return
        prefix, path = self._parse_path(full_path)
        # Make sure path string is properly formatted - it should end with
        # exactly 1 copy of the separator character.
        if path:
            path = f"{path.rstrip(self._separator)}{self._separator}"
        self._path = f"{prefix}{path}"
        self._update_breadcrumbs(self._path)

    def _build_ui(self):
        # Use a scrolling frame to prevent long paths from exploding width inut box
        self._scrolling_frame = ui.ScrollingFrame(
            horizontal_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_ALWAYS_OFF,
            vertical_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_ALWAYS_OFF,
            style=self._style,
            style_type_name_override="ScrollingFrame",
        )
        with self._scrolling_frame:
            self._build_input_field()

    def _build_input_field(self):
        self._path_model = PathFieldModel(
            self._scrolling_frame,
            self._theme,
            show_max_suggestions=10,
            apply_path_handler=self._apply_path_handler,
            branching_options_handler=self._branching_options_handler,
            current_path_provider=lambda: self._path or "",
            modal=self._modal,
        )
        self._sub_begin_edit = self._path_model.subscribe_begin_edit_fn(self._on_begin_edit)
        with ui.ZStack(style=self._style):
            ui.Rectangle()
            with ui.VStack():
                ui.Spacer(height=4)
                with ui.HStack(height=16):
                    ui.Spacer(width=3)
                    self._input_frame = ui.Frame()
                    field = ui.StringField(
                        self._path_model, style_type_name_override="InputField", identifier="filepicker_directory_path"
                    )

        self._update_breadcrumbs(self._path)

    def _on_begin_edit(self, model: PathFieldModel):
        if self._begin_edit_handler:
            self._begin_edit_handler()

    def _update_breadcrumbs(self, path: str):
        def on_breadcrumb_clicked(button: ui.RadioButton):
            if button and self._apply_path_handler:
                self._apply_path_handler(button.name)

        def create_breadcrumb(label: str, path: str):
            breadcrumb = ui.Button(text="", style_type_name_override="BreadCrumb")
            # HACK Alert: We're hijacking the name attr to store the fullpath.
            # Alternatively subclass from ui.Button and add a fullpath attr.
            breadcrumb.text = label
            breadcrumb.name = path
            breadcrumb.set_clicked_fn(lambda b=breadcrumb: on_breadcrumb_clicked(b)),
            separator = ui.Label(self._separator, style_type_name_override="BreadCrumb.Label")
            return (breadcrumb, separator)

        self._breadcrumbs.clear()
        prefix, path = self._parse_path(path)
        accum_path = ""

        with self._input_frame:
            with ui.HStack(width=0, spacing=0, style=self._style):
                ui.Spacer(width=5)
                if prefix:
                    accum_path += prefix
                    self._breadcrumbs.append(create_breadcrumb(accum_path, accum_path))
                    _, separator = self._breadcrumbs[-1]
                    separator.visible = False
                if path:
                    for token in path.rstrip(self._separator).split(self._separator):
                        accum_path += token
                        self._breadcrumbs.append(create_breadcrumb(token, accum_path))
                        accum_path += self._separator

        # For extremely long paths, scroll to the last breadcrumb
        if self._breadcrumbs:
            breadcrumb, _ = self._breadcrumbs[-1]
            breadcrumb.scroll_here_x(0)

    def destroy(self):
        """Destructor."""
        if self._path_model:
            self._path_model.destroy()
        self._path_model = None
        self._sub_begin_edit = None
        self._breadcrumbs = None
        self._input_frame = None
        self._scrolling_frame = None
