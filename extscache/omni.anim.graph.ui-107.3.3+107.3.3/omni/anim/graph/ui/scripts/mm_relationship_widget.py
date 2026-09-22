import weakref
from typing import List
import carb
from omni.kit.window.property.templates.simple_property_widget import LABEL_WIDTH
from pxr import Sdf, Vt, Usd
from pxr import UsdSkel
import AnimGraphSchema
import omni.ui as ui
import omni.kit.undo
from functools import partial
from omni.kit.property.usd.usd_attribute_model import UsdAttributeModel
from omni.kit.property.usd.relationship import RelationshipTargetPickerOld
from omni.kit.property.usd.usd_property_widget_builder import UsdPropertiesWidgetBuilder
from omni.kit.property.usd.usd_property_widget import UsdPropertyUiEntry

CLIP_ENABLED_WIDTH = ui.Pixel(10)
# TODO: this gets weird if it goes above 70%, makes the frame larger.
CLIPS_WIDTH = ui.Percent(70)
CLIPS_START_TIMES_WIDTH = ui.Percent(12)
CLIPS_END_TIMES_WIDTH = ui.Percent(12)
CLIPS_DELETE_BUTTON_WIDTH = ui.Pixel(14)


class UsdMmRelationshipUiEntry(UsdPropertyUiEntry):
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


