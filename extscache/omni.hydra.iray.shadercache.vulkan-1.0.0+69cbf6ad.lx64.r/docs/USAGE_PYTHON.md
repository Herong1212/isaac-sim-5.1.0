```{csv-table}
**Extension**: {{ extension_version }},**Documentation Generated**: {sub-ref}`today`
```

# Usage Examples

## How to create a new shader cache extension for a new render delegate

- Store the pre-compiled shaders into `cache\shadercache` folder of the extensions. 
- Shaders must have been compiled with the current ShaderDb and contain a version file in `cache\shadercache\common` folder produced by shaderDb.
- Implement the extension with the below snippet to register the search path:

```python
import omni.ext
from omni.gpu_foundation_factory import ShaderCacheConfig

class ShaderCacheExt(omni.ext.IExt):
    def on_startup(self, ext_id):
        self.shadercache_config = ShaderCacheConfig()
        self.shadercache_config.setup_shadercache_locations(ext_id)

    def on_shutdown(self):
        self.shadercache_config = None
```
