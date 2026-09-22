# Public API for module omni.gpu_foundation_factory:

## Classes

- class Device

- class IGpuFoundationFactory
  - def get_device_count(self) -> int
  - def get_device_index(self, arg0: int, arg1: int) -> int
  - def get_device_name(self, arg0: int) -> str
  - static def get_gpu_foundation(*args, **kwargs) -> typing.Any
  - def get_graphics_interface_desc(self) -> carb._carb.PluginDesc
  - def get_local_device_index(self, arg0: int) -> int
  - def get_process_count(self) -> int
  - def get_process_index(self) -> int
  - def get_process_index_for_device(self, arg0: int) -> int
  - def shutdown_gpu_foundation(self)
  - def shutdown_graphics(self)
  - def startup_gpu_foundation(self) -> bool
  - def startup_graphics(self) -> bool

- class RpResource

- class Texture

- class TextureFormat
  - def __init__(self, value: int)
  - [property] def name(self) -> str
  - [property] def value(self) -> int
  - B5_G5_R5_A1_UNORM: omni.gpu_foundation_factory._gpu_foundation_factory.TextureFormat
  - B5_G6_R5_UNORM: omni.gpu_foundation_factory._gpu_foundation_factory.TextureFormat
  - BC1_RGBA_SRGB: omni.gpu_foundation_factory._gpu_foundation_factory.TextureFormat
  - BC1_RGBA_UNORM: omni.gpu_foundation_factory._gpu_foundation_factory.TextureFormat
  - BC2_RGBA_SRGB: omni.gpu_foundation_factory._gpu_foundation_factory.TextureFormat
  - BC2_RGBA_UNORM: omni.gpu_foundation_factory._gpu_foundation_factory.TextureFormat
  - BC3_RGBA_SRGB: omni.gpu_foundation_factory._gpu_foundation_factory.TextureFormat
  - BC3_RGBA_UNORM: omni.gpu_foundation_factory._gpu_foundation_factory.TextureFormat
  - BC4_R_SNORM: omni.gpu_foundation_factory._gpu_foundation_factory.TextureFormat
  - BC4_R_UNORM: omni.gpu_foundation_factory._gpu_foundation_factory.TextureFormat
  - BC5_RG_SNORM: omni.gpu_foundation_factory._gpu_foundation_factory.TextureFormat
  - BC5_RG_UNORM: omni.gpu_foundation_factory._gpu_foundation_factory.TextureFormat
  - BC6H_RGB_SFLOAT: omni.gpu_foundation_factory._gpu_foundation_factory.TextureFormat
  - BC6H_RGB_UFLOAT: omni.gpu_foundation_factory._gpu_foundation_factory.TextureFormat
  - BC7_RGBA_SRGB: omni.gpu_foundation_factory._gpu_foundation_factory.TextureFormat
  - BC7_RGBA_UNORM: omni.gpu_foundation_factory._gpu_foundation_factory.TextureFormat
  - BGRA8_SRGB: omni.gpu_foundation_factory._gpu_foundation_factory.TextureFormat
  - BGRA8_UNORM: omni.gpu_foundation_factory._gpu_foundation_factory.TextureFormat
  - D16_UNORM: omni.gpu_foundation_factory._gpu_foundation_factory.TextureFormat
  - D24_UNORM_S8_UINT: omni.gpu_foundation_factory._gpu_foundation_factory.TextureFormat
  - D32_SFLOAT: omni.gpu_foundation_factory._gpu_foundation_factory.TextureFormat
  - D32_SFLOAT_S8_UINT_X24: omni.gpu_foundation_factory._gpu_foundation_factory.TextureFormat
  - R10_G10_B10_A2_UINT: omni.gpu_foundation_factory._gpu_foundation_factory.TextureFormat
  - R10_G10_B10_A2_UNORM: omni.gpu_foundation_factory._gpu_foundation_factory.TextureFormat
  - R11_G11_B10_UFLOAT: omni.gpu_foundation_factory._gpu_foundation_factory.TextureFormat
  - R16_SFLOAT: omni.gpu_foundation_factory._gpu_foundation_factory.TextureFormat
  - R16_SINT: omni.gpu_foundation_factory._gpu_foundation_factory.TextureFormat
  - R16_SNORM: omni.gpu_foundation_factory._gpu_foundation_factory.TextureFormat
  - R16_UINT: omni.gpu_foundation_factory._gpu_foundation_factory.TextureFormat
  - R16_UNORM: omni.gpu_foundation_factory._gpu_foundation_factory.TextureFormat
  - R24_UNORM_X8: omni.gpu_foundation_factory._gpu_foundation_factory.TextureFormat
  - R32_SFLOAT: omni.gpu_foundation_factory._gpu_foundation_factory.TextureFormat
  - R32_SFLOAT_X8_X24: omni.gpu_foundation_factory._gpu_foundation_factory.TextureFormat
  - R32_SINT: omni.gpu_foundation_factory._gpu_foundation_factory.TextureFormat
  - R32_UINT: omni.gpu_foundation_factory._gpu_foundation_factory.TextureFormat
  - R8_SINT: omni.gpu_foundation_factory._gpu_foundation_factory.TextureFormat
  - R8_SNORM: omni.gpu_foundation_factory._gpu_foundation_factory.TextureFormat
  - R8_UINT: omni.gpu_foundation_factory._gpu_foundation_factory.TextureFormat
  - R8_UNORM: omni.gpu_foundation_factory._gpu_foundation_factory.TextureFormat
  - R9_G9_B9_E5_UFLOAT: omni.gpu_foundation_factory._gpu_foundation_factory.TextureFormat
  - RG16_SFLOAT: omni.gpu_foundation_factory._gpu_foundation_factory.TextureFormat
  - RG16_SINT: omni.gpu_foundation_factory._gpu_foundation_factory.TextureFormat
  - RG16_SNORM: omni.gpu_foundation_factory._gpu_foundation_factory.TextureFormat
  - RG16_UINT: omni.gpu_foundation_factory._gpu_foundation_factory.TextureFormat
  - RG16_UNORM: omni.gpu_foundation_factory._gpu_foundation_factory.TextureFormat
  - RG32_SFLOAT: omni.gpu_foundation_factory._gpu_foundation_factory.TextureFormat
  - RG32_SINT: omni.gpu_foundation_factory._gpu_foundation_factory.TextureFormat
  - RG32_UINT: omni.gpu_foundation_factory._gpu_foundation_factory.TextureFormat
  - RG8_SINT: omni.gpu_foundation_factory._gpu_foundation_factory.TextureFormat
  - RG8_SNORM: omni.gpu_foundation_factory._gpu_foundation_factory.TextureFormat
  - RG8_UINT: omni.gpu_foundation_factory._gpu_foundation_factory.TextureFormat
  - RG8_UNORM: omni.gpu_foundation_factory._gpu_foundation_factory.TextureFormat
  - RGB32_SFLOAT: omni.gpu_foundation_factory._gpu_foundation_factory.TextureFormat
  - RGB32_SINT: omni.gpu_foundation_factory._gpu_foundation_factory.TextureFormat
  - RGB32_UINT: omni.gpu_foundation_factory._gpu_foundation_factory.TextureFormat
  - RGBA16_SFLOAT: omni.gpu_foundation_factory._gpu_foundation_factory.TextureFormat
  - RGBA16_SINT: omni.gpu_foundation_factory._gpu_foundation_factory.TextureFormat
  - RGBA16_SNORM: omni.gpu_foundation_factory._gpu_foundation_factory.TextureFormat
  - RGBA16_UINT: omni.gpu_foundation_factory._gpu_foundation_factory.TextureFormat
  - RGBA16_UNORM: omni.gpu_foundation_factory._gpu_foundation_factory.TextureFormat
  - RGBA32_SFLOAT: omni.gpu_foundation_factory._gpu_foundation_factory.TextureFormat
  - RGBA32_SINT: omni.gpu_foundation_factory._gpu_foundation_factory.TextureFormat
  - RGBA32_UINT: omni.gpu_foundation_factory._gpu_foundation_factory.TextureFormat
  - RGBA8_SINT: omni.gpu_foundation_factory._gpu_foundation_factory.TextureFormat
  - RGBA8_SNORM: omni.gpu_foundation_factory._gpu_foundation_factory.TextureFormat
  - RGBA8_SRGB: omni.gpu_foundation_factory._gpu_foundation_factory.TextureFormat
  - RGBA8_UINT: omni.gpu_foundation_factory._gpu_foundation_factory.TextureFormat
  - RGBA8_UNORM: omni.gpu_foundation_factory._gpu_foundation_factory.TextureFormat
  - SAMPLER_FEEDBACK_MIN_MIP: omni.gpu_foundation_factory._gpu_foundation_factory.TextureFormat
  - SAMPLER_FEEDBACK_MIP_REGION_USED: omni.gpu_foundation_factory._gpu_foundation_factory.TextureFormat
  - X24_R8_UINT: omni.gpu_foundation_factory._gpu_foundation_factory.TextureFormat
  - X32_R8_UINT_X24: omni.gpu_foundation_factory._gpu_foundation_factory.TextureFormat

