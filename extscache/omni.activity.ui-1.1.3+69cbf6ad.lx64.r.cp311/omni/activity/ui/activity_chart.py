# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = ["ActivityChart"]

from .activity_delegate import ActivityDelegate
from .activity_filter_model import ActivityFilterModel
from .activity_menu import ActivityMenuOptions
from .activity_model import SECOND_MULTIPLIER, TIMELINE_EXTEND_DELAY_SEC
from .activity_pack_model import ActivityPackModel
from .activity_tree_delegate import ActivityTreeDelegate
from functools import partial
from omni.ui import color as cl
from typing import Tuple
import carb.input
import math
import omni.appwindow
import omni.client
import omni.ui as ui
import weakref


DENSITY = [1, 2, 5]


def get_density(i):
    # the density will be like this [1, 2, 5, 10, 20, 50, 100, 200, 500, 1000, 2000, 5000, 10000, ...]
    level = math.floor(i / 3)
    return (10**level) * DENSITY[i % 3]


def get_current_mouse_coords() -> Tuple[float, float]:
    app_window = omni.appwindow.get_default_app_window()
    input = carb.input.acquire_input_interface()
    dpi_scale = ui.Workspace.get_dpi_scale()
    pos_x, pos_y = input.get_mouse_coords_pixel(app_window.get_mouse())
    return pos_x / dpi_scale, pos_y / dpi_scale


