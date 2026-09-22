# Copyright (c) 2024, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
import os
import sys
import carb.settings
import carb.tokens
import omni.ext
import omni.kit.app
import json
import threading

"""
A helper to setup shader caches that can be used by omni.*.shadercache.[vulkan/d3d12] extensions.

Search paths to load:
 - exts/omni.*.shadercache.[vulkan/d3d12]/cache AND ./cache.
 - appShaderCachePath: the shared cache files needed by basic apps (mandatory). We choose omni.gpu_foundation.shadercache.
 - appShaderCachePathList: additional array of paths extended by each omni.*.shadercache extension.

Search path to write/read:
 - AppData/Local/ov/cache/shaders OR next to executable ./cache.
 - shaderCachePath: only one folder can write into at a time.
"""
class ShaderCacheConfig:
    # Static variables to hold all shader cache paths in a thread safe way, and set at once to appShaderCachePathList.
    shadercache_path_count = 0
    shadercache_paths = []
    shadercache_path_lock = threading.Lock()

    def __init__(self):
        self.settings = carb.settings.get_settings()
        self.ext_manager = omni.kit.app.get_app().get_extension_manager()

    
    def add_shadercache_extension_location(self, cache_path: str):
        """ Add the shadercache location of the extension, as a read-only location for shaderdb """
        with ShaderCacheConfig.shadercache_path_lock:
            if cache_path in ShaderCacheConfig.shadercache_paths:
                return

            ShaderCacheConfig.shadercache_path_count += 1
            ShaderCacheConfig.shadercache_paths.append(cache_path)
            appcache_paths_str = ", ".join(ShaderCacheConfig.shadercache_paths)
            carb.log_info(f"appShaderCachePathList: {appcache_paths_str}")
            self.settings.set_string_array("/rtx/shaderDb/appShaderCachePathList", ShaderCacheConfig.shadercache_paths)


    def create_shadercache_manager_file(self, cache_path: str):
        """ Generate _cache.json setting file to manage clean ups of shader caches via UI in OV launcher. """
        if os.path.isfile(cache_path):
            return

        dirname = os.path.dirname(cache_path)
        os.makedirs(dirname, exist_ok=True)

        with open(cache_path, "w") as outfile:
            # Maximum size of 10GB in the root folder for all shader caches, including Vulkan driver caches.
            dictionary_cache = {
                "name": "Shader Cache",
                "maxsize": 10,
            }
            json_content = json.dumps(dictionary_cache, indent=4)
            outfile.write(json_content)
            carb.log_info(f"_cache.json has been written to ${cache_path}.")

    def setup_shadercache_locations(self, ext_id, is_foundation_setup: bool=False):
        ext_root = self.ext_manager.get_extension_path(ext_id)
        local_cache = f"{ext_root}/cache/shadercache"

        # Paths for read-only pre-generated caches for each graphics API or custom cache groups in the future (immutable caches in release builds).
        # Each render can create its own folder and extend appShaderCachePathList array.
        os.makedirs(local_cache, exist_ok=True)
        self.add_shadercache_extension_location(local_cache)

        # The rest of function only needs to be called once by a main extension, which will be omni.gpu_foundation.shadercache extension.
        if is_foundation_setup is False:
            return

        tokens = carb.tokens.get_tokens_interface()
        is_portable = self.settings.get_as_bool("/app/portableMode")
        local_driver_cache = f"{ext_root}/cache/nv_shadercache"
        os.makedirs(local_driver_cache, exist_ok=True)

        # Path for new run-time shader caches. driver cache does not need {config}
        # All caches must go into a dedicated folder under "cache/shaders/", to allow _cache.json to manage them.
        # omni_cache will be a local cache in portable mode, outside read-only foundation extensions. We just use a shorter path.
        if is_portable:
            global_cache = tokens.resolve("${omni_cache}/shadercache")
            global_driver_cache = tokens.resolve("${omni_cache}/nv_shadercache")
        else:
            global_cache = tokens.resolve("${omni_cache}/shaders/shadercache/${kit_version_short}/${kit_git_hash}/${config}")
            global_driver_cache = tokens.resolve("${omni_cache}/shaders/nv_shadercache/${kit_version_short}/${kit_git_hash}")

        # If we running in portable mode both paths are equal and point to this extension.
        # This is how shader cache gets generated in kit: just run kit in portable mode and open some stages/materials.
        # app/App version of caches are immutable caches shipped by the application.
        self.settings.set_default("/rtx/shaderDb/appShaderCachePath", local_cache)
        self.settings.set_default("/rtx/shaderDb/shaderCachePath", global_cache)
        self.settings.set_default("/rtx/shaderDb/driverAppShaderCachePath", local_driver_cache)
        self.settings.set_default("/rtx/shaderDb/driverShaderCachePath", global_driver_cache)

        carb.log_info(f"appShaderCachePath: {local_cache}")
        carb.log_info(f"shaderCachePath: {global_cache}")
        carb.log_info(f"driverAppShaderCachePath: {local_driver_cache}")
        carb.log_info(f"driverShaderCachePath: {global_driver_cache}")

        # Generate _cache.json setting file to manage clean ups of shader caches via UI in OV launcher.
        # Exit if it is already created
        if not is_portable:
            cache_json = tokens.resolve("${omni_cache}/shaders/_cache.json")
            self.create_shadercache_manager_file(cache_json)


class GpuFoundationConfig(omni.ext.IExt):
    def on_startup(self, ext_id):
        pass

    def on_shutdown(self):
        pass
