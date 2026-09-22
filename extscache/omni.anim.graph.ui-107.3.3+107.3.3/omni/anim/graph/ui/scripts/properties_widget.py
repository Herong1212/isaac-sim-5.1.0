import omni.ui as ui
import omni.usd
import types
from functools import partial
from omni.kit.property.usd.usd_property_widget import UsdPropertiesWidgetBuilder
from omni.kit.property.usd.usd_model_base import UsdBase
from pxr import Sdf, Usd, UsdGeom, UsdSkel
import OmniGraphSchema
import AnimGraphSchema
from omni.kit.property.usd.usd_property_widget import UsdPropertiesWidget, UsdPropertyUiEntry
from omni.kit.property.usd.prim_selection_payload import PrimSelectionPayload
from omni.kit.property.usd.widgets import ICON_PATH
from omni.kit.window.popup_dialog import MessageDialog
from omni.kit.usd_undo import *
from .properties_widget_nodes import AnimationGraphNodePropertiesWidget
from .properties_scheme_delegate import AnimationGraphSchemeDelegate, AnimationGraphNodeSchemeDelegate
from .utils import Prompt
from .token_array_edit_widget import build_token_array_prop
from .stage_picker_dialog import StagePickerDialog
from omni.kit.window.file_importer import get_file_importer
from pathlib import Path
from typing import List

REMOVE_BUTTON_STYLE = style = {"image_url": str(Path(ICON_PATH).joinpath("remove.svg")), "margin": 0, "padding": 0}

ANIM_GRAPH_VAR_ATTR_PREFIX = "anim:graph:variable:"
ANIM_GRAPH_REL = "animationGraph"
SKELETON_ATTR = "skel:skeleton"
ANIM_GRAPH_EXTERNAL = "animationGraph:external"

class AnimGraphProperties:
    def __init__(self):
        self._registered = False
        self.on_startup()

    def on_startup(self):
        if self._registered:
            return
        self._add_menus = []
        import omni.kit.window.property as p
        w = p.get_window()
        if w:
            w.register_widget("prim", "anim_graph_api", AnimGraphAPIPropertiesWidget("Animation Graph"))
            w.register_widget("prim", "anim_graph_variables", AnimGraphVariablesPropertiesWidget("Variables"))
            w.register_widget("prim", "anim_graph_skeleton", AnimGraphSkeletonPropertiesWidget("Skeletal Binding"))
            w.register_widget("prim", "anim_graph_node", AnimationGraphNodePropertiesWidget("Settings"))
            w.register_scheme_delegate("prim", "anim_graph", AnimationGraphSchemeDelegate())
            w.register_scheme_delegate("prim", "anim_graph_node", AnimationGraphNodeSchemeDelegate())
            self._registered = True

    def on_shutdown(self):
        if not self._registered:
            return
        self._add_menus = []
        import omni.kit.window.property as p
        w = p.get_window()
        if w:
            w.unregister_widget("prim", "anim_graph_api")
            w.unregister_widget("prim", "anim_graph_variables")
            w.unregister_widget("prim", "anim_graph_skeleton")
            w.unregister_widget("prim", "anim_graph_node")
            w.unregister_scheme_delegate("anim_graph", "anim_graph_scheme")
            w.unregister_scheme_delegate("anim_graph_node", "anim_graph_node_scheme")


