import asyncio
import re
from typing import List
import carb
from carb.eventdispatcher import get_eventdispatcher
import carb.settings
import omni.kit.app
import omni.ui as ui
from .models.prim_model import PrimModel
from .layer_model import LayerModel
from .link_delegate import LayerLinkDelegate, PrimLinkDelegate
from omni.kit.window.file import DialogOptions
from omni.kit.menu.utils import MenuHelperExtension


class LayerLinkWindow(MenuHelperExtension):  # pragma: no cover
    WINDOW_NAME = "Layer Linking"
    MENU_GROUP = "Window"

    def __init__(self):
        self._window = None
        self._prims_widget = None
        self._layerlink_widget = None
        self._stage_centric = True
        ui.Workspace.set_show_window_fn(LayerLinkWindow.WINDOW_NAME, self.show_window)
        self.menu_startup(LayerLinkWindow.WINDOW_NAME, LayerLinkWindow.WINDOW_NAME, LayerLinkWindow.MENU_GROUP)

    def __del__(self):
        self.destroy()

    def destroy(self):
        ui.Workspace.set_show_window_fn(LayerLinkWindow.WINDOW_NAME, None)
        self.menu_shutdown()
        self._clear()

    def _clear(self):
        if self._prims_widget:
            self._prims_widget.destroy()
            self._prims_widget = None

        if self._layerlink_widget:
            self._layerlink_widget.destroy()
            self._layerlink_widget = None

        if self._window:
            self._window.destroy()
            self._window = None

    async def _destroy_window_async(self):
        # wait one frame, this is due to the one frame defer
        # in Window::_moveToMainOSWindow()
        await omni.kit.app.get_app().next_update_async()
        self._clear()

    def _visiblity_changed_fn(self, visible):
        self.menu_refresh()
        if not visible:
            # Destroy the window, since we are creating new window
            # in show_window
            asyncio.ensure_future(self._destroy_window_async())

    def show_window(self, value):
        if value:
            self._build_ui()
            self._window.set_visibility_changed_fn(self._visiblity_changed_fn)
        elif self._window:
            self._window.visible = False

    def _set_centric(self, value):
        self._stage_centric = value
        self._window.frame.rebuild()

    def _build_ui(self):
        self._window = ui.Window(
            LayerLinkWindow.WINDOW_NAME, width=600, height=400,
            flags=ui.WINDOW_FLAGS_NO_SCROLLBAR | ui.WINDOW_FLAGS_MENU_BAR,
        )

        with self._window.menu_bar:
            with ui.Menu("File"):
                ui.MenuItem(
                    "Load",
                    triggered_fn=lambda: omni.kit.window.file.open()
                )
                ui.MenuItem(
                    "Save",
                    triggered_fn=lambda: omni.kit.window.file.save(dialog_options=DialogOptions.HIDE),
                )
            with ui.Menu("Window"):
                ui.MenuItem(
                    "Stage centric linking",
                    triggered_fn=lambda: self._set_centric(True)
                )
                ui.MenuItem(
                    "Layer centric linking",
                    triggered_fn=lambda: self._set_centric(False),
                )

        """Creates all the widgets in the window"""
        self._style = {
            "Button::filter": {"background_color": 0x0, "margin": 0},
            "Button::options": {"background_color": 0x0, "margin": 0},
            "Button::visibility": {"background_color": 0x0, "margin": 0, "margin_width": 1},
            "Button::visibility:checked": {"background_color": 0x0},
            "Button::visibility:hovered": {"background_color": 0x0},
            "Button::visibility:pressed": {"background_color": 0x0},
            "Label::search": {"color": 0xFF808080, "margin_width": 4},
            "TreeView": {
                "background_color": 0xFF23211F,
                "background_selected_color": 0x664F4D43,
                "secondary_selected_color": 0x0,
                "border_width": 1.5,
            },
            "TreeView.ScrollingFrame": {"background_color": 0xFF23211F},
            "TreeView.Header": {"background_color": 0xFF343432, "color": 0xFFCCCCCC, "font_size": 12},
            "TreeView.Image::object_icon_grey": {"color": 0x80FFFFFF},
            "TreeView.Image:disabled": {"color": 0x60FFFFFF},
            "TreeView.Item": {"color": 0xFF8A8777},
            "TreeView.Item:disabled": {"color": 0x608A8777},
            "TreeView.Item::object_name_grey": {"color": 0xFF4D4B42},
            "TreeView.Item::object_name_missing": {"color": 0xFF6F72FF},
            "TreeView.Item:selected": {"color": 0xFF23211F},
            "TreeView:selected": {"background_color": 0xFF8A8777},
            "TreeView:drop": {
                "background_color": ui.color.shade(ui.color("#34C7FF3B")),
                "background_selected_color": ui.color.shade(ui.color("#34C7FF3B")),
                "border_color": ui.color.shade(ui.color("#2B87AA")),
            },
            "Splitter": {"background_color": 0xFFE0E0E0, "margin_width": 2},
            "Splitter:hovered": {"background_color": 0xFF00707B},
            "Splitter:pressed": {"background_color": 0xFF00003B},
        }

        self._window.frame.set_build_fn(self._on_frame_built)
        self._window.frame.rebuild()

    def _on_frame_built(self):
        usd_context = omni.usd.get_context()
        stage = usd_context.get_stage()

        with self._window.frame:
            with ui.HStack(style=self._style):
                with ui.ZStack(width=0):
                    with ui.HStack():
                        if self._stage_centric:
                            self._prims_widget = PrimsWidget(usd_context, stage)
                        else:
                            self._layerlink_widget = LayerLinkWidget(usd_context, stage)
                        ui.Spacer(width=2)

                    with ui.Placer(offset_x=300, draggable=True, drag_axis=ui.Axis.X):
                        ui.Rectangle(width=4, style_type_name_override="Splitter")

                if self._stage_centric:
                    self._layerlink_widget = LayerLinkWidget(usd_context, stage)
                else:
                    self._prims_widget = PrimsWidget(usd_context, stage)

                self._prims_widget.set_layerlink_widget(self._layerlink_widget)
                self._layerlink_widget.set_prim_widget(self._prims_widget)


