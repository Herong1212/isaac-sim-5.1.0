from pathlib import Path
from omni.metropolis.utils.file_util import JSONFileUtil
import carb


class IncidentReport:
    """
    This class helps assemble an incident report and generate report file.
    Incident information is categorized into 3 sections:
        1. event_data: describes how this event is setup.
            It can be directly from the incident config.
        2. simulation_data: describes what happens to the event during simulation.
            It can be object transforms, event duration, physics param, etc
        3. trigger_data: describes how the incident is triggered.
            It can be directly from the trigger dict representation.

    Example report file:
        {
            "incidents": [
                "my topple event": {
                    "event_data": {
                        "type": "ToppleEvent"
                        "topple_item":{
                            "item": /World/Box01
                            "topple_radius": 1.5
                        }
                    }
                    "simulation_data": {
                        "start_time": 10
                        "end_time": 16
                        "topple_item_end_location": [
                            "/World/Box01": [1, 1, 0]
                        ]
                    }
                    "trigger_data": {
                        "type": time
                        "time": 10
                    }
                }
            ]
        }
    """

    def __init__(self):
        self._data = {}
        self._is_recording = False
        self._dir_path = None
        self._file_name = None

    def start_recording(self, dir_path: str, file_name: str = "incidents_report.json"):
        if self._is_recording:
            carb.log_warn("Incident report is already recording. Discarding previous recording to start new one.")

        self.clear()
        self._dir_path = dir_path
        self._file_name = file_name
        self._is_recording = True

    def end_recording(self):
        if not self._is_recording:
            carb.log_warn("Incident report is not recording. No report file will be generated.")
            return

        self._is_recording = False
        if not self._generate_report_file():
            carb.log_error("Generate report file fails.")

    def is_recording(self):
        return self._is_recording

    def add_event_data(self, incident_name: str, data: dict):
        self._add_data(incident_name, "event_data", data)

    def add_simulation_data(self, incident_name: str, data: dict):
        self._add_data(incident_name, "simulation_data", data)

    def add_trigger_data(self, incident_name: str, data: dict):
        self._add_data(incident_name, "trigger_data", data)

    def clear(self):
        self._data.clear()

    def _generate_report_file(self) -> bool:
        if not (self._dir_path and self._file_name):
            carb.log_error(f"Invalid report file path: {self._dir_path}/{self._file_name}.")
            return False
        return JSONFileUtil.write_to_file(f"{self._dir_path}/{self._file_name}", self._data)

    def _add_data(self, incident_name: str, section_name: str, data: dict):
        # Only store data during recording
        if not self._is_recording:
            return
        if incident_name not in self._data:
            self._data.update({incident_name: {}})
        if section_name not in self._data:
            self._data[incident_name].update({section_name: {}})
        self._data[incident_name][section_name].update(data)
