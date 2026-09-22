# Copyright (c) 2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = []

from collections import OrderedDict

from .usd_property_widget import UsdPropertyUiEntry

stack = []


class Container:
    """
    Class that represents a container in the custom layout.
    """

    def __init__(self, hide_if_true=None, show_if_true=None):
        self._children = []
        self._container_name = ""
        self._collapsed = False
        self._is_visible = True
        if isinstance(hide_if_true, bool):  # pragma: no cover
            self._is_visible = not hide_if_true
        if isinstance(show_if_true, bool):  # pragma: no cover
            self._is_visible = show_if_true

    def __enter__(self):
        stack.append(self)

    def __exit__(self, exc_type, exc_value, tb):
        """
        Exits the container.

        Args:
            exc_type (type): The type of the exception.
            exc_value (Exception): The exception.
            tb (traceback): The traceback.
        """
        stack.pop()

    def add_child(self, item):
        """
        Adds a child to the container.

        Args:
            item: The child to add.
        """
        self._children.append(item)

    def get_name(self):
        """
        Gets the name of the container.

        Returns:
            str: The name of the container.
        """
        return self._container_name

    def get_collapsed(self):
        """
        Gets the collapsed state of the container.

        Returns:
            bool: The collapsed state of the container.
        """
        return self._collapsed

    def is_visible(self):
        """
        Gets the visibility of the container.

        Returns:
            bool: The visibility of the container.
        """
        return self._is_visible


class CustomLayoutProperty:
    """
    Class that represents a property in the custom layout.
    """

    def __init__(self, prop_name, display_name=None, build_fn=None, hide_if_true=None, show_if_true=None):
        self._prop_name = prop_name
        self._display_name = display_name
        self._build_fn = build_fn  # TODO
        self._is_visible = True
        if isinstance(hide_if_true, bool):  # pragma: no cover
            self._is_visible = not hide_if_true
        if isinstance(show_if_true, bool):  # pragma: no cover
            self._is_visible = show_if_true

        stack[-1].add_child(self)

    def get_property_name(self):
        """
        Gets the name of the property.

        Returns:
            str: The name of the property.
        """
        return self._prop_name

    def get_display_name(self):
        """
        Gets the display name of the property.

        Returns:
            str: The display name of the property.
        """
        return self._display_name

    def get_build_fn(self):
        """
        Gets the build function of the property.

        Returns:
            Callable: The build function of the property.
        """
        return self._build_fn

    def is_visible(self):
        """
        Gets the visibility of the property.

        Returns:
            bool: The visibility of the property.
        """
        return self._is_visible


class CustomLayoutGroup(Container):
    """
    Class that represents a group in the custom layout.
    """

    def __init__(self, container_name, collapsed=False, hide_if_true=None, show_if_true=None):
        super().__init__(hide_if_true=hide_if_true, show_if_true=show_if_true)
        self._container_name = container_name
        self._collapsed = collapsed

        stack[-1].add_child(self)


class CustomLayoutFrame(Container):
    """
    Class that represents a frame in the custom layout.
    """

    def __init__(self, hide_extra=False):
        super().__init__()
        self._hide_extra = hide_extra

    def apply(self, props):
        """
        Applies the custom layout to the properties.

        Args:
            props: The properties to apply the custom layout to.
        """
        customized_props = []
        # preprocess to speed up lookup
        props_dict = OrderedDict()
        for prop in props:
            props_dict[prop[0]] = prop
        self._process_container(self, props_dict, customized_props, "")

        # add the remaining
        if not self._hide_extra:
            for prop in props_dict.values():
                customized_props.append(prop)

        return customized_props

    def _process_container(self, container, props_dict, customized_props, group_name):
        """
        Processes the container.

        Args:
            container: The container to process.
            props_dict: The dictionary of properties.
            customized_props: The list of customized properties.
            group_name: The name of the group.
        """
        # pylint: disable=protected-access
        for child in container._children:
            if isinstance(child, Container):
                if child.is_visible():
                    prefix = group_name + f":{child.get_name()}" if group_name else child.get_name()
                    self._process_container(child, props_dict, customized_props, prefix)
            elif isinstance(child, CustomLayoutProperty) and child.is_visible():
                prop_name = child.get_property_name()
                collapsed = container.get_collapsed()
                prop = props_dict.pop(prop_name, None)  # get and remove
                if prop:
                    if group_name != "":
                        prop.override_display_group(group_name, collapsed)
                    display_name = child.get_display_name()
                    if display_name:
                        prop.override_display_name(display_name)
                    prop.build_fn = child.get_build_fn()
                    customized_props.append(prop)
                elif child.get_build_fn():
                    prop = UsdPropertyUiEntry("", group_name, "", None, child.get_build_fn(), collapsed)
                    customized_props.append(prop)
