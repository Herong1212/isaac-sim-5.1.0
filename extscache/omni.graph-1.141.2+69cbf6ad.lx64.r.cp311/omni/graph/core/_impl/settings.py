"""Management for the OmniGraph settings.

The setting can be checked directly using this model:

    import omni.graph.core as og

    if og.Settings()(og.Settings.MY_SETTING_NAME):
        # the setting value is True (for a boolean setting)
    else:
        # the setting value if False

You can also use the class as a context manager to temporarily modify the setting:

    import omni.graph.core as og

    while og.Settings.temporary(og.Settings.MY_SETTING_NAME, False):
        # Do something that needs the setting off
"""

from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
from typing import Any, Dict, List, Tuple, Union

import carb
import omni.graph.tools._internal as ogi


@dataclass
class Settings:
    """Class that packages up all of the OmniGraph settings handling into a common location. The settings themselves
    are handled through the Carbonite settings ABI, this just provides a nicer and more focused interface.
    Values here should also be reflected in the C++ OmniGraphSettings class.
    """

    VERSION: str = "/persistent/omnigraph/settingsVersion"
    """Version number of these settings"""

    UPDATE_MESH_TO_HYDRA: str = "/persistent/omnigraph/updateMeshPointsToHydra"
    """Update mesh points directly to Hydra"""

    PLAY_COMPUTE_GRAPH: str = "/app/player/playComputegraph"
    """Evaluate OmniGraph when the Kit 'Play' button is pressed"""

    OPTIMIZE_GENERATED_PYTHON: str = "/persistent/omnigraph/generator/pyOptimize"
    """Optimize the Python code being output by the node generator"""

    ENABLE_PATH_CHANGED_CALLBACK: str = "/persistent/omnigraph/enablePathChangedCallback"
    """Enable the deprecated Node.pathChangedCallback. This will affect performance."""

    DEPRECATIONS_ARE_ERRORS: str = "/persistent/omnigraph/deprecationsAreErrors"
    """Modify deprecation paths to raise errors or exceptions instead of logging warnings."""

    DISABLE_INFO_NOTICE_HANDLING_IN_PLAYBACK = "/persistent/omnigraph/disableInfoNoticeHandlingInPlayback"
    """Disable all processing of info-only notices by OG. This is an optimization for applications which do not
    require any triggering of OG via USD (value_changed and path_changed callbacks, lazy-graph etc"""

    AUTO_INSTANCING_ENABLED = "/persistent/omnigraph/autoInstancingEnabled"
    """Control whether or not similar graph should be merged together as instances in order to allow vectorized compute """

    # --------------------------------------------------------------------------------------------------------------
    def __str__(self) -> str:
        """Returns a representation of all current settings"""
        settings = carb.settings.get_settings()
        return "\n".join(
            [
                f"{name} = {settings.get(field.default)}"
                for name, field in self.__dataclass_fields__.items()  # noqa: PLE1101
            ]
        )

    # --------------------------------------------------------------------------------------------------------------
    def __call__(self, setting_name: str) -> Any:
        """Look up and return the current value of the passed-in setting
        Call as og.Settings()(og.Settings.UPDATE_TO_USD)"""
        return carb.settings.get_settings().get(setting_name)

    # --------------------------------------------------------------------------------------------------------------
    @staticmethod
    def generator_settings() -> ogi.Settings:
        """Return the generator settings object corresponding to the current carb settings

        Returns:
            omni.graph.tools.Settings: Current settings object used by the code generator
        """
        settings = ogi.Settings()
        carb_settings = carb.settings.get_settings()
        for setting_name in settings.all().keys():
            if carb_settings.get(f"/persistent/omnigraph/generator/{setting_name}"):
                setattr(settings, setting_name, True)
        return settings

    # --------------------------------------------------------------------------------------------------------------
    @staticmethod
    @contextmanager
    def temporary(setting_name: Union[str, List[Tuple[str, Any]], Dict[str, Any]], setting_value: Any = None):
        """Generator to temporarily use a new setting value

        Args:
            setting_name: A string containing the path to the setting (e.g. "/persistent/omnigraph/deprecationsAreErrors")
                          or a list of tuples containing setting name and value pairs.
            setting_value: New value for the setting. 'None' is not a valid setting value and will generate a
                           warning. Ignored if 'setting_name' is a list.

        If a setting does not yet exist it will be created at context entry and removed at context exit.

        Examples:

            .. code-block:: python

                with og.Settings.temporary(og.Settings.AUTO_INSTANCING_ENABLED, True):
                    do_something_with_auto_instancing()

                with og.Settings.temporary([("/MySettings/debug", True), (og.Settings.DEPRECATIONS_ARE_ERRORS, False)]):
                    do_something_with_deprecations_as_errors_disabled()
        """
        # If we got a single setting, turn it into a list.
        if isinstance(setting_name, list):
            items = setting_name
        elif isinstance(setting_name, dict):
            items = list(setting_name.items())
        else:
            items = [(setting_name, setting_value)]

        settings = carb.settings.get_settings()
        original_values = []
        try:
            for name, new_value in items:
                original_values += [settings.get(name)]
                # carb.settings does not accept None as a valid value for a setting.
                if new_value is None:
                    carb.log_warn(f"'None' is not a valid value for a setting ({name})")
                else:
                    settings.set(name, new_value)
            yield
        finally:
            for original_value, (name, new_value) in zip(original_values, items):
                if new_value is not None:
                    # An original setting value of None indicates that the setting did not exist.
                    if original_value is not None:
                        settings.set(name, original_value)
                    else:
                        settings.destroy_item(name)
