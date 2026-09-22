# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = ["StageIcons"]


from .singleton import Singleton
from pathlib import Path
from typing import Union, Optional
import carb.tokens


@Singleton
class StageIcons:
    """A singleton that scans the icon folder and returns the icon depending on the type."""

    class _Event(list):
        """
        A list of callable objects. Calling an instance of this will cause a
        call to each item in the list in ascending order by index.
        """

        def __call__(self, *args, **kwargs):
            """Called when the instance is “called” as a function"""
            # Call all the saved functions
            for f in self:
                f(*args, **kwargs)

        def __repr__(self):
            """
            Called by the repr() built-in function to compute the “official”
            string representation of an object.
            """
            return f"Event({list.__repr__(self)})"

    class _EventSubscription:
        """
        Event subscription.

        _Event has callback while this object exists.
        """

        def __init__(self, event, fn):
            """
            Saves the function, the event, and adds the function to the event.
            """
            self._fn = fn
            self._event = event
            event.append(self._fn)

        def __del__(self):
            """Called by GC."""
            self._event.remove(self._fn)

    def __init__(self):
        """Instantiates the StageIcon instance."""
        self._on_icons_changed = self._Event()

        # Read all the svg files in the directory
        icon_folder_path = Path(carb.tokens.get_tokens_interface().resolve("${omni.kit.widget.stage}/icons"))
        self._icons = {icon.stem: str(icon) for icon in icon_folder_path.glob("*.svg")}

    def set(self, prim_type: str, icon_path: Optional[Union[str, Path]]):
        """
        Sets the new icon path for a specific prim type.
        When icon_path is None, removes the prim type from this icon registry.

        Args:
            prim_type (Optional[str]): The prim type to be updated.
            icon_path (Optional[Union[str, Path]]): The new icon path. When set to None, removes the prim type from this
                icon registry.
        """
        if icon_path is None:
            # Remove the icon
            if prim_type in self._icons:
                del self._icons[prim_type]
        else:
            self._icons[prim_type] = str(icon_path)

        self._on_icons_changed()

    def get(self, prim_type: str, default: Optional[Union[str, Path]] = None) -> str:
        """
        Checks the icon cache and returns the icon if exists.

        Args:
            prim_type (str): The prim type to query.

        Keyword Args:
            default (Optional[Union[str, Path]]): A default value if the prim type is not found.

        Returns:
            str: The icon path for the given prim type. If not found, returns an empty string.
        """
        found = self._icons.get(prim_type)
        if not found and default:
            found = self._icons.get(default)

        if found:
            return found

        return ""

    def subscribe_icons_changed(self, fn):
        """
        Subscribes a handler fn to icon changed event.
        Returns the subscription object that will automatically unsubscribe when destroyed.

        Args:
            fn: The event handler for icons changed.

        Returns:
            StageIcons._EventSubscription: The subscription object.
        """
        return self._EventSubscription(self._on_icons_changed, fn)
