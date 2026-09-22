import carb
import os
import omni.ext
from pathlib import Path
from pxr import UsdLux, UsdShade, Kind, Vt, Gf
from omni.kit.stage_templates.new_stage import *


class WarmLightsStage:
    def __init__(self):
        register_template("warmlights", self.new_stage)

    def __del__(self):
        unregister_template("warmlights")

    def new_stage(self, rootname):
        from pxr import UsdLux, UsdShade, Kind, Vt, Gf

        # S3 URL's
        carlight_hdr = Sdf.AssetPath("https://omniverse-content-production.s3.us-west-2.amazonaws.com/Assets/Scenes/Templates/Default/SubUSDs/textures/CarLight_512x256.hdr")
        grid_basecolor = Sdf.AssetPath("https://omniverse-content-production.s3.us-west-2.amazonaws.com/Assets/Scenes/Templates/Default/SubUSDs/textures/ov_uv_grids_basecolor_1024.png")

        # change ambientLightColor
        carb.settings.get_settings().set("/rtx/sceneDb/ambientLightColor", (0, 0, 0))
        carb.settings.get_settings().set("/rtx/indirectDiffuse/enabled", True)
        carb.settings.get_settings().set("/rtx/domeLight/upperLowerStrategy", 0)
        carb.settings.get_settings().set("/rtx/post/lensFlares/flareScale", 0.075)
        carb.settings.get_settings().set("/rtx/sceneDb/ambientLightIntensity", 0)

        # get up axis
        stage = omni.usd.get_context().get_stage()
        up_axis = UsdGeom.GetStageUpAxis(stage)

        # Create basic DistantLight
        with Usd.EditContext(stage, stage.GetRootLayer()):
            # create Environment
            omni.kit.commands.execute(
                "CreatePrim",
                prim_path="/Environment",
                prim_type="Scope",
                select_new_prim=False,
                create_default_xform=True,
            )

            # create Lights
            omni.kit.commands.execute(
                "CreatePrim",
                prim_path="/Environment/Lights",
                prim_type="Xform",
                select_new_prim=False,
                create_default_xform=True,
            )
            prim = stage.GetPrimAtPath("/Environment/Lights")
            Usd.ModelAPI(prim).SetKind(Kind.Tokens.component)
            prim.CreateAttribute("xformOp:translate:pivot", Sdf.ValueTypeNames.Double3, False).Set(Gf.Vec3d(0, 0, 0))
            prim.CreateAttribute("xformOpOrder", Sdf.ValueTypeNames.String, False).Set(["xformOp:translate", "xformOp:translate:pivot", "xformOp:rotateXYZ", "xformOp:scale", "!invert!xformOp:translate:pivot"])
            if up_axis == "Y":
                prim.CreateAttribute("xformOp:rotateXYZ", Sdf.ValueTypeNames.Double3, False).Set(Gf.Vec3d(0, -90, -90))
            else:
                prim.CreateAttribute("xformOp:rotateXYZ", Sdf.ValueTypeNames.Double3, False).Set(Gf.Vec3d(0, 0, 0))

            # create DomeLight
            omni.kit.commands.execute(
                "CreatePrim",
                prim_path="/Environment/Lights/DomeLight",
                prim_type="DomeLight",
                select_new_prim=False,
                attributes={
                            UsdLux.Tokens.inputsIntensity: 1,
                            UsdLux.Tokens.inputsColorTemperature: 6150,
                            UsdLux.Tokens.inputsEnableColorTemperature: True,
                            UsdLux.Tokens.inputsExposure: 9,
                            UsdLux.Tokens.inputsTextureFile: carlight_hdr,
                            UsdLux.Tokens.inputsTextureFormat: UsdLux.Tokens.latlong,
                            UsdGeom.Tokens.visibility: "inherited",
                            },
                create_default_xform=True,
            )
            prim = stage.GetPrimAtPath("/Environment/Lights/DomeLight")
            prim.CreateAttribute("xformOp:translate", Sdf.ValueTypeNames.Double3, False).Set(Gf.Vec3d(0, 0, 305))
            prim.CreateAttribute("xformOp:scale", Sdf.ValueTypeNames.Double3, False).Set(Gf.Vec3d(1, 1, 1))
            prim.CreateAttribute("xformOp:rotateXYZ", Sdf.ValueTypeNames.Double3, False).Set(Gf.Vec3d(0, 0, 62.30000092834234))
            prim.CreateAttribute("xformOpOrder", Sdf.ValueTypeNames.String, False).Set(["xformOp:translate", "xformOp:rotateXYZ", "xformOp:scale"])

            # create DistantLight
            omni.kit.commands.execute(
                "CreatePrim",
                prim_path="/Environment/Lights/DistantLight",
                prim_type="DistantLight",
                select_new_prim=False,
                attributes={UsdLux.Tokens.inputsAngle: 0.53,
                            UsdLux.Tokens.inputsIntensity: 1,
                            UsdLux.Tokens.inputsColorTemperature: 7250,
                            UsdLux.Tokens.inputsEnableColorTemperature: True,
                            UsdLux.Tokens.inputsExposure: 10,
                            UsdGeom.Tokens.visibility: "inherited",
                            },
                create_default_xform=True,
            )
            prim = stage.GetPrimAtPath("/Environment/Lights/DistantLight")
            prim.CreateAttribute("xformOp:translate", Sdf.ValueTypeNames.Double3, False).Set(Gf.Vec3d(0, 0, 305))
            prim.CreateAttribute("xformOp:rotateXYZ", Sdf.ValueTypeNames.Double3, False).Set(Gf.Vec3d(55, 0, 135))
            prim.CreateAttribute("xformOpOrder", Sdf.ValueTypeNames.String, False).Set(["xformOp:translate", "xformOp:rotateXYZ", "xformOp:scale"])

            # GroundPlane
            omni.kit.commands.execute(
                "CreatePrim",
                prim_path="/Environment/GroundPlane",
                prim_type="Xform",
                select_new_prim=False,
                create_default_xform=True,
            )
            prim = stage.GetPrimAtPath("/Environment/GroundPlane")
            prim.SetInstanceable(False)
            Usd.ModelAPI(prim).SetKind(Kind.Tokens.component)
            prim.CreateAttribute("xformOp:translate", Sdf.ValueTypeNames.Double3, False).Set(Gf.Vec3d(0, 0, 0))
            prim.CreateAttribute("xformOp:scale", Sdf.ValueTypeNames.Double3, False).Set(Gf.Vec3d(60, 60, 60))
            prim.CreateAttribute("xformOpOrder", Sdf.ValueTypeNames.String, False).Set(["xformOp:translate", "xformOp:rotateXYZ", "xformOp:scale"])
            if up_axis == "Y":
                prim.CreateAttribute("xformOp:rotateXYZ", Sdf.ValueTypeNames.Double3, False).Set(Gf.Vec3d(0, -90, -90))
            else:
                prim.CreateAttribute("xformOp:rotateXYZ", Sdf.ValueTypeNames.Double3, False).Set(Gf.Vec3d(0, 0, 0))

            # Mesh "Hex"
            omni.kit.commands.execute(
                "CreatePrim",
                prim_path="/Environment/GroundPlane/Hex",
                prim_type="Mesh",
                select_new_prim=False,
                create_default_xform=True,
            )
            prim = stage.GetPrimAtPath("/Environment/GroundPlane/Hex")
            prim.ApplyAPI(UsdLux.ShadowAPI)

            mesh = UsdGeom.Mesh(prim)
            mesh.CreateSubdivisionSchemeAttr("none")
            mesh.GetFaceVertexCountsAttr().Set([4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4])
            mesh.GetFaceVertexIndicesAttr().Set([4, 3, 2, 5, 0, 1, 7, 6, 1, 2, 8, 7, 2, 3, 9, 8, 3, 4, 10, 9, 4, 5, 11, 10, 5, 0, 6, 11, 24, 25, 30, 31, 25, 26, 35, 30, 26, 27, 34, 35, 27, 28, 33, 34, 28, 29, 32, 33, 29, 24, 31, 32, 12, 13, 19, 18, 13, 14, 20, 19, 14, 15, 21, 20, 15, 16, 22, 21, 16, 17, 23, 22, 17, 12, 18, 23, 20, 21, 22, 23, 6, 7, 25, 24, 7, 8, 26, 25, 8, 9, 27, 26, 9, 10, 28, 27, 10, 11, 29, 28, 11, 6, 24, 29, 13, 12, 31, 30, 12, 17, 32, 31, 17, 16, 33, 32, 16, 15, 34, 33, 15, 14, 35, 34, 14, 13, 30, 35, 18, 19, 20, 23, 1, 0, 5, 2])
            mesh.GetPointsAttr().Set(Vt.Vec3fArray([(100, 4.371139e-8, -1), (49.999996, 86.60255, -1), (-50.000008, 86.60254, -1), (-100, -0.0000086985665, -1), (-49.999992, -86.60255, -1), (49.999992, -86.60255, -1), (100, 4.371139e-8, -0.72249514), (50, 86.60255, -0.72249514), (-50.000008, 86.60254, -0.72249514), (-100, -0.0000086985665, -0.72249514), (-49.999992, -86.60255, -0.72249514), (49.999992, -86.60255, -0.72249514), (100, 4.371139e-8, -0.2775048), (50, 86.60255, -0.2775048), (-50.000008, 86.60254, -0.2775048), (-100, -0.0000086985665, -0.2775048), (-49.999992, -86.60255, -0.2775048), (49.999992, -86.60255, -0.2775048), (100, 4.371139e-8, 0), (49.999996, 86.60255, 0), (-50.000008, 86.60254, 0), (-100, -0.0000086985665, 0), (-49.999992, -86.60255, 0), (49.999992, -86.60255, 0), (99.861, 4.638057e-8, -0.6724951), (49.9305, 86.48217, -0.6724951), (-49.93051, 86.48216, -0.6724951), (-99.861, -0.000005771848, -0.6724951), (-49.930492, -86.48217, -0.6724951), (49.930492, -86.48217, -0.6724951), (49.9305, 86.48217, -0.3275048), (99.861, 4.638057e-8, -0.3275048), (49.930492, -86.48217, -0.3275048), (-49.930492, -86.48217, -0.3275048), (-99.861, -0.000005771848, -0.3275048), (-49.93051, 86.48216, -0.3275048)]))
            mesh.GetNormalsAttr().Set(Vt.Vec3fArray([(0, 0, -1), (0, 0, -1), (0, 0, -1), (0, 0, -1), (0.8660031, 0.50003856, 0), (0.86612207, 0.49983254, -0.000011923486), (0.86612207, 0.49983254, -0.000011923486), (0.86600316, 0.50003856, 0), (0, 1, 0), (0, 1, 0), (0, 1, 0), (0, 1, 0), (-0.86612207, 0.49983254, 0), (-0.86600316, 0.5000385, 0), (-0.86600316, 0.50003856, 0), (-0.86612207, 0.49983254, 0), (-0.8660031, -0.5000386, 0), (-0.86612207, -0.49983254, 0), (-0.86612207, -0.49983254, 0), (-0.8660031, -0.5000386, 0), (0, -1, 0), (0, -1, 0), (0, -1, 0), (0, -1, 0), (0.86612207, -0.49983254, 0), (0.8660031, -0.5000386, 0), (0.8660031, -0.5000387, 0), (0.86612207, -0.49983254, 0), (0.8660031, 0.50003856, 0), (0.86612207, 0.49983254, 0), (0.86612207, 0.49983254, 0), (0.8660031, 0.50003856, 0), (0, 1, 0), (0, 1, 0), (0, 1, 0), (0, 1, 0), (-0.86612207, 0.49983254, 0), (-0.86600316, 0.5000385, 0), (-0.86600316, 0.5000385, 0), (-0.86612207, 0.49983254, 0), (-0.8660031, -0.5000386, 0), (-0.86612207, -0.49983254, 0), (-0.86612207, -0.49983254, 0), (-0.8660031, -0.5000386, 0), (0, -1, 0), (0, -1, 0), (0, -1, 0), (0, -1, 0), (0.86612207, -0.49983254, 0), (0.8660031, -0.5000386, 0), (0.8660031, -0.50003856, 0), (0.86612207, -0.49983254, 0), (0.86600316, 0.50003856, 0), (0.86612207, 0.49983254, 0.000011923486), (0.86612207, 0.49983254, 0.000011923486), (0.8660031, 0.50003856, 0), (0, 1, 0), (0, 1, 0), (0, 1, 0), (0, 1, 0), (-0.86612207, 0.49983254, 0), (-0.86600316, 0.50003856, 0), (-0.86600316, 0.5000385, 0), (-0.86612207, 0.49983254, 0), (-0.8660031, -0.5000387, 0), (-0.86612207, -0.49983254, 0), (-0.86612207, -0.49983254, 0), (-0.8660031, -0.5000386, 0), (0, -1, 0), (0, -1, 0), (0, -1, 0), (0, -1, 0), (0.86612207, -0.49983254, 0), (0.8660031, -0.5000386, 0), (0.8660031, -0.5000386, 0), (0.86612207, -0.49983254, 0), (0, 0, 1), (0, 0, 1), (0, 0, 1), (0, 0, 1), (0.33871505, -0.0001368864, 0.940889), (0.16937703, 0.2929765, 0.9409974), (0.16937703, 0.2929765, 0.9409974), (0.33871505, -0.00013523527, 0.940889), (0.16937703, 0.2929765, 0.9409974), (-0.16900647, 0.29299542, 0.9410582), (-0.16900647, 0.29299542, 0.9410582), (0.16937703, 0.2929765, 0.9409974), (-0.16900647, 0.29299542, 0.9410582), (-0.33871505, 0.00013335996, 0.940889), (-0.33871505, 0.00013702258, 0.940889), (-0.16900647, 0.29299542, 0.9410582), (-0.33871505, 0.00013335996, 0.940889), (-0.16937703, -0.2929765, 0.9409974), (-0.16937703, -0.2929765, 0.9409974), (-0.33871505, 0.00013702258, 0.940889), (-0.16937703, -0.2929765, 0.9409974), (0.16900647, -0.29299542, 0.9410582), (0.16900647, -0.29299542, 0.9410582), (-0.16937703, -0.2929765, 0.9409974), (0.16900647, -0.29299542, 0.9410582), (0.33871505, -0.0001368864, 0.940889), (0.33871505, -0.00013523527, 0.940889), (0.16900647, -0.29299542, 0.9410582), (0.16900647, 0.29299542, -0.9410582), (0.33871505, 0.0001368575, -0.940889), (0.33871505, 0.00013519291, -0.940889), (0.16900647, 0.29299542, -0.9410582), (0.33871505, 0.0001368575, -0.940889), (0.16937703, -0.2929765, -0.9409974), (0.16937703, -0.2929765, -0.9409974), (0.33871505, 0.00013519291, -0.940889), (0.16937703, -0.2929765, -0.9409974), (-0.16900647, -0.29299542, -0.9410582), (-0.16900647, -0.29299542, -0.9410582), (0.16937703, -0.2929765, -0.9409974), (-0.16900647, -0.29299542, -0.9410582), (-0.33871505, -0.00014040324, -0.940889), (-0.33871505, -0.00013557557, -0.940889), (-0.16900647, -0.29299542, -0.9410582), (-0.33871505, -0.00014040324, -0.940889), (-0.16937703, 0.2929765, -0.9409974), (-0.16937703, 0.2929765, -0.9409974), (-0.33871505, -0.00013557557, -0.940889), (-0.16937703, 0.2929765, -0.9409974), (0.16900647, 0.29299542, -0.9410582), (0.16900647, 0.29299542, -0.9410582), (-0.16937703, 0.2929765, -0.9409974), (0, 0, 1), (0, 0, 1), (0, 0, 1), (0, 0, 1), (0, 0, -1), (0, 0, -1), (0, 0, -1), (0, 0, -1)]))
            mesh.SetNormalsInterpolation("faceVarying")
            prim.GetAttribute("extent").Set([(-100, -86.60255, -1), (100, 86.60255, 0)])
            prim.GetAttribute("orientation").Set(UsdGeom.Tokens.rightHanded)
            primvar = UsdGeom.PrimvarsAPI(prim).CreatePrimvar("st", Sdf.ValueTypeNames.TexCoord2fArray, UsdGeom.Tokens.faceVarying)
            primvar.Set(Vt.Vec2fArray([(0.2502916, 0.0007705142), (0.7494, 0.00071682385), (0.99928534, 0.4325493), (0.00071467983, 0.43283156), (0.25059986, 0.8646642), (0.74970835, 0.86461055), (0.750089, 0.8652724), (0.25025097, 0.86526835), (0.99993235, 0.4325194), (0.7497488, 0.000112710964), (0.2499109, 0.00010883978), (0.00006753724, 0.4328615), (0.2503683, 0.000096005526), (0.75008875, 0.00016008862), (0.7497084, 0.00082188356), (0.25066745, 0.000728975), (0.99993235, 0.4329134), (0.9992858, 0.43288368), (0.74963176, 0.865389), (0.74933267, 0.86475605), (0.24991132, 0.8653252), (0.25029194, 0.8646633), (0.00006777561, 0.4325719), (0.00071456225, 0.43260157), (0.75016356, 0.8653811), (0.2502013, 0.86535454), (1, 0.4325058), (0.25033513, 0), (0.75016344, 0.0000509806), (0, 0.4325584), (0.74979866, 0.000026472931), (0.24983634, 0), (0, 0.43287516), (0.24983652, 0.86543393), (0.7496649, 0.865485), (1, 0.43292674), (0.0011516024, 0), (0.0011516024, 0.6666666), (0.0011516024, 1), (0.0016797101, 0.9999998), (0.0016797101, 0.6666665), (0.0016797101, 0.33333325), (0.0016797101, 0), (0.0011515331, 0.33333334), (6.926932e-8, 1), (0.0028313126, 0.9999998), (0, 0.6666666), (0, 0.33333334), (0.0028313126, 0), (0.0028313126, 0.33333325), (0.0028313126, 0.6666665), (0, 0)]))
            primvar.SetIndices(Vt.IntArray([0, 1, 2, 3, 4, 5, 6, 7, 5, 2, 8, 6, 2, 1, 9, 8, 1, 0, 10, 9, 0, 3, 11, 10, 3, 4, 7, 11, 37, 38, 44, 46, 39, 40, 50, 45, 40, 41, 49, 50, 41, 42, 48, 49, 36, 43, 47, 51, 43, 37, 46, 47, 12, 13, 14, 15, 13, 16, 17, 14, 16, 18, 19, 17, 18, 20, 21, 19, 20, 22, 23, 21, 22, 12, 15, 23, 17, 19, 21, 23, 7, 6, 24, 25, 6, 8, 26, 24, 8, 9, 30, 26, 9, 10, 31, 30, 10, 11, 32, 31, 11, 7, 25, 32, 13, 12, 27, 28, 12, 22, 29, 27, 22, 20, 33, 29, 20, 18, 34, 33, 18, 16, 35, 34, 16, 13, 28, 35, 15, 14, 17, 23, 5, 4, 3, 2]))
            # primvar = UsdGeom.PrimvarsAPI(prim).CreatePrimvar("displayColor", Sdf.ValueTypeNames.Color3fArray)
            # primvar.Set(Vt.Vec3fArray([(0.34117648, 0.882353, 0.34117648)]))
            # prim.CreateAttribute("smoothgroups3DSMax", Sdf.ValueTypeNames.UIntArray, True).Set([1, 2, 4, 2, 4, 2, 4, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 4, 8, 8, 8, 8, 8, 8, 4, 4, 4, 4, 4, 4, 4, 1])

            # Material "Grid"
            mtl_path = omni.usd.get_stage_next_free_path(stage, "/Environment/GroundPlane/Grid", False)
            omni.kit.commands.execute("CreateMdlMaterialPrim", mtl_url="OmniPBR.mdl", mtl_name="Grid", mtl_path=mtl_path)
            mat_prim = stage.GetPrimAtPath(mtl_path)
            shader = UsdShade.Material(mat_prim).ComputeSurfaceSource("mdl")[0]
            shader.SetSourceAssetSubIdentifier("OmniPBR", "mdl")

            # set inputs
            omni.usd.create_material_input(mat_prim, "albedo_add", 0.0, Sdf.ValueTypeNames.Float, def_value=Vt.Float(0))
            omni.usd.create_material_input(mat_prim, "albedo_brightness", 1.0, Sdf.ValueTypeNames.Float, def_value=Vt.Float(1.0))
            omni.usd.create_material_input(mat_prim, "albedo_desaturation", 0.0, Sdf.ValueTypeNames.Float, def_value=Vt.Float(0.0))
            omni.usd.create_material_input(mat_prim, "diffuse_texture", grid_basecolor,  Sdf.ValueTypeNames.Asset, def_value=Sdf.AssetPath(""), color_space="sRGB")
            omni.usd.create_material_input(mat_prim, "project_uvw", False, Sdf.ValueTypeNames.Bool, def_value=Vt.Bool(False))
            omni.usd.create_material_input(mat_prim, "reflection_roughness_constant", 0.3, Sdf.ValueTypeNames.Float, def_value=Vt.Float(0.5))
            omni.usd.create_material_input(mat_prim, "texture_translate", Gf.Vec2f(-0.097, 0.0405), Sdf.ValueTypeNames.Float2, def_value=Gf.Vec2f(0, 0))
            omni.usd.create_material_input(mat_prim, "texture_rotate", 60, Sdf.ValueTypeNames.Float, def_value=Vt.Float(0.0))
            omni.usd.create_material_input(mat_prim, "texture_scale", Gf.Vec2f(120.2, 120.2), Sdf.ValueTypeNames.Float2, def_value=Gf.Vec2f(1, 1))
            omni.usd.create_material_input(mat_prim, "world_or_object", False, Sdf.ValueTypeNames.Bool, def_value=Vt.Bool(False))

            # bind "Grid" to "Hex"
            omni.kit.commands.execute("BindMaterialCommand", prim_path="/Environment/GroundPlane/Hex", material_path=mtl_path, strength=None)

WarmLightsStage()