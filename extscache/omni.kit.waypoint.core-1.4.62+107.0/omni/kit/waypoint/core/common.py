import carb
from pxr import Sdf, Tf

from .style import ICON_PATH

WAYPOINT_ROOT_PRIM_PATH = "/Viewport_Waypoints"
SETTINGS_WAYPOINT_ROOT = "/exts/omni.kit.waypoint.core/"
WAYPOINT_ICON_URL = f"{ICON_PATH}/Waypoint_viewport.png"
CURRENT_TOOL_PATH = "/app/viewport/currentTool"
EXTENSION_NAME = "waypoint"
IGNORE_PRIM_ATTR_NAME = "omni:ignorePrim"


def create_data_only_prim(stage, prim_path: str):
    edit_target = stage.GetEditTarget()
    current_layer = edit_target.GetLayer()

    try:
        with Sdf.ChangeBlock():
            prim_spec = Sdf.CreatePrimInLayer(current_layer, prim_path)
            prim_spec.specifier = Sdf.SpecifierDef
            ignore_prim_attr = Sdf.AttributeSpec(prim_spec, IGNORE_PRIM_ATTR_NAME, Sdf.ValueTypeNames.Bool)
            ignore_prim_attr.specifier = Sdf.SpecifierDef
            ignore_prim_attr.default = True
            ignore_prim_attr.custom = True
    except Tf.ErrorException:
        carb.log_warn(f"create_data_only_prim: AttributeSpec already exists for {prim_path}.{IGNORE_PRIM_ATTR_NAME}")

    prim = stage.GetPrimAtPath(prim_path)
    return prim
