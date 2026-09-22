"""This module defines the action management system for the Collect Tool in the Omniverse Kit, encapsulating action registration, execution, and lifecycle management within a tool or application."""

import carb
import omni.kit.actions.core
import weakref
import omni.usd

from typing import Callable


ACTIONS_TAG = "Collect Tool Actions"
ACTION_COLLECT_STAGE = "collect_stage"


class Action:
    """Represents a single action provided by an extension.

    This class encapsulates an action including its registration and lifecycle management. It associates an action with a callable function that executes when the action is triggered.

    Args:
        extension_name: str
            The name of the extension providing the action.
        action_name: str
            The unique name identifying the action.
        action_display_name: str
            The name displayed in the UI for the action.
        action_description: str
            A brief description of what the action does.
        on_action_fn: Callable[[], None]
            The function to be called when the action is executed."""

    def __init__(
        self,
        extension_name: str,
        action_name: str,
        action_display_name: str,
        action_description: str,
        on_action_fn: Callable[[], None],
    ):
        self._extension_name = extension_name
        self._action_registry = omni.kit.actions.core.get_action_registry()
        self._action_name = action_name
        self._action_display_name = action_display_name
        self._action_description = action_description
        self._on_action_fn = on_action_fn
        self._action = None

        # Register actions
        self._register()

    def _register(self):
        # actions
        self._action = self._action_registry.register_action(
            self._extension_name,
            self._action_name,
            self._on_action_fn,
            display_name=self._action_display_name,
            description=self._action_description,
            tag=ACTIONS_TAG,
        )

    def destroy(self):
        self._action = None
        self._on_action_fn = None


class ActionManager:
    """A class that manages the lifecycle of actions within a tool or application.

    This class is responsible for initializing actions when the tool starts up and properly cleaning them up on shutdown. It dynamically registers actions to an extension and ensures they are unregistered when no longer needed. The class also maintains a list of all actions it manages, providing a central point for action management within the application.
    """

    def __init__(self):
        self.__all_actions = []

    def on_startup(self, collect_tool_extension):
        self._manager = omni.kit.app.get_app().get_extension_manager()
        self._extension_name = omni.ext.get_extension_name(self._manager.get_extension_id_by_module(__name__))

        weakref_collect_tool_extension = weakref.ref(collect_tool_extension)

        def on_collect():
            collect_tool = weakref_collect_tool_extension()
            if not collect_tool:
                return

            stage = omni.usd.get_context().get_stage()
            if not stage:
                carb.log_error("Cannot collect stage as no stage is opened.")
                return

            collect_tool.collect(stage.GetRootLayer().identifier)

        collect_stage_action = Action(
            extension_name=self._extension_name,
            action_name=ACTION_COLLECT_STAGE,
            action_display_name="Collect Tool->Collect Opened Stage",
            action_description="Collect opened stage.",
            on_action_fn=on_collect,
        )

        self.__all_actions.append(collect_stage_action)

    def on_shutdown(self):
        action_registry = omni.kit.actions.core.get_action_registry()
        action_registry.deregister_all_actions_for_extension(self._extension_name)

        for action in self.__all_actions:
            action.destroy()

        self.__all_actions = []
