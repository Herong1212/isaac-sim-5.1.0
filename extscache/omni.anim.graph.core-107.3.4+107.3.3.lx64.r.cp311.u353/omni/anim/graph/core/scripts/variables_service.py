import carb
import omni.timeline
import usdrt
from pxr import Sdf, Tf, Usd, Trace
import AnimGraphSchema
import asyncio

GRAPH_VAR_ATTR_PREFIX = "graph:variable:"
ANIM_GRAPH_VAR_ATTR_PREFIX = "anim:graph:variable:"
ANIM_GRAPH_REL = "animationGraph"
DEFAULT_VALUE_ATTR_CUSTOM_DATA = "default"


def refresh_property_window():
    try:
        import omni.kit.window.property
        import omni.kit.commands
        import omni.usd
        selected_paths = omni.usd.get_context().get_selection().get_selected_prim_paths()
        omni.usd.get_context().get_selection().clear_selected_prim_paths()
        omni.kit.window.property.get_window()._window.frame.rebuild()
        omni.usd.get_context().get_selection().set_selected_prim_paths(selected_paths, True)
    except ImportError:
        pass


def notify_updated_variable_prefix(graph_paths):
    try:
        import omni.kit.notification_manager as nm
        nm.post_notification("Anim Graph variable prefix format updated.", duration=7)
    except ImportError:
        carb.log_warn("Anim Graph variable prefix format updated.")

    carb.log_info("Updated Graph Paths:\n" + "\n".join(graph_paths))


