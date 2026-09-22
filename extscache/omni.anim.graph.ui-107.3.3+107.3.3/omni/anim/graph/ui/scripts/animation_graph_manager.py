import carb
import omni.anim.graph.core as ag
import omni.stageupdate
from pxr import Usd, UsdUtils, Sdf, Tf
import AnimGraphSchema
from .animation_graph_error_utils import asset_error_to_message, ERROR_CODE_DEPS_ERROR_INDEX
from .node_graph import NodeGraphRoot
from .sparse_list import SparseList
import asyncio
from typing import Dict, Optional, Union, Callable
import usdrt

class AnimationGraphManager:
    def __init__(self):
        self._node_graph_dict: Dict[Sdf.Path, NodeGraphRoot] = {}

        self._create_callbacks: SparseList[Callable[[NodeGraphRoot], None]] \
            = SparseList[Callable[[NodeGraphRoot], None]]()

        self._destroy_callbacks: SparseList[Callable[[NodeGraphRoot], None]] \
            = SparseList[Callable[[NodeGraphRoot], None]]()

        self._move_callbacks: SparseList[Callable[[Sdf.Path, Sdf.Path], None]] \
            = SparseList[Callable[[Sdf.Path, Sdf.Path], None]]()
        self._stage: Optional[Usd.Stage] = None
        self._stage_update = omni.stageupdate.get_stage_update_interface()
        self._stage_subscription = self._stage_update.create_stage_update_node(
            "AnimationGraph",
            on_attach_fn=self._on_attach,
            on_detach_fn=self._on_detach
        )
        self._usd_listener = Tf.Notice.Register(Usd.Notice.ObjectsChanged, self._process_usd_change, None)
        self._compile_errors = dict()
        self._compile_events_sub = ag.acquire_interface().subscribe_to_compile_events(self._on_compile_events)

    def destroy(self):
        if self._compile_events_sub:
            ag.acquire_interface().unsubscribe_to_compile_events(self._compile_events_sub)
        self._usd_listener = None
        self._stage_subscription = None
        self._stage_update = None
        self._on_detach()
        self._move_callbacks = None
        self._destroy_callbacks = None
        self._create_callbacks = None
        self._node_graph_dict = None

    def _on_compile_events(self, graph_path: str, evt: ag.CompileEvent):
        if not self._node_graph_dict:
            return
        graph = self._node_graph_dict.get(Sdf.Path(graph_path))
        if graph is not None:
            if evt.type == omni.anim.graph.core.CompileEventType.COMPILE_START:
                if graph in self._compile_errors:
                    asset_errors = self._compile_errors[graph]
                    for asset_path in asset_errors.keys():
                        found, result_graph, result_node = graph.search_node(Sdf.Path(asset_path))
                        if found:
                            if asset_path in self._compile_errors[graph]:
                                compile_errors = self._compile_errors[graph][asset_path]
                                result_node.set_compile_errors(result_node, None)
                    asset_errors.clear()
            elif evt.type == omni.anim.graph.core.CompileEventType.COMPILE_STOP:
                if graph in self._compile_errors:
                    asset_errors = self._compile_errors[graph]
                    for asset_path in asset_errors.keys():
                        found, result_graph, result_node = graph.search_node(Sdf.Path(asset_path))
                        if found:
                            if asset_path in self._compile_errors[graph]:
                                compile_errors = self._compile_errors[graph][asset_path]
                                result_node.set_compile_errors(result_node, compile_errors)
            elif evt.type == omni.anim.graph.core.CompileEventType.COMPILE_ERROR:
                if graph not in self._compile_errors:
                    self._compile_errors[graph] = dict()
                error_msg = asset_error_to_message(self._stage, evt.asset_path, evt.error_code, evt.argument)
                if evt.asset_path not in self._compile_errors[graph]:
                    self._compile_errors[graph][evt.asset_path] = list()
                if error_msg not in self._compile_errors[graph][evt.asset_path]:
                    self._compile_errors[graph][evt.asset_path].append(error_msg)
                    carb.log_error(f"Animation Graph Error:\nGraph Path = {graph_path}\nAsset Path = {evt.asset_path}\nError Message = {error_msg}")
                    # mark all parent nodes as missing dependencies errors
                    parent_prim = self._stage.GetPrimAtPath(Sdf.Path(evt.asset_path)).GetParent()
                    while parent_prim and parent_prim.IsValid() and parent_prim.IsA(AnimGraphSchema.AnimationGraphNode) or parent_prim.IsA(AnimGraphSchema.AnimationGraph):
                        parent_prim_path = parent_prim.GetPath()
                        asset_path = parent_prim_path.pathString
                        if asset_path not in self._compile_errors[graph]:
                            self._compile_errors[graph][asset_path] = list()
                        error_msg = asset_error_to_message(self._stage, asset_path, ERROR_CODE_DEPS_ERROR_INDEX, 0)
                        if error_msg not in self._compile_errors[graph][asset_path]:
                            self._compile_errors[graph][asset_path].append(error_msg)
                        if parent_prim.IsA(AnimGraphSchema.AnimationGraph):
                            break
                        parent_prim = parent_prim.GetParent()

    def get_compile_errors(self, graph: NodeGraphRoot):
        if graph in self._compile_errors:
            return self._compile_errors[graph]
        return None

    def get_node_graph(self, path: Union[Sdf.Path, str]) -> Optional[NodeGraphRoot]:
        return self._node_graph_dict.get(Sdf.Path(path))

    def add_graph_create_callback(self, callback: Callable[[NodeGraphRoot], None]) -> Optional[int]:
        return self._create_callbacks.add(callback)

    def remove_graph_create_callback(self, index: int) -> bool:
        return self._create_callbacks.remove(index)

    def add_graph_destroy_callback(self, callback: Callable[[NodeGraphRoot], None]) -> Optional[int]:
        return self._destroy_callbacks.add(callback)

    def remove_graph_destroy_callback(self, index: int) -> bool:
        return self._destroy_callbacks.remove(index)

    def add_graph_move_callback(self, callback: Callable[[Sdf.Path, Sdf.Path], None]) -> Optional[int]:
        return self._move_callbacks.add(callback)

    def remove_graph_move_callback(self, index: int) -> bool:
        return self._move_callbacks.remove(index)

    def _on_attach(self, stage_id, meters_per_unit):
        cache = UsdUtils.StageCache.Get()
        self._stage = cache.Find(Usd.StageCache.Id.FromLongInt(stage_id))

        usdrtstage = usdrt.Usd.Stage.Attach(stage_id)

        anim_graph_paths = usdrtstage.GetPrimsWithAppliedAPIName("AnimationGraphAPI")
        for anim_graph_path in anim_graph_paths:
            usd_path = Sdf.Path(str(anim_graph_path))
            prim = self._stage.GetPrimAtPath(usd_path)
            self._create_node_graph(prim)

    def _on_detach(self):
        for path, graph in self._node_graph_dict.items():
            self._destroy_node_graph(graph)
        self. _compile_errors.clear()
        self._node_graph_dict.clear()
        self._stage = None

    def _process_usd_change(self, objects_changed, stage):
        if stage is None or stage != self._stage:
            return
        paths_to_add = set()
        paths_to_remove = set()
        for resync_path in objects_changed.GetResyncedPaths():
            if resync_path.IsPrimPath():
                prim = stage.GetPrimAtPath(resync_path)
                if prim:
                    paths_to_add.add(resync_path)
                else:
                    paths_to_remove.add(resync_path)
        for removed_path in paths_to_remove.copy():
            keys = [k for k in self._node_graph_dict.keys()]
            for graph_path in keys:
                if graph_path.HasPrefix(removed_path):
                    for added_path in paths_to_add.copy():
                        moved_path = graph_path.ReplacePrefix(removed_path, added_path)
                        moved_prim = stage.GetPrimAtPath(moved_path)
                        if moved_prim and moved_prim.HasAttribute("lastNodePath"):
                            last_path = Sdf.Path(moved_prim.GetAttribute("lastNodePath").Get())
                            if last_path == graph_path or last_path == moved_path:
                                paths_to_add.remove(added_path)
                                paths_to_remove.remove(removed_path)
                                graph = self._node_graph_dict.pop(graph_path, None)
                                if graph:
                                    self._node_graph_dict[moved_path] = graph
                                    for callback in self._move_callbacks:
                                        if callback:
                                            callback(graph_path, moved_path)

        async def create_node_graph(graph_prim):
            await omni.kit.app.get_app().next_update_async()
            if graph_prim and graph_prim.IsA(AnimGraphSchema.AnimationGraph) and not self._node_graph_dict.get(added_path):
                self._create_node_graph(graph_prim)

        for added_path in paths_to_add:
            asyncio.ensure_future(create_node_graph(stage.GetPrimAtPath(added_path)))
        for path in paths_to_remove:
            removed_graph = self._node_graph_dict.pop(path, None)
            if removed_graph and self._compile_errors is not None:
                self._compile_errors.pop(removed_graph, None)
                self._destroy_node_graph(removed_graph)

    def _create_node_graph(self, prim):
        graph = NodeGraphRoot(prim)
        self._node_graph_dict[prim.GetPath()] = graph
        for callback in self._create_callbacks:
            if callback:
                callback(graph)

    def _destroy_node_graph(self, graph):
        for callback in self._destroy_callbacks:
            if callback:
                callback(graph)
        graph.destroy()
