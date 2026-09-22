import math
from typing import List, Optional
import weakref

import carb.settings
from omni.kit.viewport.menubar.core import RadioMenuCollection, ViewportMenuDelegate, AbstractWidgetMenuDelegate
import omni.ui as ui

from .model import ResolutionComboBoxItem, ComboBoxResolutionModel


SETTING_CUSTOM_RESOLUTION_LIST = "/persistent/app/renderer/resolution/custom/list"

DEFAULT_RATIOS = {
    "16:9": float(16) / 9,
    "1:1": 1,
    "32:9": float(32) / 9,
    "4:3": float(4) / 3,
    "21:9": float(21) / 9,
}


class ResolutionCollectionDelegate(AbstractWidgetMenuDelegate):
    def __init__(self, model: ComboBoxResolutionModel):
        # don't use content_clipping as submenu hovering becomes inconsistent
        super().__init__(model=model, has_reset=True, content_clipping=False)
        self.__resolution_label: Optional[ui.Label] = None
        index_model = model.get_item_value_model(None, 0)
        self.__sub_index_change = index_model.subscribe_value_changed_fn(
            lambda _, this=weakref.proxy(self): this.__on_index_changed()  # noqa: PLW0212
        )

    def destroy(self):
        self.__sub_index_change = None

    def build_widget(self, item: ui.MenuHelper):
        ui.Spacer(width=4)
        ui.Label(item.text, width=0)
        ui.Spacer()
        self.__resolution_label = ui.Label(self.__get_current_resolution(), width=70)

    def __get_current_resolution(self):
        index = self._model.get_item_value_model(None, 0).as_int
        items: List[ResolutionComboBoxItem] = self._model.get_item_children(None)
        return items[index].name if index >= 0 and index < len(items) else "Unknown"

    def __on_index_changed(self) -> None:
        if self.__resolution_label:
            self.__resolution_label.text = self.__get_current_resolution()


class ResolutionCollectionMenu(RadioMenuCollection):
    ITEM_HEIGHT = 20

    def __init__(self, text: str, model: ComboBoxResolutionModel):
        super().__init__(
            text,
            model,
            delegate=ResolutionCollectionDelegate(model),
        )
        self.__custom_menu_items = {}

    def destroy(self):
        self.delegate.destroy()

    def build_menu_item(self, item: ResolutionComboBoxItem) -> ui.MenuItem:
        if item.resolution is None:
            return ui.Separator(
                delegate=ui.MenuDelegate(
                    on_build_item=lambda _: ui.Line(
                        height=0, alignment=ui.Alignment.V_CENTER, style_type_name_override="Menu.Separator"
                    )
                )
            )

        menu_item = ui.MenuItem(
            item.name,
            delegate=ViewportMenuDelegate(build_custom_widgets=lambda d, m, i=item: self.__build_resolution_menuitem_widgets(i)), identifier='RenderResolution'
        )
        if item.custom:
            self.__custom_menu_items[item.name] = menu_item
        return menu_item

    def __build_resolution_menuitem_widgets(self, item: ResolutionComboBoxItem):
        if item.is_valid_resolution():
            ui.Spacer()
            ui.Spacer(width=20)
            ui.Label(item.model.as_string, width=80, style_type_name_override="Resolution.Text")
            with ui.HStack(width=60):
                ratio = float(item.resolution[0]) / item.resolution[1]
                width = self.ITEM_HEIGHT * ratio
                with ui.ZStack(width=width):
                    ui.Rectangle(style_type_name_override="Ratio.Background")
                    ui.Label(self.get_ratio_text(ratio), alignment=ui.Alignment.CENTER, style_type_name_override="Ratio.Text")
                ui.Spacer()
            if item.custom:
                with ui.VStack(content_clipping=1, width=0):
                    ui.Image(width=20, style_type_name_override="Resolution.Del", mouse_pressed_fn=lambda x, y, b, f, i=item: self.__delete_resolution(i))
            else:
                ui.Spacer(width=20)

    def get_ratio_text(self, ratio: float):
        found = [key for (key, value) in DEFAULT_RATIOS.items() if math.isclose(value, ratio, rel_tol=1e-2)]
        return found[0] if found else f"{ratio: .2f}:1"

    def __delete_resolution(self, item: ResolutionComboBoxItem):
        settings = carb.settings.get_settings()
        custom_list = settings.get(SETTING_CUSTOM_RESOLUTION_LIST) or []
        for custom in custom_list:
            name = custom["name"]
            if name == item.name:
                custom_list.remove(custom)
                settings.set(SETTING_CUSTOM_RESOLUTION_LIST, custom_list)
                if item.name in self.__custom_menu_items:
                    self.__custom_menu_items[item.name].visible = False