class VariablesService:
    def __init__(self):
        self._loading = False
        self._graphs = {}
        self._graph_targets = {}
        self._graph_vars = {}
        self._graph_vars_updated = {}
        self._graph_vars_recreated = {}
        self._usd_listener = None
        self._usd_context = omni.usd.get_context()
        self._stage_event_sub = self._usd_context.get_stage_event_stream().create_subscription_to_pop(
            self._on_stage_event, name=f"omni.anim.graph.ui.{str(__class__)}"
        )
        self._pending_dirty_task = None
        self._pending_prims_added = set()
        self._pending_prims_removed = set()
        self._pending_props_changed = set()
        self._timeline = omni.timeline.get_timeline_interface()

    def destroy(self):
        if self._usd_listener:
            self._usd_listener.Revoke()
            self._usd_listener = None
        self._stage_event_sub = None
        self._graphs = {}
        self._graph_targets = {}
        self._graph_vars = {}
        self._graph_vars_updated = {}
        self._graph_vars_recreated = {}
        if self._pending_dirty_task is not None:
            self._pending_dirty_task.cancel()
            self._pending_dirty_task = None
        self._pending_prims_added.clear()
        self._pending_prims_removed.clear()
        self._pending_props_changed.clear()

    def _on_stage_load(self):
        if self._loading:
            return

        self._loading = True
        has_activity = False
        try:
            import omni.activity.core
            stage_opened_activity = "Stage|Opened|Anim Graph UI"
            omni.activity.core.began(stage_opened_activity)
            has_activity = True
        except ImportError:
            pass

        self._graphs.clear()
        self._graph_vars.clear()
        self._graph_vars_updated.clear()
        self._graph_vars_recreated.clear()
        stage = self._usd_context.get_stage()
        refresh_props = False
        # find all the prims that have the animationGraph relationship applied and assigned
        usdrtstage = usdrt.Usd.Stage.Attach(self._usd_context.get_stage_id())
        anim_graph_paths = usdrtstage.GetPrimsWithAppliedAPIName("AnimationGraphAPI")

        for anim_graph_path in anim_graph_paths:
            usd_path = Sdf.Path(str(anim_graph_path))
            prim = stage.GetPrimAtPath(usd_path)
            refresh_props |= self._sync_graph_targets(stage, prim)

        refresh_props |= self._sync_graph_variables(stage)
        self._loading = False
        if refresh_props:
            refresh_property_window()

        if has_activity:
            omni.activity.core.ended(stage_opened_activity)

    def _on_stage_event(self, event):
        if event.type == int(omni.usd.StageEventType.OPENED):
            self._on_stage_load()
            self._usd_listener = Tf.Notice.Register(Usd.Notice.ObjectsChanged, self._on_usd_objects_changed, None)

    async def _pending_dirty_handler(self):
        await omni.kit.app.get_app().next_update_async()
        self._pending_dirty_task = None
        stage = self._usd_context.get_stage()
        if stage is None:
            return
        refresh_props = False

        # handle prims added
        if len(self._pending_prims_added) > 0:
            prims_added = self._pending_prims_added.copy()
            self._pending_prims_added.clear()
            for prim_added in prims_added:
                prim = stage.GetPrimAtPath(prim_added)
                if prim.IsValid():
                    if prim.HasAPI(AnimGraphSchema.AnimationGraphAPI):
                        refresh_props |= self._sync_graph_targets(stage, prim)
                        refresh_props |= self._sync_graph_variables(stage)

        # handle various cases for prims removed
        if len(self._pending_prims_removed) > 0:
            prims_removed = self._pending_prims_removed.copy()
            self._pending_prims_removed.clear()
            for prim_removed in prims_removed:
                # is this a prim using a graph that was tracked
                if prim_removed in self._graph_targets:
                    graph_path = self._graph_targets[prim_removed]
                    self._graph_targets.pop(prim_removed)
                    self._graphs[graph_path].remove(prim_removed)
                # is this a anim graph being track
                if prim_removed in self._graphs:
                    for prim_path in self._graphs[prim_removed]:
                        self._graph_targets.pop(prim_path)
                        prim = stage.GetPrimAtPath(prim_path)
                        rel = prim.GetRelationship(ANIM_GRAPH_REL)
                        rel.ClearTargets(True)
                        for var in self._graph_vars[prim_removed]:
                            if prim.HasProperty(var):
                                prim.RemoveProperty(var)
                    self._graph_vars.pop(prim_removed)
                    self._graphs.pop(prim_removed)
                    refresh_props = True

        # handle property changes for animationGraph changing
        if len(self._pending_props_changed) > 0:
            props_changed = self._pending_props_changed.copy()
            self._pending_props_changed.clear()
            for prop_changed in props_changed:
                property_prim_path = prop_changed.GetPrimPath()
                prim = stage.GetPrimAtPath(property_prim_path)
                name = prop_changed.name
                if name == ANIM_GRAPH_REL:
                    refresh_props |= self._sync_graph_targets(stage, prim)
                if property_prim_path in self._graph_vars:
                    if property_prim_path not in self._graph_vars_updated:
                        self._graph_vars_updated[property_prim_path] = set()
                    self._graph_vars_updated[property_prim_path].add(name)

            refresh_props |= self._sync_graph_variables(stage)

        if refresh_props:
            refresh_property_window()

    @Trace.TraceFunction
    def _on_usd_objects_changed(self, objects_changed, stage):
        carb.profiler.begin(1, "VariablesService._on_usd_objects_changed")
        if stage is None or stage != self._usd_context.get_stage() or self._timeline.is_playing():
            carb.profiler.end(1)
            return
        dirty_prims_added = set()
        dirty_prims_removed = set()
        dirty_props_changed = set()

        for resync_path in objects_changed.GetResyncedPaths():
            if resync_path.IsPrimPath():
                prim = stage.GetPrimAtPath(resync_path)
                if prim and prim.IsValid():
                    dirty_prims_added.add(resync_path)
                else:
                    dirty_prims_removed.add(resync_path)
            elif resync_path.IsPropertyPath():
                if resync_path.name == ANIM_GRAPH_REL or resync_path.name.startswith(ANIM_GRAPH_VAR_ATTR_PREFIX):
                    dirty_props_changed.add(resync_path)
        for changed_info_only_path in objects_changed.GetChangedInfoOnlyPaths():
            if changed_info_only_path.IsPropertyPath():
                if changed_info_only_path:
                    path_name = changed_info_only_path.name
                    if path_name == ANIM_GRAPH_REL or path_name.startswith(ANIM_GRAPH_VAR_ATTR_PREFIX):
                        dirty_props_changed.add(changed_info_only_path)

        self._pending_prims_added.update(dirty_prims_added)
        self._pending_prims_removed.update(dirty_prims_removed)
        self._pending_props_changed.update(dirty_props_changed)
        if (len(self._pending_prims_added) > 0 or len(self._pending_prims_removed) > 0 or len(self._pending_props_changed) > 0) and self._pending_dirty_task is None:
            self._pending_dirty_task = asyncio.ensure_future(self._pending_dirty_handler())
        carb.profiler.end(1)

    def _sync_graph_targets(self, stage, prim):
        refresh_props = False
        prim_path = prim.GetPath()
        rel = prim.GetRelationship(ANIM_GRAPH_REL)
        anim_graph_targets = rel.GetTargets()
        if len(anim_graph_targets) > 0:
            anim_graph_path = anim_graph_targets[0]
            self._graph_targets[prim_path] = anim_graph_path
            anim_graph_prim = stage.GetPrimAtPath(anim_graph_path)
            if anim_graph_prim.IsValid():
                if anim_graph_path not in self._graphs:
                    self._graphs[anim_graph_path] = set()
                self._graphs[anim_graph_path].add(prim_path)
        else:
            if prim_path in self._graph_targets:
                graph_path = self._graph_targets[prim_path]
                attrs = prim.GetAttributes()
                for attr in attrs:
                    attr_name = attr.GetName()
                    if attr_name.startswith(ANIM_GRAPH_VAR_ATTR_PREFIX) and attr_name in self._graph_vars[graph_path]:
                        prim.RemoveProperty(attr_name)
                        refresh_props = True
                self._graph_targets.pop(prim_path)
                if graph_path in self._graphs:
                    self._graphs[graph_path].remove(prim_path)
        return refresh_props

    def _sync_graph_variables(self, stage):
        refresh_props = False
        updated_prefix_graphs = set()
        for graph_path in self._graphs:
            graph_prim = stage.GetPrimAtPath(graph_path)
            # copy the previous graph vars on the graph
            graph_vars_to_remove = set()
            if graph_path in self._graph_vars:
                graph_vars_to_remove = set(self._graph_vars[graph_path].keys())
            else:
                self._graph_vars[graph_path] = dict()
            # discover all the graph variable attributes currently on the graph starting with graph variable prefixes
            graph_attrs = graph_prim.GetAttributes()
            for attr in graph_attrs:
                attr_name = attr.GetName()
                if attr_name.startswith(GRAPH_VAR_ATTR_PREFIX):
                    # upgrade attribute with "anim:" prefix  to avoid namespace conflicts with omni graph vars
                    graph_vars_to_remove.add(attr_name)
                    upgraded_attr_name = f"anim:{attr_name}"
                    self._graph_vars[graph_path][upgraded_attr_name] = attr.GetTypeName()
                    graph_var_attr = graph_prim.GetAttribute(attr_name)
                    upgraded_var_attr = graph_prim.CreateAttribute(upgraded_attr_name, graph_var_attr.GetTypeName())
                    if graph_var_attr:
                        graph_var_value = graph_var_attr.Get()
                        if graph_var_value:
                            upgraded_var_attr.SetCustomDataByKey(DEFAULT_VALUE_ATTR_CUSTOM_DATA, graph_var_value)
                    graph_prim.RemoveProperty(attr_name)
                    updated_prefix_graphs.add(str(graph_path))
                elif attr_name.startswith(ANIM_GRAPH_VAR_ATTR_PREFIX):
                    if attr_name in self._graph_vars[graph_path] and self._graph_vars[graph_path][attr_name] != attr.GetTypeName():
                        if graph_path not in self._graph_vars_recreated:
                            self._graph_vars_recreated[graph_path] = set()
                        self._graph_vars_recreated[graph_path].add(attr_name)
                    self._graph_vars[graph_path][attr_name] = attr.GetTypeName()
                    if attr_name in graph_vars_to_remove:
                        graph_vars_to_remove.remove(attr_name)

            # remove variable that no longer exist from previous
            for var_to_remove in graph_vars_to_remove:
                if var_to_remove in self._graph_vars[graph_path]:
                    self._graph_vars[graph_path].pop(var_to_remove)

            for prim_path in self._graph_targets:
                prim = stage.GetPrimAtPath(prim_path)
                if prim.IsValid():
                    for var_name in self._graph_vars[graph_path]:
                        if not prim.HasAttribute(var_name):
                            # add new instance variable attribute
                            graph_var_attr = graph_prim.GetAttribute(var_name)
                            graph_var_value = graph_var_attr.Get()
                            inst_var_attr = prim.CreateAttribute(var_name, graph_var_attr.GetTypeName())
                            # set the default value from the graph variable attribute to the instance variable attribute
                            if graph_var_value is not None:
                                inst_var_attr.SetCustomDataByKey(DEFAULT_VALUE_ATTR_CUSTOM_DATA, graph_var_value)
                            refresh_props = True
                        else:
                            graph_var_attr = graph_prim.GetAttribute(var_name)
                            inst_var_attr = prim.GetAttribute(var_name)
                            # check if the inst variable needs updating since the graph variable updated
                            if graph_path in self._graph_vars_updated and var_name in self._graph_vars_updated[graph_path]:
                                # recreate variables if they exist
                                if graph_path in self._graph_vars_recreated and var_name in self._graph_vars_recreated[graph_path]:
                                    prim.RemoveProperty(var_name)
                                    prim.CreateAttribute(var_name, graph_var_attr.GetTypeName())

                                graph_var_value = graph_var_attr.Get()
                                inst_var_value = inst_var_attr.Get()
                                inst_var_default_value = inst_var_attr.GetCustomDataByKey(DEFAULT_VALUE_ATTR_CUSTOM_DATA)
                                if graph_var_value is not None:
                                    inst_var_attr.SetCustomDataByKey(DEFAULT_VALUE_ATTR_CUSTOM_DATA, graph_var_value)
                                if graph_var_value is not None and inst_var_value == inst_var_default_value:
                                    inst_var_attr.Set(graph_var_value)

                    # remove old instance variable attributes
                    for var_to_remove in graph_vars_to_remove:
                        if prim.HasAttribute(var_to_remove):
                            prim.RemoveProperty(var_to_remove)
                            refresh_props = True

        if len(updated_prefix_graphs) > 0:
            notify_updated_variable_prefix(updated_prefix_graphs)

        self._graph_vars_updated.clear()
        self._graph_vars_recreated.clear()
        return refresh_props
