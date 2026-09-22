import os
import carb
import carb.settings
import omni.kit.commands
from pxr import Usd, Sdf, UsdGeom, Gf, Tf, UsdShade, UsdLux
from omni.usd import make_valid_identifier


def create_test_stage():
    settings = carb.settings.get_settings()
    default_prim_name = settings.get("/persistent/app/stage/defaultPrimName")
    rootname = f"/{default_prim_name}"

    stage = omni.usd.get_context().get_stage()
    kit_folder = carb.tokens.get_tokens_interface().resolve("${kit}")
    omni_pbr_mtl = os.path.normpath(kit_folder + "/mdl/core/Base/OmniPBR.mdl")

    # create Looks folder
    omni.kit.commands.execute(
        "CreatePrim", prim_path="{}/Looks".format(rootname), prim_type="Scope", select_new_prim=False
    )

    # create GroundMat material
    mtl_name = "GroundMat"
    mtl_path = omni.usd.get_stage_next_free_path(
        stage, "{}/Looks/{}".format(rootname, make_valid_identifier(mtl_name)), False
    )
    omni.kit.commands.execute(
        "CreateMdlMaterialPrim", mtl_url=omni_pbr_mtl, mtl_name=mtl_name, mtl_path=mtl_path
    )
    ground_mat_prim = stage.GetPrimAtPath(mtl_path)
    shader = UsdShade.Material(ground_mat_prim).ComputeSurfaceSource("mdl")[0]
    shader.SetSourceAssetSubIdentifier("OmniPBR", "mdl")
    omni.usd.create_material_input(ground_mat_prim, "reflection_roughness_constant", 0.36, Sdf.ValueTypeNames.Float)
    omni.usd.create_material_input(ground_mat_prim, "specular_level", 0.25, Sdf.ValueTypeNames.Float)
    omni.usd.create_material_input(
        ground_mat_prim, "diffuse_color_constant", Gf.Vec3f(0.08, 0.08, 0.08), Sdf.ValueTypeNames.Color3f
    )
    omni.usd.create_material_input(ground_mat_prim, "diffuse_tint", Gf.Vec3f(1, 1, 1), Sdf.ValueTypeNames.Color3f)
    omni.usd.create_material_input(ground_mat_prim, "diffuse_tint", Gf.Vec3f(1, 1, 1), Sdf.ValueTypeNames.Color3f)
    omni.usd.create_material_input(ground_mat_prim, "metallic_constant", 0.0, Sdf.ValueTypeNames.Float)
    omni.usd.create_material_input(ground_mat_prim, "reflection_roughness_constant", 0.36, Sdf.ValueTypeNames.Float)

    # create BackSideMat
    mtl_name = "BackSideMat"
    backside_mtl_path = omni.usd.get_stage_next_free_path(
        stage, "{}/Looks/{}".format(rootname, make_valid_identifier(mtl_name)), False
    )
    omni.kit.commands.execute(
        "CreateMdlMaterialPrim", mtl_url=omni_pbr_mtl, mtl_name=mtl_name, mtl_path=backside_mtl_path
    )
    backside_mtl_prim = stage.GetPrimAtPath(backside_mtl_path)
    shader = UsdShade.Material(backside_mtl_prim).ComputeSurfaceSource("mdl")[0]
    shader.SetSourceAssetSubIdentifier("OmniPBR", "mdl")
    omni.usd.create_material_input(
        backside_mtl_prim,
        "diffuse_color_constant",
        Gf.Vec3f(0.11814344, 0.118142255, 0.118142255),
        Sdf.ValueTypeNames.Color3f,
    )
    omni.usd.create_material_input(backside_mtl_prim, "reflection_roughness_constant", 0.27, Sdf.ValueTypeNames.Float)
    omni.usd.create_material_input(backside_mtl_prim, "specular_level", 0.163, Sdf.ValueTypeNames.Float)

    # create EmissiveMat
    mtl_name = "EmissiveMat"
    emissive_mtl_path = omni.usd.get_stage_next_free_path(
        stage, "{}/Looks/{}".format(rootname, make_valid_identifier(mtl_name)), False
    )
    omni.kit.commands.execute(
        "CreateMdlMaterialPrim", mtl_url=omni_pbr_mtl, mtl_name=mtl_name, mtl_path=emissive_mtl_path
    )
    emissive_mtl_prim = stage.GetPrimAtPath(emissive_mtl_path)
    shader = UsdShade.Material(emissive_mtl_prim).ComputeSurfaceSource("mdl")[0]
    shader.SetSourceAssetSubIdentifier("OmniPBR", "mdl")
    omni.usd.create_material_input(
        emissive_mtl_prim, "diffuse_color_constant", Gf.Vec3f(0, 0, 0), Sdf.ValueTypeNames.Color3f
    )
    omni.usd.create_material_input(emissive_mtl_prim, "reflection_roughness_constant", 1, Sdf.ValueTypeNames.Float)
    omni.usd.create_material_input(emissive_mtl_prim, "specular_level", 0, Sdf.ValueTypeNames.Float)
    omni.usd.create_material_input(emissive_mtl_prim, "enable_emission", True, Sdf.ValueTypeNames.Bool)
    omni.usd.create_material_input(emissive_mtl_prim, "emissive_color", Gf.Vec3f(1, 1, 1), Sdf.ValueTypeNames.Color3f)
    omni.usd.create_material_input(emissive_mtl_prim, "emissive_intensity", 15000, Sdf.ValueTypeNames.Float)

    # create studiohemisphere
    hemisphere_path = omni.usd.get_stage_next_free_path(stage, "{}/studiohemisphere".format(rootname), False)
    omni.kit.commands.execute(
        "CreatePrim", prim_path=hemisphere_path, prim_type="Xform", select_new_prim=False, attributes={}
    )
    hemisphere_prim = stage.GetPrimAtPath(hemisphere_path)
    UsdGeom.PrimvarsAPI(hemisphere_prim).CreatePrimvar("doNotCastShadows", Sdf.ValueTypeNames.Bool).Set(True)
    Usd.ModelAPI(hemisphere_prim).SetKind("group")

    # create sphere
    hemisphere_sphere_path = omni.usd.get_stage_next_free_path(
        stage, "{}/studiohemisphere/Sphere".format(rootname), False
    )
    omni.kit.commands.execute(
        "CreatePrim",
        prim_path=hemisphere_sphere_path,
        prim_type="Sphere",
        select_new_prim=False,
        attributes={UsdGeom.Tokens.radius: 100},
    )
    hemisphere_prim = stage.GetPrimAtPath(hemisphere_sphere_path)
    Usd.ModelAPI(hemisphere_prim).SetKind("assembly")

    # set transform
    hemisphere_prim.CreateAttribute("xformOp:scale", Sdf.ValueTypeNames.Double3, False).Set(Gf.Vec3d(2500, 2500, 2500))
    hemisphere_prim.CreateAttribute("xformOpOrder", Sdf.ValueTypeNames.String, False).Set(["xformOp:scale"])
    UsdGeom.PrimvarsAPI(hemisphere_prim).CreatePrimvar("doNotCastShadows", Sdf.ValueTypeNames.Bool).Set(True)

    # bind material
    omni.kit.commands.execute(
        "BindMaterial",
        prim_path=hemisphere_sphere_path,
        material_path=mtl_path,
        strength=UsdShade.Tokens.strongerThanDescendants,
    )

    # create floor
    hemisphere_floor_path = omni.usd.get_stage_next_free_path(
        stage, "{}/studiohemisphere/Floor".format(rootname), False
    )
    omni.kit.commands.execute(
        "CreatePrim",
        prim_path=hemisphere_floor_path,
        prim_type="Cube",
        select_new_prim=False,
        attributes={UsdGeom.Tokens.size: 100},
    )
    hemisphere_floor_prim = stage.GetPrimAtPath(hemisphere_floor_path)

    # set transform
    hemisphere_floor_prim.CreateAttribute("xformOp:scale", Sdf.ValueTypeNames.Double3, False).Set(
        Gf.Vec3d(2500, 0.1, 2500)
    )
    hemisphere_floor_prim.CreateAttribute("xformOpOrder", Sdf.ValueTypeNames.String, False).Set(["xformOp:scale"])
    UsdGeom.PrimvarsAPI(hemisphere_floor_prim).CreatePrimvar("doNotCastShadows", Sdf.ValueTypeNames.Bool).Set(True)

    # bind material
    omni.kit.commands.execute(
        "BindMaterial",
        prim_path=hemisphere_floor_path,
        material_path=mtl_path,
        strength=UsdShade.Tokens.strongerThanDescendants,
    )

    # create LightPivot_01
    light_pivot1_path = omni.usd.get_stage_next_free_path(stage, "{}/LightPivot_01".format(rootname), False)
    omni.kit.commands.execute(
        "CreatePrim", prim_path=light_pivot1_path, prim_type="Xform", select_new_prim=False, attributes={}
    )
    light_pivot1_prim = stage.GetPrimAtPath(light_pivot1_path)
    UsdGeom.PrimvarsAPI(light_pivot1_prim).CreatePrimvar("doNotCastShadows", Sdf.ValueTypeNames.Bool).Set(True)

    # set transform
    light_pivot1_prim.CreateAttribute("xformOp:translate", Sdf.ValueTypeNames.Double3, False).Set(Gf.Vec3d(0, 0, 0))
    light_pivot1_prim.CreateAttribute("xformOp:rotateZYX", Sdf.ValueTypeNames.Double3, False).Set(
        Gf.Vec3d(-30.453436397207547, 16.954190666353664, 9.728788165428536)
    )
    light_pivot1_prim.CreateAttribute("xformOp:scale", Sdf.ValueTypeNames.Double3, False).Set(
        Gf.Vec3d(0.9999999445969171, 1.000000574567198, 0.9999995086845976)
    )
    light_pivot1_prim.CreateAttribute("xformOpOrder", Sdf.ValueTypeNames.String, False).Set(
        ["xformOp:translate", "xformOp:rotateZYX", "xformOp:scale"]
    )

    # create AreaLight
    light_pivot1_al_path = omni.usd.get_stage_next_free_path(
        stage, "{}/LightPivot_01/AreaLight".format(rootname), False
    )
    omni.kit.commands.execute(
        "CreatePrim", prim_path=light_pivot1_al_path, prim_type="Xform", select_new_prim=False, attributes={}
    )
    light_pivot1_al_prim = stage.GetPrimAtPath(light_pivot1_al_path)
    UsdGeom.PrimvarsAPI(light_pivot1_al_prim).CreatePrimvar("doNotCastShadows", Sdf.ValueTypeNames.Bool).Set(True)

    # set transform
    light_pivot1_al_prim.CreateAttribute("xformOp:translate", Sdf.ValueTypeNames.Double3, False).Set(
        Gf.Vec3d(0, 0, 800)
    )
    light_pivot1_al_prim.CreateAttribute("xformOp:rotateZYX", Sdf.ValueTypeNames.Double3, False).Set(Gf.Vec3d(0, 0, 0))
    light_pivot1_al_prim.CreateAttribute("xformOp:scale", Sdf.ValueTypeNames.Double3, False).Set(
        Gf.Vec3d(4.5, 4.5, 4.5)
    )
    light_pivot1_al_prim.CreateAttribute("xformOpOrder", Sdf.ValueTypeNames.String, False).Set(
        ["xformOp:translate", "xformOp:rotateZYX", "xformOp:scale"]
    )

    # create AreaLight RectLight
    light_pivot1_alrl_path = omni.usd.get_stage_next_free_path(
        stage, "{}/LightPivot_01/AreaLight/RectLight".format(rootname), False
    )
    omni.kit.commands.execute(
        "CreatePrim",
        prim_path=light_pivot1_alrl_path,
        prim_type="RectLight",
        select_new_prim=False,
        attributes={},
    )
    light_pivot1_alrl_prim = stage.GetPrimAtPath(light_pivot1_alrl_path)

    # set values
    # https://github.com/PixarAnimationStudios/USD/commit/b5d3809c943950cd3ff6be0467858a3297df0bb7
    # https://github.com/PixarAnimationStudios/USD/commit/3738719d72e60fb78d1cd18100768a7dda7340a4
    if hasattr(UsdLux.Tokens, 'inputsIntensity'):
        light_pivot1_alrl_prim.CreateAttribute(UsdLux.Tokens.inputsHeight, Sdf.ValueTypeNames.Float, False).Set(100)
        light_pivot1_alrl_prim.CreateAttribute(UsdLux.Tokens.inputsWidth, Sdf.ValueTypeNames.Float, False).Set(100)
        light_pivot1_alrl_prim.CreateAttribute(UsdLux.Tokens.inputsIntensity, Sdf.ValueTypeNames.Float, False).Set(15000)
        light_pivot1_alrl_prim.CreateAttribute(UsdLux.Tokens.inputsShapingConeAngle, Sdf.ValueTypeNames.Float, False).Set(180)
    else:
        light_pivot1_alrl_prim.CreateAttribute(UsdLux.Tokens.height, Sdf.ValueTypeNames.Float, False).Set(100)
        light_pivot1_alrl_prim.CreateAttribute(UsdLux.Tokens.width, Sdf.ValueTypeNames.Float, False).Set(100)
        light_pivot1_alrl_prim.CreateAttribute(UsdLux.Tokens.intensity, Sdf.ValueTypeNames.Float, False).Set(15000)
        light_pivot1_alrl_prim.CreateAttribute(UsdLux.Tokens.shapingConeAngle, Sdf.ValueTypeNames.Float, False).Set(180)

    # create AreaLight Backside
    backside_albs_path = omni.usd.get_stage_next_free_path(
        stage, "{}/LightPivot_01/AreaLight/Backside".format(rootname), False
    )
    omni.kit.commands.execute(
        "CreatePrim",
        prim_path=backside_albs_path,
        prim_type="Cube",
        select_new_prim=False,
        attributes={UsdGeom.Tokens.size: 100, UsdGeom.Tokens.extent: [(-50, -50, -50), (50, 50, 50)]},
    )
    backside_albs_prim = stage.GetPrimAtPath(backside_albs_path)

    # set values
    backside_albs_prim.CreateAttribute("xformOp:translate", Sdf.ValueTypeNames.Double3, False).Set(Gf.Vec3d(0, 0, 1.1))
    backside_albs_prim.CreateAttribute("xformOp:rotateZYX", Sdf.ValueTypeNames.Double3, False).Set(Gf.Vec3d(0, 0, 0))
    backside_albs_prim.CreateAttribute("xformOp:scale", Sdf.ValueTypeNames.Double3, False).Set(Gf.Vec3d(1, 1, 0.02))
    backside_albs_prim.CreateAttribute("xformOpOrder", Sdf.ValueTypeNames.String, False).Set(
        ["xformOp:translate", "xformOp:rotateZYX", "xformOp:scale"]
    )
    UsdGeom.PrimvarsAPI(backside_albs_prim).CreatePrimvar("doNotCastShadows", Sdf.ValueTypeNames.Bool).Set(True)

    # bind material
    omni.kit.commands.execute(
        "BindMaterial",
        prim_path=backside_albs_path,
        material_path=backside_mtl_path,
        strength=UsdShade.Tokens.strongerThanDescendants,
    )

    # create AreaLight EmissiveSurface
    backside_ales_path = omni.usd.get_stage_next_free_path(
        stage, "{}/LightPivot_01/AreaLight/EmissiveSurface".format(rootname), False
    )
    omni.kit.commands.execute(
        "CreatePrim",
        prim_path=backside_ales_path,
        prim_type="Cube",
        select_new_prim=False,
        attributes={UsdGeom.Tokens.size: 100, UsdGeom.Tokens.extent: [(-50, -50, -50), (50, 50, 50)]},
    )
    backside_ales_prim = stage.GetPrimAtPath(backside_ales_path)

    # set values
    backside_ales_prim.CreateAttribute("xformOp:translate", Sdf.ValueTypeNames.Double3, False).Set(
        Gf.Vec3d(0, 0, 0.002)
    )
    backside_ales_prim.CreateAttribute("xformOp:rotateZYX", Sdf.ValueTypeNames.Double3, False).Set(Gf.Vec3d(0, 0, 0))
    backside_ales_prim.CreateAttribute("xformOp:scale", Sdf.ValueTypeNames.Double3, False).Set(Gf.Vec3d(1, 1, 0.02))
    backside_ales_prim.CreateAttribute("xformOpOrder", Sdf.ValueTypeNames.String, False).Set(
        ["xformOp:translate", "xformOp:rotateZYX", "xformOp:scale"]
    )
    UsdGeom.PrimvarsAPI(backside_ales_prim).CreatePrimvar("doNotCastShadows", Sdf.ValueTypeNames.Bool).Set(True)

    # bind material
    omni.kit.commands.execute(
        "BindMaterial",
        prim_path=backside_ales_path,
        material_path=emissive_mtl_path,
        strength=UsdShade.Tokens.strongerThanDescendants,
    )

    # create LightPivot_02
    light_pivot2_path = omni.usd.get_stage_next_free_path(stage, "{}/LightPivot_02".format(rootname), False)
    omni.kit.commands.execute(
        "CreatePrim", prim_path=light_pivot2_path, prim_type="Xform", select_new_prim=False, attributes={}
    )
    light_pivot2_prim = stage.GetPrimAtPath(light_pivot2_path)
    UsdGeom.PrimvarsAPI(light_pivot2_prim).CreatePrimvar("doNotCastShadows", Sdf.ValueTypeNames.Bool).Set(True)

    # set transform
    light_pivot2_prim.CreateAttribute("xformOp:translate", Sdf.ValueTypeNames.Double3, False).Set(Gf.Vec3d(0, 0, 0))
    light_pivot2_prim.CreateAttribute("xformOp:rotateZYX", Sdf.ValueTypeNames.Double3, False).Set(
        Gf.Vec3d(-149.8694695859529, 35.87684189578612, -18.78499937937383)
    )
    light_pivot2_prim.CreateAttribute("xformOp:scale", Sdf.ValueTypeNames.Double3, False).Set(
        Gf.Vec3d(0.9999999347425043, 0.9999995656418647, 1.0000001493100235)
    )
    light_pivot2_prim.CreateAttribute("xformOpOrder", Sdf.ValueTypeNames.String, False).Set(
        ["xformOp:translate", "xformOp:rotateZYX", "xformOp:scale"]
    )

    # create AreaLight
    light_pivot2_al_path = omni.usd.get_stage_next_free_path(
        stage, "{}/LightPivot_02/AreaLight".format(rootname), False
    )
    omni.kit.commands.execute(
        "CreatePrim", prim_path=light_pivot2_al_path, prim_type="Xform", select_new_prim=False, attributes={}
    )
    light_pivot2_al_prim = stage.GetPrimAtPath(light_pivot2_al_path)
    UsdGeom.PrimvarsAPI(light_pivot2_al_prim).CreatePrimvar("doNotCastShadows", Sdf.ValueTypeNames.Bool).Set(True)

    # set transform
    light_pivot2_al_prim.CreateAttribute("xformOp:translate", Sdf.ValueTypeNames.Double3, False).Set(
        Gf.Vec3d(0, 0, 800)
    )
    light_pivot2_al_prim.CreateAttribute("xformOp:rotateZYX", Sdf.ValueTypeNames.Double3, False).Set(Gf.Vec3d(0, 0, 0))
    light_pivot2_al_prim.CreateAttribute("xformOp:scale", Sdf.ValueTypeNames.Double3, False).Set(
        Gf.Vec3d(1.5, 1.5, 1.5)
    )
    light_pivot2_al_prim.CreateAttribute("xformOpOrder", Sdf.ValueTypeNames.String, False).Set(
        ["xformOp:translate", "xformOp:rotateZYX", "xformOp:scale"]
    )

    # create AreaLight RectLight
    light_pivot2_alrl_path = omni.usd.get_stage_next_free_path(
        stage, "{}/LightPivot_02/AreaLight/RectLight".format(rootname), False
    )
    omni.kit.commands.execute(
        "CreatePrim",
        prim_path=light_pivot2_alrl_path,
        prim_type="RectLight",
        select_new_prim=False,
        attributes={},
    )
    light_pivot2_alrl_prim = stage.GetPrimAtPath(light_pivot2_alrl_path)

    # set values
    # https://github.com/PixarAnimationStudios/USD/commit/b5d3809c943950cd3ff6be0467858a3297df0bb7
    # https://github.com/PixarAnimationStudios/USD/commit/3738719d72e60fb78d1cd18100768a7dda7340a4
    if hasattr(UsdLux.Tokens, 'inputsIntensity'):
        light_pivot2_alrl_prim.CreateAttribute(UsdLux.Tokens.inputsHeight, Sdf.ValueTypeNames.Float, False).Set(100)
        light_pivot2_alrl_prim.CreateAttribute(UsdLux.Tokens.inputsWidth, Sdf.ValueTypeNames.Float, False).Set(100)
        light_pivot2_alrl_prim.CreateAttribute(UsdLux.Tokens.inputsIntensity, Sdf.ValueTypeNames.Float, False).Set(55000)
        light_pivot2_alrl_prim.CreateAttribute(UsdLux.Tokens.inputsShapingConeAngle, Sdf.ValueTypeNames.Float, False).Set(180)
    else:
        light_pivot2_alrl_prim.CreateAttribute(UsdLux.Tokens.height, Sdf.ValueTypeNames.Float, False).Set(100)
        light_pivot2_alrl_prim.CreateAttribute(UsdLux.Tokens.width, Sdf.ValueTypeNames.Float, False).Set(100)
        light_pivot2_alrl_prim.CreateAttribute(UsdLux.Tokens.intensity, Sdf.ValueTypeNames.Float, False).Set(55000)
        light_pivot2_alrl_prim.CreateAttribute(UsdLux.Tokens.shapingConeAngle, Sdf.ValueTypeNames.Float, False).Set(180)

    # create AreaLight Backside
    backside_albs_path = omni.usd.get_stage_next_free_path(
        stage, "{}/LightPivot_02/AreaLight/Backside".format(rootname), False
    )
    omni.kit.commands.execute(
        "CreatePrim",
        prim_path=backside_albs_path,
        prim_type="Cube",
        select_new_prim=False,
        attributes={UsdGeom.Tokens.size: 100, UsdGeom.Tokens.extent: [(-50, -50, -50), (50, 50, 50)]},
    )
    backside_albs_prim = stage.GetPrimAtPath(backside_albs_path)

    # set values
    backside_albs_prim.CreateAttribute("xformOp:translate", Sdf.ValueTypeNames.Double3, False).Set(Gf.Vec3d(0, 0, 1.1))
    backside_albs_prim.CreateAttribute("xformOp:rotateZYX", Sdf.ValueTypeNames.Double3, False).Set(Gf.Vec3d(0, 0, 0))
    backside_albs_prim.CreateAttribute("xformOp:scale", Sdf.ValueTypeNames.Double3, False).Set(Gf.Vec3d(1, 1, 0.02))
    backside_albs_prim.CreateAttribute("xformOpOrder", Sdf.ValueTypeNames.String, False).Set(
        ["xformOp:translate", "xformOp:rotateZYX", "xformOp:scale"]
    )
    UsdGeom.PrimvarsAPI(backside_albs_prim).CreatePrimvar("doNotCastShadows", Sdf.ValueTypeNames.Bool).Set(True)

    # bind material
    omni.kit.commands.execute(
        "BindMaterial",
        prim_path=backside_albs_path,
        material_path=backside_mtl_path,
        strength=UsdShade.Tokens.strongerThanDescendants,
    )

    # create AreaLight EmissiveSurface
    backside_ales_path = omni.usd.get_stage_next_free_path(
        stage, "{}/LightPivot_02/AreaLight/EmissiveSurface".format(rootname), False
    )
    omni.kit.commands.execute(
        "CreatePrim",
        prim_path=backside_ales_path,
        prim_type="Cube",
        select_new_prim=False,
        attributes={UsdGeom.Tokens.size: 100, UsdGeom.Tokens.extent: [(-50, -50, -50), (50, 50, 50)]},
    )
    backside_ales_prim = stage.GetPrimAtPath(backside_ales_path)

    # set values
    backside_ales_prim.CreateAttribute("xformOp:translate", Sdf.ValueTypeNames.Double3, False).Set(
        Gf.Vec3d(0, 0, 0.002)
    )
    backside_ales_prim.CreateAttribute("xformOp:rotateZYX", Sdf.ValueTypeNames.Double3, False).Set(Gf.Vec3d(0, 0, 0))
    backside_ales_prim.CreateAttribute("xformOp:scale", Sdf.ValueTypeNames.Double3, False).Set(Gf.Vec3d(1, 1, 0.02))
    backside_ales_prim.CreateAttribute("xformOpOrder", Sdf.ValueTypeNames.String, False).Set(
        ["xformOp:translate", "xformOp:rotateZYX", "xformOp:scale"]
    )
    UsdGeom.PrimvarsAPI(backside_ales_prim).CreatePrimvar("doNotCastShadows", Sdf.ValueTypeNames.Bool).Set(True)

    # bind material
    omni.kit.commands.execute(
        "BindMaterial",
        prim_path=backside_ales_path,
        material_path=emissive_mtl_path,
        strength=UsdShade.Tokens.strongerThanDescendants,
    )
