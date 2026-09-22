"""Establish autonode as a module and create a common logger.
To use the AutoNode logger just get it by name:

    import logging
    logger = logging.getLogger("AutoNode")
"""

import logging
import os
import sys

__all__ = ["setup_repo_tool"]


# Entry point for the repo_man tool "autonode_generator"
from .repo_tool import setup_repo_tool

# The AutoNode logger will output to stdout in a standard way, defaulting to logging level "WARN" unless the
# environment variable AUTONODE_DEBUG is set, in which case it defaults to level "DEBUG".
_autonode_logger = logging.getLogger("AutoNode")
if not _autonode_logger.handlers:
    _handler = logging.StreamHandler(sys.stdout)
    _autonode_logger.addHandler(_handler)
else:
    _handler = _autonode_logger.handlers[0]
_handler.setFormatter(logging.Formatter("[%(name)s] [%(levelname)s] %(message)s"))
_handler.setLevel(logging.DEBUG)
_autonode_logger.setLevel(logging.DEBUG if os.getenv("AUTONODE_DEBUG") else logging.WARN)
