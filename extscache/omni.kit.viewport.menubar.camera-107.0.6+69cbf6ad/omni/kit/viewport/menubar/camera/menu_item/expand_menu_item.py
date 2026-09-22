from typing import Optional
import omni.ui as ui


class _ExpandButtonDelegate(ui.MenuDelegate):
    """Simple button with left arrow"""

    def __init__(self, expanded: bool, **kwargs):
        self._expanded = expanded
        self.__icon: Optional[ui.Widget] = None
        super().__init__(**kwargs)

    def build_item(self, item: ui.MenuHelper):
        icon_type = "Menu.Item.Icon"
        self.__icon = ui.ImageWithProvider(
            style_type_name_override=icon_type,
            name="Expand",
            checked=self._expanded,
            width=20,
            height=30,
            fill_policy=ui.IwpFillPolicy.IWP_PRESERVE_ASPECT_FIT,
        )

    @property
    def checked(self) -> bool:
        return self._expanded

    @checked.setter
    def checked(self, value: bool):
        self._expanded = value
        if self.__icon:
            self.__icon.checked = value


class ExpandMenuItem(ui.MenuItem):
    def __init__(self, expand_model):
        self.__model = expand_model

        super().__init__(
            "Expand",
            delegate=_ExpandButtonDelegate(self.__model.as_bool),
            triggered_fn=lambda: self.__model.set_value(not self.__model.as_bool),
            identifier="viewport.camera.expand",
        )

    @property
    def checked(self):
        return self.delegate.checked

    @checked.setter
    def checked(self, value: bool):
        self.delegate.checked = value
