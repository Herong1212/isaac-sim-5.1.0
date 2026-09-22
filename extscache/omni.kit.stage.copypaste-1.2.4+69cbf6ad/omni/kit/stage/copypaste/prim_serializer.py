# Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = ["update_property_paths", "get_prim_as_text", "text_to_stage"]

import sys

from typing import Callable
from typing import List
from typing import Optional
from typing import Tuple

from omni.kit.commands import execute
from pxr import Sdf
from pxr import Tf
from pxr import Usd

import omni.usd
import omni.kit.app

POS_ATTR_NAME = 'ui:nodegraph:node:pos'
SMALL_OFFSET = 40


def _to_layer(text: str, keep_inputs=True, position=None) -> Optional[Sdf.Layer]:
    """Create an sdf layer from the given text"""

    if not text.startswith("#usda 1.0\n"):
        text = "#usda 1.0\n" + text

    anonymous_layer = Sdf.Layer.CreateAnonymous("clipboard.usda")
    try:
        if not anonymous_layer.ImportFromString(text):
            return None
    except Tf.ErrorException:
        return None

    if not keep_inputs or position is not None:
        graph_node_processing(anonymous_layer, keep_inputs=keep_inputs, position=position)

    return anonymous_layer


def graph_node_processing(layer: Sdf.Layer, keep_inputs=True, position=None):
    all_prims = []
    min_x, min_y = sys.maxsize, sys.maxsize
    offset = None
    root_prims = layer.rootPrims

    for prim_spec in root_prims:
        root_spec = prim_spec.nameChildren[0]
        all_prims.append(root_spec.path)

        if position is not None and POS_ATTR_NAME in root_spec.attributes:
            # Keep top left of bounding box of nodes
            pos = root_spec.attributes[POS_ATTR_NAME].default
            if pos[0] < min_x:
                min_x = pos[0]
            if pos[1] < min_y:
                min_y = pos[1]

    if position is not None:
        offset = (position[0] - min_x, position[1] - min_y)

    for prim_path in all_prims:
        prim_spec = layer.GetPrimAtPath(prim_path)
        attrs = prim_spec.attributes

        if POS_ATTR_NAME in attrs:
            offset_node_position(attrs[POS_ATTR_NAME], offset=offset)

        if not keep_inputs:
            for attr in attrs:
                connections = attr.connectionPathList.explicitItems
                if connections:
                    attr.connectionPathList.explicitItems = [
                        path for path in attr.connectionPathList.explicitItems
                        if connections[0].GetPrimPath() in all_prims
                    ]


def offset_node_position(pos_attr: Sdf.AttributeSpec, offset: Optional[Tuple[float, float]] = None):
    """Shift the nodes to be pasted, by the offset parameter, or if no offset is
    passed in, by a small offset, so pasted nodes are not exactly on top of the originals.

    Args:
        pos_attr (Sdf.AttributeSpec): AttributeSpec to get the existing position from.
        offset (Tuple[float, float], optional): Offset to place at mouse position. Defaults to None.
    """
    cur_position = pos_attr.default
    if offset is not None:
        pos_attr.default = (cur_position[0] + offset[0], cur_position[1] + offset[1])
    else:
        pos_attr.default = (cur_position[0] + SMALL_OFFSET, cur_position[1] + SMALL_OFFSET)


@omni.kit.app.deprecated("This tool function is supposed to be used only in this extension.")
def update_property_paths(prim_spec, old_path, new_path):
    if not prim_spec:
        return

    for rel in prim_spec.relationships:
        rel.targetPathList.explicitItems = [
            path.ReplacePrefix(old_path, new_path) for path in rel.targetPathList.explicitItems
        ]

    for attr in prim_spec.attributes:
        attr.connectionPathList.explicitItems = [
            path.ReplacePrefix(old_path, new_path) for path in attr.connectionPathList.explicitItems
        ]

    for child in prim_spec.nameChildren:
        update_property_paths(child, old_path, new_path)


@omni.kit.app.deprecated("This tool function is supposed to be used only in this extension.")
def get_prim_as_text(stage: Usd.Stage, prim_paths: List[Sdf.Path]) -> Optional[str]:
    """Generate a text representation from the stage and prim path"""

    if not prim_paths:
        return None

    prim_paths = [Sdf.Path(path) for path in prim_paths]
    prim_paths = Sdf.Path.RemoveDescendentPaths(prim_paths)

    # flatten_layer = stage.Flatten()
    # Stitches prims instead of flattening to avoid flattening references and payloads.
    flatten_layer = Sdf.Layer.CreateAnonymous()
    for prim_path in prim_paths:
        omni.usd.stitch_prim_specs(stage, prim_path, flatten_layer)

    paths_map = {}
    anonymous_layer = Sdf.Layer.CreateAnonymous(prim_paths[0].name + ".usda")
    for i, prim_path in enumerate(prim_paths):
        item_name = str.format("Item_{:02d}", i)
        Sdf.PrimSpec(anonymous_layer, item_name, Sdf.SpecifierDef)
        anonymous_path = Sdf.Path.absoluteRootPath.AppendChild(item_name).AppendChild(prim_path.name)

        # Copy
        Sdf.CopySpec(flatten_layer, prim_path, anonymous_layer, anonymous_path)

        paths_map[prim_path] = anonymous_path

    for prim in anonymous_layer.rootPrims:
        for source_path, target_path in paths_map.items():
            update_property_paths(prim, source_path, target_path)

    return anonymous_layer.ExportToString()


@omni.kit.app.deprecated("This tool function is supposed to be used only in this extension.")
def text_to_stage(stage: Usd.Stage, text: str, root: Sdf.Path = Sdf.Path.absoluteRootPath,
                  keep_inputs=True, position=None, filter_fn: Optional[Callable] = None) -> bool:
    """
    Convert the given text to prims and place them on the stage under the
    given root.
    """

    source_layer = _to_layer(text, keep_inputs=keep_inputs, position=position)
    if not source_layer:
        return False

    execute("ImportLayer", layer=source_layer, stage=stage, root=root,
            filter_fn=filter_fn)
    return True
