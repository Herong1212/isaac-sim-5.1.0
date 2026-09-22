import omni.kit.commands
from pxr import Usd, Sdf, UsdGeom, Gf, Tf, Trace, Kind
from .selection_actions import register_actions, deregister_actions

class SelectionExtension(omni.ext.IExt):
    def on_startup(self, ext_id):
        self._ext_name = omni.ext.get_extension_name(ext_id)
        register_actions(self._ext_name)

    def on_shutdown(self):
        deregister_actions(self._ext_name)


class SelectAllCommand(omni.kit.commands.Command):
    """
    Select all prims.

    Args:
        type (Optional[str]): Specific type name. If it's None, it will select
        all prims. If it has type str with value "", it will select all prims without any type.
        Otherwise, it will select prims with that type.
    """

    def __init__(self, type=None):
        self._type = type
        self._prev_selection = omni.usd.get_context().get_selection().get_selected_prim_paths()

    @Trace.TraceFunction
    def do(self):
        omni.usd.get_context().get_selection().select_all_prims(self._type)

    def undo(self):
        if self._prev_selection:
            omni.usd.get_context().get_selection().set_selected_prim_paths(self._prev_selection, True)
        else:
            omni.usd.get_context().get_selection().clear_selected_prim_paths()


class SelectNoneCommand(omni.kit.commands.Command):
    """
    Deselect all selected prims.
    """
    def __init__(self):
        self._prev_selection = omni.usd.get_context().get_selection().get_selected_prim_paths()

    def do(self):
        omni.usd.get_context().get_selection().clear_selected_prim_paths()

    def undo(self):
        omni.usd.get_context().get_selection().set_selected_prim_paths(self._prev_selection, True)


class SelectInvertCommand(omni.kit.commands.Command):
    """
    Deselect current prims, and select everything else not selected before.
    """
    def __init__(self):
        self._prev_selection = omni.usd.get_context().get_selection().get_selected_prim_paths()

    @Trace.TraceFunction
    def do(self):
        omni.usd.get_context().get_selection().set_selected_prim_paths(self._prev_selection, True)
        omni.usd.get_context().get_selection().select_inverted_prims()

    def undo(self):
        omni.usd.get_context().get_selection().set_selected_prim_paths(self._prev_selection, True)


class HideUnselectedCommand(omni.kit.commands.Command):
    """
    Hide prims not selected.
    """

    def _get_parent_prims(self, stage, prim):
        parent_prims = set([])
        while prim.GetParent():
            parent_prims.add(prim.GetParent().GetPath())
            prim = prim.GetParent()
            if stage.HasDefaultPrim() and stage.GetDefaultPrim() == prim:
                break

        return parent_prims

    def _get_all_children(self, prim):
        children_list = set([])
        queue = [prim]
        while len(queue) > 0:
            child_prim = queue.pop()
            for child in child_prim.GetAllChildren():
                children_list.add(child.GetPath())
                queue.append(child)

        return children_list

    def __init__(self):
        stage = omni.usd.get_context().get_stage()
        selection = omni.usd.get_context().get_selection().get_selected_prim_paths()

        # if selected path as children and none of the children are selected, then all the children are selected..
        selected_prims = set([])
        for prim_path in selection:
            sdf_prim_path = Sdf.Path(prim_path)
            prim = stage.GetPrimAtPath(sdf_prim_path)
            if prim:
                selected_prims.add(sdf_prim_path)
                selected_prims.update(self._get_all_children(prim))

        ## exclude parent prims as visabillity is inherited
        all_parent_prims = set([])
        for prim_path in selected_prims:
            prim = stage.GetPrimAtPath(prim_path)
            if prim:
                all_parent_prims.update(self._get_parent_prims(stage, prim))
        selected_prims.update(all_parent_prims)

        all_prims = set([])
        children_iterator = iter(stage.TraverseAll())
        for prim in children_iterator:
            if omni.usd.is_hidden_type(prim):
                children_iterator.PruneChildren()
                continue
            all_prims.add(prim.GetPath())
        self._invert_prims = [item for item in all_prims if item not in selected_prims]

        self._prev_visabillity = []
        for prim_path in self._invert_prims:
            prim = stage.GetPrimAtPath(prim_path)
            if prim:
                if stage.HasDefaultPrim() and stage.GetDefaultPrim() == prim:
                    continue
                imageable = UsdGeom.Imageable(prim)
                if imageable:
                    self._prev_visabillity.append([prim, imageable.ComputeVisibility()])

    @Trace.TraceFunction
    def do(self):
        stage = omni.usd.get_context().get_stage()
        for prim_path in self._invert_prims:
            prim = stage.GetPrimAtPath(prim_path)
            if prim:
                if stage.HasDefaultPrim() and stage.GetDefaultPrim() == prim:
                    continue
                imageable = UsdGeom.Imageable(prim)
                if imageable:
                    imageable.MakeInvisible()

    def undo(self):
        for prim, state in self._prev_visabillity:
            imageable = UsdGeom.Imageable(prim)
            if imageable:
                if state == UsdGeom.Tokens.invisible:
                    imageable.MakeInvisible()
                else:
                    imageable.MakeVisible()


