import weakref
from typing import List
import carb
from pxr import Sdf, Vt
import omni.ui as ui
import omni.kit.undo
from functools import partial
from omni.kit.property.usd.usd_attribute_model import UsdAttributeModel
from omni.kit.property.usd.usd_property_widget_builder import UsdPropertiesWidgetBuilder
from omni.kit.property.usd.usd_property_widget import UsdPropertyUiEntry
from omni.kit.widget.searchable_combobox import build_searchable_combo_widget
from .utils import find_skel_prim, get_joint_component_list

JOINTS_WIDTH = ui.Percent(70)
JOINTS_START_TIMES_WIDTH = ui.Percent(12)
CLIPS_START_TIMES_WIDTH = ui.Percent(12)
DELETE_BUTTON_WIDTH = ui.Pixel(14)


class UsdMmJointUiEntry(UsdPropertyUiEntry):
    def __init__(
        self,
        display_name: str,
        rel_name: str,
        display_group: str,
        pre_rel_attr_names: list,
        post_rel_attr_names: list,
        metadata,
        build_fn,
        display_group_collapsed: bool = False,
        prim_paths: List[Sdf.Path] = None,
        additional_widget_kwargs=None,
    ):
        """
        Constructor.

        Args:
            display_name: the UI entry's display label name
            prop_names: list of names of the Usd Properties. This is not the display name.
            display_group: group of the Usd Property when displayed on UI.
            metadata: metadata associated with the Usd Property. A dict with prop_name as the key.
            property_types: types of the properties. a dict with prop_name as the key. Each item is either Usd.Property or Usd.Relationship.
            build_fn: a custom build function to build the UI. Cannot be None
            display_group_collapsed: if the display group should be collapsed. Group only collapses when ALL its contents request such.
            prim_paths: to override what prim paths this property will be built upon. Leave it to None to use default (currently selected paths, or last selected path if multi-edit is off).
        """
        self.display_name = display_name
        self.prop_name = rel_name  # for legacy compatibility
        self.display_group = display_group
        self.display_group_collapsed = display_group_collapsed
        self.metadata = metadata
        self.prim_paths = prim_paths
        self.build_fn = build_fn
        self.pre_rel_attr_names = pre_rel_attr_names
        self.post_rel_attr_names = post_rel_attr_names

    def override_display_name(self, display_name: str):
        """
        Overrides the display name of the property. It only affects UI and DOES NOT write back DisplayName metadata to USD.
        Args:
            display_group: new display group to override to.
        """
        self.display_name = display_name

    def __eq__(self, other):
        return (
            type(self) == type(other)
            and self.prop_name == other.prop_name
            and self.display_name == other.display_name
            and self.display_group == other.display_group
            and self._compare_metadata(self.metadata, other.metadata)
            and self.prim_paths == other.prim_paths
        )


def _get_value(value_model, weak_self, key):
    if weak_self:
        element_type = weak_self._element_types[key]
        if element_type == Sdf.ValueTypeNames.FloatArray:
            return value_model.as_float
        elif element_type == Sdf.ValueTypeNames.BoolArray:
            return value_model.as_bool
    else:
        return None


def _set_value(weak_self, key, element_array):
    if weak_self:
        element_type = weak_self._element_types[key]
        if element_type == Sdf.ValueTypeNames.FloatArray:
            weak_self._models[key].set_value(Vt.FloatArray(element_array))
        elif element_type == Sdf.ValueTypeNames.BoolArray:
            weak_self._models[key].set_value(Vt.BoolArray(element_array))
    else:
        return


