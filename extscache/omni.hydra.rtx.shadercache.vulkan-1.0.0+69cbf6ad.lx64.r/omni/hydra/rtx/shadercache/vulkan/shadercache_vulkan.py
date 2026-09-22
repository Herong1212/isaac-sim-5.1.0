import omni.ext
from omni.gpu_foundation_factory import ShaderCacheConfig

class ShaderCacheExt(omni.ext.IExt):
    def on_startup(self, ext_id):
        self.shadercache_config = ShaderCacheConfig()
        self.shadercache_config.setup_shadercache_locations(ext_id)

    def on_shutdown(self):
        self.shadercache_config = None
