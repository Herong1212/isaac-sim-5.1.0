from __future__ import annotations
import omni.ext._extensions
import typing
import carb.dictionary._dictionary

__all__ = [
    "DownloadState",
    "EVENT_EXTENSION_PULL_BEGIN",
    "EVENT_EXTENSION_PULL_END_FAILURE",
    "EVENT_EXTENSION_PULL_END_SUCCESS",
    "EVENT_REGISTRY_REFRESH_BEGIN",
    "EVENT_REGISTRY_REFRESH_END_FAILURE",
    "EVENT_REGISTRY_REFRESH_END_SUCCESS",
    "EXTENSION_EVENT_FOLDER_CHANGED",
    "EXTENSION_EVENT_SCRIPT_CHANGED",
    "EXTENSION_SUMMARY_FLAG_ANY_ENABLED",
    "EXTENSION_SUMMARY_FLAG_BUILTIN",
    "EXTENSION_SUMMARY_FLAG_INSTALLED",
    "EXTENSION_SUMMARY_FLAG_NONE",
    "ExtensionManager",
    "ExtensionPathType",
    "ExtensionStateChangeType",
    "GLOBAL_EVENT_EXTENSION_PULL_BEGIN",
    "GLOBAL_EVENT_EXTENSION_PULL_BEGIN_DEFERRED",
    "GLOBAL_EVENT_EXTENSION_PULL_END",
    "GLOBAL_EVENT_EXTENSION_PULL_END_FAILURE",
    "GLOBAL_EVENT_EXTENSION_PULL_END_FAILURE_IMMEDIATE",
    "GLOBAL_EVENT_EXTENSION_PULL_END_SUCCESS",
    "GLOBAL_EVENT_EXTENSION_PULL_END_SUCCESS_IMMEDIATE",
    "GLOBAL_EVENT_FOLDER_CHANGED",
    "GLOBAL_EVENT_FOLDER_CHANGED_IMMEDIATE",
    "GLOBAL_EVENT_REGISTRY_REFRESH_BEGIN",
    "GLOBAL_EVENT_REGISTRY_REFRESH_BEGIN_DEFERRED",
    "GLOBAL_EVENT_REGISTRY_REFRESH_END",
    "GLOBAL_EVENT_REGISTRY_REFRESH_END_FAILURE",
    "GLOBAL_EVENT_REGISTRY_REFRESH_END_FAILURE_IMMEDIATE",
    "GLOBAL_EVENT_REGISTRY_REFRESH_END_SUCCESS",
    "GLOBAL_EVENT_REGISTRY_REFRESH_END_SUCCESS_IMMEDIATE",
    "GLOBAL_EVENT_SCRIPT_CHANGED",
    "GLOBAL_EVENT_SCRIPT_CHANGED_IMMEDIATE",
    "ICppExt",
    "IExt",
    "IExtensionManagerHooks",
    "IExtensions",
    "IHookHolder",
    "IRegistryProvider",
    "acquire_ext_interface",
    "acquire_extensions_interface",
    "release_ext_interface"
]


class DownloadState():
    """
            Index/Extension Download States.
            

    Members:

      DOWNLOADING

      DOWNLOAD_SUCCESS

      DOWNLOAD_FAILURE
    """
    def __eq__(self, other: object) -> bool: ...
    def __getstate__(self) -> int: ...
    def __hash__(self) -> int: ...
    def __index__(self) -> int: ...
    def __init__(self, value: int) -> None: ...
    def __int__(self) -> int: ...
    def __ne__(self, other: object) -> bool: ...
    def __repr__(self) -> str: ...
    def __setstate__(self, state: int) -> None: ...
    @property
    def name(self) -> str:
        """
        :type: str
        """
    @property
    def value(self) -> int:
        """
        :type: int
        """
    DOWNLOADING: omni.ext._extensions.DownloadState # value = <DownloadState.DOWNLOADING: 0>
    DOWNLOAD_FAILURE: omni.ext._extensions.DownloadState # value = <DownloadState.DOWNLOAD_FAILURE: 2>
    DOWNLOAD_SUCCESS: omni.ext._extensions.DownloadState # value = <DownloadState.DOWNLOAD_SUCCESS: 1>
    __members__: dict # value = {'DOWNLOADING': <DownloadState.DOWNLOADING: 0>, 'DOWNLOAD_SUCCESS': <DownloadState.DOWNLOAD_SUCCESS: 1>, 'DOWNLOAD_FAILURE': <DownloadState.DOWNLOAD_FAILURE: 2>}
    pass
