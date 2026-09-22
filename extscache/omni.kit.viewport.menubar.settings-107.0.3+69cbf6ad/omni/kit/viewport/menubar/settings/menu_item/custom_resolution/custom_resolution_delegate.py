import asyncio
import math
from typing import List, Optional, Callable, Tuple
import weakref

import carb.settings
import omni.kit.app
from omni.kit.viewport.menubar.core import AbstractWidgetMenuDelegate
import omni.ui as ui

from .save_window import SaveWindow


SETTING_CUSTOM_RESOLUTION_LIST = "/persistent/app/renderer/resolution/custom/list"
SETTING_MIN_RESOLUTION = "/exts/omni.kit.viewport.menubar.settings/min_resolution"


class RatioItem(ui.AbstractItem):
    def __init__(self, text: str, value: float) -> None:
        super().__init__()
        self.model = ui.SimpleStringModel(text)
        self.value = value


class RatioModel(ui.AbstractItemModel):
    """
    The model used for ratio combobox
    """

    def __init__(self):
        super().__init__()

        # List items
        self.__default_items = [
            RatioItem("16:9", 16.0 / 9),
            RatioItem("4:3", 4.0 / 3),
            RatioItem("1:1", 1.0)
        ]

        self.__custom_item: Optional[RatioItem] = None

        # Current value
        self.current_index = ui.SimpleIntModel(-1)
        self._sub = self.current_index.subscribe_value_changed_fn(
            lambda _, this=weakref.proxy(self): this.__on_index_changed()  # noqa: PLW0212
        )

    def destroy(self):
        self._sub = None
        self.current_index = None

    @property
    def ratio(self) -> float:
        items = self.get_item_children(None)
        return items[self.current_index.as_int].value

    @ratio.setter
    def ratio(self, value: float) -> None:
        found = [index for (index, item) in enumerate(self.__default_items) if math.isclose(item.value, value, rel_tol=1e-2)]
        if found:
            self.__custom_item = None
            self.current_index.set_value(found[0])
            self._item_changed(None)
        else:
            ratio_text = f"{value: .2f}:1"
            self.__custom_item = RatioItem(ratio_text, value)
            self.current_index.set_value(0)
            self._item_changed(None)

    def subscribe_ratio_changed_fn(self, on_ratio_changed_fn: Callable[[float], None]):
        def __on_sub_index_changed(this, callback):
            current_index = this.current_index.as_int
            items = this.get_item_children(None)
            callback(items[current_index].value)

        return self.current_index.subscribe_value_changed_fn(
            lambda _, this=weakref.proxy(self), callback=on_ratio_changed_fn: __on_sub_index_changed(this, callback)
        )

    def get_item_children(self, item) -> List[RatioItem]:
        items = []
        if self.__custom_item:
            items.append(self.__custom_item)
        items.extend(self.__default_items)
        return items

    def get_item_value_model(self, item, column_id):
        if item is None:
            return self.current_index
        return item.model

    def __on_index_changed(self):
        self._item_changed(None)


