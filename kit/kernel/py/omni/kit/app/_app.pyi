from __future__ import annotations
import omni.kit.app._app
import typing
import carb._carb.logging
import omni.ext._extensions

__all__ = [
    "APP_SCRIPTING_EVENT_COMMAND",
    "APP_SCRIPTING_EVENT_STDERR",
    "APP_SCRIPTING_EVENT_STDOUT",
    "EVENT_APP_READY",
    "EVENT_APP_STARTED",
    "EVENT_ORDER_DEFAULT",
    "GLOBAL_EVENT_APP_READY",
    "GLOBAL_EVENT_APP_STARTED",
    "GLOBAL_EVENT_ERROR_LOG",
    "GLOBAL_EVENT_ERROR_LOG_IMMEDIATE",
    "GLOBAL_EVENT_POST_QUIT",
    "GLOBAL_EVENT_POST_UPDATE",
    "GLOBAL_EVENT_PRE_SHUTDOWN",
    "GLOBAL_EVENT_PRE_UPDATE",
    "GLOBAL_EVENT_SCRIPT_COMMAND",
    "GLOBAL_EVENT_SCRIPT_COMMAND_IMMEDIATE",
    "GLOBAL_EVENT_SCRIPT_STDERR",
    "GLOBAL_EVENT_SCRIPT_STDERR_IMMEDIATE",
    "GLOBAL_EVENT_SCRIPT_STDOUT",
    "GLOBAL_EVENT_SCRIPT_STDOUT_IMMEDIATE",
    "GLOBAL_EVENT_UPDATE",
    "GLOBAL_MESSAGE_BUS",
    "IApp",
    "IAppScripting",
    "POST_QUIT_EVENT_TYPE",
    "POST_UPDATE_ORDER_PYTHON_ASYNC_FUTURE",
    "POST_UPDATE_ORDER_PYTHON_EXEC",
    "PRE_SHUTDOWN_EVENT_TYPE",
    "RUN_LOOP_DEFAULT",
    "RUN_LOOP_RENDERING",
    "RUN_LOOP_SIMULATION",
    "RUN_LOOP_UI",
    "UPDATE_ORDER_FABRIC_FLUSH",
    "UPDATE_ORDER_HYDRA_RENDER",
    "UPDATE_ORDER_PYTHON_ASYNC_FUTURE_BEGIN_UPDATE",
    "UPDATE_ORDER_PYTHON_ASYNC_FUTURE_END_UPDATE",
    "UPDATE_ORDER_PYTHON_EXEC_BEGIN_UPDATE",
    "UPDATE_ORDER_PYTHON_EXEC_END_UPDATE",
    "UPDATE_ORDER_UI_RENDER",
    "UPDATE_ORDER_UNSPECIFIED",
    "UPDATE_ORDER_USD",
    "acquire_app_interface",
    "crash",
    "queue_event",
    "register_event_alias"
]


