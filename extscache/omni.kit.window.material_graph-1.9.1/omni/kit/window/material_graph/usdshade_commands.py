# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = [
    "ConnectUsdShadeToSourceCommand",
    "CreateInputPortCommand",
    "CreateOutputPortCommand",
    "ImportCompoundCommand",
    "NewUsdShadeMaterialCommand",
    "NewUsdShadeNodeCommand",
    "NewUsdShadeNodeGraphCommand",
    "UsdShadeDisconnectSourceCommand",
]
import abc
from typing import Any, Dict, List, Optional, Tuple

import omni.kit.commands
import omni.usd
from omni.usd.commands import CreateShaderPrimFromSdrCommand, DeletePrimsCommand, UsdStageHelper
from pxr import Sdf, Sdr, Tf, Usd, UsdGeom, UsdShade, UsdUI


class NewUsdShadeMaterialCommand(omni.kit.commands.Command, UsdStageHelper):
    def __init__(
        self,
        parent_path: Sdf.Path,
        identifier: str,
        position: Optional[Tuple[int]] = None,
        select_new_prim: bool = False,
        stage: Optional[Usd.Stage] = None,
        context_name: Optional[str] = None,
    ):
        UsdStageHelper.__init__(self, stage, context_name)
        self._created_path = None
        self._parent_path = parent_path
        self._identifier = identifier
        self._position = position
        self._select_new_prim = select_new_prim
        self._selected_prim_paths = None

    def do(self):
        stage = self._get_stage()

        # Make sure that the created parent is of Scope type. Otherwise it has
        # no type:
        # `def "Looks"`
        parent_prim = stage.GetPrimAtPath(self._parent_path)
        if not parent_prim:
            parent_prim = UsdGeom.Scope.Define(stage, self._parent_path)

        self._created_path = Sdf.Path(
            omni.usd.get_stage_next_free_path(stage, self._parent_path.AppendElementString(self._identifier), False)
        )

        material = UsdShade.Material.Define(stage, self._created_path)
        with Sdf.ChangeBlock():
            render_context = "mdl"
            material.CreateSurfaceOutput(render_context)
            material.CreateDisplacementOutput(render_context)
            material.CreateVolumeOutput(render_context)
            prim = material.GetPrim()

            if self._position:
                node_graph_node = UsdUI.NodeGraphNodeAPI.Apply(prim)
                pos_attr = node_graph_node.CreatePosAttr()
                pos_attr.Set(self._position)

        if self._select_new_prim:
            selection = self._get_context().get_selection()
            self._selected_prim_paths = selection.get_selected_prim_paths()
            selection.set_prim_path_selected(self._created_path.pathString, True, True, True, True)

    def undo(self):
        delete_cmd = DeletePrimsCommand([self._created_path])
        delete_cmd.do()
        if self._selected_prim_paths is not None:
            selection = self._get_context().get_selection()
            selection.clear_selected_prim_paths()
            for path_str in self._selected_prim_paths:
                selection.set_prim_path_selected(path_str, True, True, False, False)


class NewUsdShadeNodeGraphCommand(omni.kit.commands.Command, UsdStageHelper):
    def __init__(self, parent_path, identifier, position, stage=None):
        UsdStageHelper.__init__(self, stage)
        self._created_path = None
        self._parent_path = parent_path
        self._identifier = identifier
        self._position = position

    def do(self):
        stage = self._get_stage()
        self._created_path = Sdf.Path(
            omni.usd.get_stage_next_free_path(stage, self._parent_path.AppendElementString(self._identifier), False)
        )

        nodegraph = UsdShade.NodeGraph.Define(stage, self._created_path)
        prim = nodegraph.GetPrim()

        if self._position:
            node_graph_node = UsdUI.NodeGraphNodeAPI.Apply(prim)
            pos_attr = node_graph_node.CreatePosAttr()
            pos_attr.Set(self._position)

    def undo(self):
        delete_cmd = DeletePrimsCommand([self._created_path])
        delete_cmd.do()


