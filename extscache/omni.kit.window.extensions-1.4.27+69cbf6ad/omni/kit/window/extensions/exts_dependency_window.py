# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
"""This module provides a visual representation of extension dependencies within the Omniverse Kit, including classes for dependency models, views, and widgets."""

__all__ = []

from collections import defaultdict
from enum import Enum
from typing import List, Tuple

import carb
import omni.kit.app
import omni.ui as ui
from carb.eventdispatcher import get_eventdispatcher

from .utils import ext_id_to_fullname

# pylint: disable=property-with-parameters


# Colors & Style
BACKGROUND_COLOR = 0xFF34302A
BORDER_DEFAULT = 0xFF232323
CONNECTION = 0xFF80C280
NODE_BACKGROUND = 0xFF141414
PLUGINS_COLOR = 0xFFFFE3C4
LIBRARIES_COLOR = 0xAA44EBE7
MODULES_COLOR = 0xFFAAE3C4

# Constants
MARGIN_WIDTH = 7.5
MARGIN_TOP = 20.0
MARGIN_BOTTOM = 25.0

BORDER_THICKNESS = 3.0
HEADER_HEIGHT = 25.0
MIN_WIDTH = 180.0

CONNECTION_CURVE = 60


class ExtsDependencyWidget:
    """Extensions dependency window

    Args:
        ext_id (str): The identifier for the extension whose dependencies are to be visualized."""

    def __init__(self, ext_id):
        """Initializes the extensions dependency widget with the given extension id."""
        self._ext_id = ext_id

        with ui.ZStack():
            self._model = DependenciesModel(self._ext_id)

            self._list_frame = ui.Frame()
            with self._list_frame:
                self._list_view = ExtsListView(self._model, self._ext_id)

    def destroy(self):
        """Cleans up and releases all the resources used by the extensions dependency widget."""
        self._model = None
        self._list_frame = None
        self._list_view = None


class ExtDependencyItem:
    """A dependency item representing an extension in the Extensions dependency.

    This class encapsulates information about an extension such as its dependencies, plugins, libraries, and Python modules.

    Args:
        manager (:obj:`omni.kit.app.ExtensionManager`): The manager handling extension-related information.
        ext_id (str): The unique identifier for the extension."""

    def __init__(self, manager, ext_id):
        """Initializes an ExtDependencyItem instance, gathering extension dependencies and information such as plugins, libraries, and modules."""
        info = manager.get_extension_dict(ext_id)

        # Extension dependencies:
        self.deps = info.get("state/dependencies", [])
        self.port_deps = [d + "/out" for d in self.deps]

        # Extension useful info (id, version, plugins, modules etc)
        state_dict = info.get("state", {})
        native_dict = state_dict.get("native", {})
        self.id = ext_id
        self.plugins = native_dict.get("plugins", [])
        self.libraries = native_dict.get("libraries", [])
        self.modules = state_dict.get("python", {}).get("modules", [])

    def __lt__(self, other):
        return self.id < other.id


