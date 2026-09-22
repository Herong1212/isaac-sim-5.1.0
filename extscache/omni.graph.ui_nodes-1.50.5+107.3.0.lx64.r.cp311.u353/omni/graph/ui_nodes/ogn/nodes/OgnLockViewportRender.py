# Copyright (c) 2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

from enum import Enum, auto

from omni.graph.core import ExecutionAttributeState
from omni.graph.ui_nodes.ogn.OgnLockViewportRenderDatabase import OgnLockViewportRenderDatabase
from omni.kit.viewport.utility import get_active_viewport_window


class LockState(Enum):
    """Enum for lock state"""

    UNLOCKED = auto()
    """The target has been unlocked."""
    LOCKED = auto()
    """The target has been locked."""
    UNLOCKING = auto()
    """The target is being unlocked."""


class OgnLockViewportRenderInternalState:
    """Convenience class for maintaining per-node state information"""

    def __init__(self):
        self._lock_state = LockState.UNLOCKED
        self._viewport_name = ""
        self._viewport_api = None
        self._viewport_widget = None
        self._previous_freeze_frame = None
        self._previous_display_delegate = None
        self._elapsed_time = 0.0
        self._fading_time = 1.0

    @property
    def lock_state(self) -> LockState:
        return self._lock_state

    @lock_state.setter
    def lock_state(self, state: LockState):
        self._lock_state = state

    @property
    def viewport_name(self):
        return self._viewport_name

    @viewport_name.setter
    def viewport_name(self, name):
        self._viewport_name = name

    @property
    def viewport_api(self):
        return self._viewport_api

    @viewport_api.setter
    def viewport_api(self, api):
        assert api is not None
        self._viewport_api = api

    @property
    def viewport_widget(self):
        return self._viewport_widget

    @viewport_widget.setter
    def viewport_widget(self, widget):
        assert widget is not None
        self._viewport_widget = widget

    @property
    def previous_freeze_frame(self):
        return self._previous_freeze_frame

    @previous_freeze_frame.setter
    def previous_freeze_frame(self, freeze_frame):
        assert isinstance(freeze_frame, bool)
        self._previous_freeze_frame = freeze_frame

    @property
    def previous_display_delegate(self):
        return self._previous_display_delegate

    @previous_display_delegate.setter
    def previous_display_delegate(self, display_delegate):
        assert display_delegate is not None
        self._previous_display_delegate = display_delegate

    @property
    def elapsed_time(self) -> float:
        return self._elapsed_time

    @elapsed_time.setter
    def elapsed_time(self, time: float):
        self._elapsed_time = time

    @property
    def fading_time(self) -> float:
        return self._fading_time

    @fading_time.setter
    def fading_time(self, time: float):
        self._fading_time = time

    def restore_freeze_frame(self):
        if self._viewport_api is not None:
            assert isinstance(self._previous_freeze_frame, bool)
            self._viewport_api.freeze_frame = self._previous_freeze_frame

            self._viewport_api = None
            self._previous_freeze_frame = None

    def restore_display_delegate(self):
        if self._viewport_widget is not None:
            self._viewport_widget.display_delegate = self._previous_display_delegate

            self._viewport_widget = None
            self._previous_display_delegate = None