class ExtensionManager():
    def add_path(self, path: str, type: ExtensionPathType = ExtensionPathType.COLLECTION) -> None: ...
    def add_path_protocol_provider(self, scheme: str, on_add_path_fn: typing.Callable[[str], str], on_remove_path_fn: typing.Callable[[str], None]) -> bool: 
        """
        Add new path protocol provider, scheme must be unique `false` returned otherwise.

        Args:
            scheme(str): Scheme name.
            fn(Callable[[str], str]): The callback to be called when new search path is added for this scheme.
        """
    @staticmethod
    def add_registry_provider(*args, **kwargs) -> typing.Any: 
        """
        Add registry provider to be used for remote extension registry.

        Args:
            name (str): Provider unique name.
            provider (IRegistryProvider): Provider.
        """
    def fetch_all_extension_packages(self) -> tuple: ...
    def fetch_extension_packages(self, arg0: str) -> tuple: ...
    def fetch_extension_summaries(self) -> tuple: ...
    def fetch_extension_versions(self, arg0: str) -> tuple: ...
    @staticmethod
    def get_change_event_stream(*args, **kwargs) -> typing.Any: ...
    def get_enabled_extension_id(self, ext_name: str) -> str: ...
    def get_extension_dict(self, ext_id: str) -> carb.dictionary._dictionary.Item: ...
    def get_extension_packages(self) -> tuple: ...
    def get_extension_path(self, ext_id: str) -> str: ...
    def get_extensions(self) -> tuple: ...
    def get_folders(self) -> tuple: 
        """
        Get folders monitored for python extensions.

        Returns (List[Dict]):
            List of folders. Each folder is dict with "path" and "builtin" key.
        """
    @staticmethod
    def get_hooks(*args, **kwargs) -> typing.Any: ...
    def get_registry_extension_dict(self, ext_id: str) -> carb.dictionary._dictionary.Item: ...
    def get_registry_extension_packages(self) -> tuple: ...
    def get_registry_extensions(self) -> tuple: ...
    def get_registry_providers(self) -> tuple: ...
    def is_extension_enabled(self, ext_name: str) -> bool: ...
    def process_and_apply_all_changes(self) -> None: ...
    def publish_extension(self, ext_id: str, provider_name: str = '', allow_overwrite: bool = False) -> bool: ...
    def pull_extension(self, ext_id: str) -> bool: ...
    def pull_extension_async(self, ext_id: str) -> None: ...
    def refresh_registry(self) -> None: ...
    def remove_path(self, path: str) -> None: ...
    def remove_path_protocol_provider(self, scheme: str) -> None: ...
    def remove_registry_provider(self, name: str) -> None: 
        """
        Remove registry provider.

        Args:
            name (str): Provider unique name.
        """
    def set_extension_enabled(self, extension_id: str, enabled: bool) -> None: 
        """
        Toggle extension enable/disable.

        Args:
            extension_id (str): Extension id. Full python module name, returned by `get_extensions`.
            enabled(bool): Enable/disable toggle.
        """
    def set_extension_enabled_immediate(self, extension_id: str, enabled: bool) -> bool: 
        """
        Toggle extension enable/disable immediately.

        Args:
            extension_id (str): Extension id. Full python module name, returned by `get_extensions`.
            enabled(bool): Enable/disable toggle.
        Returns (bool):
            Failure or success.
        """
    def set_extensions_excluded(self, exts: typing.List[str]) -> None: 
        """
        Set extensions to exclude on following solver/startup routines. They persist until next call to this function.

        Args:
            extensions (List[str]): List Extension id with or without versions.
        """
    def solve_extensions(self, exts: typing.List[str], add_enabled: bool = False, return_only_disabled: bool = False) -> tuple: 
        """
        Run extension dependencies solver on the input.

        Input is a list of extension, they can be names, full id, partial versions like `ommi.foo-2`.

        Args:
            exts(List[str]): List of extensions.
            add_enabled(bool): Automatically add already enabled extension to the input (to take into account)
            return_only_disabled(bool): If true exclude from the result extensions that are currently already enabled
        Returns(Tuple[bool, List[str], str]):
            Tuple of result, list of extensions (solution) and error message.
        """
    @staticmethod
    def subscribe_to_extension_enable(*args, **kwargs) -> typing.Any: 
        """
        Call callback if extension is enabled and hook in extension system to wait for extension to be enabled again (after reload for instance) and disabled.

        Example:

        .. code-block::

            def on_ext_enabled(ext_id: str):
                print("enabled:" + ext_id)

            def on_ext_disabled(ext_id: str):
                print("disabled:" + ext_id)

            manager = omni.kit.app.get_app().get_extension_manager()
            self.hooks = manager.subscribe_to_extension_enable(on_ext_enabled, on_ext_disabled, ext_name="omni.kit.window.console", hook_name="la la la")
            # Notice that we stored subscription holder somewhere (in self for instance) to hold it.

        Args:
            on_enable_fn(Callable[[str]]): The callback to be called when extension is enabled. It accepts extension id.
            on_disable_fn(Callable[[str]], optional): The callback to be called when extension is disabled. It accepts extension id.
            ext_name(str, optional): Extension name to look for. Hook is only called for extensions with matching name. Can be empty.
            hook_name(str): Hook name for debugging and logging.

        Returns:
            Pair of hook holders.
        """
    def sync_registry(self) -> bool: ...
    def uninstall_extension(self, ext_id: str) -> bool: ...
    def unpublish_extension(self, ext_id: str, provider_name: str = '') -> bool: ...
    pass
