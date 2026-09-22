# Public API for module omni.kit.audiodeviceenum:

## Classes

- class Direction
  - def __init__(self, value: int)
  - [property] def name(self) -> str
  - [property] def value(self) -> int
  - CAPTURE: omni.kit.audiodeviceenum._audiodeviceenum.Direction
  - PLAYBACK: omni.kit.audiodeviceenum._audiodeviceenum.Direction

- class IAudioDeviceEnum
  - def get_device_channel_count(self, dir: Direction, index: int) -> int
  - def get_device_count(self, dir: Direction) -> int
  - def get_device_description(self, dir: Direction, index: int) -> object
  - def get_device_frame_rate(self, dir: Direction, index: int) -> int
  - def get_device_id(self, dir: Direction, index: int) -> object
  - def get_device_name(self, dir: Direction, index: int) -> object
  - def get_device_sample_size(self, dir: Direction, index: int) -> int
  - def get_device_sample_type(self, dir: Direction, index: int) -> SampleType
  - def is_direct_hardware_backend(self) -> bool

- class SampleType
  - def __init__(self, value: int)
  - [property] def name(self) -> str
  - [property] def value(self) -> int
  - COMPRESSED: omni.kit.audiodeviceenum._audiodeviceenum.SampleType
  - PCM_FLOAT: omni.kit.audiodeviceenum._audiodeviceenum.SampleType
  - PCM_SIGNED_INTEGER: omni.kit.audiodeviceenum._audiodeviceenum.SampleType
  - PCM_UNSIGNED_INTEGER: omni.kit.audiodeviceenum._audiodeviceenum.SampleType
  - UNKNOWN: omni.kit.audiodeviceenum._audiodeviceenum.SampleType

## Functions

- def acquire_audio_device_enum_interface(plugin_name: str = None, library_path: str = None) -> IAudioDeviceEnum
- def get_audio_device_enum_interface() -> IAudioDeviceEnum
