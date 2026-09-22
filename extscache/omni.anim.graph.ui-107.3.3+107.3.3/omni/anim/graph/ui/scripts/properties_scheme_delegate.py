import carb
import omni.usd
from pxr import Sdf
import AnimGraphSchema
from omni.kit.window.property.property_scheme_delegate import PropertySchemeDelegate


class AnimationGraphSchemeDelegate(PropertySchemeDelegate):
    def get_widgets(self, payload):
        widgets_to_build = []
        if self._should_enable_delegate(payload):
            widgets_to_build.append("path")
            widgets_to_build.append("anim_graph_variables")
            widgets_to_build.append("anim_graph_skeleton")
        return widgets_to_build

    def get_unwanted_widgets(self, payload):
        unwanted_widgets_to_build = []
        if self._should_enable_delegate(payload):
            unwanted_widgets_to_build.append("kind")
        return unwanted_widgets_to_build

    def _should_enable_delegate(self, payload):
        stage = payload.get_stage()
        if stage:
            for prim_path in payload:
                prim = stage.GetPrimAtPath(prim_path)
                if prim:
                    if not prim.IsA(AnimGraphSchema.AnimationGraph):
                        return False
            return True
        return False


class AnimationGraphNodeSchemeDelegate(PropertySchemeDelegate):
    def get_widgets(self, payload):
        widgets_to_build = []
        if self._should_enable_delegate(payload):
            widgets_to_build.append("path")
            widgets_to_build.append("anim_graph_node")
        return widgets_to_build

    def get_unwanted_widgets(self, payload):
        unwanted_widgets_to_build = []
        if self._should_enable_delegate(payload):
            unwanted_widgets_to_build.append("kind")
        return unwanted_widgets_to_build

    def _should_enable_delegate(self, payload):
        stage = payload.get_stage()
        if stage:
            for prim_path in payload:
                prim = stage.GetPrimAtPath(prim_path)
                if prim:
                    if not prim.IsA(AnimGraphSchema.AnimationGraphNode):
                        return False
            return True
        return False
