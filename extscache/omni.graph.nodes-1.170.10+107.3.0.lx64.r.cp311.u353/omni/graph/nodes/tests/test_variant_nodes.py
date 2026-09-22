"""Testing the stability of the API in this module"""

import omni.graph.core as og
import omni.graph.core.tests as ogts
import omni.kit.test
import omni.usd
import usdrt
from pxr import Gf, Sdf


# ======================================================================
class TestVariantNodes(ogts.OmniGraphTestCase):
    def __init__(self, arg):
        super().__init__(arg)
        self.usda_file = "variant_sets.usda"
        self.reference_usda_file = "variant_sets_referenced.usda"
        self.input_prim = "/World/InputPrim"

    @staticmethod
    def set_variant_selection(prim_path, variant_set_name, variant_name):  # noqa: C901
        stage = omni.usd.get_context().get_stage()
        prim = stage.GetPrimAtPath(prim_path)
        variant_set = prim.GetVariantSet(variant_set_name)
        variant_names = variant_set.GetVariantNames()
        if variant_name not in variant_names:
            variant_set.AddVariant(variant_name)
        variant_set.SetVariantSelection(variant_name)

    def set_up_variant_sets(self):
        stage = omni.usd.get_context().get_stage()
        stage.DefinePrim("/World", "Xform")
        for prim_path in [self.input_prim]:
            prim = stage.DefinePrim(prim_path, "Xform")
            attr = prim.CreateAttribute("primvars:displayColor", Sdf.ValueTypeNames.Color3f)

            # set up different variable types
            bool_attr = prim.CreateAttribute("primvars:testBool", Sdf.ValueTypeNames.Bool)
            int_attr = prim.CreateAttribute("primvars:testInt", Sdf.ValueTypeNames.Int)
            double_attr = prim.CreateAttribute("primvars:testDouble", Sdf.ValueTypeNames.Double)
            vec2h_attr = prim.CreateAttribute("primvars:testVec2h", Sdf.ValueTypeNames.Half2)
            vec3i_attr = prim.CreateAttribute("primvars:testVec3i", Sdf.ValueTypeNames.Int3)
            vec4d_attr = prim.CreateAttribute("primvars:testVec4d", Sdf.ValueTypeNames.Double4)
            matrix4_attr = prim.CreateAttribute("primvars:testMatrix4d", Sdf.ValueTypeNames.Matrix4d)

            variant_set_name = "color"
            variant_sets = prim.GetVariantSets()
            variant_set = variant_sets.GetVariantSet(variant_set_name)

            variant_set.AddVariant("red")
            variant_set.AddVariant("green")
            variant_set.AddVariant("blue")

            variant_set.SetVariantSelection("red")
            with variant_set.GetVariantEditContext():
                attr.Set((1, 0, 0))
                bool_attr.Set(False)
                int_attr.Set(0)
                double_attr.Set(0)
                vec2h_attr.Set((0, 0))
                vec3i_attr.Set(Gf.Vec3i(0, 0, 0))
                vec4d_attr.Set((0, 0, 0, 0))
                matrix4_attr.Set(Gf.Matrix4d(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0))

            variant_set.SetVariantSelection("green")
            with variant_set.GetVariantEditContext():
                attr.Set((0, 1, 0))
                bool_attr.Set(True)
                int_attr.Set(1)
                double_attr.Set(1)
                vec2h_attr.Set((1, 1))
                vec3i_attr.Set(Gf.Vec3i(1, 1, 1))
                vec4d_attr.Set((1, 1, 1, 1))
                matrix4_attr.Set(Gf.Matrix4d(1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1))

            variant_set.SetVariantSelection("blue")
            with variant_set.GetVariantEditContext():
                attr.Set((0, 0, 1))
                bool_attr.Set(True)
                int_attr.Set(2)
                double_attr.Set(2)
                vec2h_attr.Set((2, 2))
                vec3i_attr.Set(Gf.Vec3i(2, 2, 2))
                vec4d_attr.Set((2, 2, 2, 2))
                matrix4_attr.Set(Gf.Matrix4d(2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2))

            variant_set.SetVariantSelection("default_color")

            variant_set_name = "size"
            variant_sets = prim.GetVariantSets()
            variant_set = variant_sets.GetVariantSet(variant_set_name)

            variant_set.AddVariant("small")
            variant_set.AddVariant("medium")
            variant_set.AddVariant("large")

            variant_set.SetVariantSelection("default_size")

    def get_variant_selection(self, prim_path, variant_set_name):
        stage = omni.usd.get_context().get_stage()
        prim = stage.GetPrimAtPath(prim_path)
        variant_set = prim.GetVariantSet(variant_set_name)
        return variant_set.GetVariantSelection()

    async def _test_variant_node(
        self,
        node_type,
        node_attrs,
        expected_values=None,
        expected_variants=None,
        expected_attr_values=None,
        expected_fabric_materials=None,
        usda_file=None,
        read_file=True,
        input_prim=None,
        use_connected_prim=False,
        variant_selection=None,
    ):
        input_prim = input_prim or self.input_prim
        await omni.usd.get_context().new_stage_async()
        if read_file:
            usda_file = usda_file or self.usda_file
            (result, error) = await ogts.load_test_file(usda_file, use_caller_subdirectory=True)
            self.assertTrue(result, error)
        else:
            self.set_up_variant_sets()

        if variant_selection:
            prim_path, variant_set_name, variant_name = variant_selection
            self.set_variant_selection(prim_path, variant_set_name, variant_name)

        keys = og.Controller.Keys
        controller = og.Controller()

        graph = "/TestGraph"
        variant_node = "VariantNode"

        values = [(f"{variant_node}.{key}", value) for key, value in node_attrs.items()]

        controller.edit(
            graph,
            {
                keys.CREATE_NODES: [
                    (variant_node, node_type),
                ],
                keys.SET_VALUES: values,
            },
        )

        stage = omni.usd.get_context().get_stage()
        # use a prim path connection instead of setting the value directly
        if use_connected_prim:
            (_, (_prim_at_path, _), _, _) = controller.edit(
                graph,
                {
                    keys.CREATE_NODES: [
                        ("ToTarget", "omni.graph.nodes.ToTarget"),
                        ("ConstToken", "omni.graph.nodes.ConstantToken"),
                    ],
                    keys.CONNECT: [
                        ("ConstToken.inputs:value", "ToTarget.inputs:value"),
                        ("ToTarget.outputs:converted", f"{variant_node}.inputs:prim"),
                    ],
                    keys.SET_VALUES: [
                        ("ConstToken.inputs:value", input_prim),
                    ],
                },
            )
        else:
            omni.kit.commands.execute(
                "AddRelationshipTarget",
                relationship=stage.GetPropertyAtPath(f"{graph}/{variant_node}.inputs:prim"),
                target=input_prim,
            )

        await controller.evaluate()
        stage.GetRootLayer().Export("test_variant_nodes.usda")
        if expected_values:
            for output in expected_values.keys():
                test_attribute = controller.attribute(output, f"{graph}/{variant_node}")
                actual_value = controller.get(attribute=test_attribute)

                if isinstance(expected_values[output], list):
                    actual_value = list(actual_value)

                self.assertTrue(
                    actual_value == expected_values[output],
                    f"actual_value: {actual_value}, expected_value: {expected_values[output]}",
                )

        if expected_variants:
            for prim_path, variant_set_name, expected_variant_name in expected_variants:
                actual_value = self.get_variant_selection(prim_path, variant_set_name)
                self.assertTrue(
                    actual_value == expected_variant_name,
                    f"actual_value: {actual_value}, expected_value: {expected_variant_name}",
                )

        if expected_attr_values:
            for prim_path, attr_name, expected_value in expected_attr_values:
                test_attribute = stage.GetPropertyAtPath(f"{prim_path}.{attr_name}")
                actual_value = test_attribute.Get()
                self.assertTrue(
                    actual_value == expected_value,
                    f"actual_value: {actual_value}, expected_value: {expected_value}",
                )

        if expected_fabric_materials:
            usd_context = omni.usd.get_context()
            rt_stage = usdrt.Usd.Stage.Attach(usd_context.get_stage_id())
            for prim_path, expected_value in expected_fabric_materials:
                prim = rt_stage.GetPrimAtPath(prim_path)
                rel = prim.GetRelationship(usdrt.UsdShade.Tokens.materialBinding)
                self.assertTrue(rel.IsValid())
                actual_value = rel.GetTargets()
                actual_value = str(rel.GetTargets()[0]) if actual_value else ""
                self.assertTrue(
                    actual_value == expected_value,
                    f"actual_value: {actual_value}, expected_value: {expected_value}",
                )

    async def test_get_variant_names_1(self):
        node_type = "omni.graph.nodes.GetVariantNames"
        node_attrs = {
            "inputs:variantSetName": "color",
        }
        expected_values = {"outputs:variantNames": ["blue", "green", "red"]}

        await self._test_variant_node(node_type, node_attrs, expected_values)

    async def test_get_variant_names_2(self):
        node_type = "omni.graph.nodes.GetVariantNames"
        node_attrs = {
            "inputs:variantSetName": "color",
        }
        expected_values = {"outputs:variantNames": ["blue", "green", "red"]}

        await self._test_variant_node(node_type, node_attrs, expected_values, use_connected_prim=False)
        await self._test_variant_node(node_type, node_attrs, expected_values, use_connected_prim=True)

    async def test_get_variant_selection(self):
        node_type = "omni.graph.nodes.GetVariantSelection"
        node_attrs = {
            "inputs:variantSetName": "color",
        }
        expected_values = {"outputs:variantName": "default_color"}

        await self._test_variant_node(node_type, node_attrs, expected_values)

    async def test_get_variant_selection_2(self):
        node_type = "omni.graph.nodes.GetVariantSelection"
        node_attrs = {
            "inputs:variantSetName": "color",
        }
        expected_values = {"outputs:variantName": "green"}

        variant_selection = (self.input_prim, "color", "green")

        await self._test_variant_node(
            node_type,
            node_attrs,
            expected_values,
            variant_selection=variant_selection,
            use_connected_prim=False,
        )
        await self._test_variant_node(
            node_type,
            node_attrs,
            expected_values,
            variant_selection=variant_selection,
            use_connected_prim=True,
        )

    async def test_get_variant_set_names(self):
        node_type = "omni.graph.nodes.GetVariantSetNames"
        node_attrs = {}
        expected_values = {"outputs:variantSetNames": ["color", "size", "material"]}

        await self._test_variant_node(node_type, node_attrs, expected_values)

    async def test_get_variant_set_names_2(self):
        node_type = "omni.graph.nodes.GetVariantSetNames"
        node_attrs = {}
        expected_values = {"outputs:variantSetNames": ["color", "size", "material"]}

        await self._test_variant_node(node_type, node_attrs, expected_values, use_connected_prim=False)
        await self._test_variant_node(node_type, node_attrs, expected_values, use_connected_prim=True)

    async def test_has_variant_set_1(self):
        node_type = "omni.graph.nodes.HasVariantSet"
        node_attrs = {
            "inputs:variantSetName": "color",
        }
        expected_values = {"outputs:exists": True}

        await self._test_variant_node(node_type, node_attrs, expected_values)

    async def test_has_variant_set_2(self):
        node_type = "omni.graph.nodes.HasVariantSet"
        node_attrs = {
            "inputs:variantSetName": "flavor",
        }
        expected_values = {"outputs:exists": False}

        await self._test_variant_node(node_type, node_attrs, expected_values)

    async def test_has_variant_set_3(self):
        node_type = "omni.graph.nodes.HasVariantSet"
        node_attrs = {
            "inputs:variantSetName": "flavor",
        }
        expected_values = {"outputs:exists": False}

        await self._test_variant_node(node_type, node_attrs, expected_values, use_connected_prim=False)
        await self._test_variant_node(node_type, node_attrs, expected_values, use_connected_prim=True)

    async def test_clear_variant_set_with_default(self):
        node_type = "omni.graph.nodes.ClearVariantSelection"
        node_attrs = {
            "inputs:variantSetName": "color",
        }
        expected_variants = [(self.input_prim, "color", "default_color")]

        await self._test_variant_node(node_type, node_attrs, expected_variants=expected_variants)

    async def test_clear_variant_set(self):
        node_type = "omni.graph.nodes.ClearVariantSelection"
        node_attrs = {
            "inputs:variantSetName": "color",
        }
        expected_variants = [(self.input_prim, "color", "default_color")]

        await self._test_variant_node(node_type, node_attrs, expected_variants=expected_variants, read_file=False)

    async def test_clear_variant_set_2(self):
        node_type = "omni.graph.nodes.ClearVariantSelection"
        node_attrs = {
            "inputs:variantSetName": "color",
        }
        expected_variants = [(self.input_prim, "color", "default_color")]

        await self._test_variant_node(
            node_type,
            node_attrs,
            expected_variants=expected_variants,
            read_file=False,
            use_connected_prim=False,
        )
        await self._test_variant_node(
            node_type,
            node_attrs,
            expected_variants=expected_variants,
            read_file=False,
            use_connected_prim=True,
        )

    async def test_clear_variant_set_clear_selection(self):
        """Test the setting to clear the variant selection"""
        node_type = "omni.graph.nodes.ClearVariantSelection"
        node_attrs = {
            "inputs:variantSetName": "color",
            "inputs:setVariant": True,
        }
        expected_variants = [(self.input_prim, "color", "")]

        await self._test_variant_node(node_type, node_attrs, expected_variants=expected_variants, read_file=False)

    async def test_set_variant_selection(self):
        node_type = "omni.graph.nodes.SetVariantSelection"
        node_attrs = {
            "inputs:setVariant": True,
            "inputs:variantSetName": "color",
            "inputs:variantName": "red",
        }
        expected_variants = [(self.input_prim, "color", "red")]

        await self._test_variant_node(node_type, node_attrs, expected_variants=expected_variants)

    async def test_set_variant_selection_2(self):
        node_type = "omni.graph.nodes.SetVariantSelection"
        node_attrs = {
            "inputs:setVariant": True,
            "inputs:variantSetName": "color",
            "inputs:variantName": "red",
        }
        expected_variants = [(self.input_prim, "color", "red")]

        await self._test_variant_node(
            node_type,
            node_attrs,
            expected_variants=expected_variants,
            use_connected_prim=False,
        )
        await self._test_variant_node(
            node_type,
            node_attrs,
            expected_variants=expected_variants,
            use_connected_prim=True,
        )

    async def test_blend_variants(self):
        node_type = "omni.graph.nodes.BlendVariants"
        node_attrs = {
            "inputs:variantSetName": "color",
            "inputs:blend": 0.5,
            "inputs:variantNameA": "red",
            "inputs:variantNameB": "green",
        }
        expected_attr_values = [
            (self.input_prim, "primvars:displayColor", [0.5, 0.5, 0.0]),
            (self.input_prim, "primvars:testBool", True),
            (self.input_prim, "primvars:testInt", 1),
            (self.input_prim, "primvars:testDouble", 0.5),
            (self.input_prim, "primvars:testVec2h", (0.5, 0.5)),
            (self.input_prim, "primvars:testVec3i", (1, 1, 1)),
            (self.input_prim, "primvars:testVec4d", (0.5, 0.5, 0.5, 0.5)),
            (
                self.input_prim,
                "primvars:testMatrix4d",
                Gf.Matrix4d(0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5),
            ),
        ]

        await self._test_variant_node(
            node_type,
            node_attrs,
            expected_attr_values=expected_attr_values,
            read_file=False,
        )

    async def test_set_variant_selection_material(self):
        node_type = "omni.graph.nodes.SetVariantSelection"
        node_attrs = {
            "inputs:setVariant": False,
            "inputs:variantSetName": "material",
            "inputs:variantName": "redMtl",
        }
        expected_fabric_materials = [(self.input_prim, "/World/Looks/RedMtl")]

        await self._test_variant_node(node_type, node_attrs, expected_fabric_materials=expected_fabric_materials)

    async def test_set_variant_selection_material_reference(self):
        node_type = "omni.graph.nodes.SetVariantSelection"
        node_attrs = {
            "inputs:setVariant": False,
            "inputs:variantSetName": "material",
            "inputs:variantName": "redMtl",
        }
        # Because we are using a reference, the input prim and material paths are different.
        # /World/Payload rather than /World
        expected_fabric_materials = [("/World/Payload/InputPrim", "/World/Payload/Looks/RedMtl")]

        await self._test_variant_node(
            node_type,
            node_attrs,
            usda_file=self.reference_usda_file,
            input_prim="/World/Payload/InputPrim",
            expected_fabric_materials=expected_fabric_materials,
        )

    async def test_clear_variant_selection_material(self):
        node_type = "omni.graph.nodes.ClearVariantSelection"
        node_attrs = {
            "inputs:setVariant": False,
            "inputs:variantSetName": "material",
        }
        expected_fabric_materials = [(self.input_prim, "")]

        await self._test_variant_node(node_type, node_attrs, expected_fabric_materials=expected_fabric_materials)

    async def test_blend_variants_material_1(self):
        node_type = "omni.graph.nodes.BlendVariants"
        node_attrs = {
            "inputs:setVariant": False,
            "inputs:variantSetName": "material",
            "inputs:blend": 0.4,
            "inputs:variantNameA": "redMtl",
            "inputs:variantNameB": "greenMtl",
        }
        expected_fabric_materials = [(self.input_prim, "/World/Looks/RedMtl")]

        await self._test_variant_node(
            node_type,
            node_attrs,
            expected_fabric_materials=expected_fabric_materials,
        )

    async def test_blend_variants_material_2(self):
        node_type = "omni.graph.nodes.BlendVariants"
        node_attrs = {
            "inputs:setVariant": False,
            "inputs:variantSetName": "material",
            "inputs:blend": 0.6,
            "inputs:variantNameA": "redMtl",
            "inputs:variantNameB": "greenMtl",
        }
        expected_fabric_materials = [(self.input_prim, "/World/Looks/GreenMtl")]

        await self._test_variant_node(
            node_type,
            node_attrs,
            expected_fabric_materials=expected_fabric_materials,
        )