class CustomResolutionDelegate(AbstractWidgetMenuDelegate):
    """
    Delegate to edit/save custom resolution.
    """
    def __init__(self, resolution_model, resolution_setter):
        super().__init__(width=310, has_reset=False)

        self.__resolution_model = resolution_model
        self.__resolution_setter = resolution_setter
        self.__link_button: Optional[ui.Button] = None
        self.__save_button: Optional[ui.Button] = None
        self.__save_window: Optional[SaveWindow] = None
        self.__settings = carb.settings.get_settings()
        (self.__resolution_min_width, self.__resolution_min_height) = self.__settings.get(SETTING_MIN_RESOLUTION) or [64, 64]
        self.width_model = ui.SimpleIntModel(1920)
        self.__sub_width_begin_edit = self.width_model.subscribe_begin_edit_fn(lambda _: self.__on_begin_edit())
        self.__sub_width_end_edit = self.width_model.subscribe_end_edit_fn(lambda _: self.__on_width_end_edit())
        self.height_model = ui.SimpleIntModel(1080)
        self.__sub_height_begin_edit = self.height_model.subscribe_begin_edit_fn(lambda _: self.__on_begin_edit())
        self.__sub_height_end_edit = self.height_model.subscribe_end_edit_fn(lambda _: self.__on_height_end_edit())
        self.ratio_model = RatioModel()
        self.__sub_ratio_change = None

        self.__subscribe_ratio_change()

    def destroy(self):
        self.ratio_model.destroy()
        self.__sub_ratio_change = None
        self.__sub_width_begin_edit = None
        self.__sub_width_end_edit = None
        self.__sub_height_begin_edit = None
        self.__sub_height_end_edit = None

    @property
    def resolution(self) -> Tuple[int, int]:
        return (self.width_model.as_int, self.height_model.as_int)

    @resolution.setter
    def resolution(self, res: Tuple[int, int]) -> None:
        if res[0] == -1 and res[1] == -1:
            # "Custom" selected
            self.__update_save_image_state()
        elif res[0] > 0 and res[1] > 0:
            if self.width_model.as_int == res[0] and self.height_model.as_int == res[1]:
                return
            was_r_subscibed = self.__subscribe_ratio_change(enable=False)
            self.ratio_model.ratio = res[0] / res[1]
            self.width_model.set_value(res[0])
            self.height_model.set_value(res[1])
            self.__subscribe_ratio_change(enable=was_r_subscibed)
            self.__update_save_image_state()

    def build_widget(self, item: ui.MenuHelper):
        with ui.VStack(spacing=0):
            ui.Spacer(height=0, spacing=4)
            with ui.HStack():
                ui.Spacer(width=8)

                ui.IntField(self.width_model, width=60, height=20)
                ui.Spacer(width=10)
                self.__link_button = ui.Button(
                    width=35,
                    image_height=20,
                    image_width=24,
                    checked=True,
                    clicked_fn=self.__on_link_clicked,
                    style_type_name_override="ResolutionLink",
                )
                ui.Spacer(width=10)
                ui.IntField(self.height_model, width=60, height=20)

                ui.Spacer(width=10)
                ui.ComboBox(self.ratio_model, name="ratio")
                ui.Spacer(width=10)

                with ui.VStack(width=0, content_clipping=True):
                    self.__save_button = ui.Button(
                        style_type_name_override="Menu.Item.Button",
                        name="save",
                        width=20,
                        height=20,
                        image_width=20,
                        image_height=20,
                        clicked_fn=self.__save
                    )
                ui.Spacer(width=4)

            with ui.HStack():
                ui.Spacer(width=8)
                ui.Label("Width", alignment=ui.Alignment.LEFT, width=60)
                ui.Spacer(width=54)
                ui.Label("Height", alignment=ui.Alignment.LEFT, width=60)
                ui.Spacer()

    def __on_width_changed(self, model):
        width = model.as_int
        if width < self.__resolution_min_width:
            self.__post_resolution_warning()
            model.set_value(self.__resolution_min_width)
            width = model.as_int
        if self.__link_button:
            if self.__link_button.checked:
                height = int(width / self.ratio_model.ratio)
                if height < self.__resolution_min_height:
                    # Height is too small, change width to match the min height
                    self.__post_resolution_warning()
                    height = self.__resolution_min_height
                    width = int(height * self.ratio_model.ratio)
                    model.set_value(width)
                if height != self.height_model.as_int:
                    self.height_model.set_value(height)
            else:
                self.ratio_model.ratio = float(width) / self.height_model.as_int

        self.__set_render_resolution(self.resolution)
        self.__update_save_image_state()

    def __on_height_changed(self, model):
        height = model.as_int
        if height < self.__resolution_min_height:
            self.__post_resolution_warning()
            model.set_value(self.__resolution_min_height)
            height = model.as_int
        if self.__link_button:
            if self.__link_button.checked:
                width = int(height * self.ratio_model.ratio)
                if width < self.__resolution_min_width:
                    # Width is too small, change height to match min width
                    self.__post_resolution_warning()
                    width = self.__resolution_min_width
                    height = int(width / self.ratio_model.ratio)
                    model.set_value(height)
                if width != self.width_model.as_int:
                    self.width_model.set_value(width)
            else:
                self.ratio_model.ratio = float(self.width_model.as_int) / height

        self.__set_render_resolution(self.resolution)
        self.__update_save_image_state()

    def __on_ratio_changed(self, ratio: float):
        height = int(self.width_model.as_int / self.ratio_model.ratio)
        if height != self.height_model.as_int:
            self.height_model.set_value(height)
            self.__set_render_resolution(self.resolution)
            self.__update_save_image_state()

    def __on_link_clicked(self):
        self.__link_button.checked = not self.__link_button.checked

    def __subscribe_ratio_change(self, enable: bool = True) -> bool:
        was_subscribed = self.__sub_ratio_change is not None
        if enable:
            if not was_subscribed:
                self.__sub_ratio_change = self.ratio_model.subscribe_ratio_changed_fn(self.__on_ratio_changed)
        elif was_subscribed:
            self.__sub_ratio_change = None
        return was_subscribed

    def __save(self):
        if self.__save_button.checked:
            if self.__save_window:
                self.__save_window = None
            self.__save_window = SaveWindow(self.resolution, self.__on_save_resolution)

    def __update_save_image_state(self):
        if not self.__save_button:
            return
        for item in self.__resolution_model.get_item_children(None):
            if self.resolution == item.value:
                self.__save_button.checked = False
                break
        else:
            self.__save_button.checked = True

    def __on_save_resolution(self, new_name: str, resolution: Tuple[int, int]) -> bool:
        custom_list = self.__settings.get(SETTING_CUSTOM_RESOLUTION_LIST) or []
        for custom in custom_list:
            name = custom["name"]
            if name == new_name:
                carb.log_warn("f{new_name} already exists!")
                return False

        custom_list.append(
            {
                "name": new_name,
                "width": resolution[0],
                "height": resolution[1]
            }
        )
        self.__settings.set(SETTING_CUSTOM_RESOLUTION_LIST, custom_list)
        self.__save_button.checked = False
        return True

    def __set_render_resolution(self, resolution: Tuple[int, int]):
        async def __delay_async(res: Tuple[int, int]):
            # Delay a frame to make sure current changes from UI are saved
            await omni.kit.app.get_app().next_update_async()
            self.__resolution_setter.set_resolution(res)

        asyncio.ensure_future(__delay_async(resolution))

    def __on_begin_edit(self):
        self.__saved_width = self.width_model.as_int
        self.__saved_height = self.height_model.as_int

    def __on_width_end_edit(self):
        if self.width_model.as_int <= 0:
            self.width_model.set_value(self.__saved_width)
        self.__on_width_changed(self.width_model)

    def __on_height_end_edit(self):
        if self.height_model.as_int <= 0:
            self.height_model.set_value(self.__saved_height)
        self.__on_height_changed(self.height_model)

    def __post_resolution_warning(self):
        try:
            import omni.kit.notification_manager as nm
            nm.post_notification(f"Resolution cannot be lower than {self.__resolution_min_width}x{self.__resolution_min_height}", status=nm.NotificationStatus.WARNING)
        except ImportError:
            carb.log_warn(f"Resolution cannot be lower than {self.__resolution_min_width}x{self.__resolution_min_height}")