class ActivityChart:
    """The widget that represents the activity viewer"""

    def __init__(self, model, activity_menu: ActivityMenuOptions = None, **kwargs):
        self.__model = None
        self.__packed_model = None
        self.__filter_model = None

        # Widgets
        self.__timeline_frame = None
        self.__selection_frame = None
        self.__chart_graph = None
        self.__chart_tree = None
        self._activity_menu_option = activity_menu

        # Timeline Zoom
        self.__zoom_level = 100

        self.__delegate = kwargs.pop("delegate", None) or ActivityDelegate(
            on_expand=partial(ActivityChart.__on_timeline_expand, weakref.proxy(self)),
        )
        self.__tree_delegate = ActivityTreeDelegate(
            on_expand=partial(ActivityChart.__on_treeview_expand, weakref.proxy(self)),
            initialize_expansion=partial(ActivityChart.__initialize_expansion, weakref.proxy(self)),
        )

        self.density = 3

        self.__frame = ui.Frame(
            build_fn=partial(self.__build, model),
            style={"ActivityBar": {"border_color": cl(0.25), "secondary_selected_color": cl.white, "border_width": 1}},
        )

        # Selection
        self.__is_selection = False
        self.__selection_from = None
        self.__selection_to = None

        # Pan/zoom
        self.__pan_x_start = None
        self.width = None

    def destroy(self):
        self.__model = None
        if self.__packed_model:
            self.__packed_model.destroy()
        if self.__filter_model:
            self.__filter_model.destroy()
        if self.__delegate:
            self.__delegate.destroy()
            self.__delegate = None
        self.__tree_delegate = None

    def invalidate(self):  # pragma: no cover
        """Rebuild all"""
        # TODO: Do we need it?
        self.__frame.rebuild()

    def new(self, model=None):
        """Recreate the models and start recording"""
        if self.__packed_model:
            self.__packed_model.destroy()
        if self.__filter_model:
            self.__filter_model.destroy()

        self.__model = model
        if self.__model:
            self.__packed_model = ActivityPackModel(
                self.__model,
                on_timeline_changed=partial(ActivityChart.__on_timeline_changed, weakref.proxy(self)),
                on_selection_changed=partial(ActivityChart.__on_selection_changed, weakref.proxy(self)),
            )
            self.__filter_model = ActivityFilterModel(self.__model)

            self.__apply_models()
            self.__on_timeline_changed()
        else:
            if self.__chart_graph:
                self.__chart_graph.dirty_widgets()
            if self.__chart_tree:
                self.__chart_tree.dirty_widgets()

    def save_for_report(self):
        return self.__model.get_report_data()

    def __build(self, model):
        """Build the whole UI"""
        if self._activity_menu_option:
            self._options_menu = ui.Menu("Options")
            with self._options_menu:
                ui.MenuItem("Open...", triggered_fn=self._activity_menu_option.menu_open)
                ui.MenuItem("Save...", triggered_fn=self._activity_menu_option.menu_save)
        with ui.VStack():
            self.__build_title()
            self.__build_body()
            self.__build_footer()

        self.new(model)

    def __build_title(self):
        """Build the top part of the widget"""
        pass

    def __zoom_horizontally(self, x: float, y: float, modifiers: int):
        scale = 1.1**y
        self.__zoom_level *= scale
        self.__range_placer.width = ui.Percent(self.__zoom_level)
        self.__timeline_placer.width = ui.Percent(self.__zoom_level)

        # do an offset pan, so the zoom looks like happened at the mouse coordinate
        origin = self.__range_frame.screen_position_x
        pox_x, pos_y = get_current_mouse_coords()
        offset = (pox_x - origin - self.__range_placer.offset_x) * (scale - 1)
        self.__range_placer.offset_x -= offset
        self.__timeline_placer.offset_x -= offset

        if self.__relax_timeline():
            self.__timeline_indicator.rebuild()

    def __relax_timeline(self):
        if self.width is None:
            return
        width = self.__timeline_placer.computed_width * self.width / get_density(self.density)
        if width < 25 and self.density > 0:
            self.density -= 1
            return True
        elif width > 50:
            self.density += 1
            return True
        return False

    def __selection_changed(self, selection):
        """
        Called from treeview selection change, update the timeline selection
        """
        if not selection:
            return

        # avoid selection loop
        if self.__packed_model.selection and selection[0] == self.__packed_model.selection:
            return

        self.__delegate.select_range(selection[0], self.__packed_model)

        self.selection_on_stage(selection[0])

    def selection_on_stage(self, item):
        if not item:
            return
        path = item.name_model.as_string
        # skip the one which is cached locally
        if path.startswith("file:"):
            return
        elif path.endswith("instance)"):
            path = path.split(" ")[0]
        usd_context = omni.usd.get_context()
        usd_context.get_selection().set_selected_prim_paths([path], True)

    def show_stack_from_idx(self, idx):
        if idx == 0:
            self._activity_stack.visible = False
            self._timeline_stack.visible = True
        elif idx == 1:
            self._activity_stack.visible = True
            self._timeline_stack.visible = False

    def __build_body(self):
        """Build the middle part of the widget"""
        self._collection = ui.RadioCollection()
        with ui.VStack():
            with ui.HStack(height=30):
                ui.Spacer()
                tab0 = ui.RadioButton(
                    text="Timeline",
                    width=0,
                    radio_collection=self._collection)
                ui.Spacer(width=12)
                with ui.VStack(width=3):
                    ui.Spacer()
                    ui.Rectangle(name="separator", height=16)
                    ui.Spacer()
                ui.Spacer(width=12)
                tab1 = ui.RadioButton(
                    text="Activities",
                    width=0,
                    radio_collection=self._collection)
                ui.Spacer()
                ui.Button(name="options", width=20, height=20, clicked_fn=lambda: self._options_menu.show())
            with ui.ZStack():
                self.__build_timeline_stack()
                self.__build_activity_stack()
                self._activity_stack.visible = False
            tab0.set_clicked_fn(lambda: self.show_stack_from_idx(0))
            tab1.set_clicked_fn(lambda: self.show_stack_from_idx(1))

    def __timeline_right_pressed(self, x, y, button, modifier):
        if button != 1:
            return
        # make to separate this from middle mouse selection
        self.__is_selection = False

        self.__pan_x_start = x
        self.__pan_y_start = y

    def __timeline_pan(self, x, y):
        if self.__pan_x_start is None:
            return
        self.__pan_x_end = x
        moved_x = self.__pan_x_end - self.__pan_x_start
        self.__range_placer.offset_x += moved_x
        self.__timeline_placer.offset_x += moved_x

        self.__pan_x_start = x

        self.__pan_y_end = y
        moved_y = min(self.__pan_y_start - self.__pan_y_end, self.__range_frame.scroll_y_max)
        self.__range_frame.scroll_y += moved_y
        self.__pan_y_start = y

    def __timeline_right_moved(self, x, y, modifier, button):
        if button or self.__is_selection:
            return
        self.__timeline_pan(x, y)

    def __timeline_right_released(self, x, y, button, modifier):
        if button != 1 or self.__pan_x_start is None:
            return
        self.__timeline_pan(x, y)
        self.__pan_x_start = None

    def __build_timeline_stack(self):
        self._timeline_stack = ui.VStack()
        with self._timeline_stack:
            with ui.ZStack():
                with ui.VStack():
                    ui.Rectangle(height=36, name="spacer")
                    self.__range_frame = ui.ScrollingFrame(
                        horizontal_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_ALWAYS_OFF,
                        mouse_wheel_fn=self.__zoom_horizontally)
                    with self.__range_frame:
                        self.__range_placer = ui.Placer()
                        with self.__range_placer:
                            # Chart view
                            self.__chart_graph = ui.TreeView(
                                self.__packed_model,
                                delegate=self.__delegate,
                                root_visible=False,
                                header_visible=True,
                                column_widths=[ui.Fraction(1), 0, 0, 0, 0]
                            )
                with ui.HStack():
                    with ui.ScrollingFrame(
                        horizontal_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_ALWAYS_OFF,
                        vertical_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_ALWAYS_OFF,
                    ):
                        self.__timeline_placer = ui.Placer(
                            mouse_pressed_fn=self.__timeline_right_pressed,
                            mouse_released_fn=self.__timeline_right_released,
                            mouse_moved_fn=self.__timeline_right_moved,
                        )
                        with self.__timeline_placer:
                            # It's in placer to prevent the whole ZStack from changing size
                            self.__timeline_frame = ui.Frame(build_fn=self.__build_timeline)
                    # this is really a trick to show self.__range_frame's vertical scrollbar, and 12 is the
                    # kScrollBarWidth of scrollingFrame, so that we can pan vertically for the timeline
                    scrollbar_width = 12 * ui.Workspace.get_dpi_scale()
                    ui.Spacer(width=scrollbar_width)

    def __build_activity_stack(self):
        # TreeView with all the activities
        self._activity_stack = ui.VStack()
        with self._activity_stack:
            with ui.ScrollingFrame():
                self.__chart_tree = ui.TreeView(
                    self.__filter_model,
                    delegate=self.__tree_delegate,
                    root_visible=False,
                    header_visible=True,
                    column_widths=[ui.Fraction(1), 60, 60, 60, 60],
                    columns_resizable=True,
                    selection_changed_fn=self.__selection_changed,
                )

    def __build_footer(self):
        """Build the bottom part of the widget"""
        pass

    def __build_timeline(self):
        """Build the timeline on top of the chart"""
        if self.__packed_model:
            time_begin = self.__packed_model._time_begin
            time_end = self.__packed_model._time_end
            self.time_length = (time_end - time_begin) / SECOND_MULTIPLIER
        else:
            self.time_length = TIMELINE_EXTEND_DELAY_SEC

        self.time_step = max(math.floor(self.time_length / 5.0), 1.0)
        self.width = self.time_step / self.time_length

        with ui.ZStack():
            self.__timeline_indicator = ui.Frame(build_fn=self.__build_time_indicator)
            self.__selection_frame = ui.Frame(
                build_fn=self.__build_selection,
                mouse_pressed_fn=self.__timeline_middle_pressed,
                mouse_released_fn=self.__timeline_middle_released,
                mouse_moved_fn=self.__timeline_middle_moved,
            )

    def __build_time_indicator(self):
        density = get_density(self.density)
        counts = math.floor(self.time_length / self.time_step) * density
        # put a cap on the indicator numbers. Otherwise, it hits the imgui prims limits and cause crash
        if counts > 10000:
            carb.log_warn("Zoom level is too high to show the time indicator")
            return
        width = ui.Percent(self.width / density * 100)

        with ui.VStack():
            with ui.Placer(offset_x=-0.5 * width, height=0):
                with ui.HStack():
                    for i in range(math.floor(counts / 5)):
                        ui.Label(f" {i * 5 * self.time_step / density} s", name="time", width=width * 5)
            with ui.HStack():
                for i in range(counts):
                    if i % 10 == 0:
                        height = 36
                    elif i % 5 == 0:
                        height = 24
                    else:
                        height = 12
                    ui.Line(alignment=ui.Alignment.LEFT, height=height, name="timeline", width=width)

    def __build_selection(self):
        """Build the selection widgets on top of the chart"""
        if self.__selection_from is None or self.__selection_to is None or self.__selection_from == self.__selection_to:
            ui.Spacer()
            return

        if self.__packed_model is None:
            return

        time_begin = self.__packed_model._time_begin
        time_end = self.__packed_model._time_end

        selection_from = min(self.__selection_from, self.__selection_to)
        selection_to = max(self.__selection_from, self.__selection_to)

        with ui.HStack():
            ui.Spacer(width=ui.Fraction(selection_from - time_begin))
            with ui.ZStack(width=ui.Fraction(selection_to - selection_from)):
                ui.Rectangle(name="selected_area")
                ui.Label(
                    f"{(selection_from - time_begin) / SECOND_MULTIPLIER:.2f}",
                    height=0, elided_text=True, elided_text_str="", name="selection_time")
                ui.Label(
                    f"< {(selection_to - selection_from) / SECOND_MULTIPLIER:.2f} s >",
                    height=0, elided_text=True, elided_text_str="", name="selection_time", alignment=ui.Alignment.CENTER)
            ui.Label(
                f"{(selection_to - time_begin) / SECOND_MULTIPLIER:.2f}",
                width=ui.Fraction(time_end - selection_to), height=0,
                elided_text=True, elided_text_str="", name="selection_time")

    def __on_timeline_changed(self):
        """
        Called to resubmit timeline because the global time range is
        changed.
        """
        if self.__chart_graph:
            # Update visible widgets
            self.__chart_graph.dirty_widgets()
        if self.__timeline_frame:
            self.__relax_timeline()
            self.__timeline_frame.rebuild()

    def __on_selection_changed(self):
        """
        Called from timeline selection change, update the treeview selection
        """
        selection = self.__packed_model.selection
        self.__chart_tree.selection = [selection]

        self.selection_on_stage(selection)

    def __on_timeline_expand(self, item, range_item, recursive):
        """Called from the timeline when it wants to expand something"""
        if self.__chart_graph:
            expanded = not self.__chart_graph.is_expanded(item)
            self.__chart_graph.set_expanded(item, expanded, recursive)

            # Expand the bottom tree view as well.
            if expanded != self.__chart_tree.is_expanded(range_item):
                self.__chart_tree.set_expanded(range_item, expanded, recursive)

    def __initialize_expansion(self, item, expanded):
        # expand the treeview
        if self.__chart_tree:
            if expanded != self.__chart_tree.is_expanded(item):
                self.__chart_tree.set_expanded(item, expanded, False)

        # expand the timeline
        if self.__chart_graph:
            pack_item = item._packItem
            if pack_item and expanded != self.__chart_graph.is_expanded(pack_item):
                self.__chart_graph.set_expanded(pack_item, expanded, False)

    def __on_treeview_expand(self, range_item):
        """Called from the treeview when it wants to expand something"""
        # this callback is triggered when the branch is pressed, so the expand status will be opposite of the current
        # expansion status
        if self.__chart_tree:
            expanded = not self.__chart_tree.is_expanded(range_item)

            # expand the timeline as well
            item = range_item._packItem
            if item and expanded != self.__chart_graph.is_expanded(item):
                self.__chart_graph.set_expanded(item, expanded, False)

    def __timeline_middle_pressed(self, x, y, button, modifier):
        if button != 2:
            return

        self.__is_selection = True

        if self.__packed_model is None:
            return

        width = self.__selection_frame.computed_width
        origin = self.__selection_frame.screen_position_x
        time_begin = self.__packed_model._time_begin
        time_end = self.__packed_model._time_end

        self.__selection_from_pos_x = x
        self.__selection_from = time_begin + (x - origin) / width * (time_end - time_begin)
        self.__selection_from = max(self.__selection_from, time_begin)
        self.__selection_from = min(self.__selection_from, time_end)

    def __timeline_middle_moved(self, x, y, modifier, button):
        if button or not self.__is_selection or self.__packed_model is None:
            return

        width = self.__selection_frame.computed_width
        if width == 0:
            return

        origin = self.__selection_frame.screen_position_x
        time_begin = self.__packed_model._time_begin
        time_end = self.__packed_model._time_end

        self.__selection_to = time_begin + (x - origin) / width * (time_end - time_begin)
        self.__selection_to = max(self.__selection_to, time_begin)
        self.__selection_to = min(self.__selection_to, time_end)

        self.__selection_frame.rebuild()

    def __timeline_middle_released(self, x, y, button, modifier):
        if button != 2 or not self.__is_selection or self.__packed_model is None:
            return

        self.__selection_to_pos_x = x
        width = self.__selection_frame.computed_width
        origin = self.__selection_frame.screen_position_x
        time_begin = self.__packed_model._time_begin
        time_end = self.__packed_model._time_end

        self.__selection_to = time_begin + (x - origin) / width * (time_end - time_begin)
        self.__selection_to = max(self.__selection_to, time_begin)
        self.__selection_to = min(self.__selection_to, time_end)

        self.__selection_frame.rebuild()

        self.__timeline_selected()

        self.__is_selection = False

    def __zoom_to_fit_selection(self):

        time_begin = self.__packed_model._time_begin
        time_end = self.__packed_model._time_end

        selection_from = self.__filter_model.timerange_begin
        selection_to = self.__filter_model.timerange_end

        pre_zoom_level = self.__zoom_level
        zoom_level = (time_end - time_begin) / float(selection_to - selection_from) * 100
        # zoom
        self.__zoom_level = zoom_level
        self.__range_placer.width = ui.Percent(self.__zoom_level)
        self.__timeline_placer.width = ui.Percent(self.__zoom_level)
        # offset pan
        origin = self.__selection_frame.screen_position_x

        start = min(self.__selection_to_pos_x, self.__selection_from_pos_x)
        offset = (start - origin) * zoom_level / float(pre_zoom_level) + self.__range_placer.offset_x
        self.__range_placer.offset_x -= offset
        self.__timeline_placer.offset_x -= offset

    def __timeline_selected(self):
        if self.__selection_from is None or self.__selection_to is None or self.__selection_from == self.__selection_to:
            # Deselect
            self.__filter_model.timerange_begin = None
            self.__filter_model.timerange_end = None
            return

        self.__filter_model.timerange_begin = min(self.__selection_from, self.__selection_to)
        self.__filter_model.timerange_end = max(self.__selection_from, self.__selection_to)

        self.__zoom_to_fit_selection()

    def __apply_models(self):
        if self.__chart_graph:
            self.__chart_graph.model = self.__packed_model
        if self.__chart_tree:
            self.__chart_tree.model = self.__filter_model