class MMRelationshipEditWidget:
    def __init__(self, stage, rel_name, pre_rel_attr_names, post_rel_attr_names, metadata, prim_paths, additional_widget_kwargs):
        self._models = {}
        # deposit all relationships
        self._relationships = [stage.GetPrimAtPath(path).GetRelationship(rel_name) for path in prim_paths]
        self._models[rel_name] = self._relationships
        # prepare for the relationship target picker
        self._additional_widget_kwargs = additional_widget_kwargs if additional_widget_kwargs else {}
        self._targets_limit = self._additional_widget_kwargs.get("targets_limit", 0)

        # Use old relationship picker for compatibility. This one does not require the callback (on_targets_selected).
        # TODO: we should consider refactoring to leverage the newer picker UI.
        self._target_picker = RelationshipTargetPickerOld(
            stage,
            self,
            self._additional_widget_kwargs.get("target_picker_filter_type_list", []),
            self._additional_widget_kwargs.get("target_picker_filter_lambda", None)
        )

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

        self._shared_targets = None
        self._cached_anim_source_times = []
        self._stage = stage
        self._parent_anim_graph = None
        prim = stage.GetPrimAtPath(prim_paths[0])
        while not prim.IsPseudoRoot() and not prim.IsA(AnimGraphSchema.AnimationGraph):
            prim = prim.GetParent()
        if prim.IsA(AnimGraphSchema.AnimationGraph):
            self._parent_anim_graph = prim
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
        if self._target_picker:
            self._target_picker.clean()
            self._target_picker = None

        self._relationships = None
        self._shared_targets = None
        self._frame = None

    # either a complete targets(AnimationClip) list or None
    def _get_shared_targets(self):
        # Update the self._shared_targets
        for relationship in self._relationships:
            targets = relationship.GetTargets()
            if self._shared_targets is None:
                self._shared_targets = targets
            # TODO: optimize it by comparing each target
            elif self._shared_targets != targets:
                self._shared_targets = None
                break
        return self._shared_targets is not None

    # cosmetic data array like clipEnabled, clipStartTimes, clipEndTimes
    # might be incomplete. Fill the array with default data to fill the widget
    def _get_default_value(self, attr_name, index):
        if attr_name == "inputs:clipsStartTimes":
            return self._cached_anim_source_times[index][2]
        elif attr_name == "inputs:clipsEndTimes":
            return self._cached_anim_source_times[index][3]
        else:
            custom_data = self._models[attr_name]._metadata.get("customData")
            default_element = 0.0
            if custom_data is not None:
                default_element = custom_data["defaultElement"]
            else:
                carb.log_error("No default value for array elements")
            return default_element

    # parse all the AnimationClip's SkelAnimation and get its start/end time in seconds
    def _cache_anim_times(self):
        for rel in self._relationships:
            for target in rel.GetTargets():
                startTime = endTime = 0
                enabled = False
                anim_clip_prim = self._stage.GetPrimAtPath(target)
                anim_clip = AnimGraphSchema.AnimationClip(anim_clip_prim)
                if anim_clip:
                    src_rel = anim_clip.GetInputsAnimationSourceRel()
                    src_targets = src_rel.GetTargets()
                    if src_targets:
                        src_skel_prim = self._stage.GetPrimAtPath(src_targets[0])
                        src_skel_anim = UsdSkel.Animation(src_skel_prim)
                        if src_skel_anim:
                            attrs = [src_skel_prim.GetAttribute(attr_name) for attr_name in src_skel_anim.GetSchemaAttributeNames()]
                            for attr in attrs:
                                time_samples = attr.GetTimeSamples()
                                if len(time_samples) > 0:
                                    enabled = True
                                    if time_samples[0] < startTime:
                                        startTime = time_samples[0]
                                    if time_samples[-1] > endTime:
                                        endTime = time_samples[-1]
                self._cached_anim_source_times.append((target, enabled, startTime / self._stage.GetTimeCodesPerSecond(), endTime / self._stage.GetTimeCodesPerSecond()))

    # for cosmetic arrays like clipEnabled, clipStartTimes, clipEndTimes
    # either a complete array or None. The complete array will be extended to
    # the same length of the number of AnimationClips targets with the default value
    def _get_shared_elements(self, element_array_attrs):
        shared_elements_dict = {}
        target_length = 0
        if self._shared_targets is not None:
            target_length = len(self._shared_targets)
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
                element_model = ui.FloatField(name="models", width=CLIPS_START_TIMES_WIDTH).model
                element_model.set_value(element)
                element_model.add_end_edit_fn(
                    partial(on_edit_element, weak_self=weakref.ref(self), key=attr_name, index=index)
                )
            elif element_type == Sdf.ValueTypeNames.BoolArray:
                element_model = ui.CheckBox(name="models", width=CLIP_ENABLED_WIDTH, alignement=ui.Alignment.BOTTOM).model
                element_model.set_value(element)
                element_model.add_value_changed_fn(
                    partial(on_edit_element, weak_self=weakref.ref(self), key=attr_name, index=index)
                )
            else:
                pass

    def on_targets_selected(self, selected_paths):
        for rel in self._relationships:
            existing = rel.GetTargets()
            for path in selected_paths:
                if path not in existing:
                    existing.append(Sdf.Path(path))

            rel.SetTargets(existing)


    def _build(self):
        self._shared_targets = None
        self._get_shared_targets()
        self._cache_anim_times()
        pre_shared_elements_dict = self._get_shared_elements(self._pre_element_array_attrs)
        post_shared_elements_dict = (self._get_shared_elements(self._post_element_array_attrs))

        with ui.VStack(spacing=2, height=0, alignment=ui.Alignment.RIGHT):
            from omni.kit.window.property.templates import (
                HORIZONTAL_SPACING,
                LABEL_HEIGHT
            )

            with ui.HStack(spacing=HORIZONTAL_SPACING, height=LABEL_HEIGHT):
                if self._shared_targets is not None and len(self._shared_targets) > 0:
                    # TODO: customize for each type
                    ui.Label("On", width=CLIP_ENABLED_WIDTH)
                    ui.Label("Clip Path", width=CLIPS_WIDTH, alignment=ui.Alignment.CENTER)
                    ui.Label("Clip Start", width=CLIPS_START_TIMES_WIDTH)
                    ui.Label("Clip End", width=CLIPS_END_TIMES_WIDTH)
                    ui.Label("", width=CLIPS_DELETE_BUTTON_WIDTH)
                else:
                    ui.Spacer(height=LABEL_HEIGHT)
            if self._shared_targets is not None and len(self._shared_targets) > 0:
                for index, target in enumerate(self._shared_targets):
                    with ui.HStack(spacing=HORIZONTAL_SPACING):
                        self._build_element_widgets(pre_shared_elements_dict, index)
                        ui.StringField(name="models", width=CLIPS_WIDTH, read_only=True).model.set_value(target.pathString)
                        self._build_element_widgets(post_shared_elements_dict, index)

                        def on_remove_target(weak_self, target):
                            weak_self = weak_self()
                            if weak_self:
                                omni.kit.undo.begin_group()
                                for relationship in weak_self._relationships:
                                    if relationship:
                                        omni.kit.commands.execute(
                                            "RemoveRelationshipTarget", relationship=relationship, target=target
                                        )
                                        rel_index = weak_self._shared_targets.index(target)
                                        for attr_name, attrs in weak_self._element_array_attrs.items():
                                            for attr in attrs:
                                                attr_value = attr.Get()
                                                element_array = list()
                                                if attr_value:
                                                    element_array = list(attr.Get())
                                                if rel_index < len(element_array):
                                                    element_array.pop(rel_index)
                                                    element_type = self._element_types[attr_name]
                                                    if element_type == Sdf.ValueTypeNames.FloatArray:
                                                        weak_self._models[attr_name].set_value(Vt.FloatArray(element_array))
                                                    elif element_type == Sdf.ValueTypeNames.BoolArray:
                                                        weak_self._models[attr_name].set_value(Vt.BoolArray(element_array))
                                                    else:
                                                        pass
                                omni.kit.undo.end_group()
                                # if self._on_remove_target:
                                #     self._on_remove_target(target)

                        ui.Button(
                            "-",
                            width=CLIPS_DELETE_BUTTON_WIDTH,
                            clicked_fn=partial(on_remove_target, weak_self=weakref.ref(self), target=target),
                        )

            def on_add_target(weak_self):
                weak_self = weak_self()
                if weak_self:
                    shared_target_length = 0
                    if weak_self._shared_targets is not None:
                        shared_target_length = len(weak_self._shared_targets)
                    weak_self._target_picker.show(weak_self._targets_limit - shared_target_length)

            within_target_limit = self._targets_limit == 0 or self._shared_targets is None or len(self._shared_targets) < self._targets_limit
            button = ui.Button(
                "Add Target(s)",
                width=ui.Pixel(30),
                clicked_fn=partial(on_add_target, weak_self=weakref.ref(self)),
                # enabled=True
            )
            if not within_target_limit:
                button.set_tooltip(
                    f"Targets limit of {self._targets_limit} has been reached. To add more target(s), remove current one(s) first."
                )

    def _set_dirty(self):
        self._frame.rebuild()


def mm_relationship_builder(
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
    prim = stage.GetPrimAtPath(prim_paths[0])
    if not prim.IsA(AnimGraphSchema.MotionMatching):
        return
    with ui.HStack(spacing=HORIZONTAL_SPACING):
        with ui.VStack(width=LABEL_WIDTH):
            ui.Spacer(height=LABEL_HEIGHT, width=LABEL_WIDTH)
            UsdPropertiesWidgetBuilder._create_label(label_name, metadata, additional_label_kwargs)
        ui.Spacer(width=5)
        return MMRelationshipEditWidget(stage, rel_name, pre_rel_attr_names, post_rel_attr_names, metadata, prim_paths, additional_widget_kwargs)
