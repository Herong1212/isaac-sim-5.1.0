import re
import os
import carb.settings
import omni.kit.app
import omni.ui as ui
from functools import partial
from omni.kit.window.preferences import PreferenceBuilder, show_file_importer, SettingType, PERSISTENT_SETTINGS_PREFIX


class StageTemplatesPreferences(PreferenceBuilder):
    def __init__(self):
        super().__init__("Template Startup")

        # update on setting change
        def on_change(item, event_type):
            if event_type == carb.settings.ChangeEventType.CHANGED:
                omni.kit.window.preferences.rebuild_pages()

        self._update_setting = omni.kit.app.SettingChangeSubscription(PERSISTENT_SETTINGS_PREFIX + "/app/newStage/templatePath", on_change)

    def build(self):
        template_paths = carb.settings.get_settings().get("/persistent/app/newStage/templatePath")

        default_template = omni.kit.stage_templates.get_default_template()
        script_names = []
        new_templates = omni.kit.stage_templates.get_stage_template_list()
        for templates in new_templates:
            for template in templates.items():
                script_names.append(template[0])
        if len(script_names) == 0:
            script_names = ["None##None"]

        with ui.VStack(height=0):
            with self.add_frame("New Stage Template"):
                with ui.VStack():
                    for index, path in enumerate(template_paths):
                        with ui.HStack(height=24):
                            self.label("Path to user templates")
                            widget = ui.StringField(height=20)
                            widget.model.set_value(path)
                            ui.Button(style={"image_url": "resources/icons/folder.png"}, identifier=f"stage_template_browse_{index}", clicked_fn=lambda p=self.cleanup_slashes(carb.tokens.get_tokens_interface().resolve(path))+"/", i=index, w=widget: self._on_browse_button_fn(p, i, w), width=24)

                    self.create_setting_widget_combo("Default Template", PERSISTENT_SETTINGS_PREFIX + "/app/newStage/defaultTemplate", script_names)

    def _on_browse_button_fn(self, path, index, widget):
        """ Called when the user picks the Browse button. """
        show_file_importer(
            "Select Template Directory",
            click_apply_fn=lambda p=self.cleanup_slashes(path), i=index, w=widget: self._on_file_pick(
                p, index=i, widget=w),
            filename_url=path,
            show_only_folders=True)

    def _on_file_pick(self, full_path, index, widget):
        """ Called when the user accepts directory in the Select Directory dialog. """
        directory = self.cleanup_slashes(full_path, True)
        settings = carb.settings.get_settings()
        template_paths = settings.get(PERSISTENT_SETTINGS_PREFIX + "/app/newStage/templatePath")
        if self.cleanup_slashes(carb.tokens.get_tokens_interface().resolve(template_paths[index]))+"/" != directory:
            template_paths[index] = directory
        settings.set(PERSISTENT_SETTINGS_PREFIX + "/app/newStage/templatePath", template_paths)
        widget.model.set_value(directory)