class DependenciesModel:
    """A class representing a dependency model of extension dependencies.

    This class constructs a dependency model that represents the dependencies between extensions. It can filter out unreachable nodes based on a specified root extension ID and provides functionalities to copy the dependency as a Graphviz dot representation.

    Args:
    ext_id (str): Optional. The root extension ID to filter the dependency for a specific extension."""

    class ExpansionState(Enum):
        """Enum for node expansion states."""

        OPEN = 0
        """Node is fully expanded."""
        MINIMIZED = 1
        """MINIMIZED: Node is minimized but not closed."""
        CLOSED = 2
        """Node is closed and ports content is not visible."""

    def __init__(self, ext_id: str = None):
        """Initialize the dependency model, potentially with a filtered dependency based on an extension ID."""
        super().__init__()

        # build dependency out of enabled extensions
        manager = omni.kit.app.get_app_interface().get_extension_manager()
        exts = manager.get_extensions()
        enabled_exts = [e["id"] for e in exts if e["enabled"]]
        self._nodes = {ext_id: ExtDependencyItem(manager, ext_id) for ext_id in enabled_exts}

        # If ext_id was passed filter out extension that are not reachable from this one.
        self._root_ext_id = ext_id
        if self._root_ext_id:
            self._filter_out_unreachable_nodes(ext_id)

    def _filter_out_unreachable_nodes(self, ext_id):
        visited = set()
        q = []

        root = self._nodes.get(ext_id, None)
        if not root:
            carb.log_error(f"Failure to filter dependency, can't find ext node: {ext_id}")
            return

        q.append(root)
        visited.add(root)

        while len(q) > 0:
            node = q.pop()
            for d in node.deps:
                child = self._nodes[d]
                if child not in visited:
                    visited.add(child)
                    q.append(child)

        self._nodes = {ext_id: item for ext_id, item in self._nodes.items() if item in visited}

    @property
    def expansion_state(self, item=None):
        """Gets the expansion state for a given item.

        Args:
            item (str): The identifier of the item whose expansion state to retrieve.

        Returns:
            ExpansionState: The expansion state of the item."""
        return self.ExpansionState.CLOSED

    @property
    def nodes(self, item=None):
        """Gets the node identifiers for a given item.

        Args:
            item (str): The identifier of the item whose nodes to retrieve.

        Returns:
            set: A set of node identifiers related to the item."""
        return {e.id for e in self._nodes.values()}

    @property
    def name(self, item=None):
        """Gets the name of the node for a given item.

        Args:
            item (str): The identifier of the item whose name to retrieve.

        Returns:
            str: The name of the item, if it exists."""
        if item in self._nodes:
            return self._nodes[item].id

        if item:
            # Use the last token after the slash for the port name, or the whole string
            return item.split("/")[-1]
        return None

    @property
    def item(self, item=None):
        """Gets the dependency item for a given identifier.

        Args:
            item (str): The identifier of the dependency item to retrieve.

        Returns:
            ExtDependencyItem: The dependency item associated with the identifier."""
        return self._nodes[item]

    @property
    def ports(self, item=None):
        """Gets the ports for a given item.

        Args:
            item (str): The identifier of the item whose ports to retrieve.

        Returns:
            list: A list containing the input and output ports of the item."""
        return [item + "/in", item + "/out"]

    @property
    def inputs(self, item):
        """Gets the input ports dependencies for a given item.

        Args:
            item (str): The identifier of the item whose input ports to retrieve.

        Returns:
            list: A list of input port dependencies for the item."""
        if item.endswith("/in"):
            item = self._nodes.get(item[:-3], None)
            return item.port_deps if item else []
        return None

    @property
    def outputs(self, item):
        """Gets the output ports for a given item.

        Args:
            item (str): The identifier of the item whose output ports to retrieve.

        Returns:
            list: An empty list, since items do not have output ports."""
        outputs = [] if item.endswith("/out") else None
        return outputs


