# Copyright (c) 2018-2024, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
import typing
import asyncio
import functools
import re
import carb
from carb.eventdispatcher import get_eventdispatcher
from omni.kit.async_engine import run_coroutine
import omni.usd
from .._usd import WRITABLE_USD_FILE_EXTS_STR, get_context_from_stage_id
import weakref
from pxr import Usd, Tf, Sdf, Gf, UsdShade, UsdGeom, UsdLux, Trace, UsdUtils
from typing import Callable, Union, Tuple, List, Any, Optional


_writable_usd_file_exts = tuple(WRITABLE_USD_FILE_EXTS_STR.split("|"))
_writable_usd_dotted_file_exts = tuple("." + x for x in _writable_usd_file_exts)
_writable_usd_files_desc = "USD Files ({})".format(";".join("*" + x for x in _writable_usd_dotted_file_exts))
_writable_usd_re = re.compile(rf"^[^?]*\.({WRITABLE_USD_FILE_EXTS_STR})(\?.*)?$", re.IGNORECASE)


_readable_usd_file_exts_str = None
_readable_usd_file_exts = None
_readable_usd_dotted_file_exts = None
_readable_usd_files_desc = None
_readable_usd_re = None


# Note - the writableUsd* members are functions just for symmetry with the
#        readableUsd* members
def writable_usd_file_exts_str() -> str:
    """Gets a string that includes all writable USD file formats supported by Kit.

    Returns:
        str: A string includes all file extensions of writable usd formats, and is separated by "|", like "usd|usda|usdc|live".
    """

    return WRITABLE_USD_FILE_EXTS_STR


def writable_usd_file_exts() -> List[str]:
    """Gets a list of file extensions (without dots) about writable USD formats.

    Returns:
        List[str]: A list of file extensions (without dots), like ('usd', 'usda', 'usdc', 'live').
    """

    return _writable_usd_file_exts


def writable_usd_dotted_file_exts() -> List[str]:
    """Gets a list of file extensions about writable USD formats.

    Returns:
        List[str]: A list of file extensions, like ('usd', 'usda', 'usdc', 'live').
    """

    return _writable_usd_dotted_file_exts


def writable_usd_files_desc() -> str:
    """Gets a description of all writable USD file formats.

    Returns:
        str: A description string, like "USD Files (*.usd;*.usda;*.usdc;*.live)
    """

    return _writable_usd_files_desc


def writable_usd_re() -> re.Pattern:
    """Gets the regex that matches writable USD files.

    Returns:
        re.Pattern: A compiled regex.
    """

    return _writable_usd_re


# These need to be functions so that querying of FileFormatRegistry is delayed -
# currently, it is baked on first use, so we want to give omniverse extensions
# a chance to load


def _bake_readable_usd_file_info():
    global _readable_usd_file_exts_str
    global _readable_usd_file_exts
    global _readable_usd_dotted_file_exts
    global _readable_usd_files_desc
    global _readable_usd_re

    if _readable_usd_file_exts is not None:
        return

    # restrict to file formats whose target is "usd", since that's what
    # Usd.Stage.IsSupportedFile uses
    all_supported_extensions = []
    for ext in Sdf.FileFormat.FindAllFileFormatExtensions():
        try:
            # It's possible that file format plugin is not configured correctly.
            # Or the extension startup is ignored that causes file format extenion is not
            # correctly initialized. For example, omni.usd_resolver.
            if Sdf.FileFormat.FindByExtension(ext, "usd"):
                all_supported_extensions.append(ext)
        except Exception:
            pass

    _readable_usd_file_exts = tuple(all_supported_extensions)
    _readable_usd_file_exts_str = "|".join(_readable_usd_file_exts)
    _readable_usd_dotted_file_exts = tuple("." + x for x in _readable_usd_file_exts)
    _readable_usd_files_desc = "USD Readable Files ({})".format(
        ";".join("*" + x for x in _readable_usd_dotted_file_exts)
    )
    _readable_usd_re = re.compile(rf"^[^?]*\.({_readable_usd_file_exts_str})(\?.*)?$", re.IGNORECASE)


def readable_usd_file_exts_str() -> str:
    """Gets a string that includes all readable USD file formats supported by Kit.

    Returns:
        str: A string includes all file extensions of readable USD formats, and is separated by "|", like "usd|usda|usdc|live".
    """

    _bake_readable_usd_file_info()
    return _readable_usd_file_exts_str


def readable_usd_file_exts() -> List[str]:
    """Gets a list of file extensions (without dots) about readable USD formats.

    Returns:
        List[str]: A list of file extensions (without dots), like ('usd', 'usda', 'usdc', 'live').
    """

    _bake_readable_usd_file_info()
    return _readable_usd_file_exts


def readable_usd_dotted_file_exts() -> List[str]:
    """Gets a list of file extensions about readable USD formats.

    Returns:
        List[str]: A list of file extensions, like ('usd', 'usda', 'usdc', 'live').
    """

    _bake_readable_usd_file_info()
    return _readable_usd_dotted_file_exts


def readable_usd_files_desc() -> str:
    """Gets a description of all readable USD file formats.

    Returns:
        str: A description string, like "USD Files (*.usd;*.usda;*.usdc;*.live)
    """

    _bake_readable_usd_file_info()
    return _readable_usd_files_desc


def readable_usd_re() -> re.Pattern:
    """Gets the regex that matches readable USD files.

    Returns:
        re.Pattern: A compiled regex.
    """

    _bake_readable_usd_file_info()
    return _readable_usd_re


def is_usd_writable_filetype(filepath: str) -> bool:
    """Whether the given file path is a supported writable USD file or not."""
    if not filepath:
        return False

    return bool(writable_usd_re().match(filepath))


def is_usd_readable_filetype(filepath: str) -> bool:
    """Whether the given file path is a supported readable USD file or not."""

    if not filepath:
        return False

    url = omni.client.break_url(filepath)
    if not url or not url.path:
        return False

    return Usd.Stage.IsSupportedFile(url.path)


def is_usd_crate_file(filepath: str) -> bool:
    """Whether the given file path is using USD crate file format or not."""
    if not filepath:
        return False

    if Sdf.FileFormat.GetFileExtension(filepath) not in ("usdc", "usd"):
        return False

    # If the file ext is .usd but the underlying format is .usda, it's not a crate file
    usda_ext = Sdf.FileFormat.FindByExtension(".usda")
    try:
        return not usda_ext.CanRead(filepath)
    except Tf.ErrorException:
        # We can't use Sdf.FileFormat.FindByExtension(".usdc") here due to the Crate File versioning.
        # If we try Sdf.FileFormat.FindByExtension(".usdc").CanRead(filepath) and filepath is a newer
        # Crate File version the result would be incorrectly false. So here we at least make sure that 
        # filepath can not be read by the USDA File Format
        return True


