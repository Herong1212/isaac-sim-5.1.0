import omni.ui as ui
from omni.kit.property.usd.usd_attribute_model import UsdAttributeModel
from omni.kit.property.usd.usd_property_widget_builder import UsdPropertiesWidgetBuilder
from pxr import Sdf, Vt
import AnimGraphSchema
from typing import List
from functools import partial
import weakref
from .utils import find_skel_prim, get_joint_component_list, get_blendshape_list
from omni.kit.widget.searchable_combobox import build_searchable_combo_widget


class TokenArrayEditWidget:
    def __init__(self, stage, attr_name, prim_paths, metadata):
        self._model = UsdAttributeModel(
            stage, [path.AppendProperty(attr_name) for path in prim_paths], False, metadata
        )

        self._token_array_attrs = [stage.GetPrimAtPath(path).GetAttribute(attr_name) for path in prim_paths]

        self._frame = ui.Frame()
        self._frame.set_build_fn(self._build)

    def clean(self):
        self._model.clean()
        self._frame = None

    def _build(self):
        shared_tokens = None

        for attr in self._token_array_attrs:
            if attr.HasValue():
                tokens = list(attr.Get())
            else:
                tokens = list()

            if shared_tokens is None:
                shared_tokens = tokens
            elif shared_tokens != tokens:
                shared_tokens = None
                break

        with ui.VStack(spacing=2):
            if shared_tokens is not None:
                for i in range(len(shared_tokens)):
                    token = shared_tokens[i]
                    with ui.HStack(spacing=2):
                        token_model = ui.StringField(name="models").model
                        token_model.set_value(token)

                        def on_edit_element(value_model, weak_self, index):
                            weak_self = weak_self()
                            if weak_self:
                                token_array = list(weak_self._token_array_attrs[0].Get())
                                token_array[index] = value_model.as_string
                                weak_self._model.set_value(Vt.TokenArray(token_array))

                        token_model.add_end_edit_fn(
                            partial(on_edit_element, weak_self=weakref.ref(self), index=i)
                        )

                        def on_remove_element(weak_self, index):
                            weak_self = weak_self()
                            if weak_self:
                                token_array = list(weak_self._token_array_attrs[0].Get())
                                token_array.pop(index)
                                weak_self._model.set_value(Vt.TokenArray(token_array))

                        ui.Button(
                            "-",
                            width=ui.Pixel(14),
                            clicked_fn=partial(on_remove_element, weak_self=weakref.ref(self), index=i),
                        )

                def on_add_element(weak_self):
                    weak_self = weak_self()
                    if weak_self:
                        token_array_attr = weak_self._token_array_attrs[0]
                        if token_array_attr.HasValue():
                            token_array = list(token_array_attr.Get())
                        else:
                            token_array = list()

                        token_array.append("")
                        weak_self._model.set_value(Vt.TokenArray(token_array))

                ui.Button(
                    "Add Element",
                    width=ui.Pixel(30),
                    clicked_fn=partial(on_add_element, weak_self=weakref.ref(self))
                )

            else:
                ui.StringField(name="models", read_only=True).model.set_value("Mixed")

    def _set_dirty(self):
        self._frame.rebuild()