class AnimGraphAPIPropertiesWidget(UsdPropertiesWidget):
    def __init__(self, title: str):
        super().__init__(title, collapsed=False)
        self._title = title
        from omni.kit.property.usd import PrimPathWidget
        self._add_button_menus = []
        self._add_button_menus.append(
            PrimPathWidget.add_button_menu_entry(
                "Animation/Animation Graph",
                show_fn=self.on_show_animation_graph,
                onclick_fn=self.on_click_animation_graph,
            )
        )
        self._anim_graph_vars = []
        self._stage_picker = None

    def destroy(self):
        from omni.kit.property.usd import PrimPathWidget
        for menu in self._add_button_menus:
            PrimPathWidget.remove_button_menu_entry(menu)
        self._add_button_menus = []

    def on_show_animation_graph(self, objects: dict):
        if "prim_list" not in objects or "stage" not in objects:
            return False
        stage = objects["stage"]
        if not stage:
            return False
        prim_list = objects["prim_list"]
        if len(prim_list) < 1:
            return False
        for item in prim_list:
            if isinstance(item, Sdf.Path):
                prim = stage.GetPrimAtPath(item)
            elif isinstance(item, Usd.Prim):
                prim = item
            if prim.IsA(UsdSkel.Root) and not prim.HasAPI(AnimGraphSchema.AnimationGraphAPI):
                return True
        return False

    def _on_stage_picker_select_graph(self, selected_prim):
        omni.kit.commands.execute(
            "ApplyAnimationGraphAPICommand",
            paths=self._apply_prim_paths,
            animation_graph_path=selected_prim.GetPath()
        )
        omni.kit.commands.execute("AnimGraphUIRefreshPropertyWindowCommand")
        return True

    def on_click_animation_graph(self, payload: PrimSelectionPayload):
        if payload is None:
            return Sdf.Path.emptyPath
        if self._stage_picker:
            self._stage_picker.clean()
        self._stage_picker = StagePickerDialog(
            omni.usd.get_context().get_stage(),
            lambda p: self._on_stage_picker_select_graph(p),
            "Select Animation Graph",
            "Select",
            [],
            lambda p: self._filter_target_lambda(p)
        )
        self._stage_picker.show()
        self._apply_prim_paths = payload.get_paths()
        return self._apply_prim_paths

    def _filter_target_lambda(self, target_prim):
        return target_prim.IsA(AnimGraphSchema.AnimationGraph)

    def on_new_payload(self, payload):
        self._anim_graph_vars.clear()
        if not super().on_new_payload(payload):
            return False
        if not self._payload or len(self._payload) == 0:
            return False
        for prim_path in payload:
            prim = self._get_prim(prim_path)
            if not prim:
                return False
            else:
                attrs = prim.GetProperties()
                for attr in attrs:
                    attr_name_str = attr.GetName()
                    if attr_name_str == ANIM_GRAPH_REL:
                        targets = attr.GetTargets()
                        for target in targets:
                            target_prim = self._get_prim(target)
                            target_attrs = target_prim.GetAttributes()
                            for target_attr in target_attrs:
                                target_attr_name = target_attr.GetName()
                                if target_attr_name.startswith(ANIM_GRAPH_VAR_ATTR_PREFIX):
                                    self._anim_graph_vars.append(target_attr_name)
                        return True
                return False
        return False

    def _filter_props_to_build(self, props):
        return [prop for prop in props if prop.GetName().startswith(ANIM_GRAPH_REL) or (prop.GetName().startswith(ANIM_GRAPH_VAR_ATTR_PREFIX) and prop.GetName() in self._anim_graph_vars)]

    def get_additional_kwargs(self, ui_attr):
        random_prim = Usd.Prim()
        if self._payload:
            prim_paths = self._payload.get_paths()
            for prim_path in prim_paths:
                prim = self._get_prim(prim_path)
                if not prim:
                    continue
                if not random_prim:
                    random_prim = prim
                elif random_prim.GetTypeName() != prim.GetTypeName():
                    break
        if ui_attr.prop_name == ANIM_GRAPH_REL:
            return None, {"target_picker_filter_type_list": [AnimGraphSchema.AnimationGraph], "targets_limit": 1}
        return None, None

    def _customize_props_layout(self, attrs):
        for attr in attrs:
            if attr.attr_name == ANIM_GRAPH_REL:
                attr.override_display_group("Graph")
            if attr.attr_name in self._anim_graph_vars:
                var_offset = attr.attr_name.rindex(":") + 1
                display_group = "Variables"
                display_name = attr.attr_name[var_offset:]
                attr.override_display_name(display_name)
                attr.override_display_group(display_group)
        return attrs

    def build_property_item(self, stage, ui_prop: UsdPropertyUiEntry, prim_paths: List[Sdf.Path]):
        metadata = ui_prop.metadata
        type_name = metadata.get(Sdf.PrimSpec.TypeNameKey, "unknown type")
        sdf_type_name = Sdf.ValueTypeNames.Find(type_name)
        if sdf_type_name.type == Sdf.ValueTypeNames.TokenArray.type:
            ui_prop.build_fn = build_token_array_prop

        return super().build_property_item(stage, ui_prop, prim_paths)

    def build_impl(self):
        if self._collapsable:
            self._collapsable_frame = ui.CollapsableFrame(
                self._title, build_header_fn=self._build_custom_frame_header, collapsed=self._collapsed
            )

            def on_collapsed_changed(collapsed):
                self._collapsed = collapsed

            self._collapsable_frame.set_collapsed_changed_fn(on_collapsed_changed)
        else:
            self._collapsable_frame = ui.Frame(height=10, style={"Frame": {"padding": 5}})
        self._collapsable_frame.set_build_fn(self._build_frame)

    def _on_remove_with_prompt(self):
        def on_remove_animation_api():
            selected_paths = omni.usd.get_context().get_selection().get_selected_prim_paths()
            omni.kit.commands.execute("RemoveAnimationGraphAPICommand", paths=selected_paths)
            omni.kit.commands.execute("AnimGraphUIRefreshPropertyWindowCommand")
        prompt = Prompt(
            "Remove AnimationGraph?", "Are you sure you want to remove the 'AnimationGraph' component?", "Yes", "No",
            ok_button_fn=lambda: on_remove_animation_api(), modal=True
        )
        prompt.show()

    def _build_custom_frame_header(self, collapsed, text):
        if collapsed:
            alignment = ui.Alignment.RIGHT_CENTER
            width = 5
            height = 7
        else:
            alignment = ui.Alignment.CENTER_BOTTOM
            width = 7
            height = 5

        with ui.HStack(spacing=8):
            with ui.VStack(width=0):
                ui.Spacer()
                ui.Triangle(
                    style_type_name_override="CollapsableFrame.Header", width=width, height=height, alignment=alignment
                )
                ui.Spacer()
            ui.Label(text, style_type_name_override="CollapsableFrame.Header")
            with ui.HStack(width=0):
                ui.Spacer(width=8)
                with ui.VStack(width=0):
                    ui.Spacer(height=5)
                    ui.Button(style=REMOVE_BUTTON_STYLE, height=16, width=16).set_mouse_pressed_fn(lambda *_: self._on_remove_with_prompt())
                ui.Spacer(width=5)


