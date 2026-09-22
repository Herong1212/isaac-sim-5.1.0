"""
        This module contains bindings to GPU Foundation.
        """
from __future__ import annotations
import omni.gpu_foundation_factory._gpu_foundation_factory
import typing
import carb._carb

__all__ = [
    "Device",
    "IGpuFoundationFactory",
    "RpResource",
    "Texture",
    "TextureFormat",
    "acquire_gpu_foundation_factory_interface",
    "get_driver_version",
    "get_gpus_list",
    "get_limited_processor_core_info",
    "get_memory_info",
    "get_os_build_number",
    "get_os_name",
    "get_page_swap_info",
    "get_processor_brand_name",
    "get_processor_core_count",
    "release_gpu_foundation_factory_interface"
]


class Device():
    pass
class IGpuFoundationFactory():
    def get_device_count(self) -> int: ...
    def get_device_index(self, arg0: int, arg1: int) -> int: ...
    def get_device_name(self, arg0: int) -> str: ...
    @staticmethod
    def get_gpu_foundation(*args, **kwargs) -> typing.Any: ...
    def get_graphics_interface_desc(self) -> carb._carb.PluginDesc: ...
    def get_local_device_index(self, arg0: int) -> int: ...
    def get_process_count(self) -> int: ...
    def get_process_index(self) -> int: ...
    def get_process_index_for_device(self, arg0: int) -> int: ...
    def shutdown_gpu_foundation(self) -> None: ...
    def shutdown_graphics(self) -> None: ...
    def startup_gpu_foundation(self) -> bool: ...
    def startup_graphics(self) -> bool: ...
    pass
class RpResource():
    pass
class Texture():
    pass
