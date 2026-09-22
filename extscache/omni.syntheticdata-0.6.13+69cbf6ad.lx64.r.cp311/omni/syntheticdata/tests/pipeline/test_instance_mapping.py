import carb

from pxr import Gf, UsdGeom, UsdLux, Sdf

from omni.kit.hydra_texture import create_hydra_texture
import omni.kit.test
from omni.syntheticdata import SyntheticData, SyntheticDataStage


# Test the instance mapping pipeline
class TestInstanceMapping(omni.kit.test.AsyncTestCase):

    def __init__(self, methodName: str) -> None:
        super().__init__(methodName=methodName)
        if "rtx" not in omni.usd.get_context().get_attached_hydra_engine_names():
            omni.usd.create_hydra_engine("rtx", omni.usd.get_context())

    def render_product_path(self, hydra_texture) -> str:
        '''Return a string to the UsdRender.Product used by the texture'''
        render_product = hydra_texture.get_render_product_path()
        if render_product and (not render_product.startswith('/')):
            render_product = '/Render/RenderProduct_' + render_product
        return render_product

    def register_test_instance_mapping_pipeline(self):
        sdg_iface = SyntheticData.Get()
        if not sdg_iface.is_node_template_registered("TestSimSWHFrameNumber"):
            sdg_iface.register_node_template(
                    SyntheticData.NodeTemplate(
                        SyntheticDataStage.SIMULATION,
                        "omni.syntheticdata.SdUpdateSwFrameNumber"
                    ),
                    template_name="TestSimSWHFrameNumber"
                )
        if not sdg_iface.is_node_template_registered("TestSimInstanceMapping"):
            sdg_iface.register_node_template(
                SyntheticData.NodeTemplate(
                    SyntheticDataStage.SIMULATION,
                    "omni.syntheticdata.SdTestInstanceMapping",
                    [
                        SyntheticData.NodeConnectionTemplate("TestSimSWHFrameNumber", ())
                    ],
                    {"inputs:stage":"simulation"}
                ),
                template_name="TestSimInstanceMapping"
            )
        if not sdg_iface.is_node_template_registered("TestOnDemandInstanceMapping"):
            sdg_iface.register_node_template(
                SyntheticData.NodeTemplate(
                    SyntheticDataStage.ON_DEMAND,
                    "omni.syntheticdata.SdTestInstanceMapping",
                    [
                        SyntheticData.NodeConnectionTemplate("InstanceMappingPtrWithTransforms"),
                        SyntheticData.NodeConnectionTemplate("TestSimInstanceMapping", (), attributes_mapping={"outputs:exec": "inputs:exec"})
                    ],
                    {"inputs:stage":"ondemand"}
                ),
                template_name="TestOnDemandInstanceMapping"
            )

    def activate_test_instance_mapping_pipeline(self, case_index):
        sdg_iface = SyntheticData.Get()
        sdg_iface.activate_node_template("TestSimInstanceMapping", attributes={"inputs:testCaseIndex":case_index})
        sdg_iface.activate_node_template("TestOnDemandInstanceMapping", 0,
                                         [self.render_product_path(self._hydra_texture_0)],
                                         {"inputs:testCaseIndex":case_index})
        sdg_iface.connect_node_template("TestSimInstanceMapping",
                                        "InstanceMappingPre", None,
                                        {"outputs:semanticFilterPredicate":"inputs:semanticFilterPredicate"})

    async def wait_for_num_frames(self, num_frames):
        await omni.syntheticdata.sensors.next_render_simulation_async(self.render_product_path(self._hydra_texture_0), num_frames)

    async def setUp(self):
        await omni.usd.get_context().new_stage_async()

        self._hydra_texture_0 = create_hydra_texture(
            "TEX0",
            512,
            512,
            omni.usd.get_context().get_name(),
            is_async=carb.settings.acquire_settings_interface().get("/app/asyncRendering")
        )

        self.register_test_instance_mapping_pipeline()

    async def tearDown(self):
        self._hydra_texture_0 = None

    async def test_case_0(self):
        self.activate_test_instance_mapping_pipeline(0)
        await self.wait_for_num_frames(1)

    async def test_case_1(self):
        self.activate_test_instance_mapping_pipeline(1)
        await self.wait_for_num_frames(1)

    async def test_case_2(self):
        self.activate_test_instance_mapping_pipeline(2)
        await self.wait_for_num_frames(1)

    async def test_case_3(self):
        self.activate_test_instance_mapping_pipeline(3)
        await self.wait_for_num_frames(1)

    async def test_case_4(self):
        self.activate_test_instance_mapping_pipeline(4)
        await self.wait_for_num_frames(1)

    async def test_case_5(self):
        self.activate_test_instance_mapping_pipeline(5)
        await self.wait_for_num_frames(1)

    async def test_case_6(self):
        self.activate_test_instance_mapping_pipeline(6)
        await self.wait_for_num_frames(1)
