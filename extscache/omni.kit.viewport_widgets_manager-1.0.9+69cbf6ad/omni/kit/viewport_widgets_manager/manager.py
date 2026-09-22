import asyncio
import carb
from carb.eventdispatcher import get_eventdispatcher
import weakref
import omni.usd
import omni.timeline
import omni.ui as ui
import omni.kit.app as app


from omni.kit.viewport.utility import (
    get_active_viewport_window,
    get_ui_position_for_prim,
    ViewportPrimReferencePoint
)

from typing import List
from pxr import Tf, Usd, Sdf, UsdGeom, Trace
from .widget_provider import WidgetProvider


class WidgetAlignment:
    CENTER = 0
    BOTTOM = 1
    TOP = 2


class WidgetWrapper:
    def __init__(
        self, usd_context, viewport_window, viewport_canvas, prim_path: Sdf.Path, widget_provider: WidgetProvider,
        alignment=WidgetAlignment.CENTER
    ):
        self._prim_path = prim_path
        self._widget_provider = widget_provider
        self._window = viewport_window
        self._canvas = viewport_canvas
        self._viewport_placer = None
        self._alignment = alignment
        self._layout = None
        self._anchoring = True
        self._usd_context = usd_context
        self._timeline = omni.timeline.get_timeline_interface()

    @property
    def alignment(self):
        return self._alignment

    @property
    def prim_path(self) -> Sdf.Path:
        return self._prim_path

    @property
    def visible(self):
        return self._viewport_placer and self._viewport_placer.visible

    @visible.setter
    def visible(self, value):
        if self._viewport_placer:
            self._viewport_placer.visible = value

    def clear(self):
        self._anchoring = False
        if self._layout:
            self._layout.clear()
            self._layout.destroy()
            self._layout = None
        if self._viewport_placer:
            self._viewport_placer.clear()
            self._viewport_placer.destroy()
            self._viewport_placer = None

    @Trace.TraceFunction
    def update_widget_position(self, cached_position=None):
        viewport_window = self._window
        if not viewport_window:
            return False

        alignment = {
            WidgetAlignment.TOP: ViewportPrimReferencePoint.BOUND_BOX_TOP,
            WidgetAlignment.BOTTOM: ViewportPrimReferencePoint.BOUND_BOX_BOTTOM
        }.get(self._alignment, ViewportPrimReferencePoint.BOUND_BOX_CENTER)

        if cached_position:
            ui_pos, in_viewport = cached_position
        else:
            ui_pos, in_viewport = get_ui_position_for_prim(viewport_window, str(self.prim_path), alignment=alignment)

        if not in_viewport:
            return False

        dpi = ui.Workspace.get_dpi_scale()
        dpi = dpi if (dpi > 0) else 1.0

        prim_window_pos_x, prim_window_pos_y = ui_pos
        self._viewport_placer.offset_x = prim_window_pos_x / dpi - self._window.position_x
        self._viewport_placer.offset_y = prim_window_pos_y / dpi - self._window.position_y

        computed_width = self._layout.computed_width
        comuted_height = self._layout.computed_height

        offset_x = -float(computed_width) * 0.5
        offset_y = -float(comuted_height) * 0.5

        self._viewport_placer.offset_x += offset_x
        self._viewport_placer.offset_y += offset_y

        return True

    def create_or_update_widget(self, cached_position=None):
        viewport_window = self._window
        if (viewport_window is None) or (not viewport_window.visible):
            self.clear()
            return

        stage = viewport_window.viewport_api.stage
        if not stage:
            self.clear()
            return

        prim = stage.GetPrimAtPath(self.prim_path)
        if not prim:
            self.clear()
            return

        # If prim is hidden, clearing the widget.
        if (
            not self._is_prim_visible(stage, prim) or
            not self._is_camera_mesh_visible(stage, prim)
        ):
            self.clear()
            return

        if not self._viewport_placer:
            self._anchoring = True
            with self._canvas:
                self._viewport_placer = ui.Placer()
                with self._viewport_placer:
                    self._layout = ui.HStack(width=0, height=0)
                    with self._layout:
                        self._widget_provider.build_widget(viewport_window)
        elif not self.update_widget_position(cached_position):
            self.clear()

    def _is_prim_visible(self, stage, prim):
        imageable = UsdGeom.Imageable(prim)
        if not imageable:
            return False

        visibility_attr = imageable.GetVisibilityAttr()
        time_sampled = visibility_attr.GetNumTimeSamples() > 1
        curr_time = self._timeline.get_current_time()
        if time_sampled:
            curr_time_code = curr_time * stage.GetTimeCodesPerSecond()
        else:
            curr_time_code = Usd.TimeCode.Default()
        visibility = imageable.ComputeVisibility(curr_time_code)

        return visibility != UsdGeom.Tokens.invisible

    def _is_camera_mesh_visible(self, stage, prim):
        # Only handle camera prim, as camera prim except builtin ones will
        # include a mesh.
        if not prim.IsA(UsdGeom.Camera):
            return True

        display_predicate = Usd.TraverseInstanceProxies(Usd.PrimAllPrimsPredicate)
        for prim in Usd.PrimRange(prim, display_predicate):
            if prim.IsA(UsdGeom.Mesh):
                return self._is_prim_visible(stage, prim)

        return False

    def try_anchoring(self):
        if not self._window or not self._anchoring:
            return

        computed_width = self._layout.computed_width
        comuted_height = self._layout.computed_height
        if computed_width == 0 or comuted_height == 0:
            return False

        self._anchoring = False
        self.update_widget_position()