class ExtensionPathType():
    """
            Index Refresh States.
            

    Members:

      COLLECTION

      COLLECTION_USER

      COLLECTION_CACHE

      DIRECT_PATH

      EXT_1_FOLDER
    """
    def __eq__(self, other: object) -> bool: ...
    def __getstate__(self) -> int: ...
    def __hash__(self) -> int: ...
    def __index__(self) -> int: ...
    def __init__(self, value: int) -> None: ...
    def __int__(self) -> int: ...
    def __ne__(self, other: object) -> bool: ...
    def __repr__(self) -> str: ...
    def __setstate__(self, state: int) -> None: ...
    @property
    def name(self) -> str:
        """
        :type: str
        """
    @property
    def value(self) -> int:
        """
        :type: int
        """
    COLLECTION: omni.ext._extensions.ExtensionPathType # value = <ExtensionPathType.COLLECTION: 0>
    COLLECTION_CACHE: omni.ext._extensions.ExtensionPathType # value = <ExtensionPathType.COLLECTION_CACHE: 4>
    COLLECTION_USER: omni.ext._extensions.ExtensionPathType # value = <ExtensionPathType.COLLECTION_USER: 3>
    DIRECT_PATH: omni.ext._extensions.ExtensionPathType # value = <ExtensionPathType.DIRECT_PATH: 1>
    EXT_1_FOLDER: omni.ext._extensions.ExtensionPathType # value = <ExtensionPathType.EXT_1_FOLDER: 2>
    __members__: dict # value = {'COLLECTION': <ExtensionPathType.COLLECTION: 0>, 'COLLECTION_USER': <ExtensionPathType.COLLECTION_USER: 3>, 'COLLECTION_CACHE': <ExtensionPathType.COLLECTION_CACHE: 4>, 'DIRECT_PATH': <ExtensionPathType.DIRECT_PATH: 1>, 'EXT_1_FOLDER': <ExtensionPathType.EXT_1_FOLDER: 2>}
    pass
