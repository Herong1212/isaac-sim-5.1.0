# pylint: disable=missing-function-docstring, missing-class-docstring
import os

import carb
import omni.kit.test
from omni.kit import ui_test
from omni.kit.test_suite.helpers import arrange_windows, select_prims, wait_stage_loading
from pxr import Sdf


class TestPlaceholderAttribute(omni.kit.test.AsyncTestCase):
    async def setUp(self):
        await arrange_windows("Stage", 200)
        await omni.usd.get_context().new_stage_async()

    async def test_placeholder_attribute(self):
        from omni.kit.property.usd.placeholder_attribute import PlaceholderAttribute

        omni.kit.commands.execute("CreatePrimWithDefaultXform", prim_type="Sphere")

        usd_context = omni.usd.get_context()
        stage = usd_context.get_stage()
        prim = stage.GetPrimAtPath("/Sphere")
        attr_dict = {Sdf.PrimSpec.TypeNameKey: "bool", "customData": {"default": True}}

        # verifty attribute doesn't exist
        self.assertFalse(prim.GetAttribute("primvars:doNotCastShadows"))

        #################################################################
        # test expected usage
        #################################################################
        attr = PlaceholderAttribute(name="primvars:doNotCastShadows", prim=prim, metadata=attr_dict)

        # test stubs
        self.assertFalse(attr.ValueMightBeTimeVarying())
        self.assertFalse(attr.HasAuthoredConnections())

        # test get functions
        self.assertTrue(attr.Get())
        self.assertEqual(attr.GetPath(), "/Sphere")
        self.assertEqual(attr.GetPrim(), prim)
        self.assertEqual(attr.GetMetadata("customData"), attr_dict["customData"])
        self.assertFalse(attr.GetMetadata("test"))
        self.assertEqual(attr.GetAllMetadata(), attr_dict)

        # test CreateAttribute
        attr.CreateAttribute()

        # verifty attribute does exist
        self.assertTrue(prim.GetAttribute("primvars:doNotCastShadows"))
        prim.RemoveProperty("primvars:doNotCastShadows")
        self.assertFalse(prim.GetAttribute("primvars:doNotCastShadows"))

        #################################################################
        # test no metadata usage
        #################################################################
        attr = PlaceholderAttribute(name="primvars:doNotCastShadows", prim=prim, metadata={})

        # test stubs
        self.assertFalse(attr.ValueMightBeTimeVarying())
        self.assertFalse(attr.HasAuthoredConnections())

        # test get functions
        self.assertEqual(attr.Get(), None)
        self.assertEqual(attr.GetPath(), "/Sphere")
        self.assertEqual(attr.GetPrim(), prim)
        self.assertEqual(attr.GetMetadata("customData"), False)
        self.assertFalse(attr.GetMetadata("test"))
        self.assertEqual(attr.GetAllMetadata(), {})

        # test CreateAttribute
        attr.CreateAttribute()

        # verifty attribute doesn't exist
        self.assertFalse(prim.GetAttribute("primvars:doNotCastShadows"))

        #################################################################
        # test no prim usage
        #################################################################
        attr = PlaceholderAttribute(name="primvars:doNotCastShadows", prim=None, metadata=attr_dict)

        # test stubs
        self.assertFalse(attr.ValueMightBeTimeVarying())
        self.assertFalse(attr.HasAuthoredConnections())

        # test get functions
        self.assertTrue(attr.Get())
        self.assertEqual(attr.GetPath(), None)
        self.assertEqual(attr.GetPrim(), None)
        self.assertEqual(attr.GetMetadata("customData"), attr_dict["customData"])
        self.assertFalse(attr.GetMetadata("test"))
        self.assertEqual(attr.GetAllMetadata(), attr_dict)

        # test CreateAttribute
        attr.CreateAttribute()

        # verifty attribute doesn't exist
        self.assertFalse(prim.GetAttribute("primvars:doNotCastShadows"))

        #################################################################
        # test no name
        #################################################################
        attr = PlaceholderAttribute(name="", prim=prim, metadata=attr_dict)

        # test stubs
        self.assertFalse(attr.ValueMightBeTimeVarying())
        self.assertFalse(attr.HasAuthoredConnections())

        # test get functions
        self.assertTrue(attr.Get())
        self.assertEqual(attr.GetPath(), "/Sphere")
        self.assertEqual(attr.GetPrim(), prim)
        self.assertEqual(attr.GetMetadata("customData"), attr_dict["customData"])
        self.assertFalse(attr.GetMetadata("test"))
        self.assertEqual(attr.GetAllMetadata(), attr_dict)

        # test CreateAttribute
        attr.CreateAttribute()

        # verifty attribute doesn't exist
        self.assertFalse(prim.GetAttribute("primvars:doNotCastShadows"))

    async def test_placeholder_manual_sdf_input(self):
        stage = omni.usd.get_context().get_stage()

        # create root prim
        rootname = "/World"
        stage.SetDefaultPrim(stage.DefinePrim(rootname))

        kit_folder = carb.tokens.get_tokens_interface().resolve("${kit}")
        omni_pbr_mtl = os.path.normpath(kit_folder + "/mdl/core/Base/OmniPBR.mdl")
        mtl_path = omni.usd.get_stage_next_free_path(
            stage, "{}/Looks/{}".format(rootname, omni.usd.make_valid_identifier("OmniPBR")), False
        )
        omni.kit.commands.execute("CreateMdlMaterialPrim", mtl_url=omni_pbr_mtl, mtl_name="OmniPBR", mtl_path=mtl_path)

        await select_prims(["/World/Looks/OmniPBR"])
        await wait_stage_loading()

        mdl_widget = ui_test.find("Property//Frame/**/CollapsableFrame[*].title=='Material and Shader'")
        subframe_widget = mdl_widget.find("**/CollapsableFrame[*].title=='Albedo'")
        subframe_widget.widget.collapsed = False
        await ui_test.human_delay(10)
        widget = subframe_widget.find("**/StringField[*].identifier=='sdf_asset_inputs:diffuse_texture'")
        await widget.click()
        await ui_test.human_delay(10)
        await widget.input("xyzABC\n")

        prim = stage.GetPrimAtPath("/World/Looks/OmniPBR/Shader")
        attr = prim.GetAttribute("inputs:diffuse_texture")
        self.assertEqual(attr.Get(), Sdf.AssetPath("xyzABC"))
