import omni.ext


class IsaacsimAnimRobotExt(omni.ext.IExt):
    def on_startup(self, ext_id):
        # Remove after the IAR/IRA integration is done.
        import carb
        import omni.kit.app
        import os

        COMMAND_FILE_PATH_SETTING = "/exts/isaacsim.anim.robot/command_settings/command_file_path"
        EXT_PATH = omni.kit.app.get_app().get_extension_manager().get_extension_path_by_module("isaacsim.anim.robot")
        target_path = os.path.join(EXT_PATH, "config/command_file.txt")
        carb.settings.get_settings().set(COMMAND_FILE_PATH_SETTING, target_path)

    def on_shutdown(self):
        pass