class OgnLockViewportRender:
    """
    Locks and unlocks viewport render.
    """

    @staticmethod
    def internal_state():
        """Return an object that will contain per-node state information"""
        return OgnLockViewportRenderInternalState()

    @staticmethod
    def unlock_immediately_if_locked(internal_state):
        """Unlock viewport render immediately if locked"""
        assert isinstance(internal_state, OgnLockViewportRenderInternalState)

        if internal_state.lock_state != LockState.UNLOCKED:
            internal_state.restore_display_delegate()
            internal_state.restore_freeze_frame()
            internal_state.lock_state = LockState.UNLOCKED

    @staticmethod
    def release(node):
        """When a node is removed it will get a release call for cleanup"""
        internal_state = OgnLockViewportRenderDatabase.per_instance_internal_state(node)
        if internal_state is not None:
            OgnLockViewportRender.unlock_immediately_if_locked(internal_state)

    @staticmethod
    def compute(db) -> bool:
        """Compute the outputs from the current inputs"""
        try:
            # An extension is generally not allowed to force a specific viewport backend like omni.kit.widget.viewport
            # to be loaded; instead it is the application that controls which viewport to be loaded. If the following
            # import fails at runtime, it is because omni.kit.widget.viewport is not loaded by the application, then
            # the node won't be supported to lock and unlock viewport render.
            from omni.kit.widget.viewport.display_delegate import OverlayViewportDisplayDelegate

            locked_exec_attr_state = ExecutionAttributeState.DISABLED
            fade_started_exec_attr_state = ExecutionAttributeState.DISABLED
            fade_complete_exec_attr_state = ExecutionAttributeState.DISABLED

            internal_state = db.per_instance_state

            # If target viewport is changed, make sure viewport render is unlocked for the previous viewport
            viewport_name = db.inputs.viewport
            if internal_state.viewport_name != viewport_name:
                OgnLockViewportRender.unlock_immediately_if_locked(internal_state)
                internal_state.viewport_name = viewport_name

            if db.inputs.lock == ExecutionAttributeState.ENABLED:

                if internal_state.lock_state == LockState.UNLOCKED:

                    # sanity check
                    assert (
                        internal_state.viewport_api is None
                        and internal_state.viewport_widget is None
                        and internal_state.previous_freeze_frame is None
                        and internal_state.previous_display_delegate is None
                    ), "Invalid internal state"

                    viewport_window = get_active_viewport_window(viewport_name)
                    assert viewport_window, f"Unknown viewport window {viewport_name}"
                    viewport_api = viewport_window.viewport_api
                    viewport_widget = viewport_window.viewport_widget

                    # We need to restore the display delegate to the previous one when unlocking viewport render
                    internal_state.viewport_api = viewport_api
                    internal_state.viewport_widget = viewport_widget
                    internal_state.previous_freeze_frame = viewport_api.freeze_frame
                    internal_state.previous_display_delegate = viewport_widget.display_delegate

                    # Signal other viewport elements that the viewport is locked so certain things won't update
                    viewport_api.freeze_frame = True

                    # Set to a new display delegate that overlays the locked frame on top of the renderer output
                    viewport_widget.display_delegate = OverlayViewportDisplayDelegate(viewport_api)

                    locked_exec_attr_state = ExecutionAttributeState.ENABLED

                    internal_state.lock_state = LockState.LOCKED

            else:

                if internal_state.lock_state == LockState.LOCKED:

                    # Start updating relevant parts of the viewport now that the transition has begun
                    internal_state.restore_freeze_frame()

                    internal_state.elapsed_time = 0.0
                    internal_state.fading_time = max(db.inputs.fadeTime, 0.0)

                    # Push this node in a latent state. Note the output connection of the `fadeStarted` attribute
                    # can't be activated at the same tick because only 1 activated output is permitted per compute,
                    # therefore it has to be activated until the next tick.
                    fade_complete_exec_attr_state = ExecutionAttributeState.LATENT_PUSH

                    internal_state.lock_state = LockState.UNLOCKING

                elif internal_state.lock_state == LockState.UNLOCKING:

                    elapsed_time = internal_state.elapsed_time
                    fading_time = internal_state.fading_time
                    assert elapsed_time >= 0.0 and fading_time >= 0.0

                    if elapsed_time == 0.0:
                        fade_started_exec_attr_state = ExecutionAttributeState.ENABLED

                    elif elapsed_time < fading_time:
                        display_delegate = internal_state.viewport_widget.display_delegate
                        assert isinstance(display_delegate, OverlayViewportDisplayDelegate)
                        display_delegate.set_overlay_alpha(1.0 - elapsed_time / fading_time)

                    elif elapsed_time >= fading_time:

                        # Reset the display delegate to the previous one that was used before locking viewport render
                        internal_state.restore_display_delegate()

                        # Output attribute connection is activated and the latent state is finished for this node
                        fade_complete_exec_attr_state = ExecutionAttributeState.LATENT_FINISH

                        internal_state.lock_state = LockState.UNLOCKED

                    internal_state.elapsed_time += db.abi_context.get_elapsed_time()

            db.outputs.locked = locked_exec_attr_state
            db.outputs.fadeStarted = fade_started_exec_attr_state
            db.outputs.fadeComplete = fade_complete_exec_attr_state

        except Exception as error:  # noqa: PLW0703
            db.log_error(str(error))
            return False

        return True
