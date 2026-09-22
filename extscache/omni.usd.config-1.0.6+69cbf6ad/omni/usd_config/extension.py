__all__ = ['Extension']

import os
from pathlib import Path

import carb

import omni.ext
import omni.kit.app

ENABLE_NESTED_GPRIMS_SETTINGS_PATH = "/usd/enableNestedGprims"
MDL_SEARCH_PATHS_REQUIRED = "/renderer/mdl/searchPaths/required"
MDL_SEARCH_PATHS_TEMPLATES = "/renderer/mdl/searchPaths/templates"

class Extension(omni.ext.IExt):
    def __init__(self):
        super().__init__()
        pass

    def on_startup(self):
        self._app = omni.kit.app.get_app()
        self._settings = carb.settings.acquire_settings_interface()

        self._settings.set_default_bool(ENABLE_NESTED_GPRIMS_SETTINGS_PATH, True)
        self._usd_enable_nested_gprims = self._settings.get(ENABLE_NESTED_GPRIMS_SETTINGS_PATH)

        self._setup_usd_env_settings()

        self._setup_usd_material_env_settings()

    def on_shutdown(self):
        self._settings = None
        self._app = None


    # This must be invoked before USD's TfRegistry for env settings gets initialized.
    # See https://gitlab-master.nvidia.com/carbon/Graphene/merge_requests/3115#note_5019170
    def _setup_usd_env_settings(self):
        is_release_build = not self._app.is_debug_build()
        if is_release_build:
            # Disable TfEnvSetting banners (alerting users to local environment overriding Usd defaults) in release builds.
            os.environ["TF_ENV_SETTING_ALERTS_ENABLED"] = "0"

        # Preferring translucent over additive shaders for opacity mapped preview shaders in HdStorm.
        os.environ["HDST_USE_TRANSLUCENT_MATERIAL_TAG"] = "1"

        # Experiment with sparse light updates.
        # https://github.com/PixarAnimationStudios/USD/commit/1a82d34b1144caa85909b417d18148197fba551c
        # Remove this when nv-usd 20.11+ is enabled in the build.
        os.environ["USDIMAGING_ENABLE_SPARSE_LIGHT_UPDATES"] = "1"

        if self._usd_enable_nested_gprims:
            # Enable imaging refresh for nested gprims (needed for light gizmos).
            # https://nvidia-omniverse.atlassian.net/browse/OM-9446
            os.environ["USDIMAGING_ENABLE_NESTED_GPRIMS"] = "1"

        # Enable support for querying doubles in XformCommonAPI::GetXformVectors
        os.environ["USDGEOM_XFORMCOMMONAPI_ALLOW_DOUBLES"] = "1"

        # Continue supporting old mdl schema in UsdShade for now.
        os.environ["USDSHADE_OLD_MDL_SCHEMA_SUPPORT"] = "1"

        # Disable primvar invalidation in UsdImagingGprimAdapter so that Kit's scene delegate can perform its own primvar
        # analysis.
        os.environ["USDIMAGING_GPRIMADAPTER_PRIMVAR_INVALIDATION"] = "0"

        # OM-18759
        # Disable auto-scaling of time samples from layers whose timeCodesPerSecond do not match that of
        # the stage's root layer.
        # Eventually Pixar will retire this runtime switch; we'll need tooling to find and fix all
        # non-compliant assets to maintain their original animated intent.
        # OM-28725
        # Enable auto-scaling because more and more animation content, e.g. Machinima contents, need
        # this feature. Kit now has property window to adjust timeCodePerSecond for each layer so it won't
        # be a big issue if animator brings in two layers with different timeCodePerSecond. Need a validator
        # to notify the authors such info though.
        os.environ["PCP_DISABLE_TIME_SCALING_BY_LAYER_TCPS"] = "0"

        # OM-18814
        # Temporarily disable notification when setting interpolation mode.
        # This needs to be investigated further after Ampere demos are delivered.
        os.environ["USDSTAGE_DISABLE_INTERP_NOTICE"] = "1"

        # Properties which are unknown to UsdImagingGprimAdapter do not invalidate the rprim (disabled for now-
        # see OM-9049. Use whitelist, blacklist, and carb logging in
        # omni::usd::hydra::SceneDelegate::ProcessNonAdapterBasedPropertyChange to help contribute to re-enabling it).
        # os.environ["USDIMAGING_UNKNOWN_PROPERTIES_ARE_CLEAN] = "1"

        # OM-38943
        # Enable parallel sync for non-material sprims (i.e., lights).
        os.environ["HD_ENABLE_MULTITHREADED_NON_MATERIAL_SPRIM_SYNC"] = "1"

        # OM-39636
        # Disable scene index emulation until we have integated it with our HdMaterialNode changes for MDL support.
        os.environ["HD_ENABLE_SCENE_INDEX_EMULATION"] = "0"

        # OM-47199
        # Disable the MDL Builtin Bypass for omni_usd_resolver
        os.environ["OMNI_USD_RESOLVER_MDL_BUILTIN_BYPASS"] = "1"

        # OM-62080
        # Use NV-specific maps for optimized Hydra change tracking
        os.environ["HD_CHANGETRACKER_USE_CONTIGUOUS_VALUES_MAP"] = "1"

        # OM-93197
        # Suppress warning spew about material bindings until assets are addressed
        os.environ["USD_SHADE_WARN_ON_MISSING_MATERIAL_BINDING_API"] = "0"



    def _setup_usd_material_env_settings(self):
        def gather_mdl_modules(path, prefix=""):
            try:
                if not path.exists():
                    return
            except:
                return

            for child in path.iterdir():
                if child.is_file() and (child.suffix == ".mdl"):
                    mdl_modules.add(prefix + child.name)

                elif child.is_dir():
                    gather_mdl_modules(child, prefix + child.stem + "/")


        def process_mdl_search_path(settings_path):
            paths = self._settings.get(settings_path)
            if not paths:
                carb.log_warn(f"Unable to query '{settings_path}' from carb.settings.")
                return

            paths = [Path(p.strip()) for p in paths.split(";") if p.strip()]

            for p in paths:
                gather_mdl_modules(p)

        def set_materialx_paths():
            # TODO: Handle omni.materialx.libs being loaded at runtime
            try:
                import MaterialX
            except ModuleNotFoundError:
                carb.log_warn("Enable omni.materialx.libs extension to use MaterialX")
                return

            # OM-19420, OM-88291
            # Set the MaterialX library path in order to add mtlx nodes to the NDR
            defaultDataSearchPath = Path(MaterialX.getDefaultDataSearchPath().asString())

            if defaultDataSearchPath:
                paths = [str(defaultDataSearchPath / folder) for folder in MaterialX.getDefaultDataLibraryFolders()]
                mtlx_library_paths = os.pathsep.join(paths)

                if "PXR_MTLX_STDLIB_SEARCH_PATHS" in os.environ:
                    os.environ["PXR_MTLX_STDLIB_SEARCH_PATHS"] += os.pathsep + mtlx_library_paths
                else:
                    os.environ["PXR_MTLX_STDLIB_SEARCH_PATHS"] = mtlx_library_paths

        # use a set to avoid dupliate module names
        # if Neuray finds multiple modules with the same name only the first is loaded into the database
        mdl_modules = set()

        process_mdl_search_path(MDL_SEARCH_PATHS_REQUIRED)
        process_mdl_search_path(MDL_SEARCH_PATHS_TEMPLATES)

        os.environ["OMNI_USD_RESOLVER_MDL_BUILTIN_PATHS"] = ",".join(mdl_modules)

        set_materialx_paths()