class ExtensionStateChangeType():
    """
    Members:

      BEFORE_EXTENSION_ENABLE

      AFTER_EXTENSION_ENABLE

      BEFORE_EXTENSION_DISABLE

      AFTER_EXTENSION_DISABLE

      COUNT
    """
    def __eq__(self, other: object) -> bool: ...
    def __getstate__(self) -> int: ...
    def __hash__(self) -> int: ...
    def __index__(self) -> int: ...
    def __init__(self, value: int) -> None: ...
    def __int__(self) -> int: ...
    def __ne__(self, other: object) -> bool: ...
    def __repr__(self) -> str: ...
    def __setstate__(self, state: int) -> None: ...
    @property
    def name(self) -> str:
        """
        :type: str
        """
    @property
    def value(self) -> int:
        """
        :type: int
        """
    AFTER_EXTENSION_DISABLE: omni.ext._extensions.ExtensionStateChangeType # value = <ExtensionStateChangeType.AFTER_EXTENSION_DISABLE: 3>
    AFTER_EXTENSION_ENABLE: omni.ext._extensions.ExtensionStateChangeType # value = <ExtensionStateChangeType.AFTER_EXTENSION_ENABLE: 1>
    BEFORE_EXTENSION_DISABLE: omni.ext._extensions.ExtensionStateChangeType # value = <ExtensionStateChangeType.BEFORE_EXTENSION_DISABLE: 2>
    BEFORE_EXTENSION_ENABLE: omni.ext._extensions.ExtensionStateChangeType # value = <ExtensionStateChangeType.BEFORE_EXTENSION_ENABLE: 0>
    COUNT: omni.ext._extensions.ExtensionStateChangeType # value = <ExtensionStateChangeType.COUNT: 4>
    __members__: dict # value = {'BEFORE_EXTENSION_ENABLE': <ExtensionStateChangeType.BEFORE_EXTENSION_ENABLE: 0>, 'AFTER_EXTENSION_ENABLE': <ExtensionStateChangeType.AFTER_EXTENSION_ENABLE: 1>, 'BEFORE_EXTENSION_DISABLE': <ExtensionStateChangeType.BEFORE_EXTENSION_DISABLE: 2>, 'AFTER_EXTENSION_DISABLE': <ExtensionStateChangeType.AFTER_EXTENSION_DISABLE: 3>, 'COUNT': <ExtensionStateChangeType.COUNT: 4>}
    pass
class IExt(ICppExt):
    def __init__(self) -> None: ...
    pass
class ICppExt():
    def shutdown(self) -> None: ...
    def startup(self, arg0: str) -> None: ...
    pass
class IExtensionManagerHooks():
    def create_extension_state_change_hook(self, fn: typing.Callable[[str, ExtensionStateChangeType], None], type: ExtensionStateChangeType, ext_name: str = '', ext_dict_path: str = '', order: int = 0, hook_name: str = '') -> IHookHolder: 
        """
        Create extension state change hook.

        Hook is valid while returned hook holder object is alive.

        Args:
            fn(Callable[[str, ExtensionStateChangeType]]): The callback to be called on extension state change event. It accepts extension id and type of hook event.
            type(ExtensionStateChangeType): Extension state change moment to hook into.
            ext_name(str, optional): Extension name to look for. Hook is only called for extensions with matching name. Can be empty.
            ext_dict_path(str, optional): Extension dictionary path to look for. Hook is only called if it is present.
            order(int, optional): Hook call order (if there are multiple).
            hook_name(str): Hook name for debugging and logging.

        Returns:
            The hook holder.
        """
    pass
