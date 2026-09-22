from __future__ import annotations

import abc
import json
from collections import defaultdict
from concurrent.futures import ALL_COMPLETED, ThreadPoolExecutor, wait
from enum import Enum
from pathlib import Path
from types import ModuleType

import carb

from .cache_utils import full_cache_path
from .file_utils import FileType, find_ogn_build_directory, get_module_path, get_ogn_type_and_node, walk_with_excludes
from .logging_utils import LOG
from .node_type_definition import NodeTypeDefinition
from .versions import Compatibility, GenerationVersions


# --------------------------------------------------------------------------------------------------------------
def load_extension_config(ext_root: str) -> dict:
    """Loads the extension.toml file of the extension and returns it as a dictionary

    Args:
        ext_root: the root path to the extension.

    Returns:
        Returns the loaded config as a dictionary.
    """
    import os

    import toml

    # Either use explicit config path or search for known locations
    possible_paths = [f"{ext_root}/config/extension.toml", f"{ext_root}/extension.toml"]
    for p in possible_paths:
        if os.path.exists(p):
            return toml.load(p)
    return None


class CacheScanner:
    """Scans the cache path to find any existing node definitions and tests"""

    def __init__(self, extension: ExtensionContentsBase, cache_path):
        self.extension = extension
        self.cache_path = cache_path
        self.cached_files_found = defaultdict(list)
        self.has_tests = False

    @carb.profiler.profile
    def process_directory(self, entry: tuple):
        """Extracts the class name, path and file type from the input files"""
        root, _, file_names = entry
        root_path = Path(root)
        result = []
        for file_name in file_names:
            # The generated init file can be safely skipped
            if file_name == "__init__.py":
                continue
            file_path = root_path / file_name
            (class_name, file_type) = get_ogn_type_and_node(file_path.name)

            if file_type is None:
                continue

            if class_name not in self.extension.node_type_definitions:
                _ = LOG.disabled or LOG.info(
                    "Unexpected file %s found in the cache. No definition for %s, just %s",
                    file_path,
                    class_name,
                    self.extension.node_type_definitions,
                )
                continue

            _ = LOG.disabled or LOG.info("...found cached file of type %s - %s", file_type, file_path)
            result.append((class_name, file_path, file_type))
        return result

    @carb.profiler.profile
    def add_cached_files(self, entries: list, start, end):
        """Add the cache files found for every node type definition"""
        for i in range(start, end):
            class_name, definition = entries[i]
            definition.add_cached_files(self.cached_files_found[class_name])

    def run_processing(self):
        """Traverses the folders and dispatches the work."""
        futures = []
        thread_count = 32
        with ThreadPoolExecutor() as executor:
            for results in executor.map(self.process_directory, walk_with_excludes(self.cache_path, ["__pycache__"])):
                for class_name, file_path, file_type in results:
                    self.cached_files_found[class_name].append((file_path, file_type))
                    # This information is needed at import time. Track it now to avoid a traversal to find it later.
                    if file_type == FileType.TEST:
                        self.has_tests = True

            # Try to add all of the cached files to the node type definition
            defs = list(self.extension.node_type_definitions.items())
            def_count = len(defs)
            for start in range(0, def_count, thread_count):
                futures.append(
                    executor.submit(self.add_cached_files, defs, start, min(def_count, start + thread_count))
                )
        wait(futures, timeout=None, return_when=ALL_COMPLETED)


