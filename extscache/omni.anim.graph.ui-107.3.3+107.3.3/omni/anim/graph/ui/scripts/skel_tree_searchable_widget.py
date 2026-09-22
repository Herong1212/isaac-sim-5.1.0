import omni.ui as ui
from omni.kit.property.usd.usd_attribute_model import UsdAttributeModel
from pxr import Sdf, Vt, UsdSkel
import AnimGraphSchema
from typing import List
from functools import partial
import weakref
from .utils import find_skel_prim, get_joint_component_list
from omni.kit.widget.searchable_combobox import build_searchable_combo_widget


class SkelTreeWidget:
    def __init__(self, stage, attr_name, prim_paths, metadata):
        self._model = UsdAttributeModel(
            stage, [path.AppendProperty(attr_name) for path in prim_paths], True, metadata
        )

        self._skeleton_prim = find_skel_prim(stage, prim_paths)
        
        self._combo_box = None

        self._frame = ui.Frame()
        self._frame.set_build_fn(self._build)

    def clean(self):
        self._model.clean()
        self._frame = None
        self._skeleton_prim = None
        self._combo_box = None

    def _build(self):
        component_list = get_joint_component_list(self._skeleton_prim)
        component_index = -1

        def on_combo_click_fn(model, weak_self):
            component = model.get_value_as_string()
            weak_self = weak_self()
            if weak_self and weak_self._combo_box:
                joint_name = component.lstrip()
                weak_self._combo_box.set_text(joint_name)
                if joint_name != "None":  
                    weak_self._model.set_value(joint_name)
                else:
                    weak_self._model.set_value("")

        self._combo_box = build_searchable_combo_widget(component_list, component_index, partial(on_combo_click_fn, weak_self=weakref.ref(self)), widget_height=18, default_value="None")
        attr_joint_name = self._model.get_value_as_string()
        if attr_joint_name is not None and attr_joint_name != "":
            self._combo_box.set_text(attr_joint_name)

    def _set_dirty(self):
        self._frame.rebuild()


def build_skel_tree_prop(
    stage,
    attr_name,
    metadata,
    property_type,
    prim_paths: List[Sdf.Path],
    additional_label_kwargs=None,
    additional_widget_kwargs=None,
):
    with ui.HStack(spacing=4):
        label_kwargs = {
            "name": "label",
            "width": 160,
            "height": 18
        }
        display_name = metadata.get(Sdf.PropertySpec.DisplayNameKey, attr_name)
        ui.Label(display_name, **label_kwargs)
        ui.Spacer(width=5)
        return SkelTreeWidget(stage, attr_name, prim_paths, metadata)