class PrimsWidget():  # pragma: no cover
    def __init__(self, usd_context, stage):
        self._model = PrimModel(stage)
        self._delegate = PrimLinkDelegate(usd_context)
        self.build_ui()

        # The filtering logic
        self._begin_filter_subscription = self._search.subscribe_begin_edit_fn(
            lambda _: PrimsWidget._set_widget_visible(self._search_label, False)
        )
        self._end_filter_subscription = self._search.subscribe_end_edit_fn(
            lambda m: self._filter_by_text(m.as_string)
            or PrimsWidget._set_widget_visible(self._search_label, not m.as_string)
        )

        self._stage_subscription = [
            get_eventdispatcher().observe_event(
                observer_name="omni.kit.widget.layers:layer_link_window",
                event_name=usd_context.stage_event_name(event),
                on_event=func
            )
            for event, func in (
                (omni.usd.StageEventType.OPENED, lambda _: self._open_stage(omni.usd.get_context().get_stage())),
                (omni.usd.StageEventType.CLOSING, lambda _: self._open_stage(None)),
            )
        ]

    def __del__(self):
        self.destroy()

    def destroy(self):
        self._begin_filter_subscription = None
        self._end_filter_subscription = None
        self._stage_subscription = None

        if self._model:
            self._model.destroy()
            self._model = None

        self._delegate = None

    def build_ui(self):
        self._stack = ui.VStack()
        with self._stack:
            ui.Spacer(height=4)
            with ui.ZStack(height=0):
                # Search filed
                self._search = ui.StringField(name="search").model
                # The label on the top of the search field
                self._search_label = ui.Label("Search", name="search")

            ui.Spacer(height=7)
            with ui.ScrollingFrame(
                horizontal_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_ALWAYS_OFF,
                style_type_name_override="TreeView.ScrollingFrame",
            ):
                with ui.ZStack():
                    self._tree_view = ui.TreeView(
                        self._model,
                        delegate=self._delegate,
                        column_widths=[20, 20, ui.Fraction(1)],
                        header_visible=False,
                        root_visible=False,
                        columns_resizable=False,
                    )

        self._delegate.set_tree_view(self._tree_view)

    def _open_stage(self, stage):
        """Called when opening a new stage"""
        if self._model:
            self._model.destroy()

        self._model = PrimModel(stage)

        if self._tree_view:
            self._tree_view.model = self._model

    def _filter_by_text(self, filter_text: str):
        """Set the search filter string to the models and widgets"""
        self._tree_view.keep_alive = not not filter_text
        self._tree_view.keep_expanded = not not filter_text
        self._tree_view.model.filter_by_text(filter_text)

    def set_width(self, width):
        self._stack.width = ui.Pixel(width)

    @staticmethod
    def _set_widget_visible(widget: ui.Widget, visible):
        """Utility for using in lambdas"""
        widget.visible = visible

    def set_layerlink_widget(self, layerlink_widget):
        self._delegate.set_layerlink_widget(layerlink_widget)

    def select(self, spec_paths: List[str]):
        selection = []
        for path in spec_paths:
            path_subs = re.split('[/.]', path.strip('/'))
            item = self._model.find(path_subs)
            if item:
                selection.append(item)
        self._tree_view.selection = selection

    def get_select_specs(self):
        specs = []
        for item in self._tree_view.selection:
            specs.append(item.path.pathString)
        return specs


