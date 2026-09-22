"""This module provides the ExternalDragDrop class to handle external drag and drop events for application windows in the omni.kit.window.drop_support package."""

import os
import asyncio
import carb.events
import carb.input
import omni.appwindow
import omni.ui as ui


class ExternalDragDrop:
    """A class to handle external drag and drop events for a specified window.

    The class subscribes to drag and drop events on the application's main window and invokes a callback function when an event is detected over the specified window area. It also provides utility functions to check mouse coordinates and expand drag and drop payloads that contain directories.

    Args:
        window_name (str): The name of the window to monitor for drag/drop events.
        drag_drop_fn (callable): The callback function to invoke on a drag/drop event."""

    def __init__(self, window_name: str, drag_drop_fn: callable):
        """Initializes the ExternalDragDrop with a window name and a drag and drop function."""
        self._window_name = window_name
        self._drag_drop_fn = drag_drop_fn

        # subscribe to external drag/drop events
        app_window = omni.appwindow.get_default_app_window()
        if app_window:
            self._dropsub = app_window.get_window_drop_event_stream().create_subscription_to_pop(
                self._on_drag_drop_external, name="ExternalDragDrop event", order=0
            )
        else:
            carb.log_error("Cannot setup ExternalDragDrop without a default window")


    def destroy(self):
        """Cleans up the resources and subscriptions held by the class instance."""
        self._drag_drop_fn = None
        self._dropsub = None

    def get_current_mouse_coords(self):
        """Retrieves the current mouse coordinates scaled by the DPI scale."""
        app_window = omni.appwindow.get_default_app_window()
        input = carb.input.acquire_input_interface()
        dpi_scale = ui.Workspace.get_dpi_scale()
        pos_x, pos_y = input.get_mouse_coords_pixel(app_window.get_mouse())
        return pos_x / dpi_scale, pos_y / dpi_scale

    def is_window_hovered(self, pos_x, pos_y, window_name):
        """Checks if the mouse is hovering over the specified window.

        Args:
            pos_x (float): The x-coordinate of the mouse position.
            pos_y (float): The y-coordinate of the mouse position.
            window_name (str): The name of the window to check against.

        Returns:
            bool: True if the mouse is hovering over the window, False otherwise."""
        window = ui.Workspace.get_window(window_name)
        # if window hasn't been drawn yet docked may not be valid, so check dock_id also
        if (
            not window
            or not window.visible
            or ((window.docked or window.dock_id != 0) and not window.is_selected_in_dock())
        ):
            return False

        if (
            pos_x > window.position_x
            and pos_y > window.position_y
            and pos_x < window.position_x + window.width
            and pos_y < window.position_y + window.height
        ):
            return True
        return False

    def _on_drag_drop_external(self, e: carb.events.IEvent):
        # need to wait until next frame as otherwise mouse coords can be wrong
        async def do_drag_drop():
            await omni.kit.app.get_app().next_update_async()
            mouse_x, mouse_y = self.get_current_mouse_coords()
            if self.is_window_hovered(mouse_x, mouse_y, self._window_name):
                self._drag_drop_fn(self, list(e.payload["paths"]))

        asyncio.ensure_future(do_drag_drop())

    def expand_payload(self, payload):
        """Expands payload to include all files within any directories.

        Args:
            payload (list of str): A list of file paths to expand.

        Returns:
            list of str: A new list of file paths including files within directories in the payload."""
        new_payload = []
        for file_path in payload:
            if os.path.isdir(file_path):
                for root, subdirs, files in os.walk(file_path):
                    for file in files:
                        new_payload.append(os.path.join(root, file))
            else:
                new_payload.append(file_path)
        return new_payload
