# Public API for module omni.inspect:

## Classes

- class IInspectJsonSerializer(_IInspectJsonSerializer, IInspector, _IInspector, omni.core._core.IObject)
  - def __init__(self, arg0: omni.core._core.IObject)
  - def __init__(self)
  - def as_string(self) -> str
  - def clear(self)
  - def close_array(self) -> bool
  - def close_object(self) -> bool
  - def finish(self) -> bool
  - def open_array(self) -> bool
  - def open_object(self) -> bool
  - def set_output_to_string(self)
  - def write_base64_encoded(self, value: bytes, size: int) -> bool
  - def write_bool(self, value: bool) -> bool
  - def write_double(self, value: float) -> bool
  - def write_float(self, value: float) -> bool
  - def write_int(self, value: int) -> bool
  - def write_int64(self, value: int) -> bool
  - def write_key(self, key: str) -> bool
  - def write_key_with_length(self, key: str, key_len: int) -> bool
  - def write_null(self) -> bool
  - def write_string(self, value: str) -> bool
  - def write_string_with_length(self, value: str, len: int) -> bool
  - def write_u_int(self, value: int) -> bool
  - def write_u_int64(self, value: int) -> bool
  - [property] def output_location(self) -> str
  - [property] def output_to_file_path(self)
  - [output_to_file_path.setter] def output_to_file_path(self, arg1: str)

- class IInspectMemoryUse(_IInspectMemoryUse, IInspector, _IInspector, omni.core._core.IObject)
  - def __init__(self, arg0: omni.core._core.IObject)
  - def __init__(self)
  - def reset(self)
  - def total_used(self) -> int
  - def use_memory(self, ptr: capsule, bytes_used: int) -> bool

- class IInspectSerializer(_IInspectSerializer, IInspector, _IInspector, omni.core._core.IObject)
  - def __init__(self, arg0: omni.core._core.IObject)
  - def __init__(self)
  - def as_string(self) -> str
  - def clear(self)
  - def set_output_to_string(self)
  - def write_string(self, to_write: str)
  - [property] def output_location(self) -> str
  - [property] def output_to_file_path(self)
  - [output_to_file_path.setter] def output_to_file_path(self, arg1: str)

- class IInspector(_IInspector, omni.core._core.IObject)
  - def __init__(self, arg0: omni.core._core.IObject)
  - def __init__(self)
  - def help_flag(self) -> str
  - def help_information(self) -> str
  - def is_flag_set(self, flag_name: str) -> bool
  - def set_flag(self, flag_name: str, flag_state: bool)
  - [property] def help(self)
  - [help.setter] def help(self, arg1: str)

## Other

- omni.core: public module
