"""
Support for managing the automatic creation and handling of an OGN-enabled extension.
This manages extensions outside of the build system, using Kit's automatic extension loading capabilities.

It explicitly does not handle running the generation scripts on .ogn files, though it does provide the directories
to which such generated files should be written.

The file structure of a newly created extension, beginning at the root of the extension looks like this:

    ROOT/
        my.cool.extension/
            config/
                extension.toml # (Generated) Information required to load the extension
            docs/
                README.md  # Description of your extension
            my/cool/extension/
                __init__.py # (Generated) Initialization of your extension
                nodes/
                    # Contains the .ogn and .py files implementing your OmniGraph nodes
                ogn/
                    __init__.py # (Generated) Registration of your OmniGraph nodes
                    docs/
                        # (Generated) Documentation describing your nodes
                    include/
                        # (Generated) C++ Database files, to make it easy for C++ nodes to access data
                    tests/
                        # (Generated) Test scripts that exercise your nodes
                        data/
                            # Copied test scenes that are employed in .ogn "tests" constructs.
                        usd/
                            # (Generated) Template USD file setting up the attributes in your nodes
                    python/
                        # (Generated) Python Database files, to make it easy for Python nodes to access data
"""

import os
import re
from pathlib import Path
from warnings import warn

from .utils import create_symbolic_link, dbg_reg


