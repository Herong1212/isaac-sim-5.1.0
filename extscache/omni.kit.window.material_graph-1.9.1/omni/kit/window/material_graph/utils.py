import omni.kit.app
from pxr import Sdr, Usd, UsdShade

# ToDo populate from Sdr
USD_PREVIEW_SURFACE_SHADERS = [
    "UsdPreviewSurface",
    "UsdPrimvarReader_int",
    "UsdPrimvarReader_float",
    "UsdPrimvarReader_float2",
    "UsdPrimvarReader_float3",
    "UsdPrimvarReader_float4",
    "UsdPrimvarReader_matrix",
    "UsdPrimvarReader_normal",
    "UsdPrimvarReader_point",
    "UsdPrimvarReader_string",
    "UsdPrimvarReader_vector",
    "UsdTransform2d",
    "UsdUVTexture",
]


def isUsdPreviewSurfaceShader(prim: Usd.Prim):
    shader = UsdShade.Shader(prim)
    shader_id = shader.GetShaderId()
    return shader_id and shader_id in USD_PREVIEW_SURFACE_SHADERS


def can_connect(model, source_attr: Usd.Attribute, target_attr: Usd.Attribute):
    """Return if it's possible to connect source_attr to target_attr"""
    COMPATIBILITY = {
        "bool": ["int", "float", "double"],
        "color3f": ["double3", "float3", "normal3f", "point3f", "vector3f"],
        "double3": ["color3f", "float3", "normal3f", "point3f", "vector3f"],
        "float": ["double"],
        "float3": ["color3f", "double3", "normal3f", "point3f", "vector3f"],
        "int": ["float", "double"],
        "int2": ["float2", "double2"],
        "int3": ["float3", "double3"],
        "normal3f": ["color3f", "double3", "float3", "point3f", "vector3f"],
        "point3f": ["color3f", "double3", "float3", "normal3f", "vector3f"],
        "texture_return": ["::base::texture_return"],
        "token": ["material"],
        "vector3f": ["color3f", "double3", "float3", "normal3f", "point3f"],
    }

    def get_upstream_nodes(prim: Usd.Prim):
        nodes = [prim]

        api = UsdShade.ConnectableAPI(prim)
        if api:
            for usdshade_input in api.GetInputs():
                for connected_source in api.GetConnectedSources(usdshade_input):
                    if connected_source:
                        nodes.extend(get_upstream_nodes(connected_source[0].source))

        return nodes

    def get_prim_from_attr(attr: Usd.Attribute):
        """Recursively attempt to find the underlying UsdShade.Shader or UsdShade.Material
        # prim that 'defines' the type of this attribute."""
        prim = attr.GetPrim()

        if prim.IsA(UsdShade.Shader) or prim.IsA(UsdShade.Material):
            return prim

        # prim is a UsdShade.Nodegraph
        attr_name = attr.GetName()

        if attr_name.startswith(UsdShade.Tokens.inputs):
            usdshade_nodegraph = UsdShade.NodeGraph(prim)
            iface_input_map = usdshade_nodegraph.ComputeInterfaceInputConsumersMap()

            for usdshade_input, connected_inputs in iface_input_map.items():
                if usdshade_input.GetFullName() == attr_name:
                    if connected_inputs:
                        return get_prim_from_attr(connected_inputs[0].GetAttr())
                    break

        else:
            usdshade_output = UsdShade.Output(attr)
            for value_attr in usdshade_output.GetValueProducingAttributes():
                return get_prim_from_attr(value_attr)

        # UsdShade.Nodegraph attribute is not connected, so return
        # the UsdShade.Nodegraph prim
        return prim

    source_prim = get_prim_from_attr(source_attr)
    if not source_prim:
        return False

    target_prim = get_prim_from_attr(target_attr)
    if not target_prim:
        return False

    source_path = source_prim.GetPath()
    target_path = target_prim.GetPath()

    # Allow connection if one of the following is true
    #   1. target is parent and a UsdShade.NodeGraph
    #   2. target is not in upstream nodes
    if (
        source_path.GetParentPath() == target_path and target_prim.IsA(UsdShade.NodeGraph)
    ) or target_prim not in get_upstream_nodes(source_prim):
        check_types = False
        prims_are_preview_surface = False

        if target_prim.IsA(UsdShade.Material):
            check_types = True

        elif source_prim.IsA(UsdShade.NodeGraph):
            check_types = True

        elif target_prim.IsA(UsdShade.NodeGraph):
            check_types = True

        else:
            source_is_ps = isUsdPreviewSurfaceShader(source_prim)
            target_is_ps = isUsdPreviewSurfaceShader(target_prim)
            check_types = source_is_ps == target_is_ps
            prims_are_preview_surface = source_is_ps and target_is_ps

        if not check_types:
            return False

        source_type = str(model[source_attr].type)
        target_type = str(model[target_attr].type)

        if source_type == target_type:
            return True

        app = omni.kit.app.acquire_app_interface()

        # auto type conversion added in Kit 105.1
        app_gt_105 = float(app.get_kit_version_short()) > 105

        # ToDo: hardcode the following into the COMPATIBILITY decleration above one 105.0 is
        # released.
        # hack: if both nodes are UsdPreviewSurface shaders augment the lookup table
        # to add "color" type.
        # Note: this works because in the Hydra delegate we use a special version
        # of UsdPreviewSurface, NvUsdPreviewSurface that replaces the color params with float3.
        if app_gt_105 or prims_are_preview_surface:
            for t in ["color3f", "float3", "normal3f", "point3f", "vector3f"]:
                COMPATIBILITY[t].append("color")

            COMPATIBILITY["color"] = ["float3", "normal3f", "point3f", "vector3f"]

        return target_type in COMPATIBILITY.get(source_type, [])

    return False