class NewUsdShadeNodeCommand(omni.kit.commands.Command, UsdStageHelper):
    def __init__(self, parent_path, source_asset, sub_identifier, position, node, stage=None):
        UsdStageHelper.__init__(self, stage)
        self._parent_path = parent_path
        self._source_asset = source_asset
        self._sub_identifier = sub_identifier
        self._position = position
        self._created_path = None
        self._node = node

    def do(self):
        stage = self._get_stage()

        self._created_path = Sdf.Path(
            omni.usd.get_stage_next_free_path(stage, self._parent_path.AppendElementString(self._node.name), False)
        )

        shader = UsdShade.Shader.Define(stage, self._created_path)

        # Inputs
        for parameter in self._node.parameters:
            usdshade_input = shader.CreateInput(parameter.name, parameter.type.usd)

            usdshade_input.SetRenderType(parameter.type.render)

            attr = usdshade_input.GetAttr()

            if parameter.label:
                attr.SetDisplayName(parameter.label)

            if parameter.page:
                attr.SetDisplayGroup(parameter.page)

            if parameter.description:
                usdshade_input.SetDocumentation(parameter.description)

            if parameter.sdrMetaData:
                usdshade_input.SetSdrMetadata(parameter.sdrMetaData)

            if parameter.colorSpace is not None:
                attr.SetColorSpace(parameter.colorSpace)

            for key, data in parameter.customData.items():
                attr.SetCustomDataByKey(key, data)

        for name, returnType in self._node.outputs.items():
            usdshade_output = shader.CreateOutput(name, returnType.usd)

            if returnType.render:
                usdshade_output.SetRenderType(returnType.render)

        shader.SetSourceAsset(self._source_asset, "mdl")
        shader.SetSourceAssetSubIdentifier(self._sub_identifier, "mdl")
        shader.GetImplementationSourceAttr().Set(UsdShade.Tokens.sourceAsset)

        if self._position:
            node_graph_node = UsdUI.NodeGraphNodeAPI.Apply(shader.GetPrim())
            pos_attr = node_graph_node.CreatePosAttr()
            pos_attr.Set(self._position)

        # we select the Prim both so it update its parameters but also is ready to connection using QuickSearch
        omni.usd.get_context().get_selection().set_selected_prim_paths([str(shader.GetPath())], True)

    def undo(self):
        delete_cmd = DeletePrimsCommand([self._created_path])
        delete_cmd.do()


class NewUsdShadeNodeFromSdrCommand(omni.kit.commands.Command):
    def __init__(self, parent_path, identifier, position):
        super().__init__()
        self._parent_path = parent_path
        self._identifier = identifier
        self._position = position

    def do(self):
        shader_prim = CreateShaderPrimFromSdrCommand(self._parent_path, self._identifier, select_new_prim=True).do()

        if shader_prim and self._position:
            node_graph_node = UsdUI.NodeGraphNodeAPI.Apply(shader_prim.GetPrim())
            pos_attr = node_graph_node.CreatePosAttr()
            pos_attr.Set(self._position)

    def undo(self):
        pass


class ConnectUsdShadeToSourceCommand(omni.kit.commands.Command):
    """Undoable UsdShade.Input.ConnectToSource"""

    def __init__(self, target: UsdShade.Input, source: UsdShade.Output):
        super().__init__()
        self._target = target
        self._source = source

    def do(self):
        if self._target and self._source:
            self._target.ConnectToSource(self._source)

            if self._target.GetPrim().IsA(UsdShade.NodeGraph):
                self._target.SetSdrMetadata(self._source.GetSdrMetadata())

        else:
            self._target = None
            self._source = None

    def undo(self):
        if self._target:
            self._target.DisconnectSource()


class UsdShadeDisconnectSourceCommand(omni.kit.commands.Command):
    """Undoable UsdShade.Input.DisconnectSource"""

    def __init__(self, target: UsdShade.Input):
        super().__init__()
        self._target = target
        self._source = None

    def do(self):
        # Get source for undo
        if self._target.HasConnectedSource():
            # The result is (<pxr.UsdShade.ConnectableAPI>, 'out', pxr.UsdShade.AttributeType.Output)
            source, source_name, source_type = self._target.GetConnectedSource()

            if source_type == UsdShade.AttributeType.Output:
                self._source = source.GetOutput(source_name)
            else:  # UsdShade.AttributeType.Input
                # Input-to-input connections. In UsdShade it's possible.
                self._source = source.GetInput(source_name)

            # Disconnect
            self._target.DisconnectSource()

    def undo(self):
        if not self._target or not self._source:
            # It wasn't connected
            return

        self._target.ConnectToSource(self._source)