def is_usd_crate_file_version_supported(filepath: str, stage = None, usd_context_name: str = "") -> bool:
    """
    Whether the current USD crate file version is supported or not.

    Returns:
        bool: True if the crate file version is supported or the file is not a crate file, False otherwise.
    """
    # OMPE-46871: Need to check crate file info after asset path resolution. This needs to be done before
    # checking file extension because asset path file extension could have changed after asset resolve.
    from pxr import Ar

    if not stage:
        usd_context = omni.usd.get_context(usd_context_name)
        stage = usd_context.get_stage() if usd_context else None

    resolver = Ar.GetResolver()
    if stage:
        with Ar.ResolverContextBinder(stage.GetPathResolverContext()):
            resolved_path = resolver.Resolve(resolver.CreateIdentifier(filepath))
    else:
        resolved_path = resolver.Resolve(resolver.CreateIdentifier(filepath))

    if isinstance(resolved_path, Ar.ResolvedPath) and not resolved_path.GetPathString():
        # If the asset path is not resolved, use the original filepath to check crate file info.
        carb.log_warn(f"Failed to resolve asset path {filepath}, using the original filepath to check crate file info.")
        resolved_path = filepath

    if not is_usd_crate_file(resolved_path):
        return True

    # Get crate file info
    try:
        Usd.CrateInfo.Open(resolved_path)
    except Tf.ErrorException as e:
        comment = e.args[0].commentary
        # Use regex to find the file version number if we encounter an error with mismatch
        # We can't extract the version for the current stage file using UsdCrateInfo::GetFileVersion()
        # because when we have a version mismatch we can't have a valid UsdCrateInfo instance thus
        # we are not able to query that;
        if 'Usd crate file version mismatch' in comment:
            match = re.search(r'Usd crate file version mismatch -- file is (\d+\.\d+\.\d+)', comment)
            if match:
                crate_version = match.group(1)
                supported_version = Usd.CrateInfo.GetSoftwareVersion(Usd.CrateInfo())
                carb.log_error(
                    f"Error: Crate file {resolved_path} is not supported.\nThe current OpenUSD run-time does not support usd crate file "
                    f"version {crate_version}, please re-save the file to crate version lower than {supported_version}.\n"
                    f"To update, you can set the environment variable USD_WRITE_NEW_USDC_FILES_AS_VERSION to {supported_version}, "
                    f"note that this only applies to new files being saved.")
        else:
            carb.log_error(f"Failed to open crate file {resolved_path}: {str(e)}")
        return False
    else:
        return True


def __get_stage(usd_context_or_stage: Union[str, Usd.Stage] = ""):
    if isinstance(usd_context_or_stage, omni.usd.UsdContext):
        stage = usd_context_or_stage.GetStage()
    elif isinstance(usd_context_or_stage, Usd.Stage):
        stage = usd_context_or_stage
    else:
        if not usd_context_or_stage:
            usd_context_or_stage = ""
        stage = omni.usd.get_context(usd_context_or_stage).get_stage()

    return stage


def get_prim_at_path(path: Sdf.Path, usd_context_name: Union[str, Usd.Stage] = "") -> Usd.Prim:
    """Internal. Gets prim at specific path."""

    path = Sdf.Path(path)
    stage = __get_stage(usd_context_name)
    if stage:
        return stage.GetPrimAtPath(path.GetPrimPath())
    return None


def get_prop_at_path(path: Sdf.Path, usd_context_name: Union[str, Usd.Stage] = "") -> Usd.Property:
    """Internal. Gets property at specific path."""

    path = Sdf.Path(path)
    prim = get_prim_at_path(path, usd_context_name)
    if prim:
        return prim.GetProperty(path.name)
    return None


@carb.profiler.profile
def find_spec_on_session_or_its_sublayers(
    stage: Usd.Stage, path: Sdf.Path, predicate: Callable[[Sdf.Spec], bool] = None
):
    """
    Finds spec in the session layer or its sublayers.

    Args:
        stage (Usd.Stage): Stage instance.
        path (Sdf.Path): Spec path to find.
        predicate (Callable[[Sdf.Spec], bool]): If it's provided, the spec to find must pass the predicate.

    Returns:
        (Sdf.Layer, Sdf.Spec): Layer that the spec resides in, and the spec handle. Or (None, None) if it cannot be found.
    """

    def get_spec(layer: Sdf.Layer, path: Sdf.Path):
        spec = layer.GetObjectAtPath(path)
        if spec and (predicate is None or predicate(spec)):
            return spec

        return None

    layer_stack = stage.GetLayerStack(True)
    root_layer = stage.GetRootLayer()

    for i in range(len(layer_stack)):
        layer = layer_stack[i]

        # session layers always come before root layer. We're only interested in session and its sublayers, break when hit root layer.
        if layer == root_layer:
            break

        spec = get_spec(layer, path)
        if spec:
            return layer, spec

    return None, None


def set_prop_val(
    prop: Usd.Property, val: typing.Any,
    time_code=Usd.TimeCode.Default(),
    auto_target_layer: bool = True
):
    """
    Sets the value of property.

    Args:
        prop (Usd.Property): Property handle.
        val (typing.Any): Value of property.
        time_code (Usd.TimeCode): Time code to set, and it's Usd.TimeCode.Default() by default.
        auto_target_layer (bool): Default is True. If it's true, it will be authored into the sesison layer if
            the prim of the property is defined in the session layer. If it's not defined in the session layer,
            it will find the property inside the session layer to check if there are overrides.
            If overrides are found, the value will be authored into the found layer instead.
            Otherwise, it will be authored into the current edit target.
    """

    stage = prop.GetStage()

    if auto_target_layer:
        # If the prim of the property is defined inside session layer, edits should go to session layer always.
        session_layer, _ = omni.usd.find_spec_on_session_or_its_sublayers(
            stage, prop.GetPath().GetPrimPath(), lambda spec: spec.specifier == Sdf.SpecifierDef
        )

        if not session_layer:
            # if the property exists on session layer, switch EditTarget to session layer instead
            session_layer, _ = find_spec_on_session_or_its_sublayers(stage, prop.GetPath())

        if session_layer:
            edit_target = stage.GetEditTargetForLocalLayer(session_layer)
            with Usd.EditContext(stage, edit_target):
                _set_prop_val(prop, val, time_code)
        else:
            _set_prop_val(prop, val, time_code)
    else:
        _set_prop_val(prop, val, time_code)


def set_attr_val(
    attr: Usd.Attribute, val: typing.Any, time_code=Usd.TimeCode.Default(), auto_target_layer: bool = True
):
    """
    Deprecated. See :func:`.set_prop_val` instead.
    """

    set_prop_val(attr, val, time_code, auto_target_layer)


def clear_attr_val_at_time(attr: Usd.Attribute, time_code=Usd.TimeCode.Default(), auto_target_layer: bool = True):
    """Clears attribute at specified timecode.

    Args:
        attr (Usd.Attribute): Attribute handle.
        time_code (_type_, optional): specified timecode. Defaults to Usd.TimeCode.Default().
        auto_target_layer (bool, optional): When it's True and the property exists in session layer or its sublayers,
            it will switch EditTarget to the session layer instead to clear the strongest opinion. Defaults to True.
    """

    stage = attr.GetStage()

    if auto_target_layer:
        # if the property exists on session layer, switch EditTarget to session layer instead
        session_layer, attr_spec = find_spec_on_session_or_its_sublayers(stage, attr.GetPath())
        if attr_spec:
            with Usd.EditContext(stage, session_layer):
                attr.ClearAtTime(time_code)
        else:
            new_target = stage.GetEditTargetForLocalLayer(stage.GetEditTarget().GetLayer())
            with Usd.EditContext(stage, new_target):
                attr.ClearAtTime(time_code)
    else:
        attr.ClearAtTime(time_code)

def get_prop_auto_target_session_layer(stage: Usd.Stage, prop_path: Sdf.Path):
    """
    Get property auto retarget layer.

    Args:
        stage (Usd.Stage): Usd stage
        prop_path (Sdf.Path): property path
    """

    if stage is None:
        return None, False

    # if the property exists on session layer, return this session layer
    session_layer, _ = omni.usd.find_spec_on_session_or_its_sublayers(stage, prop_path)

    if not session_layer:
        # Next check if the prim of the property is defined inside session layer
        session_layer, _ = omni.usd.find_spec_on_session_or_its_sublayers(
            stage, prop_path.GetPrimPath(), lambda spec: spec.specifier == Sdf.SpecifierDef
        )

    return session_layer



def is_path_valid(path: Union[str, Sdf.Path]):
    """Internal. If the path points to a valid USD object in the default UsdContext."""

    path = Sdf.Path(path)
    return (
        bool(omni.usd.get_context().get_stage().GetPrimAtPath(path))
        if path.GetPrimPath() == path
        else bool(omni.usd.get_prop_at_path(path))
    )


@Trace.TraceFunction
def is_hidden_type(prim: Usd.Prim):
    """Internal. If prim or its parent has metadata "hide_in_stage_window" authored. """

    while not prim.IsPseudoRoot():
        if prim.GetMetadata("hide_in_stage_window"):
            return True
        prim = prim.GetParent()
    return False


