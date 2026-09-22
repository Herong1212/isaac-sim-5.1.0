import carb
import carb.tokens
import omni.ext
import omni.kit.commands
from pxr import UsdLux, UsdShade, Kind, Vt, Gf, UsdGeom, Sdf, Usd


class DefaultStage:
    def __init__(self):
        omni.kit.stage_template.core.register_template("default stage", self.new_stage)

    def __del__(self):  # pragma: no cover
        omni.kit.stage_template.core.unregister_template("default stage")

    def new_stage(self, rootname, usd_context_name):
        data_path = carb.tokens.get_tokens_interface().resolve("${omni.kit.stage_templates}/data/")
        carlight_hdr = Sdf.AssetPath(f"{data_path}/CarLight_512x256.hdr")
        grid_basecolor = Sdf.AssetPath(f"{data_path}/ov_uv_grids_basecolor_1024.png")

        # change ambientLightColor
        carb.settings.get_settings().set("/rtx/sceneDb/ambientLightColor", (0, 0, 0))
        carb.settings.get_settings().set("/rtx/indirectDiffuse/enabled", True)
        carb.settings.get_settings().set("/rtx/domeLight/upperLowerStrategy", 0)
        carb.settings.get_settings().set("/rtx/post/lensFlares/flareScale", 0.075)
        carb.settings.get_settings().set("/rtx/sceneDb/ambientLightIntensity", 0)

        # get up axis
        usd_context = omni.usd.get_context(usd_context_name)
        stage = usd_context.get_stage()
        up_axis = UsdGeom.GetStageUpAxis(stage)

        with Usd.EditContext(stage, stage.GetRootLayer()):
            # create Environment
            omni.kit.commands.execute(
                "CreatePrim",
                prim_path="/Environment",
                prim_type="Xform",
                select_new_prim=False,
                create_default_xform=True,
                context_name=usd_context_name
            )
            prim = stage.GetPrimAtPath("/Environment")
            prim.CreateAttribute("ground:size", Sdf.ValueTypeNames.Int, False).Set(1400)
            prim.CreateAttribute("ground:type", Sdf.ValueTypeNames.String, False).Set("On")

            # create Sky
            omni.kit.commands.execute(
                "CreatePrim",
                prim_path="/Environment/Sky",
                prim_type="DomeLight",
                select_new_prim=False,
                attributes={
                            UsdLux.Tokens.inputsIntensity: 1,
                            UsdLux.Tokens.inputsColorTemperature: 6250,
                            UsdLux.Tokens.inputsEnableColorTemperature: True,
                            UsdLux.Tokens.inputsExposure: 9,
                            UsdLux.Tokens.inputsTextureFile: carlight_hdr,
                            UsdLux.Tokens.inputsTextureFormat: UsdLux.Tokens.latlong,
                            UsdGeom.Tokens.visibility: "inherited",
                            } if hasattr(UsdLux.Tokens, 'inputsIntensity') else \
                            {
                            UsdLux.Tokens.intensity: 1,
                            UsdLux.Tokens.colorTemperature: 6250,
                            UsdLux.Tokens.enableColorTemperature: True,
                            UsdLux.Tokens.exposure: 9,
                            UsdLux.Tokens.textureFile: carlight_hdr,
                            UsdLux.Tokens.textureFormat: UsdLux.Tokens.latlong,
                            UsdGeom.Tokens.visibility: "inherited",
                            },
                create_default_xform=True,
                context_name=usd_context_name
            )
            prim = stage.GetPrimAtPath("/Environment/Sky")
            prim.CreateAttribute("xformOp:scale", Sdf.ValueTypeNames.Double3, False).Set(Gf.Vec3d(1, 1, 1))
            if up_axis == "Y":
                prim.CreateAttribute("xformOp:translate", Sdf.ValueTypeNames.Double3, False).Set(Gf.Vec3d(0, 305, 0))
                prim.CreateAttribute("xformOp:rotateXYZ", Sdf.ValueTypeNames.Double3, False).Set(Gf.Vec3d(0, -90, -90))
            else:  # pragma: no cover
                prim.CreateAttribute("xformOp:translate", Sdf.ValueTypeNames.Double3, False).Set(Gf.Vec3d(0, 0, 305))
                prim.CreateAttribute("xformOp:rotateXYZ", Sdf.ValueTypeNames.Double3, False).Set(Gf.Vec3d(0, 0, 0))

            prim.CreateAttribute("xformOpOrder", Sdf.ValueTypeNames.String, False).Set(["xformOp:translate", "xformOp:rotateXYZ", "xformOp:scale"])

            # create DistantLight
            omni.kit.commands.execute(
                "CreatePrim",
                prim_path="/Environment/DistantLight",
                prim_type="DistantLight",
                select_new_prim=False,
                attributes={UsdLux.Tokens.inputsAngle: 2.5,
                            UsdLux.Tokens.inputsIntensity: 1,
                            UsdLux.Tokens.inputsColorTemperature: 7250,
                            UsdLux.Tokens.inputsEnableColorTemperature: True,
                            UsdLux.Tokens.inputsExposure: 10,
                            UsdGeom.Tokens.visibility: "inherited",
                            } if hasattr(UsdLux.Tokens, 'inputsIntensity') else \
                    {
                    UsdLux.Tokens.angle: 2.5,
                    UsdLux.Tokens.intensity: 1,
                    UsdLux.Tokens.colorTemperature: 7250,
                    UsdLux.Tokens.enableColorTemperature: True,
                    UsdLux.Tokens.exposure: 10,
                    UsdGeom.Tokens.visibility: "inherited",
                    },
                create_default_xform=True,
                context_name=usd_context_name
            )
            prim = stage.GetPrimAtPath("/Environment/DistantLight")
            if up_axis == "Y":
                prim.CreateAttribute("xformOp:translate", Sdf.ValueTypeNames.Double3, False).Set(Gf.Vec3d(0, 305, 0))
                prim.CreateAttribute("xformOp:rotateXYZ", Sdf.ValueTypeNames.Double3, False).Set(Gf.Vec3d(-105, 0, 0))
            else:  # pragma: no cover
                prim.CreateAttribute("xformOp:translate", Sdf.ValueTypeNames.Double3, False).Set(Gf.Vec3d(0, 0, 305))
                prim.CreateAttribute("xformOp:rotateXYZ", Sdf.ValueTypeNames.Double3, False).Set(Gf.Vec3d(-15, 0, 0))
            prim.CreateAttribute("xformOpOrder", Sdf.ValueTypeNames.String, False).Set(["xformOp:translate", "xformOp:rotateXYZ", "xformOp:scale"])

            # Material "Grid"
            mtl_path = omni.usd.get_stage_next_free_path(stage, "/Environment/Looks/Grid", False)
            omni.kit.commands.execute("CreateMdlMaterialPrim", mtl_url="OmniPBR.mdl", mtl_name="Grid", mtl_path=mtl_path, context_name=usd_context_name)
            mat_prim = stage.GetPrimAtPath(mtl_path)
            shader = UsdShade.Material(mat_prim).ComputeSurfaceSource("mdl")[0]
            shader.SetSourceAssetSubIdentifier("OmniPBR", "mdl")

            # set inputs
            omni.usd.create_material_input(mat_prim, "albedo_add", 0, Sdf.ValueTypeNames.Float)
            omni.usd.create_material_input(mat_prim, "albedo_brightness", 0.52, Sdf.ValueTypeNames.Float)
            omni.usd.create_material_input(mat_prim, "albedo_desaturation", 1, Sdf.ValueTypeNames.Float)
            omni.usd.create_material_input(mat_prim, "project_uvw", False, Sdf.ValueTypeNames.Bool)
            omni.usd.create_material_input(mat_prim, "reflection_roughness_constant", 0.333, Sdf.ValueTypeNames.Float)
            omni.usd.create_material_input(mat_prim, "diffuse_texture", grid_basecolor,  Sdf.ValueTypeNames.Asset, def_value=Sdf.AssetPath(""), color_space="sRGB")
            omni.usd.create_material_input(mat_prim, "texture_rotate", 0, Sdf.ValueTypeNames.Float, def_value=Vt.Float(0.0))
            omni.usd.create_material_input(mat_prim, "texture_scale", Gf.Vec2f(0.5, 0.5), Sdf.ValueTypeNames.Float2, def_value=Gf.Vec2f(1, 1))
            omni.usd.create_material_input(mat_prim, "texture_translate", Gf.Vec2f(0, 0), Sdf.ValueTypeNames.Float2, def_value=Gf.Vec2f(0, 0))
            omni.usd.create_material_input(mat_prim, "world_or_object", False, Sdf.ValueTypeNames.Bool, def_value=Vt.Bool(False))

            # Ground
            ground_path = "/Environment/ground"
            omni.kit.commands.execute(
                "CreateMeshPrimWithDefaultXform",
                prim_path=ground_path,
                prim_type="Plane",
                select_new_prim=False,
                prepend_default_prim=False,
                context_name=usd_context_name
            )
            prim = stage.GetPrimAtPath(ground_path)
            prim.CreateAttribute("xformOp:translate", Sdf.ValueTypeNames.Double3, False).Set(Gf.Vec3d(0, 0, 0))
            prim.CreateAttribute("xformOp:scale", Sdf.ValueTypeNames.Double3, False).Set(Gf.Vec3d(1, 1, 1))
            prim.CreateAttribute("xformOpOrder", Sdf.ValueTypeNames.String, False).Set(["xformOp:translate", "xformOp:rotateXYZ", "xformOp:scale"])
            if up_axis == "Y":
                prim.CreateAttribute("xformOp:rotateXYZ", Sdf.ValueTypeNames.Double3, False).Set(Gf.Vec3d(0, -90, -90))
            else:  # pragma: no cover
                prim.CreateAttribute("xformOp:rotateXYZ", Sdf.ValueTypeNames.Double3, False).Set(Gf.Vec3d(0, 0, 0))

            mesh = UsdGeom.Mesh(prim)
            mesh.CreateSubdivisionSchemeAttr("none")
            mesh.GetFaceVertexCountsAttr().Set([4])
            mesh.GetFaceVertexIndicesAttr().Set([0, 1, 3, 2])
            mesh.GetPointsAttr().Set(Vt.Vec3fArray([(-50, -50, 0), (50, -50, 0), (-50, 50, 0), (50, 50, 0)]))
            mesh.GetNormalsAttr().Set(Vt.Vec3fArray([(0, 0, 1), (0, 0, 1), (0, 0, 1), (0, 0, 1)]))
            mesh.SetNormalsInterpolation("faceVarying")

            # https://github.com/PixarAnimationStudios/USD/commit/592b4d39edf5daf0534d467e970c95462a65d44b
            # UsdGeom.Imageable.CreatePrimvar deprecated in v19.03 and removed in v22.08
            primvar = UsdGeom.PrimvarsAPI(prim).CreatePrimvar("st", Sdf.ValueTypeNames.TexCoord2fArray, UsdGeom.Tokens.faceVarying)
            primvar.Set(Vt.Vec2fArray([(0, 0), (1, 0), (1, 1), (0, 1)]))

            # Create a ground plane collider
            # NOTE: replace with USD plane prim after the next USD update
            try:
                from pxr import UsdPhysics
                colPlanePath = "/Environment/groundCollider"
                planeGeom = UsdGeom.Plane.Define(stage, colPlanePath)
                planeGeom.CreatePurposeAttr().Set("guide")
                planeGeom.CreateAxisAttr().Set(up_axis)
                colPlanePrim = stage.GetPrimAtPath(colPlanePath)
                UsdPhysics.CollisionAPI.Apply(colPlanePrim)
            except ImportError:  # pragma: no cover
                carb.log_warn("Failed to create a ground plane collider. Please load the omni.physx.bundle extension and create a new stage from this template if you need it.")

            # bind "Grid" to "Ground"
            omni.kit.commands.execute("BindMaterialCommand", prim_path=ground_path, material_path=mtl_path, strength=None, context_name=usd_context_name)

            # update extent
            attr = prim.GetAttribute(UsdGeom.Tokens.extent)
            if attr:
                bounds = UsdGeom.Boundable.ComputeExtentFromPlugins(UsdGeom.Boundable(prim), Usd.TimeCode.Default())
                if bounds:
                    attr.Set(bounds)
