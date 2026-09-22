"""Internal test utilities"""

from __future__ import annotations

import json
import sys
from contextlib import suppress
from pathlib import Path
from types import TracebackType
from typing import Any, List, Tuple

import omni.graph.tools._internal as ogi
import omni.graph.tools.ogn as ogn

# ==============================================================================================================
# Type of data to pass to the utilities when building a testing build or cache tree
BuildOgnTreeInfo_t = Tuple[ogi.GenerationVersions, ogn.LanguageTypeValues, List[ogi.FileType]]


# ==============================================================================================================
def _is_test_object(object_to_check: str) -> bool:
    return object_to_check != "scan_for_test_modules" and not object_to_check.startswith("test")


# ==============================================================================================================
def _check_module_api_consistency(module: object, ignored_extras: List[str] = None, is_test_module: bool = False):
    """Check the given module to make sure that its visible API matches the one it has published.

    Args:
        module: Module being tested (already imported)
        ignored_extras: List of known differences that can be ignored (e.g. the "tests" submodule)
        is_test_module: If True then the module is also allowed to contain the standard test definitions since they
                        must be public for the automated test registration to work.

    Raises:
        ValueError if the module API contents are not as expected - message in the exception indicates the discrepancy
    """
    objects_in_dir = [
        module_object
        for module_object in dir(module)
        if not module_object.startswith("_")
        and (ignored_extras is None or module_object not in ignored_extras)
        and (not is_test_module or _is_test_object(module_object))
    ]
    # For performance, sorting and comparing lists is 4x faster than converting both to sets and then comparing
    objects_in_dir.sort()
    with suppress(AttributeError):
        objects_in_all = module.__all__
        objects_in_all.sort()
        if objects_in_dir != objects_in_all:
            # Compute the set of objects that are in only one list to clarify what's reported
            in_dir_not_in_all = set(objects_in_dir) - set(objects_in_all)
            in_all_not_in_dir = set(objects_in_all) - set(objects_in_dir)
            msgs = []
            if in_dir_not_in_all:
                msgs.append(f"Objects in the dir() list {in_dir_not_in_all} not part of __all__")
            if in_all_not_in_dir:
                msgs.append(f"Objects in __all__ {in_all_not_in_dir} not part of the dir() list")
            raise ValueError(f"Module {module} error - {', '.join(msgs)}")


# ==============================================================================================================
def _check_public_api_contents(
    module: object, published: List[str], unpublished: List[str], only_expected_allowed: bool
):
    """Check the given module to make sure that the expected API objects are still publicly visible.

    Args:
        module: Module being tested (already imported)
        published: Names of the objects that should be publicly visible in the module
        unpublished: List of known visible objects that are not published and can be ignored (e.g. "tests" submodule)
        only_expected_allowed: If True then it is an error if objects other than the expected ones are publicly visible

    Raises:
        ValueError if the module API contents are not as expected - message in the exception indicates the discrepancy
    """
    with suppress(AttributeError):
        all_objects = module.__all__
        for expected_object in published:
            # Check to make sure the API object is exposed in the module
            if expected_object not in all_objects:
                raise ValueError(f"Expected API object '{expected_object}' not exposed in {module.__name__}.__all__")

            # Check to make sure the API object actually exists in the module
            if getattr(module, expected_object, None) is None:
                raise ValueError(f"Expected API object '{expected_object}' not a member of {module.__name__}")

        for unpublished_object in unpublished:
            # Check to make sure the unpublished object is really not published
            if unpublished_object in all_objects:
                raise ValueError(f"Unexpected API object '{unpublished_object}' exposed in {module.__name__}.__all__")

        # If the expected objects are the only ones allowed then confirm that no published or non-underscore object
        # exists in that module.
        if not only_expected_allowed:
            return

        for published_object in all_objects:
            if published_object not in published:
                raise ValueError(f"Published API object '{published_object}' not in expected list '{published}'")

        all_visible = published + unpublished
        visible_objects = [obj for obj in dir(module) if not obj.startswith("_")]
        # Use some magic to figure out if the module being tested is actually one of the test submodules, where
        # the actual tests can safely be ignored as they are required to be public for the automated test runner.
        if "scan_for_test_modules" in visible_objects:
            visible_objects = [module_object for module_object in visible_objects if _is_test_object(module_object)]
        for visible_object in visible_objects:
            if visible_object not in all_visible:
                raise ValueError(f"Visible API object '{visible_object}' not in expected list '{all_visible}'")


