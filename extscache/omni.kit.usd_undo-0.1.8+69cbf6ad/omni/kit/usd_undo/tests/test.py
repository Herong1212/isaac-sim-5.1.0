from pathlib import *
import omni.kit.test
from ..layer_undo import *
from pxr import Usd, UsdGeom, Kind, Gf


class TestUsdUndo(omni.kit.test.AsyncTestCase):
    async def test_layer_undo(self):
        def test(stage_in):
            layer_path = str(Path(__file__).parent.parent.parent.parent.parent / "data" / "test.usda")

            stage = Usd.Stage.Open(layer_path)
            stage.GetRootLayer().TransferContent(stage_in.GetRootLayer())

            usd_undo = UsdEditTargetUndo(stage.GetEditTarget())

            mesh = UsdGeom.Mesh.Define(stage, "/root/mesh")
            mesh.CreateNormalsAttr().Set([Gf.Vec3f(1, 0, 0)])
            mesh.SetNormalsInterpolation("constant")

            model = Usd.ModelAPI(mesh)
            model.SetKind(Kind.Tokens.group)

            org_stage_str = stage.GetRootLayer().ExportToString()
            #print("Original stage:")
            #print(org_stage_str)

            usd_undo.reserve("/root/mesh.normals")
            mesh.GetNormalsAttr().Set([Gf.Vec3f(0, 1, 0)])
            mesh.SetNormalsInterpolation("faceVarying")

            usd_undo.reserve("/root/mesh", "kind")
            model.SetKind(Kind.Tokens.component)

            usd_undo.reserve("/root/newPrim")
            stage.DefinePrim("/root/newPrim")

            modified_stage_str = stage.GetRootLayer().ExportToString()
            #print("Modified stage:")
            #print(modified_stage_str)

            self.assertNotEqual(org_stage_str, modified_stage_str)

            # Re-create the layer before undo
            cache_layer = Sdf.Layer.CreateAnonymous()
            cache_layer.TransferContent(stage.GetRootLayer())
            stage = None

            self.assertTrue(Sdf.Layer.Find(layer_path) is None)

            stage = Usd.Stage.Open(layer_path)

            layer = stage.GetRootLayer()
            stage.GetRootLayer().TransferContent(cache_layer)

            self.assertEqual(stage.GetRootLayer().ExportToString(), modified_stage_str)

            self.assertTrue(Sdf.Layer.Find(layer_path) is not None)

            usd_undo.undo()

            undone_stage_str = stage.GetRootLayer().ExportToString()
            #print("Undone stage:")
            #print(undone_stage_str)

            self.assertEqual(org_stage_str, undone_stage_str)

        # Test normal prim
        stage =  Usd.Stage.CreateInMemory()
        stage.DefinePrim("/root")
        test(stage)

        # Test with variant
        #print("Test with variant...")
        stage =  Usd.Stage.CreateInMemory()
        prim = stage.DefinePrim("/root")
        variant_sets = prim.GetVariantSets()
        variant_sets.AddVariantSet("variantSet")
        variant_set = variant_sets.GetVariantSet("variantSet")
        variant_set.AddVariant("variant")
        variant_set.SetVariantSelection("variant")
        with variant_set.GetVariantEditContext():
            test(stage)
