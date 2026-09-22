"""Extension implementation required by Carbonite extension loader"""

import concurrent.futures
import json
import os
import time
from collections import defaultdict
from contextlib import suppress
from enum import Enum
from pathlib import Path
from typing import List, Set, Tuple, Union

import carb
import carb.profiler
import omni.ext
import omni.graph.core as og
import omni.graph.tools._internal as ogi
from carb.eventdispatcher import get_eventdispatcher
from omni.kit.app import get_app_interface
from omni.kit.commands import unregister_module_commands
from pxr import Sdf

from .file_format_1_6 import migrate_compound_node_schema_data
from .file_format_1_7 import migrate_bundle_io_asymmetry
from .file_format_1_8 import migrate_bundle_separator
from .update_file_format import cb_update_to_include_schema, migrate_attribute_custom_data


# ==============================================================================================================
def register_categories():
    """If the Kit location is available then use it to find category configuration files and register their contents"""
    _ = ogi.LOG.disabled or ogi.LOG.info("Registering categories")
    try:  # noqa: PLR1702
        config_dir = Path(carb.tokens.get_tokens_interface().resolve("${kit}")) / "dev" / "ogn" / "config"
        if not config_dir.is_dir():
            carb.log_error(f"Configuration path was not a directory - {config_dir}")
            return
        node_categories = og.get_node_categories_interface()

        for config_file in config_dir.iterdir():
            with suppress(json.decoder.JSONDecodeError):
                with open(config_file, "r", encoding="utf-8") as json_fd:
                    configuration = json.load(json_fd)
                if "categoryDefinitions" not in configuration:
                    continue
                _ = ogi.LOG.disabled or ogi.LOG.info(
                    "Category definitions in %s - %d", config_file, len(configuration["categoryDefinitions"])
                )
                for category_name, category_description in configuration["categoryDefinitions"].items():
                    if category_name[0] == "$":
                        continue
                    node_categories.define_category(category_name, category_description)
    except (AttributeError, TypeError) as error:
        carb.log_error(f"Could not initialize the OmniGraph configuration list - {error}")


# ==============================================================================================================
@carb.profiler.profile
def complete_node_registrations(pending_registrations: dict[str, concurrent.futures.Future]):
    """
    Wait until all the pending registration tasks are complete.

    Args:
        pending_registrations: The futures corresponding to the node registration tasks that are not yet complete.
    """
    if not pending_registrations:
        return

    # copy the pending registration list, as it will mutate while the tasks complete
    tasks = list(pending_registrations.values())
    concurrent.futures.wait(tasks)


