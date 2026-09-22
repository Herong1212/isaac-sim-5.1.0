__all__ = ["LayerSettings"]
import carb.settings
import omni.kit.usd.layers as layers

from .singleton import Singleton

SETTINGS_SHOW_SESSION_LAYER = "/persistent/app/layerwindow/showSessionLayer"
SETTINGS_SHOW_METRICSASSEMBLER_LAYER = "/persistent/app/layerwindow/showMetricsAssemblerLayer"
SETTINGS_SHOW_LAYER_CONTENTS = "/persistent/app/layerwindow/showLayerContents"
SETTINGS_SHOW_LAYER_FILE_EXTENSION = "/persistent/app/layerwindow/showLayerFileExtension"
SETTINGS_FILE_DIALOG_SHOW_ROOT_LAYER_LOCATION = "/persistent/app/layerwindow/filedialog/showRootLayerLocation"
SETTINGS_SHOW_INFO_NOTIFICATION = "/persistent/app/layerwindow/showInfoNotification"
SETTINGS_SHOW_WARNING_NOTIFICATION = "/persistent/app/layerwindow/showWarningNotification"
SETTINGS_ENABLE_AUTO_AUTHORING_MODE = "/persistent/app/layerwindow/enableAutoAuthoringMode"
SETTINGS_ENABLE_SPEC_LINKING_MODE = "/persistent/app/layerwindow/enableSpecLinkingMode"
SETTINGS_SHOW_MISSING_REFERENCE = "/persistent/app/layerwindow/showMissingReference"
SETTINGS_SHOW_MERGE_OR_FLATTEN_WARNING = "/persistent/app/layerwindow/showMergeOrFlattenWarning"
SETTINGS_CONTINOUS_UPDATE_IN_AUTO_AUTHORING = "/persistent/app/layersinterface/continousUpdate"