class AnimGraphVariablesPropertiesWidget(UsdPropertiesWidget):
    def __init__(self, title: str):
        super().__init__(title, collapsed=False)
        self._title = title

    def destroy(self):
        pass

    def on_new_payload(self, payload):
        if not super().on_new_payload(payload):
            return False
        if not self._payload or len(self._payload) == 0:
            return False
        for prim_path in payload:
            prim = self._get_prim(prim_path)
            if not prim:
                return False
            else:
                is_graph_type = prim.IsA(AnimGraphSchema.AnimationGraph)
                attrs = prim.GetProperties()
                for attr in attrs:
                    attr_name_str = attr.GetName()
                    if is_graph_type and attr_name_str.startswith(ANIM_GRAPH_VAR_ATTR_PREFIX):
                        return True
                return False
        return False

    def _filter_props_to_build(self, props):
        return [prop for prop in props if prop.GetName().startswith(ANIM_GRAPH_VAR_ATTR_PREFIX)]

    def _filter_target_lambda(self, target_prim):
        return target_prim.IsA(AnimGraphSchema.AnimationGraph)

    def get_additional_kwargs(self, ui_attr):
        random_prim = Usd.Prim()
        if self._payload:
            prim_paths = self._payload.get_paths()
            for prim_path in prim_paths:
                prim = self._get_prim(prim_path)
                if not prim:
                    continue
                if not random_prim:
                    random_prim = prim
                elif random_prim.GetTypeName() != prim.GetTypeName():
                    break
        return None, None

    def _customize_props_layout(self, attrs):
        for attr in attrs:
            if attr.attr_name.startswith(ANIM_GRAPH_VAR_ATTR_PREFIX):
                var_offset = attr.attr_name.rindex(":") + 1
                display_name = attr.attr_name[var_offset:]
                attr.override_display_name(display_name)
        return attrs

    def build_property_item(self, stage, ui_prop: UsdPropertyUiEntry, prim_paths: List[Sdf.Path]):
        metadata = ui_prop.metadata
        type_name = metadata.get(Sdf.PrimSpec.TypeNameKey, "unknown type")
        sdf_type_name = Sdf.ValueTypeNames.Find(type_name)
        if sdf_type_name.type == Sdf.ValueTypeNames.TokenArray.type:
            ui_prop.build_fn = build_token_array_prop
        return super().build_property_item(stage, ui_prop, prim_paths)


class AnimGraphSkeletonPropertiesWidget(UsdPropertiesWidget):
    def __init__(self, title: str):
        super().__init__(title, collapsed=False)
        self._title = title

    def destroy(self):
        self._build_attrs = []

    def on_new_payload(self, payload):
        if not super().on_new_payload(payload):
            return False
        if not self._payload or len(self._payload) == 0:
            return False
        for prim_path in payload:
            prim = self._get_prim(prim_path)
            if not prim:
                return False
            if prim.IsA(AnimGraphSchema.AnimationGraph):
                return True
            return False
        return False

    def _filter_props_to_build(self, props):
        return [prop for prop in props if prop.GetName() == SKELETON_ATTR]

    def get_additional_kwargs(self, ui_attr):
        random_prim = Usd.Prim()
        if self._payload:
            prim_paths = self._payload.get_paths()
            for prim_path in prim_paths:
                prim = self._get_prim(prim_path)
                if not prim:
                    continue
                if not random_prim:
                    random_prim = prim
                elif random_prim.GetTypeName() != prim.GetTypeName():
                    break
        if ui_attr.prop_name == SKELETON_ATTR:
            return None, {"target_picker_filter_type_list": [UsdSkel.Skeleton], "targets_limit": 1}
        return None, None

    def build_property_item(self, stage, ui_prop: UsdPropertyUiEntry, prim_paths: List[Sdf.Path]):
        metadata = ui_prop.metadata
        type_name = metadata.get(Sdf.PrimSpec.TypeNameKey, "unknown type")
        sdf_type_name = Sdf.ValueTypeNames.Find(type_name)
        if sdf_type_name.type == Sdf.ValueTypeNames.TokenArray.type:
            ui_prop.build_fn = build_token_array_prop
        return super().build_property_item(stage, ui_prop, prim_paths)
