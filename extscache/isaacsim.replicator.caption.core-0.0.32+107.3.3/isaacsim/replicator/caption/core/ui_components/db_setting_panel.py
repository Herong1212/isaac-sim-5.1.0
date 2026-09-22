import omni.ui as ui
from ..db.db import DB, MongoDB

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


class DatabaseSettingPanel:
    def __init__(self):
        self.db = None

    def shutdown(self):
        self.db = None

    def _build_ui(self):
        self.content_frame = ui.CollapsableFrame(
            title="Database Settings",
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
                    host_label = ui.Label("Host")
                    host_label.set_tooltip("Host for where the database is located.")
                    host_widget, self.host_model = create_setting_widget(
                        ReplicatorCaptionSettings.DB_HOST,
                        SettingType.STRING,
                        hard_range=False,
                        alignment=ui.Alignment.LEFT_CENTER,
                    )
                    self.host_model.set_value(ReplicatorCaptionSettings.get_db_host())

                with ui.HStack(spacing=5):
                    model_name_label = ui.Label("Username")
                    model_name_label.set_tooltip("Set database username.")
                    with ui.HStack(alignment=ui.Alignment.LEFT_CENTER):
                        username_widget, self.username_model = create_setting_widget(
                            ReplicatorCaptionSettings.DB_USERNAME,
                            SettingType.STRING,
                            hard_range=False,
                            alignment=ui.Alignment.LEFT_CENTER,
                        )

                    self.username_model.set_value(ReplicatorCaptionSettings.get_db_username())

                with ui.HStack(spacing=5):
                    password_label = ui.Label("Password")
                    password_label.set_tooltip("Set database password.")
                    with ui.HStack(alignment=ui.Alignment.LEFT_CENTER):
                        password_widget, self.password_model = create_setting_widget(
                            ReplicatorCaptionSettings.DB_PASSWORD,
                            SettingType.STRING,
                            hard_range=False,
                            alignment=ui.Alignment.LEFT_CENTER,
                        )

                    self.password_model.set_value(ReplicatorCaptionSettings.get_db_password())

                with ui.HStack(spacing=5):
                    database_label = ui.Label("Database")
                    database_label.set_tooltip("Set database name.")
                    with ui.HStack(alignment=ui.Alignment.LEFT_CENTER):
                        database_widget, self.database_model = create_setting_widget(
                            ReplicatorCaptionSettings.DB_DATABASE,
                            SettingType.STRING,
                            hard_range=False,
                            alignment=ui.Alignment.LEFT_CENTER,
                        )

                    self.database_model.set_value(ReplicatorCaptionSettings.get_db_database())

                with ui.HStack(spacing=5):
                    collection_label = ui.Label("Collection")
                    collection_label.set_tooltip("Set database collection.")
                    with ui.HStack(alignment=ui.Alignment.LEFT_CENTER):
                        collection_widget, self.collection_model = create_setting_widget(
                            ReplicatorCaptionSettings.DB_COLLECTION,
                            SettingType.STRING,
                            hard_range=False,
                            alignment=ui.Alignment.LEFT_CENTER,
                        )

                    self.collection_model.set_value(ReplicatorCaptionSettings.get_db_collection())

                with ui.HStack(spacing=10):
                    self.accept_model_settings = ui.Button("Accept", width=120, alignment=ui.Alignment.CENTER)
                    self.accept_model_settings.set_tooltip("Accept the above model settings.")
                    self.accept_model_settings.set_clicked_fn(self.set_model_params_fn)

    def set_model_params_fn(self):
        """Load the scene from config file"""
        stage_info_manager = StageInfoManager.get_instance()
        # Get values from the text boxes
        host = self.host_model.get_value_as_string() if self.host_model else ""
        username = self.username_model.get_value_as_string() if self.username_model else ""
        password = self.password_model.get_value_as_string() if self.password_model else ""
        database = self.database_model.get_value_as_string() if self.database_model else ""
        collection = self.collection_model.get_value_as_string() if self.collection_model else ""
        options = "authMechanism=DEFAULT&replicaSet=repldev-080910&authSource=admin&ssl=false"

        self.db: DB = MongoDB(host, username, password, database, collection, options)
        stage_info_manager.set_db(self.db)