@Trace.TraceFunction
def is_child_type(prim, type):  # pragma: no cover
    """Internal. If prim has specific type of children."""

    for child in prim.GetAllChildren():
        if child.IsA(type):
            return True
        if omni.usd.is_child_type(child, type):
            return True

    return False


@Trace.TraceFunction
def is_ancestor_prim_type(stage: Usd.Stage, prim_path: Sdf.Path, prim_type: Usd.SchemaBase):
    """Internal. If any parent prims of the prim are specific type."""

    # are any parent prims in prim_path type prim_type?
    parent_path = prim_path.GetParentPath()
    while parent_path and parent_path != Sdf.Path.absoluteRootPath:
        parent_prim = stage.GetPrimAtPath(parent_path)
        if parent_prim and parent_prim.IsA(prim_type):
            return True
        parent_path = parent_path.GetParentPath()
    return False


def is_prim_material_supported(prim):
    """Internal. If material can be bound to the prim."""

    if not prim:
        return False

    # DomeLights in the RTX Renderer support baking to texture.
    if prim.IsA(UsdLux.DomeLight):
        return True

    # don't allow materials on light/camera or materials
    # https://github.com/PixarAnimationStudios/USD/commit/7540fdf3b2aa6b6faa0fce8e7b4c72b756286f51
    isLight = prim.HasAPI(UsdLux.LightAPI) if hasattr(UsdLux, 'LightAPI') else prim.IsA(UsdLux.Light)
    if isLight or prim.IsA(UsdGeom.Camera) or prim.IsA(UsdShade.Material):
        return False

    # only Imageable or Subset types
    return prim.IsA(UsdGeom.Gprim) or prim.IsA(UsdGeom.Xform) or prim.IsA(UsdGeom.Subset)


def can_prim_have_children(stage: Usd.Stage, new_path: Sdf.Path, prim: Usd.Prim):
    """Internal. If a prim can have children authored.

    It's recommended from Pixar USD that UsdGeom.Gprim is better to be the leaf node instead of
    having children attached. This function will check if it's a UsdGeom.Gprim or it's already under
    a UsdGeom.Gprim node.

    Args:
        stage (Usd.Stage): The stage of the prim.
        new_path (Sdf.Path): New prim path to create under the parent.
        prim (Usd.Prim): The parent prim.
    """
    # if prim is UsdGeom.Gprim and any parent prims are also UsdGeom.Gprim then return False
    if prim.IsA(UsdGeom.Gprim) and is_ancestor_prim_type(stage, new_path, UsdGeom.Gprim):
        return False

    return True


def _set_prop_val(prop: Usd.Property, val: typing.Any, time_code=Usd.TimeCode.Default()):
    # Add support to set Gf.Matrix4X, Gf.QuatX using python tuple
    prop_type = prop.GetTypeName()
    if prop_type == Sdf.ValueTypeNames.Matrix4d and isinstance(val, tuple):
        prop.Set(Gf.Matrix4d(*val), time_code)
    elif prop_type == Sdf.ValueTypeNames.Quath and isinstance(val, tuple):
        prop.Set(Gf.Quath(*val), time_code)
    elif prop_type == Sdf.ValueTypeNames.Quatf and isinstance(val, tuple):
        prop.Set(Gf.Quatf(*val), time_code)
    elif prop_type == Sdf.ValueTypeNames.Quatd and isinstance(val, tuple):
        prop.Set(Gf.Quatd(*val), time_code)
    elif prop_type == Sdf.ValueTypeNames.Int2 and isinstance(val, tuple):
        prop.Set(Gf.Vec2i(int(val[0]), int(val[1])), time_code)
    else:
        prop.Set(val, time_code)


def remove_property(prim_path: Union[str, Sdf.Path], property_name: str, usd_context_or_stage: Union[str, Usd.Stage] = ""):
    """Removes specified property from the prim.

    Args:
        prim_path (Union[str, Sdf.Path]): Prim path.
        property_name (str): Specified property name.
        usd_context_or_stage (Union[str, Usd.Stage], optional): Stage or UsdContext applies the changes to.
            It can be instance of Usd.Stage or context name. By default, it will apply
            the changes to the stage in default UsdContext.
    """

    prim_path = Sdf.Path(prim_path)
    stage = __get_stage(usd_context_or_stage)

    with Sdf.ChangeBlock():
        for layer in stage.GetLayerStack():
            prim_spec = layer.GetPrimAtPath(prim_path)
            if prim_spec:
                property_spec = layer.GetPropertyAtPath(prim_path.AppendProperty(property_name))
                if property_spec:
                    prim_spec.RemoveProperty(property_spec)


def get_shader_from_material(prim, get_prim=False):
    material = UsdShade.Material(prim)
    shader = material.ComputeSurfaceSource("mdl")[0] if material else None
    if shader and get_prim:
        return shader.GetPrim()
    return shader


async def get_subidentifier_from_material(prim: Usd.Prim, on_complete_fn: typing.Callable = None):  # pragma: no cover
    """Deprecated. Use {py:func}`omni.kit.material.library.get_subidentifier_from_material` instead."""

    carb.log_warn(
        f"omni.usd.get_subidentifier_from_material is deprecated. Use omni.kit.material.library.get_subidentifier_from_material instead"
    )
    if not on_complete_fn or not prim:
        return

    shader = UsdShade.Shader(prim)
    asset = shader.GetSourceAsset("mdl") if shader else None
    mdl_file = asset.resolvedPath if asset else None
    if not mdl_file:
        if on_complete_fn:
            on_complete_fn(None)
        return
    await get_subidentifier_from_mdl(mdl_file, on_complete_fn)


async def get_subidentifier_from_mdl(mdl_file: str, on_complete_fn: typing.Callable = None):  # pragma: no cover
    """Deprecated. Use {py:func}`omni.kit.material.library.get_subidentifier_from_mdl` instead."""

    carb.log_warn(
        f"omni.usd.get_subidentifier_from_mdl is deprecated. Use omni.kit.material.library.get_subidentifier_from_mdl instead"
    )
    if not mdl_file:
        carb.log_error(f"get_subidentifier_from_mdl: Failed to read file {mdl_file}")
        if on_complete_fn:
            on_complete_fn(None)
        return

    result, _, content = await omni.client.read_file_async(mdl_file)
    if result != omni.client.Result.OK:
        carb.log_error(f"get_subidentifier_from_material: Failed to read file {mdl_file}")
        if on_complete_fn:
            on_complete_fn(None)
        return

    re_material_in_mdl = re.compile(r"export\s+material\s+([^\s]+)\s*\(")
    mtl_list = []
    for line in memoryview(content).tobytes().decode("utf-8").splitlines():
        # get material names from MDL file
        for match in re.finditer(re_material_in_mdl, line):
            mtl_list.append(match.group(1))

    if on_complete_fn:
        on_complete_fn(mtl_list)
    return mtl_list


def create_material_input(
    prim: Usd.Prim, name: str, value: Any, vtype: str, def_value: Any = None, min_value: Any = None,
    max_value: Any = None, display_name: str = None, display_group: str = None, color_space: str = None
) -> Usd.Attribute:
    """Creates a material input.

    Args:
        prim (Usd.Prim): Prim handle.
        name (str): Name of the input.
        value (Any): Value of the input.
        vtype (str): Type of the value.
        def_value (Any, optional): Default value. Defaults to None.
        min_value (Any, optional): Min value. Defaults to None.
        max_value (Any, optional): Max value. Defaults to None.
        display_name (str, optional): Display name. Defaults to None.
        display_group (str, optional): Display group. Defaults to None.
        color_space (str, optional): Color space of the input. Defaults to None.

    Returns:
        Usd.Attribute: The created input attribute.
    """

    shader = omni.usd.get_shader_from_material(prim)
    if shader:
        existing_input = shader.GetInput(name)
        if existing_input and existing_input.GetTypeName() != vtype:
            omni.usd.remove_property(shader.GetPrim().GetPath(), existing_input.GetFullName())

        surfaceInput = shader.CreateInput(name, vtype)
        surfaceInput.Set(value)
        attr = surfaceInput.GetAttr()

        if def_value is not None:
            attr.SetCustomDataByKey("default", def_value)
        if min_value is not None:
            attr.SetCustomDataByKey("range:min", min_value)
        if max_value is not None:
            attr.SetCustomDataByKey("range:max", max_value)
        if display_name is not None:
            attr.SetDisplayName(display_name)
        if display_group is not None:
            attr.SetDisplayGroup(display_group)
        if color_space is not None:
            attr.SetColorSpace(color_space)

        return attr

    return None


