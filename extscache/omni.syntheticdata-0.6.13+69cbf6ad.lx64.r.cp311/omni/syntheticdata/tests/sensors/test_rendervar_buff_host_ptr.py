# NOTE:
#   omni.kit.test - std python's unittest module with additional wrapping to add suport for async/await tests
#   For most things refer to unittest docs: https://docs.python.org/3/library/unittest.html
import unittest

import ctypes
import numpy as np
import carb.settings
import omni.kit.test
from omni.gpu_foundation_factory import TextureFormat
from omni.kit.viewport.utility import get_active_viewport
from pxr import UsdGeom, UsdLux

# Import extension python module we are testing with absolute import path, as if we are external user (other extension)
import omni.syntheticdata as syn

from ..utils import add_semantics

# Test the SyntheticData following nodes :
# - SdPostRenderVarTextureToBuffer : node to convert a texture device rendervar into a buffer device rendervar
# - SdPostRenderVarToHost : node to readback a device rendervar into a host rendervar
# - SdRenderVarPtr : node to expose in the action graph, raw device / host pointers on the renderVars
#
# the tests consists in pulling the ptr data and comparing it with the data ouputed by :
# - SdRenderVarToRawArray
#
class TestRenderVarBuffHostPtr(omni.kit.test.AsyncTestCase):

    _kPinnedMemorySetting = "/exts/omni.syntheticdata/renderVarToHost/usePinnedMemory"
    
    _tolerance = 1.1
    _outputs_ptr = ["outputs:dataPtr","outputs:width","outputs:height","outputs:bufferSize","outputs:format", "outputs:strides"]
    _outputs_arr = ["outputs:data","outputs:width","outputs:height","outputs:bufferSize","outputs:format"]

    @staticmethod
    def _texture_element_size(texture_format):
        if texture_format == int(TextureFormat.RGBA16_SFLOAT):
            return 8
        elif texture_format == int(TextureFormat.RGBA32_SFLOAT):
            return 16
        elif texture_format == int(TextureFormat.R32_SFLOAT):
            return 4
        elif texture_format == int(TextureFormat.RGBA8_UNORM):
            return 4
        elif texture_format == int(TextureFormat.R32_UINT):
            return 4
        else:
            return 0
    
    @staticmethod
    def _assert_equal_tex_infos(out_a, out_b):
        assert((out_a["outputs:width"] == out_b["outputs:width"]) and 
               (out_a["outputs:height"] == out_b["outputs:height"]) and 
               (out_a["outputs:format"] == out_b["outputs:format"]))

    @staticmethod
    def _assert_equal_buff_infos(out_a, out_b):
        assert((out_a["outputs:bufferSize"] == out_b["outputs:bufferSize"]))

    @staticmethod
    def _assert_equal_data(data_a, data_b):
        assert(np.amax(np.square(data_a - data_b)) < TestRenderVarBuffHostPtr._tolerance)

    def _get_raw_array(self, render_var):
        ptr_outputs = syn.SyntheticData.Get().get_node_attributes(render_var + "ExportRawArray", TestRenderVarBuffHostPtr._outputs_arr, self.render_product)
        is_texture = ptr_outputs["outputs:width"] > 0 
        if is_texture:
            elem_size = TestRenderVarBuffHostPtr._texture_element_size(ptr_outputs["outputs:format"])
            arr_shape = (ptr_outputs["outputs:height"], ptr_outputs["outputs:width"], elem_size)
            ptr_outputs["outputs:data"] = ptr_outputs["outputs:data"].reshape(arr_shape)
        return ptr_outputs

    def _get_ptr_array(self, render_var, ptr_suffix):
        ptr_outputs = syn.SyntheticData.Get().get_node_attributes(render_var + ptr_suffix, TestRenderVarBuffHostPtr._outputs_ptr, self.render_product)
        c_ptr = ctypes.cast(ptr_outputs["outputs:dataPtr"],ctypes.POINTER(ctypes.c_ubyte))
        is_texture = ptr_outputs["outputs:width"] > 0 
        if is_texture:
            elem_size = TestRenderVarBuffHostPtr._texture_element_size(ptr_outputs["outputs:format"])
            arr_shape = (ptr_outputs["outputs:height"], ptr_outputs["outputs:width"], elem_size)
            arr_strides = ptr_outputs["outputs:strides"]
            buffer_size = arr_strides[1] * arr_shape[1]
            arr_strides = (arr_strides[1], arr_strides[0], 1)
            data_ptr = np.ctypeslib.as_array(c_ptr,shape=(buffer_size,))
            data_ptr = np.lib.stride_tricks.as_strided(data_ptr, shape=arr_shape, strides=arr_strides)
        else:
            data_ptr = np.ctypeslib.as_array(c_ptr,shape=(ptr_outputs["outputs:bufferSize"],))
        ptr_outputs["outputs:dataPtr"] = data_ptr
        return ptr_outputs

    def _assert_equal_rv_ptr(self, render_var:str, ptr_suffix:str, texture=None):
        arr_out = self._get_raw_array(render_var)
        ptr_out = self._get_ptr_array(render_var,ptr_suffix)
        if not texture is None:
            if texture:
                TestRenderVarBuffHostPtr._assert_equal_tex_infos(arr_out,ptr_out)
            else:
                TestRenderVarBuffHostPtr._assert_equal_buff_infos(arr_out,ptr_out)
        TestRenderVarBuffHostPtr._assert_equal_data(arr_out["outputs:data"],ptr_out["outputs:dataPtr"])

    def _assert_equal_rv_ptr_size(self, render_var:str, ptr_suffix:str, arr_size:int):
        ptr_out = self._get_ptr_array(render_var,ptr_suffix)
        data_ptr = ptr_out["outputs:dataPtr"]
        # helper for setting the value : print the size if None
        if arr_size is None:
            print(f"EqualRVPtrSize : {render_var} = {data_ptr.size}")
        else:
            assert(data_ptr.size==arr_size)

    def _assert_equal_rv_arr(self, render_var:str, ptr_suffix:str, texture=None):
        arr_out_a = self._get_raw_array(render_var)
        arr_out_b = self._get_raw_array(render_var+ptr_suffix)
        if not texture is None:
            if texture:
                TestRenderVarBuffHostPtr._assert_equal_tex_infos(arr_out_a,arr_out_b)
            else:
                TestRenderVarBuffHostPtr._assert_equal_buff_infos(arr_out_a,arr_out_b)
        TestRenderVarBuffHostPtr._assert_equal_data(
            arr_out_a["outputs:data"].flatten(),arr_out_b["outputs:data"].flatten())

    def _assert_executed_rv_ptr(self, render_var:str, ptr_suffix:str):
        ptr_outputs = syn.SyntheticData.Get().get_node_attributes(render_var + ptr_suffix, ["outputs:exec"], self.render_product)
        assert(ptr_outputs["outputs:exec"]>0)
        
    def __init__(self, methodName: str) -> None:
        super().__init__(methodName=methodName)
        self._settings = carb.settings.acquire_settings_interface()

    async def setUp(self):
        await omni.usd.get_context().new_stage_async()
        stage = omni.usd.get_context().get_stage()
        world_prim = UsdGeom.Xform.Define(stage,"/World")
        UsdGeom.Xformable(world_prim).AddTranslateOp().Set((0, 0, 0))
        UsdGeom.Xformable(world_prim).AddRotateXYZOp().Set((0, 0, 0))

        sphere_prim = stage.DefinePrim("/World/Sphere", "Sphere")
        add_semantics(sphere_prim, "sphere")
        UsdGeom.Xformable(sphere_prim).AddTranslateOp().Set((0, 0, 0))
        UsdGeom.Xformable(sphere_prim).AddScaleOp().Set((77, 77, 77))
        UsdGeom.Xformable(sphere_prim).AddRotateXYZOp().Set((-90, 0, 0))
        sphere_prim.GetAttribute("primvars:displayColor").Set([(1, 0.3, 1)])

        capsule0_prim = stage.DefinePrim("/World/Sphere/Capsule0", "Capsule")
        add_semantics(capsule0_prim, "capsule0")
        UsdGeom.Xformable(capsule0_prim).AddTranslateOp().Set((3, 0, 0))
        UsdGeom.Xformable(capsule0_prim).AddRotateXYZOp().Set((0, 0, 0))
        capsule0_prim.GetAttribute("primvars:displayColor").Set([(0.3, 1, 0)])

        capsule1_prim = stage.DefinePrim("/World/Sphere/Capsule1", "Capsule")
        add_semantics(capsule1_prim, "capsule1")
        UsdGeom.Xformable(capsule1_prim).AddTranslateOp().Set((-3, 0, 0))
        UsdGeom.Xformable(capsule1_prim).AddRotateXYZOp().Set((0, 0, 0))
        capsule1_prim.GetAttribute("primvars:displayColor").Set([(0, 1, 0.3)])

        capsule2_prim = stage.DefinePrim("/World/Sphere/Capsule2", "Capsule")
        add_semantics(capsule2_prim, "capsule2")
        UsdGeom.Xformable(capsule2_prim).AddTranslateOp().Set((0, 3, 0))
        UsdGeom.Xformable(capsule2_prim).AddRotateXYZOp().Set((0, 0, 0))
        capsule2_prim.GetAttribute("primvars:displayColor").Set([(0.7, 0.1, 0.4)])

        capsule3_prim = stage.DefinePrim("/World/Sphere/Capsule3", "Capsule")
        add_semantics(capsule3_prim, "capsule3")
        UsdGeom.Xformable(capsule3_prim).AddTranslateOp().Set((0, -3, 0))
        UsdGeom.Xformable(capsule3_prim).AddRotateXYZOp().Set((0, 0, 0))
        capsule3_prim.GetAttribute("primvars:displayColor").Set([(0.1, 0.7, 0.4)])

        spherelight = UsdLux.SphereLight.Define(stage, "/SphereLight")
        spherelight.GetIntensityAttr().Set(30000)
        spherelight.GetRadiusAttr().Set(30)

        self.viewport = get_active_viewport()
        self.render_product = self.viewport.render_product_path
        
        await omni.kit.app.get_app().next_update_async()

    async def test_host_arr(self):
        """Test case : ExportRawArray vs hostExportRawArray"""
        render_vars = [
            "BoundingBox2DLooseSD",
            "SemanticLocalTransformSD"
        ]
        for render_var in render_vars:
            syn.SyntheticData.Get().activate_node_template(render_var + "ExportRawArray", 0, [self.render_product])
            syn.SyntheticData.Get().activate_node_template(render_var + "hostExportRawArray", 0, [self.render_product])
        await syn.sensors.next_render_simulation_async(self.render_product, 1)
        for render_var in render_vars:
            self._assert_equal_rv_arr(render_var,"host", False)

    async def test_host_ptr_size(self):
        """Test case : hostPtr vs golden size"""
        render_vars = {
            "BoundingBox3DSD" : 576,
            "BoundingBox2DLooseSD" : 144,
            "SemanticLocalTransformSD" : 320,
            "Camera3dPositionSD" : 14745600,
            "SemanticMapSD" : 10,
            "InstanceSegmentationSD" : 3686400,
            "SemanticBoundingBox3DCamExtentSD" : 120,
            "SemanticBoundingBox3DFilterInfosSD" : 24
        }
        for render_var in render_vars:
            syn.SyntheticData.Get().activate_node_template(render_var + "hostPtr", 0, [self.render_product])
        await syn.sensors.next_render_simulation_async(self.render_product, 1)
        for render_var, arr_size in render_vars.items():
            self._assert_equal_rv_ptr_size(render_var,"hostPtr", arr_size)

    async def test_pinned_setting_host_ptr_size(self):
        """Test case : hostPtr vs golden size (non-default pinned memory setting)"""
        default_pinned_memory_setting = self._settings.get(TestRenderVarBuffHostPtr._kPinnedMemorySetting)
        self._settings.set(TestRenderVarBuffHostPtr._kPinnedMemorySetting ,not default_pinned_memory_setting)
        render_vars = {
            "BoundingBox3DSD" : 576,
            "BoundingBox2DLooseSD" : 144,
            "SemanticLocalTransformSD" : 320,
            "Camera3dPositionSD" : 14745600,
            "SemanticMapSD" : 10,
            "InstanceSegmentationSD" : 3686400,
            "SemanticBoundingBox3DCamExtentSD" : 120,
            "SemanticBoundingBox3DFilterInfosSD" : 24
        }
        for render_var in render_vars:
            syn.SyntheticData.Get().activate_node_template(render_var + "hostPtr", 0, [self.render_product])
        await syn.sensors.next_render_simulation_async(self.render_product, 1)
        for render_var, arr_size in render_vars.items():
            self._assert_equal_rv_ptr_size(render_var,"hostPtr", arr_size)
        self._settings.set(TestRenderVarBuffHostPtr._kPinnedMemorySetting , default_pinned_memory_setting)

    async def test_buff_arr(self):
        """Test case : buffExportRawArray vs ExportRawArray"""
        render_vars = [
            "Camera3dPositionSD",
            "DistanceToImagePlaneSD",
            "SemanticSegmentationSDDisplay"
        ]
        syn.SyntheticData.Get().register_device_rendervar_tex_to_buff_templates(["SemanticSegmentationSDDisplay"])
        syn.SyntheticData.Get().register_export_rendervar_array_templates(["SemanticSegmentationSDDisplay", "SemanticSegmentationSDDisplaybuff"])
        for render_var in render_vars:
            syn.SyntheticData.Get().activate_node_template(render_var + "ExportRawArray", 0, [self.render_product])
            syn.SyntheticData.Get().activate_node_template(render_var + "buffExportRawArray", 0, [self.render_product])
        await syn.sensors.next_render_simulation_async(self.render_product, 1)
        for render_var in render_vars:
            self._assert_equal_rv_arr(render_var, "buff")

    async def test_host_ptr(self):
        """Test case : hostPtr vs ExportRawArray (buffers)"""
        render_vars = [
            "BoundingBox2DTightSD",
            "BoundingBox3DSD",
            "InstanceMapSD"
        ]
        for render_var in render_vars:
            syn.SyntheticData.Get().activate_node_template(render_var + "ExportRawArray", 0, [self.render_product])
            syn.SyntheticData.Get().activate_node_template(render_var + "hostPtr", 0, [self.render_product])
        await syn.sensors.next_render_simulation_async(self.render_product, 1)
        for render_var in render_vars:
            self._assert_equal_rv_ptr(render_var,"hostPtr",False)
            self._assert_executed_rv_ptr(render_var,"hostPtr")
            
    async def test_host_ptr_tex(self):
        """Test case : hostPtr vs ExportRawArray (textures)"""
        render_vars = [
            "NormalSD",
            "DistanceToCameraSD",
            "InstanceSegmentationSD",
            "BoundingBox3DSDDisplay"
        ]
        syn.SyntheticData.Get().register_device_rendervar_to_host_templates(["BoundingBox3DSDDisplay"])
        syn.SyntheticData.Get().register_export_rendervar_ptr_templates(["BoundingBox3DSDDisplayhost"])
        for render_var in render_vars:
            syn.SyntheticData.Get().activate_node_template(render_var + "ExportRawArray", 0, [self.render_product])
            syn.SyntheticData.Get().activate_node_template(render_var + "hostPtr", 0, [self.render_product])
        await syn.sensors.next_render_simulation_async(self.render_product, 1)
        for render_var in render_vars:
            self._assert_equal_rv_ptr(render_var,"hostPtr",True)
            
    async def test_buff_host_ptr(self):
        """Test case : buffhostPtr vs ExportRawArray (textures)"""
        render_vars = [
            "LdrColorSD",
            "InstanceSegmentationSD",
        ]
        for render_var in render_vars:
            syn.SyntheticData.Get().activate_node_template(render_var + "ExportRawArray", 0, [self.render_product])
            syn.SyntheticData.Get().activate_node_template(render_var + "buffhostPtr", 0, [self.render_product])
        await syn.sensors.next_render_simulation_async(self.render_product, 1)
        for render_var in render_vars:
            self._assert_equal_rv_ptr(render_var, "buffhostPtr",True)

    async def test_cuda_copy_buff_host_ptr(self):
        """Test case : buffhostPtr vs ExportRawArray (textures) [non-default cuda copy settings]"""
        cuda_copy_setting = not carb.settings.get_settings().get("/exts/omni.syntheticdata/renderVarTextureToBuffer/cudaCopyNoStride")
        render_vars = [
            "LdrColorSD",
            "InstanceSegmentationSD",
            "NormalSD"
        ]
        for render_var in render_vars:
            syn.SyntheticData.Get().activate_node_template(render_var + "ExportRawArray", 0, [self.render_product])
            syn.SyntheticData.Get().activate_node_template(render_var + "buff", 0, [self.render_product], attributes={"inputs:cudaCopyNoStride" : cuda_copy_setting})
            syn.SyntheticData.Get().activate_node_template(render_var + "buffhostPtr", 0, [self.render_product])
        await syn.sensors.next_render_simulation_async(self.render_product, 1)
        for render_var in render_vars:
            self._assert_equal_rv_ptr(render_var, "buffhostPtr",True)
            
    async def test_empty_semantic_host_ptr(self):
        """Test case : hostPtr (buffers) executed"""
        await omni.usd.get_context().new_stage_async()
        self.viewport = get_active_viewport()
        self.render_product = self.viewport.render_product_path
        await omni.kit.app.get_app().next_update_async()

        render_vars = [
            "BoundingBox2DTightSD",
            "BoundingBox3DSD",
            "InstanceMapSD"
        ]
        for render_var in render_vars:
            syn.SyntheticData.Get().activate_node_template(render_var + "hostPtr", 0, [self.render_product])
        await syn.sensors.next_render_simulation_async(self.render_product, 1)
        for render_var in render_vars:
            self._assert_executed_rv_ptr(render_var,"hostPtr")

    # After running each test
    async def tearDown(self):
        pass
