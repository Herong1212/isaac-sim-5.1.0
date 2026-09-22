from ._gpu_foundation_factory import *
from .impl.foundation_extension import GpuFoundationConfig
from .impl.foundation_extension import ShaderCacheConfig

# Cached interface instance pointer
def get_gpu_foundation_factory_interface() -> IGpuFoundationFactory:
    """Returns cached :class:`omni.gpu_foundation.IGpuFoundationFactory` interface"""

    if not hasattr(get_gpu_foundation_factory_interface, "gpu_foundation_factory"):
        get_gpu_foundation_factory_interface.gpu_foundation_factory = acquire_gpu_foundation_factory_interface()
    return get_gpu_foundation_factory_interface.gpu_foundation_factory