def get_local_transform_matrix(prim: Usd.Prim, time_code: Usd.TimeCode = Usd.TimeCode.Default()) -> Gf.Matrix4d:
    """Gets local transform matrix of specific time code from prim.

    Args:
        prim (Usd.Prim): The prim handle.
        time_code (Usd.TimeCode, optional): Time code to query. Defaults to Usd.TimeCode.Default().

    Returns:
        Gf.Matrix4d: Local transform matrix.
    """

    xformable = UsdGeom.Xformable(prim)
    # todo GetResetXformStack (also not supported in C++ counterpart in Kit's UsdUtils.h)
    return xformable.GetLocalTransformation(time_code)


def get_world_transform_matrix(prim: Usd.Prim, time_code: Usd.TimeCode = Usd.TimeCode.Default()) -> Gf.Matrix4d:
    """Gets work transform matrix of specific time code from prim.

    Args:
        prim (Usd.Prim): The prim handle.
        time_code (Usd.TimeCode, optional): Time code to query. Defaults to Usd.TimeCode.Default().

    Returns:
        Gf.Matrix4d: World transform matrix.
    """

    xformable = UsdGeom.Xformable(prim)
    return xformable.ComputeLocalToWorldTransform(time_code)


def get_sdf_layer(prim):
    """Internal. Gets the introducing layer of the prim."""

    if prim is None:
        return None

    arcs = Usd.PrimCompositionQuery(prim).GetCompositionArcs()
    for arc in arcs:
        arc_layer = arc.GetIntroducingLayer()
        arc_prim = arc.GetIntroducingPrimPath()
        if arc_layer is None or arc_prim is None:
            continue
        if arc_prim == prim.GetPath():
            return arc_layer

    return prim.GetStage().GetRootLayer()


def get_authored_prim(prim):
    """Internal."""

    while not prim.IsPseudoRoot():
        if prim.HasAuthoredReferences():
            return prim
        prim = prim.GetParent()
    return None


def get_introducing_layer(prim: Usd.Prim) -> Tuple[Sdf.Layer, Sdf.Path]:
    """Gets the introducing layer.

    This function will find the local layer that defines this prim, or the first introducing
    layer that introduces the prim into the local layer stack if prim is defined in a reference
    or payload.

    An introducting layer is the layer that adds the prim into the composition graph.
    The difference of this function to Usd.PrimCompositionQuery is that it will return
    the first local layer where the prim is defined. If it's not defined locally, it will find
    the reference or payload arcs with Usd.PrimCompositionQuery to find the first introducing
    layer and its introducing prim path in the local layer stack.

    Args:
        prim (Usd.Prim): Prim handle

    Returns:
        Tuple[Sdf.Layer, Sdf.Path]: Introducing layer and its introducing prim path.
    """

    prim_stack = prim.GetPrimStack()
    for prim_spec in prim_stack:
        if prim_spec.specifier == Sdf.SpecifierDef and prim.GetStage().HasLocalLayer(prim_spec.layer):
            return prim_spec.layer, prim_spec.path

    query = Usd.PrimCompositionQuery(prim)
    qFilter = Usd.PrimCompositionQuery.Filter()
    qFilter.arcTypeFilter = Usd.PrimCompositionQuery.ArcTypeFilter.ReferenceOrPayload
    qFilter.arcIntroducedFilter = Usd.PrimCompositionQuery.ArcIntroducedFilter.IntroducedInRootLayerStack
    query.filter = qFilter
    arcs = query.GetCompositionArcs()
    for arc in arcs:
        layer = arc.GetIntroducingLayer()
        if layer:
            return layer, arc.GetIntroducingPrimPath()

    return None, None


def find_path_in_nodes(node, set_fn):
    """Internal. Finds specific spec recursively from node's layer stack."""

    def find_in_sublayers(node, layerTree, set_fn, sublayer=False):
        layer = layerTree.layer
        spec = layer.GetObjectAtPath(node.path)
        if spec:
            set_fn(layer.identifier)
        if layerTree.childTrees:
            find_in_sublayers(node, layerTree.childTrees[-1], set_fn, True)

    find_in_sublayers(node, node.layerStack.layerTree, set_fn, False)
    if node.children:
        omni.usd.find_path_in_nodes(node.children[-1], set_fn)


def get_url_from_prim(prim):
    """Returns url of Prim when authored reference or None."""

    url_path = None
    external_refs = omni.usd.get_composed_references_from_prim(prim)
    if not external_refs:
        external_refs = omni.usd.get_composed_payloads_from_prim(prim)

    if external_refs:
        # Show the first ref path
        ref, layer = external_refs[0]
        url_path = layer.ComputeAbsolutePath(ref.assetPath)
    else:
        authored_prim = omni.usd.get_authored_prim(prim)
        if authored_prim and authored_prim != prim:
            index = prim.GetPrimIndex()
            if index.IsValid():

                def set_url(url):
                    nonlocal url_path
                    url_path = url

                omni.usd.find_path_in_nodes(index.rootNode, set_url)

    return url_path


def get_composed_references_from_prim(
    prim: Usd.Prim, fix_slashes: bool = True
) -> List[Tuple[Sdf.Reference, Sdf.Layer]]:
    """Gets composed reference list from prim.

    Args:
        prim (Usd.Prim): Handle of Usd.Prim.

    Returns:
        List of reference items. Each item is a tuple that includes reference handle, and
        the layer it's from.
    """

    def _make_refs_absolute(info_map, layer, refs):
        ret_refs = []
        for ref in refs:
            authored_asset_path = ref.assetPath
            asset_path = (
                authored_asset_path
                if len(authored_asset_path) == 0 or layer.anonymous
                else layer.ComputeAbsolutePath(authored_asset_path)
            )
            # make a copy as Reference is immutable
            ref_new = Sdf.Reference(
                assetPath=asset_path.replace("\\", "/") if fix_slashes else asset_path,
                primPath=ref.primPath,
                layerOffset=ref.layerOffset,
                customData=ref.customData,
            )

            ret_refs.append(ref_new)
            info_map.append((ref_new, layer, ref.layerOffset, ref.assetPath))

        return ret_refs

    # Poor man's version of _GetListOpMetadataImpl and _PcpComposeSiteReferencesOrPayloads without discarding invalid reference
    ref_and_layers = []
    stack = prim.GetPrimStack()
    info_map = []  # cannot use dict, have to use equal compare. Equal reference may not have same hash
    list_ops = []
    for prim_spec in stack:
        if prim_spec.HasInfo(Sdf.PrimSpec.ReferencesKey):
            op = prim_spec.GetInfo(Sdf.PrimSpec.ReferencesKey)
            # Reference assetPath needs to be converted to absolute path so composed list properly adds and removes refs
            # that may have different relative paths but actually resolve to the same absolute path.
            if op.isExplicit:
                op.explicitItems = _make_refs_absolute(info_map, prim_spec.layer, op.explicitItems)
            else:
                op.addedItems = _make_refs_absolute(info_map, prim_spec.layer, op.addedItems)
                op.prependedItems = _make_refs_absolute(info_map, prim_spec.layer, op.prependedItems)
                op.appendedItems = _make_refs_absolute(info_map, prim_spec.layer, op.appendedItems)
                op.deletedItems = _make_refs_absolute(info_map, prim_spec.layer, op.deletedItems)
                op.orderedItems = _make_refs_absolute(info_map, prim_spec.layer, op.orderedItems)
            list_ops.append(op)

    items = []
    list_ops.reverse()
    for op in list_ops:
        items = op.ApplyOperations(items)

    for item in items:
        info = next((x for x in info_map if x[0] == item), None)
        if info:
            restored_ref = Sdf.Reference(
                assetPath=info[3].replace("\\", "/") if fix_slashes else info[3],
                primPath=info[0].primPath,
                layerOffset=info[2],
                customData=info[0].customData,
            )
            ref_and_layers.append((restored_ref, info[1]))
        else:
            carb.log_error("Cannot found reference in info map! It might be a bug in the widget code.")

    return ref_and_layers


