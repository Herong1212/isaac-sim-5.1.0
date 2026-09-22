import carb
import os.path

from pxr import Gf, UsdGeom, UsdLux, Sdf
import omni.graph.core as og
from omni.graph.action_core import get_interface
from omni.kit.hydra_texture import create_hydra_texture
import omni.kit.test
from omni.syntheticdata import SyntheticData, SyntheticDataStage

from ..utils import add_semantics

# Test the instance mapping update Fabric flag
class TestInstanceMappingUpdate(omni.kit.test.AsyncTestCase):

    def __init__(self, methodName: str) -> None:
        super().__init__(methodName=methodName)
        if "rtx" not in omni.usd.get_context().get_attached_hydra_engine_names():
            omni.usd.create_hydra_engine("rtx", omni.usd.get_context())
        # Dictionnary containing the pair (file_path , reference_data). If the reference data is None only the existence of the file is validated.
        self._golden_references = {}

        # Register a helper node type
        class SdTestCounter:
            """Helper Python node that counts input activations"""
            @staticmethod
            def compute(context: og.GraphContext, node: og.Node):
                count_attr = node.get_attribute("state:count")
                count = count_attr.get()
                count += 1
                count_attr.set(count)
                node.get_attribute("outputs:count").set(count)
                i_ag = get_interface()
                i_ag.set_execution_enabled("outputs:execOut")
                return True

            @staticmethod
            def get_node_type() -> str:
                return "omni.syntheticdata.SdTestCounter"

            @staticmethod
            def initialize_type(node_type: og.NodeType):
                node_type.add_input("inputs:execIn", "execution", True)
                node_type.add_state("state:count", "int", 0)
                node_type.add_output("outputs:execOut", "execution", True)
                node_type.add_output("outputs:count", "int", 0)
                return True

        # Avoid trying to register it twice
        if "omni.syntheticdata.SdTestCounter" not in og.get_registered_nodes():
            og.register_node_type(SdTestCounter, 1)

    def _texture_render_product_path(self, hydra_texture) -> str:
        '''Return a string to the UsdRender.Product used by the texture'''
        render_product = hydra_texture.get_render_product_path()
        if render_product and (not render_product.startswith('/')):
            render_product = '/Render/RenderProduct_' + render_product
        return render_product

    def _assert_count_equal(self, counter_template_name, count):
        count_output = SyntheticData.Get().get_node_attributes(
            counter_template_name,
            ["outputs:count"],
            self._render_product_path
        )
        assert "outputs:count" in count_output
        assert count_output["outputs:count"] == count

    def _activate_fabric_time_range(self) -> None:
        sdg_iface = SyntheticData.Get()
        if not sdg_iface.is_node_template_registered("TestSimFabricTimeRange"):
            sdg_iface.register_node_template(
                    SyntheticData.NodeTemplate(
                        SyntheticDataStage.ON_DEMAND,
                        "omni.syntheticdata.SdTestSimFabricTimeRange"
                    ),
                    template_name="TestSimFabricTimeRange"
                )
        sdg_iface.activate_node_template(
            "TestSimFabricTimeRange",
            attributes={"inputs:timeRangeName":"testFabricTimeRangeTrigger"}
        )
        if not sdg_iface.is_node_template_registered("TestPostRenderFabricTimeRange"):
            sdg_iface.register_node_template(
                SyntheticData.NodeTemplate(
                    SyntheticDataStage.POST_RENDER,
                    "omni.syntheticdata.SdFabricTimeRangeExecution",
                    [
                        SyntheticData.NodeConnectionTemplate(
                            SyntheticData.renderer_template_name(),
                            attributes_mapping=
                            {
                                "outputs:rp": "inputs:renderResults",
                                "outputs:gpu": "inputs:gpu"
                            }
                        )
                    ]
                ),
                template_name="TestPostRenderFabricTimeRange"
            )
        sdg_iface.activate_node_template(
            "TestPostRenderFabricTimeRange",
            0,
            [self._render_product_path],
            attributes={"inputs:timeRangeName":"testFabricTimeRangeTrigger"}
        )
        if not sdg_iface.is_node_template_registered("TestPostProcessFabricTimeRange"):
            sdg_iface.register_node_template(
                SyntheticData.NodeTemplate(
                    SyntheticDataStage.ON_DEMAND,
                    "omni.syntheticdata.SdFabricTimeRangeExecution",
                    [
                        SyntheticData.NodeConnectionTemplate("PostProcessDispatch"),
                        SyntheticData.NodeConnectionTemplate("TestPostRenderFabricTimeRange")
                    ]
                ),
                template_name="TestPostProcessFabricTimeRange"
            )
        sdg_iface.activate_node_template(
            "TestPostProcessFabricTimeRange",
            0,
            [self._render_product_path],
            attributes={"inputs:timeRangeName":"testFabricTimeRangeTrigger"}
        )
        if not sdg_iface.is_node_template_registered("TestPostProcessFabricTimeRangeCounter"):
            sdg_iface.register_node_template(
                SyntheticData.NodeTemplate(
                    SyntheticDataStage.ON_DEMAND,
                    "omni.syntheticdata.SdTestCounter",
                    [
                        SyntheticData.NodeConnectionTemplate(
                            "TestPostProcessFabricTimeRange",
                            attributes_mapping={"outputs:exec": "inputs:execIn"}
                        )
                    ]
                ),
                template_name="TestPostProcessFabricTimeRangeCounter"
            )
        sdg_iface.activate_node_template(
            "TestPostProcessFabricTimeRangeCounter",
            0,
            [self._render_product_path]
        )

    def _activate_instance_mapping_update(self) -> None:
        sdg_iface = SyntheticData.Get()
        if not sdg_iface.is_node_template_registered("TestPostProcessInstanceMappingUpdate"):
            sdg_iface.register_node_template(
                SyntheticData.NodeTemplate(
                    SyntheticDataStage.ON_DEMAND,
                    "omni.syntheticdata.SdTimeChangeExecution",
                    [
                        SyntheticData.NodeConnectionTemplate("InstanceMappingPtr"),
                        SyntheticData.NodeConnectionTemplate("PostProcessDispatch")
                    ]
                ),
                template_name="TestPostProcessInstanceMappingUpdate"
            )
        if not sdg_iface.is_node_template_registered("TestPostProcessInstanceMappingUpdateCounter"):
            sdg_iface.register_node_template(
                SyntheticData.NodeTemplate(
                    SyntheticDataStage.ON_DEMAND,
                    "omni.syntheticdata.SdTestCounter",
                    [
                        SyntheticData.NodeConnectionTemplate(
                            "TestPostProcessInstanceMappingUpdate",
                            attributes_mapping={"outputs:exec": "inputs:execIn"}
                        )
                    ]
                ),
                template_name="TestPostProcessInstanceMappingUpdateCounter"
            )
        sdg_iface.activate_node_template(
            "TestPostProcessInstanceMappingUpdateCounter",
            0,
            [self._render_product_path]
        )

    async def _request_fabric_time_range_trigger(self, number_of_frames=1):
        sdg_iface = SyntheticData.Get()
        sdg_iface.set_node_attributes("TestSimFabricTimeRange",{"inputs:numberOfFrames":number_of_frames})
        sdg_iface.request_node_execution("TestSimFabricTimeRange")
        await omni.kit.app.get_app().next_update_async()

    async def setUp(self):
        await omni.usd.get_context().new_stage_async()
        stage = omni.usd.get_context().get_stage()
        world_prim = UsdGeom.Xform.Define(stage,"/World")
        UsdGeom.Xformable(world_prim).AddTranslateOp().Set((0, 0, 0))
        UsdGeom.Xformable(world_prim).AddRotateXYZOp().Set((0, 0, 0))

        self._hydra_texture_0 = create_hydra_texture(
            "TEX0",
            512,
            512,
            omni.usd.get_context().get_name(),
            is_async=carb.settings.acquire_settings_interface().get("/app/asyncRendering")
        )
        self._render_product_path = self._texture_render_product_path(self._hydra_texture_0)

        await omni.syntheticdata.sensors.next_render_simulation_async(self._render_product_path)
        await omni.syntheticdata.sensors.next_render_simulation_async(self._render_product_path)

    async def tearDown(self):
        self._hydra_texture_0 = None

    async def test_case_0(self):
        """Test case 0 : no time range"""
        self._activate_fabric_time_range()
        await omni.syntheticdata.sensors.next_render_simulation_async(self._render_product_path, 11)
        self._assert_count_equal("TestPostProcessFabricTimeRangeCounter", 0)

    async def test_case_1(self):
        """Test case 1 : setup a time range of 5 frames"""
        self._activate_fabric_time_range()
        await omni.syntheticdata.sensors.next_render_simulation_async(self._render_product_path)
        await self._request_fabric_time_range_trigger(5)
        await omni.syntheticdata.sensors.next_render_simulation_async(self._render_product_path, 11)
        self._assert_count_equal("TestPostProcessFabricTimeRangeCounter", 5)

    async def test_case_2(self):
        """Test case 2 : initial instance mapping setup"""
        self._activate_instance_mapping_update()
        await omni.syntheticdata.sensors.next_render_simulation_async(self._render_product_path, 11)
        self._assert_count_equal("TestPostProcessInstanceMappingUpdateCounter", 1)

    async def test_case_3(self):
        """Test case 3 : setup an instance mapping with 1, 2, 3, 4 changes"""
        stage = omni.usd.get_context().get_stage()
        self._activate_instance_mapping_update()
        await omni.syntheticdata.sensors.next_render_simulation_async(self._render_product_path, 1)
        self._assert_count_equal("TestPostProcessInstanceMappingUpdateCounter", 1)
        sphere_prim = stage.DefinePrim("/World/Sphere", "Sphere")
        add_semantics(sphere_prim, "sphere")
        await omni.syntheticdata.sensors.next_render_simulation_async(self._render_product_path, 3)
        self._assert_count_equal("TestPostProcessInstanceMappingUpdateCounter", 2)
        sub_sphere_prim = stage.DefinePrim("/World/Sphere/Sphere", "Sphere")
        await omni.syntheticdata.sensors.next_render_simulation_async(self._render_product_path, 5)
        self._assert_count_equal("TestPostProcessInstanceMappingUpdateCounter", 3)
        add_semantics(sub_sphere_prim, "sphere")
        await omni.syntheticdata.sensors.next_render_simulation_async(self._render_product_path, 1)
        self._assert_count_equal("TestPostProcessInstanceMappingUpdateCounter", 4)