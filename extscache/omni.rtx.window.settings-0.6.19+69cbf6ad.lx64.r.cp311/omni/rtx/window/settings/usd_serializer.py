__all__ = ["USDSettingsSerialiser"]

import os.path

import carb
import omni.kit.commands
import rtx.settings
from omni.rtx.window.settings.rendersettingsdefaults import RenderSettingsDefaults
from pxr import Gf, Usd


class USDSettingsSerialiser:
    """
    Save and Load RTX settings to/from USD

    @TOOD:
    get rtx:fog:fogColor working
    """

    def __init__(self):
        self._settings = carb.settings.get_settings()

    def iterate_settings(self, usd_dict, d, path_string=""):
        for k, v in d.items():
            key_string = path_string + "/" + str(k)

            if isinstance(v, dict):
                self.iterate_settings(usd_dict, v, path_string=path_string + "/" + k)
            else:
                default_flags = self._settings.get(rtx.settings.get_associated_setting_flags_path(key_string))
                if default_flags is None or (default_flags & rtx.settings.SETTING_FLAGS_TRANSIENT):
                    continue

                val = self._settings.get(key_string)
                default_key = RenderSettingsDefaults._get_associated_defaults_path(key_string)
                default_val = self._settings.get(default_key)
                usd_str = key_string.replace("/", ":")
                if default_val != val:
                    # TODO: This code looks fairly dodgy
                    if isinstance(val, list) and len(val) in [3, 4]:
                        if isinstance(val[0], float):
                            usd_dict[usd_str[1:]] = Gf.Vec3f(val)
                        else:
                            usd_dict[usd_str[1:]] = Gf.Vec3d(val)
                    else:
                        usd_dict[usd_str[1:]] = val

    def save_to_usd(self, stage_file_path=""):

        if os.path.exists(stage_file_path):
            curr_stage = Usd.Stage.Open(stage_file_path)  # Save or overwrite
        else:
            curr_stage = Usd.Stage.CreateNew(stage_file_path)

        rootLayer = curr_stage.GetRootLayer()
        customLayerData = rootLayer.customLayerData

        settings_dict = self._settings.get_settings_dictionary("/rtx")
        usdDict = {}
        self.iterate_settings(usdDict, settings_dict.get_dict(), "/rtx")

        customLayerData["renderSettings"] = usdDict
        rootLayer.customLayerData = customLayerData
        curr_stage.Save()
        carb.log_info(f"saved {stage_file_path} {len(usdDict)} settings")

    def load_from_usd(self, stage_file_path=""):
        currStage = Usd.Stage.Open(stage_file_path)
        rootLayer = currStage.GetRootLayer()
        customLayerData = rootLayer.customLayerData
        renderSettingsVtVal = customLayerData["renderSettings"]
        loaded_count = 0
        if renderSettingsVtVal:
            omni.kit.commands.execute("RestoreDefaultRenderSettingSection", path="/rtx")
            for k, v in renderSettingsVtVal.items():
                rtx_key = k.replace(":", "/")

                default_flags = self._settings.get(rtx.settings.get_associated_setting_flags_path(rtx_key))
                if default_flags is None or (default_flags & rtx.settings.SETTING_FLAGS_TRANSIENT):
                    continue

                if isinstance(v, Gf.Vec3f) or isinstance(v, Gf.Vec3d):
                    self._settings.set("/" + rtx_key, [v[0], v[1], v[2]])
                else:
                    self._settings.set(rtx_key, v)
                loaded_count += 1

            carb.log_info(f"loaded {stage_file_path} {loaded_count} settings")