class MMJointEditWidget:
    def __init__(self, stage, rel_name, pre_rel_attr_names, post_rel_attr_names, metadata, prim_paths, additional_widget_kwargs):
        self._models = {}

        self._token_array_attrs = [stage.GetPrimAtPath(path).GetAttribute(rel_name) for path in prim_paths]

        # TODO: maybe make this a primary separate, not sure what we gain.
        self._joint_attr_name = rel_name
        self._models[rel_name] = UsdAttributeModel(
            stage, [path.AppendProperty(rel_name) for path in prim_paths], False, metadata[rel_name]
        )

        self._additional_widget_kwargs = additional_widget_kwargs if additional_widget_kwargs else {}
        self._joints_limit = self._additional_widget_kwargs.get("joints_limit", 0)

        self._combo_box_list = []

        # deposit all attributes to _models
        for attr_name in pre_rel_attr_names + post_rel_attr_names:
            self._models[attr_name] = UsdAttributeModel(
                stage, [path.AppendProperty(attr_name) for path in prim_paths], False, metadata[attr_name]
            )
        # cache all the array attributes in front of the relationship
        self._pre_element_array_attrs = {}
        self._element_types = {}
        self._element_array_attrs = {}
        for attr_name in pre_rel_attr_names:
            self._pre_element_array_attrs[attr_name] = [stage.GetPrimAtPath(path).GetAttribute(attr_name) for path in prim_paths]
            self._element_array_attrs[attr_name] = [stage.GetPrimAtPath(path).GetAttribute(attr_name) for path in prim_paths]
            self._element_types[attr_name] = stage.GetAttributeAtPath(prim_paths[0].AppendProperty(attr_name)).GetTypeName()

        # cache all the array attributes behind the relationship
        self._post_element_array_attrs = {}
        for attr_name in post_rel_attr_names:
            self._post_element_array_attrs[attr_name] = [stage.GetPrimAtPath(path).GetAttribute(attr_name) for path in prim_paths]
            self._element_array_attrs[attr_name] = [stage.GetPrimAtPath(path).GetAttribute(attr_name) for path in prim_paths]
            self._element_types[attr_name] = stage.GetAttributeAtPath(prim_paths[0].AppendProperty(attr_name)).GetTypeName()

        self._skeleton_prim = find_skel_prim(stage, prim_paths)

        self._shared_tokens = None
        self._cached_anim_source_times = []
        self._stage = stage
        self._parent_anim_graph = None
        self._frame = ui.Frame()
        self._frame.set_build_fn(self._build)

    def clean(self):
        if self._models:
            self._models.clear()
            self._models = None
        if self._pre_element_array_attrs:
            self._pre_element_array_attrs.clear()
            self._pre_element_array_attrs = None
        if self._element_types:
            self._element_types.clear()
            self._element_types = None
        if self._element_array_attrs:
            self._element_array_attrs.clear()
            self._element_array_attrs = None
        if self._post_element_array_attrs:
            self._post_element_array_attrs.clear()
            self._post_element_array_attrs = None
        if self._cached_anim_source_times:
            self._cached_anim_source_times.clear()
            self._cached_anim_source_times = None
        if self._combo_box_list:
            self._combo_box_list.clear()
            self._combo_box_list = None

        self._relationships = None
        self._shared_tokens = None
        self._frame = None

    # cosmetic data array like clipEnabled, clipStartTimes, clipEndTimes
    # might be incomplete. Fill the array with default data to fill the widget
    def _get_default_value(self, attr_name, index):
        custom_data = self._models[attr_name]._metadata.get("customData")
        default_element = 0.0
        if custom_data is not None:
            default_element = custom_data["defaultElement"]
        else:
            carb.log_error("No default value for array elements")
        return default_element

    def _populate_shared_tokens(self):
        self._shared_tokens = None
        for attr in self._token_array_attrs:
            if attr.HasValue():
                tokens = list(attr.Get())
            else:
                tokens = list()

            if self._shared_tokens is None:
                self._shared_tokens = tokens
            elif self._shared_tokens != tokens:
                self._shared_tokens = None
                break

        return self._shared_tokens is not None and len(self._shared_tokens) > 0

    # for cosmetic arrays like clipEnabled, clipStartTimes, clipEndTimes
    # either a complete array or None. The complete array will be extended to
    # the same length of the number of AnimationClips targets with the default value
    def _get_shared_elements(self, element_array_attrs):
        shared_elements_dict = {}
        target_length = 0
        if self._shared_tokens is not None:
            target_length = len(self._shared_tokens)
        for attr_name, attrs in element_array_attrs.items():
            elements = list()
            shared_elements = None
            for attr in attrs:
                if attr.HasValue():
                    elements = list(attr.Get())
                    if shared_elements is None:
                        shared_elements = elements
                    elif shared_elements != elements:
                        shared_elements = None
                        break
            if shared_elements is None and target_length > 0:
                shared_elements = [self._get_default_value(attr_name, i) for i in range(target_length)]
            # if the shared element is shorter than the target, extend it.
            # don't do any thing for a longer shared element array, we will ignore the rest element
            elif shared_elements is not None and len(shared_elements) < target_length:
                shared_elements.extend([self._get_default_value(attr_name, i + len(shared_elements)) for i in range(target_length - len(shared_elements))])
            shared_elements_dict[attr_name] = shared_elements
        return shared_elements_dict

    def _build_element_widgets(self, shared_elements_dict, index):
        for attr_name, shared_elements in shared_elements_dict.items():
            if shared_elements is None:
                continue
            element = shared_elements[index]

            def on_edit_element(value_model, weak_self, key, index):
                weak_self = weak_self()
                if weak_self:
                    attrs = weak_self._element_array_attrs[key]
                    if attrs:
                        for attr in attrs:
                            if attr:
                                attr_value = attr.Get()
                                element_array = list()
                                if attr_value:
                                    element_array = list(attr.Get())
                                value_model_value = _get_value(value_model, weak_self, key)
                                if index < len(element_array):
                                    element_array[index] = value_model_value
                                else:
                                    custom_data = self._models[attr_name]._metadata.get("customData")
                                    default_element = None
                                    if custom_data is not None:
                                        default_element = custom_data["defaultElement"]
                                    extended_element_array = [default_element for i in range(index - len(element_array) + 1)]
                                    extended_element_array[-1] = value_model_value
                                    element_array.extend(extended_element_array)
                                _set_value(weak_self, key, element_array)

            element_type = self._element_types[attr_name]
            if element_type == Sdf.ValueTypeNames.FloatArray:
                element_model = ui.FloatField(name="models", width=JOINTS_START_TIMES_WIDTH).model
                element_model.set_value(element)
                element_model.add_end_edit_fn(
                    partial(on_edit_element, weak_self=weakref.ref(self), key=attr_name, index=index)
                )
            else:
                pass

    def _build(self):
        self._combo_box_list.clear()
        self._combo_box_list = []

        has_shared_tokens = self._populate_shared_tokens()

        pre_shared_elements_dict = self._get_shared_elements(self._pre_element_array_attrs)
        post_shared_elements_dict = (self._get_shared_elements(self._post_element_array_attrs))

        skeleton_list = get_joint_component_list(self._skeleton_prim)
        skeleton_index = -1

        with ui.VStack(spacing=2, height=0, alignment=ui.Alignment.RIGHT):
            from omni.kit.window.property.templates import (
                HORIZONTAL_SPACING,
                LABEL_HEIGHT
            )

            with ui.HStack(spacing=HORIZONTAL_SPACING, height=LABEL_HEIGHT):
                if has_shared_tokens:
                    # TODO: customize for each type
                    ui.Label("Joint", width=JOINTS_WIDTH, alignment=ui.Alignment.CENTER)
                    ui.Label("Position Weight", width=JOINTS_START_TIMES_WIDTH)
                    ui.Label("Velocity Weight", width=CLIPS_START_TIMES_WIDTH)
                    ui.Label("", width=DELETE_BUTTON_WIDTH)
                else:
                    ui.Spacer(height=LABEL_HEIGHT)
            if has_shared_tokens:
                for index, token in enumerate(self._shared_tokens):
                    with ui.HStack(spacing=HORIZONTAL_SPACING):
                        self._build_element_widgets(pre_shared_elements_dict, index)

                        def on_combo_click_fn(model, weak_self, index):
                            component = model.get_value_as_string()
                            weak_self = weak_self()
                            if weak_self and len(weak_self._combo_box_list) > index:
                                joint_name = component.lstrip()
                                token_array = list(weak_self._token_array_attrs[0].Get())
                                if joint_name != "":
                                    token_array[index] = joint_name
                                weak_self._models[weak_self._joint_attr_name].set_value(Vt.TokenArray(token_array))

                        self._combo_box_list.append(build_searchable_combo_widget(
                            skeleton_list,
                            skeleton_index,
                            partial(on_combo_click_fn, weak_self=weakref.ref(self), index=index),
                            widget_height=18,
                            default_value=token))

                        self._build_element_widgets(post_shared_elements_dict, index)

                        def on_remove_token(weak_self, index):
                            weak_self = weak_self()
                            if weak_self:
                                # TODO: not sure if this is needed.
                                omni.kit.undo.begin_group()
                                token_array = list(weak_self._token_array_attrs[0].Get())
                                token_array.pop(index)
                                weak_self._models[weak_self._joint_attr_name].set_value(Vt.TokenArray(token_array))
                                for attr_name, attrs in weak_self._element_array_attrs.items():
                                    for attr in attrs:
                                        attr_value = attr.Get()
                                        element_array = list()
                                        if attr_value:
                                            element_array = list(attr.Get())
                                        if index < len(element_array):
                                            element_array.pop(index)
                                            element_type = self._element_types[attr_name]
                                            if element_type == Sdf.ValueTypeNames.FloatArray:
                                                weak_self._models[attr_name].set_value(Vt.FloatArray(element_array))
                                            elif element_type == Sdf.ValueTypeNames.BoolArray:
                                                weak_self._models[attr_name].set_value(Vt.BoolArray(element_array))
                                            else:
                                                pass
                                omni.kit.undo.end_group()

                        ui.Button(
                            "-",
                            width=DELETE_BUTTON_WIDTH,
                            clicked_fn=partial(on_remove_token, weak_self=weakref.ref(self), index=index),
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
                    weak_self._models[self._joint_attr_name].set_value(Vt.TokenArray(token_array))

            within_target_limit = self._joints_limit == 0 or not has_shared_tokens or len(self._shared_tokens) < self._targets_limit
            button = ui.Button(
                "Add Element",
                width=ui.Pixel(30),
                clicked_fn=partial(on_add_element, weak_self=weakref.ref(self)),
                # enabled=True
            )
            if not within_target_limit:
                button.set_tooltip(
                    f"Targets limit of {self._joints_limit} has been reached. To add more target(s), remove current one(s) first."
                )

    def _set_dirty(self):
        self._frame.rebuild()


def mm_joint_builder(
    stage,
    label_name,
    rel_name,
    pre_rel_attr_names,
    post_rel_attr_names,
    metadata,
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
        with ui.VStack(width=LABEL_WIDTH):
            ui.Spacer(height=LABEL_HEIGHT, width=LABEL_WIDTH)
            UsdPropertiesWidgetBuilder._create_label(label_name, metadata, additional_label_kwargs)
        ui.Spacer(width=5)
        return MMJointEditWidget(stage, rel_name, pre_rel_attr_names, post_rel_attr_names, metadata, prim_paths, additional_widget_kwargs)
