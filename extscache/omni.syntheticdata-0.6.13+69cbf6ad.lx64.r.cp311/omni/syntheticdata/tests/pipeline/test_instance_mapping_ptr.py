import ctypes
import numpy as np

import carb

from pxr import Gf, UsdGeom, UsdLux, Sdf

from omni.kit.hydra_texture import create_hydra_texture
import omni.kit.test
from omni.syntheticdata import SyntheticData, SyntheticDataStage

from ..utils import add_semantics

# Test the instance mapping pipeline
class TestInstanceMappingPtr(omni.kit.test.AsyncTestCase):

    _invalid_sem_id = 65535

    def __init__(self, methodName: str) -> None:
        super().__init__(methodName=methodName)
        if "rtx" not in omni.usd.get_context().get_attached_hydra_engine_names():
            omni.usd.create_hydra_engine("rtx", omni.usd.get_context())

    def _get_semid_ptr_array(self, name, num):
        ptr_outputs = SyntheticData.Get().get_node_attributes("InstanceMappingPtr",[f"outputs:{name}"], self._render_product_path)
        c_ptr = ctypes.cast(ptr_outputs[f"outputs:{name}"],ctypes.POINTER(ctypes.c_ushort))
        data_ptr = np.ctypeslib.as_array(c_ptr,shape=(num,))
        return data_ptr

    async def create_scene(self):
        stage = omni.usd.get_context().get_stage()
        UsdGeom.Xform.Define(stage,"/World")
        sphere_prim = stage.DefinePrim("/World/Sphere", "Sphere")
        add_semantics(sphere_prim, "sphere")
        capsule0_prim = stage.DefinePrim("/World/Sphere/Capsule0", "Capsule")
        add_semantics(capsule0_prim, "capsule0")
        capsule1_prim = stage.DefinePrim("/World/Sphere/Capsule1", "Capsule")
        add_semantics(capsule1_prim, "capsule1")
        capsule2_prim = stage.DefinePrim("/World/Capsule2", "Capsule")
        add_semantics(capsule2_prim, "capsule2")
        stage.DefinePrim("/World/Sphere/Capsule3", "Capsule")
        stage.DefinePrim("/World/Capsule4", "Capsule")

    async def activate_sdg(self):
        sdg_iface = SyntheticData.Get()
        sdg_iface.activate_node_template("InstanceMappingPtr", 0, [self._render_product_path], attributes={"inputs:cudaPtr":False})

    async def setUp(self):
        await omni.usd.get_context().new_stage_async()
        self._hydra_texture_0 = create_hydra_texture(
            "TEX0",
            512,
            512,
            omni.usd.get_context().get_name(),
            is_async=carb.settings.acquire_settings_interface().get("/app/asyncRendering")
        )
        self._render_product_path = self._hydra_texture_0.get_render_product_path()
        if self._render_product_path and (not self._render_product_path.startswith('/')):
            self._render_product_path = '/Render/RenderProduct_' + self._render_product_path

        await self.create_scene()
        await self.activate_sdg()
        await omni.syntheticdata.sensors.next_render_simulation_async(self._render_product_path, 1)

    async def tearDown(self):
        self._hydra_texture_0 = None

    async def test_case_0(self):
        """test instances data"""
        output_names = ["outputs:numInstances","outputs:minInstanceIndex"]
        output_values = SyntheticData.Get().get_node_attributes("InstanceMappingPtr", output_names, self._render_product_path)
        sem_id_arr = self._get_semid_ptr_array("instanceMapPtr",output_values["outputs:numInstances"])
        assert(np.count_nonzero(sem_id_arr != TestInstanceMappingPtr._invalid_sem_id)==5)

    async def test_case_1(self):
        """test semantic data"""
        output_names = ["outputs:numSemantics","outputs:minSemanticIndex"]
        output_values = SyntheticData.Get().get_node_attributes("InstanceMappingPtr", output_names, self._render_product_path)
        assert(output_values["outputs:numSemantics"]==4)
        assert(output_values["outputs:minSemanticIndex"]==0)
        sem_id_arr = self._get_semid_ptr_array("semanticMapPtr",output_values["outputs:numSemantics"])
        assert(np.count_nonzero(sem_id_arr == TestInstanceMappingPtr._invalid_sem_id)==2)