- class GpuFoundationConfig(omni.ext.IExt)
  - def on_startup(self, ext_id)
  - def on_shutdown(self)

- class ShaderCacheConfig
  - shadercache_path_count: int
  - shadercache_paths: List
  - shadercache_path_lock: Unknown
  - def __init__(self)
  - def add_shadercache_extension_location(self, cache_path: str)
  - def create_shadercache_manager_file(self, cache_path: str)
  - def setup_shadercache_locations(self, ext_id, is_foundation_setup: bool = False)

## Functions

- def acquire_gpu_foundation_factory_interface(plugin_name: str = None, library_path: str = None) -> IGpuFoundationFactory
- def get_driver_version(arg0: Device) -> carb._carb.Uint2
- def get_gpus_list(arg0: Device) -> typing.List[str]
- def get_limited_processor_core_info() -> dict
- def get_memory_info(system: bool = True, rss: bool = False, page: bool = False) -> dict
- def get_os_build_number() -> int
- def get_os_name() -> str
- def get_page_swap_info() -> dict
- def get_processor_brand_name() -> str
- def get_processor_core_count() -> dict
- def release_gpu_foundation_factory_interface(arg0: IGpuFoundationFactory)
- def get_gpu_foundation_factory_interface() -> IGpuFoundationFactory
