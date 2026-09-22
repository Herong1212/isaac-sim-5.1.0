from typing import List, Optional

import omni
import OmniGraphSchema
import OmniGraphSchemaTools
from omni.kit.usd_undo import UsdLayerUndo
from pxr import Sdf


class ApplyOmniGraphAPICommand(omni.kit.commands.Command):
    def __init__(
        self, layer: Sdf.Layer = None, paths: Optional[List[Sdf.Path]] = None, graph_path: Sdf.Path = Sdf.Path.emptyPath
    ):
        self._usd_undo = None
        self._layer = layer
        self._paths = paths if paths is not None else []
        self._graph_path = graph_path

    def do(self):
        stage = omni.usd.get_context().get_stage()
        if self._layer is None:
            self._layer = stage.GetEditTarget().GetLayer()
        self._usd_undo = UsdLayerUndo(self._layer)
        for path in self._paths:
            if not stage.GetPrimAtPath(path).HasAPI(OmniGraphSchema.OmniGraphAPI):
                self._usd_undo.reserve(path)
                OmniGraphSchemaTools.applyOmniGraphAPI(stage, path, self._graph_path)

    def undo(self):
        if self._usd_undo is not None:
            self._usd_undo.undo()


class RemoveOmniGraphAPICommand(omni.kit.commands.Command):
    def __init__(self, layer: Sdf.Layer = None, paths: List[Sdf.Path] = None):
        self._usd_undo = None
        self._layer = layer
        self._paths = paths if paths is not None else []

    def do(self):
        stage = omni.usd.get_context().get_stage()
        if self._layer is None:
            self._layer = stage.GetEditTarget().GetLayer()
        self._usd_undo = UsdLayerUndo(self._layer)
        for path in self._paths:
            if stage.GetPrimAtPath(path).HasAPI(OmniGraphSchema.OmniGraphAPI):
                self._usd_undo.reserve(path)
                OmniGraphSchemaTools.removeOmniGraphAPI(stage, path)

    def undo(self):
        if self._usd_undo is not None:
            self._usd_undo.undo()


omni.kit.commands.register(ApplyOmniGraphAPICommand)
omni.kit.commands.register(RemoveOmniGraphAPICommand)
