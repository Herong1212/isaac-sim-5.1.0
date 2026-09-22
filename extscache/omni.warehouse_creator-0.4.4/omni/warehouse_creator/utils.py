import asyncio
import os
import typing

import carb
import numpy as np
import omni.client
from omni.client import Result
from pxr import Gf, Kind, Sdf, Tf, Usd, UsdGeom, UsdShade, Vt

# Custom Attributes
WAREHOUSE_X_EXTENT = "warehouse:x_extent"
WAREHOUSE_Y_EXTENT = "warehouse:y_extent"
WAREHOUSE_TILE_DIM = "warehouse:tile_dimension"
WAREHOUSE_SHAPE = "warehouse:matrix_shape"
WAREHOUSE_IDX = "warehouse:idx_positions"

GHOST_COLUMNS_PRIM = "GhostColumns"
GHOST_MAT_NAME = "ghost_material"


def set_pose(prim, position, rot):
    prim.ClearXformOpOrder()
    xform_op_t = prim.AddXformOp(UsdGeom.XformOp.TypeTranslate, UsdGeom.XformOp.PrecisionDouble, "")
    xform_op_r = prim.AddXformOp(UsdGeom.XformOp.TypeRotateXYZ, UsdGeom.XformOp.PrecisionDouble, "")
    # scale = prim.AddXformOp(UsdGeom.XformOp.TypeScale, UsdGeom.XformOp.PrecisionDouble, "")
    # r = Gf.Quatd(*[float(i) for i in quat.tolist()])#quat[1], quat[2], quat[3], quat[0])
    r = Gf.Vec3d(*[float(i) for i in rot])
    pos_vec = Gf.Vec3d(*[float(i) for i in position])
    xform_op_t.Set(pos_vec)
    xform_op_r.Set(r)
    # scale.Set(Gf.Vec3d(1, 1, 1))


def get_extension_folder():
    ext_manager = omni.kit.app.get_app().get_extension_manager()
    ext_id = ext_manager.get_enabled_extension_id("omni.warehouse_creator")
    extension_path = ext_manager.get_extension_path(ext_id)
    return extension_path


def check_server(server: str) -> bool:
    """Check a specific server for a path

    Args:
        server (str): Name of Nucleus server

    Returns:
        bool: True if folder is found
    """
    carb.log_info(f"Checking path: {server}")
    # Increase hang detection timeout
    omni.client.set_hang_detection_time_ms(5000)
    omni.client.set_retries(15000, 100, 100)
    result, _ = omni.client.stat(f"{server}")
    if result == Result.OK:
        carb.log_info(f"Success: {server}")
        return True
    else:
        carb.log_info(f"Failure: {server} not accessible")
        return False


def get_default_asset_path():
    default_asset_root = carb.settings.get_settings().get("/persistent/warehouse_creator/asset_root/default")
    if not default_asset_root:
        return "Default Isaac Sim folder"
    return default_asset_root


def set_default_asset_path(path):
    carb.settings.get_settings().set("/persistent/warehouse_creator/asset_root/default", path)


def validate_asset_path(path, asset_names):
    if check_server(path):
        result, assets = omni.client.list(path)
        list_assets = [a.relative_path for a in assets]

        for asset in asset_names:
            if asset not in list_assets:
                return False
        return True
    return False


def get_assets_root_path() -> typing.Union[str, None]:
    """Tries to find the root path to the Isaac Sim assets on a Nucleus server

    Returns:
        url (str): URL of Nucleus server with root path to assets folder.
        Returns None if Nucleus server not found.
    """
    settings = carb.settings.get_settings()
    default_asset_root = carb.settings.get_settings().get("/persistent/warehouse_creator/asset_root/default")
    cloud_assets_url = carb.settings.get_settings().get("/persistent/warehouse_creator/asset_root/cloud")
    if not cloud_assets_url:
        carb.settings.get_settings().set(
            "/persistent/warehouse_creator/asset_root/cloud",
            "http://omniverse-content-production.s3-us-west-2.amazonaws.com/Assets/Isaac/4.1/Isaac/Environments/Modular_Warehouse/Props/",
        )

    # 1 - Check /persistent/isaac/asset_root/default setting
    carb.log_info("Check /persistent/warehouse_creator/asset_root/default setting")
    default_asset_root = carb.settings.get_settings().get("/persistent/warehouse_creator/asset_root/default")
    if default_asset_root:
        result = check_server(default_asset_root)
        if result:
            carb.log_info("Assets root found at {}".format(default_asset_root))
            return default_asset_root

    # 2 - Check cloud for /Assets/Isaac/{version_major}.{version_minor} folder
    cloud_assets_url = carb.settings.get_settings().get("/persistent/warehouse_creator/asset_root/cloud")
    carb.log_info("Checking {}...".format(cloud_assets_url))
    if cloud_assets_url:
        result = check_server(cloud_assets_url)
        if result:
            carb.log_info("Assets root found at {}".format(cloud_assets_url))
            return cloud_assets_url

    carb.log_warn("Could not find assets root folder")
    return None