class LayerLinkSettings:  # pragma: no cover
    SETTINGS_ENABLE_SPEC_LINKING_MODE = "/persistent/app/layerwindow/enableSpecLinkingMode"

    def __init__(self):
        self._settings = carb.settings.get_settings()
        self._show_missing_reference = False
        self._show_layer_contents = False
        self._show_session_layer = False
        self._show_metricsassembler_layer = False
        self._show_layer_file_extension = False
        self._file_dialog_show_root_layer_location = False
        self._show_info_notification = False
        self._show_warning_notification = False
        self._enable_spec_linking_mode = self._settings.get_as_bool(LayerLinkSettings.SETTINGS_ENABLE_SPEC_LINKING_MODE)
        self._show_merge_or_flatten_warning = False
        self._enable_auto_authoring_mode = False

    @property
    def show_missing_reference(self):
        return self._show_missing_reference

    @show_missing_reference.setter
    def show_missing_reference(self, show: bool):
        self._show_missing_reference = show

    @property
    def show_layer_contents(self):
        return self._show_layer_contents

    @show_layer_contents.setter
    def show_layer_contents(self, show: bool):
        self._show_layer_contents = show

    @property
    def show_session_layer(self):
        return self._show_session_layer

    @show_session_layer.setter
    def show_session_layer(self, show: bool):
        self._show_session_layer = show

    @property
    def show_metricsassembler_layer(self):
        return self._show_metricsassembler_layer

    @show_metricsassembler_layer.setter
    def show_metricsassembler_layer(self, show: bool):
        self._show_metricsassembler_layer = show

    @property
    def show_layer_file_extension(self):
        return self._show_layer_file_extension

    @show_layer_file_extension.setter
    def show_layer_file_extension(self, show: bool):
        self._show_layer_file_extension = show

    @property
    def file_dialog_show_root_layer_location(self):
        return self._file_dialog_show_root_layer_location

    @file_dialog_show_root_layer_location.setter
    def file_dialog_show_root_layer_location(self, root_layer: bool):
        self._file_dialog_show_root_layer_location = root_layer

    @property
    def show_info_notification(self):
        return self._show_info_notification

    @show_info_notification.setter
    def show_info_notification(self, enabled: bool):
        self._show_info_notification = enabled

    @property
    def show_warning_notification(self):
        return self._show_warning_notification

    @show_warning_notification.setter
    def show_warning_notification(self, enabled: bool):
        self._show_warning_notification = enabled

    @property
    def enable_auto_authoring_mode(self):
        return self._enable_auto_authoring_mode

    @enable_auto_authoring_mode.setter
    def enable_auto_authoring_mode(self, enabled: bool):
        self._enable_auto_authoring_mode = enabled

    @property
    def enable_spec_linking_mode(self):
        return self._enable_spec_linking_mode

    @enable_spec_linking_mode.setter
    def enable_spec_linking_mode(self, enabled: bool):
        self._enable_spec_linking_mode = enabled

    @property
    def show_merge_or_flatten_warning(self):
        return self._show_merge_or_flatten_warning

    @show_merge_or_flatten_warning.setter
    def show_merge_or_flatten_warning(self, enabled: bool):
        self._show_merge_or_flatten_warning = enabled