class ViewportWidgetsManager:
    def __init__(self, usd_context_name=""):
        self._stage_event_subscription = None
        self._update_subscription = None
        self._last_active_camera_path = None
        self._stage_changed_subscription = None
        self._all_widgets: List[WidgetWrapper] = []
        self._usd_context = omni.usd.get_context(usd_context_name)
        self._pending_update_all = False
        self._pending_update_prim_paths = set([])
        self._viewport_frame = None
        self._viewport_window = None
        self._frame_canvas = None
        self._current_wait_frames = 0
        self._all_widgets_hidden = False

    def _initialize(self):
        self._viewport_window = get_active_viewport_window(window_name="Viewport")
        self._viewport_frame = self._viewport_window.get_frame(f"omni.kit.viewport_widgets_manager")
        self._viewport_frame.set_computed_content_size_changed_fn(self._update_all_widgets)

        # Stores position and size for comparing.
        if self._viewport_window:
            self._last_active_camera_path = self._viewport_window.viewport_api.camera_path
            with self._viewport_frame:
                self._frame_canvas = ui.ZStack()
        else:
            self._last_active_camera_path = None

    def _reset(self):
        if self._viewport_frame:
            self._viewport_frame.set_computed_content_size_changed_fn(None)
            self._viewport_frame.clear()
            self._viewport_frame = None
            self._frame_canvas.clear()
            self._frame_canvas = None

        self._viewport_window = None
        self._last_active_camera_path = None

        for widget in self._all_widgets:
            widget.clear()
        self._all_widgets.clear()

    def start(self):
        self._initialize()

        self._stage_event_subscription = [
            get_eventdispatcher().observe_event(
                observer_name="omni.kit.viewport_widgets_manager:manager",
                event_name=self._usd_context.stage_event_name(event),
                on_event=func
            )
            for event, func in (
                (omni.usd.StageEventType.OPENED, lambda _: self._start_update_subscription()),
                (omni.usd.StageEventType.CLOSED, lambda _: self._stop_update_subscription()),
            )
        ]

        self._start_update_subscription()

    def stop(self):
        self._stage_event_subscription = None
        self._stop_update_subscription()
        self._reset()

    @Trace.TraceFunction
    def _on_objects_changed(self, notice, stage):
        if stage != self._usd_context.get_stage():
            return

        for path in notice.GetResyncedPaths():
            if path == Sdf.Path.absoluteRootPath:
                self._pending_update_all = True
                self._current_wait_frames = 0
                # TRICK: Hides all widgets to delay the refresh
                # to avoid let user be aware of the delay.
                self._hide_all_widgets()
            else:
                self._pending_update_prim_paths.add(path)

        for path in notice.GetChangedInfoOnlyPaths():
            prim_path = path.GetPrimPath()
            # self._last_active_camera_path may be None, so make sure an
            # implicit Sdf.Path isn't constructed for equality comparison
            if (
                prim_path == Sdf.Path.absoluteRootPath or
                (
                    self._last_active_camera_path and
                    prim_path == self._last_active_camera_path
                )
            ):
                self._pending_update_all = True
                self._current_wait_frames = 0
                self._hide_all_widgets()
            else:
                self._pending_update_prim_paths.add(prim_path)

    def _handle_pending_updates(self):
        if self._pending_update_all:
            self._update_all_widgets()
        elif self._pending_update_prim_paths:
            update_widgets = []
            for prim_path in self._pending_update_prim_paths:
                for widget in self._all_widgets:
                    if prim_path.HasPrefix(widget.prim_path):
                        update_widgets.append(widget)

            self._update_all_widgets_internal(update_widgets)

        self._pending_update_all = False
        self._pending_update_prim_paths.clear()

    def _update_all_widgets_internal(self, widgets: List[WidgetWrapper]):
        # TODO: How to speed up this to batch the ui pos calculation.

        def get_ui_position(widget: WidgetWrapper):
            alignment = {
                WidgetAlignment.TOP: ViewportPrimReferencePoint.BOUND_BOX_TOP,
                WidgetAlignment.BOTTOM: ViewportPrimReferencePoint.BOUND_BOX_BOTTOM
            }.get(widget.alignment, ViewportPrimReferencePoint.BOUND_BOX_CENTER)

            return get_ui_position_for_prim(
                self._viewport_window,
                str(widget.prim_path),
                alignment=alignment
            )

        for widget in widgets:
            ui_pos = get_ui_position(widget)
            widget.create_or_update_widget(ui_pos)

    def _update_all_widgets(self):
        update_widgets = []
        for widget in self._all_widgets:
            # Don't draw widget for current active camera path.
            if not self._last_active_camera_path or widget.prim_path != self._last_active_camera_path:
                update_widgets.append(widget)
            else:
                widget.clear()

        self._update_all_widgets_internal(update_widgets)

    def _trying_anchoring_all_widgets(self):
        for widget in self._all_widgets:
            widget.try_anchoring()

    def _stop_update_subscription(self):
        self._update_subscription = None
        self._last_active_camera_path = None
        for widget in self._all_widgets:
            widget.clear()
        self._all_widgets.clear()

        if self._stage_changed_subscription:
            self._stage_changed_subscription.Revoke()
            self._stage_changed_subscription = None

    def _start_update_subscription(self):
        self._update_subscription = get_eventdispatcher().observe_event(
            event_name=omni.kit.app.GLOBAL_EVENT_UPDATE,
            on_event=self._on_update,
            observer_name="omni.kit.viewport_widgets_manager update"
        )

        self._stage_changed_subscription = Tf.Notice.Register(
            Usd.Notice.ObjectsChanged, self._on_objects_changed, self._usd_context.get_stage()
        )

    def _hide_all_widgets(self):
        for widget in self._all_widgets:
            widget.visible = False
        self._all_widgets_hidden = True

    def _show_all_widgets(self):
        if not self._all_widgets_hidden:
            return

        self._all_widgets_hidden = False
        for widget in self._all_widgets:
            widget.visible = True

    def _on_update(self, _):
        # Puts some delay to avoid refreshing prims frequently
        self._current_wait_frames += 1
        if self._current_wait_frames <= 3:
            return
        else:
            self._current_wait_frames = 0

        self._show_all_widgets()

        viewport_window = get_active_viewport_window()
        if not viewport_window and self._viewport_window:
            self._reset()
            return
        elif viewport_window and not self._viewport_window:
            self._initialize()

        self._trying_anchoring_all_widgets()

        # Handle pending updates
        self._handle_pending_updates()

        # Checks changed camera
        active_camera_path = viewport_window.viewport_api.camera_path
        if (not active_camera_path) or (not self._last_active_camera_path) or (self._last_active_camera_path != active_camera_path):
            self._last_active_camera_path = active_camera_path
            self._update_all_widgets()

    def add_widget(self, prim_path: Sdf.Path, widget: WidgetProvider, alignment=WidgetAlignment.CENTER):
        usd_context = self._viewport_window.viewport_api.usd_context
        stage = usd_context.get_stage()
        usd_prim = stage.GetPrimAtPath(prim_path) if stage else False
        if usd_prim:
            xformable_prim = UsdGeom.Xformable(usd_prim)
        else:
            xformable_prim = None

        if not xformable_prim:
            carb.warn(f"Cannot add viewport widget for non-xformable prim.")
            return None

        carb.log_info(f"Adding prim widget for {prim_path}")
        widget_wrapper = WidgetWrapper(
            self._usd_context,
            self._viewport_window,
            self._frame_canvas,
            prim_path,
            widget,
            alignment
        )

        self._all_widgets.append(widget_wrapper)
        if not self._last_active_camera_path or prim_path != self._last_active_camera_path:
            widget_wrapper.create_or_update_widget()

        return weakref.ref(widget_wrapper)

    def remove_widget(self, widget_id):
        if not widget_id:
            return

        try:
            local_wiget = widget_id()
            if widget_id and local_wiget:
                if local_wiget in self._all_widgets:
                    local_wiget.clear()
                    self._all_widgets.remove(local_wiget)
        except Exception:
            pass
