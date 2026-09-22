# Public API for module omni.scene.optimizer.core:

## Classes

- class SOPluginVersion
  - def __init__(self)
  - [property] def major(self) -> int
  - [major.setter] def major(self, arg0: int)
  - [property] def minor(self) -> int
  - [minor.setter] def minor(self, arg0: int)
  - [property] def rev(self) -> int
  - [rev.setter] def rev(self, arg0: int)

- class ExecutionContext
  - def __init__(self)
  - [property] def captureStats(self) -> int
  - [captureStats.setter] def captureStats(self, arg0: int)
  - [property] def debug(self) -> int
  - [debug.setter] def debug(self, arg0: int)
  - [property] def generateReport(self) -> int
  - [generateReport.setter] def generateReport(self, arg0: int)
  - [property] def reportPath(self) -> str
  - [reportPath.setter] def reportPath(self, arg0: str)
  - [property] def singleThreaded(self) -> int
  - [singleThreaded.setter] def singleThreaded(self, arg0: int)
  - [property] def usdStageId(self) -> int
  - [usdStageId.setter] def usdStageId(self, arg0: int)
  - [property] def verbose(self) -> int
  - [verbose.setter] def verbose(self, arg0: int)

- class ISceneOptimizer
  - def delete_prims(self, arg0: ExecutionContext, arg1: typing.List[str])
  - def deregister_operation(self, arg0: str)
  - def execute_operation(self, arg0: str, arg1: ExecutionContext, arg2: str) -> tuple
  - def get_operation_arguments(self, arg0: str) -> list
  - def get_operation_author(self, arg0: str) -> str
  - def get_operation_description(self, arg0: str) -> str
  - def get_operation_display_name(self, arg0: str) -> str
  - def get_operation_version(self, arg0: str) -> SOPluginVersion
  - def get_operation_visible(self, arg0: str) -> bool
  - def get_operations(self) -> list
  - def json_parser(self, arg0: ExecutionContext, arg1: str) -> bool
  - def load_plugins(self)
  - def load_plugins_from_path(self, arg0: str)
  - def path_resolver(self, arg0: ExecutionContext, arg1: typing.List[str], arg2: bool) -> list

## Functions

- def acquire_interface(plugin_name: str = None, library_path: str = None) -> ISceneOptimizer
- def release_interface(arg0: ISceneOptimizer)

# Public API for module omni.scene.optimizer.core.operation:

## Classes

- class Operation
  - ArgumentDisplayTypeBool: str
  - ArgumentDisplayTypeCode: str
  - ArgumentDisplayTypeEnum: str
  - ArgumentDisplayTypeFloat: str
  - ArgumentDisplayTypeFloatArray: str
  - ArgumentDisplayTypeFloatSlider: str
  - ArgumentDisplayTypeInt: str
  - ArgumentDisplayTypeIntSlider: str
  - ArgumentDisplayTypePrimPath: str
  - ArgumentDisplayTypePrimPaths: str
  - ArgumentDisplayTypeText: str
  - ArgumentDisplayTypeTextList: str
  - def __init__(self, name, display_name, description)
  - [property] def name(self)
  - [property] def display_name(self)
  - [property] def description(self)
  - [property] def author(self)
  - [property] def version(self)
  - [property] def visible(self)
  - def add_argument(self, name: str, display_name: str, display_type: str, description: str, default_value, enum_values: dict = None, join_next: tuple = None, min: float = None, max: float = None, placeholder: str = None, precision: int = None, visible: bool = None, enable_if: str = None, visible_if: str = None, metadata: dict = {})
  - def get_usd_stage(self)
  - def execute(self, args)
