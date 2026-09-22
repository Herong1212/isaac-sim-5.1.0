from pathlib import Path
import omni.kit.test

import os
import omni.kit.undo
import omni.kit.commands
import omni.timeline
import omni.usd
import tempfile
from omni.kit.usd.layers import LayerUtils, get_layers, LayerEditMode
from pxr import Gf, Kind, Sdf, Usd, UsdGeom, UsdShade, UsdUtils

CURRENT_PATH = Path(__file__).parent
DATA_PATH = CURRENT_PATH.joinpath("../../../../../data")

FILE_PATH_OmniPBR = str(DATA_PATH.joinpath("material_OmniPBR.usda")).replace("\\", "/")
FILE_PATH_OmniGlass = str(DATA_PATH.joinpath("material_OmniGlass.usda")).replace("\\", "/")


def get_stage_default_prim_path(stage):
    if stage.HasDefaultPrim():
        return stage.GetDefaultPrim().GetPath()
    else:
        return Sdf.Path.absoluteRootPath


class TestUsdCommands(omni.kit.test.AsyncTestCase):

    # Before running each test
    async def setUp(self):
        self.usd_context = omni.usd.get_context()
        await omni.usd.get_context().new_stage_async()

    async def tearDown(self):
        if omni.usd.get_context().get_stage():
            await omni.usd.get_context().close_stage_async()

    async def test_create_layer_with_metadata(self):
        """Test for OM-73060."""
        usd_context = omni.usd.get_context()
        stage = usd_context.get_stage()
        default_prim_path = get_stage_default_prim_path(stage)
        root_layer = stage.GetRootLayer()
        LayerUtils.set_custom_layer_name(root_layer, "custom_name")
        metadata = {"upAxis": "Z", "metersPerUnit": 0.005, "timeCodesPerSecond": 32}
        if stage.HasDefaultPrim():
            metadata["defaultPrim"] = stage.GetDefaultPrim().GetName()
        for key, val in metadata.items():
            stage.SetMetadata(key, val)

        result, new_layer_identifier = omni.kit.commands.execute(
            "CreateSublayer",
            layer_identifier=root_layer.identifier,
            sublayer_position=0,
            new_layer_path="",
            transfer_root_content=False,
            create_or_insert=True,
        )

        self.assertTrue(result and new_layer_identifier)
        layer = Sdf.Find(new_layer_identifier)
        self.assertTrue(layer)
        self.assertNotEqual(LayerUtils.get_custom_layer_name(layer), "custom_name")
        new_layer_stage = Usd.Stage.Open(layer)
        self.assertEqual(UsdGeom.GetStageUpAxis(stage), UsdGeom.GetStageUpAxis(new_layer_stage))
        self.assertTrue(
            Gf.IsClose(
                UsdGeom.GetStageMetersPerUnit(stage),
                UsdGeom.GetStageMetersPerUnit(new_layer_stage),
                1e-6
            )
        )
        self.assertEqual(stage.GetTimeCodesPerSecond(), new_layer_stage.GetTimeCodesPerSecond())

    async def test_create_layer(self):
        usd_context = omni.usd.get_context()
        stage = usd_context.get_stage()
        default_prim_path = get_stage_default_prim_path(stage)
        root_layer = stage.GetRootLayer()
        metadata = {"upAxis": "Z", "metersPerUnit": 0.005, "timeCodesPerSecond": 32}
        if stage.HasDefaultPrim():
            metadata["defaultPrim"] = stage.GetDefaultPrim().GetName()
        for key, val in metadata.items():
            stage.SetMetadata(key, val)

        # make a sphere in the root layer to test the transfer content feature
        with Usd.EditContext(stage, root_layer):
            omni.kit.commands.execute("CreatePrim", prim_type="Sphere")
        prim = stage.GetPrimAtPath(default_prim_path.AppendChild("Sphere"))

        def check_layers(layers_info):
            for key, desired_val in metadata.items():
                val = stage.GetMetadata(key)
                self.assertTrue(val == desired_val, "stage metadata changed")

            self.assertTrue(len(layers_info) == len(root_layer.subLayerPaths), "number of layers")
            for layer_info in layers_info:
                index, anon, transfered = layer_info
                # check assumes we only transfered content 0-1 times
                layer = Sdf.Find(root_layer.subLayerPaths[index])
                self.assertTrue(layer is not None, "layer is found")
                prim = layer.GetPrimAtPath(default_prim_path.AppendChild("Sphere"))
                if transfered:
                    self.assertTrue(prim, "prim was transferred")
                else:
                    self.assertFalse(prim, "prim wasn't transferred")

        # test one layer - anonymous - no transfer
        # position_before, anonymous, transfer_root_content
        omni.kit.commands.execute(
            "CreateSublayer",
            layer_identifier=root_layer.identifier,
            sublayer_position=0,
            new_layer_path="",
            transfer_root_content=False,
            create_or_insert=True,
        )

        check_layers([(0, True, False)])
        omni.kit.undo.undo()
        check_layers([])
        omni.kit.undo.redo()
        check_layers([(0, True, False)])
        omni.kit.undo.undo()
        check_layers([])

        # test one layer - anonymous - transfer
        omni.kit.commands.execute(
            "CreateSublayer",
            layer_identifier=root_layer.identifier,
            sublayer_position=0,
            new_layer_path="",
            transfer_root_content=True,
            create_or_insert=True,
        )
        check_layers([(0, True, True)])
        omni.kit.undo.undo()
        check_layers([])
        omni.kit.undo.redo()
        check_layers([(0, True, True)])
        omni.kit.undo.undo()
        check_layers([])

        # test multiple layers - anonymous - no transfer
        omni.kit.commands.execute(
            "CreateSublayer",
            layer_identifier=root_layer.identifier,
            sublayer_position=0,
            new_layer_path="",
            transfer_root_content=False,
            create_or_insert=True,
        )
        omni.kit.commands.execute(
            "CreateSublayer",
            layer_identifier=root_layer.identifier,
            sublayer_position=1,
            new_layer_path="",
            transfer_root_content=False,
            create_or_insert=True,
        )
        omni.kit.commands.execute(
            "CreateSublayer",
            layer_identifier=root_layer.identifier,
            sublayer_position=2,
            new_layer_path="",
            transfer_root_content=False,
            create_or_insert=True,
        )
        check_layers([(0, True, False), (1, True, False), (2, True, False)])
        omni.kit.undo.undo()
        check_layers([(0, True, False), (1, True, False)])
        omni.kit.undo.redo()
        check_layers([(0, True, False), (1, True, False), (2, True, False)])
        omni.kit.undo.undo()
        omni.kit.undo.undo()
        check_layers([(0, True, False)])
        omni.kit.undo.redo()
        check_layers([(0, True, False), (1, True, False)])
        omni.kit.undo.undo()
        omni.kit.undo.undo()
        check_layers([])
        omni.kit.undo.redo()
        check_layers([(0, True, False)])
        omni.kit.undo.undo()
        check_layers([])

    async def test_replace_sublayer(self):
        usd_context = omni.usd.get_context()
        stage = usd_context.get_stage()
        root_layer = stage.GetRootLayer()

        omni.kit.commands.execute(
            "CreateSublayer",
            layer_identifier=root_layer.identifier,
            sublayer_position=1,
            new_layer_path="",
            transfer_root_content=False,
            create_or_insert=True,
        )
        sublayer_paths = root_layer.subLayerPaths
        self.assertTrue(len(sublayer_paths) == 1)
        sublayer1 = Sdf.Layer.FindOrOpen(sublayer_paths[0])
        sublayer2 = Sdf.Layer.CreateAnonymous()
        edit_target_identifier = LayerUtils.get_edit_target(stage)
        self.assertTrue(edit_target_identifier == root_layer.identifier)

        # Replace layer and check if it's successfull and edit target does not change.
        omni.kit.commands.execute(
            "ReplaceSublayer",
            layer_identifier=root_layer.identifier,
            sublayer_position=0,
            new_layer_path=sublayer2.identifier,
        )
        edit_target_identifier = LayerUtils.get_edit_target(stage)
        self.assertTrue(edit_target_identifier == root_layer.identifier)
        sublayer_paths = root_layer.subLayerPaths
        self.assertTrue(len(sublayer_paths) == 1)
        self.assertTrue(sublayer_paths[0] == sublayer2.identifier)

        omni.kit.undo.undo()
        self.assertTrue(len(sublayer_paths) == 1)
        sublayer_paths = root_layer.subLayerPaths
        self.assertTrue(sublayer_paths[0] == sublayer1.identifier)

        omni.kit.undo.redo()
        self.assertTrue(len(sublayer_paths) == 1)
        sublayer_paths = root_layer.subLayerPaths
        self.assertTrue(sublayer_paths[0] == sublayer2.identifier)
        omni.kit.undo.undo()

        # Sets sublayer as edit target and do the replacement to see if edit target is changed or not.
        LayerUtils.set_edit_target(stage, sublayer1.identifier)
        omni.kit.commands.execute(
            "ReplaceSublayer",
            layer_identifier=root_layer.identifier,
            sublayer_position=0,
            new_layer_path=sublayer2.identifier,
        )
        edit_target_identifier = LayerUtils.get_edit_target(stage)
        self.assertTrue(edit_target_identifier == sublayer2.identifier)
        sublayer_paths = root_layer.subLayerPaths
        self.assertTrue(len(sublayer_paths) == 1)
        self.assertTrue(sublayer_paths[0] == sublayer2.identifier)
        omni.kit.undo.undo()

        edit_target_identifier = LayerUtils.get_edit_target(stage)
        self.assertTrue(edit_target_identifier == sublayer1.identifier)

        # Replace a invalid index will fail.
        omni.kit.commands.execute(
            "ReplaceSublayer",
            layer_identifier=root_layer.identifier,
            sublayer_position=100,
            new_layer_path=sublayer2.identifier,
        )
        self.assertTrue(len(sublayer_paths) == 1)
        sublayer_paths = root_layer.subLayerPaths
        self.assertEqual(sublayer_paths[0], sublayer1.identifier)

    async def test_move_nodes(self):
        # move nodes also uses merge nodes and remove nodes
        usd_context = omni.usd.get_context()
        stage = usd_context.get_stage()
        default_prim_path = get_stage_default_prim_path(stage)
        root_layer = stage.GetRootLayer()

        # create anonymous layers
        LayerUtils.create_sublayer(root_layer, 0, "")
        LayerUtils.create_sublayer(root_layer, 1, "")
        LayerUtils.create_sublayer(root_layer, 2, "")
        strong_layer = Sdf.Find(root_layer.subLayerPaths[0])
        intermediate_layer = Sdf.Find(root_layer.subLayerPaths[1])
        weak_layer = Sdf.Find(root_layer.subLayerPaths[2])

        # add some content
        # root:         stage/cone* height=0.7
        # strong:       stage/sphere* radius=0.5, stage/cone
        # intermediate: empty
        # weak:         stage/sphere radius=1.234
        with Usd.EditContext(stage, weak_layer):
            omni.kit.commands.execute("CreatePrim", prim_type="Sphere")
        prim = stage.GetPrimAtPath(default_prim_path.AppendChild("Sphere"))
        sphere = UsdGeom.Sphere(prim)
        with Usd.EditContext(stage, weak_layer):
            sphere.CreateRadiusAttr(1.234)
        with Usd.EditContext(stage, strong_layer):
            sphere.CreateRadiusAttr(0.5)
        with Usd.EditContext(stage, strong_layer):
            omni.kit.commands.execute("CreatePrim", prim_type="Cone")
        prim = stage.GetPrimAtPath(default_prim_path.AppendChild("Cone"))
        cone = UsdGeom.Cone(prim)
        with Usd.EditContext(stage, root_layer):
            cone.CreateHeightAttr(0.7)

        def everything_normal():
            sphere = UsdGeom.Sphere(stage.GetPrimAtPath(default_prim_path.AppendChild("Sphere")))
            cone = UsdGeom.Cone(stage.GetPrimAtPath(default_prim_path.AppendChild("Cone")))
            self.assertTrue(
                len(stage.GetRootLayer().subLayerPaths) == 3, "Three layers"
            )  # 3 sublayers of root plus root and session layer
            self.assertTrue(sphere.GetRadiusAttr().Get() == 0.5)
            layer_identifier = LayerUtils.get_sublayer_identifier(root_layer.identifier, 0)
            stage.MuteLayer(layer_identifier)  # mute the strongest layer
            self.assertTrue(sphere.GetRadiusAttr().Get() == 1.234)
            stage.UnmuteLayer(layer_identifier)  # unmute the strongest layer
            self.assertTrue(sphere.GetRadiusAttr().Get() == 0.5)
            self.assertTrue(cone.GetHeightAttr().Get() == 0.7)

        everything_normal()

        omni.kit.commands.execute(
            "MovePrimSpecsToLayer",
            dst_layer_identifier=strong_layer.identifier,
            src_layer_identifier=weak_layer.identifier,
            prim_spec_path=default_prim_path.AppendChild("Sphere").pathString,
            dst_stronger_than_src=True,
        )

        def check_1():
            # check that Stage/Sphere is only in the strong layer with merged value
            sphere = UsdGeom.Sphere(stage.GetPrimAtPath(default_prim_path.AppendChild("Sphere")))
            self.assertEqual(sphere.GetRadiusAttr().Get(), 0.5)
            layer_identifier = LayerUtils.get_sublayer_identifier(root_layer.identifier, 0)
            stage.MuteLayer(layer_identifier)  # mute the strongest layer
            self.assertFalse(stage.GetPrimAtPath(default_prim_path.AppendChild("Sphere")))
            stage.UnmuteLayer(layer_identifier)  # unmute the strongest layer

        check_1()
        omni.kit.undo.undo()
        everything_normal()
        omni.kit.undo.redo()
        check_1()
        omni.kit.undo.undo()
        everything_normal()

        # Strong to weak
        omni.kit.commands.execute(
            "MovePrimSpecsToLayer",
            dst_layer_identifier=weak_layer.identifier,
            src_layer_identifier=strong_layer.identifier,
            prim_spec_path=default_prim_path.AppendChild("Sphere").pathString,
            dst_stronger_than_src=False,
        )

        def check_2():
            # other layers [2, ROOT] should only contain stage. [0] should have cone and sphere
            self.assertFalse(strong_layer.GetPrimAtPath(default_prim_path.AppendChild("Sphere")))
            # Radius will be the strong one
            sphere = UsdGeom.Sphere(stage.GetPrimAtPath(default_prim_path.AppendChild("Sphere")))
            self.assertTrue(sphere.GetRadiusAttr().Get() == 0.5)

        check_2()
        omni.kit.undo.undo()
        everything_normal()
        omni.kit.undo.redo()
        check_2()
        omni.kit.undo.undo()
        everything_normal()

    async def test_flatten_layers(self):
        # Note: FlattenLayers also uses MergeLayers and RemoveLayer
        usd_context = omni.usd.get_context()
        stage = usd_context.get_stage()
        default_prim_path = get_stage_default_prim_path(stage)
        root_layer = stage.GetRootLayer()

        # When no layers are created, the total layers are 2 (root and session layer).
        omni.kit.commands.execute("FlattenLayers")
        self.assertTrue(len(root_layer.subLayerPaths) == 0)
        omni.kit.undo.undo()
        self.assertTrue(len(root_layer.subLayerPaths) == 0)

        path = LayerUtils.create_sublayer(root_layer, 0, "").identifier  # strong_layer
        layer = Sdf.Layer.FindOrOpen(path)
        self.assertTrue(layer, "layer is found before flatten")
        omni.kit.commands.execute("FlattenLayers")
        self.assertTrue(len(root_layer.subLayerPaths) == 0)
        omni.kit.undo.undo()
        self.assertTrue(len(root_layer.subLayerPaths) == 1)
        self.assertTrue(Sdf.Find(path), "layer is found after undo")
        LayerUtils.create_sublayer(root_layer, 1, "")  # intermediate_layer
        LayerUtils.create_sublayer(root_layer, 2, "")  # weak_layer
        self.assertTrue(len(root_layer.subLayerPaths) == 3)
        strong_layer = Sdf.Find(root_layer.subLayerPaths[0])
        intermediate_layer = Sdf.Find(root_layer.subLayerPaths[1])
        weak_layer = Sdf.Find(root_layer.subLayerPaths[2])
        self.assertTrue(strong_layer, "strong_layer")
        self.assertTrue(intermediate_layer, "intermediate_layer")
        self.assertTrue(weak_layer, "weak_layer")
        with Usd.EditContext(stage, weak_layer):
            omni.kit.commands.execute("CreatePrim", prim_type="Sphere")
        prim = stage.GetPrimAtPath(default_prim_path.AppendChild("Sphere"))
        self.assertTrue(prim, "Prim exists")
        sphere = UsdGeom.Sphere(prim)

        with Usd.EditContext(stage, intermediate_layer):
            sphere.CreateRadiusAttr(0.987)
        with Usd.EditContext(stage, strong_layer):
            sphere.CreateRadiusAttr(1.234)

        omni.kit.commands.execute("FlattenLayers")
        self.assertTrue(len(root_layer.subLayerPaths) == 0)
        prim = stage.GetPrimAtPath(default_prim_path.AppendChild("Sphere"))
        self.assertTrue(prim)
        sphere = UsdGeom.Sphere(prim)
        self.assertTrue(sphere.GetRadiusAttr().Get() == 1.234)
        omni.kit.undo.undo()
        self.assertTrue(len(root_layer.subLayerPaths) == 3)
        layer_identifier = LayerUtils.get_sublayer_identifier(root_layer.identifier, 0)
        stage.MuteLayer(layer_identifier)  # mute the strongest layer
        prim = stage.GetPrimAtPath(default_prim_path.AppendChild("Sphere"))
        self.assertTrue(prim)
        sphere = UsdGeom.Sphere(prim)
        self.assertTrue(sphere.GetRadiusAttr().Get() == 0.987)

        # OM-77653: Test for making sure flattening will not retime timesamples.
        await usd_context.new_stage_async()
        layer = Sdf.Layer.CreateAnonymous()

        layer_content = """#sdf 1.0
(

    defaultPrim = "World"
    endTimeCode = 100
    metersPerUnit = 0.01
    startTimeCode = 0
    timeCodesPerSecond = 30
    upAxis = "Y"
)

def Xform "World"
{
    def Mesh "Cube_30"
    {
        float3[] extent = [(-50, -50, -50), (50, 50, 50)]
        int[] faceVertexCounts = [4, 4, 4, 4, 4, 4]
        int[] faceVertexIndices = [0, 1, 3, 2, 0, 4, 5, 1, 1, 5, 6, 3, 2, 3, 6, 7, 0, 2, 7, 4, 4, 7, 6, 5]
        normal3f[] normals = [(0, -1, 0), (0, -1, 0), (0, -1, 0), (0, -1, 0), (0, 0, -1), (0, 0, -1), (0, 0, -1), (0, 0, -1), (1, 0, 0), (1, 0, 0), (1, 0, 0), (1, 0, 0), (0, 0, 1), (0, 0, 1), (0, 0, 1), (0, 0, 1), (-1, 0, 0), (-1, 0, 0), (-1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, 1, 0), (0, 1, 0), (0, 1, 0)] (
            interpolation = "faceVarying"
        )
        point3f[] points = [(-50, -50, -50), (50, -50, -50), (-50, -50, 50), (50, -50, 50), (-50, 50, -50), (50, 50, -50), (50, 50, 50), (-50, 50, 50)]
        float2[] primvars:st = [(1, 0), (0, 0), (0, 1), (1, 1), (1, 0), (1, 1), (0, 1), (0, 0), (1, 0), (0, 0), (0, 1), (1, 1), (1, 0), (0, 0), (0, 1), (1, 1), (1, 0), (1, 1), (0, 1), (0, 0), (1, 0), (1, 1), (0, 1), (0, 0)] (
            interpolation = "faceVarying"
        )
        uniform token subdivisionScheme = "none"
        double3 xformOp:rotateXYZ = (0, 0, 0)
        double3 xformOp:scale = (1, 1, 1)
        double3 xformOp:translate = (0, 0, 0)
        double3 xformOp:translate.timeSamples = {
            0: (0, 0, 0),
            100: (0, 100, 0),
        }
        uniform token[] xformOpOrder = ["xformOp:translate", "xformOp:rotateXYZ", "xformOp:scale"]
    }
}
"""
        layer.ImportFromString(layer_content)
        stage = usd_context.get_stage()
        stage.GetRootLayer().subLayerPaths.append(layer.identifier)
        # Adjusts layer offset also to verify if it could be scaled correctly.
        stage.GetRootLayer().subLayerOffsets[0] = Sdf.LayerOffset(0.0, 0.8)
        UsdUtils.CopyLayerMetadata(layer, stage.GetRootLayer(), True)

        omni.kit.commands.execute("FlattenLayers")

        expected_string = """#usda 1.0
(
    defaultPrim = "World"
    endTimeCode = 100
    metersPerUnit = 0.01
    startTimeCode = 0
    timeCodesPerSecond = 30
    upAxis = "Y"
)

def Xform "World"
{
    def Mesh "Cube_30"
    {
        float3[] extent = [(-50, -50, -50), (50, 50, 50)]
        int[] faceVertexCounts = [4, 4, 4, 4, 4, 4]
        int[] faceVertexIndices = [0, 1, 3, 2, 0, 4, 5, 1, 1, 5, 6, 3, 2, 3, 6, 7, 0, 2, 7, 4, 4, 7, 6, 5]
        normal3f[] normals = [(0, -1, 0), (0, -1, 0), (0, -1, 0), (0, -1, 0), (0, 0, -1), (0, 0, -1), (0, 0, -1), (0, 0, -1), (1, 0, 0), (1, 0, 0), (1, 0, 0), (1, 0, 0), (0, 0, 1), (0, 0, 1), (0, 0, 1), (0, 0, 1), (-1, 0, 0), (-1, 0, 0), (-1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, 1, 0), (0, 1, 0), (0, 1, 0)] (
            interpolation = "faceVarying"
        )
        point3f[] points = [(-50, -50, -50), (50, -50, -50), (-50, -50, 50), (50, -50, 50), (-50, 50, -50), (50, 50, -50), (50, 50, 50), (-50, 50, 50)]
        float2[] primvars:st = [(1, 0), (0, 0), (0, 1), (1, 1), (1, 0), (1, 1), (0, 1), (0, 0), (1, 0), (0, 0), (0, 1), (1, 1), (1, 0), (0, 0), (0, 1), (1, 1), (1, 0), (1, 1), (0, 1), (0, 0), (1, 0), (1, 1), (0, 1), (0, 0)] (
            interpolation = "faceVarying"
        )
        uniform token subdivisionScheme = "none"
        double3 xformOp:rotateXYZ = (0, 0, 0)
        double3 xformOp:scale = (1, 1, 1)
        double3 xformOp:translate = (0, 0, 0)
        double3 xformOp:translate.timeSamples = {
            0: (0, 0, 0),
            80: (0, 100, 0),
        }
        uniform token[] xformOpOrder = ["xformOp:translate", "xformOp:rotateXYZ", "xformOp:scale"]
    }
}"""
        self.assertEqual(stage.GetRootLayer().ExportToString().strip(), expected_string.strip())

    async def test_merge_layers(self):
        # Note: FlattenLayers also uses MergeLayers and RemoveLayer
        usd_context = omni.usd.get_context()
        stage = usd_context.get_stage()
        default_prim_path = get_stage_default_prim_path(stage)
        root_layer = stage.GetRootLayer()

        path = LayerUtils.create_sublayer(root_layer, 0, "").identifier  # strong_layer
        self.assertTrue(Sdf.Find(path), "layer is found before merge")
        LayerUtils.create_sublayer(root_layer, 1, "")  # intermediate_layer
        LayerUtils.create_sublayer(root_layer, 2, "")  # weak_layer
        self.assertTrue(len(root_layer.subLayerPaths) == 3)
        strong_layer = Sdf.Find(root_layer.subLayerPaths[0])
        intermediate_layer = Sdf.Find(root_layer.subLayerPaths[1])
        weak_layer = Sdf.Find(root_layer.subLayerPaths[2])
        self.assertTrue(strong_layer, "strong_layer")
        self.assertTrue(intermediate_layer, "intermediate_layer")
        self.assertTrue(weak_layer, "weak_layer")
        with Usd.EditContext(stage, weak_layer):
            omni.kit.commands.execute("CreatePrim", prim_type="Sphere")
        prim = stage.GetPrimAtPath(default_prim_path.AppendChild("Sphere"))
        self.assertTrue(prim, "Prim exists")
        sphere = UsdGeom.Sphere(prim)

        with Usd.EditContext(stage, intermediate_layer):
            sphere.CreateRadiusAttr(0.987)
        with Usd.EditContext(stage, strong_layer):
            sphere.CreateRadiusAttr(1.234)

        _, success = omni.kit.commands.execute(
            "MergeLayers",
            dst_parent_layer_identifier=root_layer.identifier,
            dst_layer_identifier=strong_layer.identifier,
            src_parent_layer_identifier=root_layer.identifier,
            src_layer_identifier=intermediate_layer.identifier,
            dst_stronger_than_src=True,
            src_layer_offset=Sdf.LayerOffset(float("nan"), float("nan")),
        )
        self.assertFalse(success)

        success = omni.kit.commands.execute(
            "MergeLayers",
            dst_parent_layer_identifier=root_layer.identifier,
            dst_layer_identifier=strong_layer.identifier,
            src_parent_layer_identifier=root_layer.identifier,
            src_layer_identifier=intermediate_layer.identifier,
            dst_stronger_than_src=True,
        )
        self.assertTrue(success)

        self.assertTrue(len(root_layer.subLayerPaths) == 2)
        prim = stage.GetPrimAtPath(default_prim_path.AppendChild("Sphere"))
        self.assertTrue(prim)
        sphere = UsdGeom.Sphere(prim)
        self.assertTrue(sphere.GetRadiusAttr().Get() == 1.234)
        omni.kit.undo.undo()
        self.assertTrue(len(root_layer.subLayerPaths) == 3)
        layer_identifier = strong_layer.identifier
        stage.MuteLayer(layer_identifier)  # mute the strongest layer
        prim = stage.GetPrimAtPath(default_prim_path.AppendChild("Sphere"))
        self.assertTrue(prim)
        sphere = UsdGeom.Sphere(prim)
        self.assertTrue(sphere.GetRadiusAttr().Get() == 0.987)
        stage.UnmuteLayer(layer_identifier)

        # Assumes we want to overide strong layer's radius with intermediate one.
        omni.kit.commands.execute(
            "MergeLayers",
            dst_parent_layer_identifier=root_layer.identifier,
            dst_layer_identifier=strong_layer.identifier,
            src_parent_layer_identifier=root_layer.identifier,
            src_layer_identifier=intermediate_layer.identifier,
            dst_stronger_than_src=False,
        )
        self.assertTrue(len(root_layer.subLayerPaths) == 2)
        prim = stage.GetPrimAtPath(default_prim_path.AppendChild("Sphere"))
        self.assertTrue(prim)
        sphere = UsdGeom.Sphere(prim)
        self.assertTrue(sphere.GetRadiusAttr().Get() == 0.987)
        omni.kit.undo.undo()
        prim = stage.GetPrimAtPath(default_prim_path.AppendChild("Sphere"))
        self.assertTrue(prim)
        sphere = UsdGeom.Sphere(prim)
        self.assertTrue(sphere.GetRadiusAttr().Get() == 1.234)

        layer_identifier = strong_layer.identifier
        stage.MuteLayer(layer_identifier)  # mute the strongest layer
        prim = stage.GetPrimAtPath(default_prim_path.AppendChild("Sphere"))
        self.assertTrue(prim)
        sphere = UsdGeom.Sphere(prim)
        self.assertTrue(sphere.GetRadiusAttr().Get() == 0.987)
        stage.UnmuteLayer(layer_identifier)

    async def test_remove_layer(self):
        usd_context = omni.usd.get_context()
        stage = usd_context.get_stage()
        default_prim_path = get_stage_default_prim_path(stage)
        root_layer = stage.GetRootLayer()
        LayerUtils.create_sublayer(root_layer, 0, "")
        LayerUtils.create_sublayer(root_layer, 1, "")
        LayerUtils.create_sublayer(root_layer, 2, "")
        layer = Sdf.Find(root_layer.subLayerPaths[2])
        identifier = layer.identifier

        sphere_path = default_prim_path.AppendChild("Sphere")
        with Usd.EditContext(stage, layer):
            omni.kit.commands.execute("CreatePrim", prim_type="Sphere")

        with Usd.EditContext(stage, root_layer):
            prim = stage.GetPrimAtPath(sphere_path)
            sphere = UsdGeom.Sphere(prim)
            sphere.CreateRadiusAttr(1.234)

        def check_exists():
            self.assertTrue(len(root_layer.subLayerPaths) == 3, "There are the correct number of sublayers")
            self.assertTrue(stage.GetPrimAtPath(sphere_path), "The prim exists")
            sphere = UsdGeom.Sphere(stage.GetPrimAtPath(sphere_path))
            radius = sphere.GetRadiusAttr().Get()
            self.assertTrue(radius == 1.234, "The sphere has the correct attr")
            layer = Sdf.Find(root_layer.subLayerPaths[2])
            self.assertTrue(identifier == layer.identifier, "{} should equal {}".format(identifier, layer.identifier))

        def check_does_not_exist():
            self.assertTrue(len(root_layer.subLayerPaths) == 2, "The layer was removed")
            prim = stage.GetPrimAtPath(sphere_path)
            self.assertFalse(prim.IsDefined(), "Prim is not removed")

        check_exists()
        omni.kit.commands.execute("RemoveSublayer", layer_identifier=root_layer.identifier, sublayer_position=2)
        check_does_not_exist()
        omni.kit.undo.undo()
        check_exists()

    async def test_move_layer(self):
        usd_context = omni.usd.get_context()
        stage = usd_context.get_stage()
        root_layer = stage.GetRootLayer()
        identifier1 = LayerUtils.create_sublayer(root_layer, 0, "").identifier
        identifier2 = LayerUtils.create_sublayer(root_layer, 1, "").identifier
        identifier3 = LayerUtils.create_sublayer(root_layer, 2, "").identifier

        def check_layers(layers_info):
            self.assertTrue(len(layers_info) == len(root_layer.subLayerPaths), "number of layers")
            for layer_info in layers_info:
                index, identifier = layer_info
                layer_identifier = LayerUtils.get_sublayer_identifier(root_layer.identifier, index)
                self.assertTrue(identifier == layer_identifier, "layer identifier")
                layer = Sdf.Find(layer_identifier)
                self.assertTrue(layer is not None, "layer is found")

        check_layers([(0, identifier1), (1, identifier2), (2, identifier3)])
        omni.kit.commands.execute(
            "MoveSublayer",
            from_parent_layer_identifier=root_layer.identifier,
            from_sublayer_position=2,
            to_parent_layer_identifier=root_layer.identifier,
            to_sublayer_position=0,
            remove_source=True,
        )
        check_layers([(0, identifier3), (1, identifier1), (2, identifier2)])
        omni.kit.undo.undo()
        check_layers([(0, identifier1), (1, identifier2), (2, identifier3)])
        # Move invalid layer will fail to execute
        omni.kit.commands.execute(
            "MoveSublayer",
            from_parent_layer_identifier=root_layer.identifier,
            from_sublayer_position=-100,
            to_parent_layer_identifier=root_layer.identifier,
            to_sublayer_position=0,
            remove_source=True,
        )
        check_layers([(0, identifier1), (1, identifier2), (2, identifier3)])
        # Move layer outside of layer stack will fail to execute
        omni.kit.commands.execute(
            "MoveSublayer",
            from_parent_layer_identifier=root_layer.identifier,
            from_sublayer_position=100,
            to_parent_layer_identifier=root_layer.identifier,
            to_sublayer_position=0,
            remove_source=True,
        )
        check_layers([(0, identifier1), (1, identifier2), (2, identifier3)])
        # Move layer to position that passes the end of layer stack will move this layer to the end of the stack
        omni.kit.commands.execute(
            "MoveSublayer",
            from_parent_layer_identifier=root_layer.identifier,
            from_sublayer_position=0,
            to_parent_layer_identifier=root_layer.identifier,
            to_sublayer_position=100,
            remove_source=True,
        )
        check_layers([(0, identifier2), (1, identifier3), (2, identifier1)])
        omni.kit.undo.undo()
        check_layers([(0, identifier1), (1, identifier2), (2, identifier3)])

        # Move layer to position before the last layer
        omni.kit.commands.execute(
            "MoveSublayer",
            from_parent_layer_identifier=root_layer.identifier,
            from_sublayer_position=0,
            to_parent_layer_identifier=root_layer.identifier,
            to_sublayer_position=-1,
            remove_source=True,
        )
        check_layers([(0, identifier2), (1, identifier3), (2, identifier1)])
        omni.kit.undo.undo()
        check_layers([(0, identifier1), (1, identifier2), (2, identifier3)])

    async def test_select_layer(self):
        usd_context = omni.usd.get_context()
        stage = usd_context.get_stage()
        root_layer = stage.GetRootLayer()
        identifier1 = LayerUtils.create_sublayer(root_layer, 0, "").identifier
        identifier2 = LayerUtils.create_sublayer(root_layer, 1, "").identifier
        identifier3 = LayerUtils.create_sublayer(root_layer, 2, "").identifier
        LayerUtils.set_edit_target(stage, identifier3)
        edit_target = stage.GetEditTarget()
        current_selected_layer = edit_target.GetLayer().identifier
        self.assertTrue(current_selected_layer == identifier3)  # root layer
        omni.kit.commands.execute("SetEditTarget", layer_identifier=identifier1)
        edit_target = stage.GetEditTarget()
        current_selected_layer = edit_target.GetLayer().identifier
        self.assertTrue(current_selected_layer == identifier1)
        omni.kit.undo.undo()
        edit_target = stage.GetEditTarget()
        current_selected_layer = edit_target.GetLayer().identifier
        self.assertTrue(current_selected_layer == identifier3)
        # Select invalid layer will keep the current edit target not changed.
        omni.kit.commands.execute("SetEditTarget", layer_identifier="")
        edit_target = stage.GetEditTarget()
        current_selected_layer = edit_target.GetLayer().identifier
        self.assertTrue(current_selected_layer == identifier3)
        omni.kit.undo.undo()
        omni.kit.commands.execute("SetEditTarget", layer_identifier=identifier2)
        edit_target = stage.GetEditTarget()
        current_selected_layer = edit_target.GetLayer().identifier
        self.assertTrue(current_selected_layer == identifier2)
        omni.kit.undo.undo()
        edit_target = stage.GetEditTarget()
        current_selected_layer = edit_target.GetLayer().identifier
        self.assertTrue(current_selected_layer == identifier3)

        # OM-103530: The following check will make sure that the timesample is set according to
        # layer offset of root layer.
        stage.SetEditTarget(stage.GetRootLayer())
        stage.SetTimeCodesPerSecond(30)
        for identity in [True, False]:
            # When it's to set edit target with SetEditTarget command. The timecode will be scaled according to
            # the timeCodesPerSecond of this layer based on its value in root layer.
            if identity:
                expected_timecode_value = Sdf.TimeCode(125)
            else:
                expected_timecode_value = Sdf.TimeCode(100)

            for layer_identifier in [identifier3, identifier2, stage.GetSessionLayer().identifier]:
                layer = Sdf.Find(layer_identifier)
                self.assertTrue(layer)
                temp_stage = Usd.Stage.Open(layer)
                temp_stage.SetTimeCodesPerSecond(24.0)
                temp_stage = None
                if identity:
                    stage.SetEditTarget(layer)
                else:
                    omni.kit.commands.execute("SetEditTarget", layer_identifier=layer_identifier)
                prim = stage.DefinePrim("/World")
                attr = prim.CreateAttribute("time", Sdf.ValueTypeNames.TimeCode)
                # If layer offset is identity, the value will be scaled to 125 as layer's TCPS is 24,
                # while root layer is 30. SetEditTarget command considers the layer offset in the local layer stack,
                # and keeps it to be 100.
                attr.Set(Sdf.TimeCode(100))
                time = attr.Get()
                self.assertEqual(time, expected_timecode_value)

                # Remove it to avoid shadowing later creation.
                prim.RemoveProperty("time")

    async def test_layer_lock(self):
        usd_context = omni.usd.get_context()
        stage = usd_context.get_stage()
        root_layer = stage.GetRootLayer()
        sublayer = LayerUtils.create_sublayer(root_layer, 0, "")
        omni.kit.commands.execute("LockLayer", layer_identifier=root_layer.identifier, locked=True)
        self.assertFalse(LayerUtils.get_layer_lock_status(root_layer, root_layer.identifier))

        LayerUtils.set_edit_target(stage, sublayer.identifier)
        self.assertEqual(LayerUtils.get_edit_target(stage), sublayer.identifier)
        omni.kit.commands.execute("LockLayer", layer_identifier=sublayer.identifier, locked=True)
        self.assertEqual(LayerUtils.get_edit_target(stage), root_layer.identifier)
        self.assertTrue(LayerUtils.get_layer_lock_status(root_layer, sublayer.identifier))
        omni.kit.undo.undo()
        self.assertEqual(LayerUtils.get_edit_target(stage), sublayer.identifier)
        self.assertFalse(LayerUtils.get_layer_lock_status(root_layer, sublayer.identifier))

    async def test_unmute_layer(self):
        usd_context = omni.usd.get_context()
        stage = usd_context.get_stage()
        root_layer = stage.GetRootLayer()
        layer3 = LayerUtils.create_sublayer(root_layer, 2, "")
        identifier3 = layer3.identifier
        LayerUtils.set_edit_target(stage, identifier3)
        current_selected_layer = LayerUtils.get_edit_target(stage)
        self.assertTrue(current_selected_layer == identifier3)
        # mute root layer will do nothing
        omni.kit.commands.execute("SetLayerMuteness", layer_identifier=root_layer.identifier, muted=True)
        current_selected_layer = LayerUtils.get_edit_target(stage)
        self.assertEqual(current_selected_layer, identifier3)
        # mute invalid layer will do nothing
        omni.kit.commands.execute("SetLayerMuteness", layer_identifier="", muted=True)
        current_selected_layer = LayerUtils.get_edit_target(stage)
        self.assertEqual(current_selected_layer, identifier3)
        # mute layer 2
        omni.kit.commands.execute("SetLayerMuteness", layer_identifier=identifier3, muted=True)
        self.assertTrue(stage.IsLayerMuted(identifier3))
        current_selected_layer = LayerUtils.get_edit_target(stage)
        self.assertNotEqual(current_selected_layer, identifier3)
        omni.kit.undo.undo()
        current_selected_layer = LayerUtils.get_edit_target(stage)
        self.assertEqual(current_selected_layer, identifier3)
        self.assertTrue(not stage.IsLayerMuted(identifier3))
        # mute, then unmute
        omni.kit.commands.execute("SetLayerMuteness", layer_identifier=identifier3, muted=True)
        omni.kit.commands.execute("SetLayerMuteness", layer_identifier=identifier3, muted=False)
        self.assertTrue(not stage.IsLayerMuted(identifier3))
        omni.kit.undo.undo()
        self.assertTrue(stage.IsLayerMuted(identifier3))
        omni.kit.undo.undo()
        self.assertTrue(not stage.IsLayerMuted(identifier3))

    async def test_stitch_prim_specss_command(self):
        # move nodes also uses merge nodes and remove nodes
        usd_context = omni.usd.get_context()
        stage = usd_context.get_stage()
        default_prim_path = get_stage_default_prim_path(stage)
        root_layer = stage.GetRootLayer()

        # create anonymous layers
        strong_layer = LayerUtils.create_sublayer(root_layer, 0, "")
        intermediate_layer = LayerUtils.create_sublayer(root_layer, 1, "")
        weak_layer = LayerUtils.create_sublayer(root_layer, 2, "")

        # add some content
        # root:         stage/cone* height=0.7
        # strong:       stage/sphere* radius=0.5, stage/cone
        # intermediate: empty
        # weak:         stage/sphere radius=1.234
        with Usd.EditContext(stage, weak_layer):
            omni.kit.commands.execute("CreatePrimCommand", prim_type="Sphere")
        prim = stage.GetPrimAtPath(default_prim_path.AppendChild("Sphere"))
        sphere = UsdGeom.Sphere(prim)
        with Usd.EditContext(stage, weak_layer):
            sphere.CreateRadiusAttr(1.234)
        with Usd.EditContext(stage, strong_layer):
            sphere.CreateRadiusAttr(0.5)
        with Usd.EditContext(stage, strong_layer):
            omni.kit.commands.execute("CreatePrimCommand", prim_type="Cone")
        prim = stage.GetPrimAtPath(default_prim_path.AppendChild("Cone"))
        cone = UsdGeom.Cone(prim)
        with Usd.EditContext(stage, root_layer):
            cone.CreateHeightAttr(0.7)

        def everything_normal():
            sphere = UsdGeom.Sphere(stage.GetPrimAtPath(default_prim_path.AppendChild("Sphere")))
            cone = UsdGeom.Cone(stage.GetPrimAtPath(default_prim_path.AppendChild("Cone")))
            self.assertTrue(
                len(stage.GetRootLayer().subLayerPaths) == 3, "Three layers"
            )  # 3 sublayers of root plus root and session layer
            self.assertTrue(sphere.GetRadiusAttr().Get() == 0.5)
            layer_identifier = LayerUtils.get_sublayer_identifier(root_layer.identifier, 0)
            stage.MuteLayer(layer_identifier)  # mute the strongest layer
            self.assertTrue(sphere.GetRadiusAttr().Get() == 1.234)
            stage.UnmuteLayer(layer_identifier)  # unmute the strongest layer
            self.assertTrue(sphere.GetRadiusAttr().Get() == 0.5)
            self.assertTrue(cone.GetHeightAttr().Get() == 0.7)

        everything_normal()

        omni.kit.commands.execute(
            "StitchPrimSpecsToLayer",
            prim_paths=[default_prim_path.AppendChild("Sphere").pathString],
            target_layer_identifier=strong_layer.identifier,
        )

        def check_1():
            # check that Stage/Sphere is only in the strong layer with merged value
            sphere = UsdGeom.Sphere(stage.GetPrimAtPath(default_prim_path.AppendChild("Sphere")))
            self.assertEqual(sphere.GetRadiusAttr().Get(), 0.5)

        check_1()
        omni.kit.undo.undo()
        everything_normal()
        omni.kit.undo.redo()
        check_1()
        omni.kit.undo.undo()
        everything_normal()

        # Strong to weak
        omni.kit.commands.execute(
            "StitchPrimSpecsToLayer",
            prim_paths=[default_prim_path.AppendChild("Sphere").pathString],
            target_layer_identifier=weak_layer.identifier,
        )

        check_1()
        omni.kit.undo.undo()
        everything_normal()
        omni.kit.undo.redo()
        check_1()
        omni.kit.undo.undo()
        everything_normal()

    async def test_layer_removal_with_stage_update(self):
        usd_context = omni.usd.get_context()
        stage = usd_context.get_stage()
        root_layer = stage.GetRootLayer()
        # insert a subLayer with material.usda which contains just one material prim
        omni.kit.commands.execute(
            "CreateSublayer",
            layer_identifier=root_layer.identifier,
            sublayer_position=0,
            new_layer_path=FILE_PATH_OmniPBR,
            transfer_root_content=False,
            create_or_insert=False,
        )

        await omni.kit.app.get_app().next_update_async()
        # check the material prim is defined in the stage
        material_prim = stage.GetPrimAtPath("/World/Looks/OmniPBR")
        self.assertTrue(material_prim.IsDefined())

        # remove the subLayer
        omni.kit.commands.execute("RemoveSublayer", layer_identifier=root_layer.identifier, sublayer_position=0)
        await omni.kit.app.get_app().next_update_async()
        # check the material prim is not there anymore
        material_prim = stage.GetPrimAtPath("/World/Looks/OmniPBR")
        self.assertFalse(material_prim.IsValid())
        # check the parent folder scope is removed too
        scope_prim = stage.GetPrimAtPath("/World/Looks")
        self.assertFalse(scope_prim.IsValid())

        # insert the subLayer again
        omni.kit.commands.execute(
            "CreateSublayer",
            layer_identifier=root_layer.identifier,
            sublayer_position=0,
            new_layer_path=FILE_PATH_OmniPBR,
            transfer_root_content=False,
            create_or_insert=False,
        )
        await omni.kit.app.get_app().next_update_async()
        # check both material prims are defined in the stage
        material_prim = stage.GetPrimAtPath("/World/Looks/OmniPBR")
        self.assertTrue(material_prim.IsDefined())
        # insert another subLayer
        omni.kit.commands.execute(
            "CreateSublayer",
            layer_identifier=root_layer.identifier,
            sublayer_position=1,
            new_layer_path=FILE_PATH_OmniGlass,
            transfer_root_content=False,
            create_or_insert=False,
        )
        await omni.kit.app.get_app().next_update_async()
        # check both material prims are defined in the stage
        material_prim = stage.GetPrimAtPath("/World/Looks/OmniGlass")
        self.assertTrue(material_prim.IsDefined())

        # remove the first subLayer
        omni.kit.commands.execute("RemoveSublayer", layer_identifier=root_layer.identifier, sublayer_position=0)
        await omni.kit.app.get_app().next_update_async()
        # check the material prim is not there anymore
        material_prim = stage.GetPrimAtPath("/World/Looks/OmniPBR")
        self.assertFalse(material_prim.IsValid())
        # check the second sublayer is still there
        scope_prim = stage.GetPrimAtPath("/World/Looks")
        self.assertTrue(scope_prim.IsValid())
        material_prim = stage.GetPrimAtPath("/World/Looks/OmniGlass")
        self.assertTrue(material_prim.IsDefined())

    def __get_all_property_paths(self, prim):
        paths = []
        for p in prim.GetProperties():
            paths.append(str(p.GetPath()))
        return paths

    def __get_all_prim_childrens(self, prim, hierarchy=False):
        paths = [str(prim.GetPath())]
        paths.extend(self.__get_all_property_paths(prim))
        if hierarchy:
            for child in prim.GetAllPrimChildren():
                paths.append(str(child.GetPath()))
                paths.extend(self.__get_all_property_paths(child))

        return paths

    def __get_all_stage_paths(self, stage):
        paths = []
        for prim in stage.TraverseAll():
            paths.extend(self.__get_all_prim_childrens(prim))
        return paths

    async def test_link_specs_command(self):
        layers = get_layers()
        specs_linking = layers.get_specs_linking()

        context = omni.usd.get_context()
        layers.set_edit_mode(LayerEditMode.SPECS_LINKING)

        stage = context.get_stage()
        root_layer = stage.GetRootLayer()
        layer0 = Sdf.Layer.CreateAnonymous()
        layer1 = Sdf.Layer.CreateAnonymous()
        layer2 = Sdf.Layer.CreateAnonymous()
        root_layer.subLayerPaths.append(layer0.identifier)
        root_layer.subLayerPaths.append(layer1.identifier)
        root_layer.subLayerPaths.append(layer2.identifier)
        asset_name = f"/root/test0/l1/l2/l3"
        asset_prim = stage.DefinePrim(asset_name, "Xform")
        all_spec_paths = set(self.__get_all_stage_paths(stage))
        await omni.kit.app.get_app().next_update_async()

        specs_linking.link_spec("/root/test0", layer0.identifier, hierarchy=True)
        old_links = specs_linking.get_all_spec_links()
        for path in ["/", "/root", "/root/test0", "/root/test0/l1/l2/l3"]:
            for hierarchy in [False, True]:
                for additive in [False, True]:
                    omni.kit.commands.execute(
                        "LinkSpecs",
                        spec_paths=path,
                        layer_identifiers=layer1.identifier,
                        additive=additive,
                        hierarchy=hierarchy,
                    )

                    if path.startswith("/root/test0"):
                        base_path = path
                    else:
                        base_path = "/root/test0"
                    # Make sure it's linked successfully
                    links = specs_linking.get_all_spec_links()
                    for spec_path, layers in links.items():
                        if hierarchy:
                            if spec_path.startswith(base_path):
                                if not additive:
                                    self.assertEqual(set(layers), set([layer1.identifier]))
                                else:
                                    self.assertEqual(set(layers), set([layer0.identifier, layer1.identifier]))
                            else:
                                if spec_path.startswith("/root/test0"):
                                    self.assertEqual(set(layers), set([layer0.identifier]))
                                else:
                                    self.assertEqual(set(layers), set([layer1.identifier]))
                        else:
                            sdf_path = Sdf.Path(spec_path)
                            if str(sdf_path.GetPrimPath()) == path:
                                if spec_path.startswith(base_path):
                                    if not additive:
                                        self.assertEqual(set(layers), set([layer1.identifier]))
                                    else:
                                        self.assertEqual(set(layers), set([layer0.identifier, layer1.identifier]))
                                else:
                                    if spec_path.startswith("/root/test0"):
                                        self.assertEqual(set(layers), set([layer0.identifier]))
                                    else:
                                        self.assertEqual(set(layers), set([layer1.identifier]))
                            else:
                                self.assertEqual(set(layers), set([layer0.identifier]))

                    omni.kit.undo.undo()
                    # Make sure it's returned to old states.
                    new_links = specs_linking.get_all_spec_links()
                    self.__compare_links_map(old_links, new_links)

    def __compare_links_map(self, old_links, new_links):
        for path, layers in old_links.items():
            self.assertTrue(path in new_links, f"Spec {path} is not existed in new links.")
            new_layers = new_links.get(path)
            self.assertEqual(set(layers), set(new_layers), f"Links spec {path} are different.")

    async def test_unlink_specs_command(self):
        layers = get_layers()
        specs_linking = layers.get_specs_linking()

        context = omni.usd.get_context()
        layers.set_edit_mode(LayerEditMode.SPECS_LINKING)

        stage = context.get_stage()
        root_layer = stage.GetRootLayer()
        layer0 = Sdf.Layer.CreateAnonymous()
        layer1 = Sdf.Layer.CreateAnonymous()
        layer2 = Sdf.Layer.CreateAnonymous()
        root_layer.subLayerPaths.append(layer0.identifier)
        root_layer.subLayerPaths.append(layer1.identifier)
        root_layer.subLayerPaths.append(layer2.identifier)
        asset_name = f"/root/test0/l1/l2/l3"
        asset_prim = stage.DefinePrim(asset_name, "Xform")
        all_spec_paths = set(self.__get_all_stage_paths(stage))
        await omni.kit.app.get_app().next_update_async()

        for layer_identifier in [layer0.identifier, layer1.identifier]:
            specs_linking.link_spec("/root/test0", layer_identifier, hierarchy=True)
        old_links = specs_linking.get_all_spec_links()
        for path in ["/", "/root", "/root/test0", "/root/test0/l1/l2/l3"]:
            for hierarchy in [False, True]:
                omni.kit.commands.execute(
                    "UnlinkSpecs", spec_paths=path, layer_identifiers=layer1.identifier, hierarchy=hierarchy
                )

                if path.startswith("/root/test0"):
                    base_path = path
                else:
                    base_path = "/root/test0"
                # Make sure it's unlinked successfully
                links = specs_linking.get_all_spec_links()
                for spec_path, layers in links.items():
                    if hierarchy:
                        if spec_path.startswith(base_path):
                            self.assertEqual(set(layers), set([layer0.identifier]))
                        else:
                            self.assertEqual(set(layers), set([layer0.identifier, layer1.identifier]))
                    else:
                        sdf_path = Sdf.Path(spec_path)
                        if str(sdf_path.GetPrimPath()) == path and spec_path.startswith(base_path):
                            self.assertEqual(set(layers), set([layer0.identifier]))
                        else:
                            self.assertEqual(set(layers), set([layer0.identifier, layer1.identifier]))

                omni.kit.undo.undo()
                # Make sure it's returned to old states.
                new_links = specs_linking.get_all_spec_links()
                self.__compare_links_map(old_links, new_links)

    async def test_lock_specs_command(self):
        layers = get_layers()
        specs_locking = layers.get_specs_locking()
        context = omni.usd.get_context()
        stage = context.get_stage()
        root_layer = stage.GetRootLayer()
        layer0 = Sdf.Layer.CreateAnonymous()
        layer1 = Sdf.Layer.CreateAnonymous()
        layer2 = Sdf.Layer.CreateAnonymous()
        root_layer.subLayerPaths.append(layer0.identifier)
        root_layer.subLayerPaths.append(layer1.identifier)
        root_layer.subLayerPaths.append(layer2.identifier)
        asset_name = f"/root/test0/l1/l2/l3"
        asset_prim = stage.DefinePrim(asset_name, "Xform")
        await omni.kit.app.get_app().next_update_async()

        specs_locking.lock_spec("/root", hierarchy=False)
        old_locks = specs_locking.get_all_locked_specs()
        for path in ["/", "/root", "/root/test0", "/root/test0/l1/l2/l3"]:
            for hierarchy in [False, True]:
                omni.kit.commands.execute("LockSpecs", spec_paths=path, hierarchy=hierarchy)

                omni.kit.undo.undo()

                # Make sure it's returned to old states.
                new_locks = specs_locking.get_all_locked_specs()
                self.assertEqual(set(old_locks), set(new_locks))

        # Locks specs that don't exist.
        specs_locking.lock_spec("/__not_exist__", hierarchy=True)
        self.assertFalse(specs_locking.is_spec_locked("/__not_exist__"))

        # Locks all to persist their states.
        specs_locking.lock_spec("/", hierarchy=True)
        old_locks = specs_locking.get_all_locked_specs()
        with tempfile.TemporaryDirectory() as temp_dir:
            usd_file = os.path.join(temp_dir, "test.usd")
            await context.save_as_stage_async(usd_file)
            await context.close_stage_async()

            # Re-open the usd file again to check if lock status persists.
            await context.open_stage_async(usd_file)

            stage = context.get_stage()
            self.assertFalse(specs_locking.is_spec_locked("/"), "/")
            for path in ["/root", "/root/test0", "/root/test0/l1/l2/l3"]:
                self.assertTrue(specs_locking.is_spec_locked(path), path)
                prim = stage.GetPrimAtPath(path)

                for p in prim.GetProperties():
                    self.assertTrue(specs_locking.is_spec_locked(p.GetPath()))

            old_locks = specs_locking.get_all_locked_specs()
            # Unlock a prim and its properties and save to see if it persists still.
            prims_to_filter = ["/root", "/root/test0/l1/l2/l3"]
            for path in prims_to_filter:
                specs_locking.unlock_spec(path, hierarchy=False)
            old_locks = specs_locking.get_all_locked_specs()
            self.assertTrue(len(old_locks) > 0)
            await context.save_stage_async()
            await context.close_stage_async()

            # Re-open the usd file again
            await context.open_stage_async(usd_file)
            stage = context.get_stage()
            self.assertFalse(specs_locking.is_spec_locked("/"), "/")
            for path in ["/root", "/root/test0", "/root/test0/l1/l2/l3"]:
                locked = specs_locking.is_spec_locked(path)
                self.assertEqual(locked, path not in prims_to_filter, path)

                prim = stage.GetPrimAtPath(path)
                for p in prim.GetProperties():
                    path = p.GetPath()
                    locked = specs_locking.is_spec_locked(path)
                    self.assertEqual(locked, path.GetPrimPath() not in prims_to_filter, path)

            # Removes prim will remove its lock record
            stage.RemovePrim("/root/test0")
            old_locks = specs_locking.get_all_locked_specs()
            self.assertTrue(len(old_locks) == 0)

            # Close the stage to release temp dir
            await context.close_stage_async()

    async def test_unlock_specs_command(self):
        layers = get_layers()
        specs_locking = layers.get_specs_locking()

        context = omni.usd.get_context()
        stage = context.get_stage()
        root_layer = stage.GetRootLayer()
        layer0 = Sdf.Layer.CreateAnonymous()
        layer1 = Sdf.Layer.CreateAnonymous()
        layer2 = Sdf.Layer.CreateAnonymous()
        root_layer.subLayerPaths.append(layer0.identifier)
        root_layer.subLayerPaths.append(layer1.identifier)
        root_layer.subLayerPaths.append(layer2.identifier)
        asset_name = f"/root/test0/l1/l2/l3"
        asset_prim = stage.DefinePrim(asset_name, "Xform")
        await omni.kit.app.get_app().next_update_async()

        specs_locking.lock_spec("/root", hierarchy=True)
        old_locks = omni.kit.usd.layers.get_all_locked_specs(context)
        for path in ["/", "/root", "/root/test0", "/root/test0/l1/l2/l3"]:
            for hierarchy in [False, True]:
                omni.kit.commands.execute("UnlockSpecs", spec_paths=path, hierarchy=hierarchy)

                # Make sure it's locked successfully
                locks = specs_locking.get_all_locked_specs()
                for spec_path in locks:
                    if hierarchy:
                        self.assertFalse(spec_path.startswith(path))
                    else:
                        sdf_path = Sdf.Path(spec_path)
                        self.assertNotEqual(str(sdf_path.GetPrimPath()), path)

                omni.kit.undo.undo()

                new_locks = specs_locking.get_all_locked_specs()
                self.assertEqual(set(old_locks), set(new_locks))