@Singleton
class LayerSettings:
    def __init__(self):
        super().__init__()
        self._settings = carb.settings.get_settings()
        self._settings.set_default_bool(layers.SETTINGS_AUTO_RELOAD_SUBLAYERS, False)
        self._settings.set_default_bool(SETTINGS_SHOW_LAYER_CONTENTS, True)
        self._settings.set_default_bool(SETTINGS_SHOW_SESSION_LAYER, False)
        self._settings.set_default_bool(SETTINGS_SHOW_METRICSASSEMBLER_LAYER, False)
        self._settings.set_default_bool(SETTINGS_SHOW_LAYER_FILE_EXTENSION, True)
        self._settings.set_default_bool(SETTINGS_FILE_DIALOG_SHOW_ROOT_LAYER_LOCATION, True)
        self._settings.set_default_bool(SETTINGS_SHOW_INFO_NOTIFICATION, True)
        self._settings.set_default_bool(SETTINGS_SHOW_WARNING_NOTIFICATION, True)
        self._settings.set_default_bool(SETTINGS_ENABLE_AUTO_AUTHORING_MODE, False)
        self._settings.set_default_bool(SETTINGS_ENABLE_SPEC_LINKING_MODE, False)
        self._settings.set_default_bool(SETTINGS_SHOW_MISSING_REFERENCE, False)
        self._settings.set_default_bool(SETTINGS_SHOW_MERGE_OR_FLATTEN_WARNING, True)
        self._settings.set_default_bool(SETTINGS_CONTINOUS_UPDATE_IN_AUTO_AUTHORING, True)

    @property
    def auto_reload_sublayers(self):
        return self._settings.get_as_bool(layers.SETTINGS_AUTO_RELOAD_SUBLAYERS)

    @auto_reload_sublayers.setter
    def auto_reload_sublayers(self, value):
        self._settings.set(layers.SETTINGS_AUTO_RELOAD_SUBLAYERS, value)

    @property
    def continuous_update_in_auto_authoring(self):
        return self._settings.get_as_bool(SETTINGS_CONTINOUS_UPDATE_IN_AUTO_AUTHORING)

    @continuous_update_in_auto_authoring.setter
    def continuous_update_in_auto_authoring(self, value):
        self._settings.set(SETTINGS_CONTINOUS_UPDATE_IN_AUTO_AUTHORING, value)

    @property
    def show_missing_reference(self):
        return self._settings.get_as_bool(SETTINGS_SHOW_MISSING_REFERENCE)

    @show_missing_reference.setter
    def show_missing_reference(self, show: bool):
        self._settings.set(SETTINGS_SHOW_MISSING_REFERENCE, show)

    @property
    def show_layer_contents(self):
        return self._settings.get_as_bool(SETTINGS_SHOW_LAYER_CONTENTS)

    @show_layer_contents.setter
    def show_layer_contents(self, show: bool):
        self._settings.set(SETTINGS_SHOW_LAYER_CONTENTS, show)

    @property
    def show_session_layer(self):
        return self._settings.get_as_bool(SETTINGS_SHOW_SESSION_LAYER)

    @show_session_layer.setter
    def show_session_layer(self, show: bool):
        self._settings.set(SETTINGS_SHOW_SESSION_LAYER, show)

    @property
    def show_metricsassembler_layer(self):
        return self._settings.get_as_bool(SETTINGS_SHOW_METRICSASSEMBLER_LAYER)

    @show_metricsassembler_layer.setter
    def show_metricsassembler_layer(self, show: bool):
        self._settings.set(SETTINGS_SHOW_METRICSASSEMBLER_LAYER, show)

    @property
    def show_layer_file_extension(self):
        return self._settings.get_as_bool(SETTINGS_SHOW_LAYER_FILE_EXTENSION)

    @show_layer_file_extension.setter
    def show_layer_file_extension(self, show: bool):
        self._settings.set(SETTINGS_SHOW_LAYER_FILE_EXTENSION, show)

    # The default location of file dialog. By default, it will be the root layer's location if it's not
    # anonymous. Otherwise, it will be last access location.
    @property
    def file_dialog_show_root_layer_location(self):
        return self._settings.get_as_bool(SETTINGS_FILE_DIALOG_SHOW_ROOT_LAYER_LOCATION)

    @file_dialog_show_root_layer_location.setter
    def file_dialog_show_root_layer_location(self, root_layer: bool):
        self._settings.set(SETTINGS_FILE_DIALOG_SHOW_ROOT_LAYER_LOCATION, root_layer)

    @property
    def show_info_notification(self):
        return self._settings.get_as_bool(SETTINGS_SHOW_INFO_NOTIFICATION)

    @show_info_notification.setter
    def show_info_notification(self, enabled: bool):
        self._settings.set(SETTINGS_SHOW_INFO_NOTIFICATION, enabled)

    @property
    def show_warning_notification(self):
        return self._settings.get_as_bool(SETTINGS_SHOW_WARNING_NOTIFICATION)

    @show_warning_notification.setter
    def show_warning_notification(self, enabled: bool):
        self._settings.set(SETTINGS_SHOW_WARNING_NOTIFICATION, enabled)

    @property
    def enable_auto_authoring_mode(self):
        return self._settings.get_as_bool(SETTINGS_ENABLE_AUTO_AUTHORING_MODE)

    @enable_auto_authoring_mode.setter
    def enable_auto_authoring_mode(self, enabled: bool):
        self._settings.set(SETTINGS_ENABLE_AUTO_AUTHORING_MODE, enabled)
        if enabled:
            self._settings.set(SETTINGS_ENABLE_SPEC_LINKING_MODE, False)

    @property
    def enable_spec_linking_mode(self):
        return self._settings.get_as_bool(SETTINGS_ENABLE_SPEC_LINKING_MODE)

    @enable_spec_linking_mode.setter
    def enable_spec_linking_mode(self, enabled: bool):
        self._settings.set(SETTINGS_ENABLE_SPEC_LINKING_MODE, enabled)
        if enabled:
            self._settings.set(SETTINGS_ENABLE_AUTO_AUTHORING_MODE, False)

    @property
    def show_merge_or_flatten_warning(self):
        return self._settings.get_as_bool(SETTINGS_SHOW_MERGE_OR_FLATTEN_WARNING)

    @show_merge_or_flatten_warning.setter
    def show_merge_or_flatten_warning(self, enabled: bool):
        self._settings.set(SETTINGS_SHOW_MERGE_OR_FLATTEN_WARNING, enabled)

    @property
    def ignore_outdate_notification(self):
        return self._settings.get_as_bool(layers.SETTINGS_IGNORE_OUTDATE_NOTIFICATION)

    @ignore_outdate_notification.setter
    def ignore_outdate_notification(self, value: bool):
        self._settings.set(layers.SETTINGS_IGNORE_OUTDATE_NOTIFICATION, value)
