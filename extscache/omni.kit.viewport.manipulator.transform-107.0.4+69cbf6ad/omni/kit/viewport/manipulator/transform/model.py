# Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
from __future__ import annotations

__all__ = [
    "ManipulationMode",
    "Viewport1WindowState",
    "DataAccessorRegistry",
    "DataAccessor",
    "ViewportTransformModel",
]

# import asyncio
# import math
# import traceback
from enum import Enum, Flag, IntEnum, auto

# from typing import Dict, List, Sequence, Set, Tuple, Union
# import concurrent.futures
import carb
import carb.dictionary
import carb.events
import carb.profiler
import carb.settings

# import omni.kit.app
from omni.kit.async_engine import run_coroutine
import omni.kit.undo
import omni.timeline

# from omni.kit.manipulator.tool.snap import settings_constants as snap_c
from omni.kit.manipulator.transform import AbstractTransformManipulatorModel, Operation

# from omni.kit.manipulator.transform.settings_constants import c
# from omni.kit.manipulator.transform.settings_listener import OpSettingsListener, SnapSettingsListener
# from omni.ui import scene as sc
# from pxr import Gf, Sdf, Tf, Usd, UsdGeom, UsdUtils
# from .utils import *
# from .settings_constants import Constants as prim_c


class ManipulationMode(IntEnum):
    """An enumeration.

    This enumeration defines different manipulation modes for transforming objects.
    """

    PIVOT = 0  # transform around manipulator pivot
    UNIFORM = 1  # set same world transform from manipulator to all prims equally
    INDIVIDUAL = 2  # 2: (TODO) transform around each prim's own pivot respectively


class Viewport1WindowState:
    """A class for managing the state of Viewport-1 windows.

    This class provides functionality to handle multiple Viewport-1 window instances, focusing on manipulating their states such as disabling selection rectangles, enabling picking, and retrieving picked world positions. It also manages the USD context name for the focused windows.
    """

    def __init__(self):
        """Initializes the Viewport1WindowState instance."""
        self._focused_windows = None
        focused_windows = []
        try:
            # For some reason is_focused may return False, when a Window is definitely in fact is the focused window!
            # And there's no good solution to this when multiple Viewport-1 instances are open; so we just have to
            # operate on all Viewports for a given usd_context.
            import omni.kit.viewport_legacy as vp

            vpi = vp.acquire_viewport_interface()
            for instance in vpi.get_instance_list():
                window = vpi.get_viewport_window(instance)
                if not window:
                    continue
                focused_windows.append(window)
            if focused_windows:
                self._focused_windows = focused_windows
                for window in self._focused_windows:
                    # Disable the selection_rect, but enable_picking for snapping
                    window.disable_selection_rect(True)
                    # Schedule a picking request so if snap needs it later, it may arrive by the on_change event
                    window.request_picking()
        except Exception:
            pass

    def get_picked_world_pos(self):
        """Gets the picked world position from the focused viewport window.

        Returns:
            tuple or None: The picked world position or None if not available.
        """
        if self._focused_windows:
            # Try to reduce to the focused window now after, we've had some mouse-move input
            focused_windows = [window for window in self._focused_windows if window.is_focused()]
            if focused_windows:
                self._focused_windows = focused_windows
            for window in self._focused_windows:
                window.disable_selection_rect(True)
                # request picking FOR NEXT FRAME
                window.request_picking()
                # get PREVIOUSLY picked pos, it may be None the first frame but that's fine
                return window.get_picked_world_pos()
        return None

    def __del__(self):
        self.destroy()

    def destroy(self):
        """Destroys the state by resetting focused windows."""
        self._focused_windows = None

    def get_usd_context_name(self):
        """Gets the USD context name from the focused viewport window.

        Returns:
            str: The USD context name or an empty string.
        """
        if self._focused_windows:
            return self._focused_windows[0].get_usd_context_name()
        else:
            return ""


class DataAccessorRegistry:
    """A registry for managing data accessors.

    This class provides mechanisms to retrieve and manage instances of data accessors, facilitating the access to various data operations and transformations.
    """

    def __init__(self):
        """Initializes the DataAccessorRegistry instance."""
        ...

    def getDataAccessor(self):
        """Creates and returns a new DataAccessor instance.

        Returns:
            DataAccessor: A new instance of DataAccessor.
        """
        self.dataAccessor = DataAccessor()
        return self.dataAccessor


class DataAccessor:
    """An abstract class for accessing and manipulating transformation data.

    This class provides methods to retrieve and clear transformation data, such as local-to-world and parent-to-world transforms for objects within a 3D environment. It is designed to interface with other components that require transformation data handling and manipulation.
    """

    def __init__(self):
        """Initializes the DataAccessor instance."""
        ...

    def get_local_to_world_transform(self, obj):
        """Calculates the local-to-world transform for the given object.

        Args:
            obj (object): The object to calculate the transform for.
        """
        ...

    def get_parent_to_world_transform(self, obj):
        """Calculates the parent-to-world transform for the given object.

        Args:
            obj (object): The object to calculate the transform for.
        """
        ...

    def clear_xform_cache(self):
        """Clears the transformation cache."""
        ...


class ViewportTransformModel(AbstractTransformManipulatorModel):
    """A class for managing viewport transformations in a 3D manipulation context.

    This class is responsible for handling transformations within a viewport, utilizing the USD context and viewport API provided during initialization. It extends the AbstractTransformManipulatorModel to provide specific functionalities for viewport transformations.

    Args:
        usd_context_name (str): The name of the USD context associated with the viewport.
        viewport_api: The API interface for interacting with the viewport.
    """

    def __init__(self, usd_context_name: str = "", viewport_api=None):
        """Initializes the ViewportTransformModel instance."""
        super().__init__()