def build_token_array_prop(
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
        return TokenArrayEditWidget(stage, attr_name, prim_paths, metadata)


class JointsTokenArrayEditWidget:
    def __init__(self, stage, attr_name, prim_paths, metadata):
        self._model = UsdAttributeModel(
            stage, [path.AppendProperty(attr_name) for path in prim_paths], False, metadata
        )

        self._token_array_attrs = [stage.GetPrimAtPath(path).GetAttribute(attr_name) for path in prim_paths]

        self._skeleton_prim = find_skel_prim(stage, prim_paths)

        self._combo_box_list = []

        self._frame = ui.Frame()
        self._frame.set_build_fn(self._build)

    def clean(self):
        self._model.clean()
        self._combo_box_list.clear()
        self._combo_box_list = None
        self._skeleton_prim = None
        self._frame = None

    def _build(self):
        shared_tokens = None
        self._combo_box_list.clear()
        self._combo_box_list = []

        for attr in self._token_array_attrs:
            if attr.HasValue():
                tokens = list(attr.Get())
            else:
                tokens = list()

            if shared_tokens is None:
                shared_tokens = tokens
            elif shared_tokens != tokens:
                shared_tokens = None
                break
        skeleton_list = get_joint_component_list(self._skeleton_prim)
        skeleton_index = -1

        with ui.VStack(spacing=2):
            if shared_tokens is not None:
                for i in range(len(shared_tokens)):
                    token = shared_tokens[i]
                    with ui.HStack(spacing=2):
                        def on_combo_click_fn(model, weak_self, index):
                            component = model.get_value_as_string()
                            weak_self = weak_self()
                            if weak_self and len(weak_self._combo_box_list)>index:
                                joint_name = component.lstrip()
                                token_array = list(weak_self._token_array_attrs[0].Get())
                                if joint_name != "":
                                    token_array[index] = joint_name
                                weak_self._model.set_value(Vt.TokenArray(token_array))
                        self._combo_box_list.append(build_searchable_combo_widget(skeleton_list, skeleton_index, partial(on_combo_click_fn, weak_self=weakref.ref(self), index=i), widget_height=18, default_value=token))

                        def on_remove_element(weak_self, index):
                            weak_self = weak_self()
                            if weak_self:
                                token_array = list(weak_self._token_array_attrs[0].Get())
                                token_array.pop(index)
                                weak_self._model.set_value(Vt.TokenArray(token_array))

                        ui.Button(
                            "-",
                            width=ui.Pixel(14),
                            clicked_fn=partial(on_remove_element, weak_self=weakref.ref(self), index=i),
                        )

                def on_add_element(weak_self):
                    weak_self = weak_self()
                    if weak_self:
                        token_array_attr = weak_self._token_array_attrs[0]
                        if token_array_attr.HasValue():
                            token_array = list(token_array_attr.Get())
                        else:
                            token_array = list()
                        if len(skeleton_list) > 0:
                            token_array.append("")
                        weak_self._model.set_value(Vt.TokenArray(token_array))

                ui.Button(
                    "Add Element",
                    width=ui.Pixel(30),
                    clicked_fn=partial(on_add_element, weak_self=weakref.ref(self))
                )

            else:
                mixed_style = {"Field": {"color": 0xFFCC9E61}, "Tooltip": {"color": 0xFF333333}}
                ui.StringField(name="models", enabled=False, style=mixed_style).model.set_value("Mixed")

    def _set_dirty(self):
        self._frame.rebuild()


def build_joints_token_array_prop(
    stage,
    attr_name,
    metadata,
    property_type,
    prim_paths: List[Sdf.Path],
    additional_label_kwargs=None,
    additional_widget_kwargs=None,
):
    from omni.kit.window.property.templates import (
        HORIZONTAL_SPACING,
        LABEL_WIDTH,
        LABEL_HEIGHT,
    )
    with ui.HStack(spacing=HORIZONTAL_SPACING):
        UsdPropertiesWidgetBuilder._create_label(attr_name, metadata, additional_label_kwargs)
        return JointsTokenArrayEditWidget(stage, attr_name, prim_paths, metadata)


class BlendshapesTokenArrayEditWidget:
    def __init__(self, stage, attr_name, prim_paths, metadata):
        self._model = UsdAttributeModel(
            stage, [path.AppendProperty(attr_name) for path in prim_paths], False, metadata
        )

        self._token_array_attrs = [stage.GetPrimAtPath(path).GetAttribute(attr_name) for path in prim_paths]

        self._skeleton_prim = find_skel_prim(stage, prim_paths)

        self._combo_box_list = []

        self._frame = ui.Frame()
        self._frame.set_build_fn(self._build)

    def clean(self):
        self._model.clean()
        self._combo_box_list.clear()
        self._combo_box_list = None
        self._skeleton_prim = None
        self._frame = None

    def _build(self):
        shared_tokens = None
        self._combo_box_list.clear()
        self._combo_box_list = []

        for attr in self._token_array_attrs:
            if attr.HasValue():
                tokens = list(attr.Get())
            else:
                tokens = list()

            if shared_tokens is None:
                shared_tokens = tokens
            elif shared_tokens != tokens:
                shared_tokens = None
                break
        blendshape_list = get_blendshape_list(self._skeleton_prim)
        blendshape_index = -1

        with ui.VStack(spacing=2):
            if shared_tokens is not None:
                for i in range(len(shared_tokens)):
                    token = shared_tokens[i]
                    with ui.HStack(spacing=2):
                        def on_combo_click_fn(model, weak_self, index):
                            component = model.get_value_as_string()
                            weak_self = weak_self()
                            if weak_self and len(weak_self._combo_box_list)>index:
                                joint_name = component.lstrip()
                                token_array = list(weak_self._token_array_attrs[0].Get())
                                if joint_name != "":
                                    token_array[index] = joint_name
                                weak_self._model.set_value(Vt.TokenArray(token_array))
                        self._combo_box_list.append(build_searchable_combo_widget(blendshape_list, blendshape_index, partial(on_combo_click_fn, weak_self=weakref.ref(self), index=i), widget_height=18, default_value=token))

                        def on_remove_element(weak_self, index):
                            weak_self = weak_self()
                            if weak_self:
                                token_array = list(weak_self._token_array_attrs[0].Get())
                                token_array.pop(index)
                                weak_self._model.set_value(Vt.TokenArray(token_array))

                        ui.Button(
                            "-",
                            width=ui.Pixel(14),
                            clicked_fn=partial(on_remove_element, weak_self=weakref.ref(self), index=i),
                        )

                def on_add_element(weak_self):
                    weak_self = weak_self()
                    if weak_self:
                        token_array_attr = weak_self._token_array_attrs[0]
                        if token_array_attr.HasValue():
                            token_array = list(token_array_attr.Get())
                        else:
                            token_array = list()
                        if len(blendshape_list) > 0:
                            token_array.append("")
                        weak_self._model.set_value(Vt.TokenArray(token_array))

                ui.Button(
                    "Add Element",
                    width=ui.Pixel(30),
                    clicked_fn=partial(on_add_element, weak_self=weakref.ref(self))
                )

            else:
                mixed_style = {"Field": {"color": 0xFFCC9E61}, "Tooltip": {"color": 0xFF333333}}
                ui.StringField(name="models", enabled=False, style=mixed_style).model.set_value("Mixed")

    def _set_dirty(self):
        self._frame.rebuild()


def build_blendshapes_token_array_prop(
    stage,
    attr_name,
    metadata,
    property_type,
    prim_paths: List[Sdf.Path],
    additional_label_kwargs=None,
    additional_widget_kwargs=None,
):
    from omni.kit.window.property.templates import (
        HORIZONTAL_SPACING,
        LABEL_WIDTH,
        LABEL_HEIGHT,
    )
    with ui.HStack(spacing=HORIZONTAL_SPACING):
        UsdPropertiesWidgetBuilder._create_label(attr_name, metadata, additional_label_kwargs)
        return BlendshapesTokenArrayEditWidget(stage, attr_name, prim_paths, metadata)
