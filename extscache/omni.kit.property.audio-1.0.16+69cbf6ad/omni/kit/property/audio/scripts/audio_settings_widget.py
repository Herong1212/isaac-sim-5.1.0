# Copyright (c) 2020-2021, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

"""A module providing a widget to manage audio settings for USD scenes within the Omniverse Kit."""


import omni.kit.app
import omni.ui as ui
import omni.usd
import omni.usd.audio
from omni.kit.property.usd.usd_property_widget import UsdPropertiesWidgetBuilder
from omni.kit.window.property.templates import SimplePropertyWidget
from pxr import Usd


class AudioSettingsWidget(SimplePropertyWidget):
    """A widget to manage audio settings in a USD scene.

    This widget allows users to manipulate various audio parameters such as the active listener, doppler effects, distance delay, and others. It provides a user interface to modify settings that affect the audio simulation in the scene, including the speed of sound, doppler scale, and the timescale for spatial and non-spatial audio processing. The widget interacts with the USD stage and its audio interface to reflect changes and update the scene accordingly.
    """

    def __init__(self):
        """Initializes the AudioSettingsWidget with default settings."""
        super().__init__(title="Audio Settings", collapsed=False)
        self._stage = None
        self._audio = omni.usd.audio.get_stage_audio_interface()
        self._listener_setting_model = None
        self._events = self._audio.get_metadata_change_stream()
        if self._events is not None:
            self._stage_event_sub = self._events.create_subscription_to_pop(
                self._on_metadata_event, name="audio settings window"
            )

        self._doppler_setting = None
        self._distance_delay_setting = None
        self._interaural_delay_setting = None
        self._concurrent_voices_setting = None
        self._speed_of_sound_setting = None
        self._doppler_scale_setting = None
        self._doppler_limit_setting = None
        self._spatial_timescale_setting = None
        self._nonspatial_timescale_setting = None
        self._any_item_visible = None
        self._listener_setting = None
        self._doppler_setting_model = None
        self._distance_delay_setting_model = None
        self._interaural_delay_setting_model = None
        self._concurrent_voices_setting_notifier = None
        self._speed_of_sound_setting_notifier = None
        self._doppler_scale_setting_notifier = None
        self._doppler_limit_setting_notifier = None
        self._spatial_timescale_setting_notifier = None
        self._nonspatial_timescale_setting_notifier = None

    def __del__(self):
        self._stage_event_sub = None
        self._events = None

    def on_new_payload(self, payload):
        """Handles a new payload for the widget.

        Args:
            payload (dict): The new payload to be handled by the widget.

        Returns:
            bool: True if payload is not None, False otherwise."""
        if not super().on_new_payload(payload):
            return False

        # stage is not part of LayerItem payload
        self.set_stage(omni.usd.get_context().get_stage())

        return payload is not None

    class ListenerComboBoxNotifier(omni.ui.AbstractItemModel):
        """A class that represents a custom item model for a combo box notifier.

        This model manages the selection and notification of changes in a combo box that represents a list of listeners. It is designed to be used in a UI context where the user can select an active listener from a dropdown menu. The class also handles the refresh of the item list based on external callbacks.

        Args:
            refresh_items_callback (Callable[[], List[str]]): A callback function that returns a list of strings representing the available items for the combo box.
            set_callback (Callable[[int], None]): A callback function that takes an index as an argument and sets the selected item based on this index.
        """

        class MinimalItem(omni.ui.AbstractItem):
            """A minimalist UI item for representing an option in a combo box.

            This class is used to create a simple UI element representing a selectable option within a combo box widget.

            Args:
                text (str): The display text for the combo box option."""

            def __init__(self, text):
                """Initializes a MinimalItem instance with default settings."""
                super().__init__()
                self.model = omni.ui.SimpleStringModel(text)

        def __init__(self, refresh_items_callback, set_callback):
            """Initializer for ListenerComboBoxNotifier."""
            super().__init__()
            self._current_index = omni.ui.SimpleIntModel()
            self._current_index.add_value_changed_fn(self._changed_model)
            self._set_callback = set_callback
            self._refresh_items_callback = refresh_items_callback
            self._options = []
            self.refresh_items()
            self._path = ""

        def get_value_as_string(self):
            """Returns the current path as a string.

            Returns:
                str: The current path."""
            return self._path

        def refresh_items(self):
            """Refreshes the items in the combo box based on the refresh_items_callback."""
            self._options = ["Active Camera"]
            self._options.extend(self._refresh_items_callback())

            self._items = [AudioSettingsWidget.ListenerComboBoxNotifier.MinimalItem(text) for text in self._options]

            return self._items

        def _changed_model(self, model):
            self._set_callback(model.as_int - 1)
            self._item_changed(None)

        def set_value(self, value):
            """Sets the value of the selected item.

            Args:
                value (str): The value to set as the selected item."""
            # item 0 will always be "Active Camera" => handle 'None' or an empty string specially
            #   as if it were that value.
            if value is None or value == "":
                self._current_index.as_int = 0
                self._path = ""
                return

            for i, option in enumerate(self._options):
                if option == value:
                    self._current_index.as_int = i
                    break

            self._path = value

        def get_item_children(self, item):
            """Gets the children of the given item.

            Args:
                item (AbstractItem): The item to get children for.

            Returns:
                The children of the given item.
            """
            return self._items

        def get_item_value_model(self, item, column_id):
            """Gets the value model for the item in the given column.

            Args:
                item (AbstractItem): The item to get the value model for.
                column_id (int): The ID of the column.

            Returns:
                The value model of the input item.
            """
            if item is None:
                return self._current_index
            return item.model

    class DefaultsComboBoxNotifier(omni.ui.AbstractItemModel):
        """A class for managing default audio feature settings via a combo box UI component.

        This class provides a way to select between different default states for audio features such as on, off, force on, and force off. It is used within the audio settings widget to control settings like Doppler effect, distance delay, and more.

        Args:
            set_callback (Callable[[int], None]): A callback function that is called when the selected option changes. The callback is passed the integer value associated with the selected option.
        """

        class MinimalItem(omni.ui.AbstractItem):
            """A minimalist UI item for representing an option in a combo box.

            This class is used to create a simple UI element representing a selectable option within a combo box widget.

            Args:
                text (str): The display text for the combo box option."""

            def __init__(self, text):
                """Initializes a MinimalItem instance with default settings."""
                super().__init__()
                self.model = omni.ui.SimpleStringModel(text)

        def __init__(self, set_callback):
            """Initializer for DefaultsComboBoxNotifier."""
            super().__init__()
            self._options = [
                ["on", omni.usd.audio.FeatureDefault.ON],
                ["off", omni.usd.audio.FeatureDefault.OFF],
                ["force on", omni.usd.audio.FeatureDefault.FORCE_ON],
                ["force off", omni.usd.audio.FeatureDefault.FORCE_OFF],
            ]

            self._current_index = omni.ui.SimpleIntModel()
            self._current_index.add_value_changed_fn(self._changed_model)
            self._set_callback = set_callback

            self._items = [
                AudioSettingsWidget.DefaultsComboBoxNotifier.MinimalItem(text) for (text, value) in self._options
            ]

        def _changed_model(self, model):
            self._set_callback(self._options[model.as_int][1])
            self._item_changed(None)

        def set_value(self, value):
            """Sets the selected value in the combo box.

            Args:
                value (int): The value to be set as selected in the combo box."""
            for i in range(0, len(self._options) - 1):
                if self._options[i][1] == value:
                    self._current_index.as_int = i
                    break

        def get_item_children(self, item):
            """Returns the child items of the given item.

            Args:
                item (omni.ui.AbstractItem): The item to get children for.

            Returns:
                The children of the given item.
            """
            return self._items

        def get_item_value_model(self, item, column_id):
            """Gets the value model for the item and column id.

            Args:
                item (omni.ui.AbstractItem): The item to get the model for.
                column_id (int): The column id for which the model is requested.

            Returns:
                The value model for the item.
            """
            if item is None:
                return self._current_index
            return item.model

    class ChangeNotifier(omni.ui.AbstractValueModel):
        """A model representing the value of a changeable entity in the UI.

        This model notifies the provided callback with the updated value when a change occurs. It is typically used to reflect and manipulate values within UI components.

        Args:
            update_callback (Callable[[Any], None]): The callback function to invoke when the value changes."""

        def __init__(self, update_callback):
            """Initializes a new instance of ChangeNotifier."""
            super().__init__()
            self._update_callback = update_callback
            self._value = 0

        def get_value_as_string(self):
            """Returns the current value as a string.

            Returns:
                str: The value of the model represented as a string."""
            return str(self._value)

        def get_value_as_int(self):
            """Retrieves the current value as an integer.

            Returns:
                int: The value of the model converted to an integer."""
            return int(self._value)

        def get_value_as_float(self):
            """Retrieves the current value as a float.

            Returns:
                float: The value of the model converted to a float."""
            return float(self._value)

    class SlowChangeNotifier(ChangeNotifier):
        """A notifier for handling slow changes to values.

        This class inherits from ChangeNotifier and is designed to update its value in a way
        that does not immediately trigger an update callback. Instead, the update callback
        is triggered when the end_edit method is called. This allows for delayed
        notification of changes, which is useful in scenarios where immediate feedback
        from every change is not necessary or desired."""

        def set_value(self, value):
            """Sets the value to the notifier without triggering an update callback.

            Args:
                value (Any): The new value to be set."""
            self._value = value
            self._value_changed()

        def end_edit(self):
            """Triggers the update callback with the current value."""
            self._update_callback(self._value)

    class FastChangeNotifier(ChangeNotifier):
        """A class that provides a fast notification mechanism for value changes.

        This notifier is designed to immediately trigger an update callback whenever its value is changed, without waiting for an edit to end. It is a specialized version of ChangeNotifier, inheriting its interface for value retrieval and modification.

        Args:
            update_callback (callable): A function to be called whenever the value changes."""

        def set_value(self, value):
            """Sets the value to the notifier without triggering an update callback.

            Args:
                value (Any): The new value to be set."""
            self._value = value
            self._value_changed()
            self._update_callback(self._value)

    def set_stage(self, stage: Usd.Stage):
        """Sets the stage for audio settings.

        Args:
            stage (Usd.Stage): The stage to be set for the widget."""
        self._stage = stage

    def _caption(self, text, width=150):
        """Create a formated heading"""
        with omni.ui.ZStack():
            omni.ui.Rectangle(name="caption", width=width, style={"background_color": 0x454545})
            omni.ui.Label(text, name="caption")

    def _create_tooltip(self, text):
        """Create a tooltip in a fixed style"""
        with omni.ui.VStack(width=400, style={"Label": {"color": 0xFF3B494B}}):
            omni.ui.Label(text, word_wrap=True)

    def _refresh_active_listener(self):
        if not self._listener_setting_model:
            return

        active_listener = self._audio.get_active_listener()

        if active_listener is None:
            self._listener_setting_model.set_value(None)
        else:
            self._listener_setting_model.set_value(str(active_listener.GetPath()))

    def _refresh(self):
        self._refresh_active_listener()

        if not self._listener_setting_model:
            return

        if self._doppler_setting:
            self._doppler_setting.model.set_value(self._audio.get_doppler_default())
        if self._distance_delay_setting:
            self._distance_delay_setting.model.set_value(self._audio.get_distance_delay_default())
        if self._interaural_delay_setting:
            self._interaural_delay_setting.model.set_value(self._audio.get_interaural_delay_default())
        if self._concurrent_voices_setting:
            self._concurrent_voices_setting.model.set_value(self._audio.get_concurrent_voices())
        if self._speed_of_sound_setting:
            self._speed_of_sound_setting.model.set_value(self._audio.get_speed_of_sound())
        if self._doppler_scale_setting:
            self._doppler_scale_setting.model.set_value(self._audio.get_doppler_scale())
        if self._doppler_limit_setting:
            self._doppler_limit_setting.model.set_value(self._audio.get_doppler_limit())
        if self._spatial_timescale_setting:
            self._spatial_timescale_setting.model.set_value(self._audio.get_spatial_time_scale())
        if self._nonspatial_timescale_setting:
            self._nonspatial_timescale_setting.model.set_value(self._audio.get_nonspatial_time_scale())

    def _on_metadata_event(self, event):
        if event.type == int(omni.usd.audio.EventType.METADATA_CHANGE):
            self._refresh()

        elif event.type == int(omni.usd.audio.EventType.LISTENER_LIST_CHANGE):
            if self._listener_setting_model is not None:
                self._listener_setting_model.refresh_items()

        elif event.type == int(omni.usd.audio.EventType.ACTIVE_LISTENER_CHANGE):
            self._refresh_active_listener()

    def _refresh_listeners(self):
        listener_list = []
        count = self._audio.get_listener_count()
        for i in range(0, count):
            listener_list.append(str(self._audio.get_listener_by_index(i).GetPath()))

        return listener_list

    def _set_active_listener(self, index):
        # a negative index means the active camera should be used as the listener.
        if index < 0:
            self._audio.set_active_listener(None)

        # all other indices are assumed to be an index into the listener list.
        else:
            prim = self._audio.get_listener_by_index(index)

            if prim is None:
                return

            self._audio.set_active_listener(prim)

    def _add_label(self, label: str):
        filter_text = self._filter.name
        UsdPropertiesWidgetBuilder.create_label(label, {}, {"highlight": filter_text})
        self._any_item_visible = True

    def build_items(self):
        """Builds the UI items for the audio settings widget."""

        def item_visible(label: str) -> bool:
            return not self._filter or self._filter.matches(label)

        with omni.ui.VStack(height=0, spacing=8):
            if item_visible("Active Listener"):
                with ui.HStack():
                    self._add_label("Active Listener")
                    self._listener_setting_model = AudioSettingsWidget.ListenerComboBoxNotifier(
                        self._refresh_listeners, self._set_active_listener
                    )
                    self._listener_setting = omni.ui.ComboBox(
                        self._listener_setting_model,
                        tooltip_fn=lambda: self._create_tooltip(
                            "The path to the active Listener prim in the current USD scene. "
                            + "Spatial audio calculations use the active listener as the position "
                            + "(and optionally orientation) in 3D space, where the audio is heard "
                            + "from. This value must be set to a valid Listener prim if 'Use "
                            + "active camera as listener' is unchecked."
                        ),
                    )

            if item_visible("Doppler default"):
                with ui.HStack():
                    self._add_label("Doppler default")
                    self._doppler_setting_model = AudioSettingsWidget.DefaultsComboBoxNotifier(
                        self._audio.set_doppler_default
                    )
                    self._doppler_setting = omni.ui.ComboBox(
                        self._doppler_setting_model,
                        tooltip_fn=lambda: self._create_tooltip(
                            "This sets the value that Sound prims will use for enableDoppler "
                            + "when that parameter is set to 'default'. This also allows the "
                            + "setting to be forced on or off on all prims for testing purposes, "
                            + "using the 'force on' and 'force off' values"
                        ),
                    )

            if item_visible("Distance delay default"):
                with ui.HStack():
                    self._add_label("Distance delay default")
                    self._distance_delay_setting_model = AudioSettingsWidget.DefaultsComboBoxNotifier(
                        self._audio.set_distance_delay_default
                    )
                    self._distance_delay_setting = omni.ui.ComboBox(
                        self._distance_delay_setting_model,
                        tooltip_fn=lambda: self._create_tooltip(
                            "The value that Sound prims will use for enableDistanceDelay when "
                            + "that parameter is set to 'default'. This also allows the setting "
                            + "to be forced on or off on all prims for testing purposes, using "
                            + "the 'force on' and 'force off' values"
                        ),
                    )

            if item_visible("Interaural delay default"):
                with ui.HStack():
                    self._add_label("Interaural delay default")
                    self._interaural_delay_setting_model = AudioSettingsWidget.DefaultsComboBoxNotifier(
                        self._audio.set_interaural_delay_default
                    )
                    self._interaural_delay_setting = omni.ui.ComboBox(
                        self._interaural_delay_setting_model,
                        tooltip_fn=lambda: self._create_tooltip(
                            "The value that Sound prims will use for enableInterauralDelay when "
                            + "that parameter is set to 'default'. This also allows the setting "
                            + "to be forced on or off on all prims for testing purposes, using "
                            + "the 'force on' and 'force off' values"
                        ),
                    )

            if item_visible("Concurrent voices"):
                with ui.HStack():
                    self._add_label("Concurrent voices")
                    self._concurrent_voices_setting_notifier = AudioSettingsWidget.SlowChangeNotifier(
                        self._audio.set_concurrent_voices
                    )
                    self._concurrent_voices_setting = omni.ui.IntDrag(
                        self._concurrent_voices_setting_notifier,
                        min=2,
                        max=4096,
                        tooltip_fn=lambda: self._create_tooltip(
                            "The number of sounds in a scene that can be played concurrently. "
                            + "In a scene where there this is set to N and N + 1 sounds are "
                            + "played concurrently, the N + 1th sound will be simulated instead "
                            + "of playing on the audio device and instead simulate that voice. "
                            + "The simulated voice will begin playing again when fewer than N "
                            + "voices are playing"
                        ),
                    )

            if item_visible("Speed of sound"):
                with ui.HStack():
                    self._add_label("Speed of sound")
                    self._speed_of_sound_setting_notifier = AudioSettingsWidget.FastChangeNotifier(
                        self._audio.set_speed_of_sound
                    )
                    self._speed_of_sound_setting = omni.ui.FloatDrag(
                        self._speed_of_sound_setting_notifier,
                        min=0.0001,
                        max=float("inf"),
                        step=1.0,
                        tooltip_fn=lambda: self._create_tooltip(
                            "Sets the speed of sound in the medium surrounding the listener "
                            + "(typically air). This is measured in meters per second. This would "
                            + "typically be adjusted when doing an underwater scene (as an "
                            + "example). The speed of sound in dry air at sea level is "
                            + "approximately 340.0m/s."
                        ),
                    )

            if item_visible("Doppler scale"):
                with ui.HStack():
                    self._add_label("Doppler scale")
                    self._doppler_scale_setting_notifier = AudioSettingsWidget.FastChangeNotifier(
                        self._audio.set_doppler_scale
                    )
                    self._doppler_scale_setting = omni.ui.FloatDrag(
                        self._doppler_scale_setting_notifier,
                        min=0.0001,
                        max=float("inf"),
                        tooltip_fn=lambda: self._create_tooltip(
                            "The scaler that can exaggerate or lessen the Doppler effect. Setting "
                            + "this above 1.0 will exaggerate the Doppler effect. Setting this "
                            + "below 1.0 will lessen the Doppler effect."
                        ),
                    )

            if item_visible("Doppler limit"):
                with ui.HStack():
                    self._add_label("Doppler limit")
                    self._doppler_limit_setting_notifier = AudioSettingsWidget.FastChangeNotifier(
                        self._audio.set_doppler_limit
                    )
                    self._doppler_limit_setting = omni.ui.FloatDrag(
                        self._doppler_limit_setting_notifier,
                        min=1.0,
                        max=float("inf"),
                        tooltip_fn=lambda: self._create_tooltip(
                            "A Limit on the maximum Doppler pitch shift that can be applied to "
                            + "a playing voice. Since supersonic spatial audio is not handled, a "
                            + "maximum frequency shift must be set for prims that move toward the "
                            + "listener at or faster than the speed of sound."
                        ),
                    )

            if item_visible("Spatial time scale"):
                with ui.HStack():
                    self._add_label("Spatial time scale")
                    self._spatial_timescale_setting_notifier = AudioSettingsWidget.FastChangeNotifier(
                        self._audio.set_spatial_time_scale
                    )
                    self._spatial_timescale_setting = omni.ui.FloatDrag(
                        self._spatial_timescale_setting_notifier,
                        min=0.0001,
                        max=float("inf"),
                        tooltip_fn=lambda: self._create_tooltip(
                            "The timescale modifier for all spatial voices. Each spatial Sound "
                            + "prim multiplies its timeScale attribute by this value. For "
                            + "example, setting this to 0.5 will play all spatial sounds at half "
                            + "speed and setting this to 2.0 will play all spatial sounds at "
                            + "double speed. This affects delay times for the distance delay "
                            + "effect. This feature is intended to allow time-dilation to be "
                            + "performed with the sound effects in the scene without affecting "
                            + "non-spatial elements like the background music."
                        ),
                    )

            if item_visible("Non-spatial time scale"):
                with ui.HStack():
                    self._add_label("Non-spatial time scale")
                    self._nonspatial_timescale_setting_notifier = AudioSettingsWidget.FastChangeNotifier(
                        self._audio.set_nonspatial_time_scale
                    )
                    self._nonspatial_timescale_setting = omni.ui.FloatDrag(
                        self._nonspatial_timescale_setting_notifier,
                        min=0.0001,
                        max=float("inf"),
                        tooltip_fn=lambda: self._create_tooltip(
                            "The timescale modifier for all non-spatial voices. Each non-spatial "
                            + "Sound prim multiplies its timeScale attribute by this value. For "
                            + "example, setting this to 0.5 will play all non-spatial sounds at "
                            + "half speed and setting this to 2.0 will play all non-spatial "
                            + "sounds at double speed."
                        ),
                    )

        self._refresh()
