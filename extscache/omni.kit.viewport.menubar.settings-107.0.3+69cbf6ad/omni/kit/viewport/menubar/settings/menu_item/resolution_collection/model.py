import asyncio
from typing import Tuple, List, Optional

import carb.settings
import omni.kit.app
from omni.kit.viewport.menubar.core import ComboBoxItem, SettingComboBoxModel, ResetHelper

SETTING_RESOLUTION_LIST = "/app/renderer/resolution/list"
SETTING_CUSTOM_RESOLUTION_LIST = "/persistent/app/renderer/resolution/custom/list"

NAME_RESOLUTIONS = {
    "Icon": (512, 512),
    "Square": (1024, 1024),
    "SD": (1280, 960),
    "HD720P": (1280, 720),
    "HD1080P": (1920, 1080),
    "2K": (2048, 1080),
    "1440P": (2560, 1440),
    "UHD": (3840, 2160),
    "Ultra Wide": (3440, 1440),
    "Super Ultra Wide": (3840, 1440),
    "5K Wide": (5120, 2880),
}


class ResolutionComboBoxItem(ComboBoxItem):
    def __init__(self, resolution: Tuple[int, int], name: Optional[str] = None, custom: bool = False) -> None:
        self.resolution = resolution
        self.name = name if name else self.get_name_from_resolution(resolution)
        text = f"{resolution[0]}x{resolution[1]}" if self.is_valid_resolution() else self.name
        self.custom = custom
        super().__init__(text, resolution if resolution else "")

    def get_name_from_resolution(self, resolution: Tuple[int, int]) -> str:
        for name, res in NAME_RESOLUTIONS.items():
            if res == resolution:
                return name
        return ""

    def is_valid_resolution(self):
        return self.resolution and self.resolution[0] > 0 and self.resolution[1] > 0


class ComboBoxResolutionModel(SettingComboBoxModel, ResetHelper):
    """The resolution model has all the resolutions and sets the viewport resolution"""
    def __init__(self, resolution_setter, resolution_setting, settings):
        # Parse the incoming resolution list via settings
        self.__resolution_setter = resolution_setter
        # Set the default restore to value based on the resolved default pref-key
        self.__default = resolution_setting[1][1]
        self.__default = tuple(self.__default) if self.__default else (0, 0)
        self.__custom_items: List[ResolutionComboBoxItem] = []
        # XXX: For test-suite which passes None!
        full_resolution = resolution_setter.full_resolution if resolution_setter else (0, 0)

        values = None
        try:
            sttg_values = settings.get(SETTING_RESOLUTION_LIST)
            if sttg_values is not None:
                num_values = len(sttg_values)
                if num_values > 0 and num_values % 2 == 0:
                    values = [(sttg_values[i * 2 + 0], sttg_values[i * 2 + 1]) for i in range(int(num_values / 2))]
                else:  # pragma: no cover
                    raise RuntimeError(f"Resolution list has invalid length of {num_values}")
        except Exception as e:  # pragma: no cover  # noqa: PLW0718
            import traceback
            carb.log_error(f"{e}")
            carb.log_error(f"{traceback.format_exc()}")

        if values is None:  # pragma: no cover
            values = [(3840, 2160), (2560, 1440), (2048, 1080), (1920, 1080), (1280, 720), (1024, 1024), (512, 512)]

        SettingComboBoxModel.__init__(
            self,
            # Set the key to set to to the persistent per-viewport key
            setting_path=resolution_setting[0][0],
            # Filled in below
            texts=[],
            values=[],
            # Set the current value to the resolved persistent per-viewport value
            # This is passed to avoid defaulting the per-viewport persitent key to a value so that changes to the
            # setting when not adjusted/saved will pick up the new default
            current_value=full_resolution,
        )
        ResetHelper.__init__(self)

        self._items.append(ResolutionComboBoxItem((0, 0), name="Viewport"))
        for value in values:
            self._items.append(ResolutionComboBoxItem(value))

        # Separator
        self._items.append(ResolutionComboBoxItem(None))

        self._items.append(ResolutionComboBoxItem((-1, -1), "Custom"))
        # Custom is the last one
        self.__index_custom = len(self._items) - 1

        current = self._get_current_index_by_value(full_resolution)
        self.current_index.set_value(current)

        self.__update_setting = omni.kit.app.SettingChangeSubscription(SETTING_CUSTOM_RESOLUTION_LIST, self.__on_custom_change)
        self.__on_custom_change(None, carb.settings.ChangeEventType.CHANGED)

    def destroy(self):
        self.__update_setting = None
        self.__resolution_setter = None
        self.__custom_items = []

    def _on_current_item_changed(self, item: ResolutionComboBoxItem) -> None:
        value = item.value
        if value[0] >= 0 and value[1] >= 0:
            super()._on_current_item_changed(item)
            if self.__resolution_setter:
                self.__resolution_setter.set_resolution(value)
            self._update_reset_button()

    def get_item_children(self, item) -> List[ResolutionComboBoxItem]:
        if item is None:
            items = []
            items.extend(self._items)
            items.extend(self.__custom_items)
            return items

        return []  # pragma: no cover

    # for ResetHelper
    def get_default(self):
        return self.__default

    def restore_default(self) -> None:
        if self.__default is None:
            return

        current_index = self.current_index
        if current_index:
            current = current_index.as_int
            items = self.get_item_children(None)
            # Early exit if the model is already correct
            if items[current].value == self.__default:
                return
            # Iterate all items, and select the first match to the real value
            for index, item in enumerate(items):
                if item.value == self.__default:
                    current_index.set_value(index)
                    return

            current_index.set_value(3)

    def get_value(self) -> Optional[Tuple[int, int]]:
        if self.__resolution_setter:
            return self.__resolution_setter.full_resolution
        return None

    def is_custom(self, resolution: Tuple[int, int]) -> bool:
        return any(custom.value == resolution for custom in self.__custom_items)

    @property
    def fill_frame(self) -> bool:
        return self.__resolution_setter.fill_frame if self.__resolution_setter else False

    def __on_custom_change(self, value, event_type) -> None:
        async def __refresh_custom():
            # It is strange that sometimes it is triggered with not all fields updated.
            # Update a frame to make sure full information filled
            await omni.kit.app.get_app().next_update_async()
            self.__custom_items = []
            custom_list = carb.settings.get_settings().get(SETTING_CUSTOM_RESOLUTION_LIST) or []
            if custom_list:
                # Separator
                self.__custom_items.append(ResolutionComboBoxItem(None))

            for custom in custom_list:
                name = custom.pop("name", "")
                width = custom.pop("width", -1)
                height = custom.pop("height", -1)
                if name and width > 0 and height > 0:
                    self.__custom_items.append(ResolutionComboBoxItem((width, height), name=name, custom=True))

            self._item_changed(None)

            if self.__resolution_setter:
                current = self._get_current_index_by_value(self.__resolution_setter.full_resolution, default=self.__index_custom)
                self.current_index.set_value(current)

        asyncio.ensure_future(__refresh_custom())
