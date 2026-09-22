"""
This script generates the set of [[native.library]] blocks in the omni.usd.libs
extension that loads the appropriate base dlls from OpenUSD and its dependencies.
In order to support different versions of OpenUSD flexibly, this script
will look into the OpenUSD runtime directories to find the names of all libraries
and use those to generate the [[native.library]] blocks.  This is done generically
because the specific set of libraries included with each OpenUSD version varies
widely depending on the version and the dependency list, and keeping a map of those
is cumbersome and hard to keep up to date with each OpenUSD release.
"""
import argparse
import logging
import os
import subprocess
import sys

from string import Template
from typing import List, Dict

class LibraryNode:
    """
    Represents a tree node for a type in a dependency tree.
    """
    def __init__(self, library_name : str):
        """
        Initializes a new instance.

        Args:
            library_name: A string representing the name of the library
                          held by the node.
        """
        self._library_name = library_name
        self._dependencies = []

    @property
    def library_name(self) -> str:
        """
        Retrieves the name of the library held by the node.
        """
        return self._library_name

    @property
    def dependencies(self) -> List['LibraryNode']:
        """
        Retrieves the library nodes containing libraries that
        are dependencies for this library.
        """
        return self._dependencies

def walk_library(node : LibraryNode,
    seen_libraries : List[str]):
    """
    """
    # if we've already seen this library we don't need to process it again
    if node.library_name not in seen_libraries:
        for dependency in node.dependencies:
            walk_library(dependency, seen_libraries)

        # add this one
        seen_libraries.append(node.library_name)

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--usd_root",
        type=str,
        help="Absolute path to the root of the USD installation to use.")
    parser.add_argument("--config",
        type=str,
        help="Configuration the extension.toml file is being generated for.")
    parser.add_argument("--output",
        type=str,
        help="Output directory for extension.toml.")

    logger = logging.getLogger("omni.usd.libs")
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

    args = parser.parse_args()
    usd_root = args.usd_root
    target_dir_location = args.output
    config = args.config

    # to be flexible to the OpenUSD build, this script will look in the
    # following locations for libraries ending in .dll / .so
    # - lib (primary location of OpenUSD, boost, OpenEXR libraries)
    # - bin (typical location of MaterialX, tbb libraries)
    # - lib64 (on linux, typical location of ILM, OpenImageIO libraries)
    search_paths = [
        "lib",
        "bin",
        "lib64"
    ]

    native_libraries = []
    native_library_paths = []
    native_library_block = ""
    for search_path in search_paths:
        relative_path = os.path.join(usd_root, search_path).replace("\\", "/")
        if os.path.exists(relative_path):
            for file in os.listdir(relative_path):
                # something between 22.11 and 24.05 changed the ordering in
                # which NDR gets loaded in such a way that if `tf` isn't loaded
                # early NDR won't get populated correctly - this seems to be
                # a runtime initialization order, not a dll load order as dependencies
                # are resolved out of the same directory on windows with the right flags
                # which carb uses - to solve this for now we just move tf to the front
                if file.endswith("tf.dll"):
                    native_library_paths.insert(0, os.path.join(relative_path, file).replace("\\", "/"))
                    native_libraries.insert(0, file)
                    pre_block = "[[native.library]]\n"
                    pre_block += 'path = "bin/' + file + '"\n\n'
                    native_library_block = pre_block + native_library_block
                    continue

                # tbbbind needs libhwloc, which isn't in this bin
                # additionally, in some USD packages python is included
                # but we shouldn't load that here because it isn't copied
                if (file.endswith(".dll") or file.endswith(".so")) and \
                "usdviewq" not in file and \
                "boost_iostreams" not in file and \
                "tbbbind" not in file and \
                not file.startswith("python"):
                    if "_debug" in file and config == "release":
                        continue

                    native_library_paths.append(os.path.join(relative_path, file).replace("\\", "/"))
                    native_libraries.append(file)
                    native_library_block += "[[native.library]]\n"
                    native_library_block += 'path = "bin/' + file + '"\n\n'

    if len(native_library_paths) and native_library_paths[0].endswith(".so"):
        # in order for the libraries on Linux to load correctly, the load order needs
        # to be set properly because we can't control RPATH in some cases
        # so attempt to determine a dependency ordering based on some heuristics
        # from ldd
        library_name_to_node_map = {}
        for native_library in native_library_paths:
            ldd_command_line = [
                "ldd",
                native_library
            ]

            # create a library node for this library
            # then use 'ldd' to find its dependencies
            library_name = os.path.basename(native_library)
            if library_name not in library_name_to_node_map:
                library_name_to_node_map[library_name] = LibraryNode(library_name)

            completed_process = subprocess.run(ldd_command_line,
                capture_output=True)
            if completed_process.returncode == 0:
                lines = completed_process.stdout.decode().split("\n")

                # two possibilities for the line formats
                # libname (address)
                # libname => path (address)
                for line in lines:
                    if len(line) > 0:
                        if "=>" in line:
                            line = line[0:line.find("=>")].strip()
                        else:
                            line = line[0:line.find("(")].strip()

                        if not line.endswith(".so"):
                            line = line[0:line.find(".so") + 3]

                        if line in native_libraries:
                            # this is a library we care about because
                            # it's one of the libraries we are processing
                            # so add it as a dependency
                            if line not in library_name_to_node_map:
                                library_name_to_node_map[line] = LibraryNode(line)

                            library_name_to_node_map[library_name].dependencies.append(
                                library_name_to_node_map[line])

        # now we have a list of all libraries and their dependencies
        # we need to walk the list to output the native libraries in the right
        # order to load for linux
        native_library_block = ""
        seen_libraries = []
        for library_name in library_name_to_node_map:
            walk_library(library_name_to_node_map[library_name], seen_libraries)

        for seen_library in seen_libraries:
            native_library_block += "[[native.library]]\n"
            native_library_block += 'path = "bin/' + seen_library + '"\n\n'

    # copy the file over to the extension config directory
    file_location = os.path.abspath(__file__)
    source_file_location = os.path.join(os.path.dirname(file_location), "..", "template", "extension.toml")
    target_file_location = os.path.join(target_dir_location, "extension.toml")

    # Previous build may have a linked directory, so try os.remove and allow FileNotFoundError
    # This can likely be removed after some amount of time where only the directory created below would exist.
    try:
        os.remove(target_dir_location)
    except (FileNotFoundError, PermissionError, IsADirectoryError):
        pass

    # Create the parent /config directory in the build output
    # #
    try:
        os.mkdir(target_dir_location)
    except FileExistsError:
        pass

    # read the template contents
    try:
        with open(source_file_location, "r") as source_file:
            content = source_file.read()
    except Exception as e:
        logger.error(f"Could not open template file at {source_file_location}: {e}")
        exit(1)

    # replace the placeholder
    tokens_to_resolve = {
        'native_library_block': native_library_block
    }

    try:
        template = Template(content)
        content = template.safe_substitute(tokens_to_resolve)
    except Exception as e:
        logger.error(f"Template substituion failed: {e}")
        exit(1)

    # write the actual configuration
    try:
        if not os.path.exists(target_dir_location):
            os.mkdir(target_dir_location)
        logger.debug(f"Writing target extension.toml file to {target_file_location}")
        with open(target_file_location, "w") as target_file:
            target_file.write(content)
    except Exception as e:
        logger.error(f"Could not create target extension.toml file at {target_file_location}: {e}")
        exit(1)

    exit(0)
