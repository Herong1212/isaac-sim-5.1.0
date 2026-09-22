import carb
import os.path
import pathlib
import shutil

from pxr import UsdGeom, UsdLux, Sdf
from ..utils import add_semantics

from omni.kit.hydra_texture import create_hydra_texture
import omni.kit.test
from omni.syntheticdata import SyntheticData, SyntheticDataStage

# Test the instance mapping pipeline
class TestRenderVarHostToDisk(omni.kit.test.AsyncTestCase):

    OUTPUTS_DIR = pathlib.Path(omni.kit.test.get_test_output_path())
    EXTENSION_FOLDER_PATH = pathlib.Path(omni.kit.app.get_app().get_extension_manager().get_extension_path_by_module(__name__))
    GOLDEN_DIR = pathlib.Path(os.path.dirname(os.path.abspath(__file__))) / ".." / "data" / "golden" / "renderVarHostToDisk"
    COMP_THRESHOLD = 1e-5

    def __init__(self, methodName: str) -> None:
        super().__init__(methodName=methodName)
        if "rtx" not in omni.usd.get_context().get_attached_hydra_engine_names():
            omni.usd.create_hydra_engine("rtx", omni.usd.get_context())

    def _texture_render_product_path(self, hydra_texture) -> str:
        '''Return a string to the UsdRender.Product used by the texture'''
        render_product = hydra_texture.get_render_product_path()
        if render_product and (not render_product.startswith('/')):
            render_product = '/Render/RenderProduct_' + render_product
        return render_product

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
        sdg_iface.activate_node_template("TestSimFabricTimeRange", attributes={"inputs:timeRangeName":"testFabricTimeRangeTrigger"})
        sdg_iface.activate_node_template(
            SyntheticData.rendervar_host_to_disk_trigger_template_name(),
            0,
            [self._render_product_path],
            attributes={"inputs:timeRangeName":"testFabricTimeRangeTrigger"}
        )

    async def _request_fabric_time_range_trigger(self, number_of_frames=1):
        sdg_iface = SyntheticData.Get()
        sdg_iface.set_node_attributes("TestSimFabricTimeRange",{"inputs:numberOfFrames":number_of_frames})
        sdg_iface.request_node_execution("TestSimFabricTimeRange")
        await omni.kit.app.get_app().next_update_async()

    def _activate_write_pipeline(self, render_vars: list, rational_time_in_filename=False, detach_resource=False):
        sdg_iface = SyntheticData.Get()
        render_product_paths = [self._render_product_path]
        attributes = {
            "inputs:outputRationalRenderTime":rational_time_in_filename,
            "inputs:outputFolder":str(TestRenderVarHostToDisk.OUTPUTS_DIR),
            "inputs:detachResourceBeforeDispatch" : detach_resource
        }
        for render_var in render_vars:
            sdg_iface.activate_node_template(render_var+"PostCopyToDisk", 0, render_product_paths, attributes)

    async def setUp(self):
        await omni.usd.get_context().new_stage_async()

        stage = omni.usd.get_context().get_stage()
        camera_0 = UsdGeom.Camera.Define(stage, "/Camera0").GetPrim()
        camera_0.CreateAttribute("cameraProjectionType", Sdf.ValueTypeNames.Token).Set("fisheyePolynomial")
        UsdGeom.Xformable(camera_0).AddTranslateOp().Set((0, 50, 0))
        UsdGeom.Xformable(camera_0).AddRotateXYZOp().Set((-90, 0, 0))

        self._hydra_texture_0 = create_hydra_texture(
            "TEX0",
            512,
            512,
            omni.usd.get_context().get_name(),
            "/Camera0",
            is_async=carb.settings.acquire_settings_interface().get("/app/asyncRendering")
        )
        self._render_product_path = self._texture_render_product_path(self._hydra_texture_0)
        self._reference_data = {}
        self._output_directory_rp = TestRenderVarHostToDisk.OUTPUTS_DIR.joinpath(self._render_product_path.strip("/"))
        self._activate_fabric_time_range()

        spherelight = UsdLux.SphereLight.Define(stage, "/SphereLight")
        spherelight.GetIntensityAttr().Set(30000)
        spherelight.GetRadiusAttr().Set(30)

        world_cube_prim = stage.DefinePrim("/World/Cube", "Cube")
        UsdGeom.Xformable(world_cube_prim).AddTranslateOp().Set((100, 0, 0))
        UsdGeom.Xformable(world_cube_prim).AddScaleOp().Set((30, 30, 30))
        UsdGeom.Xformable(world_cube_prim).AddRotateXYZOp().Set((-90, 0, 0))
        add_semantics(world_cube_prim, "cube", "class")


        world_sphere_prim = stage.DefinePrim("/World/Sphere", "Sphere")
        UsdGeom.Xformable(world_sphere_prim).AddTranslateOp().Set((-100, 0, 0))
        UsdGeom.Xformable(world_sphere_prim).AddScaleOp().Set((30, 30, 30))
        UsdGeom.Xformable(world_sphere_prim).AddRotateXYZOp().Set((-90, 0, 0))
        add_semantics(world_sphere_prim, "sphere", "type")

        await omni.syntheticdata.sensors.next_render_simulation_async(self._render_product_path, 1)

    async def tearDown(self):
        self._hydra_texture_0 = None
        omni.usd.get_context().close_stage() # closing stage to ensure IO tasks terminated
        for file_path, golden_img_name in self._reference_data.items():
            assert(os.path.isfile(file_path))
            if not golden_img_name is None:
                from omni.kit.test_helpers_gfx.compare_utils import finalize_capture_and_compare, ComparisonMetric
                shutil.copyfile(file_path, pathlib.Path(self._output_directory_rp).joinpath(golden_img_name))
                finalize_capture_and_compare(
                    golden_img_name,
                    TestRenderVarHostToDisk.COMP_THRESHOLD,
                    self._output_directory_rp,
                    TestRenderVarHostToDisk.GOLDEN_DIR,
                    metric=ComparisonMetric.MEAN_ERROR_SQUARED
                )

    async def test_case_0(self):
        """Test case : write 3 color frames """
        self._activate_write_pipeline(["LdrColorbuffhost","HdrColorbuffhost"])
        await self._request_fabric_time_range_trigger(3)
        for i in range(3):
            self._reference_data[str(self._output_directory_rp.joinpath(f"LdrColor_00000{i}.png"))]=None
            self._reference_data[str(self._output_directory_rp.joinpath(f"HdrColor_00000{i}.exr"))]=None
        await omni.syntheticdata.sensors.next_render_simulation_async(self._render_product_path, 3)

    async def test_case_1(self):
        """Test case : write 2 CameraDistance and InstanceSegmentationSD frames """
        self._activate_write_pipeline(["DistanceToCameraSDbuffhost","InstanceSegmentationSDbuffhost"])
        await self._request_fabric_time_range_trigger(2)
        for i in range(2):
            self._reference_data[str(self._output_directory_rp.joinpath(f"DistanceToCameraSD_00000{i}.exr"))]=None
            self._reference_data[str(self._output_directory_rp.joinpath(f"InstanceSegmentationSD_00000{i}.tif"))]=None
        await omni.syntheticdata.sensors.next_render_simulation_async(self._render_product_path, 2)

    async def test_case_2(self):
        """Test case : write 1 SemanticLabelTokenSD, InstanceMappingInfoSD and SemanticBoundingBox2DExtentTightSD frame """
        self._activate_write_pipeline(["SemanticLabelTokenSDhost", "InstanceMappingInfoSDhost", "SemanticBoundingBox2DExtentTightSDbuffhost"])
        await self._request_fabric_time_range_trigger(1)
        for i in range(1):
            self._reference_data[str(self._output_directory_rp.joinpath(f"SemanticLabelTokenSDhost_00000{i}.bin"))]=None
            self._reference_data[str(self._output_directory_rp.joinpath(f"InstanceMappingInfoSDhost_00000{i}.bin"))]=None
            self._reference_data[str(self._output_directory_rp.joinpath(f"SemanticBoundingBox2DExtentTightSDhost_00000{i}.bin"))]=None
        await omni.syntheticdata.sensors.next_render_simulation_async(self._render_product_path, 1)

    async def test_case_3(self):
        """Test case : write 2 Camera3dPositionSD RenderProductCameraSD frames (detach resource mode)"""
        self._activate_write_pipeline(["Camera3dPositionSDbuffhost","RenderProductCameraSD"], detach_resource=True)
        await self._request_fabric_time_range_trigger(2)
        for i in range(2):
            self._reference_data[str(self._output_directory_rp.joinpath(f"Camera3dPositionSD_00000{i}.exr"))]=None
            self._reference_data[str(self._output_directory_rp.joinpath(f"RenderProductCameraSD_00000{i}.bin"))]=None
        await omni.syntheticdata.sensors.next_render_simulation_async(self._render_product_path, 3)

    async def test_case_4(self):
        """Test case : write 1 color, distance to camera, and normal frame and compare to golden"""
        self._activate_write_pipeline(["LdrColorbuffhost", "DistanceToCameraSDDisplaybuffhost", "NormalSDDisplaybuffhost"])
        await self._request_fabric_time_range_trigger(1)
        for i in range(1):
            self._reference_data[str(self._output_directory_rp.joinpath(f"LdrColor_00000{i}.png"))]=f"tc4_color_00000{i}.png"
            self._reference_data[str(self._output_directory_rp.joinpath(f"DistanceToCameraSDDisplay_00000{i}.png"))]=f"tc4_distance_to_camera_00000{i}.png"
            self._reference_data[str(self._output_directory_rp.joinpath(f"NormalSDDisplay_00000{i}.png"))]=f"tc4_normal_00000{i}.png"
        await omni.syntheticdata.sensors.next_render_simulation_async(self._render_product_path, 1)
