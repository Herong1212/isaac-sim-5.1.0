"""Utilities to help with non-standard command argument parsing"""

import argparse
from pathlib import Path


# ==============================================================================================================
class ReadableDir(argparse.Action):  # pragma: no cover    Unsupported code
    """Helper class for the parser to check that a value is a readable directory"""

    def __call__(self, parser, namespace, values, option_string=None):
        """Function called by the arg parser to verify that a directory exists and is readable.

        If the function succeeds then the "self.dest" value, which is the argparse option for the argument being
        checked, will be set to a Path pointing to the readable directory.

        Args:
            parser: argparser required argument, ignored
            namespace: argparser required argument, ignored
            values: The path to the directory being checked for readability
            option_string: argparser required argument, ignored

        Raises:
            argparse.ArgumentTypeError if the requested directory cannot be found or created in readable mode
        """
        try:
            # If this is not a path then a TypeError will be raised
            prospective_dir = Path(values)
        except TypeError as error:
            raise argparse.ArgumentTypeError(f"'{values}' is not a valid directory path") from error

        if prospective_dir.is_dir():
            setattr(namespace, self.dest, prospective_dir)
        else:
            raise argparse.ArgumentTypeError(f"{prospective_dir} is not a directory")


# ==============================================================================================================
class ReadableFileOrDir(argparse.Action):  # pragma: no cover    Unsupported code
    """Helper class for the parser to check that a value is a readable directory or file"""

    def __call__(self, parser, namespace, values, option_string=None):
        """Function called by the arg parser to verify that a directory exists and is readable.

        If the function succeeds then the "self.dest" value, which is the argparse option for the argument being
        checked, will be set to a Path pointing to the readable directory or file.

        Args:
            parser: argparser required argument, ignored
            namespace: argparser required argument, ignored
            values: The list of paths to the directory or file being checked for readability
            option_string: argparser required argument, ignored

        Raises:
            argparse.ArgumentTypeError if the requested directory cannot be found or created in readable mode
        """
        parsed_paths = []
        for value in values:
            try:
                # If this is not a path then a TypeError will be raised
                path_to_check = Path(value)
            except TypeError as error:
                raise argparse.ArgumentTypeError(f"'{value}' is not a valid path") from error

            if path_to_check.is_dir() or path_to_check.is_file():
                parsed_paths.append(path_to_check)
            else:
                raise argparse.ArgumentTypeError(f"{path_to_check} is not a directory or file")
        setattr(namespace, self.dest, parsed_paths)


# ==============================================================================================================
class WritableDir(argparse.Action):  # pragma: no cover    Unsupported code
    """Helper class for the parser to check for a writable directory"""

    def __call__(self, parser, namespace, values, option_string=None):
        """Function called by the arg parser to verify that a directory exists and is writable

        If the function succeeds then the "self.dest" value, which is the argparse option for the argument being
        checked, will be set to a Path pointing to the readable directory.

        Args:
            parser: argparser required argument, ignored
            namespace: argparser required argument, ignored
            values: The path to the directory being checked for writability. None is passed unchecked.
            option_string: argparser required argument, ignored

        Raises:
            argparse.ArgumentTypeError if the requested directory cannot be found or created in writable mode
        """
        try:
            # If this is not a path then a TypeError will be raised
            prospective_dir = Path(values)
        except TypeError as error:
            raise argparse.ArgumentTypeError(f"'{values}' is not a valid directory path") from error

        try:
            if not prospective_dir.is_dir():
                prospective_dir.mkdir(mode=0o777, parents=True, exist_ok=True)
                if prospective_dir.is_dir():
                    setattr(namespace, self.dest, prospective_dir)
                else:
                    raise argparse.ArgumentTypeError(f"{prospective_dir} could not be created as a writable directory")
        except (IOError, ValueError) as error:
            raise argparse.ArgumentTypeError(f"{prospective_dir} is not a writable directory") from error