class OmniGraphExtension:  # pragma: no cover   Part of the obsolete node description editor
    """Class handling all of the requirements of an OGN-enabled extension

    Properties:
        ogn_docs_directory: Path to the directory containing user-written docs
        ogn_include_directory: Path to the directory containing .ogn-generated C++ header files
        ogn_nodes_directory: Path to the directory containing user-implemented nodes (.ogn and .py/.cpp)
        ogn_python_directory: Path to the directory containing .ogn-generated Python interface files
        ogn_tests_directory: Path to the directory containing .ogn-generated Python test scripts
        ogn_tests_data_directory: Path to the directory containing copied test scenes for use in .ogn "tests" constructs.
        ogn_usd_directory: Path to the directory containing .ogn-generated USD template files

    Internal:
        extension_root: Top level directory where the extension is defined
        python_directory: Directory in which the Python import root for this extension is found
        import_path: Import path for the Python root of this extension (e.g. omni.my.example)
                     Also used to determine the extension subdirectory
                     (e.g. $extension_root/omni.my.example/omni/my/example)
    """

    def __init__(self, extension_root: str, import_path: str):
        """Initialize the location information for an extension

        Args:
            extension_root: Root directory of the extension to be managed.
        """
        self._extension_root = extension_root
        self._import_path = import_path

        self.extension_directory = None
        self.python_directory = None
        self.ogn_docs_directory = None
        self.ogn_include_directory = None
        self.ogn_nodes_directory = None
        self.ogn_python_directory = None
        self.ogn_tests_directory = None
        self.ogn_tests_data_directory = None
        self.ogn_usd_directory = None
        self.extension_name = None

        self.rebuild_configuration()

    # ================================================================================
    def __str__(self):
        """Returns a string with the class's information nicely formatted"""
        return "\n".join(
            [
                f"Root = {self._extension_root}",
                f"Import = {self._import_path}",
                f"Directory = {self.extension_directory}",
                f"Python Directory = {self.python_directory}",
                f"Name = {self.extension_name}",
            ]
        )

    # ================================================================================
    def rebuild_configuration(self):
        """Reset all of the internal file paths and variables based on current configurations"""
        self.extension_directory = os.path.join(self._extension_root, self._import_path)
        self.python_directory = os.path.join(self.extension_directory, *self._import_path.split("."))
        # extension_name is an InterCaps version of the import_path, plus the word "Extension"
        # e.g. omni.my.example -> OmniMyExampleExtension
        self.extension_name = "".join(word.capitalize() for word in self._import_path.split(".")) + "Extension"

        self.ogn_nodes_directory = os.path.join(self.python_directory, "nodes")
        self.ogn_python_directory = os.path.join(self.python_directory, "ogn")
        self.ogn_docs_directory = os.path.join(self.ogn_python_directory, "docs")
        self.ogn_include_directory = os.path.join(self.ogn_python_directory, "include")
        self.ogn_tests_directory = os.path.join(self.ogn_python_directory, "tests")
        self.ogn_tests_data_directory = os.path.join(self.ogn_tests_directory, "data")
        self.ogn_usd_directory = os.path.join(self.ogn_tests_directory, "usd")

    # ================================================================================
    @property
    def import_path(self):
        """Returns the current value of the extension's import path"""
        return self._import_path

    @import_path.setter
    def import_path(self, new_import_path: str):
        """Sets the import path to the new location, updating all internal file paths and variables
        Note that if you call this all of your existing paths will be reconfigured to the default layout.

        Args:
            new_import_path: Python import path for the extension

        Raises:
            ValueError if new_import_path is not a valid path
        """
        if not self.validate_import_path(new_import_path):
            raise ValueError(
                "Import path must be a valid Python name with dot-separated components consisting of the uppercase"
                " and lowercase letters A through Z, the underscore _ and, except for the first character, the digits"
                f" 0 through 9. '{new_import_path}' does not satisfy that requirement."
            )

        self._import_path = new_import_path
        self.rebuild_configuration()

    @staticmethod
    def validate_import_path(import_path: str) -> bool:
        """Returns True iff the given import path has a legal name"""
        re_path_component_name = re.compile("^[_A-Za-z][_0-9A-Za-z]*$")

        return all(re_path_component_name.match(path_component) for path_component in import_path.split("."))

    # ================================================================================
    @property
    def extension_root(self):
        """Get the current value of the extension's root directory"""
        return self._extension_root

    @extension_root.setter
    def extension_root(self, new_root_directory: str):
        """Sets the root directory of the extension the new location, updating all internal file paths and variables
        Note that if you call this all of your existing paths will be reconfigured to the default layout.

        Args:
            new_root_directory: Root directory for the extension files
        """
        self._extension_root = new_root_directory
        self.rebuild_configuration()

    # ================================================================================
    def create_directory_tree(self):
        """Create all of the directories that comprise the OGN-enabled extension, including locations for new nodes"""
        os.makedirs(os.path.join(self.extension_directory, "config"), exist_ok=True)
        os.makedirs(os.path.join(self.extension_directory, "docs"), exist_ok=True)
        os.makedirs(self.ogn_docs_directory, exist_ok=True)
        os.makedirs(self.ogn_include_directory, exist_ok=True)
        os.makedirs(self.ogn_nodes_directory, exist_ok=True)
        os.makedirs(self.ogn_python_directory, exist_ok=True)
        os.makedirs(self.ogn_tests_directory, exist_ok=True)
        os.makedirs(self.ogn_tests_data_directory, exist_ok=True)
        os.makedirs(self.ogn_usd_directory, exist_ok=True)
        # Linking the nodes directory accomplishes the dual goals of keeping the generated and handwritten code
        # separated, while still encapsulating everything needed for OGN inside a single directory.
        try:
            create_symbolic_link(self.ogn_nodes_directory, os.path.join(self.ogn_python_directory, "nodes"))
        except Exception as error:  # pylint: disable=broad-except
            dbg_reg(f"Could not symlink to {self.ogn_nodes_directory}, will look for directory named 'nodes' - {error}")

    # ================================================================================
    def __remove_directory_contents(self, directory_path: str, file_pattern: str):
        """Remove the specified files in a directory

        Args:
            directory_path: Path to the directory from which to remove the files
            file_pattern: Regular expression string specifying which files are to be removed
        """
        file_matcher = re.compile(file_pattern)
        for file_to_check in os.listdir(directory_path):
            if file_matcher.match(file_to_check):
                try:
                    os.remove(os.path.join(directory_path, file_to_check))
                except Exception as error:  # pylint: disable=broad-except
                    dbg_reg(f"Could not remove generated file {file_to_check} from {directory_path} - {error}")

    # ================================================================================
    def remove_generated_files(self):
        """Delete all of the files under the extension that are automatically generated from a .ogn file"""
        self.__remove_directory_contents(self.ogn_python_directory, r".*\.py$")
        self.__remove_directory_contents(self.ogn_docs_directory, r".*\.rst$")
        self.__remove_directory_contents(self.ogn_include_directory, r".*\.h$")
        self.__remove_directory_contents(self.ogn_tests_directory, r".*\.py$")
        self.__remove_directory_contents(self.ogn_tests_data_directory, r".*\.usd$")
        self.__remove_directory_contents(self.ogn_tests_data_directory, r".*\.usda$")
        self.__remove_directory_contents(self.ogn_usd_directory, r".*\.usda$")

    # ================================================================================
    def write_extension_init(self, force: bool):
        """Writes out the extension's main __init__.py file, responsible for setting up the extension"""
        init_file_path = os.path.join(self.python_directory, "__init__.py")
        if not force and os.path.isfile(init_file_path):
            return
        try:
            with open(init_file_path, "w", newline="\n", encoding="utf-8") as init_fd:
                init_fd.write(
                    f"""
import omni.ext

# Any class derived from `omni.ext.IExt` in a top level module (defined in `python.modules` of `extension.toml`) will be
# instantiated when the extension is enabled and `on_startup(ext_id)` will be called. Later when extension gets disabled
# on_shutdown() will be called.
class {self.extension_name}(omni.ext.IExt):
    # ext_id is the current extension id. It can be used with the extension manager to query additional information,
    # such as where this extension is located in the filesystem.
    def on_startup(self, ext_id):
        print("[{self._import_path}] {self.extension_name} startup", flush=True)

    def on_shutdown(self):
        print("[{self._import_path}] {self.extension_name} shutdown", flush=True)
"""
                )
        except Exception as error:  # pylint: disable=broad-except
            warn(f"Could not write extension's init file {init_file_path} - {error}")

    # ================================================================================
    def write_ogn_init(self, force: bool):
        """Write out the OGN __init__.py file that registers all of the nodes in the ogn/ subdirectory"""
        try:
            init_file_path = Path(self.python_directory) / "ogn" / "__init__.py"
            if not force and init_file_path.is_file():
                return
            # The __init__.py file only needs to exist to properly initialize the module
            init_file_path.touch()
        except (TypeError, IOError) as error:
            warn(f"Could not write ogn's init file {init_file_path} - {error}")

    # ================================================================================
    def write_extension_toml(self, force: bool):
        """Write out the extension definition file, used for configuring it when the extension loads"""
        toml_file_path = os.path.join(self.extension_directory, "config", "extension.toml")
        if not force and os.path.isfile(toml_file_path):
            return
        try:
            with open(toml_file_path, "w", newline="\n", encoding="utf-8") as toml_fd:
                toml_fd.write(
                    f"""
[package]
# Semantic Versioning is used: https://semver.org/
version = "0.1.0"

# Lists people or organizations that are considered the "authors" of the package.
authors = []

# The title and description fields are primarly for displaying extension info in UI
title = "Omniverse Graph Extension Example"
description="Example extension for OmniGraph nodes."

# Path (relative to the root) or content of readme markdown file for UI.
readme  = "docs/README.md"

# URL of the extension source repository.
repository="https://gitlab-master.nvidia.com/omniverse/kit-extensions/example"

# Categories for UI.
category = "Example"

# Keywords for the extension
keywords = ["kit", "omnigraph"]

# Watch the .ogn files for hot reloading (only works for Python files)
[fswatcher.patterns]
include = ["*.ogn", "*.py"]
exclude = ["Ogn*Database.py"]

[dependencies]
"omni.kit.test" = {{}}
"omni.graph" = {{}}

# Main python module this extension provides, it will be publicly available as "import {self._import_path}".
[[python.module]]
name = "{self._import_path}"
"""
                )
        except Exception as error:  # pylint: disable=broad-except
            warn(f"Could not write extension's configuration file {toml_file_path} - {error}")

    # ================================================================================
    def write_readme(self, force: bool):
        """Write out the README.md file that the extension uses to identify itself in the extension window"""
        readme_path = os.path.join(self.extension_directory, "docs", "README.md")
        if not force and os.path.isfile(readme_path):
            return
        try:
            with open(readme_path, "w", newline="\n", encoding="utf-8") as readme_fd:
                readme_fd.write(
                    f"""
# OmniGraph Extension [{self._import_path}]
Extension with implementation of some OmniGraph nodes
"""
                )
        except Exception as error:  # pylint: disable=broad-except
            warn(f"Could not write extension's description file {readme_path} - {error}")

    # ================================================================================
    def write_all_files(self, force: bool = False):
        """Write all of the manually generated extension's files

        Args:
            force: If True then write out the files even if they already exist
        """
        self.write_extension_init(force)
        self.write_ogn_init(force)
        self.write_extension_toml(force)
        self.write_readme(force)