def get_warehouse_matrix(warehouse_prim):
    shape = warehouse_prim.GetAttribute(WAREHOUSE_SHAPE).Get()
    mtx = np.full(shape, None)
    children = [c for c in warehouse_prim.GetChildren() if omni.usd.get_composed_references_from_prim(c)]
    for prim in children:
        path = prim.GetPath()
        idxs = prim.GetAttribute(WAREHOUSE_IDX)
        if idxs:
            for idx in idxs.Get():
                mtx[idx[0], idx[1]] = path
    return mtx


def get_column_map(warehouse_prim):
    warehouse_matrix = get_warehouse_matrix(warehouse_prim)
    stage = warehouse_prim.GetStage()
    session_layer = stage.GetSessionLayer()
    tile_size = warehouse_prim.GetAttribute(WAREHOUSE_TILE_DIM).Get()
    children = [c for c in warehouse_prim.GetChildren() if omni.usd.get_composed_references_from_prim(c)]
    column_map = {}  # key : column absolute position index; values: list of column prims
    column_selection = {}

    with Sdf.ChangeBlock():
        with Usd.EditContext(stage, stage.GetRootLayer()):
            for child in warehouse_prim.GetChildren():
                columnvariantsets = [a for a in child.GetVariantSets().GetNames() if "Column" in a]
                column_selection[child] = {
                    a: a.GetVariantSelection() for a in [child.GetVariantSet(s) for s in columnvariantsets]
                }
                for a in columnvariantsets:
                    vset = child.GetVariantSet(a)
                    vset.ClearVariantSelection()
    for prim in children:
        transform = omni.usd
        for p in [p for p in prim.GetChildren() if "column" in p.GetName()]:
            idx = get_column_index(p, tile_size)
            if idx in column_map:
                column_map[idx].append(p.GetPath())
            else:
                column_map[idx] = [p.GetPath()]
    with Sdf.ChangeBlock():
        with Usd.EditContext(stage, stage.GetRootLayer()):
            for child in warehouse_prim.GetChildren():
                for vset in column_selection[child]:
                    # print(child, vset, column_selection[child][vset])
                    vset.SetVariantSelection(column_selection[child][vset])
    return column_map


def get_column_index(column_prim, tile_size):
    parent_block = column_prim.GetParent()
    warehouse_prim = parent_block.GetParent()
    x_min = warehouse_prim.GetAttribute(WAREHOUSE_X_EXTENT).Get()[0]
    y_min = warehouse_prim.GetAttribute(WAREHOUSE_Y_EXTENT).Get()[0]
    column_pose = omni.usd.get_world_transform_matrix(column_prim)
    warehouse_origin = omni.usd.get_world_transform_matrix(warehouse_prim)
    column_position = (warehouse_origin.GetInverse() * column_pose).ExtractTranslation() - Gf.Vec3d(x_min, y_min, 0)
    # column_position = column_pose.ExtractTranslation()
    # absolute_column_pose = block_rotate.TransformDir(column_position)
    column_offset = Gf.Vec2i(int(round(column_position[0])), int(round(column_position[1]))) / tile_size
    return column_offset


def get_variant_from_prim_name(column_name):
    return f"Column_{column_name.split('_')[2]}"


def get_ghost_column_status(column_prim):
    shading_material_binding = UsdShade.MaterialBindingAPI(column_prim)
    bound_material = shading_material_binding.GetDirectBindingRel().GetTargets()
    return not bool(bound_material)


def toggle_ghost_column(column_prims, value=None):
    stage = column_prims[0].GetStage()
    material = stage.GetPrimAtPath(column_prims[0].GetParent().GetPath().AppendPath(GHOST_MAT_NAME))
    with Sdf.ChangeBlock():
        with Usd.EditContext(stage, stage.GetSessionLayer()):
            for column_prim in column_prims:
                shading_material_binding = UsdShade.MaterialBindingAPI(column_prim)
                c_value = value
                if value is None:
                    bound_material = shading_material_binding.GetDirectBindingRel().GetTargets()
                    c_value = bool(bound_material)
                # print(bound_material, c_value)

                if not c_value:
                    shading_material_binding.Bind(
                        UsdShade.Material(material),
                        UsdShade.Tokens.strongerThanDescendants,
                    )
                else:
                    shading_material_binding.GetDirectBindingRel().ClearTargets(True)


