"""Support for generating an icon file representing a node type in the build directory."""

import shutil
from pathlib import Path
from typing import Optional

from .nodes import NodeInterfaceGenerator
from .utils import GeneratorConfiguration, ParseError, ensure_writable_directory, logger

__all__ = ["generate_icon"]


class NodeIconGenerator(NodeInterfaceGenerator):
    """Manage the functions required to install a representative icon for a node type"""

    def __init__(self, configuration: GeneratorConfiguration):  # noqa: PLW0246
        """Set up the generator to get ready to copy the icon file

        Just passes the initialization on to the parent class. See the argument and exception descriptions there.
        """
        super().__init__(configuration)

    # ----------------------------------------------------------------------
    def interface_file_name(self) -> str:
        """Return the path to the name of the node icon file"""
        return f"{self.node_interface.name}.svg"

    # ----------------------------------------------------------------------
    def generate_node_interface(self):
        """Copy the icon for the node type from the specified location, if it exists, to the destination
        The output stream will contain the path to the final destination file.

        These are the possibilities for finding the icon:
            1. Path explicitly specified in the .ogn
            2. No path specified, but .svg file lives alongside the .ogn file
            3. No path or .svg file exists
        """
        # This ensures the file is not overwritten by the base class after returning as it is being used to
        # contain the copied icon file.
        output_path = Path(self.output_path) if self.output_path is not None else None
        self.output_path = None

        if self.node_interface.icon_path is None:
            # If there was no icon specified check to see if there's a .svg file of the same base name with the .ogn
            if self.node_file_path is None:
                return
            potential_path = Path(self.node_file_path.replace(".ogn", ".svg"))
            if not potential_path.is_file():
                return
        else:
            # Find the absolute location of the icon file for copying
            potential_path = Path(self.node_interface.icon_path)
            if not potential_path.is_absolute():
                if self.node_file_path is None:
                    raise ParseError(f"Specified relative icon path {potential_path} but there is no .ogn path")
                potential_path = Path(self.node_file_path).parent / potential_path
            if not potential_path.is_file():
                raise ParseError(f"Icon path {potential_path} does not exist")

        # Non-icon files should not be copied
        if potential_path.suffix != ".svg":
            raise ParseError(f"Node icon path must be an SVG file. '{potential_path}' not allowed")

        # If there is an icon file and no place to put it then the actual file contents should be returned, not the path
        if output_path is None:
            with open(potential_path, "r", encoding="utf-8") as icon_fd:
                self.out.write(icon_fd.readlines())
        else:
            # Write the file name to the output so that the generator can pick it up
            self.out.write(str(output_path))

            # Copy the file from the source location to the output path
            try:
                ensure_writable_directory(output_path.parent)
                shutil.copy(potential_path, output_path)
            except Exception as error:
                raise ParseError("Failed to copy node icon file") from error


# ======================================================================
def generate_icon(configuration: GeneratorConfiguration) -> Optional[str]:
    """Create support files for the icons defined within the node

    Args:
        configuration: Information defining how and where the documentation will be generated

    Returns:
        Relative path of the icon file if it existed and was successfully installed, else None

    Raises:
        NodeGenerationError: When there is a failure in the generation of the icon files
    """
    if not configuration.node_interface.can_generate("icon"):
        return None
    logger.info("Generating icon")
    needed_directory = configuration.needs_directory

    configuration.needs_directory = False
    generator = NodeIconGenerator(configuration)
    generator.generate_interface()

    configuration.needs_directory = needed_directory

    icon_path = str(generator.out).rstrip()
    return icon_path if icon_path else None
