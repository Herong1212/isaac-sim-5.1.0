import os
import platform
import carb.settings
import omni.kit.app
import omni.kit.audiodeviceenum
import omni.usd.audio
from functools import partial
import omni.ui as ui
from omni.kit.audiodeviceenum import Direction, SampleType
from omni.kit.window.preferences import PreferenceBuilder, show_file_importer, PERSISTENT_SETTINGS_PREFIX, SettingType


class AudioPreferences(PreferenceBuilder):
    def __init__(self):
        super().__init__("Audio")

        self._settings = carb.settings.get_settings()
        self._enum = omni.kit.audiodeviceenum.acquire_audio_device_enum_interface()
        self._audio = omni.usd.audio.get_stage_audio_interface()

        carb.settings.get_settings().set_default_bool(
            PERSISTENT_SETTINGS_PREFIX + "/audio/context/closeAudioPlayerOnStop", False
        )
        carb.settings.get_settings().set_default_float(PERSISTENT_SETTINGS_PREFIX + "/audio/context/uiVolume", 1.0)

    def build(self):
        devices = self.get_device_list(Direction.PLAYBACK)
        capture_devices = self.get_device_list(Direction.CAPTURE)
        speaker_list = [
            "auto-detect",
            "mono",
            "stereo",
            "2.1",
            "quad",
            "4.1 surround",
            "5.1 surround",
            "7.1 surround",
            "7.1.4 surround",
            "9.1 surround",
            "9.1.4 surround",
            "9.1.6 surround",
        ]

        """ Audio Device """
        with ui.VStack(height=0):
            with self.add_frame("Audio Output"):
                with ui.VStack():
                    self._device_widget = self.create_setting_widget_combo(
                        "Output Device", PERSISTENT_SETTINGS_PREFIX + "/audio/context/deviceName", devices
                    )
                    self._capture_device_widget = self.create_setting_widget_combo(
                        "Input Device", PERSISTENT_SETTINGS_PREFIX + "/audio/context/captureDeviceName", capture_devices
                    )
                    self.create_setting_widget_combo(
                        "Speaker Configuration", PERSISTENT_SETTINGS_PREFIX + "/audio/context/speakerMode", speaker_list
                    )
                    with ui.HStack(height=24):
                        ui.Button("Refresh", clicked_fn=partial(self._on_refresh_button_fn))
                        ui.Spacer(width=10)
                        ui.Button("Apply", clicked_fn=partial(self._on_apply_button_fn))

            self.spacer()

            """ Audio Parameters """
            with self.add_frame("Audio Parameters"):
                with ui.VStack():
                    self.create_setting_widget(
                        "Auto Stream Threshold (in Kilobytes)",
                        PERSISTENT_SETTINGS_PREFIX + "/audio/context/autoStreamThreshold",
                        SettingType.INT,
                        range_from=0,
                        range_to=10240,
                        speed=10,
                    )

            self.spacer()

            """ Audio Player Parameters """
            with self.add_frame("Audio Player Parameters"):
                with ui.VStack():
                    self.create_setting_widget(
                        "Auto Stream Threshold (in Kilobytes)",
                        PERSISTENT_SETTINGS_PREFIX + "/audio/context/audioPlayerAutoStreamThreshold",
                        SettingType.INT,
                        range_from=0,
                        range_to=10240,
                        speed=10,
                    )
                    self.create_setting_widget(
                        "Close Audio Player on Stop",
                        PERSISTENT_SETTINGS_PREFIX + "/audio/context/closeAudioPlayerOnStop",
                        SettingType.BOOL,
                    )

            self.spacer()

            """ Volume Levels """
            with self.add_frame("Volume Levels"):
                with ui.VStack():
                    self.create_setting_widget(
                        "Master Volume",
                        PERSISTENT_SETTINGS_PREFIX + "/audio/context/masterVolume",
                        SettingType.FLOAT,
                        range_from=0.0,
                        range_to=1.0,
                        speed=0.01,
                    )
                    self.create_setting_widget(
                        "USD Volume",
                        PERSISTENT_SETTINGS_PREFIX + "/audio/context/usdVolume",
                        SettingType.FLOAT,
                        range_from=0.0,
                        range_to=1.0,
                        speed=0.01,
                    )
                    self.create_setting_widget(
                        "Spatial Voice Volume",
                        PERSISTENT_SETTINGS_PREFIX + "/audio/context/spatialVolume",
                        SettingType.FLOAT,
                        range_from=0.0,
                        range_to=1.0,
                        speed=0.01,
                    )
                    self.create_setting_widget(
                        "Non-spatial Voice Volume",
                        PERSISTENT_SETTINGS_PREFIX + "/audio/context/nonSpatialVolume",
                        SettingType.FLOAT,
                        range_from=0.0,
                        range_to=1.0,
                        speed=0.01,
                    )
                    self.create_setting_widget(
                        "UI Audio Volume",
                        PERSISTENT_SETTINGS_PREFIX + "/audio/context/uiVolume",
                        SettingType.FLOAT,
                        range_from=0.0,
                        range_to=1.0,
                        speed=0.01,
                    )

            self.spacer()

            """ Debug """
            with self.add_frame("Debug"):
                with ui.VStack():
                    self.create_setting_widget(
                        "Stream Dump Filename",
                        PERSISTENT_SETTINGS_PREFIX + "/audio/context/streamerFile",
                        SettingType.STRING,
                        clicked_fn=self._on_browse_button_fn,
                    )

                    # checkbox to enable stream dumping.  Note that the setting path for
                    # this is *intentionally* not persistent.  This forces the stream
                    # dumping to need to be toggled on at each launch instead of just
                    # enabling it on startup and filling up everyone's harddrives.
                    self.create_setting_widget("Enable Stream Dump", "/audio/context/enableStreamer", SettingType.BOOL)

    def _on_browse_button_fn(self, origin): # pragma: no cover
        """ Called when the user picks the Browse button. """
        full_path = origin.model.get_value_as_string()
        path = os.path.dirname(full_path)
        if path == "":
            path = "/"
            if platform.system().lower() == "windows":
                path = "C:/"
        filename = os.path.basename(full_path)
        if filename == "":
            filename = "stream_dump"

        # NOTE: navigate_to doesn't work if target file doesn't exist...
        navigate_to = self.cleanup_slashes(os.path.join(path, filename))
        if not os.path.exists(navigate_to):
            navigate_to = self.cleanup_slashes(path)

        show_file_importer(
            title="Select Filename (Local Files Only)",
            file_exts=[("RIFF Files(*.wav)", ""), ("All Files(*)", "")],
            click_apply_fn=self._on_file_pick,
            filename_url=navigate_to
        )

    def _on_file_pick(self, full_path): # pragma: no cover
        """ Called when the user accepts filename in the Select Filename dialog. """
        path = os.path.dirname(full_path)
        if path == "":
            path = "/"
            if platform.system().lower() == "windows":
                path = "C:/"
        filename = os.path.basename(full_path)
        if filename == "":
            filename = "stream_dump.bin"

        self._settings.set(
            PERSISTENT_SETTINGS_PREFIX + "/audio/context/streamerFile",
            self.cleanup_slashes(os.path.join(path, filename)),
        )

    def _on_refresh_button_fn(self):
        """ Called when the user clicks on the 'Refresh' button. """
        devices = self.get_device_list(Direction.PLAYBACK)
        self._device_widget.model.set_items(devices)

        devices = self.get_device_list(Direction.CAPTURE)
        self._capture_device_widget.model.set_items(devices)

    def _on_apply_button_fn(self):
        """ Called when the user clicks on the 'Apply' button. """
        deviceId = self._settings.get(PERSISTENT_SETTINGS_PREFIX + "/audio/context/deviceName")
        self._audio.set_device(deviceId)

    def get_device_list(self, direction):
        device_count = self._enum.get_device_count(direction)
        default_device = self._enum.get_device_name(direction, 0)
        if default_device is None:
            return {"No audio device is connected": ""}

        devices = {"Default Device (" + self._enum.get_device_name(direction, 0) + ")": ""}

        for i in range(device_count):
            dev_name = self._enum.get_device_description(direction, i)
            dev_id = self._enum.get_device_id(direction, i)

            if dev_name == None or dev_id == None:
                continue

            devices[dev_name] = dev_id

        return devices