def make_ghost_columns(warehouse_prim):
    mtl_path = os.path.join(get_extension_folder(), "data/GhostVolumetric.mdl")
    # print(mtl_path)
    stage = warehouse_prim.GetStage()
    session_layer = stage.GetSessionLayer()
    column_selection = {}

    with Sdf.ChangeBlock():
        with Usd.EditContext(stage, stage.GetRootLayer()):
            for child in warehouse_prim.GetChildren():
                columnvariantsets = [a for a in child.GetVariantSets().GetNames() if "Column" in a]
                column_selection[child] = {
                    a.GetName(): a.GetVariantSelection() for a in [child.GetVariantSet(s) for s in columnvariantsets]
                }

    c_map = get_column_map(warehouse_prim)
    asyncio.ensure_future(omni.kit.app.get_app().next_update_async())
    with Usd.EditContext(stage, session_layer):
        ghost_columns_prim = stage.DefinePrim(f"/{warehouse_prim.GetName()}_{GHOST_COLUMNS_PRIM}", "Xform")
        transform = omni.usd.get_world_transform_matrix(warehouse_prim)
        omni.usd.editor.set_hide_in_stage_window(ghost_columns_prim, True)
        material = omni.kit.commands.execute(
            "CreateMdlMaterialPrim",
            mtl_url=mtl_path,
            mtl_name="voltest_02",
            mtl_path=Sdf.Path(ghost_columns_prim.GetPath()).AppendPath(GHOST_MAT_NAME),
        )
        shader_prim = stage.GetPrimAtPath(
            Sdf.Path(ghost_columns_prim.GetPath()).AppendPath(GHOST_MAT_NAME).AppendPath("Shader")
        )
        shader_prim.CreateAttribute("inputs:absorption", Sdf.ValueTypeNames.Color3f).Set(Gf.Vec3f(0.8, 0.8, 0.8))
        shader_prim.CreateAttribute("inputs:scattering", Sdf.ValueTypeNames.Color3f).Set(Gf.Vec3f(0.5, 0.5, 0.5))
        shader_prim.CreateAttribute("inputs:distance_scale", Sdf.ValueTypeNames.Float).Set(1.0)
        shader_prim.CreateAttribute("inputs:emissive_scale", Sdf.ValueTypeNames.Float).Set(300.0)
        shader_prim.CreateAttribute("inputs:transmission_color", Sdf.ValueTypeNames.Color3f).Set(
            Gf.Vec3f(0.2, 0.8, 0.3)
        )
        for c in c_map:
            c_prim = stage.DefinePrim(ghost_columns_prim.GetPath().AppendPath(Tf.MakeValidIdentifier(str(c))), "Xform")
            model_api = Usd.ModelAPI(c_prim)
            model_api.SetKind(Kind.Tokens.component)
            enabled = False

            for column in c_map[c]:
                parent = stage.GetPrimAtPath(column).GetParent()
                enabled = (
                    enabled
                    or parent.GetVariantSet(get_variant_from_prim_name(column.name)).GetVariantSelection() != "Disabled"
                )

            for column in c_map[c]:
                parent = stage.GetPrimAtPath(column).GetParent()
                # column_prim = stage.DefinePrim(ghost_columns_prim.GetPath().Append(column.GetName()), "Xform")
                new_column_path = omni.usd.get_stage_next_free_path(
                    stage, c_prim.GetPath().AppendPath(column.name), False
                )
                ret = omni.kit.commands.execute("CopyPrimSelect", path_from=column, path_to=new_column_path)
                ghost_prim = stage.GetPrimAtPath(new_column_path)

                t = omni.usd.get_world_transform_matrix(stage.GetPrimAtPath(column))
                # t = column_global_pose
                set_pose(
                    UsdGeom.Xformable(ghost_prim),
                    t.ExtractTranslation(),
                    t.ExtractRotation().Decompose(Gf.Vec3d(1, 0, 0), Gf.Vec3d(0, 1, 0), Gf.Vec3d(0, 0, 1)),
                )
                vset = parent.GetVariantSet(get_variant_from_prim_name(column.name))
                # print(column_selection[parent])
                if (
                    enabled and column_selection[parent][vset.GetName()] == "Disabled"
                ):  # in column_selection[parent].values():
                    # print("reset disabled", parent, vset)
                    with Usd.EditContext(stage, stage.GetRootLayer()):
                        vset.ClearVariantSelection()  # If any portion of the column is not disabled, enable it all
            if not enabled:
                UsdShade.MaterialBindingAPI(c_prim).Bind(
                    UsdShade.Material(shader_prim.GetParent()),
                    UsdShade.Tokens.strongerThanDescendants,
                )

    # session_layer.subLayerPaths.remove(layer.identifier)
    # layer = None
    return ghost_columns_prim, c_map
