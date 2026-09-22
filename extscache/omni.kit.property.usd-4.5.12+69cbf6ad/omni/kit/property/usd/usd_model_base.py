# Copyright (c) 2020-2021, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = ["UsdBase"]

import contextlib
import copy
from typing import Any, List

import carb
import carb.input
import carb.profiler
import carb.settings
import omni.kit.commands
import omni.kit.property.adapter.core as ac
import omni.kit.undo
import omni.timeline
import omni.usd
from omni.kit.property.adapter.core import AttributeAdapter, StageAdapter
from omni.kit.usd.layers import LayerEventType, get_layer_event_payload, get_layers
from pxr import Ar, Gf, Sdf, Tf, Trace, Usd

from .control_state_manager import ControlStateManager
from .placeholder_attribute import PlaceholderAttribute

PERSISTENT_SETTINGS_PREFIX = "/persistent"


class UsdBase:
    """A base class for USD attributes and properties management.

    This class provides functionality to handle USD stage interactions, listen to changes,
    manage control states, and perform value manipulation for USD attributes. It is designed to
    be a common base class for USD model implementations, offering a rich set of features for
    USD data handling.

    Args:
        stage (:obj:`Usd.Stage`): The USD stage to interact with.
        object_paths (List[Sdf.Path]): A list of Sdf.Path objects representing the USD attributes or properties.
        self_refresh (bool): If True, the model will listen for USD changes itself; otherwise, it will rely on external update triggers.
        metadata (Optional[dict]): Additional metadata associated with the USD attributes or properties. Defaults to None.
        change_on_edit_end (bool): If True, changes to the USD are only committed when the edit ends (e.g., focus lost), improving performance during rapid edits. Defaults to True.
        treat_array_entry_as_comp (bool): Treats each entry in an array as a separate component, which is useful for building UI widgets that indicate non-default or ambiguous states at the entry level.

    Keyword Args:
        auto_target_session_layer_def (bool): Targets session layer definition for edits by default.
        min: The minimum allowed value for the attribute; this acts as a lower bound.
        max: The maximum allowed value for the attribute; this acts as an upper bound."""

    def __init__(
        self,
        stage: Usd.Stage,
        object_paths: List[Sdf.Path],
        self_refresh: bool,
        metadata: dict = None,
        change_on_edit_end: bool = True,
        treat_array_entry_as_comp: bool = False,
        **kwargs,
    ):
        """Initializes the UsdBase instance."""
        self._control_state_mgr = ControlStateManager.get_instance()
        if isinstance(stage, StageAdapter):
            self._stage = stage.usd_stage
            self._update_stage_adapters()
            adapter_registry_stream = ac.get_adapter_registry().event_stream
            self._adapter_change_listener = adapter_registry_stream.create_subscription_to_pop(self._on_adapter_changed)
        else:
            self._stage = stage
            self._stage_adapters_sorted_read = []
            self._stage_adapters_sorted_write = []

        self._valid_stage = stage
        self._listener_adapters = []
        self._listener = None
        self._usd_context = None
        self._object_paths = object_paths
        self._object_paths_set = set(object_paths)
        self._metadata = metadata if metadata else {}
        self._change_on_edit_end = change_on_edit_end
        self._treat_array_entry_as_comp = treat_array_entry_as_comp
        self._auto_target_session_layer_def = kwargs.get("auto_target_session_layer_def", True)
        self._dirty = True
        self._readonly = False
        self._value = None  # The value to be displayed on widget
        self._has_default_value = False
        self._default_value = None
        self._real_values = []  # The actual values in usd, might be different from self._value if ambiguous.
        self._connections = []
        self._is_big_array = False
        self._prev_value = None
        self._prev_real_values = []
        self._editing = 0
        self._ignore_notice = False
        self._ambiguous = False
        # "comp" is the first dimension of an array (when treat_array_entry_as_comp is enabled) or vector attribute.
        # - If attribute is non-array vector type, comp indexes into the vector itself. e.g. for vec3 type, comp=1 means
        #   the 2nd channel of the vector vec3[1].
        # - If attribute is an array type:
        #   - When treat_array_entry_as_comp is enabled) is enabled:
        #       - If the attribute is an array of scalar (i.e. float[]), `comp`` is the entry index. e.g. for
        #         SdfAssetArray type, comp=1 means the 2nd path in the path array.
        #       - If the attribute is an array of vector (i.e. vec3f[]), `comp` only indexes the array entry, it does
        #         not support indexing into the channel of the vector within the array entry. i.e a "2D" comp is not
        #         supported yet.
        #   - When treat_array_entry_as_comp is enabled) is disabled:
        #       - comp is 0 and the entire array is treated as one scalar value.
        #
        # This applies to all `comp` related functionality in this model base.
        self._comp_ambiguous = []
        self._might_be_time_varying = False  # Inaccurate named. It really means if timesamples > 0
        self._timeline = omni.timeline.get_timeline_interface()
        self._current_time = self._timeline.get_current_time()
        self._timeline_sub = None
        self._on_set_default_fn = None
        self._soft_range_min = None
        self._soft_range_max = None
        self._follow_connections = kwargs.get("follow_connections", False)
        self._bad_connection = False
        self._bad_connection_error = ""

        # get PlaceholderAttribute class
        self._placeholder_cls = self._metadata.get("placeholder_class", PlaceholderAttribute)

        # get soft_range userdata settings
        attributes = self._get_attributes()
        if attributes:
            attribute = attributes[-1]
            if isinstance(attribute, AttributeAdapter):
                # usdrt not support GetCustomDataByKey
                usd_attr = self._stage.GetAttributeAtPath(attribute.GetPath().pathString)
            else:
                usd_attr = attribute
            if isinstance(usd_attr, Usd.Attribute) and usd_attr.IsValid():
                soft_range = usd_attr.GetCustomDataByKey("omni:kit:property:usd:soft_range_ui")
                if soft_range:
                    self._soft_range_min = soft_range[0]
                    self._soft_range_max = soft_range[1]
                if usd_attr.GetCustomDataByKey("omni:kit:property:usd:readonly"):
                    self._readonly = True

        # override readonly
        self._readonly = kwargs.get("readonly", self._readonly)

        # commands used by self._change_property_2() when creating/modifying a property.
        self._change_property_commands = kwargs.get("change_property_commands", ["ChangeProperty"])

        # If enabled properties will be removed if they are set to their default value.
        self._remove_if_default = kwargs.get("remove_if_default", False)

        # Hard range for the value. For vector type, range value is a float/int that compares against each component individually
        self._min = kwargs.get("min", None)
        self._max = kwargs.get("max", None)

        # Invalid range
        if self._min is not None and self._max is not None and self._min >= self._max:
            self._min = self._max = None

        # The state of the icon on the right side of the line with widget_get_usd_contextses
        self._control_state = 0
        # Callback when the control state is changing. We use it to redraw UI
        self._on_control_state_changed_fn = None
        # Callback when the value is reset. We use it to redraw UI
        self._on_set_default_fn = None
        # True if the attribute has the default value and the current value is not default
        self._different_from_default = False
        # Per component different from default
        self._comp_different_from_default = []

        # Whether the UsdModel should self register Tf.Notice or let UsdPropertiesWidget inform a property change
        if self_refresh:
            if self._stage_adapters_sorted_read:
                for adapter in self._stage_adapters_sorted_read:
                    self._listener_adapters.append(
                        adapter.CreateChangeTracker(attributes, self.get_prim_paths(adapter), self._on_usd_changed)
                    )
            else:
                self._listener = Tf.Notice.Register(Usd.Notice.ObjectsChanged, self._on_usd_changed, self._stage)

        # Notification handler to throttle notifications.
        self._notification = None

        self._settings = carb.settings.get_settings()

        # layer locked changed event
        usd_context = self._get_usd_context()
        layers = get_layers(usd_context)
        self._spec_locks_subscription = layers.get_event_stream().create_subscription_to_pop(
            self._on_spec_locks_changed, name="Property USD"
        )

    @property
    def control_state(self):
        """Gets the current control state, it's the icon on the right side of the line with widgets."""
        return self._control_state

    @property
    def stage(self):
        """Gets the USD stage associated with this instance."""
        return self._valid_stage

    def _update_stage_adapters(self):
        def by_prio_r(adapter):
            return adapter.priority_read

        def by_prio_w(adapter):
            return adapter.priority_write

        stage_adapters = ac.get_adapter_registry().instantiate_all_stage_adapters(self._stage)
        self._stage_adapters_sorted_read = list(stage_adapters.values())
        self._stage_adapters_sorted_read.sort(key=by_prio_r)
        self._stage_adapters_sorted_write = list(stage_adapters.values())
        self._stage_adapters_sorted_write.sort(key=by_prio_w)

    def _on_adapter_changed(self, evt):
        self._update_stage_adapters()

    def get_valid_stage_adapter_read(self, path):
        """Gets the stage adapter that can read the given path.

        Args:
            path (str): The path to check for a valid stage adapter.

        Returns:
            :obj:`Usd.Stage`: The stage that can read from the given path."""
        for stage in self._stage_adapters_sorted_read:
            with contextlib.suppress(Exception):
                if stage.GetAttributeAtPath(path):
                    return stage
        return self._stage

    def get_valid_stage_adapter_write(self, path):
        """Gets the stage adapter that can write to the given path.

        Args:
            path (str): The path to check for a valid stage adapter.

        Returns:
            :obj:`Usd.Stage`: The stage that can write to the given path."""
        for stage in self._stage_adapters_sorted_write:
            with contextlib.suppress(Exception):
                if stage.GetAttributeAtPath(path):
                    return stage
        return self._stage

    @property
    def metadata(self):
        """Gets the metadata associated with this instance."""
        return self._metadata

    def update_control_state(self):
        """Updates the control state based on the current conditions."""
        control_state, force_refresh = self._control_state_mgr.update_control_state(self)

        # Redraw control state icon when the control state is changed
        if self._control_state != control_state or force_refresh:
            self._control_state = control_state
            if self._on_control_state_changed_fn:
                self._on_control_state_changed_fn()

    def set_on_control_state_changed_fn(self, fn):
        """Sets a callback function to be called when the control state changes.

        Args:
            fn (function): The callback function to be set."""
        self._on_control_state_changed_fn = fn

    def create_placeholder_attribute(self, name, prim=None, metadata=None):
        """Creates a placeholder attribute.

        Args:
            name (str): The name of the placeholder attribute to create.
            prim (Optional[:obj:`Usd.Prim`]): The USD primitive associated with the attribute.
            metadata (dict): The metadata to associate with the placeholder attribute."""
        return self._placeholder_cls(name, prim, metadata)

    def set_on_set_default_fn(self, fn):
        """Sets a callback function to be called when the default value is set.

        Args:
            fn (function): The callback function to be set."""
        self._on_set_default_fn = fn

    def clean(self):
        """Cleans up the instance by removing listeners and resetting state."""
        self._notification = None
        self._timeline_sub = None
        self._stage = None
        self._valid_stage = None
        self._stage_adapters_sorted_read = []
        self._stage_adapters_sorted_write = []
        self._adapter_change_listener = None
        self._spec_locks_subscription = None
        if self._listener:
            self._listener.Revoke()
            self._listener = None
        for listener in self._listener_adapters:
            listener.destroy()
        self._listener_adapters = []

    def is_different_from_default(self) -> bool:
        """Determines if the current value is different from the default value.

        Returns:
            bool: True if different, False otherwise."""
        self._update_value()
        # soft_range has been overridden
        if self._soft_range_min is not None and self._soft_range_max is not None:
            return True
        return self._different_from_default

    def might_be_time_varying(self) -> bool:
        """Determines if the associated attribute might vary over time.

        Returns:
            bool: True if it might vary, False otherwise."""
        self._update_value()
        return self._might_be_time_varying

    def is_ambiguous(self) -> bool:
        """Determines if the attribute's value is ambiguous due to multiple sources.

        Returns:
            bool: True if ambiguous, False otherwise."""
        self._update_value()
        return self._ambiguous

    def is_readonly(self) -> bool:
        """Determines if the attribute is read-only.

        Returns:
            bool: True if read-only, False otherwise."""
        return self._readonly

    def is_comp_ambiguous(self, index: int) -> bool:
        """Determines if a specific component of the attribute's value is ambiguous.

        Args:
            index (int): The index of the component to check.

        Returns:
            bool: True if the specified component is ambiguous, False otherwise."""
        self._update_value()
        comp_len = len(self._comp_ambiguous)
        if comp_len == 0 or index < 0:
            return self.is_ambiguous()
        if index < comp_len:
            return self._comp_ambiguous[index]
        return False

    def is_array_type(self) -> bool:
        """Determines if the attribute's value is of an array type.

        Returns:
            bool: True if an array type, False otherwise."""
        return self._is_array_type()

    def get_all_comp_ambiguous(self) -> List[bool]:
        """Retrieves a list indicating which components of the attribute's value are ambiguous.

        Returns:
            List[bool]: A list with each element indicating ambiguity of the corresponding component."""
        self._update_value()
        return self._comp_ambiguous

    def get_attribute_paths(self) -> List[Sdf.Path]:
        """Retrieves the attribute paths associated with this instance.

        Returns:
            List[Sdf.Path]: The list of attribute paths."""
        return self._object_paths

    def get_property_paths(self) -> List[Sdf.Path]:
        """Retrieves the property paths associated with this instance.

        Returns:
            List[Sdf.Path]: The list of property paths."""
        return self.get_attribute_paths()

    def get_prim_paths(self, stage) -> List[Sdf.Path]:
        """Returns the list of Sdf.Paths for the prims associated with this USD model.

        Args:
            stage (:obj:`Usd.Stage`): The stage to query for prim paths.

        Returns:
            List[:obj:`Sdf.Path`]: The list of prim paths."""
        prim_paths = set()
        for path in self._object_paths_set:
            prim_path = path.GetPrimPath()
            if stage.GetPrimAtPath(prim_path):
                prim_paths.add(prim_path)
        return list(prim_paths)

    def get_connections(self):
        """Returns the list of connections for the last attribute in the model.

        Returns:
            list: The list of connections."""
        return self._connections

    def get_bad_connection(self) -> tuple[bool, str]:
        """
        Retrieves the bad connection status and error message.

        Returns:
            tuple: A tuple containing two elements:
                - bool: True if there is a bad connection, False otherwise.
                - str: The error message associated with the bad connection.
        """
        return self._bad_connection, self._bad_connection_error

    def set_default(self, comp=-1):
        """Set the UsdAttribute default value if it exists in metadata.

        Args:
            comp (int): The component index to set default for. -1 means all components."""
        self.set_soft_range_userdata(None, None)
        if self.is_different_from_default() is False or self._has_default_value is False:
            if self._soft_range_min is not None and self._soft_range_max is not None:
                if self._on_set_default_fn:
                    self._on_set_default_fn()
                self.update_control_state()
            return

        current_time_code = self.get_current_time_code()

        with omni.kit.undo.group():
            # TODO clear timesample
            # However, when a value is timesampled, the "default" button is overridden by timesampled button,
            # so there's no way to invoke this function
            for attribute in self._get_attributes():
                if isinstance(attribute, (Usd.Attribute, AttributeAdapter)):
                    current_value = attribute.Get(current_time_code)
                    if comp >= 0:
                        # OM-46294: Make a value copy to avoid changing with reference.
                        default_value = copy.copy(current_value)
                        default_value[comp] = self._default_value[comp]
                    else:
                        default_value = self._default_value

                    self._change_property(attribute.GetPath(), default_value, current_value)

        # We just set all the properties to the same value, it's no longer ambiguous
        self._ambiguous = False
        self._comp_ambiguous.clear()

        self._different_from_default = False
        self._comp_different_from_default.clear()

        if self._on_set_default_fn:
            self._on_set_default_fn()

    def _create_placeholder_attributes(self, attributes, on_create_fn=None):
        try:
            self._editing += 1
            for index, attribute in enumerate(attributes):
                if isinstance(attribute, PlaceholderAttribute):
                    attributes[index] = attribute.CreateAttribute()
                    if on_create_fn:
                        on_create_fn(attributes[index])
        finally:
            self._editing -= 1

    def set_value(self, value, comp: int = -1) -> bool:
        """Sets the value of the attribute. Can set value for a specific component.

        Args:
            value (Any): The new value to set.
            comp (int): The component index to set the value for."""
        if self._min is not None:
            if hasattr(value, "__len__"):
                for i, item in enumerate(value):
                    if item < self._min:
                        value[i] = self._min
            else:
                if value < self._min:
                    value = self._min

        if self._max is not None:
            if hasattr(value, "__len__"):
                for i, item in enumerate(value):
                    if item > self._max:
                        value[i] = self._max
            else:
                if value > self._max:
                    value = self._max

        if not self._ambiguous and not any(self._comp_ambiguous) and value == self._value:
            return False

        if self.is_instance_proxy():
            self._post_notification("Cannot edit attributes of instance proxy.")
            self._update_value(True)  # reset value
            return False

        if self.is_locked():
            self._post_notification("Cannot edit locked attributes.")
            self._update_value(True)  # reset value
            return False

        if self._might_be_time_varying:
            self._post_notification("Setting time varying attribute is not supported yet")
            return False

        self._value = value if comp == -1 else UsdBase.update_value_by_comp(value, self._value, comp)
        attributes = self._get_attributes()
        if len(attributes) == 0:
            return False

        with omni.kit.undo.group():
            self._create_placeholder_attributes(attributes)
            if self._editing:

                # Allow dragging to update on any change, while typing should honor _change_on_edit_end
                iinput = carb.input.acquire_input_interface()  # pylint: disable=c-extension-no-member
                app_window = omni.appwindow.get_default_app_window()  # pylint: disable=c-extension-no-member
                mouse = app_window.get_mouse()
                mouse_down = iinput.get_mouse_value(mouse, carb.input.MouseInput.LEFT_BUTTON)

                # Use the setting if it is set.  Otherwise fall back to self._change_on_edit_end.
                # If the mouse is down, it must be dragging this field, so always update immediately.
                edit_end_setting = self._settings.get(
                    PERSISTENT_SETTINGS_PREFIX + "/exts/omni.kit.property.usd/update_on_press_enter"
                )
                local_change_on_edit_end = (
                    edit_end_setting if edit_end_setting is not None else self._change_on_edit_end
                )
                local_change_on_edit_end = not bool(mouse_down) if local_change_on_edit_end else False

                for i, attribute in enumerate(attributes):
                    self._ignore_notice = True

                    # OM-81448: When prim is defined inside session layer,
                    # edits should be authored into session layer directly
                    # instead of current edit target to avoid leaving stale
                    # overrides.
                    if comp == -1:
                        self._real_values[i] = self._value
                        if not local_change_on_edit_end:
                            self._change_property_2(attribute.GetPath(), self._value, undoable=False)
                    else:
                        # Only update a single component of the value (for vector type)
                        value = self._real_values[i]
                        self._real_values[i] = self._update_value_by_comp(value, comp)
                        if not local_change_on_edit_end:
                            self._change_property_2(attribute.GetPath(), value, undoable=False)

                    self._ignore_notice = False
            else:
                for i, attribute in enumerate(attributes):
                    self._ignore_notice = True
                    if attribute is None:
                        continue
                    # begin_edit is not called for certain widget (like Checkbox), issue the command directly
                    if comp == -1:
                        self._change_property(attribute.GetPath(), self._value, None)
                    else:
                        # Only update a single component of the value (for vector type)
                        value = self._real_values[i]
                        self._real_values[i] = self._update_value_by_comp(value, comp)
                        self._change_property(attribute.GetPath(), value, None)
                    self._ignore_notice = False

            if comp == -1:
                # We just set all the properties to the same value, it's no longer ambiguous
                self._ambiguous = False
                self._comp_ambiguous.clear()
            else:
                self._comp_ambiguous[comp] = False
                self._ambiguous = any(self._comp_ambiguous)

            if self._has_default_value:
                self._comp_different_from_default = [False] * self._get_comp_num()
                if comp == -1:
                    self._different_from_default = value != self._default_value
                    if self._different_from_default:
                        for index, _ in enumerate(self._comp_different_from_default):
                            self._comp_different_from_default[index] = not self._compare_value_by_comp(
                                value, self._default_value, index
                            )
                else:
                    self._comp_different_from_default[comp] = not self._compare_value_by_comp(
                        value, self._default_value, comp
                    )
                    self._different_from_default = any(self._comp_different_from_default)
            else:
                self._different_from_default = False
                self._comp_different_from_default.clear()

        self.update_control_state()
        return True

    def _is_prev_same(self):
        return self._prev_real_values == self._real_values

    def begin_edit(self):
        """Begins an edit operation by increasing the internal editing counter."""
        self._editing = self._editing + 1
        self._prev_value = self._value
        self._save_real_values_as_prev()

    def end_edit(self):
        """Ends an edit operation by decreasing the internal editing counter and updating the value if changed."""
        self._editing = self._editing - 1

        if self._is_prev_same():
            return

        attributes = self._get_attributes()
        with omni.kit.undo.group():
            self._create_placeholder_attributes(attributes)
            self._ignore_notice = True
            for i, attribute in enumerate(attributes):
                if attribute:
                    self._change_property(attribute.GetPath(), self._real_values[i], self._prev_real_values[i])
            self._ignore_notice = False
        # Set flags. It calls _on_control_state_changed_fn when the user finished editing
        self._update_value(True)

    def is_editing(self) -> bool:
        """Checks if the model is currently in an editing state.

        Returns:
            bool: True if editing, False otherwise."""
        return self._editing

    def _post_notification(self, message):
        try:
            import omni.kit.notification_manager as nm

            if not self._notification or self._notification.dismissed:
                status = nm.NotificationStatus.WARNING
                self._notification = nm.post_notification(message, status=status)
                carb.log_warn(message)
        except ModuleNotFoundError:
            pass

    def _get_edit_target(self, path: Sdf.Path) -> Usd.EditTarget:
        """Override this function to customize the target layer."""
        edit_target = self._stage.GetEditTarget()
        if self._auto_target_session_layer_def:
            # OM-75480: For props inside sesison layer, it will always change specs
            # in the session layer to avoid shadowing. Why it needs to be def is that
            # session layer is used for several runtime data for now as built-in cameras,
            # MDL material params, and etc. Not all of them create runtime prims inside
            # session layer. For those that are defined inside session layer, we should
            # avoid leaving delta inside other sublayers as they are shadowed and useless after
            # stage close.
            target_layer, _ = omni.usd.find_spec_on_session_or_its_sublayers(
                self._stage, path.GetPrimPath(), lambda spec: spec.specifier == Sdf.SpecifierDef
            )
            if target_layer:
                edit_target = Usd.EditTarget(target_layer)

        # return the EditTarget instead of a layer so that things like variant editing can utilize this too.
        # however, ChangeProperty command still takes layer rather than EditTarget, a new or improved command is needed to further support it
        return edit_target

    def _change_property_2(self, path, new_value: Any, *args, old_value: Any = None, undoable: bool = True, **kwargs):
        cmd_args = []
        cmd_kwargs = {}
        self._valid_stage = self.get_valid_stage_adapter_write(path)
        if not self._valid_stage:
            return

        read_stage = self.get_valid_stage_adapter_read(path)
        if read_stage != self._valid_stage:
            path = read_stage.convert_data(path, self._valid_stage.name)
            new_value = read_stage.convert_data(new_value, self._valid_stage.name)
            old_value = read_stage.convert_data(old_value, self._valid_stage.name)

        # If the value is set to it's default we can remove the property to prevent unecessary serialization of data.
        if (
            self._remove_if_default
            and not self._editing
            and self._has_default_value
            and (self._default_value == new_value)
        ):
            cmd_args = ["RemoveProperty"]
            cmd_kwargs = {
                "prop_path": path,
                "remove_from_layers": self._get_edit_target(path).GetLayer(),
                "usd_context_name": self._stage,
            }

        else:
            if isinstance(self._valid_stage, StageAdapter):
                cmd_args, cmd_kwargs, _ = self._valid_stage.GetChangeAttributeArgs(path, new_value, old_value)
            if not cmd_args:
                cmd_args = self._change_property_commands
                cmd_kwargs = {
                    "prop_path": path,
                    "value": new_value,
                    "prev": old_value,
                    "target_layer": self._get_edit_target(path).GetLayer(),
                    "usd_context_name": self._stage,
                }
        if undoable:
            omni.kit.commands.execute(*cmd_args, **cmd_kwargs)
        else:
            omni.kit.commands.create(*cmd_args, **cmd_kwargs).do()

    def _change_property(self, path: Sdf.Path, new_value: Any, old_value: Any):
        """To maintain backward compatibility, _change_property function is kept and forwards the call to _change_property_2"""
        self._change_property_2(path=path, new_value=new_value, old_value=old_value)

    def get_value_by_comp(self, comp: int):
        """Gets the value of a specific component of the attribute value.

        Args:
            comp (int): The component index to get the value for.

        Returns:
            Any: The value of the specified component."""
        self._update_value()
        if comp == -1:
            return self._value

        return self._get_value_by_comp(self._value, comp)

    def _save_real_values_as_prev(self):
        # It's like copy.deepcopy but not all USD types support pickling (e.g. Gf.Quat*)
        self._prev_real_values = [type(value)(value) for value in self._real_values]

    def _get_value_by_comp(self, value, comp: int):
        if value.__class__.__module__ == "pxr.Gf":
            if value.__class__.__name__.startswith("Quat"):
                if comp == 0:
                    return value.real
                return value.imaginary[comp - 1]
            if value.__class__.__name__.startswith("Matrix"):
                dimension = len(value)
                row = comp // dimension
                col = comp % dimension
                return value[row, col]
            if value.__class__.__name__.startswith("Vec"):
                return value[comp]
        else:
            if comp < len(value):
                return value[comp]

        return None

    def _update_value_by_comp(self, value, comp: int):
        """update value from self._value"""
        return UsdBase.update_value_by_comp(self._value, value, comp)

    @staticmethod
    def update_value_by_comp(from_value, to_value, comp: int):
        """Updates the value of a specific component.

        Args:
            from_value (Any): The value to update from.
            to_value (Any): The value to update to.
            comp (int): The component index to update."""
        if from_value.__class__.__module__ == "pxr.Gf":
            if from_value.__class__.__name__.startswith("Quat"):
                if comp == 0:
                    to_value.real = from_value.real
                else:
                    imaginary = from_value.imaginary
                    imaginary[comp - 1] = from_value.imaginary[comp - 1]
                    to_value.SetImaginary(imaginary)
            elif from_value.__class__.__name__.startswith("Matrix"):
                dimension = len(from_value)
                row = comp // dimension
                col = comp % dimension
                to_value[row, col] = from_value[row, col]
            elif from_value.__class__.__name__.startswith("Vec"):
                to_value[comp] = from_value[comp]
        else:
            to_value[comp] = from_value[comp]
        return to_value

    def _compare_value_by_comp(self, val1, val2, comp: int):
        return self._get_value_by_comp(val1, comp) == self._get_value_by_comp(val2, comp)

    def _get_comp_num(self):
        # TODO any better way than this??
        # Checks if the value type is a vector type
        if self._value.__class__.__module__ in ("pxr.Gf", "usdrt.Gf._Gf"):
            if self._value.__class__.__name__.startswith("Quat"):
                return 4
            if self._value.__class__.__name__.startswith("Matrix"):
                mat_dimension = len(self._value)
                return mat_dimension * mat_dimension
            if hasattr(self._value, "__len__"):
                return len(self._value)
        elif self._is_array_type() and self._treat_array_entry_as_comp:
            return len(self._value)
        return 0

    @Trace.TraceFunction
    def _on_usd_changed(self, notice, stage):
        if stage != self.stage:
            return

        if self._editing > 0:
            return

        if self._ignore_notice:
            return

        for path in notice.GetResyncedPaths():
            if path in self._object_paths_set:
                self._set_dirty()
                return

        for path in notice.GetChangedInfoOnlyPaths():
            if path in self._object_paths_set:
                self._set_dirty()
                return

    def _on_dirty(self):
        pass

    def _set_dirty(self):
        # OM-36400: Removed early return when self._editing > 0 because when tabbing between fields it
        # was causing 2nd field to not update due to this being called asynchronously after editing mode
        # was already turned on.
        self._dirty = True
        self._on_dirty()

    def _get_type_name(self, obj=None):
        if obj and not isinstance(obj, AttributeAdapter):
            if hasattr(obj, "GetTypeName"):
                return obj.GetTypeName()
            if hasattr(obj, "typeName"):
                return obj.typeName
            return None

        type_name = self._metadata.get(Sdf.PrimSpec.TypeNameKey, "unknown type")
        if isinstance(type_name, Sdf.ValueTypeName):
            return type_name
        return Sdf.ValueTypeNames.Find(type_name)

    def _is_array_type(self, obj=None):
        type_name = self._get_type_name(obj)

        if isinstance(type_name, Sdf.ValueTypeName):
            return type_name.isArray
        return False

    def is_value_array(self):
        """Checks if the attribute value is an array.

        Returns:
            bool: True if the attribute value is an array, False otherwise."""
        return False

    def _get_obj_type_default_value(self, obj):
        type_name = self._get_type_name(obj)

        if isinstance(type_name, Sdf.ValueTypeName):
            return type_name.defaultValue
        return None

    def _update_value(self, force=False):
        return self._update_value_objects(force, True)

    def _update_value_objects(self, force: bool, update_attribute: bool):
        def update():
            carb.profiler.begin(1, "UsdBase._update_value_objects")
            self._might_be_time_varying = False
            self._value = None
            self._has_default_value = False
            self._default_value = None
            self._real_values.clear()
            self._connections.clear()
            self._ambiguous = False
            self._comp_ambiguous.clear()
            self._different_from_default = False
            self._comp_different_from_default.clear()

            current_time_code = None
            for index, path in enumerate(self._object_paths):
                prev_stage, self._valid_stage = self._valid_stage, self.get_valid_stage_adapter_read(path)
                if not self._valid_stage:
                    continue

                if current_time_code is None or prev_stage != self._valid_stage:
                    current_time_code = self.get_current_time_code()

                if update_attribute:
                    obj = self._valid_stage.GetAttributeAtPath(path)
                    if not obj:
                        prim = self._valid_stage.GetPrimAtPath(path.GetPrimPath())
                        obj = self.create_placeholder_attribute(name=path.name, prim=prim, metadata=self._metadata)

                else:
                    obj = self._valid_stage.GetObjectAtPath(path)

                if not obj or obj.IsHidden():
                    continue

                value = self._read_value(obj, current_time_code)

                self._real_values.append(value)
                if isinstance(obj, (AttributeAdapter, Usd.Attribute)):
                    self._might_be_time_varying = self._might_be_time_varying or obj.GetNumTimeSamples() > 0
                    self._connections.append(list(obj.GetConnections()) if obj.HasAuthoredConnections() else [])
                # only need to check the first prim. All other prims are supposedly to be the same
                if index == 0:
                    self._value = value
                    if (
                        self._value
                        and self._is_array_type(obj)
                        and hasattr(self._value, "__len__")
                        and len(self._value) > 16
                    ):
                        self._is_big_array = True
                    comp_num = self._get_comp_num()
                    self._comp_ambiguous = [False] * comp_num
                    self._comp_different_from_default = [False] * comp_num
                    # Loads the default value
                    self._has_default_value, self._default_value = self._get_default_value(obj)
                elif self._value != value:
                    # check each item in array obj
                    all_children_equal = False
                    if hasattr(self._value, "__len__") and hasattr(value, "__len__") and len(self._value) == len(value):
                        all_children_equal = True
                        for i, sub_value in enumerate(self._value):
                            if sub_value != value[i]:
                                all_children_equal = False
                                break
                    if not all_children_equal:
                        self._value = value
                        self._ambiguous = True
                        comp_num = len(self._comp_ambiguous)
                        if comp_num > 0:
                            for i in range(comp_num):
                                if not self._comp_ambiguous[i]:
                                    self._comp_ambiguous[i] = not self._compare_value_by_comp(
                                        value, self._real_values[0], i
                                    )

                if self._has_default_value:
                    comp_num = len(self._comp_different_from_default)
                    if comp_num > 0:
                        for i in range(comp_num):
                            if not self._comp_different_from_default[i]:
                                self._comp_different_from_default[i] = not self._compare_value_by_comp(
                                    value, self._default_value, i
                                )
                        self._different_from_default |= any(self._comp_different_from_default)
                    else:
                        self._different_from_default = value != self._default_value

            self._dirty = False
            self._timeline_sub = self._timeline.get_timeline_event_stream().create_subscription_to_pop(
                self._on_timeline_event
            )

            self.update_control_state()
            carb.profiler.end(1)

        # Usdrt stage does not use resolver context
        if (self._dirty or force) and self.stage:
            resolver_context = self.stage.GetPathResolverContext()
            if resolver_context:
                with Ar.ResolverContextBinder(resolver_context):
                    with Ar.ResolverScopedCache():
                        update()
            else:
                update()
            return True
        return False

    def _get_default_value(self, prop, metadata=None):
        default_values = {"xformOp:scale": Gf.Vec3d(1.0, 1.0, 1.0), "primvars:multimatte_id": -1}
        if isinstance(prop, AttributeAdapter):
            path = prop.GetPath().pathString
            prop = self._stage.GetObjectAtPath(path)

        if isinstance(prop, Usd.Attribute):
            prim = prop.GetPrim()
            if prim:
                metadata = metadata if metadata else self._metadata
                custom = prop.GetCustomData()
                if "default" in custom:
                    # This is not the standard USD way to get default.
                    return True, custom["default"]
                if "customData" in metadata:
                    # This is to fetch default value for custom property.
                    default_value = metadata["customData"].get("default", None)
                    if default_value is not None:
                        return True, default_value
                else:
                    prim_definition = prim.GetPrimDefinition()
                    if prim_definition:
                        prop_spec = prim_definition.GetSchemaPropertySpec(prop.GetPath().name)
                        if prop_spec and prop_spec.default is not None:
                            return True, prop_spec.default

                if prop.GetName() in default_values:
                    return True, default_values[prop.GetName()]

                # If we still don't find default value, use type's default value
                value_type = prop.GetTypeName()
                if hasattr(value_type, "defaultValue"):
                    default_value = value_type.defaultValue
                elif value_type.isArray:
                    default_value = {}
                else:
                    default_value = type(prop.Get())()
                return True, default_value

        elif isinstance(prop, PlaceholderAttribute):
            return True, prop.Get()

        return False, None

    def _get_attributes(self):
        attributes = []
        for path in self._object_paths:
            self._valid_stage = self.get_valid_stage_adapter_read(path)
            if self._valid_stage:
                attr = self._valid_stage.GetAttributeAtPath(path)
                if attr:
                    if not attr.IsHidden():
                        attributes.append(attr)
                else:
                    prim = self._valid_stage.GetPrimAtPath(path.GetPrimPath())
                    attributes.append(
                        self.create_placeholder_attribute(name=path.name, prim=prim, metadata=self._metadata)
                    )
        return attributes

    def _get_objects(self):
        objects = []
        for path in self._object_paths:
            self._valid_stage = self.get_valid_stage_adapter_read(path)
            if self._valid_stage:
                obj = self._valid_stage.GetObjectAtPath(path)
                if obj and not obj.IsHidden():
                    objects.append(obj)

        return objects

    def _on_timeline_event(self, e):
        if e.type == int(omni.timeline.TimelineEventType.CURRENT_TIME_TICKED):
            current_time = e.payload["currentTime"]
            if current_time != self._current_time:
                self._current_time = current_time
                if self._might_be_time_varying:
                    self._set_dirty()
        elif e.type == int(omni.timeline.TimelineEventType.TENTATIVE_TIME_CHANGED):
            tentative_time = e.payload["tentativeTime"]
            if tentative_time != self._current_time:
                self._current_time = tentative_time
                if self._might_be_time_varying:
                    self._set_dirty()

    def _get_connected_attr(self, obj, connected_path) -> tuple[Usd.Prim, Usd.Attribute]:
        used_paths = []
        while True:
            if connected_path.pathString in used_paths:
                if not self._bad_connection_error:
                    carb.log_warn(f"found connection with infinite loop: {used_paths}")
                return f"Connection with infinite loop: {used_paths}", None, None

            connected_prim = obj.GetPrim().GetStage().GetPrimAtPath(connected_path.GetPrimPath())
            used_paths.append(connected_path.pathString)
            if connected_prim:
                connected_attr = connected_prim.GetAttribute(connected_path.name)
                if connected_attr and connected_attr.HasAuthoredConnections():
                    connections = connected_attr.GetConnections()
                    if connections:
                        # NOTE: Only 1 connection is supported
                        connected_path = connections[0]
                        continue
                    return "No connections", None, None
                return "", connected_prim, connected_attr
            return "Connected prim not found", None, None

    def _read_value(self, obj, time_code):
        carb.profiler.begin(1, "UsdBase._read_value")
        if time_code:
            val = obj.Get(time_code)
        else:
            val = obj.Get()

        if isinstance(val, Sdf.UnregisteredValue):
            val = val.value
            # mark as read-only as value should never be changed
            self._readonly = True

        if val is None:
            if isinstance(obj, Usd.Attribute) and self._follow_connections:
                self._bad_connection = False
                connections = obj.GetConnections()
                for connected_path in connections:
                    msg, connected_prim, connected_attr = self._get_connected_attr(obj, connected_path)
                    if not connected_attr:
                        self._bad_connection = True
                        self._bad_connection_error = msg
                        break

                    if connected_attr:
                        if self._get_type_name(obj) != self._get_type_name(connected_attr):
                            self._bad_connection = True
                            self._bad_connection_error = f"Connection is wrong type. {self._get_type_name(obj)} vs {self._get_type_name(connected_attr)}"
                            break

                        val = connected_attr.Get()
                        if not val:
                            result, val = self._get_default_value(
                                connected_attr, metadata=connected_prim.GetAllMetadata()
                            )
                            if not result:
                                val = self._get_obj_type_default_value(connected_attr)
                    # NOTE: Only 1 connection is supported
                    break

            if val is None:
                result, val = self._get_default_value(obj)
                if not result:
                    val = self._get_obj_type_default_value(obj)

        carb.profiler.end(1)
        return val

    def _on_spec_locks_changed(self, event: carb.events.IEvent):
        payload = get_layer_event_payload(event)
        if payload and payload.event_type == LayerEventType.SPECS_LOCKING_CHANGED:
            self.update_control_state()

    def _get_usd_context(self):
        if not self._usd_context:
            self._usd_context = omni.usd.get_context_from_stage(self._stage)

        return self._usd_context

    def set_locked(self, locked):
        """Sets the locked state of the attributes.

        Args:
            locked (bool): Whether to lock or unlock the attributes."""
        usd_context = self._get_usd_context()
        if not usd_context:
            carb.log_warn("Current stage is not attached to any usd context.")
            return

        if locked:
            omni.kit.usd.layers.lock_specs(usd_context, self._object_paths, False)
        else:
            omni.kit.usd.layers.unlock_specs(usd_context, self._object_paths, False)

    def is_instance_proxy(self):
        """Checks if the object is an instance proxy.

        Returns:
            bool: True if the object is an instance proxy, False otherwise."""
        if not self._object_paths:
            return False

        path = Sdf.Path(self._object_paths[0]).GetPrimPath()
        prim = self._stage.GetPrimAtPath(path) if self._stage else None

        return prim and prim.IsInstanceProxy()

    def is_locked(self):
        """Checks if the attributes are locked.

        Returns:
            bool: True if attributes are locked, False otherwise."""
        usd_context = self._get_usd_context()
        if not usd_context:
            carb.log_warn("Current stage is not attached to any usd context.")
            return False

        return all(omni.kit.usd.layers.is_spec_locked(usd_context, path) for path in self._object_paths)

    def has_connections(self):
        """Checks if the last attribute in the model has connections.

        Returns:
            bool: True if there are connections, False otherwise."""
        return len(self._connections[-1]) > 0

    def get_value(self):
        """Gets the value of the attribute.

        Returns:
            Any: The current value of the attribute."""
        self._update_value()
        return self._value

    def get_stage(self):
        """Gets the stage of the attribute.

        Returns:
            :obj:`Usd.Stage`: The stage of the attribute."""
        return self._stage

    def get_current_time_code(self):
        """Gets the current time code of the stage.

        Returns:
            :obj:`Usd.TimeCode`: The current time code."""
        if self.stage:
            if isinstance(self.stage, StageAdapter):
                return self.stage.get_frame_time_code(self._current_time)
            if isinstance(self.stage, Usd.Stage):
                return Usd.TimeCode(
                    omni.usd.get_frame_time_code(self._current_time, self.stage.GetTimeCodesPerSecond())
                )

        return None

    def set_soft_range_userdata(self, soft_range_min, soft_range_max):
        """Sets the soft range for the attributes.

        Args:
            soft_range_min (float): The minimum value of the soft range.
            soft_range_max (float): The maximum value of the soft range."""
        # set soft_range userdata settings

        for attribute in self._get_attributes():
            if isinstance(attribute, Usd.Attribute):
                if soft_range_min is None and soft_range_max is None:
                    attribute.SetCustomDataByKey("omni:kit:property:usd:soft_range_ui", None)
                else:
                    attribute.SetCustomDataByKey(
                        "omni:kit:property:usd:soft_range_ui", Gf.Vec2f(soft_range_min, soft_range_max)
                    )

        self._soft_range_min = soft_range_min
        self._soft_range_max = soft_range_max

    def get_layers_with_strongest_value_opinions(self) -> list[Sdf.Layer]:
        """Gets a list of strongest layers that contribute to the value of each attributes in the model.

        Returns:
            list[Sdf.Layer]: The list of layers contributed to each attribute.
        """
        layers = []

        for attribute in self._get_attributes():
            prop_stack = attribute.GetPropertyStack(self.get_current_time_code())
            for prop_spec in prop_stack:
                if prop_spec == prop_stack[-1] or prop_spec.HasDefaultValue():
                    layers.append(prop_spec.layer)
                    break

        return layers

    get_attributes = _get_attributes
    get_objects = _get_objects
