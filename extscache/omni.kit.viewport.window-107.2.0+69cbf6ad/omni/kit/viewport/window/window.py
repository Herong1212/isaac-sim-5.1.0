# Copyright (c) 2021-2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

__all__ = ['ViewportWindow']

import contextlib
from typing import Callable, Optional, Sequence
import weakref

import carb.settings
import omni.ui as ui


class ViewportWindow(ui.Window):
    __APP_WINDOW_HIDE_UI = "/app/window/hideUi"
    __GAMEPAD_CONTROL = "/persistent/app/omniverse/gamepadCameraControl"
    __OBJECT_CENTRIC = "/persistent/app/viewport/objectCentricNavigation"
    __DOUBLE_CLICK_COI = "/persistent/app/viewport/coiDoubleClick"

    active_window: Optional[weakref.ProxyType] = None

    """The Viewport Window, simple window holding a ViewportLayers widget"""

    def __init__(self,
                 name: str | None = None,
                 usd_context_name: str = '',
                 width: int = None,
                 height: int = None,
                 flags: int = None,
                 style: dict = None,
                 usd_drop_support: bool = True,
                 hydra_engine_options: Optional[dict] = None,
                 **ui_kw_args):
        """
        ViewportWindow constructor

        Args:
            name (str): The name of the Window.
            usd_context_name (str): The name of a UsdContext this ViewportWindow will be viewing.
            width(int): The width of the Window.
            height(int): The height of the Window.
            flags(int): omni.ui.WINDOW flags to use for the Window.
            style (dict): Optional style overrides to apply to the Window's frame.
            usd_drop_support (bool): Enable Usd drop support (requires {py:mod}`omni.kit.window.drop_support`)
            hydra_engine_options (dict, None): Optional dictionary to use in creation of the HydraEngine
            *args: Additional arguments to pass to omni.ui.Window
            **kwargs: Additional keyword arguments to pass to omni.ui.Window
        """
        resolved_args = ViewportWindow.__resolve_window_args(width, height, flags)
        if resolved_args:
            ui_kw_args.update(resolved_args)

        settings = carb.settings.get_settings()

        # Create a default Window name if none is provided
        # 1. Pull the setting for default-window name
        # 2. Format with key usd_context_name=usd_context_name
        # 3. If format leads to the same name as default-window, append ' (usd_context_name)'
        #
        if name is None:
            name = settings.get("/exts/omni.kit.viewport.window/startup/windowName") or "Viewport"
            if usd_context_name:
                fmt_name = name.format(usd_context_name=usd_context_name)
                if fmt_name == name:
                    name += f" ({usd_context_name})"
                else:
                    name = fmt_name

        super().__init__(name, **ui_kw_args)
        self.__name = name
        self.__external_drop_support = None
        self.__added_frames = {}
        self.__setting_subs: Sequence[carb.settings.SubscriptionId] = ()
        self.__hide_ui_state = None
        self.__minimize_window_sub = None
        self.set_selected_in_dock_changed_fn(self.__selected_in_dock_changed)
        self.set_docked_changed_fn(self.__dock_changed)
        self.set_focused_changed_fn(self.__focused_changed)
        # Window takes focus on any mouse down
        self.focus_policy = ui.FocusPolicy.FOCUS_ON_ANY_MOUSE_DOWN

        # Make a simple style and update it with user provided values if provided
        applied_style = ViewportWindow.__g_default_style
        if style:
            applied_style = applied_style.copy()
            applied_style.update(style)

        self.set_style(applied_style)

        legacy_display_subs: Optional[Sequence[carb.settings.SubscriptionId]] = None

        # Basic Frame for the Viewport
        from .layers import ViewportLayers
        from .legacy import _setup_viewport_options
        with self.frame:
            self.__z_stack = ui.ZStack()
            with self.__z_stack:
                # Currently ViewportWindow only has/supports one embedded ViewportWidget, but give it a unique name
                # that will co-operate if that ever changes.
                viewport_id = f"{name}/Viewport0"

                # Setup the mapping from legacy displayOptions to the persistent viewport settings
                legacy_display_subs = _setup_viewport_options(viewport_id, usd_context_name, settings)

                self.__viewport_layers = ViewportLayers(viewport_id=viewport_id, usd_context_name=usd_context_name,
                                                        get_frame_parent=self.get_frame, hydra_engine_options=hydra_engine_options)

        # Now Viewport & Layers are completely built, if the VP has a stage attached, force a sync when omni.ui does
        # layout.  This works around an issue where the Viewport frame's computed-size notification may not be pushed.
        self.frame.set_build_fn(self.__frame_built)
        if usd_drop_support:
            self.add_external_drag_drop_support()

        ViewportWindow.__g_instances.append(weakref.proxy(self, ViewportWindow.__clean_instances))

        self.__setting_subs = (
            # Watch for hideUi notification to toggle visible items
            settings.subscribe_to_node_change_events(ViewportWindow.__APP_WINDOW_HIDE_UI, self.__hide_ui),
            # Watch for global gamepad enabled change
            settings.subscribe_to_node_change_events(ViewportWindow.__GAMEPAD_CONTROL, self.__set_gamepad_enabled),
            # Watch for global object centric movement changes
            settings.subscribe_to_node_change_events(ViewportWindow.__OBJECT_CENTRIC, self.__set_object_centric),
            # Watch for global double click-to-orbit
            settings.subscribe_to_node_change_events(ViewportWindow.__DOUBLE_CLICK_COI, self.__set_double_click_coi),
        )
        # Store any additional legacy_disply_sub subscription here
        if legacy_display_subs:
            self.__setting_subs = self.__setting_subs + legacy_display_subs

        self.__minimize_window_sub = self.app_window.get_window_minimize_event_stream().create_subscription_to_push(
            self.__on_minimized,
            name=f'omni.kit.viewport.window.minimization_subscription.{self}'
        )

        self.__set_gamepad_enabled()
        self.__set_object_centric()
        self.__set_double_click_coi()

    def __on_minimized(self, event: carb.events.IEvent = None, **kwargs):
        if carb.settings.get_settings().get('/app/renderer/skipWhileMinimized'):
            # If minimized, always stop rendering.
            # If not minimized, restore rendering based on window docked and selected in doock or visibility
            if event.payload.get('isMinimized', False):
                self.viewport_api.updates_enabled = False
            elif self.docked:
                self.viewport_api.updates_enabled = self.selected_in_dock
            else:
                self.viewport_api.updates_enabled = self.visible

    def __focused_changed(self, focused: bool):
        if not focused:
            return

        prev_active, ViewportWindow.active_window = ViewportWindow.active_window, weakref.proxy(self)
        with contextlib.suppress(ReferenceError):
            if prev_active:
                if prev_active == self:
                    return
                prev_active.__set_gamepad_enabled(force_off=True)  # noqa PLW0212
            self.__set_gamepad_enabled()

    @staticmethod
    def __resolve_window_args(width, height, flags):
        settings = carb.settings.get_settings()
        hide_ui = settings.get(ViewportWindow.__APP_WINDOW_HIDE_UI)
        if width is None and height is None:
            width = settings.get("/app/window/width")
            height = settings.get("/app/window/height")
            # If above settings are not set but using hideUi, set to fill main window
            if hide_ui and (width is None) and (height is None):
                width = ui.Workspace.get_main_window_width()
                height = ui.Workspace.get_main_window_height()
            # If still none, use some sane default values
            if width is None and height is None:
                width, height = (1280, 720 + 20)

        if flags is None:
            flags = ui.WINDOW_FLAGS_NO_SCROLLBAR
            # Additional flags to fill main-window when hideUi is in use
            if hide_ui:
                flags |= ui.WINDOW_FLAGS_NO_COLLAPSE | ui.WINDOW_FLAGS_NO_RESIZE | ui.WINDOW_FLAGS_NO_MOVE | ui.WINDOW_FLAGS_NO_TITLE_BAR
            if settings.get("/app/viewport/defaults/noTitleBar"):
                flags |= ui.WINDOW_FLAGS_NO_TITLE_BAR | ui.WINDOW_FLAGS_NO_MOVE

        ui_args = {
            'width': width,
            'height': height,
            'flags': flags,
            # Viewport is changing every frame. We can't raster it.
            'raster_policy': ui.RasterPolicy.NEVER,
        }
        if hide_ui or settings.get("/persistent/app/viewport/noPadding"):
            ui_args['padding_x'], ui_args['padding_y'] = (0, 0)

        return ui_args

    @property
    def name(self):
        """Return the name of the ViewportWindow"""
        return self.__name

    @property
    def viewport_api(self):
        """Return the active ViewportAPI for the ViewportWindow"""
        return self.__viewport_layers.viewport_api if self.__viewport_layers else None

    @property
    def viewport_widget(self):
        """Return the active omni.kit.widget.viewport.ViewportWidget for the ViewportWindow"""
        return self.__viewport_layers.viewport_widget if self.__viewport_layers else None

    def set_style(self, style):
        """
        Set the style for the ViewportWindow

        Args:
             style: The omni.ui style object to apply.
        """
        self.frame.set_style(style)

    @ui.Window.visible.setter
    def visible(self, visible: bool):
        ui.Window.visible.fset(self, visible)
        viewport_api = self.viewport_api
        if viewport_api:
            if visible:
                viewport_api.updates_enabled = True
            elif carb.settings.get_settings().get("/app/renderer/skipWhileInvisible"):
                viewport_api.updates_enabled = False

    def add_external_drag_drop_support(self, callback_fn: Callable = None):
        """
        Add a callback for an external drag-drop event onto the ViewportWindow

        Args:
             callback_fn (Callable): Object to be invoked when the item is dragged or dropped over the ViewportWindow
        """

        # Remove any previously registered support
        prev_callback = self.remove_external_drag_drop_support()
        # If no user supplied function, use the default to open a usd file
        if callback_fn is None:
            callback_fn = self.__external_drop
        try:
            from omni.kit.window.drop_support import ExternalDragDrop
            self.__external_drop_support = ExternalDragDrop(window_name=self.name, drag_drop_fn=callback_fn)
            return prev_callback
        except ImportError:
            import carb
            carb.log_info('Enable omni.kit.window.drop_support for external drop support')

        return False

    def remove_external_drag_drop_support(self):
        """Disable external drag-drop into the ViewportWindow"""
        if self.__external_drop_support:
            prev_callback = self.__external_drop_support._drag_drop_fn  # noqa PLW0212
            self.__external_drop_support.destroy()
            self.__external_drop_support = None
            return prev_callback
        return None

    def get_frame(self, name: str) -> ui.Frame:
        """
        Add a unique {py:class}`omni.ui.Frame` into the view hierarchy.
        This will return a newly created {py:class}`omni.ui.Frame` on the first call for a unique name,
        or return a previously created {py:class}`omni.ui.Frame` for the same unique name.

        Args:
            name (str): A unique identifier for the frame.
        Returns:
            An {py:class}`omni.ui.Frame`.
        """

        frame = self.__added_frames.get(name)
        if frame is None:
            with self.__z_stack:
                frame = ui.Frame(horizontal_clipping=True)
                self.__added_frames[name] = frame
        return frame

    def _find_viewport_layer(self, layer_id: str, category: str = None, layers=None):
        def recurse_layers(layer):
            if layer_id == getattr(layer, 'name', None):  # noqa SIM102
                if (category is None) or (category in getattr(layer, 'categories', ())):
                    return layer
            for child_layer in getattr(layer, 'layers', ()):
                found_layer = recurse_layers(child_layer)
                if found_layer:
                    return found_layer
            return None

        return recurse_layers(layers or self.__viewport_layers)

    def _post_toast_message(self, message: str, message_id: str = None):
        msg_layer = self._find_viewport_layer('Toast Message', 'stats')
        if msg_layer:
            msg_layer.add_message(message, message_id)

    def __del__(self):
        self.destroy()

    def destroy(self):
        """Destroy the ViewportWindow instance"""
        self.remove_external_drag_drop_support()
        self.set_selected_in_dock_changed_fn(None)
        self.set_docked_changed_fn(None)
        self.set_focused_changed_fn(None)

        if self.__minimize_window_sub:
            self.__minimize_window_sub = None

        settings = carb.settings.get_settings()
        for setting_sub in self.__setting_subs:
            if setting_sub:
                settings.unsubscribe_to_change_events(setting_sub)
        self.__setting_subs = ()

        if self.__viewport_layers:
            self.__viewport_layers.destroy()
            self.__viewport_layers = None
            ViewportWindow.__clean_instances(None, self)
        if self.__z_stack:
            self.__z_stack.clear()
            self.__z_stack.destroy()
            self.__z_stack = None
        if self.__added_frames:
            for name, frame in self.__added_frames.items():  # noqa B007
                frame.destroy()
            self.__added_frames = None
        super().destroy()

        # Done last as it is the active ViewportWindow until replaced or fully destroyed
        with contextlib.suppress(ReferenceError):
            if ViewportWindow.active_window == self:
                ViewportWindow.active_window = None

    def __hide_ui(self, *args, **kwargs):
        class UiToggle:
            def __init__(self, window: ViewportWindow):
                self.__visible_layers = None
                self.__tab_visible = window.dock_tab_bar_enabled

            def __log_error(self, visible: bool, *args):
                import traceback
                carb.log_error(f"Error {'showing' if visible else 'hiding'} layer {args}. Traceback:\n{traceback.format_exc()}")

            def __set_visibility(self, window: ViewportWindow, visible: bool, layer_args):
                layers = set()
                try:
                    for name, category in layer_args:
                        layer = window._find_viewport_layer(name, category)  # noqa PLW0212
                        if layer and getattr(layer, 'visible', visible) != visible:
                            layer.visible = visible
                            layers.add((name, category))
                except Exception:  # noqa PLW0718
                    self.__log_error(visible, name, category)
                return layers

            def hide_ui(self, window: ViewportWindow, hide_ui: bool):
                if hide_ui:
                    if self.__visible_layers:
                        return
                    self.__visible_layers = self.__set_visibility(window, False, (
                        ("Axis", "guide"),
                        ("Menubar", "menubar"),
                    ))
                    window.dock_tab_bar_enabled = False
                elif self.__visible_layers:
                    visible_layers, self.__visible_layers = self.__visible_layers, None
                    self.__set_visibility(window, True, visible_layers)
                    window.dock_tab_bar_enabled = self.__tab_visible

        hide_ui = carb.settings.get_settings().get(ViewportWindow.__APP_WINDOW_HIDE_UI)
        if not self.__hide_ui_state:
            self.__hide_ui_state = UiToggle(self)
        self.__hide_ui_state.hide_ui(self, hide_ui)

    def __set_gamepad_enabled(self, *args, force_off: bool = False, **kwargs):
        if not force_off:
            # Get current global value
            enabled = carb.settings.get_settings().get(ViewportWindow.__GAMEPAD_CONTROL)
            # If gamepad set to on, only enable it for the active ViewportWindow
            if enabled:
                with contextlib.suppress(ReferenceError):
                    if ViewportWindow.active_window and ViewportWindow.active_window != self:
                        return
        else:
            enabled = False

        # Dig deep into some implementation details
        cam_manip_item = self._find_viewport_layer('Camera', 'manipulator')
        if not cam_manip_item:
            return
        cam_manip_layer = getattr(cam_manip_item, 'layer', None)
        if not cam_manip_layer:
            return
        cam_manipulator = getattr(cam_manip_layer, 'manipulator', None)
        if not cam_manipulator or not hasattr(cam_manipulator, 'gamepad_enabled'):
            return
        cam_manipulator.gamepad_enabled = enabled
        return

    def __set_object_centric(self, *args, **kwargs):
        settings = carb.settings.get_settings()
        value = settings.get(ViewportWindow.__OBJECT_CENTRIC)
        if value is not None:
            settings.set("/exts/omni.kit.manipulator.camera/objectCentric/type", value)

    def __set_double_click_coi(self, *args, **kwargs):
        settings = carb.settings.get_settings()
        value = settings.get(ViewportWindow.__DOUBLE_CLICK_COI)
        if value is not None:
            settings.set("/exts/omni.kit.viewport.window/coiDoubleClick", value)

    def __external_drop(self, edd, payload):
        import re
        import os
        import pathlib
        import omni.usd
        import omni.kit.undo
        import omni.kit.commands
        from pxr import Sdf

        default_prim_path = Sdf.Path("/")
        stage = omni.usd.get_context().get_stage()
        if stage.HasDefaultPrim():
            default_prim_path = stage.GetDefaultPrim().GetPath()

        re_audio = re.compile(r"^.*\.(wav|wave|ogg|oga|flac|fla|mp3|m4a|spx|opus)(\?.*)?$", re.IGNORECASE)
        re_usd = re.compile(r"^.*\.(usd|usda|usdc|usdz)(\?.*)?$", re.IGNORECASE)

        for source_url in edd.expand_payload(payload):
            if re_usd.match(source_url):
                try:
                    import omni.kit.window.file
                    omni.kit.window.file.open_stage(source_url.replace(os.sep, '/'))
                except ImportError:
                    import carb
                    carb.log_warn(f'Failed to import omni.kit.window.file - Cannot open stage {source_url}')
                return

        with omni.kit.undo.group():
            for source_url in edd.expand_payload(payload):
                if re_audio.match(source_url):
                    stem = pathlib.Path(source_url).stem
                    path = default_prim_path.AppendChild(omni.usd.make_valid_identifier(stem))
                    omni.kit.commands.execute(
                        "CreateAudioPrimFromAssetPath",
                        path_to=path,
                        asset_path=source_url,
                        usd_context=omni.usd.get_context(),
                    )

    def __frame_built(self, *args, **kwargs):
        vp_api = self.__viewport_layers.viewport_api
        stage = vp_api.stage if vp_api else None
        if stage:
            vp_api.viewport_changed(vp_api.camera_path, stage)
        # ViewportWindow owns the hideUi state, so do it now
        self.__hide_ui()

    def __selected_in_dock_changed(self, is_selected):
        self.viewport_api.updates_enabled = is_selected if self.docked else True

    def __dock_changed(self, is_docked):
        self.viewport_api.updates_enabled = self.selected_in_dock if is_docked else True

    @staticmethod
    def set_default_style(style, overwrite: bool = False, usd_context_name: str | None = '', apply: bool = True):
        if overwrite:
            ViewportWindow.__g_default_style = style
        else:
            ViewportWindow.__g_default_style.update(style)
        if apply:
            # Apply the default to all instances of usd_context_name
            for instance in ViewportWindow.get_instances(usd_context_name):
                instance.set_style(ViewportWindow.__g_default_style)

    @staticmethod
    def get_instances(usd_context_name: str | None = ''):
        for instance in ViewportWindow.__g_instances:
            try:
                viewport_api = instance.viewport_api
                if not viewport_api:
                    continue
                # None is the key for all ViewportWindows for all UsdContexts
                # Otherwise compare the provided UsdContext matches the Viewports
                if usd_context_name is None or usd_context_name == viewport_api.usd_context_name:
                    yield instance
            except ReferenceError:
                pass

    @staticmethod
    def __clean_instances(dead, self=None):
        active = []
        for p in ViewportWindow.__g_instances:
            with contextlib.suppress(ReferenceError):
                if p and p != self:
                    active.append(p)

        ViewportWindow.__g_instances = active

    __g_instances = []
    __g_default_style = {
        'ViewportBackgroundColor': {
            'background_color': 0xff000000
        },
        'ViewportStats::Root': {
            'margin_width': 5,
            'margin_height': 3,
        },
        'ViewportStats::Spacer': {
            'margin': 18
        },
        'ViewportStats::Group': {
            'margin_width': 10,
            'margin_height': 5,
        },
        'ViewportStats::Stack': {
        },
        'ViewportStats::Background': {
            'background_color': ui.color(0.145, 0.157, 0.165, 0.8),
            'border_radius': 5,
        },
        'ViewportStats::Label': {
            'margin_height': 1.75,
        },
        'ViewportStats::LabelError': {
            'margin_height': 1.75,
            'color': 0xff0000ff
        },
        'ViewportStats::LabelWarning': {
            'margin_height': 1.75,
            'color': 0xff00ffff
        },
        'ViewportStats::LabelDisabled': {
            'margin_height': 1.75,
            'color': ui.color("#808080")
        }
    }