class IApp():
    def delay_app_ready(self, requester_name: str) -> None: ...
    def ensure_runloop(self, runloop_name: str = 'main') -> bool: ...
    def get_app_environment(self) -> str: 
        """
        Name of the environment we are running in. (/app/environment/name setting, e.g.: teamcity, launcher, etm, default)
        """
    def get_app_filename(self) -> str: 
        """
        App filename. Name of a kit file
        """
    def get_app_name(self) -> str: 
        """
        App name. It is app/name setting if defined, otherwise same as `filename`
        """
    def get_app_version(self) -> str: 
        """
        App version. Version in kit file or kit version
        """
    def get_app_version_short(self) -> str: 
        """
        Short app version, currently major.minor, e.g. `2021.3`
        """
    def get_build_version(self) -> str: ...
    def get_extension_manager(self) -> omni.ext._extensions.ExtensionManager: ...
    def get_kernel_version(self) -> str: 
        """
        Full kit kernel version, e.g. `103.5+release.7032.aac30830.tc.windows-x86_64.release`
        """
    def get_kit_version(self) -> str: 
        """
        Full kit version, e.g. `103.5+release.7032.aac30830.tc.windows-x86_64.release`
        """
    def get_kit_version_hash(self) -> str: 
        """
        Git hash of kit build, 8 letters, e.g. `aac30830`
        """
    def get_kit_version_short(self) -> str: 
        """
        Short kit version, currently major.minor. e.g. `103.5`
        """
    @staticmethod
    def get_log_event_stream(*args, **kwargs) -> typing.Any: 
        """
        Log event stream.
        """
    @staticmethod
    def get_message_bus_event_stream(*args, **kwargs) -> typing.Any: ...
    def get_platform_info(self) -> dict: ...
    @staticmethod
    def get_post_update_event_stream(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def get_pre_update_event_stream(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def get_python_scripting(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def get_shutdown_event_stream(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def get_startup_event_stream(*args, **kwargs) -> typing.Any: ...
    def get_time_since_start_ms(self) -> float: ...
    def get_time_since_start_s(self) -> float: ...
    @staticmethod
    def get_update_event_stream(*args, **kwargs) -> typing.Any: ...
    def get_update_number(self) -> int: ...
    def is_app_external(self) -> bool: 
        """
        Is external (public) configuration
        """
    def is_app_ready(self) -> bool: ...
    def is_debug_build(self) -> bool: ...
    def is_running(self) -> bool: ...
    def post_quit(self, return_code: int = 0) -> None: ...
    def post_uncancellable_quit(self, return_code: int = 0) -> None: ...
    def print_and_log(self, message: str) -> None: ...
    def replay_log_messages(self, arg0: carb._carb.logging.Logger) -> None: 
        """
        Replays recorded log messages for the specified target.
        """
    def report_alive(self) -> None: ...
    def restart(self, args: typing.List[str] = [], overwrite_args: bool = False, uncancellable: bool = False) -> None: ...
    def run(self, app_name: str, app_path: str, argv: typing.List[str] = []) -> int: ...
    def shutdown(self) -> int: ...
    def shutdown_and_release_framework(self) -> int: ...
    def startup(self, app_name: str, app_path: str, argv: typing.List[str] = []) -> None: ...
    def toggle_log_message_recording(self, arg0: bool) -> None: 
        """
        Toggles log message recording.
        """
    def try_cancel_shutdown(self, reason: str = '') -> bool: ...
    def update(self) -> None: ...
    pass
class IAppScripting():
    def add_search_script_folder(self, path: str) -> bool: ...
    def execute_file(self, path: str, args: typing.List[str]) -> bool: ...
    def execute_string(self, str: str, source_file: str = '', execute_as_file: bool = '') -> bool: ...
    @staticmethod
    def get_event_stream(*args, **kwargs) -> typing.Any: ...
    def remove_search_script_folder(self, path: str) -> bool: ...
    pass
def acquire_app_interface(plugin_name: str = None, library_path: str = None) -> IApp:
    pass
def crash() -> None:
    pass
def queue_event(event_name: str, payload: object = None, **kwargs) -> None:
    """
    Dispatches an immediate event and then queues it for later processing.

    An event is dispatched via `IEventDispatcher` immediately when this function is called. Any observers of the immediate
    event will be called with the parameters passed in `payload`. A deferred event is then queued and will be dispatched
    during the next runloop update (typically the next `omni.kit.app.IApp.update()` function call).

    The immediate event is dispatched by either appending ":immediate" to the given `event_name`, or will use the
    `immediate_event_name` keyword arg if provided.

    The deferred event is queued to the message queue (as found by carb.eventdispatcher.IMessageQueueFactory.get_message_queue)
    identified by the keyword arg `runloop_name`. If `runloop_name` is not provided or matches `omni.kit.app.RUN_LOOP_DEFAULT`,
    the message queue `omni.kit.app.GLOBAL_MESSAGE_BUS` is used, otherwise the message queue identifier is formatted by
    `f"runloop:{runloop_name}:messageBus"`. If the message queue has not been created, an exception is raised, but after the
    immediate event is sent.

    Args:
        event_name: (str) The name of the event to defer.
        payload: (dict, default: None) The event arguments to defer.

    Keyword Args:
        immediate_event_name: (str, default: None) The name of the immediate event to dispatch. If not provided, `":immediate"`
                is appended to `event_name` to compose the name of the immediate event.
        runloop_name: (str, default: None) The name of the runloop used to find the message queue. If the runloop does not
                exist, it will be created. If not provided, `omni.kit.app.DEFAULT_RUN_LOOP` is used. See above for more
                information.

    Returns:
        None
    """
def register_event_alias(event_type: int, event_name: str, push_event_name: object = None) -> bool:
    """
    Registers an event alias.

    This function aids conversion from Events 1.0 to 2.0 by creating an alias to an Events 1.0 `EventType` to Events 2.0 names.

    Arguments:
        event_type: (int) The numeric identifier for a carb.events EventType, such as by carb.events.type_from_string().
        event_name: (str) The string name for dispatching the deferred event via IEventDispatcher.
        push_event_name: (str, default: None) An optional string name for dispatching an immediate event. If None (the default)
                this name is determined by adding `:immediate` to the given `event_name`.

    Returns:
        True if the aliases were created; False if an error occurs or if the aliases were already registered.
    """
APP_SCRIPTING_EVENT_COMMAND = 0
APP_SCRIPTING_EVENT_STDERR = 2
APP_SCRIPTING_EVENT_STDOUT = 1
EVENT_APP_READY = 6559629015549994352
EVENT_APP_STARTED = 4314192531916293802
EVENT_ORDER_DEFAULT = 0
GLOBAL_EVENT_APP_READY = 'omni.kit.app:ready'
GLOBAL_EVENT_APP_STARTED = 'omni.kit.app:started'
GLOBAL_EVENT_ERROR_LOG = 'omni.kit.app:error_log'
GLOBAL_EVENT_ERROR_LOG_IMMEDIATE = 'omni.kit.app:error_log:immediate'
GLOBAL_EVENT_POST_QUIT = 'omni.kit.app:post_quit'
GLOBAL_EVENT_POST_UPDATE = 'postUpdate'
GLOBAL_EVENT_PRE_SHUTDOWN = 'omni.kit.app:pre_shutdown'
GLOBAL_EVENT_PRE_UPDATE = 'preUpdate'
GLOBAL_EVENT_SCRIPT_COMMAND = 'omni.kit.app:script_command'
GLOBAL_EVENT_SCRIPT_COMMAND_IMMEDIATE = 'omni.kit.app:script_command:immediate'
GLOBAL_EVENT_SCRIPT_STDERR = 'omni.kit.app:script_stderr'
GLOBAL_EVENT_SCRIPT_STDERR_IMMEDIATE = 'omni.kit.app:script_stderr:immediate'
GLOBAL_EVENT_SCRIPT_STDOUT = 'omni.kit.app:script_stdout'
GLOBAL_EVENT_SCRIPT_STDOUT_IMMEDIATE = 'omni.kit.app:script_stdout:immediate'
GLOBAL_EVENT_UPDATE = 'update'
GLOBAL_MESSAGE_BUS = 'messageBus'
POST_QUIT_EVENT_TYPE = 0
POST_UPDATE_ORDER_PYTHON_ASYNC_FUTURE = -25
POST_UPDATE_ORDER_PYTHON_EXEC = -10
PRE_SHUTDOWN_EVENT_TYPE = 1
RUN_LOOP_DEFAULT = 'main'
RUN_LOOP_RENDERING = 'rendering'
RUN_LOOP_SIMULATION = 'simulation'
RUN_LOOP_UI = 'ui'
UPDATE_ORDER_FABRIC_FLUSH = 20
UPDATE_ORDER_HYDRA_RENDER = 30
UPDATE_ORDER_PYTHON_ASYNC_FUTURE_BEGIN_UPDATE = -50
UPDATE_ORDER_PYTHON_ASYNC_FUTURE_END_UPDATE = 50
UPDATE_ORDER_PYTHON_EXEC_BEGIN_UPDATE = -45
UPDATE_ORDER_PYTHON_EXEC_END_UPDATE = 100
UPDATE_ORDER_UI_RENDER = 15
UPDATE_ORDER_UNSPECIFIED = 0
UPDATE_ORDER_USD = -10
