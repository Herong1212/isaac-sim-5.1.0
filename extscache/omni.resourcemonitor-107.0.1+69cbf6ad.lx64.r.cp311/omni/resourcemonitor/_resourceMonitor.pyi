"""pybind11 omni.resourcemonitor bindings"""
from __future__ import annotations
import omni.resourcemonitor._resourceMonitor
import typing
import carb.events._events

__all__ = [
    "IResourceMonitor",
    "ResourceMonitorEventType",
    "acquire_resource_monitor_interface",
    "deviceMemoryWarnFractionSettingName",
    "deviceMemoryWarnMBSettingName",
    "hostMemoryWarnFractionSettingName",
    "hostMemoryWarnMBSettingName",
    "release_resource_monitor_interface",
    "sendDeviceMemoryWarningSettingName",
    "sendHostMemoryWarningSettingName",
    "timeBetweenQueriesSettingName"
]


class IResourceMonitor():
    def get_available_device_memory(self, arg0: int) -> int: ...
    def get_available_host_memory(self) -> int: ...
    def get_event_stream(self) -> carb.events._events.IEventStream: ...
    def get_total_device_memory(self, arg0: int) -> int: ...
    def get_total_host_memory(self) -> int: ...
    pass
class ResourceMonitorEventType():
    """
            ResourceMonitor notification.
            

    Members:

      DEVICE_MEMORY

      HOST_MEMORY

      LOW_DEVICE_MEMORY

      LOW_HOST_MEMORY
    """
    def __eq__(self, other: object) -> bool: ...
    def __getstate__(self) -> int: ...
    def __hash__(self) -> int: ...
    def __index__(self) -> int: ...
    def __init__(self, value: int) -> None: ...
    def __int__(self) -> int: ...
    def __ne__(self, other: object) -> bool: ...
    def __repr__(self) -> str: ...
    def __setstate__(self, state: int) -> None: ...
    @property
    def name(self) -> str:
        """
        :type: str
        """
    @property
    def value(self) -> int:
        """
        :type: int
        """
    DEVICE_MEMORY: omni.resourcemonitor._resourceMonitor.ResourceMonitorEventType # value = <ResourceMonitorEventType.DEVICE_MEMORY: 0>
    HOST_MEMORY: omni.resourcemonitor._resourceMonitor.ResourceMonitorEventType # value = <ResourceMonitorEventType.HOST_MEMORY: 1>
    LOW_DEVICE_MEMORY: omni.resourcemonitor._resourceMonitor.ResourceMonitorEventType # value = <ResourceMonitorEventType.LOW_DEVICE_MEMORY: 2>
    LOW_HOST_MEMORY: omni.resourcemonitor._resourceMonitor.ResourceMonitorEventType # value = <ResourceMonitorEventType.LOW_HOST_MEMORY: 3>
    __members__: dict # value = {'DEVICE_MEMORY': <ResourceMonitorEventType.DEVICE_MEMORY: 0>, 'HOST_MEMORY': <ResourceMonitorEventType.HOST_MEMORY: 1>, 'LOW_DEVICE_MEMORY': <ResourceMonitorEventType.LOW_DEVICE_MEMORY: 2>, 'LOW_HOST_MEMORY': <ResourceMonitorEventType.LOW_HOST_MEMORY: 3>}
    pass
def acquire_resource_monitor_interface(plugin_name: str = None, library_path: str = None) -> IResourceMonitor:
    pass
def release_resource_monitor_interface(arg0: IResourceMonitor) -> None:
    pass
deviceMemoryWarnFractionSettingName = '/persistent/resourcemonitor/deviceMemoryWarnFraction'
deviceMemoryWarnMBSettingName = '/persistent/resourcemonitor/deviceMemoryWarnMB'
hostMemoryWarnFractionSettingName = '/persistent/resourcemonitor/hostMemoryWarnFraction'
hostMemoryWarnMBSettingName = '/persistent/resourcemonitor/hostMemoryWarnMB'
sendDeviceMemoryWarningSettingName = '/persistent/resourcemonitor/sendDeviceMemoryWarning'
sendHostMemoryWarningSettingName = '/persistent/resourcemonitor/sendHostMemoryWarning'
timeBetweenQueriesSettingName = '/persistent/resourcemonitor/timeBetweenQueries'
