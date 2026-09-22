"""This module provides a delegate class for generating path-related widgets based on payloads."""

from omni.kit.window.property.property_scheme_delegate import PropertySchemeDelegate


class PathPrimSchemeDelegate(PropertySchemeDelegate):
    """A delegate class for generating widgets based on the given payload.

    This class inherits from PropertySchemeDelegate and provides a mechanism to determine
    which widgets should be constructed for a given payload, specifically for paths."""

    def get_widgets(self, payload):
        """Returns a list of widgets based on the provided payload.

        Args:
            payload (list): The payload to evaluate for widget creation.

        Returns:
            list: A list of widgets to be built."""
        widgets_to_build = []

        if len(payload):
            widgets_to_build.append("path")

        return widgets_to_build
