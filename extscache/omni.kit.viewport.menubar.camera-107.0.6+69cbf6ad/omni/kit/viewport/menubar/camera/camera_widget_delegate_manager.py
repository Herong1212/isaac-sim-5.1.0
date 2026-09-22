from pxr import Sdf

from .abstract_camera_widget_delegate import AbstractCameraButtonDelegate, AbstractCameraMenuItemDelegate


class CameraWidgetDelegateManager:

    def destroy(self):
        for delegate in AbstractCameraButtonDelegate.get_instances():
            delegate.destroy()

        for delegate in AbstractCameraMenuItemDelegate.get_instances():
            delegate.destroy()

    def __get_all_delegates(self, camera_button_or_menu_item: bool):
        all_widget_delegates = []

        if camera_button_or_menu_item:
            for delegate in AbstractCameraButtonDelegate.get_instances():
                all_widget_delegates.append(delegate)
        else:
            for delegate in AbstractCameraMenuItemDelegate.get_instances():
                all_widget_delegates.append(delegate)

        # Sort list in ascending order.
        all_widget_delegates.sort(key=lambda item: item.order)

        return all_widget_delegates

    def build_widgets(
        self, parent_id, viewport_api, camera_path: Sdf.Path, camera_button_or_menu_item: bool
    ):
        """Build all camera widgets for specific camera path with sort based on their orders."""

        all_widget_delegates = self.__get_all_delegates(camera_button_or_menu_item)
        for delegate in all_widget_delegates:
            delegate.build_widget(parent_id, viewport_api, camera_path)

    def on_parent_destroyed(self, parent_id, camera_button_or_menu_item: bool) -> None:
        # Clean up when parent widget destroyed

        all_widget_delegates = self.__get_all_delegates(camera_button_or_menu_item)
        for delegate in all_widget_delegates:
            delegate.on_parent_destroyed(parent_id)

    def on_camera_path_changed(self, parent_id, camera_path, camera_button_or_menu_item: bool):
        """The camera tracked has changed."""
        all_widget_delegates = self.__get_all_delegates(camera_button_or_menu_item)
        for delegate in all_widget_delegates:
            delegate.on_camera_path_changed(parent_id, camera_path)