def get_composed_payloads_from_prim(prim: Usd.Prim, fix_slashes: bool = True) -> List[Tuple[Sdf.Payload, Sdf.Layer]]:
    """Gets composed payload list from prim.

    Args:
        prim (Usd.Prim): Handle of Usd.Prim.

    Returns:
        List of payload items. Each item is a tuple that includes payload handle, and
        the layer it's from.
    """

    def _make_refs_absolute(info_map, layer, refs):
        ret_refs = []
        for ref in refs:
            authored_asset_path = ref.assetPath
            asset_path = (
                authored_asset_path
                if len(authored_asset_path) == 0 or layer.anonymous
                else layer.ComputeAbsolutePath(authored_asset_path)
            )
            # make a copy as Payload is immutable
            ref_new = Sdf.Payload(
                assetPath=asset_path.replace("\\", "/") if fix_slashes else asset_path,
                primPath=ref.primPath,
                layerOffset=ref.layerOffset,
            )

            ret_refs.append(ref_new)
            info_map.append((ref_new, layer, ref.layerOffset, ref.assetPath))

        return ret_refs

    # Poor man's version of _GetListOpMetadataImpl and _PcpComposeSiteReferencesOrPayloads without discarding invalid payload
    ref_and_layers = []
    stack = prim.GetPrimStack()
    info_map = []  # cannot use dict, have to use equal compare. Equal payload may not have same hash
    list_ops = []
    for prim_spec in stack:
        if prim_spec.HasInfo(Sdf.PrimSpec.PayloadKey):
            op = prim_spec.GetInfo(Sdf.PrimSpec.PayloadKey)
            # Payload assetPath needs to be converted to absolute path so composed list properly adds and removes refs
            # that may have different relative paths but actually resolve to the same absolute path.
            if op.isExplicit:
                op.explicitItems = _make_refs_absolute(info_map, prim_spec.layer, op.explicitItems)
            else:
                op.addedItems = _make_refs_absolute(info_map, prim_spec.layer, op.addedItems)
                op.prependedItems = _make_refs_absolute(info_map, prim_spec.layer, op.prependedItems)
                op.appendedItems = _make_refs_absolute(info_map, prim_spec.layer, op.appendedItems)
                op.deletedItems = _make_refs_absolute(info_map, prim_spec.layer, op.deletedItems)
                op.orderedItems = _make_refs_absolute(info_map, prim_spec.layer, op.orderedItems)
            list_ops.append(op)

    items = []
    list_ops.reverse()
    for op in list_ops:
        items = op.ApplyOperations(items)

    for item in items:
        info = next((x for x in info_map if x[0] == item), None)
        if info:
            restored_ref = Sdf.Payload(
                assetPath=info[3].replace("\\", "/") if fix_slashes else info[3],
                primPath=info[0].primPath,
                layerOffset=info[2],
            )
            ref_and_layers.append((restored_ref, info[1]))
        else:
            carb.log_error("Cannot found payload in info map! It might be a bug in the widget code.")

    return ref_and_layers


def check_ancestral(prim: Usd.Prim) -> bool:
    """Check if prim is brought into composition by its ancestor.

    Args:
        prim (Usd.Prim): The prim to check.

    Returns:
        bool: True if it's ancestral prim, or False otherwise.
    """

    def check_ancestral_node(node):
        # Check if any of the node is ancestral
        is_ancestral = node.IsDueToAncestor()
        if not is_ancestral:
            for child in node.children:
                is_ancestral = check_ancestral_node(child) or is_ancestral
                if is_ancestral:
                    break
        return is_ancestral

    return check_ancestral_node(prim.GetPrimIndex().rootNode)


def can_be_copied(prim):
    """Internal. If the prim can be copied. A prim can be copied means the prim is authored to the local layer stack directly.

    REMINDER: This function works differently as :class:`omni.usd.commands.CopyPrimCommand`.
    Please don't depend on this function to check if a prim can be copied or not. It's kept for
    back compatibility.
    """
    stage = prim.GetStage()
    for layer in stage.GetLayerStack():
        old_prim_spec = layer.GetPrimAtPath(prim.GetPath().pathString)
        if old_prim_spec is not None:
            return True

    return False


def handle_exception(func):
    """Decorator to print exception in async functions."""

    import traceback

    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except asyncio.CancelledError:
            # We always cancel the task. It's not a problem.
            pass
        except Exception as e:
            carb.log_error(f"Exception when async '{func}'")
            carb.log_error(f"{e}")
            carb.log_error(f"{traceback.format_exc()}")

    return wrapper


