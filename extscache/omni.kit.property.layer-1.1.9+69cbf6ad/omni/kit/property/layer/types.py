"""This module defines classes and constants for representing and handling metadata types and names associated with layers."""

__all__ = ["LayerMetaType", "LayerMetaName"]


class LayerMetaType:
    """A class representing metadata types for a layer.

    This class defines various constants that are used to represent different types of metadata associated with a layer. These include temporal information such as start and end times, spatial information such as layer offset and scale, as well as other properties like units and comments.
    """

    START_TIME = 0
    """int: The start time code index."""
    END_TIME = 1
    """int: The end time code index."""
    TIMECODES_PER_SECOND = 2
    """int: Number of time codes per second."""
    FPS_PER_SECOND = 3
    """int: Number of frames per second."""
    UNITS = 4
    """int: The index for units of measurement."""
    LAYER_OFFSET = 5
    """int: The index for the layer's offset."""
    LAYER_SCALE = 6
    """int: The index for the layer's scale factor."""
    KG_PER_UNIT = 7
    """int: The index for kilograms per unit."""
    COMMENT = 8
    """int: The index for comments."""
    DOC = 9
    """int: The index for documentation."""
    NUM_PROPERTIES = 10
    """int: The total number of properties."""


LayerMetaName = [
    "Start Time Code",
    "End Time Code",
    "Time Codes Per Second",
    "Frames Per Second",
    "Meters Per Unit",
    "Layer Offset",
    "Layer Scale",
    "Kgs Per Unit",
    "Comment",
    "Documentation",
]
