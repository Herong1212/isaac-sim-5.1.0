"""Testing nodes that allow writing to specific layers"""

import omni.graph.core as og
import omni.graph.core.tests as ogts
import omni.kit.test
import omni.usd
import OmniGraphSchemaTools
from pxr import Sdf, Usd, UsdGeom


# ======================================================================
class TestWriteToLayers(ogts.OmniGraphTestCase):
    def __init__(self, arg):
        super().__init__(arg)
        self.stage = None
        self.session_layer = None
        self.root_layer = None
        self.sub_layer_01 = None
        self.sub_layer_02 = None
        self.define_layer = None
        self.test_layers = []
        self.test_layer_count = 0

    TEST_GRAPH_PATH = "/World/TestGraph"

    async def setUp(self):
        """Set up  test environment, to be torn down when done"""
        await super().setUp()

        usd_context = omni.usd.get_context()
        self.stage: Usd.Stage = usd_context.get_stage()

        self.session_layer = self.stage.GetSessionLayer()
        self.sub_layer_01 = Sdf.Layer.CreateAnonymous("sub_layer_01")
        self.sub_layer_02 = Sdf.Layer.CreateAnonymous("sub_layer_02")
        self.define_layer = Sdf.Layer.CreateAnonymous("define")
        self.root_layer = self.stage.GetRootLayer()
        self.root_layer.subLayerPaths.append(self.sub_layer_01.identifier)
        self.root_layer.subLayerPaths.append(self.sub_layer_02.identifier)
        self.root_layer.subLayerPaths.append(self.define_layer.identifier)

        self.test_layers = list(self.stage.GetLayerStack())[:-1]
        self.test_layer_count = len(self.test_layers)

    # ----------------------------------------------------------------------
    async def test_write_prim_attr_to_layer(self):
        """Test omni.graph.nodes.WritePrimAttribute to a different layer"""

        controller = og.Controller()
        keys = og.Controller.Keys

        # Edit on least weakest layer
        with Usd.EditContext(self.stage, self.define_layer):

            def create_scope_with_test_attrs(prim_path: str):
                scope = UsdGeom.Scope.Define(self.stage, prim_path)
                scope_prim = scope.GetPrim()
                scope_prim.CreateAttribute("test_attr_0", Sdf.ValueTypeNames.Bool).Set(False)
                scope_prim.CreateAttribute("test_attr_1", Sdf.ValueTypeNames.Bool).Set(False)
                scope_prim.CreateAttribute("test_attr_2", Sdf.ValueTypeNames.Bool).Set(False)
                scope_prim.CreateAttribute("test_attr_3", Sdf.ValueTypeNames.Bool).Set(False)
                scope_prim.CreateAttribute("test_attr_array_0", Sdf.ValueTypeNames.BoolArray).Set([False])
                scope_prim.CreateAttribute("test_attr_array_1", Sdf.ValueTypeNames.BoolArray).Set([False])
                scope_prim.CreateAttribute("test_attr_array_2", Sdf.ValueTypeNames.BoolArray).Set([False])
                scope_prim.CreateAttribute("test_attr_array_3", Sdf.ValueTypeNames.BoolArray).Set([False])
                return scope_prim

            source_prims = []
            for i in range(self.test_layer_count):
                source_prims.append(create_scope_with_test_attrs(f"/Scope_{i}"))

            (graph, _, _, _) = controller.edit(
                self.TEST_GRAPH_PATH,
                {
                    keys.CREATE_NODES: [
                        ("Write0", "omni.graph.nodes.WritePrimAttribute"),
                        ("Write1", "omni.graph.nodes.WritePrimAttribute"),
                        ("Write2", "omni.graph.nodes.WritePrimAttribute"),
                        ("Write3", "omni.graph.nodes.WritePrimAttribute"),
                        ("WriteArray0", "omni.graph.nodes.WritePrimAttribute"),
                        ("WriteArray1", "omni.graph.nodes.WritePrimAttribute"),
                        ("WriteArray2", "omni.graph.nodes.WritePrimAttribute"),
                        ("WriteArray3", "omni.graph.nodes.WritePrimAttribute"),
                    ],
                    keys.SET_VALUES: [
                        ("Write0.inputs:prim", "/Scope_0"),
                        ("Write0.inputs:name", "test_attr_0"),
                        ("Write0.inputs:value", {"type": "bool", "value": True}),
                        ("Write0.inputs:layerIdentifier", "<Session Layer>"),  # Session Layer
                        ("Write1.inputs:prim", "/Scope_1"),
                        ("Write1.inputs:name", "test_attr_1"),
                        ("Write1.inputs:value", {"type": "bool", "value": True}),
                        ("Write1.inputs:layerIdentifier", "<Root Layer>"),  # Root Layer
                        ("Write2.inputs:prim", "/Scope_2"),
                        ("Write2.inputs:name", "test_attr_2"),
                        ("Write2.inputs:value", {"type": "bool", "value": True}),
                        ("Write2.inputs:layerIdentifier", self.sub_layer_01.identifier),  # Sublayer (sub_layer_01)
                        ("Write3.inputs:prim", "/Scope_3"),
                        ("Write3.inputs:name", "test_attr_3"),
                        ("Write3.inputs:value", {"type": "bool", "value": True}),
                        ("Write3.inputs:layerIdentifier", ""),  # Current Layer (sub_layer_02)
                        ("WriteArray0.inputs:prim", "/Scope_0"),
                        ("WriteArray0.inputs:name", "test_attr_array_0"),
                        ("WriteArray0.inputs:value", {"type": "bool[]", "value": [True]}),
                        ("WriteArray0.inputs:layerIdentifier", "<Session Layer>"),  # Session Layer
                        ("WriteArray1.inputs:prim", "/Scope_1"),
                        ("WriteArray1.inputs:name", "test_attr_array_1"),
                        ("WriteArray1.inputs:value", {"type": "bool[]", "value": [True]}),
                        ("WriteArray1.inputs:layerIdentifier", "<Root Layer>"),  # Root Layer
                        ("WriteArray2.inputs:prim", "/Scope_2"),
                        ("WriteArray2.inputs:name", "test_attr_array_2"),
                        ("WriteArray2.inputs:value", {"type": "bool[]", "value": [True]}),
                        ("WriteArray2.inputs:layerIdentifier", self.sub_layer_01.identifier),  # Sublayer (sub_layer_01)
                        ("WriteArray3.inputs:prim", "/Scope_3"),
                        ("WriteArray3.inputs:name", "test_attr_array_3"),
                        ("WriteArray3.inputs:value", {"type": "bool[]", "value": [True]}),
                        ("WriteArray3.inputs:layerIdentifier", ""),  # Current Layer (sub_layer_02)
                    ],
                },
            )

        # Compute and compare on next highest layer
        with Usd.EditContext(self.stage, self.sub_layer_02):

            await controller.evaluate(graph)

            for layer_idx, layer in enumerate(self.test_layers):
                for prim_idx in range(self.test_layer_count):
                    prim_spec = layer.GetPrimAtPath(f"/Scope_{prim_idx}")
                    if layer_idx == prim_idx:
                        self.assertTrue(prim_spec)
                        for attr_idx in range(self.test_layer_count):
                            attr_spec = layer.GetAttributeAtPath(f"/Scope_{prim_idx}.test_attr_{attr_idx}")
                            attr_array_spec = layer.GetAttributeAtPath(f"/Scope_{prim_idx}.test_attr_array_{attr_idx}")
                            if layer_idx == attr_idx:
                                self.assertTrue(attr_spec)
                                self.assertTrue(attr_spec.default)
                                self.assertTrue(attr_array_spec)
                                self.assertTrue(attr_array_spec.default == [True])
                            else:
                                self.assertFalse(attr_spec)
                                self.assertFalse(attr_array_spec)
                    else:
                        self.assertFalse(prim_spec)

    # ----------------------------------------------------------------------
    async def test_write_prim_attr_to_layer_with_instances(self):
        """Test omni.graph.nodes.WritePrimAttribute to a different layer with instances"""

        controller = og.Controller()
        keys = og.Controller.Keys

        # Edit on least weakest layer
        with Usd.EditContext(self.stage, self.define_layer):

            def create_scope_with_test_attrs(prim_path: str, layer_id: str):
                scope = UsdGeom.Scope.Define(self.stage, prim_path)
                scope_prim = scope.GetPrim()
                scope_prim.CreateAttribute("test_attr", Sdf.ValueTypeNames.Bool).Set(False)
                scope_prim.CreateAttribute("test_attr_array", Sdf.ValueTypeNames.BoolArray).Set([False])
                OmniGraphSchemaTools.applyOmniGraphAPI(self.stage, prim_path, self.TEST_GRAPH_PATH)
                scope_prim.CreateAttribute("graph:variable:layerIdentifier", Sdf.ValueTypeNames.Token).Set(layer_id)
                return scope_prim

            (graph, _, _, _) = controller.edit(
                self.TEST_GRAPH_PATH,
                {
                    keys.CREATE_NODES: [
                        ("ReadVariable", "omni.graph.core.ReadVariable"),
                        ("Write", "omni.graph.nodes.WritePrimAttribute"),
                        ("WriteArray", "omni.graph.nodes.WritePrimAttribute"),
                    ],
                    keys.CONNECT: [
                        ("ReadVariable.outputs:value", "Write.inputs:layerIdentifier"),
                        ("ReadVariable.outputs:value", "WriteArray.inputs:layerIdentifier"),
                    ],
                    keys.CREATE_VARIABLES: [
                        ("layerIdentifier", og.Type(og.BaseDataType.TOKEN)),
                    ],
                    keys.SET_VALUES: [
                        ("ReadVariable.inputs:variableName", "layerIdentifier"),
                        ("Write.inputs:prim", "_OMNI_GRAPH_TARGET"),
                        ("Write.inputs:name", "test_attr"),
                        ("Write.inputs:value", {"type": "bool", "value": True}),
                        # layerIdentifier needs to have a spec or it won't properly resolve
                        ("Write.inputs:layerIdentifier", ""),
                        ("WriteArray.inputs:prim", "_OMNI_GRAPH_TARGET"),
                        ("WriteArray.inputs:name", "test_attr_array"),
                        ("WriteArray.inputs:value", {"type": "bool[]", "value": [True]}),
                        ("WriteArray.inputs:layerIdentifier", ""),
                    ],
                },
            )

            create_scope_with_test_attrs("/Scope_0", "<Session Layer>")
            create_scope_with_test_attrs("/Scope_1", "<Root Layer>")
            create_scope_with_test_attrs("/Scope_2", self.sub_layer_01.identifier)
            create_scope_with_test_attrs("/Scope_3", "")

        # Compute and compare on next highest layer
        with Usd.EditContext(self.stage, self.sub_layer_02):

            await controller.evaluate(graph)

            for layer_idx, layer in enumerate(self.test_layers):
                for prim_idx in range(self.test_layer_count):
                    prim_spec = layer.GetPrimAtPath(f"/Scope_{prim_idx}")
                    if layer_idx == prim_idx:
                        self.assertTrue(prim_spec)
                        attr_spec = layer.GetAttributeAtPath(f"/Scope_{prim_idx}.test_attr")
                        attr_array_spec = layer.GetAttributeAtPath(f"/Scope_{prim_idx}.test_attr_array")
                        self.assertTrue(attr_spec)
                        self.assertTrue(attr_spec.default)
                        self.assertTrue(attr_array_spec)
                        self.assertTrue(attr_array_spec.default == [True])
                    else:
                        self.assertFalse(prim_spec)

    # ----------------------------------------------------------------------
    async def test_write_prim_to_layer(self):
        """Test omni.graph.nodes.WritePrim to a different layer"""

        controller = og.Controller()
        keys = og.Controller.Keys

        # Edit on least weakest layer
        with Usd.EditContext(self.stage, self.define_layer):

            def create_scope_with_test_attrs(prim_path: str):
                scope = UsdGeom.Scope.Define(self.stage, prim_path)
                scope_prim = scope.GetPrim()
                scope_prim.CreateAttribute("test_attr_0", Sdf.ValueTypeNames.Bool).Set(False)
                scope_prim.CreateAttribute("test_attr_1", Sdf.ValueTypeNames.Bool).Set(False)
                scope_prim.CreateAttribute("test_attr_2", Sdf.ValueTypeNames.Bool).Set(False)
                scope_prim.CreateAttribute("test_attr_3", Sdf.ValueTypeNames.Bool).Set(False)
                return scope_prim

            source_prims = []
            for i in range(self.test_layer_count):
                source_prims.append(create_scope_with_test_attrs(f"/Scope_{i}"))

            # Create nodes
            (graph, nodes, _, _) = controller.edit(
                self.TEST_GRAPH_PATH,
                {
                    keys.CREATE_NODES: [
                        ("Write0", "omni.graph.nodes.WritePrim"),
                        ("Write1", "omni.graph.nodes.WritePrim"),
                        ("Write2", "omni.graph.nodes.WritePrim"),
                        ("Write3", "omni.graph.nodes.WritePrim"),
                        ("ConstBool", "omni.graph.nodes.ConstantBool"),
                    ],
                    keys.SET_VALUES: [
                        ("Write0.inputs:prim", "/Scope_0"),
                        ("Write0.inputs:layerIdentifier", "<Session Layer>"),  # Session Layer
                        ("Write1.inputs:prim", "/Scope_1"),
                        ("Write1.inputs:layerIdentifier", "<Root Layer>"),  # Root Layer
                        ("Write2.inputs:prim", "/Scope_2"),
                        ("Write2.inputs:layerIdentifier", self.sub_layer_01.identifier),  # Sublayer (sub_layer_01)
                        ("Write3.inputs:prim", "/Scope_3"),
                        ("Write3.inputs:layerIdentifier", ""),  # Current Layer (sub_layer_02)
                        ("ConstBool.inputs:value", True),
                    ],
                },
            )

            write_nodes = nodes[:-1]
            const_node = nodes[-1]

            # Evaluate to create inputs
            await controller.evaluate(graph)

            # Connect constant to attributes to write
            out_attr = controller.attribute("inputs:value", const_node)
            for node_idx, node in enumerate(write_nodes):
                attr = controller.attribute(f"inputs:test_attr_{node_idx}", node)
                og.Controller.connect(out_attr, attr)

        # Compute and compare on next highest layer
        with Usd.EditContext(self.stage, self.sub_layer_02):

            await controller.evaluate(graph)

            for layer_idx, layer in enumerate(self.test_layers):
                for prim_idx in range(self.test_layer_count):
                    prim_spec = layer.GetPrimAtPath(f"/Scope_{prim_idx}")
                    if layer_idx == prim_idx:
                        self.assertTrue(prim_spec)
                        for attr_idx in range(self.test_layer_count):
                            attr_spec = layer.GetAttributeAtPath(f"/Scope_{prim_idx}.test_attr_{attr_idx}")
                            if layer_idx == attr_idx:
                                self.assertTrue(attr_spec)
                                self.assertTrue(attr_spec.default)
                            else:
                                self.assertFalse(attr_spec)
                    else:
                        self.assertFalse(prim_spec)

    # ----------------------------------------------------------------------
    async def test_write_prim_rel_to_layer(self):
        """Test omni.graph.nodes.WritePrimRelationship to a different layer"""

        controller = og.Controller()
        keys = og.Controller.Keys

        # Edit on least weakest layer
        with Usd.EditContext(self.stage, self.define_layer):

            def create_scope_with_test_attrs(prim_path: str):
                scope = UsdGeom.Scope.Define(self.stage, prim_path)
                scope_prim = scope.GetPrim()
                scope_prim.CreateRelationship("test_rel_0")
                scope_prim.CreateRelationship("test_rel_1")
                scope_prim.CreateRelationship("test_rel_2")
                scope_prim.CreateRelationship("test_rel_3")
                return scope_prim

            source_prims = []
            for i in range(self.test_layer_count):
                source_prims.append(create_scope_with_test_attrs(f"/Scope_{i}"))

            (graph, _, _, _) = controller.edit(
                self.TEST_GRAPH_PATH,
                {
                    keys.CREATE_NODES: [
                        ("Write0", "omni.graph.nodes.WritePrimRelationship"),
                        ("Write1", "omni.graph.nodes.WritePrimRelationship"),
                        ("Write2", "omni.graph.nodes.WritePrimRelationship"),
                        ("Write3", "omni.graph.nodes.WritePrimRelationship"),
                    ],
                    keys.CREATE_PRIMS: [("/Cube", "Cube")],
                    keys.SET_VALUES: [
                        ("Write0.inputs:prim", "/Scope_0"),
                        ("Write0.inputs:name", "test_rel_0"),
                        ("Write0.inputs:value", "/Cube"),
                        ("Write0.inputs:layerIdentifier", "<Session Layer>"),  # Session Layer
                        ("Write1.inputs:prim", "/Scope_1"),
                        ("Write1.inputs:name", "test_rel_1"),
                        ("Write1.inputs:value", "/Cube"),
                        ("Write1.inputs:layerIdentifier", "<Root Layer>"),  # Root Layer
                        ("Write2.inputs:prim", "/Scope_2"),
                        ("Write2.inputs:name", "test_rel_2"),
                        ("Write2.inputs:value", "/Cube"),
                        ("Write2.inputs:layerIdentifier", self.sub_layer_01.identifier),  # Sublayer (sub_layer_01)
                        ("Write3.inputs:prim", "/Scope_3"),
                        ("Write3.inputs:name", "test_rel_3"),
                        ("Write3.inputs:value", "/Cube"),
                        ("Write3.inputs:layerIdentifier", ""),  # Current Layer (sub_layer_02)
                    ],
                },
            )

        # Compute and compare on next highest layer
        with Usd.EditContext(self.stage, self.sub_layer_02):

            await controller.evaluate(graph)

            for layer_idx, layer in enumerate(self.test_layers):
                for prim_idx in range(self.test_layer_count):
                    prim_spec = layer.GetPrimAtPath(f"/Scope_{prim_idx}")
                    if layer_idx == prim_idx:
                        self.assertTrue(prim_spec)
                        for rel_idx in range(self.test_layer_count):
                            rel_spec = layer.GetRelationshipAtPath(f"/Scope_{prim_idx}.test_rel_{rel_idx}")
                            rel_targets = list(rel_spec.targetPathList.GetAddedOrExplicitItems()) if rel_spec else []
                            if layer_idx == rel_idx:
                                self.assertTrue(rel_spec)
                                self.assertTrue(len(rel_targets) > 0 and rel_targets[0] == Sdf.Path("/Cube"))
                            else:
                                self.assertFalse(rel_spec)
                    else:
                        self.assertFalse(prim_spec)

    # ----------------------------------------------------------------------
    async def test_write_prim_material_to_layer(self):
        """Test omni.graph.nodes.WritePrimMaterial to a different layer"""

        controller = og.Controller()
        keys = og.Controller.Keys

        # Edit on least weakest layer
        with Usd.EditContext(self.stage, self.define_layer):

            (graph, _, _, _) = controller.edit(
                self.TEST_GRAPH_PATH,
                {
                    keys.CREATE_NODES: [
                        ("Write0", "omni.graph.nodes.WritePrimMaterial"),
                        ("Write1", "omni.graph.nodes.WritePrimMaterial"),
                        ("Write2", "omni.graph.nodes.WritePrimMaterial"),
                        ("Write3", "omni.graph.nodes.WritePrimMaterial"),
                    ],
                    keys.CREATE_PRIMS: [
                        ("/Cube_0", "Cube"),
                        ("/Cube_1", "Cube"),
                        ("/Cube_2", "Cube"),
                        ("/Cube_3", "Cube"),
                        ("/Material", "Material"),
                    ],
                    keys.SET_VALUES: [
                        ("Write0.inputs:prim", "/Cube_0"),
                        ("Write0.inputs:material", "/Material"),
                        ("Write0.inputs:layerIdentifier", "<Session Layer>"),  # Session Layer
                        ("Write1.inputs:prim", "/Cube_1"),
                        ("Write1.inputs:material", "/Material"),
                        ("Write1.inputs:layerIdentifier", "<Root Layer>"),  # Root Layer
                        ("Write2.inputs:prim", "/Cube_2"),
                        ("Write2.inputs:material", "/Material"),
                        ("Write2.inputs:layerIdentifier", self.sub_layer_01.identifier),  # Sublayer (sub_layer_01)
                        ("Write3.inputs:prim", "/Cube_3"),
                        ("Write3.inputs:material", "/Material"),
                        ("Write3.inputs:layerIdentifier", ""),  # Current Layer (sub_layer_02)
                    ],
                },
            )

        # Compute and compare on next highest layer
        with Usd.EditContext(self.stage, self.sub_layer_02):

            await controller.evaluate(graph)

            for layer_idx, layer in enumerate(self.test_layers):
                for prim_idx in range(self.test_layer_count):
                    prim_spec = layer.GetPrimAtPath(f"/Cube_{prim_idx}")
                    if layer_idx == prim_idx:
                        self.assertTrue(prim_spec)
                        rel_spec = layer.GetRelationshipAtPath(f"/Cube_{prim_idx}.material:binding")
                        self.assertTrue(rel_spec)
                        rel_targets = list(rel_spec.targetPathList.GetAddedOrExplicitItems()) if rel_spec else []
                        self.assertTrue(len(rel_targets) > 0 and rel_targets[0] == Sdf.Path("/Material"))
                    else:
                        self.assertFalse(prim_spec)

    # ----------------------------------------------------------------------
    async def test_set_variant_selection_to_layer(self):
        """Test omni.graph.nodes.SetVariantSelection to a different layer"""

        controller = og.Controller()
        keys = og.Controller.Keys

        # Edit on least weakest layer
        with Usd.EditContext(self.stage, self.define_layer):

            def create_scope_with_variants(prim_path: str):
                scope = UsdGeom.Scope.Define(self.stage, prim_path)
                scope_prim = scope.GetPrim()
                attr = scope_prim.CreateAttribute("test_attr", Sdf.ValueTypeNames.Bool)
                variant_set = scope_prim.GetVariantSets().AddVariantSet("TEST")
                variant_set.AddVariant("on")
                variant_set.AddVariant("off")
                variant_set.SetVariantSelection("on")
                with variant_set.GetVariantEditContext():
                    attr.Set(True)
                variant_set.SetVariantSelection("off")
                with variant_set.GetVariantEditContext():
                    attr.Set(False)
                return scope_prim

            source_prims = []
            for i in range(self.test_layer_count):
                source_prims.append(create_scope_with_variants(f"/Scope_{i}"))

            (graph, write_nodes, _, _) = controller.edit(
                self.TEST_GRAPH_PATH,
                {
                    keys.CREATE_NODES: [
                        ("Write0", "omni.graph.nodes.SetVariantSelection"),
                        ("Write1", "omni.graph.nodes.SetVariantSelection"),
                        ("Write2", "omni.graph.nodes.SetVariantSelection"),
                        ("Write3", "omni.graph.nodes.SetVariantSelection"),
                    ],
                    keys.SET_VALUES: [
                        ("Write0.inputs:prim", "/Scope_0"),
                        ("Write0.inputs:variantSetName", "TEST"),
                        ("Write0.inputs:variantName", "on"),
                        ("Write0.inputs:setVariant", True),
                        ("Write0.inputs:layerIdentifier", "<Session Layer>"),  # Session Layer
                        ("Write1.inputs:prim", "/Scope_1"),
                        ("Write1.inputs:variantSetName", "TEST"),
                        ("Write1.inputs:variantName", "on"),
                        ("Write1.inputs:setVariant", True),
                        ("Write1.inputs:layerIdentifier", "<Root Layer>"),  # Root Layer
                        ("Write2.inputs:prim", "/Scope_2"),
                        ("Write2.inputs:variantSetName", "TEST"),
                        ("Write2.inputs:variantName", "on"),
                        ("Write2.inputs:setVariant", True),
                        ("Write2.inputs:layerIdentifier", self.sub_layer_01.identifier),  # Sublayer (sub_layer_01)
                        ("Write3.inputs:prim", "/Scope_3"),
                        ("Write3.inputs:variantSetName", "TEST"),
                        ("Write3.inputs:variantName", "on"),
                        ("Write3.inputs:setVariant", True),
                        ("Write3.inputs:layerIdentifier", ""),  # Current Layer (sub_layer_02)
                    ],
                },
            )

        # Compute and compare on next highest layer
        with Usd.EditContext(self.stage, self.sub_layer_02):

            await controller.evaluate(graph)

            # Also toggle set variant to verify that values are written on correct layers
            for node in write_nodes:
                og.Controller.set(("inputs:setVariant", node), False)

            await controller.evaluate(graph)

            for layer_idx, layer in enumerate(self.test_layers):
                for prim_idx in range(self.test_layer_count):
                    prim_spec = layer.GetPrimAtPath(f"/Scope_{prim_idx}")
                    if layer_idx == prim_idx:
                        self.assertTrue(prim_spec)
                        self.assertTrue(prim_spec.variantSelections.get("TEST", "off") == "on")
                        attr_spec = layer.GetAttributeAtPath(f"/Scope_{prim_idx}.test_attr")
                        self.assertTrue(attr_spec)
                        self.assertTrue(attr_spec.default)

                    else:
                        self.assertFalse(prim_spec)

    # ----------------------------------------------------------------------
    async def test_clear_variant_selection_to_layer(self):
        """Test omni.graph.nodes.ClearVariantSelection in a different layer"""

        controller = og.Controller()
        keys = og.Controller.Keys

        # Edit on least weakest layer
        with Usd.EditContext(self.stage, self.define_layer):

            def create_scope_with_variants(prim_path: str):
                scope = UsdGeom.Scope.Define(self.stage, prim_path)
                scope_prim = scope.GetPrim()
                attr = scope_prim.CreateAttribute("test_attr", Sdf.ValueTypeNames.Bool)
                variant_set = scope_prim.GetVariantSets().AddVariantSet("TEST")
                variant_set.AddVariant("on")
                variant_set.AddVariant("off")
                variant_set.SetVariantSelection("on")
                with variant_set.GetVariantEditContext():
                    attr.Set(True)
                variant_set.SetVariantSelection("off")
                with variant_set.GetVariantEditContext():
                    attr.Set(False)
                return scope_prim

            source_prims = []
            for i in range(self.test_layer_count):
                source_prims.append(create_scope_with_variants(f"/Scope_{i}"))

            (graph, _, _, _) = controller.edit(
                self.TEST_GRAPH_PATH,
                {
                    keys.CREATE_NODES: [
                        ("Write0", "omni.graph.nodes.ClearVariantSelection"),
                        ("Write1", "omni.graph.nodes.ClearVariantSelection"),
                        ("Write2", "omni.graph.nodes.ClearVariantSelection"),
                        ("Write3", "omni.graph.nodes.ClearVariantSelection"),
                    ],
                    keys.SET_VALUES: [
                        ("Write0.inputs:prim", "/Scope_0"),
                        ("Write0.inputs:variantSetName", "TEST"),
                        ("Write0.inputs:setVariant", True),
                        ("Write0.inputs:layerIdentifier", "<Session Layer>"),  # Session Layer
                        ("Write1.inputs:prim", "/Scope_1"),
                        ("Write1.inputs:variantSetName", "TEST"),
                        ("Write1.inputs:setVariant", True),
                        ("Write1.inputs:layerIdentifier", "<Root Layer>"),  # Root Layer
                        ("Write2.inputs:prim", "/Scope_2"),
                        ("Write2.inputs:variantSetName", "TEST"),
                        ("Write2.inputs:setVariant", True),
                        ("Write2.inputs:layerIdentifier", self.sub_layer_01.identifier),  # Sublayer (sub_layer_01)
                        ("Write3.inputs:prim", "/Scope_3"),
                        ("Write3.inputs:variantSetName", "TEST"),
                        ("Write3.inputs:setVariant", True),
                        ("Write3.inputs:layerIdentifier", ""),  # Current Layer (sub_layer_02)
                    ],
                },
            )

        # Compute and compare on next highest layer
        with Usd.EditContext(self.stage, self.sub_layer_02):

            await controller.evaluate(graph)

            for layer_idx, layer in enumerate(self.test_layers):
                for prim_idx in range(self.test_layer_count):
                    prim_spec = layer.GetPrimAtPath(f"/Scope_{prim_idx}")
                    if layer_idx == prim_idx:
                        self.assertTrue(prim_spec)
                        self.assertTrue(prim_spec.variantSelections.get("TEST", "off") == "")
                    else:
                        self.assertFalse(prim_spec)

    # ----------------------------------------------------------------------
    async def test_blend_variants_to_layer(self):
        """Test omni.graph.nodes.BlendVariants in a different layer"""

        controller = og.Controller()
        keys = og.Controller.Keys

        # Edit on least weakest layer
        with Usd.EditContext(self.stage, self.define_layer):

            def create_scope_with_variants(prim_path: str):
                scope = UsdGeom.Scope.Define(self.stage, prim_path)
                scope_prim = scope.GetPrim()
                attr = scope_prim.CreateAttribute("test_attr", Sdf.ValueTypeNames.Double)
                variant_set = scope_prim.GetVariantSets().AddVariantSet("TEST")
                variant_set.AddVariant("on")
                variant_set.AddVariant("off")
                variant_set.SetVariantSelection("on")
                with variant_set.GetVariantEditContext():
                    attr.Set(1.0)
                variant_set.SetVariantSelection("off")
                with variant_set.GetVariantEditContext():
                    attr.Set(0.0)
                return scope_prim

            source_prims = []
            for i in range(self.test_layer_count):
                source_prims.append(create_scope_with_variants(f"/Scope_{i}"))

            (graph, _, _, _) = controller.edit(
                self.TEST_GRAPH_PATH,
                {
                    keys.CREATE_NODES: [
                        ("Write0", "omni.graph.nodes.BlendVariants"),
                        ("Write1", "omni.graph.nodes.BlendVariants"),
                        ("Write2", "omni.graph.nodes.BlendVariants"),
                        ("Write3", "omni.graph.nodes.BlendVariants"),
                    ],
                    keys.SET_VALUES: [
                        ("Write0.inputs:prim", "/Scope_0"),
                        ("Write0.inputs:variantSetName", "TEST"),
                        ("Write0.inputs:variantNameA", "off"),
                        ("Write0.inputs:variantNameB", "on"),
                        ("Write0.inputs:blend", 0.5),
                        ("Write0.inputs:layerIdentifier", "<Session Layer>"),  # Session Layer
                        ("Write1.inputs:prim", "/Scope_1"),
                        ("Write1.inputs:variantSetName", "TEST"),
                        ("Write1.inputs:variantNameA", "off"),
                        ("Write1.inputs:variantNameB", "on"),
                        ("Write1.inputs:blend", 0.5),
                        ("Write1.inputs:layerIdentifier", "<Root Layer>"),  # Root Layer
                        ("Write2.inputs:prim", "/Scope_2"),
                        ("Write2.inputs:variantSetName", "TEST"),
                        ("Write2.inputs:variantNameA", "off"),
                        ("Write2.inputs:variantNameB", "on"),
                        ("Write2.inputs:blend", 0.5),
                        ("Write2.inputs:layerIdentifier", self.sub_layer_01.identifier),  # Sublayer (sub_layer_01)
                        ("Write3.inputs:prim", "/Scope_3"),
                        ("Write3.inputs:variantSetName", "TEST"),
                        ("Write3.inputs:variantNameA", "off"),
                        ("Write3.inputs:variantNameB", "on"),
                        ("Write3.inputs:blend", 0.5),
                        ("Write3.inputs:layerIdentifier", ""),  # Current Layer (sub_layer_02)
                    ],
                },
            )

        # Compute and compare on next highest layer
        with Usd.EditContext(self.stage, self.sub_layer_02):

            await controller.evaluate(graph)

            # Test during the middle of a blend
            for layer_idx, layer in enumerate(self.test_layers):
                for prim_idx in range(self.test_layer_count):
                    prim_spec = layer.GetPrimAtPath(f"/Scope_{prim_idx}")
                    if layer_idx == prim_idx:
                        attr_spec = layer.GetAttributeAtPath(f"/Scope_{prim_idx}.test_attr")
                        self.assertTrue(attr_spec)
                        self.assertTrue(attr_spec.default == 0.5)
                    else:
                        self.assertFalse(prim_spec)
