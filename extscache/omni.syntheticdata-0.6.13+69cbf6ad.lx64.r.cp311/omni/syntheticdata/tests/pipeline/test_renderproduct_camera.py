import carb

from pxr import Gf, UsdGeom, UsdLux, Sdf

from omni.kit.hydra_texture import create_hydra_texture
import omni.kit.test
from omni.syntheticdata import SyntheticData, SyntheticDataStage


# Test the instance mapping pipeline
class TestRenderProductCamera(omni.kit.test.AsyncTestCase):

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

    def register_test_rp_cam_pipeline(self):
        sdg_iface = SyntheticData.Get()
        if not sdg_iface.is_node_template_registered("TestSimRpCam"):
                sdg_iface.register_node_template(
                    SyntheticData.NodeTemplate(
                        SyntheticDataStage.SIMULATION,
                        "omni.syntheticdata.SdTestRenderProductCamera",
                        attributes={"inputs:stage":"simulation"}
                    ),
                    template_name="TestSimRpCam"
                )
        if not sdg_iface.is_node_template_registered("TestPostRpCam"):
            sdg_iface.register_node_template(
                SyntheticData.NodeTemplate(
                    SyntheticDataStage.POST_RENDER,
                    "omni.syntheticdata.SdTestRenderProductCamera",
                    [SyntheticData.NodeConnectionTemplate("PostRenderProductCamera")],
                    attributes={"inputs:stage":"postRender"}
                ),
                template_name="TestPostRpCam"
            )
        if not sdg_iface.is_node_template_registered("TestOnDemandRpCam"):
            sdg_iface.register_node_template(
                SyntheticData.NodeTemplate(
                    SyntheticDataStage.ON_DEMAND,
                    "omni.syntheticdata.SdTestRenderProductCamera",
                    [
                        SyntheticData.NodeConnectionTemplate("PostProcessRenderProductCamera"),
                        SyntheticData.NodeConnectionTemplate(
                            "PostProcessDispatch",
                            attributes_mapping={"outputs:renderResults": "inputs:renderResults"})
                    ],
                    attributes={"inputs:stage":"onDemand"}
                ),
                template_name="TestOnDemandRpCam"
            )

    def activate_test_rp_cam_pipeline(self, test_case_index):
        sdg_iface = SyntheticData.Get()
        attributes = {
            "inputs:renderProductCameraPath": self._camera_path,
            "inputs:width": self._resolution[0],
            "inputs:height": self._resolution[1],
            "inputs:traceError": True
        }
        sdg_iface.activate_node_template("TestSimRpCam", 0, [self.render_product_path(self._hydra_texture_0)], attributes)
        sdg_iface.activate_node_template("TestPostRpCam", 0, [self.render_product_path(self._hydra_texture_0)], attributes)
        sdg_iface.activate_node_template("TestOnDemandRpCam", 0, [self.render_product_path(self._hydra_texture_0)],attributes)


    async def wait_for_num_frames(self, num_frames):
        await omni.syntheticdata.sensors.next_render_simulation_async(self.render_product_path(self._hydra_texture_0), num_frames)

    async def setUp(self):
        await omni.usd.get_context().new_stage_async()

        self._camera_path = "/TestRPCamera"
        UsdGeom.Camera.Define(omni.usd.get_context().get_stage(), self._camera_path)
        self._resolution = [512,512]

        self._hydra_texture_0 = create_hydra_texture(
            "TEX0",
            width=self._resolution[0],
            height=self._resolution[1],
            usd_context_name=omni.usd.get_context().get_name(),
            usd_camera_path=self._camera_path,
            is_async=carb.settings.acquire_settings_interface().get("/app/asyncRendering")
        )

        self.register_test_rp_cam_pipeline()

    async def tearDown(self):
        self._hydra_texture_0 = None

    async def test_case_0(self):
        self.activate_test_rp_cam_pipeline(0)
        await self.wait_for_num_frames(33)
