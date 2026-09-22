import omni.ui as ui
from omni.kit.window.preferences import PreferenceBuilder, SettingType


class ResourceMonitorPreferences(PreferenceBuilder):
    def __init__(self):
        super().__init__("Resource Monitor")

    def build(self):
        """ Resource Monitor """
        try:
            import omni.resourcemonitor as rm
            with ui.VStack(height=0):
                with self.add_frame("Resource Monitor"):
                    with ui.VStack():
                        self.create_setting_widget(
                            "Time Between Queries",
                            rm.timeBetweenQueriesSettingName,
                            SettingType.FLOAT,
                        )
                        self.create_setting_widget(
                            "Send Device Memory Warnings",
                            rm.sendDeviceMemoryWarningSettingName,
                            SettingType.BOOL,
                        )
                        self.create_setting_widget(
                            "Device Memory Warning Threshold (MB)",
                            rm.deviceMemoryWarnMBSettingName,
                            SettingType.INT,
                        )
                        self.create_setting_widget(
                            "Device Memory Warning Threshold (Fraction)",
                            rm.deviceMemoryWarnFractionSettingName,
                            SettingType.FLOAT,
                            range_from=0.,
                            range_to=1.,
                        )
                        self.create_setting_widget(
                            "Send Host Memory Warnings",
                            rm.sendHostMemoryWarningSettingName,
                            SettingType.BOOL
                        )
                        self.create_setting_widget(
                            "Host Memory Warning Threshold (MB)",
                            rm.hostMemoryWarnMBSettingName,
                            SettingType.INT,
                        )
                        self.create_setting_widget(
                            "Host Memory Warning Threshold (Fraction)",
                            rm.hostMemoryWarnFractionSettingName,
                            SettingType.FLOAT,
                            range_from=0.,
                            range_to=1.,
                        )
        except ImportError: # pragma: no cover
            pass