class IExtensions():
    @staticmethod
    def create_extension_manager(*args, **kwargs) -> typing.Any: ...
    pass
class IHookHolder():
    """
    Hook holder.
    """
    pass
class IRegistryProvider():
    def __init__(self) -> None: ...
    pass
def acquire_ext_interface(plugin_name: str = None, library_path: str = None) -> ICppExt:
    pass
def acquire_extensions_interface(plugin_name: str = None, library_path: str = None) -> IExtensions:
    pass
def release_ext_interface(arg0: ICppExt) -> None:
    pass
EVENT_EXTENSION_PULL_BEGIN = 109964613158269658
EVENT_EXTENSION_PULL_END_FAILURE = 9223291169657293387
EVENT_EXTENSION_PULL_END_SUCCESS = 14987627931003739926
EVENT_REGISTRY_REFRESH_BEGIN = 3495945649151246744
EVENT_REGISTRY_REFRESH_END_FAILURE = 14616543551050129989
EVENT_REGISTRY_REFRESH_END_SUCCESS = 3684627524544370228
EXTENSION_EVENT_FOLDER_CHANGED = 16256091767625351810
EXTENSION_EVENT_SCRIPT_CHANGED = 5696860606285888797
EXTENSION_SUMMARY_FLAG_ANY_ENABLED = 2
EXTENSION_SUMMARY_FLAG_BUILTIN = 4
EXTENSION_SUMMARY_FLAG_INSTALLED = 8
EXTENSION_SUMMARY_FLAG_NONE = 0
GLOBAL_EVENT_EXTENSION_PULL_BEGIN = 'omni.ext:extension_pull_begin'
GLOBAL_EVENT_EXTENSION_PULL_BEGIN_DEFERRED = 'omni.ext:extension_pull_begin:deferred'
GLOBAL_EVENT_EXTENSION_PULL_END = 'omni.ext:extension_pull_end'
GLOBAL_EVENT_EXTENSION_PULL_END_FAILURE = 'omni.ext:extension_pull_end:failure'
GLOBAL_EVENT_EXTENSION_PULL_END_FAILURE_IMMEDIATE = 'omni.ext:extension_pull_end:failure:immediate'
GLOBAL_EVENT_EXTENSION_PULL_END_SUCCESS = 'omni.ext:extension_pull_end:success'
GLOBAL_EVENT_EXTENSION_PULL_END_SUCCESS_IMMEDIATE = 'omni.ext:extension_pull_end:success:immediate'
GLOBAL_EVENT_FOLDER_CHANGED = 'omni.ext:folder_changed'
GLOBAL_EVENT_FOLDER_CHANGED_IMMEDIATE = 'omni.ext:folder_changed:immediate'
GLOBAL_EVENT_REGISTRY_REFRESH_BEGIN = 'omni.ext:registry_refresh_begin'
GLOBAL_EVENT_REGISTRY_REFRESH_BEGIN_DEFERRED = 'omni.ext:registry_refresh_begin:deferred'
GLOBAL_EVENT_REGISTRY_REFRESH_END = 'omni.ext:registry_refresh_end'
GLOBAL_EVENT_REGISTRY_REFRESH_END_FAILURE = 'omni.ext:registry_refresh_end:failure'
GLOBAL_EVENT_REGISTRY_REFRESH_END_FAILURE_IMMEDIATE = 'omni.ext:registry_refresh_end:failure:immediate'
GLOBAL_EVENT_REGISTRY_REFRESH_END_SUCCESS = 'omni.ext:registry_refresh_end:success'
GLOBAL_EVENT_REGISTRY_REFRESH_END_SUCCESS_IMMEDIATE = 'omni.ext:registry_refresh_end:success:immediate'
GLOBAL_EVENT_SCRIPT_CHANGED = 'omni.ext:script_changed'
GLOBAL_EVENT_SCRIPT_CHANGED_IMMEDIATE = 'omni.ext:script_changed:immediate'
