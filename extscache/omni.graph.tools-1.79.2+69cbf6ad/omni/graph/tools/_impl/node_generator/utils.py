# noqa: PLC0302
# pylint: disable=broad-exception-raised
"""Common constants, methods, and classes used by the various sections of the node generator.
These were split out into a separate file to avoid circular inclusions.
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import locale
import logging
import os
import re
import subprocess
import sys
from functools import partial
from pathlib import Path
from typing import IO, Any, Dict, List, Optional, Tuple, Union

# Support for deprecated location of these types
from .keys import IconKeys  # noqa
from .keys import MemoryTypeValues  # noqa
from .keys import MetadataKeyOutput  # noqa
from .keys import MetadataKeys  # noqa

# ======================================================================
# Environment variable gating display and execution of parse debugging information
# The parsing debugging is turned on in any one of these situations:
#   OGN_DEBUG=1
#   OGN_DEBUG.contains("parse")
#   OGN_PARSE_DEBUG=1
env_var = os.getenv("OGN_DEBUG")
has_debugging = env_var is not None
OGN_PARSE_DEBUG = (
    has_debugging
    and (env_var == "1" or env_var.lower().find("parse") >= 0)
    or (os.getenv("OGN_PARSE_DEBUG") is not None)
)
OGN_REG_DEBUG = (
    has_debugging and (env_var == "1" or env_var.lower().find("reg") >= 0) or (os.getenv("OGN_REG_DEBUG") is not None)
)


# ======================================================================
def __dbg(gate: bool, message: str, *args, **kwargs):  # pragma: no cover  Debugging only
    """
    Print out a debugging message if the gate_variable is enabled, additional args will be passed
    to format the given message.
    """
    if gate:
        if args or kwargs:
            print("DBG: " + message.format(*args, **kwargs), flush=True)
        else:
            print(f"DBG: {message}", flush=True)


dbg_parse = partial(__dbg, OGN_PARSE_DEBUG)
dbg_reg = partial(__dbg, OGN_REG_DEBUG)


# Color type that can be either a hex string or an RGBA tuple
ColorType = Union[str, Tuple[int, int, int, int]]


# Constant defining the name of the OmniGraph core extension, since some code needs to generate differently for it
OMNI_GRAPH_CORE_EXTENSION = "omni.graph.core"


# Special file inserted into a a generated ogn/ directory to tag it as not requiring runtime regeneration
UNWRITABLE_TAG_FILE = "__ogn_files_prebuilt"
# Legacy file name that causes part of the packaging process to breakdown due to the leading dot
__OLD_UNWRITABLE_TAG_FILE = ".ogn_files_prebuilt"


# Deprecated - use keys.MemoryTypeValues instead
MEMORY_TYPE_CPU = MemoryTypeValues.CPU
MEMORY_TYPE_CUDA = MemoryTypeValues.CUDA
MEMORY_TYPE_ANY = MemoryTypeValues.ANY
ALL_MEMORY_TYPES = MemoryTypeValues.ALL
CPP_MEMORY_TYPES = MemoryTypeValues.CPP


# Pattern for legal token names
# - starts with a letter or underscore
# - then an arbitrary number of alphanumerics or underscores
# - other special characters cause problems in the generated code and so are disallowed
RE_TOKEN_NAME = re.compile(r"^[A-Za-z_][A-Za-z0-9_,]*$")
TOKEN_NAME_REQUIREMENT = (
    "Token name '{}' should be CamelCase with letters, numbers, underscores."
    " Tokens with special characters should use a dictionary rather than a list, where the key is the name."
)


# Enum values corresponding to extended attribute types (to avoid relying on omni.graph.core)
_EXTENDED_TYPE_REGULAR = 0
_EXTENDED_TYPE_UNION = 1
_EXTENDED_TYPE_ANY = 2


# Global logger avoids multiple loggers clashing with each other or duplicating output
logger = None


# ======================================================================
def global_logger():
    """Global status logger for the node generator.

    Delay initialization so that it can be set up from the main function as well as scripts that import this one.

    Returns:
        A logging.Logger instance that will be shared by all scripts used for node generation
    """
    global logger
    if logger is None:
        logger = logging.getLogger("generate_node")
        if not logger.handlers:
            logging_handler = logging.StreamHandler(sys.stdout)
            logging_handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
            logger.addHandler(logging_handler)
        logger.setLevel(logging.INFO if OGN_PARSE_DEBUG else logging.ERROR)
    return logger


# Bootstrap initialization of the global variable
global_logger()


# ================================================================================
class CarbLogError(Exception):
    """Exception to raise when there is an error that requires logging"""


# ================================================================================
class DebugError(Exception):
    """Exception to raise when there is an error that requires a debug message but no specific action"""


# ======================================================================
class ParseError(Exception):
    """Exception to raise when there is an error in the parsing of the node interface description"""


# ======================================================================
class UnimplementedError(Exception):
    """Custom exception to raise when attempting to access unimplemented functionality"""


# ======================================================================
class Settings:
    """Manage the build settings that can be used for tuning the code generation. The settings are all available
    as properties on the class.

    Add any new settings with their default and description in the __init__ method. New settings should also be
    reflected in the omni.graph.core/plugins/OmniGraphSettings.h file.

    The only name not allowed is "all" as that is used to return the list of all available settings.
    Defining slots allows interception of attempts to get/set unknown settings with an AttributeError.
    """

    __slots__ = ["__settings"]

    def __init__(self):
        """Initialize the list of available settings and their defaults."""
        self.__settings = {
            "pyOptimize": (False, "When generating Python nodes use a more optimized approach"),
        }
        for setting_name in self.__settings:
            self.__slots__.append(setting_name)

        for setting_name, (default_value, description) in self.__settings.items():

            def _get(self, _default=default_value) -> bool:
                return _default

            def _set(self, setting_value, _name=setting_name, _description=description):
                self.__settings[_name] = (setting_value, _description)

            setattr(Settings, setting_name, property(_get, _set))

    def __str__(self) -> str:
        """Returns a string containing the list of allowed settings"""
        return ", ".join(list(self.__settings.keys()))

    def all(self) -> Dict[str, Tuple[Any, str]]:  # noqa: A003
        """Return a dictionary of all known settings mapped onto (DEFAULT, DESCRIPTION)"""
        return self.__settings

    @staticmethod
    def generator_settings() -> Settings:
        """Return the generator settings object corresponding to the current carb settings"""
        settings = Settings()
        try:
            import carb

            carb_settings = carb.settings.get_settings()
            for setting_name in settings.all():
                if carb_settings.get(f"/persistent/omnigraph/generator/{setting_name}"):
                    setattr(settings, setting_name, True)
        except ImportError:  # pragma: no cover   Firewall
            logger.warning("Could not access Carbonite setttings - assuming all defaults")

        return settings


# ======================================================================
class GeneratorConfiguration:
    """Storage class containing common information used by the generators.

    Mostly created to avoid passing long argument lists around.

    Properties:
        base_name: Name of the .ogn file with directory and extension stripped away
        destination_directory: Directory for the generated code
        extension: Name of the extension running the generation
        generator_version: Version identification for this extension to embed in generated code
        module: Python module in which the generated Python files will live
        needs_directory: Destination will be ensured to exist before running the generator
        node_file_path: Location of the .ogn file used to generate the code
        node_interface: Node interface class to be processed
        target_version: Identification for the version of the omni.graph.core extension for which code was generated
        verbose: True if extra debugging information is to be output
        settings: List of settings that were enabled as part of the build
        generator_version_override: Generator version to use instead of the one extracted from omni.graph.tools
        target_version_override: Target version to use instead of the one extracted from omni.graph.core
    """

    def __init__(
        self,
        node_file_path: str,
        node_interface,
        extension: str,
        module: str,
        base_name: str,
        destination_directory: Optional[str],
        verbose: bool = False,
        settings: Optional[Settings] = None,
        generator_version_override: Optional[Tuple[int, int, int]] = None,
        target_version_override: Optional[Tuple[int, int, int]] = None,
    ):
        """Collect the data members into the structure"""
        self.node_file_path = node_file_path.replace("\\", "/") if node_file_path else None  # Standardize the separator
        self.node_interface = node_interface
        self.extension = extension
        self.module = module
        self.base_name = base_name
        self.destination_directory = destination_directory
        self.needs_directory = True
        self.verbose = verbose
        self.settings = settings or Settings()

        # It would have been nicer to use the toml package here but it's not available to the build script, and
        # finding the version is trivial anyway.
        tools_extension_root = Path(__file__).parent.parent.parent.parent.parent.parent
        if generator_version_override is None:
            self.generator_version = (0, 0, 0)
            re_version = re.compile('version = "(.*)"')
            toml_path = tools_extension_root / "config" / "extension.toml"
            if not toml_path.is_file():
                raise ParseError(f"Could not find generator file containing the version information '{toml_path}'")
            with open(toml_path, "r", encoding="utf-8") as toml_fd:
                for line in toml_fd:
                    match = re_version.match(line)
                    if match:
                        self.generator_version = tuple(
                            int(version) for version in f"{match.group(1)}.0.0.0".split(".")[0:3]
                        )
                        break
        else:
            self.generator_version = generator_version_override

        # There is no dependency from tools to the OmniGraph core but for now they always appear in the same build
        # tree so rely on that fact to find the configuration information.
        if target_version_override is None:
            self.target_version = (0, 0, 0)
            # The path may have extra information in it such as version, SHA1, or platform, so use a pattern
            core_toml_path = None
            for core_dir in tools_extension_root.parent.rglob("omni.graph.core*"):
                core_toml_path = core_dir / "config" / "extension.toml"
                # There should only be one, but break on the first one found anyway
                if core_toml_path.is_file():
                    break
            # Do not fail if a file wasn't found, but issue a warning and use the default values
            if core_toml_path is not None and core_toml_path.is_file():
                with open(core_toml_path, "r", encoding="utf-8") as toml_fd:
                    for line in toml_fd:
                        match = re_version.match(line)
                        if match:
                            self.target_version = tuple(
                                int(version) for version in f"{match.group(1)}.0.0.0".split(".")[0:3]
                            )
                            break
            else:  # pragma: no cover   Firewall
                logger.warning("Failed to find the target looking at %s, using default", tools_extension_root.parent)
        else:
            self.target_version = target_version_override

    # --------------------------------------------------------------------------------------------------------------
    def __str__(self):
        """Convert the configuration to a string for debugging - one property per line"""
        return f"""generator_version = {self.generator_version}
