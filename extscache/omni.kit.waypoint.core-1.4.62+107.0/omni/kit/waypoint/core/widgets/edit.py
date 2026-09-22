import asyncio

import omni.kit.app
from omni import ui

from ..extension import get_instance as get_waypoint_instance
from ..model import WaypointItem
from ..style import ICON_PATH


class WaypointItemEditWidget:
    def __init__(self, item: WaypointItem, on_edit_end_fn: callable = None):
        self._on_edit_end_fn = on_edit_end_fn
        self._waypoint_instance = get_waypoint_instance()

        self._build_ui(item)

    def destroy(self):
        self._container.clear()
        self._on_edit_end_fn = None
        self._waypoint_instance = None

    @property
    def visible(self) -> bool:
        return self._container.visible

    @visible.setter
    def visible(self, value: bool) -> None:
        self._container.visible = value

    def _build_ui(self, item: WaypointItem) -> None:
        self._container = ui.ZStack()
        with self._container:
            ui.Rectangle(style_type_name_override="GridView.Edit.Frame")
            with ui.HStack():
                ui.Spacer()
                with ui.VStack(width=18):
                    ui.Spacer(height=5)
                    ui.Image(f"{ICON_PATH}/unlock_dark.svg", width=12, height=12)
                ui.Spacer(width=1)

            with ui.VStack():
                ui.Spacer(height=18)
                with ui.HStack():
                    # It is strange here that clicked_fn cannot be triggered if background image has drag function
                    # Has to use mouse_pressed_fn instead
                    self._apply_button = ui.Button(
                        "Apply",
                        width=ui.Percent(33),
                        name="apply",
                        mouse_pressed_fn=lambda x, y, btn, a, item=item: self._edit_save(btn, item),
                        mouse_hovered_fn=lambda hovered, item=item: self._on_edit_hovered(hovered, item),
                        style_type_name_override="GridView.Edit.Button",
                    )
                    self._new_button = ui.Button(
                        "Add New",
                        width=ui.Percent(33),
                        name="new",
                        mouse_pressed_fn=lambda x, y, btn, a, item=item: self._edit_new(btn, item),
                        mouse_hovered_fn=lambda hovered, item=item: self._on_edit_hovered(hovered, item),
                        style_type_name_override="GridView.Edit.Button",
                    )
                    self._cancel_button = ui.Button(
                        "Cancel",
                        width=ui.Percent(33),
                        name="cancel",
                        mouse_pressed_fn=lambda x, y, btn, a, item=item: self._edit_cancel(btn, item),
                        mouse_hovered_fn=lambda hovered, item=item: self._on_edit_hovered(hovered, item),
                        style_type_name_override="GridView.Edit.Button",
                    )

                ui.Spacer(height=18)

    def _edit_save(self, btn: int, item: WaypointItem):
        if btn == 0:
            self._container.visible = False

            # Here wait a frame to refresh all waypoint widgets due to waypoint changed
            async def __end_edit_async(item: WaypointItem):
                await omni.kit.app.get_app().next_update_async()
                if self._waypoint_instance:
                    self._waypoint_instance.end_edit_waypoint(item.waypoint, True)

                if callable(self._on_edit_end_fn):
                    self._on_edit_end_fn(item)

            asyncio.ensure_future(__end_edit_async(item))

    def _edit_new(self, btn: int, item: WaypointItem):
        if btn == 0:
            if self._waypoint_instance:
                self._waypoint_instance.end_edit_waypoint(item.waypoint, False, create=True)
            self._container.visible = False
            if callable(self._on_edit_end_fn):
                self._on_edit_end_fn(item)

    def _edit_cancel(self, btn: int, item: WaypointItem):
        if btn == 0:
            if self._waypoint_instance:
                self._waypoint_instance.end_edit_waypoint(item.waypoint, False)
            self._container.visible = False
            if callable(self._on_edit_end_fn):
                self._on_edit_end_fn(item)

    def _on_edit_hovered(self, hovered: bool, item: WaypointItem):
        # Clear selected status to show hovered style
        self._apply_button.selected = False
        self._new_button.selected = False
        self._cancel_button.selected = False
