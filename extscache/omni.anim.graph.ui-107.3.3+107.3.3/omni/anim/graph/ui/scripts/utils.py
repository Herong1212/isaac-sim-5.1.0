import omni.ui as ui
import omni.usd
import omni.kit.window.property
from pxr import Sdf, Usd, UsdSkel, UsdGeom
import AnimGraphSchema
import re


def find_anim_graph_parent(prim: Usd.Prim) -> Usd.Prim:
    while prim and not prim.IsPseudoRoot() and not prim.IsA(AnimGraphSchema.AnimationGraph):
        prim = prim.GetParent()
    if prim and prim.IsA(AnimGraphSchema.AnimationGraph):
        return prim
    return None


def find_anim_graph_prim(stage: Usd.Stage, prim_paths: str) -> Usd.Prim:
    if prim_paths and len(prim_paths) > 0:
        return find_anim_graph_parent(stage.GetPrimAtPath(prim_paths[0]))
    return None


def find_skel_prim(stage, prim_paths):
    if prim_paths and len(prim_paths) > 0:
        prim = find_anim_graph_parent(stage.GetPrimAtPath(prim_paths[0]))
        if prim:
            _anim_graph = AnimGraphSchema.AnimationGraph(prim)
            rel = _anim_graph.GetSkelSkeletonRel()
            if rel:
                targets = rel.GetTargets()
                if targets and len(targets) > 0:
                    return stage.GetPrimAtPath(targets[0])

    return None


def get_joint_component_list(skel_prim):
    if skel_prim:
        skeleton = UsdSkel.Skeleton(skel_prim)
        if skeleton:
            joint_attr = skeleton.GetJointsAttr()
            if joint_attr:
                joints = joint_attr.Get()
                return [re.sub('[a-zA-Z\_][0-9a-zA-Z\_]*/', '\t', x) for x in joints]

    return []


def get_mesh_descendents(prim: Usd.Prim, results):
    if prim.IsA(UsdGeom.Mesh):
        results.append(UsdGeom.Mesh(prim))

    children = prim.GetChildren()
    for child in children:
        get_mesh_descendents(child, results)


def get_blendshape_list(skel_prim: Usd.Prim):
    blendshapes = []

    if skel_prim:
        # locate the SkelRoot from the skeleton
        sr_prim = skel_prim.GetParent()
        while sr_prim and not sr_prim.IsPseudoRoot() and not sr_prim.IsA(UsdSkel.Root):
            sr_prim = sr_prim.GetParent()
        if sr_prim and sr_prim.IsA(UsdSkel.Root):
            # locate meshes under the SkelRoot
            meshes = []
            get_mesh_descendents(sr_prim, meshes)
            for mesh in meshes:
                binding = UsdSkel.BindingAPI(mesh)
                if binding:
                    attr = binding.GetBlendShapesAttr()
                    if attr.HasValue():
                        blendshapes.extend(list(attr.Get()))

    return blendshapes


def get_title_space_name(name: str) -> str:
    attr_name = name[name.rindex(":") + 1:]
    return re.sub("([a-z])([A-Z0-9])", "\g<1> \g<2>", attr_name).title()


def get_stage_default_prim_path(stage):
    if stage.HasDefaultPrim():
        return stage.GetDefaultPrim().GetPath()
    else:
        return Sdf.Path.absoluteRootPath


def relationship_has_target(relationship, target_path):
    if relationship:
        targets = relationship.GetTargets()
        for path in targets:
            if path == target_path:
                return True
    return False


def refresh_property_window():
    selected_paths = omni.usd.get_context().get_selection().get_selected_prim_paths()
    omni.usd.get_context().get_selection().clear_selected_prim_paths()
    omni.kit.window.property.get_window()._window.frame.rebuild()
    omni.usd.get_context().get_selection().set_selected_prim_paths(selected_paths, True)


class Prompt:
    def __init__(
        self,
        title,
        text,
        ok_button_text="OK",
        cancel_button_text=None,
        middle_button_text=None,
        ok_button_fn=None,
        cancel_button_fn=None,
        middle_button_fn=None,
        modal=False,
    ):
        self._title = title
        self._text = text
        self._cancel_button_text = cancel_button_text
        self._cancel_button_fn = cancel_button_fn
        self._ok_button_fn = ok_button_fn
        self._ok_button_text = ok_button_text
        self._middle_button_text = middle_button_text
        self._middle_button_fn = middle_button_fn
        self._modal = modal
        self._build_ui()

    def __del__(self):
        self._cancel_button_fn = None
        self._ok_button_fn = None

    def __enter__(self):
        self._window.show()
        return self

    def __exit__(self, type, value, trace):
        self._window.hide()

    def show(self):
        self._window.visible = True

    def hide(self):
        self._window.visible = False

    def is_visible(self):
        return self._window.visible

    def set_text(self, text):
        self._text_label.text = text

    def set_confirm_fn(self, on_ok_button_clicked):
        self._ok_button_fn = on_ok_button_clicked

    def set_cancel_fn(self, on_cancel_button_clicked):
        self._cancel_button_fn = on_cancel_button_clicked

    def set_middle_button_fn(self, on_middle_button_clicked):
        self._middle_button_fn = on_middle_button_clicked

    def _on_ok_button_fn(self):
        self.hide()
        if self._ok_button_fn:
            self._ok_button_fn()

    def _on_cancel_button_fn(self):
        self.hide()
        if self._cancel_button_fn:
            self._cancel_button_fn()

    def _on_middle_button_fn(self):
        self.hide()
        if self._middle_button_fn:
            self._middle_button_fn()

    def _build_ui(self):
        self._window = ui.Window(
            self._title, visible=False, height=0, dockPreference=ui.DockPreference.DISABLED
        )
        self._window.flags = (
            ui.WINDOW_FLAGS_NO_COLLAPSE
            | ui.WINDOW_FLAGS_NO_RESIZE
            | ui.WINDOW_FLAGS_NO_SCROLLBAR
            | ui.WINDOW_FLAGS_NO_RESIZE
            | ui.WINDOW_FLAGS_NO_MOVE
        )

        if self._modal:
            self._window.flags = self._window.flags | ui.WINDOW_FLAGS_MODAL

        with self._window.frame:
            with ui.VStack(height=0):
                ui.Spacer(width=0, height=10)
                with ui.HStack(height=0):
                    ui.Spacer()
                    self._text_label = ui.Label(self._text, word_wrap=True, width=self._window.width - 80, height=0)
                    ui.Spacer()
                ui.Spacer(width=0, height=10)
                with ui.HStack(height=0):
                    ui.Spacer(height=0)
                    if self._ok_button_text:
                        ok_button = ui.Button(self._ok_button_text, width=60, height=0)
                        ok_button.set_clicked_fn(self._on_ok_button_fn)
                    if self._middle_button_text:
                        middle_button = ui.Button(self._middle_button_text, width=60, height=0)
                        middle_button.set_clicked_fn(self._on_middle_button_fn)
                    if self._cancel_button_text:
                        cancel_button = ui.Button(self._cancel_button_text, width=60, height=0)
                        cancel_button.set_clicked_fn(self._on_cancel_button_fn)
                    ui.Spacer(height=0)
                ui.Spacer(width=0, height=10)