# Public API for module omni.graph.tools:

## Classes

- class DeprecatedDictConstant(dict)
  - def __init__(self, name: str, new_value: dict, message: str, deprecation_level: DeprecationLevel = None)

- class DeprecatedStringConstant(str)
  - def __init__(self, name: str, new_value: str | None, message: str, deprecation_level: DeprecationLevel = None)

- class DeprecateMessage
  - SILENCE_LOG: bool
  - SHOW_STACK: bool
  - MAX_STACK_LEVELS: int
  - class NoLogging
    - def __init__(self, *args, **kwargs)
  - class def messages_logged(cls) -> Set[str]
  - class def clear_messages(cls)
  - class def deprecations_are_errors(cls) -> bool
  - class def set_deprecations_are_errors(cls, make_errors: bool)
  - class def deprecated(cls, message: str, deprecation_level: DeprecationLevel = None)

- class DeprecationError(Exception)

- class DeprecationLevel(Enum)
  - WARNING: Unknown
  - ERROR: Unknown

- class IndentedOutput
  - def __init__(self, output: IO)
  - def indent(self, message: str = None) -> bool
  - def exdent(self, message: str = None)
  - def close(self)
  - def prepend(self, message: str)
  - def write(self, message: Union[List, str] = '')
  - def write_as_is(self, message: Union[List, str])

## Functions

- def build_directory_metadata(ext_path: str, destination: Path | None) -> dict[str, dict | str]
- def deprecated_constant_object(constant: any, deprecation_message: str, deprecation_level: DeprecationLevel = None)
- def deprecated_function(deprecation_message: str, is_property: bool = False)
- def DeprecatedClass(deprecation_message: str = None) -> object
- def DeprecatedImport(deprecation_message: str)
- def destroy_property(self, property_name: str)
- def function_trace(env_var = None)
- def get_node_type_names_from_metadata(metadata: dict[str, any]) -> list[str]
- def import_tests_in_directory(module_file: str, module_name: str)
- def make_nice_name(raw_name: str, preserve_final_part: bool = False) -> str
- def RenamedClass(cls, old_class_name: str, rename_message: Optional[str] = None) -> object
- def shorten_string_lines_to(full_string: str, suggested_limit: int) -> List[str]
- def supported_attribute_type_names(*args, **kwargs)

## Variables

- dbg: Unknown
- dbg_eval: Unknown
- dbg_gc: Unknown
- dbg_ui: Unknown
- OGN_DEBUG: Unknown
