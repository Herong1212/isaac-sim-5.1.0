from .singleton import Singleton


@Singleton
class LayerColorScheme:
    def __init__(self):
        import carb.settings

        self._style = carb.settings.get_settings().get_as_string("/persistent/app/window/uiStyle") or "NvidiaDark"

        # For now, the style is uniform for dark and light
        self.EDIT_TARGET_BACKGROUND_COLOR = 0x668A8778
        self.NON_EDIT_TARGET_BACKGROUND_COLOR = 0x0

        self.LAYER_LABEL_DISABLED = 0xFFA0A0A0
        self.LAYER_LABEL_MISSING = 0xFF6F72FF

        self.LAYER_LABEL_MISSING_SELECTED = 0xFF2424AE
        if self._style == "NvidiaDark":
            self.LAYER_LABEL_NORMAL = 0xFF8A8777
        else:
            self.LAYER_LABEL_NORMAL = 0xFF535354

        self.LAYER_MUTE_BUTTON_DISABLED = 0xFF808080
        self.LAYER_MUTE_BUTTON_ENABLED = 0xFFFFFFFF

        self.LAYER_SAVE_BUTTON_NOT_DIRTY = 0xFF808080
        self.LAYER_SAVE_BUTTON_DIRTY = 0xFFFF901E
        self.LAYER_SAVE_BUTTON_READ_ONLY = 0xFF6F72FF

        self.LAYER_LIVE_MODE_BUTTON_DISABLED = 0xFF808080
        self.LAYER_LIVE_MODE_BUTTON_ENABLED = 0xFF00B976

        self.LAYER_LOCK_BUTTON_LOCKED_BY_ME = 0xFFFF901E
        self.OUTDATED = 0xFF0097FF