class ImportCompoundCommand(omni.kit.commands.Command, UsdStageHelper):
    """
    Import compound shader from external USD file.

    ### Arguments:

        `parent_path : Sdf.Path`
            The path of the prim we need to add the new compound to.

        `source_asset : str`
            The path of the external usd file. It's important the default
            prim in this layer is the NodeGraph prim.

        `identifier : str`
            The name of the new prim.

        `position : Optional[List[int]]`
            The position of the new node in the canvas.

        `stage : Optional[int]`
            The stage it's necessary to add the new prim. If None, it takes
            the stage from the USD Context.

        `attributes_to_set: Optional[Dict[Sdf.Path, Any]]`
            Dict that has the list of attributes and values to set after the
            prim is imported.
    """

    def __init__(
        self,
        parent_path: Sdf.Path,
        source_asset: str,
        identifier: str,
        position: Optional[List[int]] = None,
        stage=None,
        path=None,
        attributes_to_set: Optional[Dict[Sdf.Path, Any]] = None,
    ):
        UsdStageHelper.__init__(self, stage)
        self._parent_path = parent_path
        self._source_asset = source_asset
        self._identifier = identifier
        self._position = position
        self._attributes_to_set = attributes_to_set
        self._created_path: Optional[str] = None
        self._path = path

    def do(self):
        stage = self._get_stage()
        source_layer = Sdf.Layer.FindOrOpen(self._source_asset)
        target_layer = stage.GetEditTarget().GetLayer()
        source_path = self._identifier

        if not source_path.startswith("/"):
            source_path = Sdf.Path.absoluteRootPath.AppendChild(self._identifier)

        source_path_name = Sdf.Path(source_path).name
        target_path = omni.usd.get_stage_next_free_path(
            stage, self._parent_path.AppendChild(Sdf.Path(source_path).name).pathString, False
        )
        self._created_path: str = target_path
        target_path = Sdf.Path(target_path)

        # Create spec and copy
        Sdf.CreatePrimInLayer(target_layer, target_path)
        Sdf.CopySpec(source_layer, source_path, target_layer, target_path)
        target_prim = stage.GetPrimAtPath(target_path)

        # remove xformOpOrder. It probably shouldn't be exported.
        if target_prim.HasProperty(UsdGeom.Tokens.xformOpOrder):
            target_prim.RemoveProperty(UsdGeom.Tokens.xformOpOrder)

        # Position
        if self._position:
            node_graph_node = UsdUI.NodeGraphNodeAPI.Apply(target_prim)
            pos_attr = node_graph_node.CreatePosAttr()
            pos_attr.Set(self._position)

        if self._attributes_to_set:
            # Set the given attributes
            for attribute_path, value in self._attributes_to_set.items():
                attribute = stage.GetObjectAtPath(target_path.AppendPath(attribute_path))
                if attribute:
                    if attribute.GetTypeName() == Sdf.ValueTypeNames.Asset:
                        value = Sdf.AssetPath(value)
                    attribute.Set(value)

        # We select the Prim both so it update its parameters but also is ready to connection using QuickSearch
        omni.usd.get_context().get_selection().set_selected_prim_paths([self._created_path], True)

    def undo(self):
        delete_cmd = DeletePrimsCommand([self._created_path])
        delete_cmd.do()


class CreateAbstractPortCommand(omni.kit.commands.Command, UsdStageHelper, metaclass=abc.ABCMeta):
    """
    Base class for CreateInputPortCommand and for CreateOutputPortCommand
    that has the shared code for both.
    """

    def __init__(self, prim_path: Sdf.Path, port_name: str, port_type: Sdf.ValueTypeName, stage=None):
        UsdStageHelper.__init__(self, stage)
        self._prim_path = prim_path
        self._port_name = port_name
        self._port_type = port_type
        self._created_attr_name = None

    @abc.abstractmethod
    def _create_port(self, prim):
        pass

    def do(self):
        stage = self._get_stage()
        prim = stage.GetPrimAtPath(self._prim_path)

        self._created_attr_name = self._create_port(prim)

    def undo(self):
        if self._created_attr_name is None:
            return

        stage = self._get_stage()
        prim = stage.GetPrimAtPath(self._prim_path)
        prim.RemoveProperty(self._created_attr_name)


class CreateInputPortCommand(CreateAbstractPortCommand):
    """
    Create connectable input on the prim

    ### Arguments:

        `prim_path : Sdf.Path`
            The path of the prim we need to add the new port.

        `port_name : str`
            The name of the port. The attribute name will be `inputs:port_name`.

        `port_type : Sdf.ValueTypeName`
            The type of the port.

        `stage : Optional[int]`
            The stage it's necessary to add the new prim. If None, it takes
            the stage from the USD Context.
    """

    def __init__(self, prim_path: Sdf.Path, port_name: str, port_type: Sdf.ValueTypeName, stage=None):
        CreateAbstractPortCommand.__init__(self, prim_path, port_name, port_type, stage)

    def _create_port(self, prim):
        connectable_api = UsdShade.ConnectableAPI(prim)
        usdshade_input = connectable_api.CreateInput(self._port_name, self._port_type)
        return usdshade_input.GetFullName()


class CreateOutputPortCommand(CreateAbstractPortCommand):
    """
    Create connectable output on the prim

    ### Arguments:

        `prim_path : Sdf.Path`
            The path of the prim we need to add the new port.

        `port_name : str`
            The name of the port. The attribute name will be `outputs:port_name`.

        `port_type : Sdf.ValueTypeName`
            The type of the port.

        `stage : Optional[int]`
            The stage it's necessary to add the new prim. If None, it takes
            the stage from the USD Context.
    """

    def __init__(self, prim_path: Sdf.Path, port_name: str, port_type: Sdf.ValueTypeName, stage=None):
        CreateAbstractPortCommand.__init__(self, prim_path, port_name, port_type, stage)

    def _create_port(self, prim):
        connectable_api = UsdShade.ConnectableAPI(prim)
        usdshade_input = connectable_api.CreateOutput(self._port_name, self._port_type)
        return usdshade_input.GetFullName()