class ExtsListView:
    """A view widget to list the dependencies and reverse dependencies of an extension.

    This view provides an interface to display direct and indirect dependencies and reverse dependencies of a particular extension within the Omniverse Kit application. The list is presented in a scrolling frame with labels for each category of dependencies.

    Args:
        model (:obj:`DependenciesModel`): The dependency model containing node data for dependencies.
        ext_id (str): The identifier of the extension to display dependencies for."""

    def __init__(self, model, ext_id):
        """Initializes the ExtsListView which provides a UI representation of extension dependencies."""
        self._model = model
        self._ext_id = ext_id

        # gather reverse dependencies from both local extensions and registry extensions
        registry_exts = []
        unique_registry_exts = set()
        manager = omni.kit.app.get_app_interface().get_extension_manager()
        for ext in manager.get_extensions():
            ext_name = ext["name"]
            registry_exts.append(ext)
            unique_registry_exts.add(ext_name)
        for ext in manager.get_registry_extensions():
            ext_id = ext["id"]
            ext_name = ext["name"]
            if ext_name not in unique_registry_exts:
                # grab latest version of each extension
                versions = manager.fetch_extension_versions(ext_name)
                if len(versions) > 0 and versions[0]["id"] == ext_id:
                    registry_exts.append(ext)
                    unique_registry_exts.add(ext_name)
        self._reverse_dep = self._get_reverse_dependencies(manager, registry_exts)

        with ui.ScrollingFrame(
            horizontal_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_ALWAYS_OFF,
            vertical_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_ALWAYS_ON,
        ):
            with ui.ZStack():
                ui.Rectangle(style_type_name_override="ExtensionDescription.ContentBackground")
                with ui.HStack():
                    ui.Spacer(width=10)
                    with ui.VStack(height=0):
                        ui.Spacer(height=10)
                        direct = self._model._nodes[self._ext_id].deps if self._ext_id else ()
                        ui.Label(f"- Direct Dependencies ({len(direct)}):", height=20)
                        for ext in sorted(direct):
                            ui.Label(ext)
                        ui.Spacer(height=10)
                        indirect = [
                            node
                            for node in self._model._nodes.values()
                            if node.id not in direct and node.id != self._ext_id
                        ]
                        ui.Label(f"- All Indirect Dependencies ({len(indirect)}):", height=20)
                        for node in sorted(indirect):
                            ui.Label(node.id)
                    ui.Spacer(width=10)
                    with ui.VStack(height=10):
                        ui.Spacer(height=10)
                        direct = self._reverse_dep[0]
                        ui.Label(f"- Direct Reverse Dependencies ({len(direct)}):", height=20)
                        for item in sorted(direct):
                            ui.Label(item)
                        ui.Spacer(height=10)
                        indirect = [
                            ext
                            for ext in self._reverse_dep[1]
                            if ext not in direct and ext != ext_id_to_fullname(self._ext_id)
                        ]
                        ui.Label(f"- All Indirect Reverse Dependencies ({len(indirect)}):", height=20)
                        for item in sorted(indirect):
                            ui.Label(item)

    def _get_reverse_dependencies(self, manager, exts) -> Tuple[List, List]:
        dependents = defaultdict(set)
        unique_exts_first_order = set()
        unique_exts = set()
        max_depth = 40

        for ext in exts:
            ext_id = ext["id"]
            ext_name = ext["name"]
            info = manager.get_extension_dict(ext_id)
            if not info:
                info = manager.get_registry_extension_dict(ext_id)
            if info:
                deps = info.get("dependencies", [])
                for dep_name in deps:
                    dependents[dep_name].add(ext_name)

        def recurse(ext_name: str, cur_depth: int):
            if cur_depth < max_depth:
                if cur_depth == 1:
                    unique_exts_first_order.add(ext_name)
                unique_exts.add(ext_name)
                for dep_name in dependents[ext_name]:
                    recurse(dep_name, cur_depth + 1)

        if self._ext_id:
            info = manager.get_extension_dict(self._ext_id)
            ext_name = info.get("package/name", "")
            recurse(ext_name, 0)

        # returns a tuple, 1st order deps only and all reverse deps
        return list(unique_exts_first_order), list(unique_exts)


class ExtsDependenciesWindow:
    """A window that visualizes the list of extensions and their interdependencies.

    The window includes functionality to refresh its contents based on changes in the extension manager, select specific extensions to focus on, and toggle its visibility.
    """

    def __init__(self):
        """Initializes the ExtsDependenciesWindow with necessary UI components and subscriptions."""
        self._frame = ui.Frame()
        self._frame.visible = False
        self._dependency_widget = None
        self.select_ext(None)

        self._change_script_sub = [
            get_eventdispatcher().observe_event(
                observer_name="exts_dependency_window",
                on_event=lambda _: self._refresh(),
                event_name=omni.ext.GLOBAL_EVENT_SCRIPT_CHANGED,
            ),
            get_eventdispatcher().observe_event(
                observer_name="exts_dependency_window",
                on_event=lambda _: self._refresh(),
                event_name=omni.ext.GLOBAL_EVENT_FOLDER_CHANGED,
            ),
        ]

    def destroy(self):
        """Cleans up the UI components and subscriptions associated with the ExtsDependenciesWindow."""
        self._frame = None
        if self._dependency_widget:
            self._dependency_widget.destroy()
        self._change_script_sub = None

    def _refresh(self):
        self.set_visible(self._frame.visible)

    def select_ext(self, ext_id):
        """Selects an extension by its identifier to be displayed or focused on in the dependency.

        Args:
            ext_id (str): The identifier of the extension to select."""
        self._ext_id = ext_id

    def set_visible(self, visible: bool):
        """Sets the visibility of the Extensions Dependencies Window.

        Args:
            visible (bool): A flag to toggle the visibility of the window."""
        if self._frame.visible == visible:
            if visible:
                # recreate if already shown
                self.set_visible(False)
            else:
                # if not shown already -> do nothing.
                return

        if not visible:
            self._frame.visible = False
        else:
            self._build()
            self._frame.visible = True

    def _build(self):
        with self._frame:
            if self._dependency_widget:
                self._dependency_widget.destroy()
            self._dependency_widget = ExtsDependencyWidget(self._ext_id)
