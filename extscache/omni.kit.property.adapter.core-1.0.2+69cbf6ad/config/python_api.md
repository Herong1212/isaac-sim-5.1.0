# Public API for module omni.kit.property.adapter.core:

## Classes

- class PropertyType(Enum)
  - ATTRIBUTE: Tuple
  - RELATIONSHIP: Unknown

- class AttributeAdapter(ABC)
  - def __init__(self, attribute)
  - [property] def attribute(self)
  - def GetPrim(self)
  - def GetPropertyType(self)

- class PrimAdapter(ABC)
  - def __init__(self, prim)
  - [property] def prim(self)

- class StageAdapter(ABC)
  - def __init__(self, stage)
  - [property] def name(self) -> str
  - [property] def priority_read(self) -> int
  - [property] def priority_write(self) -> int
  - [property] def stage(self)
  - [property] def usd_stage(self)
  - def GetPrimAtPath(self, path)
  - def GetAttributeAtPath(self, path)
  - def CreateChangeTracker(self, attr_names: list, prim_paths: list, callback: Callable) -> Any
  - def convert_data(self, data, dst_adapter_name: str)
  - def resolve_path_array(self, path, resolve_path: str, path_list, index)
  - def get_notice_paths(self, stage, notice)

- class RegistryEventType(IntEnum)
  - ADAPTER_ADDED: Unknown
  - ADAPTER_REMOVED: Unknown

- class SceneDescriptionAdapterRegistry
  - def __init__(self)
  - [property] def event_stream(self) -> carb.events.IEventStream
  - [property] def registered_adapters(self) -> Dict[str, Callable[[Usd.Stage], StageAdapter]]
  - def register_stage_adapter(self, name: str, adapter_type: Callable[[Usd.Stage], StageAdapter])
  - def unregister_stage_adapter(self, name: str)
  - def instantiate_all_stage_adapters(self, stage: Usd.Stage) -> Dict[str, StageAdapter]

- class CorePropertyAdapterExtension(omni.ext.IExt)
  - def __init__(self)
  - def on_startup(self, ext_id)
  - def on_shutdown(self)
  - [property] def adapter_registry(self) -> SceneDescriptionAdapterRegistry

## Functions

- def get_adapter_registry()
