# Public API for module omni.resourcemonitor:

## Classes

- class IResourceMonitor
  - def get_available_device_memory(self, arg0: int) -> int
  - def get_available_host_memory(self) -> int
  - def get_event_stream(self) -> carb.events._events.IEventStream
  - def get_total_device_memory(self, arg0: int) -> int
  - def get_total_host_memory(self) -> int

- class ResourceMonitorEventType
  - def __init__(self, value: int)
  - [property] def name(self) -> str
  - [property] def value(self) -> int
  - DEVICE_MEMORY: omni.resourcemonitor._resourceMonitor.ResourceMonitorEventType
  - HOST_MEMORY: omni.resourcemonitor._resourceMonitor.ResourceMonitorEventType
  - LOW_DEVICE_MEMORY: omni.resourcemonitor._resourceMonitor.ResourceMonitorEventType
  - LOW_HOST_MEMORY: omni.resourcemonitor._resourceMonitor.ResourceMonitorEventType

- class PublicExtension(omni.ext.IExt)
  - def on_startup(self)
  - def on_shutdown(self)

## Functions

- def acquire_resource_monitor_interface(plugin_name: str = None, library_path: str = None) -> IResourceMonitor
- def release_resource_monitor_interface(arg0: IResourceMonitor)

## Variables

- deviceMemoryWarnFractionSettingName: str
- deviceMemoryWarnMBSettingName: str
- hostMemoryWarnFractionSettingName: str
- hostMemoryWarnMBSettingName: str
- sendDeviceMemoryWarningSettingName: str
- sendHostMemoryWarningSettingName: str
- timeBetweenQueriesSettingName: str

## Other

- carb: public module
- omni.ext: public module
- omni.kit.app: public module