# ==============================================================================================================
class _PublicExtension(omni.ext.IExt):
    """Mandatory extension instantiation required by the Carbonite extension handler"""

    class NodeRegistrationMode(Enum):
        """Specifies the node registration strategy for the python nodes and modules in the extension."""

        Deferred = 1
        """The nodes registration is deferred to a background thread and performed asynchronously."""
        Synchronous = 2
        """The node registration is synchronized on the main thread."""

    # Globally accessible timing information tracking how long it takes to register and deregister nodes in an extension
    REGISTRATION_TIMING = {}
    DEREGISTRATION_TIMING = {}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__extension_pre_disabled_hook = None
        self.__extension_post_enabled_hook = None
        self.__interface = None
        self.__upgrade_format_cb = None
        self.__module_registrations: dict[str, list[og.PythonNodeRegistration]] = defaultdict(list)
        self.__pre_del_prim_cb = None
        self.__pre_del_prim_cb = None
        self.__executor = concurrent.futures.ThreadPoolExecutor()
        self.__pending_registrations: dict[str, concurrent.futures.Future] = defaultdict()
        self.__app_ready_sub = None
        self.__registry_subscription = None
        # Set the environment variable OGN_REG_DEBUG to 1 if you wish to debug the registration process (very verbose)
        log_destination = "stdout" if os.getenv("OGN_REG_DEBUG") else None
        ogi.set_registration_logging(log_destination)

    # --------------------------------------------------------------------------------------------------------------
    @carb.profiler.profile
    def get_node_registration_mode(self, ext_id) -> NodeRegistrationMode:
        """
        In application startup, it queries the extension configuration for the node registration mode.

        If the application is already initialized, or if the global flag for synchronous node registration is set,
        it returns NodeRegistrationMode.Deferred.

        Args:
            ext_id: The ID of the extension which will be loaded.

        Return: Returns the node registration mode used for the given extension.
        """

        # If the app has already been initialized, we will import the newly activated extensions synchronously
        app_initialized = not self.__app_ready_sub

        # Fallback setting in case the async node registration has some global negative side effects
        settings = carb.settings.get_settings()
        force_global_sync_node_registration = settings and settings.get("/exts/omni.graph/syncNodeRegistration")
        if app_initialized or force_global_sync_node_registration:
            return self.NodeRegistrationMode.Synchronous

        mode = self.NodeRegistrationMode.Deferred
        manager = get_app_interface().get_extension_manager()
        config = manager.get_extension_dict(ext_id).get_dict()
        package_config = config["package"]
        python_config = package_config.get("python", None)
        if python_config:
            m = python_config.get("node_registration_mode", None)
            mode = mode if m is None else self.NodeRegistrationMode[m]

        return mode

    # --------------------------------------------------------------------------------------------------------------
    def on_after_ext_enabled(self, ext_id: str, *_):
        """
        Triggers the node registration task. Depending on the extension configuration and other factors,
        the node registration task can be executed asynchronously, on a background thread.

        Args:
            ext_id: The ID of the extension which will be loaded.
        """

        # query the extension config to see if a given extension is forced imported synchronously
        mode = self.get_node_registration_mode(ext_id)
        if mode == self.NodeRegistrationMode.Synchronous:
            self.__register_nodes(ext_id)
            return

        future = self.__executor.submit(self.__register_nodes, ext_id)
        future.add_done_callback(lambda future: self.__on_register_python_ogn_complete(ext_id, future))
        self.__pending_registrations[ext_id] = future

    # --------------------------------------------------------------------------------------------------------------
    def __register_nodes(self, ext_id: str, *_):
        """Performs the node registration as a background task."""
        _ = ogi.LOG.disabled or ogi.LOG.info("Looking for Python nodes to register in %s", ext_id)
        start_registration = time.perf_counter_ns()
        carb.profiler.begin(1, f"OmniGraph.PythonNode.Registration.{ext_id}")
        manager = get_app_interface().get_extension_manager()
        try:
            ext_info = manager.get_extension_dict(ext_id).get_dict()
            try:
                ext_path = Path(ext_info["path"])
            except KeyError:
                carb.log_warn(f"Unable to find the path of extension {ext_id} - nodes could not be registered")
                return
            try:
                module_list = ext_info["python"]["module"]
            except KeyError:
                # If there is no Python module there is no chance it has Python nodes implemented
                return

            for module_info in module_list:
                try:
                    # If the module or extension information isn't available then nothing can be registered
                    module_name = module_info["name"]
                    ext_name = ext_info["package"]["name"]
                except KeyError:
                    continue
                try:
                    autonode_config = ext_info["omni"]["graph"]["autonode"]
                except KeyError:
                    autonode_config = {}
                try:
                    _ = ogi.LOG.disabled or ogi.LOG.info(
                        " -> Registered nodes from module %s at %s", module_name, ext_path
                    )
                    # No sense in registering this extension as everything will be gone if it unloads anyway
                    if not ext_id.startswith("omni.graph-"):
                        new_registration = og.PythonNodeRegistration(ext_name, module_name, ext_path, autonode_config)
                        self.__module_registrations[ext_id].append(new_registration)
                except ModuleNotFoundError as error:
                    _ = ogi.LOG.disabled or ogi.LOG.info(
                        "...Skipping: No Python module for the extension %s - %s", ext_name, error
                    )
                except ogi.OmniGraphExtensionError as error:
                    _ = ogi.LOG.disabled or ogi.LOG.info(
                        "...Skipping: No OmniGraph presence in the module %s - %s", module_name, error
                    )
        except KeyError as error:
            carb.log_error(f"Extension {ext_id} failed to register Python nodes - {error}")
        finally:
            carb.profiler.end(1)
            end_registration = time.perf_counter_ns()
            self.REGISTRATION_TIMING[ext_id] = end_registration - start_registration
            _ = ogi.LOG.disabled or ogi.LOG.info("OGN register %s took %f", ext_id, self.REGISTRATION_TIMING[ext_id])

    def __on_register_python_ogn_complete(self, ext_id: str, future: concurrent.futures.Future):
        """
        Callback when the python code registration completes.

        Args:
            ext_id: The id of the extension that was loaded by the background task.
            future: The future of the background task.
        """
        # Remove the pending task once complete
        with suppress(AttributeError):
            self.__pending_registrations.pop(ext_id, None)

        exception = future.exception()
        if exception:
            carb.log_error(f"OGN node registration completed with errors: {exception}")

        _ = ogi.LOG.disabled or ogi.LOG.info("OGN Python module registration complete %s", ext_id)

    # --------------------------------------------------------------------------------------------------------------
    def on_before_ext_disabled(self, ext_id: str, *_):
        _ = ogi.LOG.disabled or ogi.LOG.info("Looking for Python nodes to deregister in %s", ext_id)
        start_deregistration = time.perf_counter_ns()
        # cancel the pending registration task, if still running
        future = self.__pending_registrations.pop(ext_id, None)
        if future and not future.done:
            cancelled = future.cancel()
            # Futures cannot be cancelled if they are already running.
            # In that case, we have to wait for them to complete before we can unload the extension,
            # otherwise the background tasks will raise exceptions when trying to access attributes
            # that have already been destroyed.
            if not cancelled:
                concurrent.futures.wait(future)

        try:
            carb.profiler.begin(1, f"OmniGraph.PythonNode.Deregistration.{ext_id}")
            with suppress(KeyError):
                for x in self.__module_registrations[ext_id]:
                    x.deregister()
                del self.__module_registrations[ext_id]
                _ = ogi.LOG.disabled or ogi.LOG.info("Deregistered Python nodes in %s", ext_id)
        finally:
            carb.profiler.end(1)
            end_deregistration = time.perf_counter_ns()
            self.DEREGISTRATION_TIMING[ext_id] = end_deregistration - start_deregistration
            _ = ogi.LOG.disabled or ogi.LOG.info(
                "OGN deregister %s took %.2fus", ext_id, self.DEREGISTRATION_TIMING[ext_id] / 1e3
            )

    # --------------------------------------------------------------------------------------------------------------
    # begin-file-format-update
    def on_startup(self):
        """Set up initial conditions for the Python part of the extension"""
        self.__module_registrations = defaultdict(list)
        self.__interface = og.acquire_interface()
        og.register_python_node()

        hooks = omni.kit.app.get_app_interface().get_extension_manager().get_hooks()
        self.__extension_post_enabled_hook = hooks.create_extension_state_change_hook(
            self.on_after_ext_enabled, omni.ext.ExtensionStateChangeType.AFTER_EXTENSION_ENABLE
        )
        assert self.__extension_post_enabled_hook
        self.__extension_pre_disabled_hook = hooks.create_extension_state_change_hook(
            self.on_before_ext_disabled, omni.ext.ExtensionStateChangeType.BEFORE_EXTENSION_DISABLE
        )
        assert self.__extension_pre_disabled_hook

        self.__registry_subscription = (
            og.GraphRegistry()
            .get_event_stream()
            .create_subscription_to_pop(self.__on_pre_attach, name="OGN Node Registration")
        )
        assert self.__registry_subscription

        def upgrade_format(old_format_version, new_format_version, _):
            if old_format_version < og.FileFormatVersion(1, 5):
                cb_update_to_include_schema(old_format_version, new_format_version, None)
            if old_format_version < og.FileFormatVersion(1, 6):
                migrate_attribute_custom_data(old_format_version, new_format_version, None)
            if old_format_version < og.FileFormatVersion(1, 7):
                migrate_compound_node_schema_data(old_format_version, new_format_version, None)
            if old_format_version < og.FileFormatVersion(1, 8):
                migrate_bundle_io_asymmetry(old_format_version, new_format_version, None)
            if old_format_version < og.FileFormatVersion(1, 9):
                migrate_bundle_separator(old_format_version, new_format_version, None)

        self.__upgrade_format_cb = og.register_pre_load_file_format_upgrade_callback(upgrade_format)

        self.__pre_del_prim_cb = omni.kit.commands.register_callback(
            "DeletePrimsCommand", omni.kit.commands.PRE_DO_CALLBACK, self.__on_before_del_prim
        )

        # Listen for the app ready event to complete the registration tasks if necessary.
        def _on_app_ready(_):
            settings = carb.settings.get_settings()
            # when running the tests, force the background registration tasks to finish immediately
            # to ensure that all tests and nodes are registered
            if not settings or settings.get("/app/isTestRun"):
                complete_node_registrations(self.__pending_registrations)
            self.__app_ready_sub = None

        self.__app_ready_sub = get_eventdispatcher().observe_event(
            event_name=omni.kit.app.GLOBAL_EVENT_APP_READY,
            on_event=_on_app_ready,
            observer_name="Finish OGN Registration",
        )

        # Categories are in configuration files so they have to be added to OmniGraph here
        register_categories()

    # --------------------------------------------------------------------------------------------------------------
    def on_shutdown(self):
        """Shutting down this part of the extension prepares it for hot reload"""
        self.__app_ready_sub = None
        self.__registry_subscription = None
        self.__extension_post_enabled_hook = None
        self.__extension_pre_disabled_hook = None
        omni.kit.commands.unregister_callback(self.__pre_del_prim_cb)
        self.__pre_del_prim_cb = None
        og.on_shutdown()
        og.release_interface(self.__interface)
        self.__interface = None
        unregister_module_commands(og.cmds)
        if self.__pending_registrations:
            carb.log_warn(
                f"Shutting down OmniGraph with modules pending registration - {self.__pending_registrations.keys()}"
            )
            self.__pending_registrations = defaultdict()
        if self.__module_registrations:
            carb.log_warn(f"Shutting down OmniGraph with modules registered - {self.__module_registrations.keys()}")
            self.__module_registrations = defaultdict(list)

        og.deregister_pre_load_file_format_upgrade_callback(self.__upgrade_format_cb)
        self.__upgrade_format_cb = None
        # end-file-format-update
        self.DEREGISTRATION_TIMING = {}

    def __on_pre_attach(self, event: carb.events.IEvent):
        """Handle the PRE_ATTACH event and synchronize the background tasks if necessary."""
        if event.type == int(og.GraphRegistryEvent.STAGE_PRE_ATTACH) and event.payload.get(
            "has_og_prims_on_stage", False
        ):
            complete_node_registrations(self.__pending_registrations)

    # --------------------------------------------------------------------------------------------------------------
    def __on_before_del_prim(self, info):
        # Get the command's 'paths' argument.
        paths: List[Union[str, Sdf.Path]] = info.get("paths", None)
        if not paths:
            return

        # Remove duplicates.
        paths = set(paths)

        # Find all the OG nodes which will be removed.
        nodes_being_removed: Set[og.Node] = set()
        while paths:
            path = paths.pop()
            graph = og.Controller.graph(path)
            if graph:
                # Add the subgraph's nodes.
                for node in graph.get_nodes():
                    paths.add(node.get_prim_path())
            else:
                with suppress(og.OmniGraphValueError):
                    node = og.Controller.node(path)
                    nodes_being_removed.add(node)

        # Find any connections where the source node is being deleted
        # but the destination isn't. Those will result in broken connections
        # which the OG core won't be able to restore if the DeletePrims
        # command is undone. To work around that we'll add an undo task
        # to the command's undo block.
        conns_to_undo: List[Tuple[str, str]] = []
        for node in nodes_being_removed:
            for attr in node.get_attributes():
                for dest_attr in attr.get_downstream_connections():
                    dest_node = dest_attr.get_node()
                    if dest_node not in nodes_being_removed:
                        # Attribute.get_path() does not return a valid path for bundle outputs so
                        # we must build the path from its parts.
                        src_path = node.get_prim_path() + "." + attr.get_name()
                        dest_path = dest_node.get_prim_path() + "." + dest_attr.get_name()
                        conns_to_undo.append((src_path, dest_path))
        if conns_to_undo:
            omni.kit.commands.execute("_OGRestoreConnectionsOnUndo", connections=conns_to_undo)