class SelectParentCommand(omni.kit.commands.Command):
    """
    Set the new selection to all parent prims of the current selection.
    """
    def __init__(self):
        self._prev_selection = omni.usd.get_context().get_selection().get_selected_prim_paths()

    def do(self):
        stage = omni.usd.get_context().get_stage()
        parent_prims = set()
        for prim_path in self._prev_selection:
            prim = stage.GetPrimAtPath(prim_path)
            if prim and prim.GetParent() is not None:
                parent_prims.add(prim.GetParent().GetPath().pathString)

        omni.usd.get_context().get_selection().set_selected_prim_paths(sorted(list(parent_prims)), True)

    def undo(self):
        omni.usd.get_context().get_selection().set_selected_prim_paths(self._prev_selection, True)


class SelectLeafCommand(omni.kit.commands.Command):
    """
    Set the new selection to all descendant prims of the current selection.
    """
    def __init__(self):
        self._prev_selection = omni.usd.get_context().get_selection().get_selected_prim_paths()

    def collect_leafs(self, prim, leaf_set):
        prim_children = prim.GetChildren()
        if not prim_children:
            leaf_set.add(prim.GetPath().pathString)
        else:
            for child in prim_children:
                self.collect_leafs(child, leaf_set)

    def do(self):
        stage = omni.usd.get_context().get_stage()
        leaf_prims = set()
        for prim_path in self._prev_selection:
            prim = stage.GetPrimAtPath(prim_path)
            self.collect_leafs(prim, leaf_prims)

        omni.usd.get_context().get_selection().set_selected_prim_paths(sorted(list(leaf_prims)), True)

    def undo(self):
        omni.usd.get_context().get_selection().set_selected_prim_paths(self._prev_selection, True)


class SelectHierarchyCommand(omni.kit.commands.Command):
    """
    Set the new selection to all child prims of the current selection.
    """
    def __init__(self):
        self._prev_selection = omni.usd.get_context().get_selection().get_selected_prim_paths()

    def _collect_hierarchy(self, prim, hierarchy_set):
        hierarchy_set.add(prim.GetPath().pathString)
        prim_children = prim.GetChildren()
        for child in prim_children:
            self._collect_hierarchy(child, hierarchy_set)

    def do(self):
        stage = omni.usd.get_context().get_stage()
        heirarchy_prims = set()
        for prim_path in self._prev_selection:
            prim = stage.GetPrimAtPath(prim_path)
            self._collect_hierarchy(prim, heirarchy_prims)

        omni.usd.get_context().get_selection().set_selected_prim_paths(sorted(list(heirarchy_prims)), True)

    def undo(self):
        omni.usd.get_context().get_selection().set_selected_prim_paths(self._prev_selection, True)


class SelectSimilarCommand(omni.kit.commands.Command):
    """
    Select all prims with the same type of the current selection.
    """
    def __init__(self):
        self._prev_selection = omni.usd.get_context().get_selection().get_selected_prim_paths()

    def do(self):
        stage = omni.usd.get_context().get_stage()
        similar_prim_types = set()
        for prim_path in self._prev_selection:
            prim_type = stage.GetPrimAtPath(prim_path).GetTypeName()
            similar_prim_types.add(prim_type)

        omni.usd.get_context().get_selection().select_all_prims(sorted(list(similar_prim_types)))

    def undo(self):
        omni.usd.get_context().get_selection().set_selected_prim_paths(self._prev_selection, True)


class SelectListCommand(omni.kit.commands.Command):
    """
    Set the new selection from the given list of prim paths.

    Keyword Args:
        selection (List[str]): the new selection to set.
    """
    def __init__(self, **kwargs):
        self._prev_selection = omni.usd.get_context().get_selection().get_selected_prim_paths()
        self._new_selection = []
        if 'selection' in kwargs:
            self._new_selection = kwargs['selection']

    def do(self):
        omni.usd.get_context().get_selection().set_selected_prim_paths(self._new_selection, True)

    def undo(self):
        omni.usd.get_context().get_selection().set_selected_prim_paths(self._prev_selection, True)


class SelectKindCommand(omni.kit.commands.Command):
    """
    Set the new selection to all prim with the given kind.

    Keyword Args:
        kind (str): kind of prim to select.
    """
    def __init__(self, **kwargs):
        self._prev_selection = omni.usd.get_context().get_selection().get_selected_prim_paths()
        self._kind = ""
        if 'kind' in kwargs:
            self._kind = kwargs['kind']

    @Trace.TraceFunction
    def do(self):
        selection = []
        for prim in omni.usd.get_context().get_stage().TraverseAll():
            model_api = Usd.ModelAPI(prim)
            if Kind.Registry.IsA(model_api.GetKind(), self._kind):
                selection.append(str(prim.GetPath()))

        omni.usd.get_context().get_selection().set_selected_prim_paths(selection, True)

    def undo(self):
        omni.usd.get_context().get_selection().set_selected_prim_paths(self._prev_selection, True)
