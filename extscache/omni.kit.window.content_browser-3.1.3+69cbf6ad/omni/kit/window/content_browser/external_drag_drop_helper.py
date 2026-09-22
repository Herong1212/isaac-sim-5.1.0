import os
import asyncio
import carb
import omni.client
import omni.appwindow
import omni.ui as ui
from typing import List, Tuple
from omni.kit.window.drop_support import ExternalDragDrop

external_drag_drop = None


def setup_external_drag_drop(window_name: str, browser_widget, window_frame: ui.Frame):
    global external_drag_drop
    destroy_external_drag_drop()
    external_drag_drop = ExternalDragDrop(window_name=window_name,
                                          drag_drop_fn=lambda e, p, a=browser_widget.api, f=window_frame: _on_ext_drag_drop(e, p, a, f))


def destroy_external_drag_drop():
    global external_drag_drop
    if external_drag_drop:
        external_drag_drop.destroy()
        external_drag_drop = None


def _cleanup_slashes(path: str, is_directory: bool = False) -> str:
    """
    Makes path/slashes uniform

    Args:
        path: path
        is_directory is path a directory, so final slash can be added

    Returns:
        path
    """
    path = os.path.normpath(path)
    path = path.replace("\\", "/")
    if is_directory:
        if path[-1] != "/":
            path += "/"

    return path


def _on_ext_drag_drop(edd: ExternalDragDrop, payload: List[str], api, frame: ui.Frame):
    import omni.kit.notification_manager

    def get_current_mouse_coords() -> Tuple[float, float]:
        app_window = omni.appwindow.get_default_app_window()
        input = carb.input.acquire_input_interface()
        dpi_scale = ui.Workspace.get_dpi_scale()
        pos_x, pos_y = input.get_mouse_coords_pixel(app_window.get_mouse())
        return pos_x / dpi_scale, pos_y / dpi_scale

    search_frame = api.tool_bar._search_frame
    search_delegate = api.tool_bar._search_delegate
    if search_delegate and search_frame and search_frame.visible:
        pos_x, pos_y = get_current_mouse_coords()
        if (pos_x > search_frame.screen_position_x and pos_y > search_frame.screen_position_y
                and pos_x < search_frame.screen_position_x + search_frame.computed_width
                and pos_y < search_frame.screen_position_y + search_frame.computed_height):
            if hasattr(search_delegate, "handle_drag_drop"):
                if search_delegate.handle_drag_drop(payload):
                    return

    target_dir = api.get_current_directory()
    if not target_dir:
        omni.kit.notification_manager.post_notification("No target directory", hide_after_timeout=False)
        return

    # get common source path
    common_path = ""
    if len(payload) > 1:
        common_path = os.path.commonpath(payload)
    if not common_path:
        common_path = os.path.dirname(payload[0])
    common_path = _cleanup_slashes(common_path, True)

    # get payload
    payload = edd.expand_payload(payload)

    # copy files
    async def do_copy():
        from .progress_popup import ProgressPopup
        from .file_ops import copy_item_async

        copy_cancelled = False

        def do_cancel_copy():
            nonlocal copy_cancelled
            copy_cancelled = True

        # show progress...
        waiting_popup = ProgressPopup("Copying...", status_text="Copying...")
        waiting_popup.status_text = "Copying..."
        waiting_popup.progress = 0.0
        waiting_popup.centre_in_window(frame)
        waiting_popup.set_cancel_fn(do_cancel_copy)
        waiting_popup.show()

        try:
            await omni.kit.app.get_app().next_update_async()

            current_file = 0
            total_files = len(payload)
            for file_path in payload:
                if copy_cancelled:
                    break
                file_path = _cleanup_slashes(file_path)
                target_path = target_dir.rstrip("/") + "/" + file_path.replace(common_path, "")

                # update progress
                waiting_popup.progress = float(current_file) / total_files
                waiting_popup.status_text = f"Copying {os.path.basename(target_path)}..."
                waiting_popup.centre_in_window(frame)

                # copy file
                # OM-90753: Route through same code path as normal copy item
                await copy_item_async(file_path, target_path)

                current_file += 1
        except Exception as exc:
            carb.log_error(f"error {exc}")

        await omni.kit.app.get_app().next_update_async()
        api.refresh_current_directory()
        waiting_popup.hide()
        del waiting_popup

    asyncio.ensure_future(do_copy())