class TextureFormat():
    """
    Members:

      R8_UNORM

      R8_SNORM

      R8_UINT

      R8_SINT

      RG8_UNORM

      RG8_SNORM

      RG8_UINT

      RG8_SINT

      BGRA8_UNORM

      BGRA8_SRGB

      RGBA8_UNORM

      RGBA8_SNORM

      RGBA8_UINT

      RGBA8_SINT

      RGBA8_SRGB

      R16_UNORM

      R16_SNORM

      R16_UINT

      R16_SINT

      R16_SFLOAT

      RG16_UNORM

      RG16_SNORM

      RG16_UINT

      RG16_SINT

      RG16_SFLOAT

      RGBA16_UNORM

      RGBA16_SNORM

      RGBA16_UINT

      RGBA16_SINT

      RGBA16_SFLOAT

      R32_UINT

      R32_SINT

      R32_SFLOAT

      RG32_UINT

      RG32_SINT

      RG32_SFLOAT

      RGB32_UINT

      RGB32_SINT

      RGB32_SFLOAT

      RGBA32_UINT

      RGBA32_SINT

      RGBA32_SFLOAT

      R10_G10_B10_A2_UNORM

      R10_G10_B10_A2_UINT

      R11_G11_B10_UFLOAT

      R9_G9_B9_E5_UFLOAT

      B5_G6_R5_UNORM

      B5_G5_R5_A1_UNORM

      BC1_RGBA_UNORM

      BC1_RGBA_SRGB

      BC2_RGBA_UNORM

      BC2_RGBA_SRGB

      BC3_RGBA_UNORM

      BC3_RGBA_SRGB

      BC4_R_UNORM

      BC4_R_SNORM

      BC5_RG_UNORM

      BC5_RG_SNORM

      BC6H_RGB_UFLOAT

      BC6H_RGB_SFLOAT

      BC7_RGBA_UNORM

      BC7_RGBA_SRGB

      D16_UNORM

      D24_UNORM_S8_UINT

      D32_SFLOAT

      D32_SFLOAT_S8_UINT_X24

      R24_UNORM_X8

      X24_R8_UINT

      X32_R8_UINT_X24

      R32_SFLOAT_X8_X24

      SAMPLER_FEEDBACK_MIN_MIP

      SAMPLER_FEEDBACK_MIP_REGION_USED
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
    B5_G5_R5_A1_UNORM: omni.gpu_foundation_factory._gpu_foundation_factory.TextureFormat # value = <TextureFormat.B5_G5_R5_A1_UNORM: 48>
    B5_G6_R5_UNORM: omni.gpu_foundation_factory._gpu_foundation_factory.TextureFormat # value = <TextureFormat.B5_G6_R5_UNORM: 47>
    BC1_RGBA_SRGB: omni.gpu_foundation_factory._gpu_foundation_factory.TextureFormat # value = <TextureFormat.BC1_RGBA_SRGB: 50>
    BC1_RGBA_UNORM: omni.gpu_foundation_factory._gpu_foundation_factory.TextureFormat # value = <TextureFormat.BC1_RGBA_UNORM: 49>
    BC2_RGBA_SRGB: omni.gpu_foundation_factory._gpu_foundation_factory.TextureFormat # value = <TextureFormat.BC2_RGBA_SRGB: 52>
    BC2_RGBA_UNORM: omni.gpu_foundation_factory._gpu_foundation_factory.TextureFormat # value = <TextureFormat.BC2_RGBA_UNORM: 51>
    BC3_RGBA_SRGB: omni.gpu_foundation_factory._gpu_foundation_factory.TextureFormat # value = <TextureFormat.BC3_RGBA_SRGB: 54>
    BC3_RGBA_UNORM: omni.gpu_foundation_factory._gpu_foundation_factory.TextureFormat # value = <TextureFormat.BC3_RGBA_UNORM: 53>
    BC4_R_SNORM: omni.gpu_foundation_factory._gpu_foundation_factory.TextureFormat # value = <TextureFormat.BC4_R_SNORM: 56>
    BC4_R_UNORM: omni.gpu_foundation_factory._gpu_foundation_factory.TextureFormat # value = <TextureFormat.BC4_R_UNORM: 55>
    BC5_RG_SNORM: omni.gpu_foundation_factory._gpu_foundation_factory.TextureFormat # value = <TextureFormat.BC5_RG_SNORM: 58>
    BC5_RG_UNORM: omni.gpu_foundation_factory._gpu_foundation_factory.TextureFormat # value = <TextureFormat.BC5_RG_UNORM: 57>
    BC6H_RGB_SFLOAT: omni.gpu_foundation_factory._gpu_foundation_factory.TextureFormat # value = <TextureFormat.BC6H_RGB_SFLOAT: 60>
    BC6H_RGB_UFLOAT: omni.gpu_foundation_factory._gpu_foundation_factory.TextureFormat # value = <TextureFormat.BC6H_RGB_UFLOAT: 59>
    BC7_RGBA_SRGB: omni.gpu_foundation_factory._gpu_foundation_factory.TextureFormat # value = <TextureFormat.BC7_RGBA_SRGB: 62>
    BC7_RGBA_UNORM: omni.gpu_foundation_factory._gpu_foundation_factory.TextureFormat # value = <TextureFormat.BC7_RGBA_UNORM: 61>
    BGRA8_SRGB: omni.gpu_foundation_factory._gpu_foundation_factory.TextureFormat # value = <TextureFormat.BGRA8_SRGB: 10>
    BGRA8_UNORM: omni.gpu_foundation_factory._gpu_foundation_factory.TextureFormat # value = <TextureFormat.BGRA8_UNORM: 9>
    D16_UNORM: omni.gpu_foundation_factory._gpu_foundation_factory.TextureFormat # value = <TextureFormat.D16_UNORM: 63>
    D24_UNORM_S8_UINT: omni.gpu_foundation_factory._gpu_foundation_factory.TextureFormat # value = <TextureFormat.D24_UNORM_S8_UINT: 64>
    D32_SFLOAT: omni.gpu_foundation_factory._gpu_foundation_factory.TextureFormat # value = <TextureFormat.D32_SFLOAT: 65>
    D32_SFLOAT_S8_UINT_X24: omni.gpu_foundation_factory._gpu_foundation_factory.TextureFormat # value = <TextureFormat.D32_SFLOAT_S8_UINT_X24: 66>
    R10_G10_B10_A2_UINT: omni.gpu_foundation_factory._gpu_foundation_factory.TextureFormat # value = <TextureFormat.R10_G10_B10_A2_UINT: 44>
    R10_G10_B10_A2_UNORM: omni.gpu_foundation_factory._gpu_foundation_factory.TextureFormat # value = <TextureFormat.R10_G10_B10_A2_UNORM: 43>
    R11_G11_B10_UFLOAT: omni.gpu_foundation_factory._gpu_foundation_factory.TextureFormat # value = <TextureFormat.R11_G11_B10_UFLOAT: 45>
    R16_SFLOAT: omni.gpu_foundation_factory._gpu_foundation_factory.TextureFormat # value = <TextureFormat.R16_SFLOAT: 20>
    R16_SINT: omni.gpu_foundation_factory._gpu_foundation_factory.TextureFormat # value = <TextureFormat.R16_SINT: 19>
    R16_SNORM: omni.gpu_foundation_factory._gpu_foundation_factory.TextureFormat # value = <TextureFormat.R16_SNORM: 17>
    R16_UINT: omni.gpu_foundation_factory._gpu_foundation_factory.TextureFormat # value = <TextureFormat.R16_UINT: 18>
    R16_UNORM: omni.gpu_foundation_factory._gpu_foundation_factory.TextureFormat # value = <TextureFormat.R16_UNORM: 16>
    R24_UNORM_X8: omni.gpu_foundation_factory._gpu_foundation_factory.TextureFormat # value = <TextureFormat.R24_UNORM_X8: 67>
    R32_SFLOAT: omni.gpu_foundation_factory._gpu_foundation_factory.TextureFormat # value = <TextureFormat.R32_SFLOAT: 33>
    R32_SFLOAT_X8_X24: omni.gpu_foundation_factory._gpu_foundation_factory.TextureFormat # value = <TextureFormat.R32_SFLOAT_X8_X24: 70>
    R32_SINT: omni.gpu_foundation_factory._gpu_foundation_factory.TextureFormat # value = <TextureFormat.R32_SINT: 32>
    R32_UINT: omni.gpu_foundation_factory._gpu_foundation_factory.TextureFormat # value = <TextureFormat.R32_UINT: 31>
    R8_SINT: omni.gpu_foundation_factory._gpu_foundation_factory.TextureFormat # value = <TextureFormat.R8_SINT: 4>
    R8_SNORM: omni.gpu_foundation_factory._gpu_foundation_factory.TextureFormat # value = <TextureFormat.R8_SNORM: 2>
    R8_UINT: omni.gpu_foundation_factory._gpu_foundation_factory.TextureFormat # value = <TextureFormat.R8_UINT: 3>
    R8_UNORM: omni.gpu_foundation_factory._gpu_foundation_factory.TextureFormat # value = <TextureFormat.R8_UNORM: 1>
    R9_G9_B9_E5_UFLOAT: omni.gpu_foundation_factory._gpu_foundation_factory.TextureFormat # value = <TextureFormat.R9_G9_B9_E5_UFLOAT: 46>
    RG16_SFLOAT: omni.gpu_foundation_factory._gpu_foundation_factory.TextureFormat # value = <TextureFormat.RG16_SFLOAT: 25>
    RG16_SINT: omni.gpu_foundation_factory._gpu_foundation_factory.TextureFormat # value = <TextureFormat.RG16_SINT: 24>
    RG16_SNORM: omni.gpu_foundation_factory._gpu_foundation_factory.TextureFormat # value = <TextureFormat.RG16_SNORM: 22>
    RG16_UINT: omni.gpu_foundation_factory._gpu_foundation_factory.TextureFormat # value = <TextureFormat.RG16_UINT: 23>
    RG16_UNORM: omni.gpu_foundation_factory._gpu_foundation_factory.TextureFormat # value = <TextureFormat.RG16_UNORM: 21>
    RG32_SFLOAT: omni.gpu_foundation_factory._gpu_foundation_factory.TextureFormat # value = <TextureFormat.RG32_SFLOAT: 36>
    RG32_SINT: omni.gpu_foundation_factory._gpu_foundation_factory.TextureFormat # value = <TextureFormat.RG32_SINT: 35>
    RG32_UINT: omni.gpu_foundation_factory._gpu_foundation_factory.TextureFormat # value = <TextureFormat.RG32_UINT: 34>
    RG8_SINT: omni.gpu_foundation_factory._gpu_foundation_factory.TextureFormat # value = <TextureFormat.RG8_SINT: 8>
    RG8_SNORM: omni.gpu_foundation_factory._gpu_foundation_factory.TextureFormat # value = <TextureFormat.RG8_SNORM: 6>
    RG8_UINT: omni.gpu_foundation_factory._gpu_foundation_factory.TextureFormat # value = <TextureFormat.RG8_UINT: 7>
    RG8_UNORM: omni.gpu_foundation_factory._gpu_foundation_factory.TextureFormat # value = <TextureFormat.RG8_UNORM: 5>
    RGB32_SFLOAT: omni.gpu_foundation_factory._gpu_foundation_factory.TextureFormat # value = <TextureFormat.RGB32_SFLOAT: 39>
    RGB32_SINT: omni.gpu_foundation_factory._gpu_foundation_factory.TextureFormat # value = <TextureFormat.RGB32_SINT: 38>
    RGB32_UINT: omni.gpu_foundation_factory._gpu_foundation_factory.TextureFormat # value = <TextureFormat.RGB32_UINT: 37>
    RGBA16_SFLOAT: omni.gpu_foundation_factory._gpu_foundation_factory.TextureFormat # value = <TextureFormat.RGBA16_SFLOAT: 30>
    RGBA16_SINT: omni.gpu_foundation_factory._gpu_foundation_factory.TextureFormat # value = <TextureFormat.RGBA16_SINT: 29>
    RGBA16_SNORM: omni.gpu_foundation_factory._gpu_foundation_factory.TextureFormat # value = <TextureFormat.RGBA16_SNORM: 27>
    RGBA16_UINT: omni.gpu_foundation_factory._gpu_foundation_factory.TextureFormat # value = <TextureFormat.RGBA16_UINT: 28>
    RGBA16_UNORM: omni.gpu_foundation_factory._gpu_foundation_factory.TextureFormat # value = <TextureFormat.RGBA16_UNORM: 26>
    RGBA32_SFLOAT: omni.gpu_foundation_factory._gpu_foundation_factory.TextureFormat # value = <TextureFormat.RGBA32_SFLOAT: 42>
    RGBA32_SINT: omni.gpu_foundation_factory._gpu_foundation_factory.TextureFormat # value = <TextureFormat.RGBA32_SINT: 41>
    RGBA32_UINT: omni.gpu_foundation_factory._gpu_foundation_factory.TextureFormat # value = <TextureFormat.RGBA32_UINT: 40>
    RGBA8_SINT: omni.gpu_foundation_factory._gpu_foundation_factory.TextureFormat # value = <TextureFormat.RGBA8_SINT: 14>
    RGBA8_SNORM: omni.gpu_foundation_factory._gpu_foundation_factory.TextureFormat # value = <TextureFormat.RGBA8_SNORM: 12>
    RGBA8_SRGB: omni.gpu_foundation_factory._gpu_foundation_factory.TextureFormat # value = <TextureFormat.RGBA8_SRGB: 15>
    RGBA8_UINT: omni.gpu_foundation_factory._gpu_foundation_factory.TextureFormat # value = <TextureFormat.RGBA8_UINT: 13>
    RGBA8_UNORM: omni.gpu_foundation_factory._gpu_foundation_factory.TextureFormat # value = <TextureFormat.RGBA8_UNORM: 11>
    SAMPLER_FEEDBACK_MIN_MIP: omni.gpu_foundation_factory._gpu_foundation_factory.TextureFormat # value = <TextureFormat.SAMPLER_FEEDBACK_MIN_MIP: 71>
    SAMPLER_FEEDBACK_MIP_REGION_USED: omni.gpu_foundation_factory._gpu_foundation_factory.TextureFormat # value = <TextureFormat.SAMPLER_FEEDBACK_MIP_REGION_USED: 72>
    X24_R8_UINT: omni.gpu_foundation_factory._gpu_foundation_factory.TextureFormat # value = <TextureFormat.X24_R8_UINT: 68>
    X32_R8_UINT_X24: omni.gpu_foundation_factory._gpu_foundation_factory.TextureFormat # value = <TextureFormat.X32_R8_UINT_X24: 69>
    __members__: dict # value = {'R8_UNORM': <TextureFormat.R8_UNORM: 1>, 'R8_SNORM': <TextureFormat.R8_SNORM: 2>, 'R8_UINT': <TextureFormat.R8_UINT: 3>, 'R8_SINT': <TextureFormat.R8_SINT: 4>, 'RG8_UNORM': <TextureFormat.RG8_UNORM: 5>, 'RG8_SNORM': <TextureFormat.RG8_SNORM: 6>, 'RG8_UINT': <TextureFormat.RG8_UINT: 7>, 'RG8_SINT': <TextureFormat.RG8_SINT: 8>, 'BGRA8_UNORM': <TextureFormat.BGRA8_UNORM: 9>, 'BGRA8_SRGB': <TextureFormat.BGRA8_SRGB: 10>, 'RGBA8_UNORM': <TextureFormat.RGBA8_UNORM: 11>, 'RGBA8_SNORM': <TextureFormat.RGBA8_SNORM: 12>, 'RGBA8_UINT': <TextureFormat.RGBA8_UINT: 13>, 'RGBA8_SINT': <TextureFormat.RGBA8_SINT: 14>, 'RGBA8_SRGB': <TextureFormat.RGBA8_SRGB: 15>, 'R16_UNORM': <TextureFormat.R16_UNORM: 16>, 'R16_SNORM': <TextureFormat.R16_SNORM: 17>, 'R16_UINT': <TextureFormat.R16_UINT: 18>, 'R16_SINT': <TextureFormat.R16_SINT: 19>, 'R16_SFLOAT': <TextureFormat.R16_SFLOAT: 20>, 'RG16_UNORM': <TextureFormat.RG16_UNORM: 21>, 'RG16_SNORM': <TextureFormat.RG16_SNORM: 22>, 'RG16_UINT': <TextureFormat.RG16_UINT: 23>, 'RG16_SINT': <TextureFormat.RG16_SINT: 24>, 'RG16_SFLOAT': <TextureFormat.RG16_SFLOAT: 25>, 'RGBA16_UNORM': <TextureFormat.RGBA16_UNORM: 26>, 'RGBA16_SNORM': <TextureFormat.RGBA16_SNORM: 27>, 'RGBA16_UINT': <TextureFormat.RGBA16_UINT: 28>, 'RGBA16_SINT': <TextureFormat.RGBA16_SINT: 29>, 'RGBA16_SFLOAT': <TextureFormat.RGBA16_SFLOAT: 30>, 'R32_UINT': <TextureFormat.R32_UINT: 31>, 'R32_SINT': <TextureFormat.R32_SINT: 32>, 'R32_SFLOAT': <TextureFormat.R32_SFLOAT: 33>, 'RG32_UINT': <TextureFormat.RG32_UINT: 34>, 'RG32_SINT': <TextureFormat.RG32_SINT: 35>, 'RG32_SFLOAT': <TextureFormat.RG32_SFLOAT: 36>, 'RGB32_UINT': <TextureFormat.RGB32_UINT: 37>, 'RGB32_SINT': <TextureFormat.RGB32_SINT: 38>, 'RGB32_SFLOAT': <TextureFormat.RGB32_SFLOAT: 39>, 'RGBA32_UINT': <TextureFormat.RGBA32_UINT: 40>, 'RGBA32_SINT': <TextureFormat.RGBA32_SINT: 41>, 'RGBA32_SFLOAT': <TextureFormat.RGBA32_SFLOAT: 42>, 'R10_G10_B10_A2_UNORM': <TextureFormat.R10_G10_B10_A2_UNORM: 43>, 'R10_G10_B10_A2_UINT': <TextureFormat.R10_G10_B10_A2_UINT: 44>, 'R11_G11_B10_UFLOAT': <TextureFormat.R11_G11_B10_UFLOAT: 45>, 'R9_G9_B9_E5_UFLOAT': <TextureFormat.R9_G9_B9_E5_UFLOAT: 46>, 'B5_G6_R5_UNORM': <TextureFormat.B5_G6_R5_UNORM: 47>, 'B5_G5_R5_A1_UNORM': <TextureFormat.B5_G5_R5_A1_UNORM: 48>, 'BC1_RGBA_UNORM': <TextureFormat.BC1_RGBA_UNORM: 49>, 'BC1_RGBA_SRGB': <TextureFormat.BC1_RGBA_SRGB: 50>, 'BC2_RGBA_UNORM': <TextureFormat.BC2_RGBA_UNORM: 51>, 'BC2_RGBA_SRGB': <TextureFormat.BC2_RGBA_SRGB: 52>, 'BC3_RGBA_UNORM': <TextureFormat.BC3_RGBA_UNORM: 53>, 'BC3_RGBA_SRGB': <TextureFormat.BC3_RGBA_SRGB: 54>, 'BC4_R_UNORM': <TextureFormat.BC4_R_UNORM: 55>, 'BC4_R_SNORM': <TextureFormat.BC4_R_SNORM: 56>, 'BC5_RG_UNORM': <TextureFormat.BC5_RG_UNORM: 57>, 'BC5_RG_SNORM': <TextureFormat.BC5_RG_SNORM: 58>, 'BC6H_RGB_UFLOAT': <TextureFormat.BC6H_RGB_UFLOAT: 59>, 'BC6H_RGB_SFLOAT': <TextureFormat.BC6H_RGB_SFLOAT: 60>, 'BC7_RGBA_UNORM': <TextureFormat.BC7_RGBA_UNORM: 61>, 'BC7_RGBA_SRGB': <TextureFormat.BC7_RGBA_SRGB: 62>, 'D16_UNORM': <TextureFormat.D16_UNORM: 63>, 'D24_UNORM_S8_UINT': <TextureFormat.D24_UNORM_S8_UINT: 64>, 'D32_SFLOAT': <TextureFormat.D32_SFLOAT: 65>, 'D32_SFLOAT_S8_UINT_X24': <TextureFormat.D32_SFLOAT_S8_UINT_X24: 66>, 'R24_UNORM_X8': <TextureFormat.R24_UNORM_X8: 67>, 'X24_R8_UINT': <TextureFormat.X24_R8_UINT: 68>, 'X32_R8_UINT_X24': <TextureFormat.X32_R8_UINT_X24: 69>, 'R32_SFLOAT_X8_X24': <TextureFormat.R32_SFLOAT_X8_X24: 70>, 'SAMPLER_FEEDBACK_MIN_MIP': <TextureFormat.SAMPLER_FEEDBACK_MIN_MIP: 71>, 'SAMPLER_FEEDBACK_MIP_REGION_USED': <TextureFormat.SAMPLER_FEEDBACK_MIP_REGION_USED: 72>}
    pass
def acquire_gpu_foundation_factory_interface(plugin_name: str = None, library_path: str = None) -> IGpuFoundationFactory:
    pass
def get_driver_version(arg0: Device) -> carb._carb.Uint2:
    pass
def get_gpus_list(arg0: Device) -> typing.List[str]:
    pass
def get_limited_processor_core_info() -> dict:
    pass
def get_memory_info(system: bool = True, rss: bool = False, page: bool = False) -> dict:
    pass
def get_os_build_number() -> int:
    pass
def get_os_name() -> str:
    pass
def get_page_swap_info() -> dict:
    pass
def get_processor_brand_name() -> str:
    pass
def get_processor_core_count() -> dict:
    pass
def release_gpu_foundation_factory_interface(arg0: IGpuFoundationFactory) -> None:
    pass
