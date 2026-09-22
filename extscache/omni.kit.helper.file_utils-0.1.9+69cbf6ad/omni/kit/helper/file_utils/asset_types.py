# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = [
    "AssetTypeDef",
    "ASSET_TYPE_ANIM_USD",
    "ASSET_TYPE_CACHE_USD",
    "ASSET_TYPE_CURVE_ANIM_USD",
    "ASSET_TYPE_GEO_USD",
    "ASSET_TYPE_MATERIAL_USD",
    "ASSET_TYPE_PROJECT_USD",
    "ASSET_TYPE_SEQ_USD",
    "ASSET_TYPE_SKEL_USD",
    "ASSET_TYPE_SKEL_ANIM_USD",
    "ASSET_TYPE_USD_SETTINGS",
    "ASSET_TYPE_USD",
    "ASSET_TYPE_FBX",
    "ASSET_TYPE_OBJ",
    "ASSET_TYPE_MATERIAL",
    "ASSET_TYPE_IMAGE",
    "ASSET_TYPE_SOUND",
    "ASSET_TYPE_SCRIPT",
    "ASSET_TYPE_VOLUME",
    "ASSET_TYPE_FOLDER",
    "ASSET_TYPE_ICON",
    "ASSET_TYPE_HIDDEN",
    "ASSET_TYPE_UNKNOWN",
    "init_asset_types",
    "known_asset_types",
    "clear_asset_types",
    "register_file_extensions",
    "asset_type_exts",
    "is_asset_type",
    "is_udim_sequence",
    "get_asset_type",
    "get_icon",
    "get_thumbnail",
]

from typing import Dict, List
from collections import namedtuple
from pathlib import Path

AssetTypeDef = namedtuple("AssetTypeDef", "glyph thumbnail matching_exts")

# The known list of asset types, stored in this singleton variable
_known_asset_types: Dict = None

# Default Asset types
ASSET_TYPE_ANIM_USD = "anim_usd"
ASSET_TYPE_CACHE_USD = "cache_usd"
ASSET_TYPE_CURVE_ANIM_USD = "curve_anim_usd"
ASSET_TYPE_GEO_USD = "geo_usd"
ASSET_TYPE_MATERIAL_USD = "material_usd"
ASSET_TYPE_PROJECT_USD = "project_usd"
ASSET_TYPE_SEQ_USD = "seq_usd"
ASSET_TYPE_SKEL_USD = "skel_usd"
ASSET_TYPE_SKEL_ANIM_USD  = "skel_anim_usd"
ASSET_TYPE_USD_SETTINGS = "settings_usd"
ASSET_TYPE_USD = "usd"
ASSET_TYPE_FBX = "fbx"
ASSET_TYPE_OBJ = "obj"
ASSET_TYPE_MATERIAL = "material"
ASSET_TYPE_IMAGE = "image"
ASSET_TYPE_SOUND = "sound"
ASSET_TYPE_SCRIPT = "script"
ASSET_TYPE_VOLUME = "volume"
ASSET_TYPE_FOLDER = "folder"
ASSET_TYPE_ICON = "icon"
ASSET_TYPE_HIDDEN = "hidden"
ASSET_TYPE_UNKNOWN = "unknown"