# ==============================================================================================================
class CreateHelper:
    """Helper class containing all of the functions that build temporary files for the OGN tree
    Attributes:
        __root: Path to the root of the tree where the generated code will live
        __ext_name: Name of the extension this tree belongs to
        __module_name: Name of the Python module this tree belongs to; usually the same as __ext_name
        __versions: Generation versions for any generated code
        __generated_code: The collection of generated code for nodes added to this tree
    """

    TEST_CLASS = "OgnTestNode"

    # --------------------------------------------------------------------------------------------------------------
    @staticmethod
    def safe_create(directory: Path, class_name: str | None, file_type: ogi.FileType | None, content: str) -> Path:
        """Create a new OGN-related file in the given location with the given type and contents.
        If class_name is None then the directory is assumed to be the full path name and file_type is ignored. A bit
        questionable but avoids two versions of this function.
        Raises AttributeError if the file could not be written, returns the new file path otherwise
        Returns the path to the newly created file
        """
        if class_name is None:
            file_path = directory
        else:
            file_path = directory / ogi.get_ogn_file_name(class_name, file_type)
        try:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, "w", encoding="utf-8") as fd:
                fd.write(content)
            return file_path
        except IOError as error:  # pragma: no cover
            raise AttributeError(f"Failed to write {class_name} file of type {file_type} to {directory}") from error

    # --------------------------------------------------------------------------------------------------------------
    def __init__(self, ext_name: str, root_path: Path, versions: ogi.GenerationVersions):
        self.__root = root_path
        self.__ext_name = ext_name
        self.__module_name = ext_name
        self.__versions = versions
        self.__generated_code = {}

    # --------------------------------------------------------------------------------------------------------------
    def _generate_code(
        self,
        class_name: str,
        exclusions: list[ogi.FileType] = None,
        language: str = "Python",
    ) -> dict[ogi.FileType, str]:
        """Creates an OGN definition and the code it will generate.
        Adds the set of generated code for the class type to the internal dictionary for later use.

        Args:
            class_name: Name of the class in the generated node type
            exclusions: List of file types excluded from generation
            language: Implementation language, usually Python for these tests
        Returns:
            A reference to the saved generated code for this class
        """
        if class_name in self.__generated_code:
            _ = ogi.LOG.disabled or ogi.LOG.info("Skipping generation of code for %s, it already exists", class_name)
            return self.__generated_code[class_name]
        _ = ogi.LOG.disabled or ogi.LOG.info("Generating code for %s with exclusions %s", class_name, exclusions)

        # Remember the .ogn definitions for use in the generation of sample code
        ogn_code = {
            class_name: {
                ogn.NodeTypeKeys.DESCRIPTION: "None",
                ogn.NodeTypeKeys.VERSION: 1,
                ogn.NodeTypeKeys.LANGUAGE: ogn.LanguageTypeValues.PYTHON,
            }
        }
        if exclusions is not None:
            ogn_code[class_name].update(
                {
                    ogn.NodeTypeKeys.EXCLUDE: [
                        ogi.GENERATED_FILE_CONFIG_NAMES[exclusion]
                        for exclusion in exclusions
                        if exclusion in ogi.GENERATED_FILE_CONFIG_NAMES
                    ],
                }
            )

        _ = ogi.LOG.disabled or ogi.LOG.info("Creating node for %s", class_name)

        # Start with the two user-driven files that will be matched with the generated code
        generated_code = {
            ogi.FileType.OGN: json.dumps(ogn_code, indent=4),
            ogi.FileType.PYTHON: f"""
class {class_name}:
    @staticmethod
    def compute(db) -> bool:
        return True
""",
        }

        # Run the code generator to get all of the results
        results = ogn.code_generation(
            ogn_code,
            class_name,
            self.__ext_name,
            self.__ext_name,
            generator_version_override=self.__versions[ogi.VersionProperties.GENERATOR],
            target_version_override=self.__versions[ogi.VersionProperties.TARGET],
        )
        for file_type, config_name in ogi.GENERATED_FILE_CONFIG_NAMES.items():
            if file_type not in (exclusions or []) and config_name in results:
                generated_code[file_type] = results[config_name]

        self.__generated_code.update({class_name: generated_code})
        return generated_code

    # --------------------------------------------------------------------------------------------------------------
    def create_ogn(
        self, class_name: str, language: str, relative_path: Path, exclusions: list[ogi.FileType] = None
    ) -> Path:
        _ = ogi.LOG.disabled or ogi.LOG.info("...Create OGN file for %s", class_name)
        my_code = self._generate_code(class_name, exclusions, language)
        return CreateHelper.safe_create(
            self.__root.joinpath(relative_path),
            class_name,
            ogi.FileType.OGN,
            my_code[ogi.FileType.OGN],
        )

    # --------------------------------------------------------------------------------------------------------------
    def create_cpp(self, class_name: str, file_path: Path) -> Path:
        _ = ogi.LOG.disabled or ogi.LOG.info("...Create CPP file for %s", class_name)
        my_code = self._generate_code(class_name)
        return CreateHelper.safe_create(
            self.__root.joinpath(file_path),
            class_name,
            ogi.FileType.CPP,
            my_code[ogi.FileType.CPP],
        )

    # --------------------------------------------------------------------------------------------------------------
    def create_cpp_database(self, class_name: str, file_path: Path) -> Path:
        _ = ogi.LOG.disabled or ogi.LOG.info("...Create CPP_DB file for %s", class_name)
        my_code = self._generate_code(class_name)
        return CreateHelper.safe_create(
            self.__root.joinpath(file_path),
            class_name,
            ogi.FileType.CPP_DB,
            my_code[ogi.FileType.CPP_DB],
        )

    # --------------------------------------------------------------------------------------------------------------
    def create_py_database(self, class_name: str, relative_path: Path) -> Path:
        _ = ogi.LOG.disabled or ogi.LOG.info("...Create PY_DB file for %s", class_name)
        my_code = self._generate_code(class_name)
        return CreateHelper.safe_create(
            self.__root.joinpath(relative_path),
            class_name,
            ogi.FileType.PYTHON_DB,
            my_code[ogi.FileType.PYTHON_DB],
        )

    # --------------------------------------------------------------------------------------------------------------
    def create_py(self, class_name: str, relative_path: Path) -> Path:
        _ = ogi.LOG.disabled or ogi.LOG.info("...Create PY file for %s", class_name)
        my_code = self._generate_code(class_name)
        return CreateHelper.safe_create(
            self.__root.joinpath(relative_path),
            class_name,
            ogi.FileType.PYTHON,
            my_code[ogi.FileType.PYTHON],
        )

    # --------------------------------------------------------------------------------------------------------------
    def create_docs(self, class_name: str, relative_path: Path) -> Path:
        _ = ogi.LOG.disabled or ogi.LOG.info("...Create DOCS file for %s", class_name)
        my_code = self._generate_code(class_name)
        return CreateHelper.safe_create(
            self.__root.joinpath(relative_path),
            class_name,
            ogi.FileType.DOCS,
            my_code[ogi.FileType.DOCS],
        )

    # --------------------------------------------------------------------------------------------------------------
    def create_tests(self, class_name: str, relative_path: Path) -> Path:
        _ = ogi.LOG.disabled or ogi.LOG.info("...Create TESTS file for %s", class_name)
        my_code = self._generate_code(class_name)
        return CreateHelper.safe_create(
            self.__root.joinpath(relative_path),
            class_name,
            ogi.FileType.TEST,
            my_code[ogi.FileType.TEST],
        )

    # --------------------------------------------------------------------------------------------------------------
    def create_usd(self, class_name: str, relative_path: Path) -> Path:
        _ = ogi.LOG.disabled or ogi.LOG.info("...Create USD file for %s", class_name)
        my_code = self._generate_code(class_name)
        return CreateHelper.safe_create(
            self.__root.joinpath(relative_path),
            class_name,
            ogi.FileType.USD,
            my_code[ogi.FileType.USD],
        )

    # --------------------------------------------------------------------------------------------------------------
    def _add_init_to_generated_tree(self, relative_module_root: Path) -> Path:
        """Adds the __init__.py file to the generated tree that is used for importing the node definitions
        Args:
            relative_module_root: Root directory of the node type's Python module relative to the main root
        Returns:
            Path to the created file
        """
        init_path = self.__root / relative_module_root / "__init__.py"
        with open(init_path, "w", encoding="utf-8") as init_fd:
            init_fd.write("# Placeholder for database imports\n")
            for database_file in relative_module_root.glob("*Database.py"):
                class_name = database_file.stem
                init_fd.write(f"from .{class_name} import {class_name}\n")
        return init_path

    # --------------------------------------------------------------------------------------------------------------
    def _add_test_init_file(self, ogn_root: Path) -> list[Path]:
        """Adds the __init__.py file to the generated tree that is used for importing the node definitions
        Args:
            ogn_root: Root directory of the node type's generated OGN definitions
        Returns:
            List containing the created file, or empty list if the file already existed
        """
        created_files = []
        test_init_file = ogn_root / "tests" / "__init__.py"
        if not test_init_file.is_file():
            created_files.append(
                CreateHelper.safe_create(
                    test_init_file,
                    None,
                    None,
                    """
import omni.graph.tools._internal as ogi
ogi.import_tests_in_directory(__file__, __name__)
""",
                )
            )
        return created_files

    # --------------------------------------------------------------------------------------------------------------
    def _add_node_type_to_tree(
        self,
        relative_root: Path,
        node_type_name: str,
        language: ogn.LanguageTypeValues,
        versions: ogi.GenerationVersions,
        tree_description: list[tuple[ogi.FileType, Path]],
        exclusions: list[ogi.FileType] = None,
    ) -> list[Path]:
        """Adds a node type file with the given configuration to the tree
        Args:
            relative_root: Top level directory of the simulated Python module build tree relative to the main root
            node_type_name: Name of the node type being constructed, also used as the class name
            language: Implementation language the .ogn file specifies
            versions: Target and generator versions for the constructed node type files
            tree_description: List of file type and relative path for all files to be constructed
            exclusions: List of file types that will not be constructed (and are added to the .ogn "exclusions" list)
        Returns:
            List of the paths to the files that were constructed
        """
        node_paths = []
        for file_type, relative_to_module in tree_description:
            if exclusions is not None and file_type in exclusions:
                continue
            relative_path = relative_root / relative_to_module
            try:
                if file_type == ogi.FileType.OGN:
                    node_paths.append(self.create_ogn(node_type_name, language, relative_path, exclusions))
                elif file_type == ogi.FileType.CPP_DB:
                    node_paths.append(self.create_cpp_database(node_type_name, relative_path))
                elif file_type == ogi.FileType.PYTHON_DB:
                    node_paths.append(self.create_py_database(node_type_name, relative_path))
                elif file_type == ogi.FileType.PYTHON:
                    node_paths.append(self.create_py(node_type_name, relative_path))
                elif file_type == ogi.FileType.CPP:
                    node_paths.append(self.create_cpp(node_type_name, relative_path))
                elif file_type == ogi.FileType.DOCS:
                    node_paths.append(self.create_docs(node_type_name, relative_path))
                elif file_type == ogi.FileType.TEST:
                    node_paths.append(self.create_tests(node_type_name, relative_path))
                elif file_type == ogi.FileType.USD:
                    node_paths.append(self.create_usd(node_type_name, relative_path))
                else:  # pragma: no cover
                    raise ValueError(f"Unrecognized type: {file_type} building {node_type_name}")
            except IOError as error:  # pragma: no cover
                raise IOError(f"Failed to create file type {file_type} on node {node_type_name}") from error

        _ = ogi.LOG.disabled or ogi.LOG.info("Built Tree with %s", node_paths)
        return node_paths

    # --------------------------------------------------------------------------------------------------------------
    def add_standalone_node(
        self,
        node_type_name: str,
        exclusions: list[ogi.FileType] = None,
    ) -> list[Path]:
        """Adds a set of node type files with the given configuration, without any generated files, to the root tree

        The structure of these directories looks like this:

            .../omni.my.extension/
                omni/
                    my/
                        extension/
                            nodes/
                                OgnMyNode.py
                                OgnMyNode.ogn

        Args:
            root: Top level directory of the simulated Python module build tree
            exclusions: List of file types that will not be constructed (and are added to the .ogn "exclusions" list)
        Returns:
            List of the paths to the files that were constructed
        """
        relative_module_root = Path(self.__ext_name) / self.__module_name.replace(".", "/")
        tree = [
            (ogi.FileType.OGN, "nodes"),
            (ogi.FileType.PYTHON, "nodes"),
        ]
        return self._add_node_type_to_tree(
            relative_module_root, node_type_name, ogn.LanguageTypeValues.PYTHON, self.__versions, tree, exclusions
        )

    # --------------------------------------------------------------------------------------------------------------
    def add_extension_module(
        self,
        ext_path: Path,
        ext_name: str,
        module_path: Path,
        import_ogn: bool,
        import_ogn_tests: bool,
    ):
        """Create the support files required for a local extension.
        The files will not be deleted by this class, their lifespan must be managed by the caller, e.g. through using
        a TempDirectory for their location.

        Files created will include:
            ext_path/
                config/
                    extension.toml
                my/
                    python/
                        module/
                            __init__.py

        Args:
            ext_path: Directory to contain the new extension
            ext_name: Name of the extension to create (e.g. 'omni.my.extension')
            import_ogn: Add a python module spec for the .ogn submodule in the extension.toml
            import_ogn_tests: Add a python module spec for the .ogn.tests submodule in the extension.toml
        Raises:
            AttributeError if there was a problem creating the extension configuration
        """
        _ = ogi.LOG.disabled or ogi.LOG.info(
            "Creating extension %s in %s using module %s", ext_name, ext_path, module_path
        )
        install_path: Path = Path(ext_path) / ext_name
        config_dir: Path = install_path / "config"
        created_files: list[Path] = []

        # Add any extras requested by the arguments
        extras = ""
        if import_ogn:
            extras += f"""[[python.module]]
name = "{ext_name}.ogn"
"""
        if import_ogn_tests:
            extras += f"""[[python.module]]
name = "{ext_name}.ogn.tests"
"""

        # Create a minimal extension.toml file that will set up the test extension for OmniGraph Python nodes
        created_files.append(
            CreateHelper.safe_create(
                config_dir / "extension.toml",
                None,
                None,
                f"""
[package]
version = "0.1.0"
title = "{ext_name}"

[fswatcher.patterns]
include = ["*.ogn", "*.py"]
exclude = ["Ogn*Database.py"]

[dependencies]
"omni.graph" = {{}}

# Main python module this extension provides, it will be publicly available as "import {ext_name}".
[[python.module]]
name = "{ext_name}"
{extras}""",
            )
        )

        # Create a minimal __init__.py file for the extension
        created_files.append(
            CreateHelper.safe_create(
                module_path / "__init__.py",
                None,
                None,
                f"""
import omni.ext

class _PublicExtension(omni.ext.IExt):
    def on_startup(self, ext_id):
        print("[{module_path.as_posix()}] {ext_name} startup", flush=True)

    def on_shutdown(self):
        print("[{module_path.as_posix()}] {ext_name} shutdown", flush=True)
""",
            )
        )

        return created_files

    # --------------------------------------------------------------------------------------------------------------
    def add_v1_18_node(
        self,
        node_type_name: str,
        exclusions: list[ogi.FileType] = None,
    ) -> list[Path]:
        """Adds a standard Python node, as it appears in omni.graph.tools V1.18, to the given root tree.
        Note that the ordering is such that it behaves as though the generation happened after the node creation, so the
        "generated" files are all newer than the implementation files.

        The structure of these directories looks like this:

            .../omni.my.extension/
                omni/
                    my/
                        extension/
                            ogn/
                                OgnMyNodeDatabase.py
                                nodes/
                                    OgnMyNode.ogn
                                    OgnMyNode.py
                                tests/
                                    __init__.py
                                    TestOgnMyNode.py
                                    usd/
                                        OgnMyNodeTemplate.usda

        Args:
            node_type_name: Name of the node type being constructed, also used as the class name
            exclusions: List of file types that will not be constructed (and are added to the .ogn "exclusions" list)
        Returns:
            List of the paths to the files that were constructed
        """
        _ = ogi.LOG.disabled or ogi.LOG.info(
            "Adding V1.18 node %s in extension %s at %s", node_type_name, self.__ext_name, self.__root
        )
        created_files = []
        relative_module_root = Path(self.__ext_name) / self.__module_name.replace(".", "/")
        tree = [
            (ogi.FileType.OGN, "ogn/nodes"),
            (ogi.FileType.PYTHON, "ogn/nodes"),
            (ogi.FileType.PYTHON_DB, "ogn"),
        ]
        if exclusions is None or ogi.FileType.TEST not in exclusions:
            tree.append((ogi.FileType.TEST, "ogn/tests"))
            created_files += self._add_test_init_file(self.__root / relative_module_root / "ogn")
        if exclusions is None or ogi.FileType.USD not in exclusions:
            tree.append((ogi.FileType.USD, "ogn/tests/usd"))
        created_files += self._add_node_type_to_tree(
            relative_module_root, node_type_name, ogn.LanguageTypeValues.PYTHON, self.__versions, tree, exclusions
        )
        return created_files

    # --------------------------------------------------------------------------------------------------------------
    def add_v1_19_node(
        self,
        node_type_name: str,
        exclusions: list[ogi.FileType] = None,
    ) -> list[Path]:
        """Adds a standard Python node, as it appears in omni.graph.tools V1.19 and higher, to the given root tree.
        Note that the ordering is such that it behaves as though the generation happened after the node creation, so the
        "generated" files are all newer than the implementation files. The docs file is omitted to give the caller
        something to test both for presence and omission.

        The structure of these directories looks like this:

            .../omni.my.extension/
                ogn/
                    generated/
                        __init__.py
                        ogn/
                            OgnMyNodeDatabase.py
                        tests/
                            TestOgnMyNode.py
                            usd/
                                OgnMyNodeTemplate.usda
                omni/
                    my/
                        extension/
                            OgnMyNode.ogn
                            OgnMyNode.py

        Args:
            node_type_name: Name of the node type being constructed, also used as the class name
            exclusions: List of file types that will not be constructed (and are added to the .ogn "exclusions" list)
        Returns:
            List of the paths to the files that were constructed
        """
        relative_module_root = Path(self.__ext_name) / self.__module_name.replace(".", "/")
        relative_generated_root = Path(self.__ext_name) / "ogn" / "generated"
        user_tree = [
            (ogi.FileType.OGN, "."),
            (ogi.FileType.PYTHON, "."),
        ]
        generated_tree = [
            (ogi.FileType.PYTHON_DB, "ogn"),
        ]
        if exclusions is None or ogi.FileType.TEST not in exclusions:
            generated_tree.append((ogi.FileType.TEST, "tests"))
        if exclusions is None or ogi.FileType.USD not in exclusions:
            generated_tree.append((ogi.FileType.USD, "tests/usd"))
        if exclusions is None or ogi.FileType.DOCS not in exclusions:
            generated_tree.append((ogi.FileType.DOCS, "docs"))
        files_added = self._add_node_type_to_tree(
            relative_module_root, node_type_name, ogn.LanguageTypeValues.PYTHON, self.__versions, user_tree, exclusions
        )
        files_added += self._add_node_type_to_tree(
            relative_generated_root,
            node_type_name,
            ogn.LanguageTypeValues.PYTHON,
            self.__versions,
            generated_tree,
            exclusions,
        )
        files_added.append(self._add_init_to_generated_tree(self.__root / relative_generated_root))
        print(files_added)
        return files_added

    # --------------------------------------------------------------------------------------------------------------
    def add_cache_for_node(
        self,
        node_type_name: str,
        exclusions: list[ogi.FileType] = None,
    ) -> list[Path]:
        """Adds a set of generated node type files with the given configuration as they would appear in the cache

        The structure of these directories looks like this:

            .../cache/ogn_generated/
                1.19.0/
                    omni.my.extension-0.1.0/
                        ogn/
                            __init__.py
                            OgnMyNodeDatabase.py
                            tests/
                                TestOgnMyNode.py
                                usd/
                                    OgnMyNodeTemplate.usd

        Args:
            node_type_name: Name of the node type being constructed, also used as the class name
            exclusions: List of file types that will not be constructed (and are added to the .ogn "exclusions" list)
        Returns:
            List of the paths to the files that were constructed
        """
        # Append the default extension ID version to the name to get a consistent path
        self.__root = ogi.full_cache_path(self.__versions, self.__ext_name + "-0.1.0", self.__module_name)
        old_root = self.__root
        tree = [(ogi.FileType.PYTHON_DB, ".")]
        files_added = []
        try:
            if exclusions is None or ogi.FileType.TEST not in exclusions:
                tree.append((ogi.FileType.TEST, "tests"))
                files_added += self._add_test_init_file(self.__root)
            if exclusions is None or ogi.FileType.DOCS not in exclusions:
                tree.append((ogi.FileType.DOCS, "docs"))
            if exclusions is None or ogi.FileType.DOCS not in exclusions:
                tree.append((ogi.FileType.USD, "tests/usd"))
            files_added += self._add_node_type_to_tree(
                Path("."), node_type_name, ogn.LanguageTypeValues.PYTHON, self.__versions, tree, exclusions
            )
            files_added.append(self._add_init_to_generated_tree(Path(".")))
        finally:
            self.__root = old_root
        return files_added


# ==============================================================================================================
class TemporaryPathAddition:
    """Context manager to temporarily add extra locations to the sys import path.
    with TemporaryPathAddition(new_path_location):
        do_import_from_new_path()
    """

    def __init__(self, new_location: Path | str):
        self.__new_location = str(new_location)

    def __enter__(self):
        sys.path.append(self.__new_location)
        return self.__new_location

    def __exit__(self, exit_type: Any, value: Any, traceback: TracebackType):
        with suppress(ValueError):
            sys.path.remove(self.__new_location)
        self.__new_location = None
