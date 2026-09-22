from typing import Tuple
import omni.ui as ui
from .custom_resolution_delegate import CustomResolutionDelegate


class CustomResolutionMenuItem(ui.MenuItem):
    """
    Menu item to edit/save custom resolution.
    """
    def __init__(self, res_model, res_setter):
        self.__delegate = CustomResolutionDelegate(res_model, res_setter)
        ui.MenuItem(
            "Custom Resolution",
            delegate=self.__delegate,
            hide_on_click=False,
        )
        super().__init__("Custom Resolution")

    def destroy(self):
        self.__delegate.destroy()

    @property
    def resolution(self) -> Tuple[int, int]:
        return self.__delegate.resolution

    @resolution.setter
    def resolution(self, res: Tuple[int, int]) -> None:
        self.__delegate.resolution = res
