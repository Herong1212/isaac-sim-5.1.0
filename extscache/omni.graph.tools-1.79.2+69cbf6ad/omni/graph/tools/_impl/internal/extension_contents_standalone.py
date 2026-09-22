from __future__ import annotations

import sys
from contextlib import suppress
from importlib import import_module
from pathlib import Path
from types import ModuleType

import carb

from .extension_contents_base import ExtensionContentsBase
from .file_utils import FileType, get_module_path, get_ogn_type_and_node, load_module_from_file
from .logging_utils import LOG, OmniGraphExtensionError
from .node_type_definition import NodeTypeDefinition


# ==============================================================================================================
class ExtensionContentsStandalone(ExtensionContentsBase):
    """Variation of the ExtensionContents class that handles the case of node types not being part of a build.
    In this case there is no generated code and the cache is relied on for everything.
    """

    def __init__(self, ext_id: str, module: ModuleType, ext_path: str | Path):
        _ = LOG.disabled or LOG.info(
            "Creating standalone extension manager for %s in module %s at %s", ext_id, module, ext_path
        )
        super().__init__(ext_id, module, ext_path)
        self._ogn_files = []
        self._py_files = []

    # --------------------------------------------------------------------------------------------------------------
    def __str__(self) -> str:
        return f"STANDALONE {super().__str__()}"

    # --------------------------------------------------------------------------------------------------------------
    def set_scanned_files(self, python_files: list[Path], ogn_files: list[Path]):
        _ = LOG.disabled or LOG.info(
            "Adding in %d scanned Python files and %d scanned .ogn files", len(python_files), len(ogn_files)
        )
        self._ogn_files = ogn_files
        self._py_files = []
        for ogn_file in ogn_files:
            python_file = ogn_file.with_suffix(".py")
            if python_file in python_files:
                self._py_files.append(python_file)
            else:
                # Make the two lists match so that they can be easily walked later
                self._py_files.append(None)
        _ = LOG.disabled or LOG.info("...OGN files %s", self._ogn_files)
        _ = LOG.disabled or LOG.info("...Database files %s", self._py_files)

    # --------------------------------------------------------------------------------------------------------------
    def scan_for_nodes(self):
        """Process the already-scanned files to determine the available node types"""
        _ = LOG.disabled or LOG.info("Scanning the nodes available in the standalone extension manager")
        for ogn_file, py_file in zip(self._ogn_files, self._py_files):
            (class_name, file_type) = get_ogn_type_and_node(ogn_file.name)
            if file_type is None:
                continue
            _ = LOG.disabled or LOG.info("...adding definition for %s at %s", class_name, ogn_file)
            self.node_type_definitions[class_name] = NodeTypeDefinition(class_name, ogn_file)
            if py_file is not None:
                self.node_type_definitions[class_name].add_files([(py_file, FileType.PYTHON)])

        # Standalone extensions always need a cache created for them - see if it exists yet
        self.scan_cache()

    # --------------------------------------------------------------------------------------------------------------
    # TODO: The description is customized for standalone setups, the code is not
    def ensure_required_modules_exist(self) -> tuple[ModuleType | None, ModuleType | None]:
        """Make sure the required OGN modules exist.

        As this is a standalone extension the modules are created directly from the cache. The cache comprises a
        package with generated __init__.py file that imports everything so all that is required is to import the
        cache modules into the proper namespaces.

        Returns:
            A tuple with the populated .ogn and .ogn.tests modules. If nothing was needed in the modules (e.g. no
            node definitions or no tests) then the module will be None. As a side effect the tuples are stored on
            this object for future use.

        Raises:
            OmniGraphExtensionError if anything that prevents proper registration happens
        """
        (ogn_module_name, ogn_test_module_name) = self.ogn_module_names()
        _ = LOG.disabled or LOG.info("Importing %s and %s", ogn_module_name, ogn_test_module_name)

        def __find_module(module_name: str, parent_module: ModuleType, submodule_name: str) -> ModuleType | None:
            """Find a module in this extension's space, or import it from the cache"""
            _ = LOG.disabled or LOG.info(
                "--- Finding module %s in %s with submodule name %s", module_name, parent_module, submodule_name
            )
            module = None

            # Check 1 - has the module already been imported on its own?
            with suppress(KeyError):
                module = sys.modules[module_name]
                _ = LOG.disabled or LOG.info("...module %s was already in the Python namespace", module_name)
                return module

            _ = LOG.disabled or LOG.info("--X module was not already imported")

            # Check 2 - has the module been imported as a member of the main module?
            # submodule_name might be ogn.tests but the parent module is ogn so only the "tests" part is needed here
            last_element = ".".join(submodule_name.split(".")[:-1])
            if hasattr(parent_module, last_element):
                submodule = getattr(parent_module, last_element)
                _ = LOG.disabled or LOG.info("...ogn found as an object in %s (%s)", parent_module, submodule)
                if isinstance(submodule, ModuleType):
                    return submodule
                raise OmniGraphExtensionError(f"ogn object {submodule} should have been a module itself")

            # Check 3 - can the module be imported from a directory in the build tree?
            _ = LOG.disabled or LOG.info("... Trying to import %s directly", module_name)
            with suppress(ModuleNotFoundError):
                module = import_module(module_name)
                _ = LOG.disabled or LOG.info("--> Found the module at %s", module)
                return module

            _ = LOG.disabled or LOG.info("--X Submodule %s could not be imported, trying the cache", module_name)

            # If all else fails import the module from the cache tree, which must exist if everything is consistent
            if self.cache_path is None or not self.cache_path.is_dir():
                raise OmniGraphExtensionError(f"Cache path required for import is not a directory - {self.cache_path}")
            # The cache path already includes the ogn/ subdirectory so bump it up one level
            cache_submodule_path = "/".join(submodule_name.split(".")[1:])
            submodule_cache_path = self.cache_path / cache_submodule_path / "__init__.py"
            if not submodule_cache_path.is_file():
                raise OmniGraphExtensionError(
                    f"Submodule cache path required for import is not a file - {submodule_cache_path}"
                )

            try:
                module = load_module_from_file(module_name, submodule_cache_path)
            except ModuleNotFoundError as error:
                raise OmniGraphExtensionError(
                    f"Submodule cache path {submodule_cache_path} could not be imported"
                ) from error

            return module

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Construct the EXTENSION.ogn import space, either from the build if available, or the cache if not
        if self.ogn_module is None:
            try:
                self.ogn_module = __find_module(ogn_module_name, self._module, "ogn")
            except KeyError as error:
                raise OmniGraphExtensionError(f"Main module {self.module_name} could not be found") from error
        if self.ogn_test_module is None and self._has_tests and self.ogn_module is not None:
            _ = LOG.disabled or LOG.info("-> Found .ogn module, looking for ogn.tests too")
            self.ogn_test_module = __find_module(ogn_test_module_name, self.ogn_module, "ogn.tests")
        return (self.ogn_module, self.ogn_test_module)

    # --------------------------------------------------------------------------------------------------------------
    # TODO: The description is customized for standalone setups, the code is not
    def do_python_imports(self):
        """Find or create the .ogn and .ogn.tests modules in the extension and import the required files into them

        Since all of the work is done when defining the modules this just calls that and returns.
        """
        _ = LOG.disabled or LOG.info("Attempting OGN Standalone Python imports for %s", self._ext_id)
        if not self.node_type_definitions:
            return (None, None)

        (ogn_module, ogn_test_module) = self.ensure_required_modules_exist()
        node_classes = {}

        # Walk all of the known node types and insert their XDatabase.py and TestX.py files into the module,
        # if they exist. (Either may be legally excluded from generation.)
        for definition in self.node_type_definitions.values():
            if ogn_module is not None:
                db_file = definition.database_to_use()
                if db_file is not None:
                    db_module_name = f"{ogn_module.__name__}.{db_file.stem}"
                    db_module = load_module_from_file(db_module_name, db_file)
                    setattr(ogn_module, db_file.stem, db_module)
                    node_file = definition.file_path(FileType.PYTHON)
                    _ = LOG.disabled or LOG.info(
                        "...Importing DB %s into %s from %s", db_module_name, db_module, db_file
                    )
                    if node_file is not None:
                        relative_location = ".".join(node_file.relative_to(self.module_directory).with_suffix("").parts)
                        node_module_name = f"{self.module_name}.{relative_location}"
                        node_module = load_module_from_file(node_module_name, node_file)
                        _ = LOG.disabled or LOG.info(
                            "...Importing Node %s into %s from %s", node_module_name, node_module, node_file
                        )
                        node_class = getattr(node_module, definition.name, None)
                        if node_class is None:
                            carb.log_warn(f"Node definition in {node_file} had no implementation of the node class")
                        else:
                            node_classes[db_file.stem] = node_class
                else:
                    _ = LOG.disabled or LOG.info(
                        "No database file for %s - not trying to import the node", definition.name
                    )

            if ogn_test_module is not None:
                test_file = definition.test_to_use()
                if test_file is not None:
                    test_module_name = f"{ogn_test_module.__name__}.{test_file.stem}"
                    test_module = load_module_from_file(test_module_name, test_file)
                    setattr(ogn_test_module, test_file.stem, test_module.TestOgn)
                    _ = LOG.disabled or LOG.info(
                        "...Imported test %s into %s from %s", test_module_name, test_module, test_file
                    )

        # The special node implementation
        if ogn_module is not None:
            setattr(ogn_module, self.NODE_STORAGE_OBJECT, node_classes)

            # Add any symlinked or copied non-generated files into the module, for backward compatibility.
            ogn_module_path = get_module_path(ogn_module)
            if self.module_path in ogn_module_path.parents:
                for potential_import in ogn_module_path.iterdir():
                    submodule_name = potential_import.stem
                    # The generated tests directory, database files, and Python caches can be ignored
                    if submodule_name in ["tests", "__pycache__"]:
                        continue
                    if submodule_name.endswith("Database"):
                        continue

                    import_module_name = f"{ogn_module.__name__}.{submodule_name}"
                    top_level_module = load_module_from_file(import_module_name, potential_import)
                    if top_level_module is not None:
                        setattr(ogn_module, submodule_name, top_level_module)

        return (ogn_module, ogn_test_module)