# Python equivalent of UsdUtils::getLocalTransformSRT
def get_local_transform_SRT(
    prim, time=Usd.TimeCode.Default()
) -> Tuple[Gf.Vec3d | Gf.Vec3f | Gf.Vec3h, Gf.Vec3d | Gf.Vec3f | Gf.Vec3h, Gf.Vec3i, Gf.Vec3d | Gf.Vec3f | Gf.Vec3h]:
    """Internal. Return a tuple of [scale, rotation, rotation_order, translate] for given prim."""

    xform = UsdGeom.Xformable(prim)

    extra_xform_ops = []
    ordered_xform_ops = xform.GetOrderedXformOps() or []

    seen_scale = False
    seen_rotation = 0  # use a counter here, because euler angle can show up as individual xform_op.
    seen_axes = [False, False, False]
    seen_translation = False

    # default values
    scale = Gf.Vec3d(1.0, 1.0, 1.0)
    rotation = Gf.Vec3d(0.0, 0.0, 0.0)
    rotation_order = Gf.Vec3i(-1, -1, -1)  # placeholder
    translation = Gf.Vec3d(0.0, 0.0, 0.0)

    type_enums_to_int = {
        UsdGeom.XformOp.TypeInvalid: 0,
        UsdGeom.XformOp.TypeTranslate: 1,
        UsdGeom.XformOp.TypeScale: 2,
        UsdGeom.XformOp.TypeRotateX: 3,
        UsdGeom.XformOp.TypeRotateY: 4,
        UsdGeom.XformOp.TypeRotateZ: 5,
        UsdGeom.XformOp.TypeRotateXYZ: 6,
        UsdGeom.XformOp.TypeRotateXZY: 7,
        UsdGeom.XformOp.TypeRotateYXZ: 8,
        UsdGeom.XformOp.TypeRotateYZX: 9,
        UsdGeom.XformOp.TypeRotateZXY: 10,
        UsdGeom.XformOp.TypeRotateZYX: 11,
        UsdGeom.XformOp.TypeOrient: 12,
        UsdGeom.XformOp.TypeTransform: 13,
    }

    ordered_xform_ops.reverse()
    for xform_op in ordered_xform_ops:

        # A.B. temp solution to unblock a showstopper for supporting unitsResolve suffix xformOp stacks
        # for preop we do full composition, for post op we know how to transform, we do the transformation at the end
        if xform_op.GetOpName().endswith(":unitsResolve"):
            if xform_op == ordered_xform_ops[-1]:
                seen_scale = True
                seen_rotation = 3
                seen_translation = True
                mtx = xform.GetLocalTransformation(time)

                rot_mat = Gf.Matrix4d(1.0)
                _, _, scale, rot_mat, translation, _ = mtx.Factor()

                # By default decompose as XYZ order (make it an option?)
                decomp_rot = rot_mat.ExtractRotation().Decompose(Gf.Vec3d.ZAxis(), Gf.Vec3d.YAxis(), Gf.Vec3d.XAxis())
                rotation = Gf.Vec3d(decomp_rot[2], decomp_rot[1], decomp_rot[0])
                rotation_order = Gf.Vec3i(0, 1, 2)
                return scale, rotation, rotation_order, translation
            else:
                extra_xform_ops.append(xform_op)

            continue


        if xform_op.IsInverseOp():
            continue

        op_type = xform_op.GetOpType()

        if op_type == UsdGeom.XformOp.TypeTransform:
            seen_scale = True
            seen_rotation = 3
            seen_translation = True
            mtx = xform_op.GetOpTransform(time)

            rot_mat = Gf.Matrix4d(1.0)
            _, _, scale, rot_mat, translation, _ = mtx.Factor()

            # By default decompose as XYZ order (make it an option?)
            decomp_rot = rot_mat.ExtractRotation().Decompose(Gf.Vec3d.ZAxis(), Gf.Vec3d.YAxis(), Gf.Vec3d.XAxis())
            rotation = Gf.Vec3d(decomp_rot[2], decomp_rot[1], decomp_rot[0])
            rotation_order = Gf.Vec3i(0, 1, 2)

            break

        if not seen_scale:
            if op_type == UsdGeom.XformOp.TypeScale:
                if seen_rotation or seen_translation:
                    carb.log_warn("Incompatible xformOpOrder, rotation or translation applied before scale.")

                seen_scale = True
                scale = xform_op.Get(time) or (1.0, 1.0, 1.0)

        if seen_rotation != 3:
            if (
                type_enums_to_int[op_type] >= type_enums_to_int[UsdGeom.XformOp.TypeRotateXYZ]
                and type_enums_to_int[op_type] <= type_enums_to_int[UsdGeom.XformOp.TypeRotateZYX]
            ):
                if seen_translation or seen_rotation != 0:
                    carb.log_warn(
                        "Incompatible xformOpOrder, translation applied before rotation or too many rotation ops."
                    )

                seen_rotation = 3
                rotation = xform_op.Get(time) or (0.0, 0.0, 0.0)

                rotation_orders = [
                    Gf.Vec3i(0, 1, 2),  # XYZ
                    Gf.Vec3i(0, 2, 1),  # XZY
                    Gf.Vec3i(1, 0, 2),  # YXZ
                    Gf.Vec3i(1, 2, 0),  # YZX
                    Gf.Vec3i(2, 0, 1),  # ZXY
                    Gf.Vec3i(2, 1, 0),  # ZYX
                ]

                rotation_order = rotation_orders[
                    type_enums_to_int[op_type] - type_enums_to_int[UsdGeom.XformOp.TypeRotateXYZ]
                ]

            elif op_type >= UsdGeom.XformOp.TypeRotateX and op_type <= UsdGeom.XformOp.TypeRotateZ:
                if seen_translation or seen_rotation > 3:
                    carb.log_warn("Incompatible xformOpOrder, too many single axis rotation ops.")

                # Set rotation order based on individual axis order
                rotation_order[seen_rotation] = (
                    type_enums_to_int[op_type] - type_enums_to_int[UsdGeom.XformOp.TypeRotateX]
                )
                seen_rotation += 1
                seen_axes[type_enums_to_int[op_type] - type_enums_to_int[UsdGeom.XformOp.TypeRotateX]] = True

                angle = xform_op.Get(time) or 0.0

                rotation[type_enums_to_int[op_type] - type_enums_to_int[UsdGeom.XformOp.TypeRotateX]] = angle
            elif op_type == UsdGeom.XformOp.TypeOrient:
                if seen_translation or seen_rotation != 0:
                    carb.log_warn(
                        "Incompatible xformOpOrder, translation applied before rotation or too many rotation ops."
                    )

                seen_rotation = 3
                rot = Gf.Rotation()
                quat = xform_op.Get(time)
                if quat is not None:
                    rot.SetQuat(quat)

                # By default decompose as XYZ order (make it an option?)
                decomp_rot = rot.Decompose(Gf.Vec3d.ZAxis(), Gf.Vec3d.YAxis(), Gf.Vec3d.XAxis())
                rotation = Gf.Vec3d(decomp_rot[2], decomp_rot[1], decomp_rot[0])
                rotation_order = Gf.Vec3i(0, 1, 2)

        if not seen_translation:
            # Do not get translation from pivot
            if op_type == UsdGeom.XformOp.TypeTranslate and "pivot" not in xform_op.SplitName():
                seen_translation = True
                translation = xform_op.Get(time) or (0.0, 0.0, 0.0)

    if seen_rotation == 0:
        # If we did not see any rotation op, get it from the preferences
        order_map = {
            "XYZ": Gf.Vec3i(0, 1, 2),
            "XZY": Gf.Vec3i(0, 2, 1),
            "YXZ": Gf.Vec3i(1, 0, 2),
            "YZX": Gf.Vec3i(1, 2, 0),
            "ZXY": Gf.Vec3i(2, 0, 1),
            "ZYX": Gf.Vec3i(2, 1, 0),
        }
        settings = carb.settings.get_settings()
        if prim.IsA(UsdGeom.Camera):
            order_str = settings.get("/persistent/app/primCreation/DefaultCameraRotationOrder")
        else:
            order_str = settings.get("/persistent/app/primCreation/DefaultRotationOrder")
        rotation_order = order_map.get(order_str, Gf.Vec3i(0, 1, 2))
        seen_rotation = 3
    else:
        # Assign rotation order to missing rotation ops after existing rotation ops
        for i in range(0, 3):
            if rotation_order[i] == -1:
                for j in range(0, 3):
                    if not seen_axes[j]:
                        rotation_order[i] = j
                        seen_axes[j] = True
                        break


    # A.B. this is a known transformation, we have a rotateX +-90 and scale
    # we can just add the X euler rotation and swap the scale Y,Z axis, this should represent the additonal transformation
    if len(extra_xform_ops) > 0:
        scale_value = Gf.Vec3d(1.0)
        for xform_op in extra_xform_ops:
            if xform_op.GetOpType() == UsdGeom.XformOp.TypeScale:
                scale_value = xform_op.Get()
                scale = Gf.CompMult(Gf.Vec3d(scale), Gf.Vec3d(scale_value))
            elif xform_op.GetOpType() == UsdGeom.XformOp.TypeRotateX:
                rot_value = xform_op.Get()
                if Gf.IsClose(abs(rot_value), 90.0, 0.01):
                    rotation[0] = rotation[0] + rot_value
                    scale[1], scale[2] = scale[2], scale[1]

    return scale, rotation, rotation_order, translation


def get_stage_next_free_path(stage: Usd.Stage, path: Union[str, Sdf.Path], prepend_default_prim: bool, source_prim: Optional[Usd.Prim] = None):
    """Gets a new prim path that doesn't exist in the stage given a base path.

    If the given path doesn't exist in the stage already, it returns the given path directly.
    Otherwise, it appends a suffix with number index to the given path until it finds a path that's not taken.

    Args:
        stage (Usd.Stage): The stage handle.
        path (Union[str, Sdf.Path]): Base prim path.
        prepend_default_prim (bool): Whether it should prepend default prim name to the path or not.
        source_prim (Usd.Prim, optional): The prim to use as a source for the new path.

    Raises:
        ValueError: Path is not a valid prim path.

    Returns:
        str: prim path that doesn't exist in the stage.
    """

    if isinstance(path, str) and not Sdf.Path.IsValidPathString(path):
        raise ValueError(f"{path} is not a valid path")

    path = Sdf.Path(path)
    # If path is missing leading slash, it's still ValidPathString but may crash in other USD api. Correct it here and issue a warning.
    corrected_path = path.MakeAbsolutePath(Sdf.Path.absoluteRootPath)
    if path != corrected_path:
        carb.log_warn(f"Path {path} is auto-corrected to {corrected_path}. Please verify your path format.")
        path = corrected_path

    if prepend_default_prim and stage.HasDefaultPrim():
        defaultPrim = stage.GetDefaultPrim()
        if defaultPrim and not (path.HasPrefix(defaultPrim.GetPath()) and path != defaultPrim.GetPath()):
            path = path.ReplacePrefix(Sdf.Path.absoluteRootPath, defaultPrim.GetPath())

    def increment_path(path):
        match = re.search(r"_(\d+)$", path)
        if match:
            new_num = int(match.group(1)) + 1
            ret = re.sub(r"_(\d+)$", str.format("_{:02d}", new_num), path)
        else:
            ret = path + "_01"
        return ret

    path_string = path.pathString
    while stage.GetPrimAtPath(path_string):
        if source_prim and source_prim.IsValid():
            if stage.GetPrimAtPath(path_string) == source_prim:
                return path_string
        path_string = increment_path(path_string)

    return path_string


