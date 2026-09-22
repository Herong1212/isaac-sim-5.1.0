# NOTE: all imported classes must have different class names
"""This module provides functionality for managing USD stage templates, including registration, creation, and transformation of stages within Omniverse Kit."""

__all__ = [
    "register_template",
    "unregister_template",
    "get_stage_template_list",
    "get_stage_template",
    "get_default_template",
    "new_stage",
    "new_stage_with_callback",
    "new_stage_async",
]

from .stage_core import *
