"""This file contains AutoNode definitions used for testing. They are not meant for general use."""

import omni.graph.tools._impl.autonode_generator.ogn_types as ogdt
from omni.graph.core import node_type


@node_type
def an_float_test(value: ogdt.Float) -> ogdt.Float:
    """Trivial node to copy a float value from input to output"""
    return value
