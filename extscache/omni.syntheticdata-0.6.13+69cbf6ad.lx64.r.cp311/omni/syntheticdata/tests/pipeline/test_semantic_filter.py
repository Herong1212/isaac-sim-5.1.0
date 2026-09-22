# NOTE:
#   omni.kit.test - std python's unittest module with additional wrapping to add suport for async/await tests
#   For most things refer to unittest docs: https://docs.python.org/3/library/unittest.html
import carb
import omni.kit.test
from omni.gpu_foundation_factory import TextureFormat
from omni.syntheticdata import SyntheticData, SyntheticDataStage
from omni.kit.hydra_texture import create_hydra_texture

from pxr import UsdGeom, Sdf, UsdLux
from ..utils import add_semantics

import numpy as np
import ctypes

# Test the semantic filter
class TestSemanticFilter(omni.kit.test.AsyncTestCase):

    _outputs_ptr = ["outputs:dataPtr","outputs:width","outputs:height","outputs:bufferSize","outputs:format", "outputs:strides"]

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
    def _equal_segmentation(data_a, data_b):
        return ((data_a>0) == (data_b>0)).all()

    def _get_uint_tex_ptr(self, ptr_template_name):
        ptr_outputs = SyntheticData.Get().get_node_attributes(ptr_template_name, TestSemanticFilter._outputs_ptr, self._render_product_path)
        c_ptr = ctypes.cast(ptr_outputs["outputs:dataPtr"],ctypes.POINTER(ctypes.c_uint))
        is_texture = ptr_outputs["outputs:width"] > 0
        assert(is_texture)
        elem_size = TestSemanticFilter._texture_element_size(ptr_outputs["outputs:format"])
        arr_shape = (ptr_outputs["outputs:height"], ptr_outputs["outputs:width"], 1)
        arr_strides = ptr_outputs["outputs:strides"]
        arr_strides = (arr_strides[1], arr_strides[0], elem_size)
        data_ptr = np.ctypeslib.as_array(c_ptr,shape=arr_strides)
        data_ptr = np.lib.stride_tricks.as_strided(data_ptr, shape=arr_shape, strides=arr_strides)
        return data_ptr

    def _texture_render_product_path(self, hydra_texture) -> str:
        '''Return a string to the UsdRender.Product used by the texture'''
        render_product = hydra_texture.get_render_product_path()
        if render_product and (not render_product.startswith('/')):
            render_product = '/Render/RenderProduct_' + render_product
        return render_product

    def activate_instance_segmentation(self):
        SyntheticData.Get().activate_node_template("InstanceSegmentationSDbuffhostPtr", 0, [self._render_product_path])

    def fetch_instance_segmentation(self):
        return self._get_uint_tex_ptr("InstanceSegmentationSDbuffhostPtr").copy()

    def activate_semantic_filter_segmentation(self, filter_name):
        template_name = filter_name + "SemanticFilterSegmentationMapSD"
        if template_name not in SyntheticData._ogn_templates_registry:
            SyntheticData.register_node_template(
                SyntheticData.NodeTemplate(
                    SyntheticDataStage.POST_RENDER,
                    "omni.syntheticdata.SdPostSemanticFilterSegmentationMap",
                    [
                        SyntheticData.NodeConnectionTemplate(SyntheticData._rendererTemplateName),
                        SyntheticData.NodeConnectionTemplate(SyntheticData.Get().get_semantic_filter_label_template_name(filter_name, True)),
                        SyntheticData.NodeConnectionTemplate("InstanceMappingPost"),
                        SyntheticData.NodeConnectionTemplate("PostRenderProductCamera"),
                        SyntheticData.NodeConnectionTemplate("InstanceSegmentationSD")
                    ]
                ),
                template_name=template_name
            )
            SyntheticData.register_device_rendervar_tex_to_buff_templates([template_name])
            SyntheticData.register_device_rendervar_to_host_templates([template_name+"buff"])
            SyntheticData.register_export_rendervar_ptr_templates([template_name+"buffhost"])
        SyntheticData.Get().activate_node_template(template_name+"buffhostPtr", 0, [self._render_product_path])

    def fetch_semantic_filter_segmentation(self, filter_name):
        return self._get_uint_tex_ptr(filter_name + "SemanticFilterSegmentationMapSD" + "buffhostPtr").copy()

    def __init__(self, methodName: str) -> None:
        super().__init__(methodName=methodName)
        if "rtx" not in omni.usd.get_context().get_attached_hydra_engine_names():
            omni.usd.create_hydra_engine("rtx", omni.usd.get_context())

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
        await omni.syntheticdata.sensors.next_render_simulation_async(self._render_product_path)

        SyntheticData.Get().set_semantic_filter("classFilter","class:*")
        SyntheticData.Get().activate_node_template(SyntheticData.Get().get_semantic_filter_label_template_name("classFilter", False), 0, [self._render_product_path])
        SyntheticData.Get().set_semantic_filter("typeFilter","type:*")
        SyntheticData.Get().activate_node_template(SyntheticData.Get().get_semantic_filter_label_template_name("typeFilter", False), 0, [self._render_product_path])
        SyntheticData.Get().set_semantic_filter("nameThisFilter","name:this")
        SyntheticData.Get().activate_node_template(SyntheticData.Get().get_semantic_filter_label_template_name("nameThisFilter", False), 0, [self._render_product_path])

        await omni.syntheticdata.sensors.next_render_simulation_async(self._render_product_path)

    async def tearDown(self):
        self._hydra_texture_0 = None

    def fetch_semantic_label_tokens(self, filter_name):
        output_names = ["outputs:numSemantics", "outputs:semanticLabelTokenSDHostPtr"]
        outputs = SyntheticData.Get().get_node_attributes(
            SyntheticData.Get().get_semantic_filter_label_template_name(filter_name, False),
            output_names, self._render_product_path)
        assert(outputs and outputs["outputs:semanticLabelTokenSDHostPtr"])
        c_ptr = ctypes.cast(outputs["outputs:semanticLabelTokenSDHostPtr"],ctypes.POINTER(ctypes.c_uint64))
        data_ptr = np.ctypeslib.as_array(c_ptr,shape=(outputs["outputs:numSemantics"],))
        return data_ptr

    async def check_num_valid_labels(self, filter_name, expected_num_valid_labels):
        num_valid_labels = np.count_nonzero(self.fetch_semantic_label_tokens(filter_name))
        assert num_valid_labels == expected_num_valid_labels

    async def test_semantic_filter_count_all(self):
        # scene
        stage = omni.usd.get_context().get_stage()
        world_prim = stage.DefinePrim("/World", "Plane")
        add_semantics(world_prim, "world", "type")
        world_cube_prim = stage.DefinePrim("/World/Cube", "Cube")
        add_semantics(world_cube_prim, "cube", "class")
        world_cube_sphere_prim = stage.DefinePrim("/World/Cube/Sphere", "Sphere")
        add_semantics(world_cube_sphere_prim, "sphere", "class")
        world_capsule_prim = stage.DefinePrim("/World/Capsule", "Capsule")
        add_semantics(world_capsule_prim, "capsule", "class")
        cube_prim = stage.DefinePrim("/Cube", "Cube")
        add_semantics(cube_prim, "this", "name")
        capsule_prim = stage.DefinePrim("/Capsule", "Capsule")
        add_semantics(capsule_prim, "aspirin", "name")
        nothing_prim = stage.DefinePrim("/Nothing", "Plane")
        add_semantics(nothing_prim, "nothing", "type")

        await omni.syntheticdata.sensors.next_render_simulation_async(self._render_product_path, 1)

        await self.check_num_valid_labels("classFilter",3)
        await self.check_num_valid_labels("typeFilter",2)
        await self.check_num_valid_labels("nameThisFilter",1)

    async def test_semantic_filter_map_class(self):

        self.activate_instance_segmentation()
        self.activate_semantic_filter_segmentation("classFilter")

        # scene
        stage = omni.usd.get_context().get_stage()
        world_cube_prim = stage.DefinePrim("/World/Cube", "Cube")
        UsdGeom.Xformable(world_cube_prim).AddTranslateOp().Set((100, 0, 0))
        UsdGeom.Xformable(world_cube_prim).AddScaleOp().Set((30, 30, 30))
        UsdGeom.Xformable(world_cube_prim).AddRotateXYZOp().Set((-90, 0, 0))
        add_semantics(world_cube_prim, "cube", "class")

        spherelight = UsdLux.SphereLight.Define(stage, "/SphereLight")
        spherelight.GetIntensityAttr().Set(30000)
        spherelight.GetRadiusAttr().Set(30)

        await omni.syntheticdata.sensors.next_render_simulation_async(self._render_product_path, 1)

        class_instance_map = self.fetch_instance_segmentation()

        world_sphere_prim = stage.DefinePrim("/World/Sphere", "Sphere")
        UsdGeom.Xformable(world_sphere_prim).AddTranslateOp().Set((-100, 0, 0))
        UsdGeom.Xformable(world_sphere_prim).AddScaleOp().Set((30, 30, 30))
        UsdGeom.Xformable(world_sphere_prim).AddRotateXYZOp().Set((-90, 0, 0))
        add_semantics(world_sphere_prim, "sphere", "type")

        await omni.syntheticdata.sensors.next_render_simulation_async(self._render_product_path, 1)

        all_instance_map = self.fetch_instance_segmentation()
        semantic_filter_map = self.fetch_semantic_filter_segmentation("classFilter")

        assert(TestSemanticFilter._equal_segmentation(class_instance_map, semantic_filter_map))
        assert(not TestSemanticFilter._equal_segmentation(all_instance_map, semantic_filter_map))