def init_asset_types():
    """ Init default asset types's value """
    global _known_asset_types
    _known_asset_types = {}

    try:
        import carb.settings
        theme = carb.settings.get_settings().get_as_string("/persistent/app/window/uiStyle")
    except Exception:
        theme = None
    finally:
        theme = theme or "NvidiaDark"

    import omni.kit.app
    ext_path = omni.kit.app.get_app().get_extension_manager().get_extension_path_by_module(__name__)
    icon_path = Path(ext_path).joinpath("icons").joinpath(theme).absolute()
    thumbnail_path = Path(ext_path).joinpath(f"data").joinpath("thumbnails").absolute()

    _known_asset_types[ASSET_TYPE_USD_SETTINGS] = AssetTypeDef(
        f"{icon_path}/settings_usd.svg",
        f"{thumbnail_path}/settings_usd_256.png",
        [".settings.usd", ".settings.usda", ".settings.usdc", ".settings.usdz"],
    )
    _known_asset_types[ASSET_TYPE_ANIM_USD] = AssetTypeDef(
        f"{icon_path}/anim_usd.svg",
        f"{thumbnail_path}/anim_usd_256.png",
        [".anim.usd", ".anim.usda", ".anim.usdc", ".anim.usdz"],
    )
    _known_asset_types[ASSET_TYPE_CACHE_USD] = AssetTypeDef(
        f"{icon_path}/cache_usd.svg",
        f"{thumbnail_path}/cache_usd_256.png",
        [".cache.usd", ".cache.usda", ".cache.usdc", ".cache.usdz"],
    )
    _known_asset_types[ASSET_TYPE_CURVE_ANIM_USD] = AssetTypeDef(
        f"{icon_path}/anim_usd.svg",
        f"{thumbnail_path}/curve_anim_usd_256.png",
        [".curveanim.usd", ".curveanim.usda", ".curveanim.usdc", ".curveanim.usdz"],
    )
    _known_asset_types[ASSET_TYPE_GEO_USD] = AssetTypeDef(
        f"{icon_path}/geo_usd.svg",
        f"{thumbnail_path}/geo_usd_256.png",
        [".geo.usd", ".geo.usda", ".geo.usdc", ".geo.usdz"],
    )
    _known_asset_types[ASSET_TYPE_MATERIAL_USD] = AssetTypeDef(
        f"{icon_path}/material_usd.png",
        f"{thumbnail_path}/material_usd_256.png",
        [".material.usd", ".material.usda", ".material.usdc", ".material.usdz"],
    )
    _known_asset_types[ASSET_TYPE_PROJECT_USD] = AssetTypeDef(
        f"{icon_path}/project_usd.svg",
        f"{thumbnail_path}/project_usd_256.png",
        [".project.usd", ".project.usda", ".project.usdc", ".project.usdz"],
    )
    _known_asset_types[ASSET_TYPE_SEQ_USD] = AssetTypeDef(
        f"{icon_path}/sequence_usd.svg",
        f"{thumbnail_path}/sequence_usd_256.png",
        [".seq.usd", ".seq.usda", ".seq.usdc", ".seq.usdz"],
    )
    _known_asset_types[ASSET_TYPE_SKEL_USD] = AssetTypeDef(
        f"{icon_path}/skel_usd.svg",
        f"{thumbnail_path}/skel_usd_256.png",
        [".skel.usd", ".skel.usda", ".skel.usdc", ".skel.usdz"],
    )
    _known_asset_types[ASSET_TYPE_SKEL_ANIM_USD] = AssetTypeDef(
        f"{icon_path}/anim_usd.svg",
        f"{thumbnail_path}/skel_anim_usd_256.png",
        [".skelanim.usd", ".skelanim.usda", ".skelanim.usdc", ".skelanim.usdz"],
    )
    _known_asset_types[ASSET_TYPE_FBX] = AssetTypeDef(
        f"{icon_path}/usd_stage.svg", f"{thumbnail_path}/fbx_256.png", [".fbx"]
    )
    _known_asset_types[ASSET_TYPE_OBJ] = AssetTypeDef(
        f"{icon_path}/usd_stage.svg", f"{thumbnail_path}/obj_256.png", [".obj"]
    )
    _known_asset_types[ASSET_TYPE_MATERIAL] = AssetTypeDef(
        f"{icon_path}/mdl.svg", f"{thumbnail_path}/mdl_256.png", [".mdl", ".mtlx"]
    )
    _known_asset_types[ASSET_TYPE_IMAGE] = AssetTypeDef(
        f"{icon_path}/image.svg",
        f"{thumbnail_path}/image_256.png",
        [".bmp", ".gif", ".jpg", ".jpeg", ".png", ".tga", ".tif", ".tiff", ".hdr", ".dds", ".exr", ".psd", ".ies", ".tx"],
    )
    _known_asset_types[ASSET_TYPE_SOUND] = AssetTypeDef(
        f"{icon_path}/sound.svg",
        f"{thumbnail_path}/sound_256.png",
        [".wav", ".wave", ".ogg", ".oga", ".flac", ".fla", ".mp3", ".m4a", ".spx", ".opus", ".adpcm"],
    )
    _known_asset_types[ASSET_TYPE_SCRIPT] = AssetTypeDef(
        f"{icon_path}/script.svg", f"{thumbnail_path}/script_256.png", [".py"]
    )
    _known_asset_types[ASSET_TYPE_VOLUME] = AssetTypeDef(
        f"{icon_path}/volume.svg",
        f"{thumbnail_path}/volume_256.png",
        [".nvdb", ".vdb"],
    )
    _known_asset_types[ASSET_TYPE_ICON] = AssetTypeDef(None, None, [".svg"])
    _known_asset_types[ASSET_TYPE_HIDDEN] = AssetTypeDef(None, None, [".thumbs"])

    try:
        # avoid dependency on USD in this extension and only use it when available
        import omni.usd
        usd_exts = omni.usd.readable_usd_dotted_file_exts()
    except ImportError:
        usd_exts = ('.live', '.omni', '.usd', '.usda', '.usdc', '.usdz')

    # readable_usd_dotted_file_exts() is auto-generated by querying USD;
    # however, it includes some items that we've assigned more specific
    # roles (ie, .mdl).  So do this last, and subtract out any already-
    # known types.
    known_exts = set()
    for asset_type_def in _known_asset_types.values():
        known_exts.update(asset_type_def.matching_exts)
    usd_exts = [
        x for x in usd_exts
        if x not in known_exts
    ]
    _known_asset_types[ASSET_TYPE_USD] = AssetTypeDef(
        f"{icon_path}/usd_stage.svg",
        f"{thumbnail_path}/usd_stage_256.png",
        usd_exts,
    )