def get_prim_descendents(root_prim: Usd.Prim) -> List[Usd.Prim]:
    """Internal. Returns all descendants for a given prim.

    Args:
        root_prim (Usd.Prim): The root prim to query.

    Returns:
        List[Usd.Prim]: A list of prim handles.
    """

    descendents = []
    for prim in Usd.PrimRange(root_prim):
        if prim.IsA(UsdGeom.Subset) or prim.IsA(UsdGeom.Gprim) or prim.IsA(UsdGeom.Xform):
            descendents.append(prim)

    return descendents


class PrimCaching:
    """Internal. Utility class that monitors changes from specific prim type."""

    def __init__(self, usd_type: Any,
                 stage: [Usd.Stage|None] = None,
                 on_changed: Callable[[], None] = None,
                 usd_context_name: [str|None] = None):
        """Constructor.

        Args:
            usd_type (Any): Usd prim type, like UsdShade.Material, UsdShade.Shader, etc.
            stage (Usd.Stage): The stage to listen.
            on_changed (Callable[[], None], optional): The callback to invoke when interested prims are changed or any prims are removed.
                Defaults to None.
            usd_context_name (str): The UsdContext name to listen on (rather than passing a stage)
        """
        self._usd_type = usd_type
        self._on_changed = on_changed
        self._usd_cache_state = False
        self._usd_property_changes = set()
        self.__prim_changed_task_or_future = None

        usd_context = None
        if (usd_context_name is None) and (stage is not None):
            usd_context = get_context_from_stage(stage)
            usd_context_name = usd_context.get_name() if usd_context else ""

        self.__usd_context_name = usd_context_name if usd_context_name else ""

        if usd_context is None:
            usd_context = omni.usd.get_context(self.__usd_context_name)
            assert usd_context is not None

        if stage is None:
            stage = usd_context.get_stage()

        if stage:
            self._stage = weakref.ref(stage)
            self._notice_listener = Tf.Notice.Register(Usd.Notice.ObjectsChanged, self._on_usd_changed, stage)
        else:
            self._stage, self._notice_listener = None, None

        self._stage_event_sub = [
            get_eventdispatcher().observe_event(
                observer_name="omi.usd:PrimCaching",
                event_name=usd_context.stage_event_name(event),
                on_event=func
            )
            for event, func in (
                (omni.usd.StageEventType.CLOSING, self._on_stage_closing),
                (omni.usd.StageEventType.OPENED, self._on_stage_opened)
            )
        ]
        usd_context, stage = None, None

    def __del__(self):
        if self._notice_listener:
            carb.log_error(f"PrimCaching leak. destroy has not been called")
            self.destroy()

    def destroy(self):
        if self._notice_listener:
            self._notice_listener.Revoke()
        self._notice_listener = None
        self._stage = None
        self._usd_type = None
        self._usd_property_changes = None
        self.__prim_changed_task_or_future = None
        self._stage_event_sub = None

    @Trace.TraceFunction
    def _on_usd_changed(self, notice, stage):
        if not self._stage or not self._stage():
            return

        if stage != self._stage():
            return

        for p in notice.GetResyncedPaths():
            self._usd_property_changes.add(p.GetPrimPath() if p.IsPropertyPath() else p)

        for p in notice.GetChangedInfoOnlyPaths():
            self._usd_property_changes.add(p.GetPrimPath() if p.IsPropertyPath() else p)

        # Update in the next frame. We need it because we want to accumulate the affected prims
        if self.__prim_changed_task_or_future is None or self.__prim_changed_task_or_future.done():
            self.__prim_changed_task_or_future = run_coroutine(self._update_usd_cache_state())

    @handle_exception
    async def _update_usd_cache_state(self):
        await omni.kit.app.get_app().next_update_async()
        if not self._stage or not self._stage():
            return
        stage = self._stage()
        for path in self._usd_property_changes:
            prim = stage.GetPrimAtPath(path)
            # if prim is deleted or is a material, clear cache
            if not prim:
                carb.log_verbose(f"prim {path.GetPrimPath()} deleted/renamed - cleared cache")
                self.set_cache_state(False)
                if self._on_changed:
                    self._on_changed()
                break
            if prim.IsA(self._usd_type):
                carb.log_verbose(f"prim {prim} changed - cleared cache")
                self.set_cache_state(False)
                if self._on_changed:
                    self._on_changed()
                break
        self._usd_property_changes = set()

    def _on_stage_opened(self, *args, **kwargs):
        carb.log_verbose(f"new stage - cleared cache & initalized new stage")
        stage = omni.usd.get_context(self.__usd_context_name).get_stage()
        if stage:
            self._stage = weakref.ref(stage)
            self._notice_listener = Tf.Notice.Register(Usd.Notice.ObjectsChanged, self._on_usd_changed, stage)
        self.set_cache_state(False)
        if self._on_changed:
            self._on_changed()

    def _on_stage_closing(self, *args, **kwargs):
        carb.log_verbose(f"stage closed - cleared cache & reset stage")
        if self._notice_listener:
            self._notice_listener.Revoke()
        self._notice_listener = None
        self._stage = None
        self.set_cache_state(False)
        if self._on_changed:
            self._on_changed()

    def get_cache_state(self) -> bool:
        """Gets cache state.

        Returns:
            bool: True if cached, or False otherwise.
        """

        return self._usd_cache_state

    def set_cache_state(self, state: bool):
        """Sets cache state.

        Args:
            state (bool): True for cached, and False for non-cached.
        """

        self._usd_cache_state = state

    def get_stage(self) -> Optional[Usd.Stage]:
        """Gets listened stage handle.

        Returns:
            Optional[Usd.Stage]: Stage handle or None.
        """
        if self._stage:
            return self._stage()
        return None