node_file_path    = {self.node_file_path}
node_interface    = {self.node_interface}
extension         = {self.extension}
module            = {self.module}
base_name         = {self.base_name}
directory         = {self.destination_directory}
target_version    = {self.target_version}
verbose           = {self.verbose}"""


# ======================================================================
class IndentedOutput:
    """Helper class that provides output capabilities to messages with preserved indentation levels

    Properties:
        output: File type that receives the output
        indent_level: Number of indentation levels for the current output
        indent_string: String representing the current indentation level
    """

    def __init__(self, output: IO):
        """Initialize the indentation level and prepare for output

        Args:
            output: IO object to which this object will be sending its output
                    Both io.TextIOWrapper (output from "open()") and io.StringIO can be used
        """
        self.output = output
        self.indent_level = 0
        self.indent_string = ""

    # ----------------------------------------------------------------------
    def indent(self, message: str = None) -> bool:
        """Increase the indentation level for emitted code

        If a message is specified then emit that message immediately before indenting,
        allowing you to easily open sections like: out.indent("{")

        Returns True so that indented sections can be indented in the code:
            if output.indent("begin {"):
                output.exdent("})
        """
        if message is not None:
            self.write(message)
        self.indent_level += 1
        self.indent_string = "    " * self.indent_level
        return True

    # ----------------------------------------------------------------------
    def exdent(self, message: str = None):
        """Decrease the indentation level for emitted code

        If a message is specified then emit that message immediately after exdenting,
        allowing you to easily close sections like: out.exdent("}")
        """
        assert self.indent_level > 0
        self.indent_level -= 1
        self.indent_string = "    " * self.indent_level
        if message is not None:
            self.write(message)

    # ----------------------------------------------------------------------
    def __str__(self):
        """Return the accumulated string saved when there is no file to write, or the file path if there was"""
        if isinstance(self.output, io.StringIO):
            return self.output.getvalue()
        return self.output.name

    # ----------------------------------------------------------------------
    def close(self):
        """Close the output stream"""
        self.output.close()

    # ----------------------------------------------------------------------
    def prepend(self, message: str):
        """Write the message line at the beginning of the output.

        This rewrites the entire output so it is best to minimize its use, and stick with string implementations.
        The message is written as-is with no newlines or indenting
        """
        if isinstance(self.output, io.StringIO):
            current_output = self.output.getvalue()
            self.output = io.StringIO()
            self.output.write(message)
            self.output.write(current_output)
        else:
            filename = self.output.name
            self.output = open(filename, "r+", newline="\n", encoding="utf-8")  # noqa: SIM115,PLR1732
            content = self.output.read()
            self.output.seek(0, 0)
            self.output.write(message + content)

    # ----------------------------------------------------------------------
    def write(self, message: Union[List, str] = ""):
        """Output a single message line to the file.
        This assumes indentation will be used and a newline will be appended.
        Passing in a list will write each list member on its own line.

        Args:
            message: Line of text being emitted
        """
        if not message:
            self.output.write("\n")
        elif isinstance(message, list):
            for line in message:
                self.write(line)
        else:
            self.output.write(f"{self.indent_string}{message}\n")

    # ----------------------------------------------------------------------
    def write_as_is(self, message: Union[List, str]):
        """Output a string to the output file without indentation or added newline
        Passing in a list will write each list member on its own line.

        Args:
            message: Line of text being emitted
        """
        if isinstance(message, list):
            for line in message:
                self.write_as_is(line)
        elif message:
            self.output.write(f"{message}")


# ======================================================================
def is_comment(keyword: str) -> bool:
    """Returns True if the keyword matches the specially reserved pattern for comments, the leading '$'"""
    return keyword[0] == "$" if keyword else False


# ======================================================================
def is_unwritable(generated_directory: str) -> bool:
    """Returns True if the OGN generated directory is tagged as unwritable (i.e. part of a build) or if it is
    physically unwritable.
    """
    unwritable_tag = os.path.join(generated_directory, UNWRITABLE_TAG_FILE)
    old_unwritable_tag = os.path.join(generated_directory, __OLD_UNWRITABLE_TAG_FILE)
    if os.path.isfile(unwritable_tag) or os.path.isfile(old_unwritable_tag):
        return True

    # The directory is not tagged as unwritable, now check to see if it is physically unwritable.
    try:
        # Attempting to write a temp file is the only reliable way to detect unwritable directories on Windows
        test_path = Path(generated_directory) / "__test_file__"
        with open(test_path, "w", encoding="utf-8"):
            pass
        test_path.unlink()
    except OSError:  # pragma: no cover   Firewall
        # error.errno == errno.EACCES or error.errno == errno.EEXIST
        return True

    return False


# ======================================================================
def ensure_quoted(value: str) -> str:
    """Returns the value in quotes if it wasn't already quoted, or just itself if it was"""
    if len(value) > 1 and ((value[0] == "'" and value[-1] == "'") or (value[0] == '"' and value[-1] == '"')):
        return value
    value_escaped = value.replace('"', '\\"')
    return f'"{value_escaped}"'


# ======================================================================
def shorten_string_lines_to(full_string: str, suggested_limit: int) -> List[str]:
    """Convert a single long line into a list of shorter lines

    Args:
        full_string: Single line to be trimmed
        suggested_limit: Minimum length of line; line will extend to the next space past this limit
    """
    shortened_strings = []
    while len(full_string) > suggested_limit:
        next_space = full_string.find(" ", suggested_limit)
        if next_space > 0:
            shortened_strings.append(full_string[0:next_space])
            full_string = full_string[next_space + 1 :]
        else:
            break
    shortened_strings.append(full_string)
    return shortened_strings


# ======================================================================
def attrib_description_to_string(description):
    """Convert convert to string if the input has a List type"""
    description_list = description if isinstance(description, List) else [description]
    return "\n".join(description_list)


# ======================================================================
def to_cpp_str(raw: Union[str, List[str]], separator: str = " "):
    """Convert a string or list of string into a string literal safe for writing to a .cpp file.

    Args:
        raw: The string or list of strings to be converted.
        separator: If an list of strings is supplied they will be concatenated together with this arg separating them.
    """
    if isinstance(raw, list):
        raw = separator.join(raw)
    t = "".maketrans({"\\": "\\\\", "\n": "\\n", "\r": "\\r", '"': '\\"'})
    return '"' + raw.translate(t) + '"'


# ======================================================================
def to_usd_str(raw: str, bare: bool = False):
    """Convert a string into a string literal safe for writing to a .usda file.

    Args:
        raw: The string to be converted.
        bare: True iff the raw string has already had its contents quoted.
    """
    if bare:
        t = "".maketrans({"\\": "\\\\", "\n": "\\n", "\r": "\\r", '"': '\\"'})
        return '"' + raw.translate(t) + '"'
    return raw


# ======================================================================
def to_comment(comment_separator: str, multiline_string: str, indent_level: int = 0):
    """Convert a multiline string into a comment where each line begins with the comment_separator

    Args:
        comment_separator: Character that indicates a line of comments, usually language-specific
        multiline_string: String with potential newlines in it
        indent_level: Number of spaces the resulting comment should be indented

    Returns:
        String representing a comment with one line of the comment per one line of the input.
        Each line of the string is indented the given number of spaces.
    """
    # Convert the multiline string into a set of truncated strings that pack into comments nicely
    comment_lines = []
    for single_line in multiline_string.splitlines():
        shortened_lines = shorten_string_lines_to(single_line, 80)
        comment_lines += shortened_lines
    # Empty lines should not have a trailing space so embed that in the non-empty lines before joining them
    string_lines = [f"{comment_separator} {x}" if x else f"{comment_separator}" for x in comment_lines]
    if indent_level > 0:
        indent_string = "    " * indent_level
        string_lines = [f"{indent_string}{line}" for line in string_lines]
    return "\n".join(string_lines)


# ======================================================================
def to_cpp_comment(multiline_string: str, indent_level: int = 0):
    """Convert a multiline string into a C++ comment

    Args:
        multiline_string: String with potential newlines in it
        indent_level: Number of spaces the resulting comment should be indented

    Returns:
        String representing a C++ comment with one line of the comment per one line of the input.
        Each line of the string is indented the given number of spaces.
    """
    return to_comment("//", multiline_string, indent_level)


# ======================================================================
def to_python_comment(multiline_string: str, indent_level: int = 0):
    """Convert a multiline string into a Python comment

    Args:
        multiline_string: String with potential newlines in it
        indent_level: Number of spaces the resulting comment should be indented

    Returns:
        String representing a Python comment with one line of the comment per one line of the input.
        Each line of the string is indented the given number of spaces.
    """
    return to_comment("#", multiline_string, indent_level)


# ======================================================================
def to_usd_comment(multiline_string: str, indent_level: int = 0):
    """Convert a multiline string into a USD comment

    Args:
        multiline_string: String with potential newlines in it
        indent_level: Number of spaces the resulting comment should be indented

    Returns:
        String representing a USD comment with one line of the comment per one line of the input.
        Each line of the string is indented the given number of spaces.
    """
    return to_comment("#", multiline_string, indent_level)


# ======================================================================
def to_usd_docs(docs: Union[List, str]) -> List[str]:
    """Returns the USD documentation as a list of strings with the docs= included"""
    if not docs:
        return 'docs="""No documentation provided"""'
    if isinstance(docs, list):
        text = [f'docs="""{docs[0]}']
        if len(docs) > 1:
            text += docs[1:]
        text[-1] += '"""'
        return text

    return f'docs="""{docs}"""'


# ======================================================================
def value_as_usd(python_value: Union[None, Tuple, List, str, bool, int, float]) -> str:
    """Convert a Python data type into a USD structure equivalent

    Args:
        python_value: Python value to convert. Dictionaries and sets have no equivalent.

    Returns:
        Structure representing the USD version of the value passed in, for converting to a string
    """
    if python_value is None:
        return None

    if isinstance(python_value, str):
        return to_usd_str(python_value, bare=True)

    if isinstance(python_value, bool):
        return "true" if python_value else "false"

    if isinstance(python_value, (int, float)):
        return python_value

    # Lists and tuples both appear as parenthesized values so convert them to that. There is also no
    # representation of an empty array so return None if the list or tuple is empty.
    if isinstance(python_value, List):
        usd_list = [value_as_usd(value) for value in python_value]
        return tuple(usd_list) if usd_list else None

    if isinstance(python_value, Tuple):
        usd_list = [value_as_usd(value) for value in python_value]
        return tuple(usd_list) if usd_list else None

    return None


# ======================================================================
def rst_title(title: str, title_level: int = 0) -> str:
    """Returns a string implementing a title_level header formatting for the string"""
    title_char = ["=", "-", "~", "_", "+", "*", ":", "^"][title_level]
    return f"\n{title}\n{title_char * len(title)}"


# ======================================================================
def rst_table(table_to_format: List[List[str]]) -> str:
    """
    Utility to take a list of lists representing a text table and format it in
    reStructedText format. This means equalizing all of the column widths,
    separating columns with " | ", separating the second and third rows with
    "+==+..==+" and putting "+--+..--+" between other rows, and at the top and
    bottom.

    e.g. this input [["Name", "Value"], ["Fred", "Flinstone"], ["Bamm-Bamm", "Rubble"]]
    yields this output:
        +-----------+------------+
        | Name      | Value      |
        +===========+============+
        | Fred      | Flintstone |
        +-----------+------------+
        | Bamm-Bamm | Rubble     |
        +-----------+------------+
    Note how the columns have been adjusted to have constant width, and the header has different padding characters.

    If strings have embedded newlines then the rows are expanded to the same number of lines, like this:
        +----------+----------------------------------+
        | Language | Hello World                      |
        +==========+==================================+
        | C++      | #include <iostream>              |
        |          | int main()                       |
        |          | {                                |
        |          |     std::cout << "Hello World!"; |
        |          |     return 0;                    |
        |          | }                                |
        +----------+----------------------------------+
        | Python   | print("Hello World!")            |
        +----------+----------------------------------+

    Args:
        table_to_format: List of columns to go in the table, where the first list is the header row and
                         subsequent lists must all be the same length.

    Returns:
        A string implementing the table of data, formatted as an RST aligned-table.

    Raises:
        ValueError: If the inner lists have different lengths
    """
    # Verify the list sizes before any work begins
    if not table_to_format:
        return ""
    if not table_to_format[0]:
        return ""
    row_count = len(table_to_format)
    column_count = len(table_to_format[0])
    if any(column_count != len(row) for row in table_to_format[1:]):
        raise ValueError(f"At least one table row does not have the expected number of columns - {column_count}")

    # max_column_widths will be the largest number of characters in each column
    # max_lines_in_row will be the largest number of string lines in any column, per row
    max_column_widths = [0] * column_count
    max_lines_in_row = [0] * row_count
    for row_index, row in enumerate(table_to_format):
        for column_index, column in enumerate(row):
            column_lines = str(column).split("\n")
            if len(column_lines) > max_lines_in_row[row_index]:
                max_lines_in_row[row_index] = len(column_lines)
            # The columns will be split into lines so only the maximum per-line width is needed
            for column_line in column_lines:
                if len(column_line) > max_column_widths[column_index]:
                    max_column_widths[column_index] = len(column_line)

    # Title and row separators are the same width as the columns, with different characters for padding
    title_separator = "+"
    row_separator = "+"
    for column_width in max_column_widths:
        title_separator += f"{'=' * (column_width + 2)}+"
        row_separator += f"{'-' * (column_width + 2)}+"
    title_separator += "\n"
    row_separator += "\n"
    table = row_separator

    # Walk each of the inner lists, adding spaces to each column as required, and column separators
    first_row = True
    empty_column = [""] * column_count
    for row_index, row in enumerate(table_to_format):
        # Populate the row_contents with a list of sub-row lines, containing one column per line
        row_contents = [list(empty_column) for _ in range(max_lines_in_row[row_index] * 2 - 1)]

        for column_index, column in enumerate(row):
            # Populate the column contents with a list of column lines, padding with spaces for
            # the columns that do not contain the maximum number of lines
            column_lines = str(column).split("\n")
            num_lines = len(column_lines)

            for line_index in range(max_lines_in_row[row_index]):
                column_line = column_lines[line_index] if line_index < num_lines else ""
                padding = max_column_widths[column_index] - len(column_line)
                row_contents[line_index * 2][column_index] = f"{column_line}{' ' * padding}"
                # Blank lines are required in .rst format to create multi-line table entries
                if line_index > 0:
                    row_contents[line_index * 2 - 1][column_index] = " " * max_column_widths[column_index]

        # Add all of the lines for this row into the table
        for row_lines in row_contents:
            table += f"| {' | '.join(row_lines)} |\n"

        # Put the separator after the row
        if first_row:
            first_row = False
            table += title_separator
        else:
            table += row_separator

    return table


# ==============================================================================================================
def rst_csv_table(table_data: list[tuple], extra_directives: list[str] = None) -> list[str]:
    """Convert a table description to an RST CSV equivalent

    Args:
        table_data: List of tuples containing the table data. The first entry is the table header.
        extra_directives: Optional list of directives to add with the header

    Returns:
        list[str]: List of RST commands implementing a csv-table section that formats the table data.
    """
    if not table_data:
        return []

    def _row_data(original: tuple) -> str:
        r"""Return the tuple list with elements of the tuple quoted (including escaping pre-existing quotes)
        and comma-separated. Use json to escape quotes, a substring to remove the list brackets, and then
        replace the JSON escaping of a double quote backslash-quote(\") with the csv-table escape double-quote("").
        """
        return json.dumps([str(item) for item in original])[1:-1].replace('\\"', '""')

    csv_data = [
        ".. csv-table::",
        f"    :header: {_row_data(table_data[0])}",
    ]
    if extra_directives:
        csv_data += [f"    {directive}" for directive in extra_directives]
    csv_data.append("")
    if len(table_data) > 1:
        csv_data += [f"    {_row_data(row)}" for row in table_data[1:]]
    csv_data.append("")

    return csv_data


# ======================================================================
def check_color(color: ColorType):
    """Check to see if the color has a legal specification.
    Args:
        color Value to check using one of these two formats
            "#AABBGGRR" Hex digits of color components in 0-255
            [R, G, B, A] Decimal values of color components in 0-255

    Returns:
        Hex string representing the RGBA values (to be used as metadata, using uppercase letters as #AABBGGRR)

    Raises:
        ParseError if the color specification was not legal
    """
    if isinstance(color, List):
        if len(color) != 4:
            raise ParseError(f"Color list '{color}' must have 4 elements - R, G, B, A")
        try:
            (red, green, blue, alpha) = [int(component) for component in color]
        except TypeError as error:
            raise ParseError(f"Color list '{color}' must have 4 integer elements in [0, 255] - R, G, B, A") from error
    elif isinstance(color, str):
        try:
            red = int(f"0x{color[7:9]}", 16)
            green = int(f"0x{color[5:7]}", 16)
            blue = int(f"0x{color[3:5]}", 16)
            alpha = int(f"0x{color[1:3]}", 16)
        except (TypeError, ValueError) as error:
            raise ParseError(f"Color string '{color}' must be in the hexadecimal format '#AABBGGRR'") from error

    if red < 0 or red > 255:
        raise ParseError("Red component '{red}' is out of the range [0, 255]")
    if green < 0 or green > 255:
        raise ParseError("Green component '{green}' is out of the range [0, 255]")
    if blue < 0 or blue > 255:
        raise ParseError("Blue component '{blue}' is out of the range [0, 255]")
    if alpha < 0 or alpha > 255:
        raise ParseError("Alpha component '{alpha}' is out of the range [0, 255]")

    return f"#{format(alpha, '02X')}{format(blue, '02X')}{format(green, '02X')}{format(red, '02X')}".upper()


# ======================================================================
def check_icon_information(icon_info: Union[str, Dict[str, ColorType]]):
    """Raises ParseError if the icon_path is not legal, otherwise returns the path

    Args:
        icon_info: If a string then it is the icon path relative to the .ogn file
        If a dictionary then the dictionary contains extended icon information with these keywords

    Returns:
        (path, color, background_color, border_color) extracted from the icon information
        If any element was not specified then it will be None

    Raises:
        ParseError if any of the icon properties are illegal
    """
    path = None
    color = None
    background_color = None
    border_color = None
    # Simple spec - just the path
    if isinstance(icon_info, str):
        path = icon_info
    # Extended spec - dictionary of properties
    elif isinstance(icon_info, dict):
        for key, value in icon_info.items():
            if key == IconKeys.PATH:
                path = value
            elif key == IconKeys.COLOR:
                color = check_color(value)
            elif key == IconKeys.BACKGROUND_COLOR:
                background_color = check_color(value)
            elif key == IconKeys.BORDER_COLOR:
                border_color = check_color(value)
            else:
                raise ParseError(f"Icon keyword '{key}' not in legal list of path, color, backgroundColor, borderColor")
    else:
        raise ParseError(f"Icon information not a string path or a dictionary of properties - `{icon_info}`")
    return (path, color, background_color, border_color)


# ======================================================================
def check_memory_type(memory_type: str):
    """Raises ParseError if the memory type is not legal, otherwise returns the memory type value"""
    if memory_type not in MemoryTypeValues.ALL:
        raise ParseError(f'Memory type "{memory_type} not in allowed list of {MemoryTypeValues.ALL}')
    return memory_type


# ======================================================================
def check_token_name(token_name: str):
    """Raises a ParseError if the given node name has an illegal pattern, else returns the node name"""
    if not RE_TOKEN_NAME.match(token_name):
        raise ParseError(TOKEN_NAME_REQUIREMENT.format(token_name))

    return token_name


# ======================================================================
def get_metadata_dictionary(metadata):
    """Raises ParseError if the metadata is not legal, otherwise returns it as a dictionary with comments removed.
    This function only does generic checks, applicable to all types of metadata. More specific metadata checks,
    in particular for legal values and keywords, is done elsewhere
    """

    def to_string(value: Any) -> str:
        """Turn metadata values into strings, notably lists and tuples are comma-separated strings"""
        output = io.StringIO()
        # Metadata specified as a list is stored as a comma-separated string
        if isinstance(value, (tuple, list)):
            csv_data = list(value)
        # Metadata specified as a dictionary means the values might contain special characters that the generated code
        # cannot handle and the keys are safe names. For storing the actual metadata only the values are of interest.
        elif isinstance(value, dict):
            csv_data = list(value.values())
        # Simple elements are still run through CSV to quote any embedded commas
        else:
            csv_data = [value]
        writer = csv.writer(output, quoting=csv.QUOTE_MINIMAL)
        writer.writerow(csv_data)
        return output.getvalue().rstrip()

    try:
        pruned_metadata = {key: to_string(value) for key, value in metadata.items() if key[0] != "$"}
        logger.info(" -> %s", pruned_metadata)
    except AttributeError as error:
        raise ParseError("Metadata must be a dictionary of strings") from error
    return pruned_metadata


# If True then perform more aggressive directory checks, not safe in a multi-threaded environment
SAFE_DIRECTORY_CREATION = False


# ======================================================================
def ensure_writable_directory(prospective_dir: str | Path):
    """Ensure a directory exists and is writable

    Args:
        prospective_dir: Full path to the directory to check or create

    Raises:
        ValueError: If the path could not be made into a writable directory for any reason
    """
    # There are race condition issues with the prospective directory checking so only do it
    # if it was explicitly requested. (It has to be hardcoded since this test happens during
    # argument parsing so you can't safely pass an argument to enable that.)
    try:
        if prospective_dir is None:
            raise ValueError("Directory cannot be None")
        writable_dir = prospective_dir if isinstance(prospective_dir, Path) else Path(prospective_dir)
        if SAFE_DIRECTORY_CREATION:  # pragma: no cover   Debugging only
            if writable_dir.is_file():
                logger.warning('Directory "%s" existed as a file - removing', writable_dir)
                writable_dir.unlink()
            if not writable_dir.is_dir():
                writable_dir.mkdir(mode=0o777, parents=True, exist_ok=True)
            if not writable_dir.is_dir():
                raise Exception
            if not os.access(str(writable_dir), os.W_OK):
                raise Exception
        else:
            if not writable_dir.is_dir():
                writable_dir.mkdir(mode=0o777, parents=True, exist_ok=True)
    except Exception as error:  # pragma: no cover   Firewall
        raise ValueError(f"writable_dir:{prospective_dir} could not be made into a writable directory") from error


# ==============================================================================================================
class WritableDir(argparse.Action):
    """Helper class for the argparser to check for a writable directory"""

    def __call__(self, parser, namespace, values, option_string=None):
        """Function called by the arg parser to verify that a directory exists and is writable

        Args:
            parser: argparser required argument, ignored
            namespace: Python module into which the writable directory is to be placed
            values: The Path of the directory being checked for writability
            option_string: argparser required argument, ignored

        Raises:
            argparse.ArgumentTypeError if the requested directory cannot be found or created in writable mode
        """
        try:
            ensure_writable_directory(values)
            setattr(namespace, self.dest, values)
        except Exception as error:
            raise argparse.ArgumentTypeError(error)


# ==============================================================================================================
class ReadableDirs(argparse.Action):
    """Helper class for the argparser to check for one or more readable directories
    Uses the nargs value along with a validate() method to implement proper count checking
    """

    def __call__(self, parser, namespace, values, option_string=None):
        """Function called by the arg parser to verify that the directories exist

        Args:
            parser: argparser required argument, ignored
            namespace: Python module in which the directories are to be placed
            values: The Path or list of paths to the directory being checked
            option_string: argparser required argument, ignored

        Raises:
            argparse.ArgumentTypeError if the requested directory cannot be found
        """
        try:
            if not isinstance(values, list):
                values = [values]
            for directory in values:
                if directory is None:
                    raise ValueError("Directory cannot be None")
                directory_path = directory if isinstance(directory, Path) else Path(directory)
                if directory_path.is_file():
                    raise TypeError(f"{directory_path} is a file, expected a directory")
                if not directory_path.is_dir():
                    raise TypeError(f"{directory_path} is not a directory")
                self._directory_list.append(directory_path)
                if len(self._directory_list) > self._max_size:
                    raise argparse.ArgumentTypeError(
                        f"{self._opt} accepts at most {self._max_size} arguments, found {len(self._directory_list)}"
                    )
                if self._as_list:
                    setattr(namespace, self.dest, self._directory_list)
                else:
                    setattr(namespace, self.dest, self._directory_list[0])
        except TypeError as error:
            raise argparse.ArgumentTypeError(error)

    def validate(self):
        """Validate the arguments parsed with this action. Mostly to allow for nargs values to be checked for
        insufficient argument count.

        Raises:
            argparse.ArgumentTypeError: if the arguments provided did not match the specified nargs requirement
        """
        found_count = len(self._directory_list)
        if found_count < self._min_size:
            raise argparse.ArgumentTypeError(
                f"{self._opt} requires at least {self._min_size} arguments, found {found_count}"
            )
        if found_count > self._max_size:
            raise argparse.ArgumentTypeError(
                f"{self._opt} requires at most {self._max_size} arguments, found {found_count}"
            )

    def __init__(self, *args, **kwargs):
        """Initialize the list of directories that will be gathered from the arguments"""
        self._opt = kwargs.get("option_strings", "DIR")
        nargs = kwargs.get("nargs", None)
        if nargs == "+":
            self._as_list = True
            self._min_size = 1
            self._max_size = 99999
        elif nargs == "?":
            self._as_list = True
            self._min_size = 0
            self._max_size = 1
        elif isinstance(nargs, int):
            self._as_list = True
            self._min_size = nargs
            self._max_size = nargs
        else:
            self._as_list = False
            self._min_size = 1
            self._max_size = 1

        self._directory_list = []
        super().__init__(*args, **kwargs)


# ======================================================================
#
# Collection of functions to make a symbolic link - ends at the next separator with "=====" in it or EOF
#
def _find_junction_location(junction_path: str) -> str:  # pragma: no cover  OS-Specific
    """Returns the location to which the junction path points

    As with the os.symlink call the equivalent fsutil function can only be run with admin privileges,
    resulting in the necessity of this roundabout path to the same information.
        - use the /A:L functions to get the file type information in the parent directory
        - find the entry that matches junction_path
        - parse the link location from the remainder of the line
    """
    # Normalizing the path ensures we don't end up at the target's parent instead of the link's parent
    with subprocess.Popen(
        ("dir", "/A:L", os.path.normpath(os.path.join(junction_path, os.pardir))),
        bufsize=0,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True,
    ) as results:
        out, _ = results.communicate()
        out = out.decode(locale.getdefaultlocale()[1])  # pylint: disable=deprecated-method
        if results.returncode == 0:
            lines = out.splitlines()
            keys = ["<JUNCTION>", "<SYMLINKD>"]
            for line in lines:
                for key in keys:
                    start = line.find(key)
                    if start == -1:
                        continue
                    end = start + len(key)
                    terms = line[end:].split("[")
                    if len(terms) < 2:
                        continue
                    junction_name = os.path.normcase(terms[0].strip())
                    junction_target = terms[1].strip("]")
                    junction_name_to_find = os.path.normcase(os.path.basename(junction_path))
                    if junction_name == junction_name_to_find:
                        return junction_target
    raise OSError(f"Failed to get link target for '{junction_path}'")


# ----------------------------------------------------------------------
def _find_linked_location(link_path: str) -> str:  # pragma: no cover  OS-Specific
    """Looks for the location to which the link_path points

    Args:
        link_path: Location of the link to check

    Returns:
        Location the link points to

    Raises:
        OSError: If the link doesn't exist, is the wrong type, or could not be read
    """
    try:
        # First the easy way...
        return os.readlink(link_path)

    except Exception as error:

        # Then the hard way on Windows...
        if os.name == "nt":
            try:
                return _find_junction_location(link_path)
            except Exception as secondary_error:
                raise OSError() from secondary_error

        raise OSError() from error


# ----------------------------------------------------------------------
def _try_os_symlink(existing_path: str, link_to_create: str):  # pragma: no cover  OS-Specific
    """Implementation of symbolic link that uses the Python os.symlink method

    Args:
        existing_path: Current location to which the link will point
        link_to_create: Location of the new link

    Raises:
        OSError: If the link could not be created
    """
    try:
        os.symlink(existing_path, link_to_create, target_is_directory=True)
    except FileExistsError as error:
        # Find the linked location
        target = _find_linked_location(link_to_create)

        # If the link is to a different location than the one requested that's bad
        if os.path.normcase(target) != os.path.normcase(existing_path):
            raise OSError("Link already exists, pointing to a different location") from error


# ----------------------------------------------------------------------
def _try_junction_link(existing_path: str, link_to_create: str):  # pragma: no cover  OS-Specific
    """Implementation of symbolic link that uses the native Windows linking capabilities.

    This is only necessary because Windows requires admin privileges to create symlinks and we may not have them

    Args:
        existing_path: Current location to which the link will point
        link_to_create: Location of the new link

    Raises:
        OSError: If the link could not be created
    """
    # Even though they do exactly the same things "mklink" can be done with admin privileges
    with subprocess.Popen(
        ("mklink", "/j", link_to_create, existing_path),
        bufsize=0,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True,
    ) as results:
        _, err = results.communicate()
        err = err.decode(locale.getdefaultlocale()[1])  # pylint: disable=deprecated-method
        if results.returncode:
            if "file already exists" in err:
                target = _find_linked_location(link_to_create)
                # If the link exists but is to the same place as was requested that's good
                if os.path.normcase(target) == os.path.normcase(existing_path):
                    return
            raise OSError(f"{err.strip()} ({link_to_create} ==> {existing_path})")


# ----------------------------------------------------------------------
def create_symbolic_link(existing_path: str, link_to_create: str):  # pragma: no cover  OS-Specific
    """Create a symbolic link, if possible

    Args:
        existing_path: Current location to which the link will point
        link_to_create: Location of the new link

    Raises:
        OSError: If the link could not be created
    """
    try:
        _try_os_symlink(existing_path, link_to_create)
    except OSError as error:
        # On Windows there can be privilege errors that prevent the link from being made, but there is another way...
        if os.name == "nt" and "privilege not held" in str(error):
            _try_junction_link(existing_path, link_to_create)
        else:
            raise error
    except Exception as error:
        raise OSError(str(error)) from error


# ======================================================================
class NameManager:
    """Class that manages naming of generated code where the name is not important to the user

    Name uniqueness is only important within a single file generation, so different name managers should be used for
    different languages (e.g. one for C++, a different one for Python).

    Internal Properties:
        __current: Current unique index for the next name
        __shortened_names: Map of original name to shortened name.
    """

    # Control the naming algorithm through environment variables.
    SHORTEN_NAMES = os.getenv("DEBUG") or os.getenv("OGN_DEBUG")

    def __init__(self):
        """Initialize with an empty name map"""
        self.__shortened_names = {}
        self.__current = 0

    def name(self, original_name: str) -> str:
        """Returns a shortened unique name corresponding to original_name if shortening is enabled, otherwise the name.
        This is similar to tokenization, with the goal of minimizing the amount of code the compiler has to
        read when compiling/interpreting the generated code that's invisible to the user.  For instance there might
        be a unique local variable called "attribute_inputs_myInput" that can be shorted to "__2"
        """
        if self.SHORTEN_NAMES:
            try:
                return self.__shortened_names[original_name]
            except KeyError:
                self.__shortened_names[original_name] = f"__{self.__current}"
                self.__current += 1
                return self.__shortened_names[original_name]

        return original_name