def known_asset_types():
    """
    Initializes and returns a dictionary of known asset types.

    Returns:
        dict: A dictionary containing known asset types, where the keys are asset type
        identifiers, and the values are instances of the `AssetTypeDef` class.

    Example:
        >>> asset_types = known_asset_types()
        >>> print(asset_types[ASSET_TYPE_ICON])
        AssetTypeDef(None, None, ['.svg'])

    """
    global _known_asset_types
    if _known_asset_types is None:
        init_asset_types()
    return _known_asset_types


def clear_asset_types():
    """clear known asset types."""
    known_asset_types().clear()


def register_file_extensions(asset_type: str, exts: [str], replace: bool = False):
    """
    Adds an asset type to the recognized list.

    Args:
        asset_type (str): Name of asset type.
        exts ([str]): List of extensions to associate with this asset type, e.g. [".usd", ".usda"].
        replace (bool): If True, replaces extensions in the existing definition. Otherwise, append
            to the existing list.

    """
    if not asset_type or exts == None:
        return
    asset_types = known_asset_types()
    if asset_type in asset_types:
        glyph = asset_types[asset_type].glyph
        thumbnail = asset_types[asset_type].thumbnail
        if replace:
            asset_types[asset_type] = AssetTypeDef(glyph, thumbnail, exts)
        else:
            exts.extend(asset_types[asset_type].matching_exts)
            asset_types[asset_type] = AssetTypeDef(glyph, thumbnail, exts)
    else:
        asset_types[asset_type] = AssetTypeDef(None, None, exts)


def asset_type_exts(asset_type: str) -> List[str]:
    """
    Returns a list of file extensions associated with the given asset type.

    Args:
        asset_type (str): The asset type identifier.

    Returns:
        List[str]: A list of file extensions that match the given asset type.
    """
    asset_types = known_asset_types()
    return asset_types[asset_type].matching_exts


def is_asset_type(filename: str, asset_type: str) -> bool:
    """
    Returns True if given filename is of specified type.

    Args:
        filename (str)
        asset_type (str): Tested type name.

    Returns:
        bool

    """
    asset_types = known_asset_types()
    if not (filename and asset_type):
        return False
    elif asset_type not in asset_types:
        return False
    return any([filename.lower().endswith(ext.lower()) for ext in asset_types[asset_type].matching_exts])


def is_udim_sequence(filename: str):
    """
    Checks if the given filename represents a UDIM sequence image.

    Args:
        filename (str): The filename to check.

    Returns:
        bool: True if the filename represents a UDIM sequence image, False otherwise.
    """
    return "<UDIM>" in filename and is_asset_type(filename, ASSET_TYPE_IMAGE)


def get_asset_type(filename: str) -> str:
    """
    Returns asset type, based on extension of given filename.

    Args:
        filename (str): Given file's name.

    Returns:
        str: The give file's asset type.

    """
    if not filename:
        return None
    asset_types = known_asset_types()
    for asset_type in asset_types:
        if is_asset_type(filename, asset_type):
            return asset_type
    return ASSET_TYPE_UNKNOWN


def get_icon(filename: str) -> str:
    """
    Returns icon for specified file.

    Args:
        filename (str)

    Returns:
        str: Fullpath to the icon file, None if not found.

    """
    if not filename:
        return None
    icon = None
    asset_type = get_asset_type(filename)
    asset_types = known_asset_types()
    if asset_type in asset_types:
        icon = asset_types[asset_type].glyph
    return icon


def get_thumbnail(filename: str) -> str:
    """
    Returns thumbnail for specified file.

    Args:
        filename (str)

    Returns:
        str: Fullpath to the thumbnail file, None if not found.

    """
    if not filename:
        return None
    thumbnail = None
    asset_type = get_asset_type(filename)
    asset_types = known_asset_types()
    if asset_type == ASSET_TYPE_ICON:
        thumbnail = filename
    else:
        if asset_type in asset_types:
            thumbnail = asset_types[asset_type].thumbnail

    import omni.kit.app
    ext_path = omni.kit.app.get_app().get_extension_manager().get_extension_path_by_module(__name__)
    thumbnail_path = Path(ext_path).joinpath(f"data").joinpath("thumbnails").absolute()

    return thumbnail or f"{thumbnail_path}/unknown_file_256.png"
