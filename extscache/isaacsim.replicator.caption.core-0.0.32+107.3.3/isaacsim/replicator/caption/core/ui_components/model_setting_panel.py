import omni.ui as ui
from omni.kit.widget.settings import SettingType, create_setting_widget

from ..settings import ReplicatorCaptionSettings
from ..stage_info_manager import StageInfoManager

COLOR_BLACK = 0x0
BOUNDING_RADIUS = 1.5
UI_DISTANCE = 120
STRING_FIELD_WIDTH = 300


def get_collapsable_frame_style():
    return {
        "border_radius": BOUNDING_RADIUS * 2,
        "border_color": COLOR_BLACK,
        "border_width": 1,
        "padding": 6,
    }


class ModelSettingPanel:
    def __init__(self):
        self.url_model = None
        self.name_model = None
        self.key_model = None

    def shutdown(self):
        self.url_model = None
        self.name_model = None
        self.key_model = None

    def _build_ui(self):
        self.content_frame = ui.CollapsableFrame(
            title="Model Settings",
            height=0,
            collapsed=True,
            style=get_collapsable_frame_style(),
            name="subFrame",
            horizontal_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_AS_NEEDED,
            vertical_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_ALWAYS_ON,
        )

        with self.content_frame:
            with ui.VStack(spacing=10):
                with ui.HStack(spacing=5):
                    model_url_label = ui.Label("Model URL")
                    model_url_label.set_tooltip("Set the URL of the model.")
                    model_url_widget, self.url_model = create_setting_widget(
                        ReplicatorCaptionSettings.MODEL_URL,
                        SettingType.STRING,
                        hard_range=False,
                        alignment=ui.Alignment.LEFT_CENTER,
                    )
                    self.url_model.set_value(ReplicatorCaptionSettings.get_model_url())

                with ui.HStack(spacing=5):
                    model_name_label = ui.Label("Model Name")
                    model_name_label.set_tooltip("Set the name of the model.")
                    with ui.HStack(alignment=ui.Alignment.LEFT_CENTER):
                        model_name_widget, self.name_model = create_setting_widget(
                            ReplicatorCaptionSettings.MODEL_NAME,
                            SettingType.STRING,
                            hard_range=False,
                            alignment=ui.Alignment.LEFT_CENTER,
                        )

                    self.name_model.set_value(ReplicatorCaptionSettings.get_model_name())

                with ui.HStack(spacing=5):
                    api_key_label = ui.Label("API Key")
                    api_key_label.set_tooltip("Set the API key.")
                    with ui.HStack(alignment=ui.Alignment.LEFT_CENTER):
                        api_key_widget, self.key_model = create_setting_widget(
                            ReplicatorCaptionSettings.API_KEY,
                            SettingType.STRING,
                            hard_range=False,
                            alignment=ui.Alignment.LEFT_CENTER,
                        )

                    self.key_model.set_value(ReplicatorCaptionSettings.get_api_key())

                with ui.HStack(spacing=10):
                    self.accept_model_settings = ui.Button("Accept", width=120, alignment=ui.Alignment.CENTER)
                    self.accept_model_settings.set_tooltip("Accept the above model settings.")
                    self.accept_model_settings.set_clicked_fn(self.set_model_params_fn)

    def set_model_params_fn(self):
        """Load the scene from config file"""
        stage_info_manager = StageInfoManager.get_instance()
        # Get values from the text boxes
        url = self.url_model.get_value_as_string() if self.url_model else ""
        name = self.name_model.get_value_as_string() if self.name_model else ""
        key = self.key_model.get_value_as_string() if self.key_model else "placeholder"
        stage_info_manager.set_model_params(url, name, key)
