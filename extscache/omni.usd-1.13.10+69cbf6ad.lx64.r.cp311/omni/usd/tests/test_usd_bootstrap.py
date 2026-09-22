
import asyncio

import omni.kit.test
import omni.usd_libs

from pathlib import Path
from unittest import mock

from pxr import Tf, Usd


class TestUsdBootstrap(omni.kit.test.AsyncTestCase):
    # Verifies that TfEnvSettings are bootstrapped in the correct order--
    # see https://gitlab-master.nvidia.com/carbon/Graphene/merge_requests/3115#note_5019170
    async def test_tf_env_settings(self):

        # https://github.com/PixarAnimationStudios/USD/commit/1a82d34b1144caa85909b417d18148197fba551c
        usd_version = Usd.GetVersion()
        if usd_version < (0,20,11):
            self.assertEqual(Tf.GetEnvSetting("USDIMAGING_ENABLE_SPARSE_LIGHT_UPDATES"), 1)

        self.assertEqual(Tf.GetEnvSetting("PCP_DISABLE_TIME_SCALING_BY_LAYER_TCPS"), 0)

        # Disabled until all cases found in OM-9409 are addressed
        mdl_string = r'AperturePBR.mdl,AperturePBR_Opacity.mdl,AperturePBR_ThinOpaque.mdl,AperturePBR_ThinTranslucent.mdl,AperturePBR_Translucent.mdl,DebugWhite.mdl,DebugWhiteEmissive.mdl,Default.mdl,MdlStates.mdl,OmniGlass.mdl,OmniGlass_Opacity.mdl,OmniHair.mdl,OmniHairPresets.mdl,OmniPBR.mdl,OmniPBRBase.mdl,OmniPBR_ClearCoat.mdl,OmniPBR_ClearCoat_Opacity.mdl,OmniPBR_Opacity.mdl,OmniSurface.mdl,OmniSurface/OmniHairBase.mdl,OmniSurface/OmniImage.mdl,OmniSurface/OmniShared.mdl,OmniSurface/OmniSurfaceBase.mdl,OmniSurface/OmniSurfaceBlendBase.mdl,OmniSurface/OmniSurfaceLiteBase.mdl,OmniSurfaceBlend.mdl,OmniSurfaceLite.mdl,OmniSurfacePresets.mdl,OmniUe4Base.mdl,OmniUe4Function.mdl,OmniUe4FunctionExtension17.mdl,OmniUe4Subsurface.mdl,OmniUe4Translucent.mdl,OmniVolumeDensity.mdl,OmniVolumeNoise.mdl,UsdPreviewSurface.mdl,ad_3dsmax_maps.mdl,ad_3dsmax_materials.mdl,adobe/anisotropy.mdl,adobe/annotations.mdl,adobe/convert.mdl,adobe/materials.mdl,adobe/mtl.mdl,adobe/util.mdl,adobe/volume.mdl,alg/base/annotations.mdl,alg/base/core.mdl,alg/base/normalmapping.mdl,alg/materials/asm/standard_scatter.mdl,alg/materials/blinn.mdl,alg/materials/designer.mdl,alg/materials/designer/blinn.mdl,alg/materials/designer/lambert.mdl,alg/materials/designer/legacy/physically_metallic_roughness.mdl,alg/materials/designer/legacy/physically_metallic_roughness_coated.mdl,alg/materials/designer/legacy/physically_metallic_roughness_sss.mdl,alg/materials/designer/legacy/physically_specular_glossiness.mdl,alg/materials/designer/lights.mdl,alg/materials/designer/pbr.mdl,alg/materials/designer/skin.mdl,alg/materials/lambert.mdl,alg/materials/lights.mdl,alg/materials/physically_metallic_roughness.mdl,alg/materials/physically_specular_glossiness.mdl,anno.mdl,architectural.mdl,base.mdl,debug.mdl,df.mdl,environment.mdl,gltf/pbr.mdl,iray/architectural.mdl,iray/environment.mdl,iray/omni_light.mdl,limits.mdl,materialx/core.mdl,materialx/hsv.mdl,materialx/noise.mdl,materialx/pbrlib.mdl,materialx/sampling.mdl,materialx/stdlib.mdl,materialx/swizzle.mdl,math.mdl,nvidia/aux_definitions.mdl,nvidia/core_definitions.mdl,nvidia/support_definitions.mdl,omni_light.mdl,scene.mdl,state.mdl,std.mdl,tex.mdl,vray_maps.mdl,vray_materials.mdl'
        mdl_list = mdl_string.split(",")

        env_mdls = Tf.GetEnvSetting("OMNI_USD_RESOLVER_MDL_BUILTIN_PATHS").split(",")
        # We cannot compare mdl_list vs env_mdls here directly because it's possible for additional modules to be present in the env_mdls list as its contents are
        # dynamic due to the consideration of user defined mdl paths that can be set via environment variables or the Create preferences->Material->Local Paths configuration.
        # Therefore, the mdl_list that we test against contains only those modules that have been defined through the "/renderer/mdl/searchPaths/required" and
        # "/renderer/mdl/searchPaths/templates" configurations.  If additional modules are installed into the paths specified through the above two config paths then this
        # test will need to be updated. We could generate mdl_string dynamically as well; however in doing so we'd be using the exact same code used to generate env_mdls making
        # the test essentially useless.
        for module in mdl_list:
            self.assertIn(module, env_mdls)

        # this should really be tied to OpenUsd or NvUsd, but use a known version number for now
        nv_usd_dependent_value = 1 if usd_version < (0,24,5) else None
        self.assertEqual(Tf.GetEnvSetting("USDIMAGING_ENABLE_NESTED_GPRIMS"), nv_usd_dependent_value)
        self.assertEqual(Tf.GetEnvSetting("USDGEOM_XFORMCOMMONAPI_ALLOW_DOUBLES"), nv_usd_dependent_value)
        self.assertEqual(Tf.GetEnvSetting("HD_CHANGETRACKER_USE_CONTIGUOUS_VALUES_MAP"), nv_usd_dependent_value)

        nv_usd_dependent_value = 0 if usd_version < (0,24,5) else None
        self.assertEqual(Tf.GetEnvSetting("USDIMAGING_UNKNOWN_PROPERTIES_ARE_CLEAN"), nv_usd_dependent_value)