# ==============================================================================================================
class ExtensionContentsBase(abc.ABC):
    """Base class for the management of the OmniGraph Python content of an extension.
    This would have been better as a Protocol class but that's not available until we move to Python 3.8+

    Attributes:
        __config_dir (Path): Directory containing the OGN configuration files, either locally or in the Kit SDK
        __node_prefix (str): Unique prefix to prepend to the node type name
        _built_versions (GenerationVersions): Version numbers present in the pre-built generated code
        _categories: dict[str, str]: Available node type categories (for generating code)
        _current_versions (GenerationVersions): Most recent generator and target version numbers
        _ext_name (str): Name of the extension
        _ext_path (Path): Path to the root directory of the extension
        _has_tests (bool): Did scanning the extension find any tests?
        _module (ModuleType): Imported main module for this extension definition
        cache_path (Path): Path to the root directory of the generated code cache
        module_directory (Path): Path to the extension module definition directory, or parent if it's a file
        module_path (Path): Path to the extension module definition file or directory
        node_type_definitions (dict[str, NodeTypeDefinition]): Node type definitions in the extension, by name
        ogn_module (ModuleType): Module containing OGN generated code
        ogn_test_module (ModuleType): Module containing OGN generated tests
    """

    # This is a generated object for the imports to gather all of the extension's node implementations into one place.
    # Practically this will end up in the import location "omni.my.extension.ogn._NODE_IMPLEMENTATIONS" as a dictionary
    # mapping the generated database class name to node implementation objects.
    NODE_STORAGE_OBJECT = "_NODE_IMPLEMENTATIONS"

    class ImportThreadingType(Enum):
        """Specifies the loading strategy for the ogn python nodes and tests in the extension."""

        SingleThreaded = 1
        """The python nodes and test modules in the extension will be loaded on the main thread."""
        SerialThread = 2
        """The python nodes in the extension will be loaded serially in a separate thread, while the tests will be loaded in parallel."""
        ParallelThread = 3
        """The python nodes and the tests will be loaded in separate threads, in parallel."""

    def __init__(self, ext_id: str, main_module: ModuleType, ext_path: str | Path):
        """Common setup that can be shared by all content managers
        Args:
            ext_id: Name and version of the extension for which this factory is constructing a manager
            main_module: Top level Python module within the extension being handled
            ext_path: Root directory of the extension
        """
        self.__config_dir: Path = None
        self._built_versions: GenerationVersions = GenerationVersions()
        self._categories: dict[str, str] = None
        self._current_versions: GenerationVersions = GenerationVersions(Compatibility.FullyCompatible)
        self._ext_name: str = ext_id.split("-")[0]
        self._ext_id: str = ext_id
        self._ext_path: Path = Path(ext_path)
        self._has_tests: bool = False
        self._module: ModuleType = main_module
        self.cache_path: Path = full_cache_path(self._current_versions, ext_id, main_module.__name__)
        self.module_path: Path = get_module_path(self._module)
        self.module_directory: Path = self.module_path.parent if self.module_path.is_file() else self.module_path
        self.node_type_definitions: dict[str, NodeTypeDefinition] = {}
        self.ogn_module: ModuleType = None
        self.ogn_test_module: ModuleType = None
        # Prepend this to the node name to provide a per-extension unique name. Any prebuilt extensions will be
        # using the extension name as a prefix but those delivered without prebuilt files will, due to an inconsistency
        # bug, use the module name instead.
        self.__node_prefix: str = self._ext_name
        _ = LOG.disabled or LOG.info(
            "Created base content manager for module %s (%s - %s) in extension %s at %s using cache %s",
            main_module.__name__,
            self.module_path,
            self.module_directory,
            ext_id,
            ext_path,
            self.cache_path,
        )

    # --------------------------------------------------------------------------------------------------------------
    def __str__(self) -> str:
        content = (
            f"EXT: {self._ext_name}, " f"MODULE: {self.module_name} @ {self.module_path}, " f"CACHE: {self.cache_path}"
        )
        if self.node_type_definitions:
            content += "\n    "
            content += "\n    ".join(str(definition) for definition in self.node_type_definitions.values())
        else:
            content += ", NO NODE TYPE DEFINITIONS"
        return content

    # --------------------------------------------------------------------------------------------------------------
    @property
    def ext_name(self) -> str:
        """Returns the name of the extension to which this object refers"""
        return self._ext_name

    # --------------------------------------------------------------------------------------------------------------
    @property
    def module_name(self) -> str:
        """Returns the name used by the import statement for this extension"""
        return self._module.__name__

    # --------------------------------------------------------------------------------------------------------------
    @property
    def config_dir(self) -> Path | None:
        """Returns the path to the configuration directory in the Kit build, or None if it could not be found"""
        if self.__config_dir is None:
            try:
                # Start looking at the symlinked dev directory, which is probably the right place
                kit_path = Path(carb.tokens.get_tokens_interface().resolve("${kit}")) / "dev"
                try:
                    ogn_build_directory = find_ogn_build_directory(kit_path)
                    if ogn_build_directory is None:
                        raise TypeError(f"Could not find build directory at {kit_path}")
                    config_dir = ogn_build_directory / "config"
                    if not config_dir.is_dir():
                        raise TypeError(f"'{config_dir}' is not a directory containing configuration information")
                    self.__config_dir = config_dir
                except TypeError as error:
                    carb.log_warn(f"Could not find configuration directory in the Kit build tree {kit_path} - {error}")

            except AttributeError:
                carb.log_warn("Could not resolve the Carbonite token '${kit}'")
        return self.__config_dir

    # --------------------------------------------------------------------------------------------------------------
    @property
    def categories(self) -> dict | None:
        """Returns the dictionary of CategoryName:Description for all known categories"""
        if self._categories is None and self.config_dir is not None:
            _ = LOG.disabled or LOG.info("Reading the default category list")
            try:
                self._categories = {}
                try:
                    category_file = self.config_dir / "CategoryConfiguration.json"
                    if not category_file.is_file():
                        raise TypeError(f"'{category_file}' is not a file containing category information")
                    _ = LOG.disabled or LOG.info("...Category file found in %s", category_file)
                except (AttributeError, TypeError) as error:
                    carb.log_warn(f"Could not find category file in the config dir {self.config_dir} - {error}")
                    return {}
                try:
                    with open(category_file, "r", encoding="utf-8") as cat_fd:
                        raw_categories = json.load(cat_fd)["categoryDefinitions"]
                    _ = LOG.disabled or LOG.info("...raw category list loaded with %d items", len(raw_categories))
                    self._categories = {
                        name: description for name, description in raw_categories.items() if not name.startswith("$")
                    }
                    _ = LOG.disabled or LOG.info("...after ignoring comments there are %d items", len(self._categories))
                except (json.JSONDecodeError, KeyError) as error:
                    carb.log_warn(f"Could not parse category file {category_file} - {error}")
            except AttributeError:
                carb.log_warn("Could not resolve the Carbonite token '${kit}'")
        return self._categories or {}

    # --------------------------------------------------------------------------------------------------------------
    @property
    def node_type_count(self) -> int:
        return len(self.node_type_definitions)

    # --------------------------------------------------------------------------------------------------------------
    @property
    def import_mode(self) -> ImportThreadingType:
        """Specifies the import strategy which will be applied when loading the python modules in this extension."""
        mode = self.ImportThreadingType.SingleThreaded
        config = load_extension_config(self._ext_path)
        if not config:
            return mode

        package_config = config["package"]
        python_config = package_config.get("python", None)
        if python_config:
            m = python_config.get("import_mode", None)
            mode = mode if m is None else self.ImportThreadingType[m]

        return mode

    # --------------------------------------------------------------------------------------------------------------
    def node_type_definition(self, node_type_name: str) -> NodeTypeDefinition | None:
        """Returns the node type definition associated with the node type name, or None if there is none"""
        return self.node_type_definitions.get(node_type_name, None)

    # --------------------------------------------------------------------------------------------------------------
    def ogn_module_names(self) -> tuple[str, str]:
        """Returns the names of the ogn and ogn/tests submodules for this extension.
        e.g. for the extension 'omni.sample' this should return ('omni.sample.ogn', 'omni.sample.ogn.tests')
        """
        return (f"{self.module_name}.ogn", f"{self.module_name}.ogn.tests")

    # --------------------------------------------------------------------------------------------------------------
    @carb.profiler.profile
    def scan_cache(self):
        """Walk the cache directory and add any cached files to the node type definitions"""
        if self.cache_path is None:
            _ = LOG.disabled or LOG.info("No existing cache path to scan")
            return
        if not self.cache_path.is_dir():
            _ = LOG.disabled or LOG.info("Cache path %s is not a directory", self.cache_path)
            return
        if not self.node_type_definitions:
            _ = LOG.disabled or LOG.info("No node type definitions to look up in the cache")
            return

        _ = LOG.disabled or LOG.info("Scanning the cache path %s", self.cache_path)

        scanner = CacheScanner(self, self.cache_path)
        scanner.run_processing()
        self._has_tests = self._has_tests or scanner.has_tests

    # --------------------------------------------------------------------------------------------------------------
    def get_out_of_date_definitions(self) -> dict[str, NodeTypeDefinition]:
        """Returns the subset of the node type definitions that are out of date against the current versions"""
        return {
            class_name: definition
            for class_name, definition in self.node_type_definitions.items()
            if definition.is_out_of_date(self._current_versions)
        }

    # --------------------------------------------------------------------------------------------------------------
    def ensure_files_up_to_date(self):
        """Find all of the files that are not currently up to date and regenerate new versions in the cache."""
        _ = LOG.disabled or LOG.info("Ensuring node types in extension %s are up to date", self._ext_name)

        needing_generation = self.get_out_of_date_definitions()
        if not needing_generation:
            return

        _ = LOG.disabled or LOG.info(
            "...%d node types out of date - regenerating into %s", len(needing_generation), self.cache_path
        )
        if self.cache_path is None:
            raise ValueError(f"Could not regenerate {len(needing_generation)} node type(s) - no valid cache path")

        # Create an empty __init__.py file to establish a location for importing the cache as a package
        init_path = self.cache_path / "__init__.py"
        init_path.parent.mkdir(exist_ok=True, parents=True)
        init_path.touch()

        def do_generate_definition(self: ExtensionContentsBase, definition: NodeTypeDefinition):
            """
            Generate the definition of a node type and store it in the cache.

            Args:
                self: The extension content object owning the definition cache.
                definition: The definition to generate.
            """
            _ = LOG.disabled or LOG.info("do_generate_definition %s-%s", self.module_name, definition.name)
            carb.profiler.begin(3, f"do_generate_definition {self.module_name}-{definition.name}")
            if definition.generate(
                self.cache_path, self.__node_prefix, self._module.__name__, self.config_dir, self.categories
            ):
                self._has_tests = True
            carb.profiler.end(3)

        futures: list = []
        with ThreadPoolExecutor() as executor:
            for definition in needing_generation.values():
                futures.append(executor.submit(do_generate_definition, self, definition))
        wait(futures, timeout=None, return_when=ALL_COMPLETED)

    # --------------------------------------------------------------------------------------------------------------
    @abc.abstractmethod
    def scan_for_nodes(self):
        """Look through the extension contents to find .ogn and related nodes, creating node type definitions for them.
        Each type of recognized directory will implement a customized scan that's efficient for its structure"""

    # --------------------------------------------------------------------------------------------------------------
    @abc.abstractmethod
    def ensure_required_modules_exist(self) -> tuple[ModuleType | None, ModuleType | None]:
        """Make sure the required OGN modules exist.

        The rules for defining the import module location and construction are a little complicated in
        order to account for various situations:
            1. the directory exists in the build tree and was already imported as a module
               The existing module is used for population
            2. the directory exists in the build tree but was not yet imported
               The existing directory is imported and then used for population
            3. the directory does not exist at all in the build tree
               A cache directory should exist, and it is imported and then used for population

        .ogn and .ogn.tests modules populate themselves from both the build tree and the cache tree according to which
        versions of generated files are the latest. No attention is paid to what is already there, if anything.

        Returns a tuple with the populated .ogn and .ogn.tests modules. If nothing was needed in the modules (e.g. no
        node definitions or no tests) then the module will be None.

        Raises OmniGraphExtensionError if anything that prevents proper registration happens
        """

    # --------------------------------------------------------------------------------------------------------------
    @abc.abstractmethod
    def do_python_imports(self):
        """Find or create the .ogn and .ogn.tests modules in the extension and import the required files into them"""
