"""Utilities for managing the OGN-related contents of an extension"""

from __future__ import annotations

import re
import sys
from importlib import import_module
from pathlib import Path
from types import ModuleType

import carb
import omni.graph.core as og
import omni.graph.tools._internal as ogi
import omni.kit

_RE_EXT_ID = re.compile(r"(.*)-[\.0-9]+$")
"""Regex to separate an extension version and name from a full id - e.g. omni.graph.core-0.1.0"""


# ==============================================================================================================
def extension_management_factory(
    ext_name: str, module_name: str, ext_path: str | Path
) -> ogi.ExtensionContentsBase | None:
    """Figures out what kind of OmniGraph content is in the named extension module

    Args:
        ext_name: Name of the extension for which this factory is constructing a manager. Optionally contains the
            version number which will be used rather than looking it up in the extension registry.
        module_name: Python module within the extension being handled
        ext_path: Root directory of the extension

    Returns:
        omni.graph.tools._internal.ExtensionContentsBase: Constructed manager for OmniGraph contents in the given
            extension, or None if there is no OmniGraph content in the Python module.
    """

    def __construct_manager(
        base_class, ext_id: str, module: ModuleType, ext_path: str | Path
    ) -> ogi.ExtensionContentsBase:
        class _ExtensionManagement(base_class):
            """Extends the tools handling of the files relating to node types within an extension.
            The extended part manages the information that is only available from OmniGraph proper.
            For example it has access to all node categories whereas the tools area only has access
            to the ones hard-coded in the tools extension.
            """

            def __init__(self, ext_id: str, module: ModuleType, ext_path: str | Path):
                """See :py:class:`omni.graph.tools._internal.ExtensionContents` for details"""
                _ = ogi.LOG.disabled or ogi.LOG.info("Creating OmniGraph extension management class")
                self._categories = None  # Defined in parent but lint does not know that so duplicate it here
                super().__init__(ext_id, module, ext_path)

            # --------------------------------------------------------------------------------------------------------------
            @property
            def categories(self) -> dict | None:
                """Returns the dictionary of CategoryName:Description for all known categories.
                Overrideds the version in the base class that gets them directly from the hard-coded file
                """
                if self._categories is None:
                    self._categories = og.get_node_categories_interface().get_all_categories()
                    _ = ogi.LOG.disabled or ogi.LOG.info("...Allowed categories = %s", self._categories)
                return self._categories

            # --------------------------------------------------------------------------------------------------------------
            def do_registration(self) -> dict[str, callable]:
                """Register all of the known node types and return the list of their deregistration functions
                Returns:
                    Dictionary of NodeTypeName:DeregistrationMethod Python node types that were registered here
                """
                _ = ogi.LOG.disabled or ogi.LOG.info("Registering the nodes in %s", self.ext_name)
                deregister_functions = {}
                # Walk all of the XDatabase.py files and run their register() methods
                node_implementations = getattr(self.ogn_module, self.NODE_STORAGE_OBJECT, {})
                _ = ogi.LOG.disabled or ogi.LOG.info("-- node implementations %s", node_implementations)
                for database_class_name, node_module in node_implementations.items():
                    try:
                        database_class = getattr(getattr(self.ogn_module, database_class_name), database_class_name)
                        _ = ogi.LOG.disabled or ogi.LOG.info(
                            "Found the database class %s with node module %s", database_class, node_module
                        )
                        database_class.register(node_module)
                        _ = ogi.LOG.disabled or ogi.LOG.info(
                            "Registered okay, adding the deregister function %s", database_class.deregister
                        )
                        deregister_functions[database_class_name] = database_class.deregister
                        _ = ogi.LOG.disabled or ogi.LOG.info("...Registered through database %s", database_class_name)
                    except AttributeError:
                        carb.log_warn(
                            f"Registering {self.ext_name} failed when it could not find the "
                            f"database class for {database_class_name} - {dir(self.ogn_module)}"
                        )

                return deregister_functions

        return _ExtensionManagement(ext_id, module, ext_path)

    # If the extension does not have a dependency on omni.graph then there will be no Python nodes to find.
    # This gives a quick early-out for non-OmniGraph extensions. Start the check as True since the test cannot be
    # relied on if the extension is not yet enabled, as would be the case in testing.
    might_have_nodes = True
    # If the extension name was passed with a version already in place use it rather than looking it up and it will
    # be assumed that the extension might have nodes in it. (Most useful as a shortcut for tests with temporary
    # extensions that may not be registered.)
    ext_match = _RE_EXT_ID.match(ext_name)
    ext_id = ext_name
    if ext_match:
        ext_name = ext_match.group(1)
    else:
        mgr = omni.kit.app.get_app().get_extension_manager()
        # Loop twice here, the first time just checking what is already in the extension registry and the second
        # time refreshing the registry so that it contains the latest extensions. The refresh should only be
        # necessary in testing situations as usually the extension is requesting the registration and so will be
        # already enabled.
        for attempt in range(2):
            if attempt == 1:
                _ = ogi.LOG.disabled or ogi.LOG.info(
                    f"Synchronizing the registry looking for {ext_name}, {module_name}, {ext_path}"
                )
                mgr.sync_registry()
            found_version = False
            for version in mgr.fetch_extension_versions(ext_name):
                if not version["enabled"]:
                    continue
                found_version = True
                might_have_nodes = False
                ext_id = version["id"]
                result, dependencies, error = mgr.solve_extensions([ext_id])
                if not result:
                    _ = ogi.LOG.disabled or ogi.LOG.warn(
                        f"Could not find dependencies of {ext_id} due to '{error}', assuming OmniGraph used"
                    )
                    might_have_nodes = True
                elif any(dependency["id"].startswith("omni.graph-") for dependency in dependencies):
                    might_have_nodes = True
                break
            if found_version:
                break
    if not might_have_nodes:
        _ = ogi.LOG.disabled or ogi.LOG.info(
            "No dependency on omni.graph, therefore no nodes to register in %s", ext_name
        )
        return None

    if ext_id == ext_name:
        ogi.LOG.warn("Extension '%s' was not registered so no version ID was available - using the name", ext_id)

    _ = ogi.LOG.disabled or ogi.LOG.info(
        "Finding OmniGraph extension content manager for %s in module %s at %s", ext_id, module_name, ext_path
    )
    try:
        main_module = sys.modules[module_name]
    except KeyError:
        try:
            main_module = import_module(module_name)
        except ModuleNotFoundError:
            _ = ogi.LOG.disabled or ogi.LOG.info("-> No Python module in this extension")
            return None

    # Check for a new-style extension with generated code in the top level ogn/ subdirectory.
    # e.g. exts/omni.my.extension/ogn/omni.my.extension/
    generated_folder = ext_path / "ogn" / module_name
    if generated_folder.is_dir():
        return None  # TODO: __construct_manager(ogi.ExtensionContentsV119, ext_id, main_module, ext_path)
    _ = ogi.LOG.disabled or ogi.LOG.info("-> New generated folder %s is not a directory", generated_folder)

    # Check for a V1.18 extension with generated code in the module's ogn/ subdirectory.
    # e.g. exts/omni.my.extension/omni/my/extension/ogn/
    module_path = ext_path / module_name.replace(".", "/")
    ogn_folder = module_path / "ogn"
    if ogn_folder.is_dir():
        return __construct_manager(ogi.ExtensionContentsV118, ext_id, main_module, ext_path)
    _ = ogi.LOG.disabled or ogi.LOG.info("-> Old ogn/ folder %s is not a directory", ogn_folder)

    # Check for standalone nodes in the extension by walking the module's directory tree.
    # os.walk is used instead of Path.rglob because in tests it was found to be 50% faster.
    # Remember the contents of the tree to avoid walking it again in the scan phase.
    python_files = []
    ogn_files = []
    for root, _, files in ogi.walk_with_excludes(module_path, ["__pycache__"]):
        if not ogi.autonode_developer_mode() and ogi.OGN_AUTOGENERATED_SUBFOLDER_NAME in Path(root).parts:
            carb.log_warn(
                f"Found AutoNode definitions in {root} but the setting '{ogi.AUTONODE_DEVELOPER_MODE_SETTING}'"
                f" has not been enabled. Skipping registration of node types in that directory."
            )
            return None
        for file in files:
            if file.endswith(".ogn"):
                ogn_file = Path(root) / file
                ogn_files.append(ogn_file)
                python_file = ogn_file.with_suffix(".py")
                if python_file.is_file():
                    python_files.append(python_file)

    if ogn_files:
        standalone_manager = __construct_manager(ogi.ExtensionContentsStandalone, ext_id, main_module, ext_path)
        standalone_manager.set_scanned_files(python_files, ogn_files)
        return standalone_manager

    _ = ogi.LOG.disabled or ogi.LOG.info(
        "-> Extension contents not recognized as containing OmniGraph Python information"
    )
    return None