class LayerLinkWidget():  # pragma: no cover
    def __init__(self, usd_context, stage):
        self._delegate = LayerLinkDelegate(usd_context)
        self._model = LayerModel(usd_context, layer_settings=LayerLinkSettings())
        self._model.add_stage_attach_listener(self._on_stage_attached)
        self.build_ui()

        # The filtering logic
        self._begin_filter_subscription = self._search.subscribe_begin_edit_fn(
            lambda _: LayerLinkWidget._set_widget_visible(self._search_label, False)
        )
        self._end_filter_subscription = self._search.subscribe_end_edit_fn(
            lambda m: self._filter_by_text(m.as_string)
            or LayerLinkWidget._set_widget_visible(self._search_label, not m.as_string)
        )

    def __del__(self):
        self.destroy()

    def destroy(self):
        if self._model:
            self._model.destroy()
            self._model = None

        if self._delegate:
            self._delegate.destroy()
            self._delegate = None

        self._begin_filter_subscription = None
        self._end_filter_subscription = None

    def build_ui(self):
        with ui.VStack():
            ui.Spacer(height=4)
            with ui.ZStack(height=0):
                # Search filed
                self._search = ui.StringField(name="search").model
                # The label on the top of the search field
                self._search_label = ui.Label("Search", name="search")

            ui.Spacer(height=7)
            with ui.ScrollingFrame(
                horizontal_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_ALWAYS_OFF,
                style_type_name_override="TreeView.ScrollingFrame",
            ):
                with ui.ZStack():
                    self._tree_view = ui.TreeView(
                        self._model,
                        delegate=self._delegate,
                        column_widths=[ui.Fraction(1), 0, 0, 0, 0, 0],
                        header_visible=False,
                        root_visible=False,
                        drop_between_items=True,
                    )

                    self._delegate.set_tree_view(self._tree_view)

    def _on_stage_attached(self, attached: bool):
        if attached:
            self._delegate.on_stage_attached()

    def set_prim_widget(self, prim_widegt: PrimsWidget):
        self._delegate.set_prim_widget(prim_widegt)

    def select(self, layers):
        selection = []
        for layer in layers:
            item = self._model.get_layer_item_by_identifier(layer)
            if item:
                selection.append(item)
        self._tree_view.selection = selection

    def get_select_layers(self):
        layers = [selected.identifier for selected in self._tree_view.selection]
        return layers

    @staticmethod
    def _set_widget_visible(widget: ui.Widget, visible):
        """Utility for using in lambdas"""
        widget.visible = visible

    def _filter_by_text(self, filter_text: str):
        """Set the search filter string to the models and widgets"""
        self._tree_view.visible = True
        self._tree_view.keep_alive = not not filter_text
        self._tree_view.keep_expanded = not not filter_text
        self._tree_view.model.filter_by_text(filter_text)
