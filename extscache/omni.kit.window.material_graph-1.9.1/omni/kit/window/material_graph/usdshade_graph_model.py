# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = ["UsdShadeGraphModel"]

import asyncio
import functools
import os
import tempfile
import traceback
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional

import carb
import carb.events
import omni.stageupdate
import omni.usd
from omni.kit.widget.graph import GraphModel
from omni.kit.widget.material_preview import MaterialPreviewProducer
from omni.usd.commands import UsdStageHelper
from pxr import Sdf, Tf, Trace, Usd, UsdShade, UsdUI

from .export_utils import copy_input_metadata
from .shader_registry import ShaderRegistry
from .svg_picker import ATTRIBUTE_EMBEDDED_ICON
from .utils import can_connect

CURRENT_PATH = Path(__file__).parent
ICONS_PATH = CURRENT_PATH.parent.parent.parent.parent.joinpath("icons")


def handle_exception(func):
    """
    Decorator to print exception in async functions
    """

    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            carb.log_error(f"Exception when async '{func}'")
            carb.log_error(f"{e}")
            carb.log_error(f"{traceback.format_exc()}")

    return wrapper


class PrimNotSupportedError(Exception):
    """Wrong prim is passed to the model."""

    pass


class UsdShadeGraphModel(GraphModel):
    """The model to watch the UsdShade shading network"""

    DISPLAY_NAME = "UsdShade"

    class AttributeGroup(UsdStageHelper):
        def __init__(self, stage: Usd.Stage, name: str, child_paths: Optional[List[Sdf.Path]] = None):
            super().__init__(stage)
            self.name: str = name
            # child_paths argument is the classic Python interview question.
            # It should be None, not []
            self.child_paths: List[Sdf.Path] = child_paths or []
            self.state: GraphModel.ExpansionState = GraphModel.ExpansionState.OPEN

        def __repr__(self):
            return f"<AttributeGroup {self.name}>"

    def __init__(self, prims: List[Usd.Prim]):
        super().__init__()
        self.__materials_to_begin_with: List[Usd.Prim] = prims
        self.__paths_to_begin_with: List[Sdf.Path] = [prim.GetPath() for prim in prims]
        self.__positions = {}
        self.__positions_on_begin = {}
        self.__sizes = {}
        self.__sizes_on_begin = {}
        # The node that drives position of many nodes. Eample: the backdrop
        # node that is currently dragged
        self.__current_drive_node = None
        # The nodes that belong to the current backdrop
        self.__driven_nodes = {}
        # The list of all nodes of the model. We need it to determine if Kit
        # selection has nodes of the model.
        # TODO: Victor this is unused
        self.__nodes_paths = []
        # The hirarchy of all the nodes. We need it to have the full representation of the model.
        self.__root_to_hirarchy: Dict[Sdf.Path, List[Sdf.Path]] = {}
        # Has selected items. We need it to avoid calling GetPrimAtPath every time selection changes
        self.__selection_cache: List[Usd.Prim] = []

        # The standard set to watch the Kit selection
        # TODO: This block is the same in OmniGraphModel. We need to use
        # multiple inheritance and create a selection helper model
        # TODO: Victor this is unused
        self.__selection_paths = []
        self._usd_context = omni.usd.get_context()
        self._selection = self._usd_context.get_selection()
        self._events = self._usd_context.get_stage_event_stream()
        self._stage_selection_subscription = self._events.create_subscription_to_pop(
            self._on_stage_event, name="UsdShadeGraphModel Selection Watch"
        )

        # Get the stage from the first prim. We assume that all the prims are from the same stage.
        if self.__materials_to_begin_with:
            self._stage = self.__materials_to_begin_with[0].GetStage()
        else:
            self._stage = None

        # Stage watching
        if self._stage:
            self.__stage_listener = Tf.Notice.Register(Usd.Notice.ObjectsChanged, self._on_objects_changed, self._stage)

        self.__dirty_prim_paths: List[Sdf.Path] = []
        self.__dirty_prop_paths: List[Sdf.Path] = []
        self.__prim_changed_task = None

        # A cache of all the connections. We need it to delete them when the node is deleted.
        self.__reversed_connections: Dict[Sdf.Path, Sdf.Path] = defaultdict(set)

        # __preview_files is a dict with hash from content and and filename of
        # all the generated icon files.
        self.__preview_files: Dict[int, str] = {}

        self.__material_preview_producer: Optional[MaterialPreviewProducer] = None
        self.__shading_node_type_cache = {}

        self.__pause = False
        self.__locked_attributes = set()

    def destroy(self):
        self.pause = False

        self.__material_preview_producer = None

        if self.__prim_changed_task:
            if not self.__prim_changed_task.done():
                self.__prim_changed_task.cancel()
            self.__prim_changed_task = None
        self.__dirty_prim_paths = []
        self.__dirty_prop_paths = []

        self.__materials_to_begin_with = None
        self.__positions = {}
        self.__nodes_paths = []
        self.__selection_paths = []
        self._usd_context = None
        self._selection = None
        self._events = None
        self._stage_selection_subscription = None
        self._stage = None
        self.__stage_listener = None
        self.__root_to_hirarchy = {}
        self.__selection_cache = []
        self.__shading_node_type_cache = {}

        for _, path in self.__preview_files.items():
            os.remove(path)

    @staticmethod
    def has_nodes(obj):
        """Returns true if the model can currently build the graph network using the provided object"""
        if not isinstance(obj, Usd.Prim):
            return

        return obj.IsA(UsdShade.Material) or obj.IsA(UsdShade.Shader) or obj.IsA(UsdShade.NodeGraph)

    @staticmethod
    def is_compound(obj):
        return obj.IsA(UsdShade.NodeGraph)

    def _on_stage_event(self, event):
        """Called with omni.usd.context when stage event"""
        if event.type == int(omni.usd.StageEventType.SELECTION_CHANGED):
            self._on_kit_selection_changed()

    def _on_kit_selection_changed(self):
        """The selection in kit is changed"""
        self._selection_changed()

    def _get_connected_source(self, input):
        if not input.HasConnectedSource():
            return

        # The result is (<pxr.UsdShade.ConnectableAPI>, 'out', pxr.UsdShade.AttributeType.Output)
        source, source_name, source_type = input.GetConnectedSource()

        if source_type == UsdShade.AttributeType.Output:
            output = source.GetOutput(source_name)
        else:  # UsdShade.AttributeType.Input
            # Input-to-input connections. In UsdShade it's possible.
            output = source.GetInput(source_name)

        input_attr = input.GetAttr()
        output_attr = output.GetAttr()

        self.__reversed_connections[output_attr.GetPrim().GetPath()].add(input_attr.GetPrim().GetPath())

        return output.GetAttr()

    @property
    def pause(self):
        return self.__pause

    @pause.setter
    def pause(self, enabled):
        if not self.nodes or (self.__pause == enabled):
            return

        self.__pause = enabled

        prim_path = self.nodes[0].GetPath()
        prop_path = prim_path.AppendProperty("paused")

        omni.kit.commands.execute(
            "ChangePropertyCommand", prop_path=prop_path, value=self.__pause, prev=not self.__pause
        )

        if not self.__pause and self.__locked_attributes:
            omni.kit.commands.execute("UnlockSpecs", spec_paths=list(self.__locked_attributes))
            self.__locked_attributes.clear()

    @property
    def name(self, item=None):
        if isinstance(item, Usd.Prim):
            return item.GetPath().name
        elif isinstance(item, Usd.Attribute):
            display_name = item.GetDisplayName()
            if display_name:
                return display_name
            if UsdShade.Input.IsInput(item):
                return UsdShade.Input(item).GetBaseName()
            if UsdShade.Output.IsOutput(item):
                return UsdShade.Output(item).GetBaseName()
        elif isinstance(item, self.AttributeGroup):
            return item.name
        raise PrimNotSupportedError(f"Can't get name for object of unknown type: '{type(item)}' object: '{item}'")

    @name.setter
    def name(self, value, item=None):
        if isinstance(item, Usd.Attribute):
            # TODO: Command
            # For now we can only set the name of the port
            display_group = None
            if "|" in value:
                display_group = value.split("|")[0]
                value = value.split("|")[1]

            item.SetDisplayName(value)

            if display_group:
                item.SetDisplayGroup(display_group)

            # Toggle selection to update property window
            selection = omni.usd.get_context().get_selection()
            selection.set_prim_path_selected(item.GetPrim().GetPath().pathString, True, True, True, True)

            # TODO: Find a way to rebuild the specific port only
            self._item_changed(None)
        elif isinstance(item, self.AttributeGroup):
            # TODO
            pass
        elif isinstance(item, Usd.Prim):
            old_path = item.GetPath()
            new_path = old_path.GetParentPath().AppendChild(value)
            if new_path == old_path:
                return
            omni.kit.commands.execute("MovePrim", path_from=old_path, path_to=new_path)

    @property
    def type(self, item=None):
        if not item or isinstance(item, self.AttributeGroup):
            return None

        item_type = None

        if isinstance(item, Usd.Prim):
            if item.IsA(UsdShade.Shader):
                item_path = item.GetPath()
                item_type = self.__shading_node_type_cache.get(item_path, None)

                if item_type:
                    return item_type

                shader = UsdShade.Shader(item)
                source_asset = shader.GetSourceAsset("mdl")
                if source_asset:
                    source_asset = source_asset.path
                    sub_identifier = shader.GetSourceAssetSubIdentifier("mdl")
                    # Check MDL Registry
                    shading_node = ShaderRegistry().Get("mdl").get_node_by_asset_and_id(source_asset, sub_identifier)
                    if shading_node:
                        item_type = shading_node.category
                        self.__shading_node_type_cache[item_path] = item_type

            elif item.IsA(UsdShade.NodeGraph):
                # Use the display group as a type
                display_group_attr = item.GetAttribute(UsdUI.Tokens.uiDisplayGroup)
                display_group = display_group_attr.Get()
                if display_group:
                    item_type = display_group

        elif isinstance(item, Usd.Attribute):
            if item.GetPrim().IsA(UsdShade.Material) and UsdShade.Output.IsOutput(item):
                item_type = "material"

            # Check the render type first
            else:
                if UsdShade.Input.IsInput(item):
                    item_type = UsdShade.Input(item).GetRenderType()

                elif UsdShade.Output.IsOutput(item):
                    item_type = UsdShade.Output(item).GetRenderType()

        else:
            raise PrimNotSupportedError(f"Can't get type for object of unknown type: '{type(item)}' object: '{item}'")

        if not item_type:
            item_type = item.GetTypeName()

        return item_type

    def _is_prim_hidden(self, prim):
        while not prim.IsPseudoRoot():
            if prim.GetMetadata("hide_in_stage_window"):
                return True
            prim = prim.GetParent()
        return False

    @property
    def nodes(self, item: Usd.Prim = None) -> Optional[List[Usd.Prim]]:
        """
        The list of sub-nodes. When item is None, return the list of nodes in
        the model.
        """
        if item is None:
            return self.__materials_to_begin_with

        if not item:
            # It happens when prim is deleted
            return

        if not item.IsA(UsdShade.Material) and not item.IsA(UsdShade.NodeGraph):
            # Regular shaders don't have children
            return None

        stage = self.__get_stage()
        if item is None:
            item_path = None
        else:
            item_path = item.GetPath()

        cache = self.__root_to_hirarchy.get(item_path, None)
        if cache is None:
            cache: List[Usd.Prim] = []
            self.__root_to_hirarchy[item_path] = cache

            if item is None:
                roots: List[Usd.Prim] = self.__materials_to_begin_with
            else:
                roots: List[Usd.Prim] = [item]

            for root_prim in roots:
                for child in root_prim.GetChildren():
                    if self._is_prim_hidden(child):
                        continue

                    child_path = child.GetPath()
                    if child_path in cache:
                        continue

                    if child.IsA(UsdShade.Shader) or child.IsA(UsdShade.NodeGraph) or child.IsA(UsdUI.Backdrop):
                        cache.append(child_path)
                        if child_path not in self.__root_to_hirarchy:
                            self.__root_to_hirarchy[child_path] = None

        return [stage.GetPrimAtPath(path) for path in cache]

    @property
    def ports(self, item=None):
        """
        The list of sub-ports. `item` can be a node or a port.
        """
        if isinstance(item, self.AttributeGroup):
            stage = self.__get_stage()
            if item.name == "Material Flags":
                return []

            return [stage.GetObjectAtPath(path) for path in item.child_paths]
        elif (
            isinstance(item, Usd.Prim)
            and item
            and (item.IsA(UsdShade.Material) or item.IsA(UsdShade.Shader) or item.IsA(UsdShade.NodeGraph))
        ):
            conn = UsdShade.ConnectableAPI(item)
        else:
            return

        all_attributes = []

        # if output port is connected to a node that has been hidden, hide the port
        if item.IsA(UsdShade.Material):
            outputs_by_context = {}

            material = UsdShade.Material(item)
            for output in material.GetOutputs(False):
                connected = output.GetConnectedSource()
                if not connected or not self._is_prim_hidden(connected[0].GetPrim()):
                    output_attr = output.GetAttr()

                    # i.e. outputs:mdl:displacement or outputs:surface
                    parts = output_attr.GetName().replace("outputs:", "").split(":")
                    key = ""
                    if len(parts) == 2:
                        key = parts[0]

                    if not key in outputs_by_context:
                        outputs_by_context[key] = []
                    outputs_by_context[key].append(output_attr)

            # sort
            keys = list(outputs_by_context.keys())
            keys.sort()

            all_attributes = []
            for key in keys:
                outputs_by_context[key].sort(key=lambda output_attr: output_attr.GetName())
                all_attributes.extend(outputs_by_context[key])
        else:
            all_attributes = [c.GetAttr() for c in conn.GetOutputs()]

        all_attributes += [c.GetAttr() for c in conn.GetInputs() if c.GetConnectability() == UsdShade.Tokens.full]

        groups: Dict[str, self.AttributeGroup] = {}
        result = []
        stage = self.__get_stage()

        for a in all_attributes:
            if a.HasAuthoredDisplayGroup():
                display_group = a.GetDisplayGroup()

                # For Now We Skil Material Flags to clean up the nodes
                # Should it be an options? not sure one really even wants to connect that in the graph?
                if display_group == "Material Flags":
                    continue

                if display_group not in groups:
                    group = self.AttributeGroup(stage, display_group)
                    state = a.GetCustomDataByKey("displayGroup:state")
                    if state == GraphModel.ExpansionState.CLOSED.name.lower():
                        group.state = GraphModel.ExpansionState.CLOSED
                    groups[display_group] = group
                    result.append(group)
                groups[display_group].child_paths.append(a.GetPath())
            else:
                result.append(a)

        return result

    @ports.setter
    def ports(self, value, item=None):
        new_ports = value

        # Check which ports we need to delete. self[item].ports is a mix of
        # Attribute and AttributeGroup, we need to flatten it to have the list
        # with Attribute only.
        stage = self.__get_stage()
        old_ports: List[Usd.Attribute] = []
        for port in self[item].ports:
            if isinstance(port, Usd.Attribute):
                old_ports.append(port)
            elif isinstance(port, self.AttributeGroup):
                old_ports += [stage.GetObjectAtPath(path) for path in port.child_paths]

        ports_to_remove = []
        for port in old_ports:
            if port not in new_ports:
                ports_to_remove.append(port)

        prim = item if isinstance(item, Usd.Prim) else port.GetPrim() if old_ports else None

        for port in ports_to_remove:
            # TODO: Command
            name = port.GetName()
            prim.RemoveProperty(name)

        # TODO: Command
        prim.SetPropertyOrder([port.GetName() for port in new_ports])

    @property
    def inputs(self, item):
        if isinstance(item, Usd.Attribute):
            attribute = item
            if UsdShade.Input.IsInput(item):
                source = self._get_connected_source(UsdShade.Input(attribute))
                return [source] if source else []

    @inputs.setter
    def inputs(self, value, item=None):
        undo_group_started = False

        if isinstance(item, Usd.Prim) and item.IsA(UsdShade.NodeGraph):
            # Request to connect something to the node itself. We need to create a new port
            if not value:
                return

            prim = item
            prim_path = item.GetPath()
            usdshade_input = None
            connectable_api = UsdShade.ConnectableAPI(prim)

            for source in value:
                if UsdShade.Input.IsInput(source):
                    source_output = UsdShade.Input(source)
                elif UsdShade.Output.IsOutput(source):
                    source_output = UsdShade.Output(source)
                else:
                    continue

                # We are going to use commands, so start the group
                if not undo_group_started:
                    undo_group_started = True
                    omni.kit.undo.begin_group()

                # Unique name for the new port
                source_name = source_output.GetBaseName()
                input_name = source_name
                counter = 1
                while True:
                    input_ = connectable_api.GetOutput(input_name)
                    if not input_:
                        break

                    input_name = "{}{:02d}".format(source_name, counter)
                    counter += 1

                # Create a new port with the name and type of the first available
                omni.kit.commands.execute(
                    "CreateOutputPortCommand",
                    prim_path=prim_path,
                    port_name=input_name,
                    port_type=source_output.GetTypeName(),
                )
                usdshade_input = connectable_api.GetOutput(input_name)
                copy_input_metadata(source_output, usdshade_input)
                item = usdshade_input.GetAttr()

                break

        elif isinstance(item, Usd.Attribute):
            # Request to connect something to the attribute
            attribute = item
            if UsdShade.Input.IsInput(attribute):
                usdshade_input = UsdShade.Input(attribute)
            elif UsdShade.Output.IsOutput(attribute):
                usdshade_input = UsdShade.Output(attribute)
            else:
                return
        else:
            # Unknown request to connect
            return

        if not usdshade_input:
            if undo_group_started:
                omni.kit.undo.end_group()
            return

        if not undo_group_started:
            undo_group_started = True
            omni.kit.undo.begin_group()

        attr_path = item.GetPath()

        if usdshade_input.HasConnectedSource():
            omni.kit.commands.execute("UsdShadeDisconnectSourceCommand", target=usdshade_input)
            if self.pause:

                async def lock_specs(attr_path):
                    for _ in range(2):
                        await omni.kit.app.get_app().next_update_async()

                    self.__locked_attributes.add(attr_path)
                    omni.kit.commands.execute("LockSpecs", spec_paths=[attr_path])

                asyncio.ensure_future(lock_specs(attr_path))

        for source in value or []:
            if isinstance(source, Usd.Prim) and source.IsA(UsdShade.NodeGraph):
                # Request to create a new connection from the node itself. We need to create a new port.

                # Generate unique name for the new plug
                connectable_api = UsdShade.ConnectableAPI(source)
                base_name = usdshade_input.GetBaseName()
                proposed_name = base_name
                proposed_id = 0
                while connectable_api.GetInput(proposed_name):
                    proposed_id += 1
                    proposed_name = f"{base_name}{proposed_id}"
                # Create a new plug
                omni.kit.commands.execute(
                    "CreateInputPortCommand",
                    prim_path=source.GetPath(),
                    port_name=proposed_name,
                    port_type=usdshade_input.GetTypeName(),
                )
                source_input = connectable_api.GetInput(proposed_name)
                copy_input_metadata(usdshade_input, source_input)

            elif isinstance(source, Usd.Attribute) and isinstance(item, Usd.Attribute):
                if not can_connect(self, source, item):
                    continue

                if UsdShade.Input.IsInput(source):
                    source_input = UsdShade.Input(source)
                elif UsdShade.Output.IsOutput(source):
                    source_input = UsdShade.Output(source)
                else:
                    continue

            if self.pause and (attr_path in self.__locked_attributes):
                omni.kit.commands.execute("UnlockSpecs", spec_paths=[attr_path])
                self.__locked_attributes.remove(attr_path)

            omni.kit.commands.execute("ConnectUsdShadeToSourceCommand", target=usdshade_input, source=source_input)

        omni.kit.undo.end_group()

    @property
    def outputs(self, item):
        if isinstance(item, Usd.Attribute):
            attribute = item
            if UsdShade.Output.IsOutput(attribute):
                source = self._get_connected_source(UsdShade.Output(attribute))
                return [source] if source else []

    @outputs.setter
    def outputs(self, value, item=None):
        pass

    @property
    def expansion_state(self, item=None):
        if isinstance(item, self.AttributeGroup):
            return item.state

        if not isinstance(item, Usd.Prim):
            return self.ExpansionState.OPEN

        node_graph_node = UsdUI.NodeGraphNodeAPI(item)
        state_attr = node_graph_node.GetExpansionStateAttr()
        if state_attr.Get() == None:
            node_graph_node.CreateExpansionStateAttr("open")
            return self.ExpansionState.OPEN

        if state_attr.Get() == "open":
            return self.ExpansionState.OPEN
        elif state_attr.Get() == "minimized":
            return self.ExpansionState.MINIMIZED
        elif state_attr.Get() == "closed":
            return self.ExpansionState.CLOSED

    @expansion_state.setter
    def expansion_state(self, value: GraphModel.ExpansionState, item: Any = None):
        def set_state(item):
            node_graph_node = UsdUI.NodeGraphNodeAPI(item)
            state_attr = node_graph_node.GetExpansionStateAttr()
            state_attr.Set(value.name.lower())

        if isinstance(item, self.AttributeGroup):
            if item.state != value:
                item.state = value
                stage = self.__get_stage()
                attrs = [stage.GetObjectAtPath(path) for path in item.child_paths if path]

                with Sdf.ChangeBlock():
                    for attr in attrs:
                        if attr:
                            attr.SetCustomDataByKey("displayGroup:state", value.name.lower())

                # TODO: It's not a good idea to serialize collapsed/expanded
                # state to USD metadata. Tf.Notice doesn't always detect
                # changes. And we need to call _item_changed. We need to
                # serialize it to attribute.
                self.__dirty_prim_paths = []
                self.__dirty_prop_paths = []
                self._item_changed(None)
            return

        if isinstance(item, Usd.Prim):
            if item.IsA(UsdShade.Material):
                for child_item in item.GetAllChildren():
                    set_state(child_item)
            else:
                set_state(item)

        self._item_changed(None)

    @property
    def position(self, item=None):
        result = self.__positions.get(item.GetPath(), None)
        if result:
            return result

        # Caching position for fastest access
        if isinstance(item, Usd.Attribute):
            # TODO: Temporary place to store metadata for position of the attribute
            object_with_metadata = item.GetPrim()
            if UsdShade.Input.IsInput(item):
                metadata_key = UsdUI.Tokens.uiNodegraphNodePos + ":input"
            elif UsdShade.Output.IsOutput(item):
                metadata_key = UsdUI.Tokens.uiNodegraphNodePos + ":output"

            if object_with_metadata.HasMetadataDictKey("customData", metadata_key):
                result = object_with_metadata.GetMetadataByDictKey("customData", metadata_key)
                self.__positions[item.GetPath()] = result
                return result
        elif item.HasAPI(UsdUI.NodeGraphNodeAPI):
            node_graph_node = UsdUI.NodeGraphNodeAPI(item)
            pos_attr = node_graph_node.GetPosAttr()
            if pos_attr:
                result = pos_attr.Get()
                self.__positions[item.GetPath()] = result
                return result

        return None

    @position.setter
    def position(self, value, item=None):
        if value is None:
            omni.kit.commands.execute("UsdUIRemovePositionCommand", prim_path=item.GetPath())
        else:
            self.__positions[item.GetPath()] = value

        if value and self.__current_drive_node == item:
            for node, node_position in self.__driven_nodes.items():
                self[node].position = (value[0] + node_position[0], value[1] + node_position[1])
                # Tell the view that this node is changed
                self._item_changed(node)

    def position_begin_edit(self, item):
        position = self[item].position
        path = item.GetPath()
        self.__positions_on_begin[path] = position

        # If it's a backdrop, send the position_begin event to all the related nodes
        if position and not self.__current_drive_node and self[item].type == "Backdrop":
            stage = self.__get_stage()
            parent_path = path.GetParentPath()
            self.__current_drive_node = item
            size = self[item].size
            for node_path in self.__root_to_hirarchy.keys():
                if node_path == path or parent_path != node_path.GetParentPath():
                    continue

                node = stage.GetPrimAtPath(node_path)

                node_position = self[node].position
                if not node_position or not position:
                    continue

                # Check if the node is inside the backdrop
                if (
                    node_position[0] < position[0]
                    or node_position[1] < position[1]
                    or node_position[0] > position[0] + size[0]
                    or node_position[1] > position[1] + size[1]
                ):
                    continue

                # Save the position of the node relative to the backdrop
                self.__driven_nodes[node] = (node_position[0] - position[0], node_position[1] - position[1])

                self.position_begin_edit(node)
        elif not self.__current_drive_node:
            # The current node is the drive node.
            self.__current_drive_node = item
            # The rest of selection are driven nodes.
            selection = self.selection
            # TODO: When moving input/output of compound, the selection has a
            # compound node, not input/output. So the Material Graph thinks
            # that the compound node is driven by input/output. Solution:
            # implement the multiselection moving logic in graph view.
            # Multiselection is something everyone wants to have, so it would
            # be nicer to make it available to everyone.
            if item in selection:
                for node in selection:
                    if node == item:
                        continue
                    node_position = self[node].position
                    if not node_position or not position:
                        continue

                    self.__positions_on_begin[node.GetPath()] = node_position
                    self.__driven_nodes[node] = (node_position[0] - position[0], node_position[1] - position[1])

    def position_end_edit(self, item):
        if self.__current_drive_node == item:
            omni.kit.undo.begin_group()

        path = item.GetPath()
        prim = item.GetPrim()
        prev = self.__positions_on_begin.get(path, (0.0, 0.0))
        value = self.__positions[path]

        if prev != value:
            if isinstance(item, Usd.Attribute) or prim.IsA(UsdShade.Material):
                # TODO: Temporary place to store metadata for position of the attribute
                metadata_suffix = None

                if prim.IsA(UsdShade.Material) or UsdShade.Output.IsOutput(item):
                    metadata_suffix = "output"

                elif UsdShade.Input.IsInput(item):
                    metadata_suffix = "input"

                # TODO: Command
                if metadata_suffix:
                    metadata_key = f"{UsdUI.Tokens.uiNodegraphNodePos}:{metadata_suffix}"
                    prim.SetMetadataByDictKey("customData", metadata_key, value)

            else:
                omni.kit.commands.execute(
                    "UsdUINodeGraphNodeSetCommand",
                    attribute=UsdUI.Tokens.uiNodegraphNodePos,
                    prim_path=item.GetPath(),
                    value=value,
                    prev=prev,
                )

        if path in self.__positions_on_begin:
            del self.__positions_on_begin[path]

        if self.__current_drive_node == item:
            for node in self.__driven_nodes:
                self.position_end_edit(node)

            omni.kit.undo.end_group()

            self.__current_drive_node = None
            self.__driven_nodes = {}

    @property
    def size(self, item):
        result = self.__sizes.get(item.GetPath(), None)
        if result:
            return result

        # Caching size for fastest access
        if item.HasAPI(UsdUI.NodeGraphNodeAPI):
            node_graph_node = UsdUI.NodeGraphNodeAPI(item)
            size_attr = node_graph_node.GetSizeAttr()
            if size_attr:
                result = size_attr.Get()
                self.__sizes[item.GetPath()] = result
                return result

    @size.setter
    def size(self, value, item=None):
        path = item.GetPath()
        if path in self.__sizes_on_begin:
            self.__sizes[path] = value

    def size_begin_edit(self, item):
        self.__sizes_on_begin[item.GetPath()] = self[item].size

    def size_end_edit(self, item):
        path = item.GetPath()
        omni.kit.commands.execute(
            "UsdUINodeGraphNodeSetCommand",
            attribute=UsdUI.Tokens.uiNodegraphNodeSize,
            prim_path=item.GetPath(),
            value=self.__sizes[path],
            prev=self.__sizes_on_begin[path],
        )
        self.__sizes_on_begin.pop(path)

    @property
    def description(self, item):
        try:
            type = self[item].type
        except PrimNotSupportedError:
            return
        if type == "Backdrop":
            backdrop = UsdUI.Backdrop(item)
            description_attr = backdrop.GetDescriptionAttr()
            if description_attr:
                return description_attr.Get()

    @description.setter
    def description(self, value, item=None):
        try:
            type = self[item].type
        except PrimNotSupportedError:
            return
        if type == "Backdrop":
            prop_path = item.GetPath().AppendProperty(UsdUI.Tokens.uiDescription)
            omni.kit.commands.execute(
                "ChangePropertyCommand",
                prop_path=prop_path,
                value=value,
                prev=None,
                type_to_create_if_not_exist=Sdf.ValueTypeNames.Token,
            )

    @property
    def display_color(self, item):
        if item.HasAPI(UsdUI.NodeGraphNodeAPI):
            node_graph_node = UsdUI.NodeGraphNodeAPI(item)
            color_attr = node_graph_node.GetDisplayColorAttr()
            if color_attr:
                return color_attr.Get()

    @display_color.setter
    def display_color(self, value, item=None):
        omni.kit.commands.execute(
            "UsdUINodeGraphNodeSetCommand",
            attribute=UsdUI.Tokens.uiNodegraphNodeDisplayColor,
            prim_path=item.GetPath(),
            value=value,
            prev=None,
        )

    @property
    def stacking_order(self, item):
        if self[item].type == "Backdrop":
            return -1

        return 1

    @property
    def selection(self) -> List[Usd.Prim]:
        # TODO: It's slow. Consider using stage directly.
        stage = self.__get_stage()
        if not stage:
            return

        result = []

        kit_selected = set(self._selection.get_selected_prim_paths() or [])

        # Shortcut on the case the selection didn't change
        was_selected = set([prim.GetPath().pathString for prim in self.__selection_cache])
        if kit_selected == was_selected:
            return self.__selection_cache

        for path_name in kit_selected:
            path = Sdf.Path(path_name)
            if path not in self.__root_to_hirarchy and path not in self.__paths_to_begin_with:
                continue

            prim = stage.GetPrimAtPath(path)
            if prim:
                result.append(prim)

        return result

    @selection.setter
    def selection(self, value: list):
        old_selection = set(self._selection.get_selected_prim_paths() or [])
        new_selection = set([prim.GetPath().pathString for prim in value or []])

        if old_selection != new_selection:
            # Selection is different from Kit
            self.__selection_cache = value
            omni.kit.commands.execute(
                "SelectPrimsCommand",
                old_selected_paths=list(old_selection),
                new_selected_paths=list(new_selection),
                expand_in_stage=True,
            )
        elif self.__selection_cache != value:
            # Happens when there was selected input node and now it's output
            # node selected
            self.__selection_cache = value
            self._selection_changed()

    def set_selected_nodes_state(self, state: GraphModel.ExpansionState):
        """change the state of all the selected nodes"""
        for prim in self.selection:
            if isinstance(prim, Usd.Prim):
                node_graph_node = UsdUI.NodeGraphNodeAPI(prim)
                state_attr = node_graph_node.GetExpansionStateAttr()
                state_attr.Set(state.name.lower())

        self._item_changed(None)

    @property
    def icon(self, item):
        """Return icon of the image"""
        if isinstance(item, Usd.Prim):
            # Check UsdUI for icon
            if item.HasAPI(UsdUI.NodeGraphNodeAPI):
                node_graph_node = UsdUI.NodeGraphNodeAPI(item)
                icon_attr = node_graph_node.GetIconAttr()
                if icon_attr:
                    asset_path = icon_attr.Get()
                    if asset_path:
                        resolved = asset_path.resolvedPath
                        if not resolved:
                            resolved = asset_path.path
                        icon_path = Path(resolved)
                        if not icon_path.is_absolute():
                            icon_path = ICONS_PATH.joinpath("mdl-thumbnails").joinpath(icon_path)
                        return f"{icon_path}"

            # Check if the prim contains svg
            if item.HasAttribute(ATTRIBUTE_EMBEDDED_ICON):
                embedded_icon_data = item.GetAttribute(ATTRIBUTE_EMBEDDED_ICON).Get()
                if embedded_icon_data:
                    # TODO: Check it's svg
                    hash_icon_data = hash(embedded_icon_data)
                    # __preview_files is a dict with hash
                    asset_path = self.__preview_files.get(hash_icon_data, None)
                    if not asset_path:
                        with tempfile.NamedTemporaryFile(prefix="Kit.ShadingIcon.", suffix=".svg", delete=False) as f:
                            f.write(embedded_icon_data.encode())
                            asset_path = f.name
                            self.__preview_files[hash_icon_data] = asset_path

                    return asset_path

            if item.IsA(UsdShade.Shader):
                # Icon from the MDL github
                shader = UsdShade.Shader(item)

                source_asset = shader.GetSourceAsset("mdl")
                if source_asset:
                    source_asset = source_asset.path
                    sub_identifier = shader.GetSourceAssetSubIdentifier("mdl")
                    # Check MDL Registry
                    shading_node = ShaderRegistry().Get("mdl").get_node_by_asset_and_id(source_asset, sub_identifier)
                    if shading_node:
                        source_asset_name = os.path.basename(source_asset).split(".")[0]
                        icon_path = ICONS_PATH.joinpath(f"mdl-thumbnails/{source_asset_name}.{shading_node.name}.png")
                        if icon_path.exists():
                            return f"{icon_path}"

    @icon.setter
    def icon(self, value, item=None):
        if isinstance(item, Usd.Prim):
            # Write using UsdUI
            node_graph_node = UsdUI.NodeGraphNodeAPI(item)
            icon_attr = node_graph_node.GetIconAttr()
            asset = Sdf.AssetPath(value)
            # TODO: Command
            icon_attr.Set(asset)

    @property
    def preview(self, item):
        """Return the preview of the image"""
        if isinstance(item, Usd.Prim):
            if (
                self[item].preview_state & GraphModel.PreviewState.OPEN
                and self.__material_preview_producer is not None
                and item.IsA(UsdShade.Material)
            ):
                # GPU Buffer
                self.__material_preview_producer.set_material(item.GetPath())
                return {
                    "gpu_reference": None,
                    "resolution": self.__material_preview_producer.resolution,
                }

            texture_input = UsdShade.ConnectableAPI(item).GetInput("texture")
            if texture_input and not texture_input.HasConnectedSource():
                asset_path = texture_input.GetAttr().Get()
                if asset_path:
                    return asset_path.resolvedPath

    @preview.setter
    def preview(self, value, item=None):
        # TODO: Not implemented
        pass

    @property
    def preview_state(self, item) -> GraphModel.PreviewState:
        if isinstance(item, Usd.Prim):
            if item.HasMetadataDictKey("customData", "ui:nodegraph:node:previewState:open"):
                is_open = item.GetMetadataByDictKey("customData", "ui:nodegraph:node:previewState:open")
            else:
                is_open = False

            if is_open:
                return GraphModel.PreviewState.OPEN
        return GraphModel.PreviewState.NONE

    @preview_state.setter
    def preview_state(self, value: GraphModel.PreviewState, item=None):
        if isinstance(item, Usd.Prim):
            is_open = not not value & GraphModel.PreviewState.OPEN
            item.SetMetadataByDictKey("customData", "ui:nodegraph:node:previewState:open", is_open)
            self._item_changed(None)

    def create_node(
        self,
        parent_item,
        prim_type,
        sub_identifier,
        source_asset,
        position=None,
        attributes_to_set=None,
    ):
        """Create a new shading node with the given identifier at the given MDL asset"""
        parent_path = parent_item.GetPath()

        if prim_type == "Backdrop":
            omni.kit.commands.execute(
                "CreateUsdUIBackdropCommand", parent_path=parent_path, identifier=prim_type, position=position
            )
        elif prim_type == "NodeGraph":
            omni.kit.commands.execute(
                "NewUsdShadeNodeGraphCommand", parent_path=parent_path, identifier=prim_type, position=position
            )
        elif prim_type == "Shader":
            if source_asset == "SDR":
                omni.kit.commands.execute(
                    "NewUsdShadeNodeFromSdrCommand",
                    parent_path=parent_path,
                    identifier=sub_identifier,
                    position=position,
                )
            else:
                omni.kit.commands.execute(
                    "NewUsdShadeNodeCommand",
                    parent_path=parent_path,
                    source_asset=source_asset,
                    sub_identifier=sub_identifier,
                    position=position,
                    node=ShaderRegistry().Get("mdl").get_node_by_asset_and_id(source_asset, sub_identifier),
                )
        elif prim_type == "ImportCompound":
            omni.kit.commands.execute(
                "ImportCompoundCommand",
                parent_path=parent_path,
                source_asset=source_asset,
                identifier=sub_identifier,
                position=position,
                attributes_to_set=attributes_to_set,
            )

    def set_material_preview_producer(self, material_preview_producer: MaterialPreviewProducer):
        self.__material_preview_producer = material_preview_producer

    def _update_dirty(self):
        """
        Create/remove dirty items that was collected from TfNotice. Can be
        called any time to pump changes.
        """
        dirty_prim_paths = set(self.__dirty_prim_paths)
        self.__dirty_prim_paths = []

        dirty_props_paths = set(self.__dirty_prop_paths)
        self.__dirty_prop_paths = []

        regenerate = False
        changed_prim_paths = set()

        stage = self.__get_stage()
        # Check if dirty prims belong to this network
        for path in dirty_prim_paths:
            prim = stage.GetPrimAtPath(path)
            if path not in self.__root_to_hirarchy:
                # removed the graph's parent or graph itself
                for root_path in self.__paths_to_begin_with:
                    if root_path.HasPrefix(path) and not prim:
                        self._item_changed(None)
                        return

                parent_path = path.GetParentPath()
                is_in_hirarchy = parent_path in self.__root_to_hirarchy
                is_in_root = parent_path in self.__paths_to_begin_with
                if is_in_hirarchy or is_in_root:
                    # Prim is just created
                    parent = None
                    if is_in_root:
                        parent = self.__root_to_hirarchy.get(None, None)
                    if parent is None:
                        parent = self.__root_to_hirarchy.get(parent_path, None)

                    if parent is not None:
                        parent.append(path)
                        self.__root_to_hirarchy[path] = None
                        regenerate = True

                continue

            if not prim:
                # Prim is just removed
                parent_path = path.GetParentPath()
                if parent_path in self.__root_to_hirarchy:
                    self.__root_to_hirarchy.pop(parent_path)
                self.__root_to_hirarchy.pop(path)

                # Remove connections
                for connected_to in self.__reversed_connections.pop(path, []):
                    self.__remove_connections(connected_to, path)

                # Remove positions
                self.__positions.pop(path, None)
                self.__positions_on_begin.pop(path, None)

                regenerate = True
            else:
                # Prim is changed
                changed_prim_paths.add(path)

        if regenerate:
            # Regenerate everything. No necessary to continue.
            self._item_changed(None)
            return

        for prop_path in dirty_props_paths:
            path = prop_path.GetParentPath()
            if path in changed_prim_paths or path not in self.__root_to_hirarchy:
                continue

            prop_name = prop_path.name
            if prop_name == UsdUI.Tokens.uiNodegraphNodePos:
                if path in self.__positions:
                    # Delete the cache so the next time it will be regenerated
                    del self.__positions[path]
                changed_prim_paths.add(path)
            elif prop_name == UsdUI.Tokens.uiNodegraphNodeSize:
                if path in self.__sizes:
                    # Delete the cache so the next time it will be regenerated
                    del self.__sizes[path]
                    # TODO: The next two lines are temporary before we don't
                    # have on_size_changed callback
                    self._item_changed(None)
                    return
                changed_prim_paths.add(path)
            elif prop_name == UsdUI.Tokens.uiDescription:
                self._item_changed(None)
                return
            elif prop_name == UsdUI.Tokens.uiNodegraphNodeDisplayColor:
                self._item_changed(None)
                return
            elif prop_name == ATTRIBUTE_EMBEDDED_ICON:
                self._item_changed(None)
                return
            elif prop_name == "inputs:texture":
                self._item_changed(None)
                return
            else:
                attribute = self._stage.GetObjectAtPath(prop_path)
                if not attribute:
                    # Property is removed
                    self._item_changed(None)
                    return

                if UsdShade.Input.IsInput(attribute) or UsdShade.Output.IsOutput(attribute):
                    if attribute.HasAuthoredConnections():
                        connections = attribute.GetConnections()
                        if not connections:
                            # Next time it will not have AuthoredConnections
                            attribute.ClearConnections()

                        # Connection is changed. Regenerate all.
                        self._item_changed(None)
                        return
                    # else: It's just an attribute change. The graph is not changed

        for path in changed_prim_paths:
            prim = self._stage.GetPrimAtPath(path)
            self._item_changed(prim)

    @Trace.TraceFunction
    def _on_objects_changed(self, notice, sender):
        """Called by Usd.Notice.ObjectsChanged"""
        prims_changed = []
        props_changed = []

        for p in notice.GetResyncedPaths():
            if p.IsAbsoluteRootOrPrimPath():
                prims_changed.append(p)
            if p.IsPropertyPath():
                props_changed.append(p)

        if not prims_changed or not props_changed:
            for p in notice.GetChangedInfoOnlyPaths():
                if p.IsAbsoluteRootOrPrimPath():
                    prims_changed.append(p)
                if p.IsPropertyPath():
                    props_changed.append(p)

        if not prims_changed and not props_changed:
            return

        # if any of the properties under info have changed then we need to add the prim
        # itself in order to ensure that the widget redraws
        if props_changed:
            material_prim_path = self.__materials_to_begin_with[0].GetPath()

            for prop in props_changed:
                # remove the item

                if prop.name.startswith("info:"):
                    prims_changed.append(self.__materials_to_begin_with[0].GetPath())

                    # clear prim from cache if any of the info properties have changed.
                    self.__shading_node_type_cache.pop(prop.GetParentPath(), None)
                    break

        self.__dirty_prim_paths += prims_changed
        self.__dirty_prop_paths += props_changed

        # Update in the next frame. We need it because we want to accumulate the affected prims
        if self.__prim_changed_task is None or self.__prim_changed_task.done():
            self.__prim_changed_task = asyncio.ensure_future(self.__delayed_prim_changed())

    @handle_exception
    @Trace.TraceFunction
    async def __delayed_prim_changed(self):
        """Called to pump changes at the next frame after the changes received"""
        await omni.kit.app.get_app().next_update_async()

        self.__prim_changed_task = None

        # Pump the changes to the model.
        self._update_dirty()

    def __get_stage(self):
        return self._usd_context.get_stage()

    def __remove_connections(self, prim_path, connection_to_path):
        """
        Scans prim_path and removes all the connections to
        connection_to_path.
        """

        prim = self.__get_stage().GetPrimAtPath(prim_path)
        if not prim:
            return

        connectable_api = UsdShade.ConnectableAPI(prim)
        for usdshade_input in connectable_api.GetInputs():
            sources = usdshade_input.GetRawConnectedSourcePaths()
            if not sources:
                continue

            for source in sources:
                if source.HasPrefix(connection_to_path):
                    usdshade_input.ClearSource()
                    break