def duplicate_prim(
    stage: Usd.Stage, prim_path: Union[str, Sdf.Path], path_to: Union[str, Sdf.Path], duplicate_layers: bool = True
):
    """
    Duplicate prim.

    Args:
        stage (Usd.Stage): Stage handle.

        prim_path (Union[str, Sdf.Path]): Prim path.

        path_to (Union[str, Sdf.Path]): Copy to path.

        duplicate_layers (bool): True if it's to duplicate this prim in all local layers.
            False if it's to duplicate this prim to the current edit target. And it
            depends on whether the prim is defined or not. If it's not defined, it will only
            copy the opinions in the current edit target if it exists. Otherwise, it
            will copy the def to the current edit target, even it's from other layers
            instead of the current edit target. If you want to collapse all overrides
            inside all local layers for the prim, see omni.usd.stitch_prim_specs for reference.
    Return:
        True if successful, or false otherwise.
    """

    # TODO AND FIXME: This function is full with assumption and does not work
    # well when prim has multiple defs, which is mostly ok for now as most of
    # the contents authored with Kit has only one def for a prim. We need to
    # revisit this later to define the correct behavior for duplicate especially
    # when it's invovles with multi-layers to define or override the same prim.

    sdf_from_path = Sdf.Path(prim_path)
    sdf_to_path = Sdf.Path(path_to)
    if sdf_from_path == sdf_to_path:
        carb.log_error(f"Failed to duplicate prim {prim_path} to itself.")
        return False

    usd_prim = stage.GetPrimAtPath(sdf_from_path)
    if not usd_prim or sdf_from_path == Sdf.Path.absoluteRootPath:
        carb.log_warn(f"Cannot duplicate prim {prim_path} since it doesn't exist.")
        return False

    # If usd_prim is not defined and don't copy all local layers.
    if not usd_prim.IsDefined() and not duplicate_layers:
        dst_layer = stage.GetEditTarget().GetLayer()
        prim_spec = dst_layer.GetPrimAtPath(sdf_from_path)
        if not prim_spec:
            carb.log_error(
                f"Cannot duplicate prim {prim_path} as it's not defined and doesn't exist in the current edit target."
            )
            return False
        else:
            Sdf.CreatePrimInLayer(dst_layer, sdf_to_path)
            Sdf.CopySpec(dst_layer, sdf_from_path, dst_layer, sdf_to_path)

            return True

    # Gets the local layer where the prim is firstly introduced.
    introducing_layer, intro_prim_path = omni.usd.get_introducing_layer(usd_prim)

    # If it's to duplicate prim in the current local stack
    copy_prim_from_local_stack = intro_prim_path == sdf_from_path

    # Otherwise, checks if the prim is from a reference or payload.
    from_reference_or_payload = False
    # The prim spec that defines the source prim in a reference or payload.
    prim_spec_in_def_layer = None
    if not copy_prim_from_local_stack:
        for prim_spec in usd_prim.GetPrimStack():
            if prim_spec.specifier == Sdf.SpecifierDef and not stage.HasLocalLayer(prim_spec.layer):
                from_reference_or_payload = True
                prim_spec_in_def_layer = prim_spec
                break

    with Sdf.ChangeBlock():
        for old_prim_spec in usd_prim.GetPrimStack():
            layer = old_prim_spec.layer

            if copy_prim_from_local_stack:
                if not stage.HasLocalLayer(layer):
                    continue

                # Copies the first def only if it's not to copy all layers.
                if not duplicate_layers:
                    layer = introducing_layer

            if not duplicate_layers:
                dst_layer = stage.GetEditTarget().GetLayer()
            elif from_reference_or_payload and prim_spec_in_def_layer == old_prim_spec:
                dst_layer = introducing_layer
            elif stage.HasLocalLayer(layer):
                dst_layer = layer
            else:
                continue

            if duplicate_layers or copy_prim_from_local_stack or old_prim_spec.specifier == Sdf.SpecifierDef:
                if layer != dst_layer:
                    # Copy def prim from reference or payload into temp layer
                    temp_layer = Sdf.Layer.CreateAnonymous()
                    Sdf.CreatePrimInLayer(temp_layer, sdf_from_path)
                    Sdf.CopySpec(layer, old_prim_spec.path, temp_layer, sdf_from_path)

                    # Converts all external references inside temp_layer to absolute path.
                    # All paths will be resolved against layer.identifier.
                    omni.usd.resolve_paths(layer.identifier, temp_layer.identifier, False)

                    # Converts all external references inside temp_layer to relative path.
                    # And the relative path is compuated against dst_layer.identifier.
                    omni.usd.resolve_paths(dst_layer.identifier, temp_layer.identifier, True, True)

                    # If prim is not inside the sublayer list but in reference or payload,
                    # it needs to resolve the prim path since all its referenced relationships
                    # needs to be remapped to new paths against the introducing path.
                    if not stage.HasLocalLayer(layer) and from_reference_or_payload:
                        root_prim_path = old_prim_spec.path.GetPrefixes()[0]
                        target_root_prim_path = sdf_from_path.RemoveCommonSuffix(old_prim_spec.path, True)[0]
                        omni.usd.resolve_prim_path_references(
                            temp_layer.identifier, str(root_prim_path), str(target_root_prim_path)
                        )

                    if from_reference_or_payload and prim_spec_in_def_layer == old_prim_spec:
                        # It's possible that there are overrides in the intro layer, it
                        # needs to merge all those overrides.
                        omni.usd.merge_prim_spec(
                            temp_layer.identifier, introducing_layer.identifier,
                            str(sdf_from_path), False
                        )

                    # It's possible that the prim is defined inside reference or payload,
                    # and it has overrides inside the target layer. It needs to
                    # copy all those overrides also.
                    if dst_layer.GetPrimAtPath(sdf_from_path):
                        omni.usd.merge_prim_spec(temp_layer.identifier, dst_layer.identifier, str(sdf_from_path), False)

                    src_layer = temp_layer
                    src_prim_path = sdf_from_path
                else:
                    src_layer = layer
                    src_prim_path = old_prim_spec.path

                Sdf.CreatePrimInLayer(dst_layer, sdf_to_path)
                Sdf.CopySpec(src_layer, src_prim_path, dst_layer, sdf_to_path)

                # TODO: What if there are two defs of the same prim?
                if not duplicate_layers:
                    break

    return True


def make_path_relative_to_current_edit_target(url_path: str, stage: Usd.Stage = None) -> str:
    """Make path relative to the current edit target of the stage.

    Args:
        url_path (str): The asset url.
        stage (Usd.Stage, optional): The stage that the **url_path** is relative to. Defaults to None.

    Returns:
        str: Relative path if it can be computed or url_path untouched.
    """

    import omni.client.utils as client_utils
    if not url_path:
        return url_path

    path_method = carb.settings.get_settings().get("/persistent/app/material/dragDropMaterialPath") or "relative"
    if not stage:
        stage = omni.usd.get_context().get_stage()
        if not stage:
            carb.log_verbose('make_path_relative_to_current_edit_target: Failed due to no stage')
            return url_path

    if path_method.lower() == "relative":
        # XXX: PyBind omni::usd::UsdUtils::makePathRelativeToLayer
        url = url_path
        stage_layer = stage.GetEditTarget().GetLayer()
        if not stage_layer.anonymous and not Sdf.Layer.IsAnonymousLayerIdentifier(url):
            stage_layer_path = stage_layer.realPath
            # OM-115814: Use omni.client.utils for url comparison
            if client_utils.equal_urls(url, stage_layer_path):
                carb.log_verbose(f'make_path_relative_to_current_edit_target: Failed as cannot reference {url} onto itself')
                return url_path
            # OMPE-12316: If the current relative url is an absolute local path, and the layer is non-local, prepend
            #  the `file` scheme to the local path to make sure it resolves correctly; Currently on Linux, an abs
            #  local path may get recognized as relative without the explicit file scheme
            if client_utils.is_local_url(url) and not client_utils.is_local_url(stage_layer_path):
                relative_url = omni.client.normalize_url(client_utils.make_file_url_if_possible(url))
            else:
                relative_url = client_utils.make_relative_url_if_possible(stage_layer_path, url)
            if relative_url:
                return relative_url
        else:
            carb.log_verbose('make_path_relative_to_current_edit_target: Failed as stage is anonymous')

    return url_path


def get_context_from_stage(stage):
    """Gets corresponding UsdContext of the stage if it's found."""

    cache = UsdUtils.StageCache.Get()
    if hasattr(stage, "stage"):
        stage = stage.stage

    try:
        stage_id = cache.GetId(stage)
        if not stage_id.IsValid():
            return None
        else:
            stage_id = stage_id.ToLongInt()
    except:
        stage_id = stage.GetStageId()


    return get_context_from_stage_id(stage_id)


def correct_filename_case(file: str) -> str:
    """Internal."""

    try:
        import platform, glob, re

        if platform.system().lower() == "windows":
            # get correct case filename
            ondisk = glob.glob(re.sub(r'([^:/\\])(?=[/\\]|$)|\[', r'[\g<0>]', file))[0].replace("\\", "/")
            # correct drive letter case
            if ondisk[0].islower() and ondisk[1] == ":":
                ondisk = ondisk[0].upper() + ondisk[1:]
            # has only case changed
            if ondisk.lower() == file.lower():
                return ondisk
    except Exception as exc:
        pass
    return file


def gather_default_attributes(prim_type):
    """Internal. Gets default attributes for specific prim type."""

    settings_attrs = carb.settings.get_settings().get_settings_dictionary(f"/persistent/app/primCreation/typedDefaults/{prim_type}")
    return settings_attrs.get_dict() if settings_attrs else {}
