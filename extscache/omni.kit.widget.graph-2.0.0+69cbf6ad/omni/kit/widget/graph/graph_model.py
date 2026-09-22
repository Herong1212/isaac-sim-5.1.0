# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

"""This module defines the GraphModel class used for managing the data structure and interactions within a graph widget, following the model-view pattern."""


__all__ = ["GraphModel"]

from enum import Enum
from enum import IntFlag
from enum import auto
from typing import Any
from typing import Optional
from typing import Union


class GraphModel:
    """The base class for the Graph model.

    The model is the central component of the graph widget. It is the
    application's dynamic data structure, independent of the user interface,
    and it directly manages the data. It follows closely model–view pattern.
    It defines the standard interface to be able to interoperate with the
    components of the model-view architecture. It is not supposed to be
    instantiated directly. Instead, the user should subclass it to create a
    new model.

    The model manages two kinds of data elements. Node and port are the
    atomic data elements of the model. Both node and port can have any number
    of sub-ports and any number of input and output connections.

    There is no specific Python type for the elements of the model. Since
    Python has dynamic types, the model can return any object as a node or a
    port. When the widget needs to get a property of the node, it provides
    the given node back to the model.

    Example:

    .. code:: python

       class UsdShadeModel(GraphModel):
           @property
           def nodes(self, prim=None):
               # Return Usd.Prim in a list
               return [stage.GetPrimAtPath(selection)]

           @property
           def name(self, item=None):
               # item here is Usd.Prim because UsdShadeModel.nodes returns
               # Usd.Prim
               return item.GetPath().name

       # Accessing nodes and properties example
       model = UsdShadeModel()

       # UsdShadeModel decides the type of nodes. It's a list with Usd.Prim
       nodes = model.nodes

       for node in nodes:
           # The node is accessed through evaluation of self[key]. It will
           # return the proxy object that redirects its properties back to
           # model. So the following line will call UsdShadeModel.name(node).
           name = model[node].name
           print(f"The model has node {name}")
    """

    class _ItemProxy:
        """
        The proxy that allows accessing the nodes and ports of the model
        through evaluation of self[key]. This proxy object redirects its
        properties to the model that has properties like this:

        class Model:
           @property
           def name(self, item):
               pass

           @name.setter
           def name(self, value, item):
               pass

        """

        def __init__(self, model, item):
            """Save model and item to be able to redirect the properties"""
            # Since we already have __setattr__ reimplemented, the following
            # code is the way to bypass it
            super().__setattr__("_model", model)
            super().__setattr__("_item", item)

        def __getattr__(self, attr):
            """
            Called when the default attribute access fails with an
            AttributeError.
            """
            model_property = getattr(type(self._model), attr)
            return model_property.fget(self._model, self._item)

        def __setattr__(self, attr, value):
            """
            Called when an attribute assignment is attempted. This is called
            instead of the normal mechanism (i.e. store the value in the
            instance dictionary).
            """
            model_property = getattr(type(self._model), attr)
            model_property.fset(self._model, value, self._item)
            # TODO: Maybe it's better to automatically call model._item_changed here?
            # No, it's not better because in some cases node is changing and
            # the widget doesn't change. For example when the user changes the
            # position.

    class _Event(set):
        """
        A list of callable objects. Calling an instance of this will cause a
        call to each item in the list in ascending order by index.
        """

        def __call__(self, *args, **kwargs):
            """Called when the instance is “called” as a function"""
            # Call all the saved functions
            for f in list(self):
                f(*args, **kwargs)

        def __repr__(self):
            """
            Called by the repr() built-in function to compute the “official”
            string representation of an object.
            """
            return f"Event({set.__repr__(self)})"

    class ExpansionState(Enum):
        """Enum for node expansion states."""
        OPEN = 0
        """Node is fully expanded."""
        MINIMIZED = 1
        """MINIMIZED: Node is minimized but not closed."""
        CLOSED = 2
        """Node is closed and ports content is not visible."""

    class PreviewState(IntFlag):
        """Enum flags for node preview states."""
        NONE = 0
        """No preview available."""
        OPEN = auto()
        """Preview is currently open."""
        CACHED = auto()
        """Preview is cached for quick access."""
        LARGE = auto()
        """Preview is available in a large format."""

    class _EventSubscription:
        """
        Event subscription.

        _Event has callback while this object exists.
        """

        def __init__(self, event, fn):
            """
            Save the function, the event, and add the function to the event.
            """
            self._fn = fn
            self._event = event
            event.add(self._fn)

        def __del__(self):
            """Called by GC."""
            self._event.remove(self._fn)

    DISPLAY_NAME = None
    """The display name for the GraphModel instance."""

    def __init__(self):
        """Initialize the GraphModel, setting up events for item changes, node changes, and selection changes."""
        super().__init__()
        # TODO: begin_edit/end_edit
        self.__on_item_changed = self._Event()
        self.__on_selection_changed = self._Event()
        self.__on_node_changed = self._Event()

    def __getitem__(self, item):
        """Called to implement evaluation of self[key]"""
        # Return a proxy that redirects its properties back to the model.
        return self._ItemProxy(self, item)

    def _item_changed(self, item=None):
        """Call the event object that has the list of functions"""
        self.__on_item_changed(item)

    def _rebuild_node(self, item=None, full=False):
        """Call the event object that has the list of functions"""
        self.__on_node_changed(item, full=full)

    def subscribe_item_changed(self, fn):
        """Subscribes a callback function to item change events.

        Args:
            fn: The callback function to be invoked when an item changes.

        Returns:
            An _EventSubscription object that will automatically unsubscribe when destroyed."""
        return self._EventSubscription(self.__on_item_changed, fn)

    def _selection_changed(self):
        """Call the event object that has the list of functions"""
        self.__on_selection_changed()

    def subscribe_selection_changed(self, fn):
        """Subscribes a callback function to selection change events.

        Args:
            fn: The callback function to be invoked when the selection changes.

        Returns:
            An _EventSubscription object that will automatically unsubscribe when destroyed."""
        return self._EventSubscription(self.__on_selection_changed, fn)

    def subscribe_node_changed(self, fn):
        """Subscribes a callback function to node change events.

        Args:
            fn: The callback function to be invoked when a node changes.

        Returns:
            An _EventSubscription object that will automatically unsubscribe when destroyed."""
        return self._EventSubscription(self.__on_node_changed, fn)

    @staticmethod
    def has_nodes(obj):
        """Checks whether the model can currently build the graph network using the provided object.

        Args:
            obj: The object to check for nodes.

        Returns:
            bool: True if nodes are present; otherwise, False."""
        pass

    # The list of properties of node and port.

    @property
    def name(self, item) -> str:
        """Gets the name of the item.

        Returns:
            The name of the item."""
        pass

    @name.setter
    def name(self, value: str, item=None):
        """Sets the name of the item.

        Args:
            value: The new name.
            item: The item whose name is being set."""
        pass

    @property
    def type(self, item):
        """Gets the type of the item.

        Returns:
            The type of the item."""
        pass

    @property
    def inputs(self, item):
        """Gets the inputs of the item.

        Returns:
            The inputs of the item."""
        pass

    @inputs.setter
    def inputs(self, value, item=None):
        """Sets the inputs of the item.

        Args:
            value: The new inputs value.
            item: The item whose inputs are being set."""
        pass

    @property
    def outputs(self, item):
        """Gets the outputs of the item.

        Returns:
            The outputs of the item."""
        pass

    @outputs.setter
    def outputs(self, value, item=None):
        """Sets the outputs of the item.

        Args:
            value: The new outputs value.
            item: The item whose outputs are being set."""
        pass

    @property
    def nodes(self, item=None):
        """Gets the nodes of the item.

        Returns:
            The nodes of the item."""
        pass

    @property
    def ports(self, item=None):
        """Gets the ports of the item.

        Returns:
            The ports of the item."""
        pass

    @ports.setter
    def ports(self, value, item=None):
        """Sets the ports of the item.

        Args:
            value: The new ports value.
            item: The item whose ports are being set."""
        pass

    @property
    def expansion_state(self, item=None) -> ExpansionState:
        """Gets the expansion state of the item.

        Returns:
            The expansion state of the item."""
        return self.ExpansionState.OPEN

    @expansion_state.setter
    def expansion_state(self, value: ExpansionState, item=None):
        """Sets the expansion state of the item.

        Args:
            value: The new expansion state.
            item: The item whose expansion state is being set."""
        pass

    def can_connect(self, source, target):
        """Determines if a connection between source and target is allowed.

        Args:
            source: The starting point of the connection.
            target: The end point of the connection.

        Returns:
            bool: True if the connection is possible; otherwise, False."""
        return True

    @property
    def position(self, item=None):
        """Gets the position of the item.

        Returns:
            The position of the item."""
        pass

    @position.setter
    def position(self, value, item=None):
        """Sets the position of the item.

        Args:
            value: The new position value.
            item: The item whose position is being set."""
        pass

    def position_begin_edit(self, item):
        """Invoked when a user starts dragging the node.

        Args:
            item: The item being edited."""
        pass

    def position_end_edit(self, item):
        """Invoked when a user has finished dragging the node and released the mouse.

        Args:
            item: The item that was edited."""
        pass

    @property
    def size(self, item):
        """The node size. Is used for nodes like Backdrop.

        Returns:
            The size of the item."""
        pass

    @size.setter
    def size(self, value, item=None):
        """The node position setter.

        Args:
            value: The new size value.
            item: The item whose size is being set."""
        pass

    def size_begin_edit(self, item):
        """Invoked when a user starts resizing the node.

        Args:
            item: The item being resized."""
        pass

    def size_end_edit(self, item):
        """Invoked when a user has finished resizing the node and released the mouse.

        Args:
            item: The item that was resized."""
        pass

    @property
    def description(self, item):
        """The text label that is displayed on the backdrop in the node graph.

        Returns:
            The description text of the item."""
        pass

    @description.setter
    def description(self, value, item=None):
        """Sets the description of the item.

        Args:
            value: The new description text.
            item: The item whose description is being set."""
        pass

    @property
    def display_color(self, item):
        """Gets the display color of the item.

        Returns:
            The display color of the item."""
        pass

    @display_color.setter
    def display_color(self, value, item=None):
        """Sets the display color of the item.

        Args:
            value: The new color value.
            item: The item whose display color is being set."""
        pass

    @property
    def stacking_order(self, item):
        """This value is a hint when an application cares about the visibility
        of a node and whether each node overlaps another.

        Returns:
            An integer representing the stacking order."""
        return 0

    @property
    def selection(self):
        """Gets the current selection list.

        Returns:
            The current selection list."""
        pass

    @selection.setter
    def selection(self, value: list):
        """Sets the selection list.

        Args:
            value: The new selection list."""
        pass

    def special_select_widget(self, node, node_widget):
        """Provides a special selection widget for the node if necessary.

        Args:
            node: The node for which the selection widget is to be provided.
            node_widget: The widget corresponding to the node.

        Returns:
            A widget to be used for the node's selection, or None if the default node_widget should be used."""
        # Returning None means node_widget will get used
        return None

    def destroy(self):
        """Perform any necessary cleanup when the GraphModel is destroyed."""
        pass

    @property
    def icon(self, item) -> Optional[Union[str, Any]]:
        """Gets the icon of the image.

        Returns:
            The icon of the item, which can be a string or any other type."""
        pass

    @icon.setter
    def icon(self, value: Optional[Union[str, Any]], item=None):
        """Sets the icon of the image.

        Args:
            value: The new icon value, which can be a string or any other type.
            item: The item whose icon is being set."""
        pass

    @property
    def preview(self, item) -> Optional[Union[str, Any]]:
        """Gets the preview of the image.

        Returns:
            The preview of the item, which can be a string or any other type."""
        pass

    @preview.setter
    def preview(self, value: Optional[Union[str, Any]], item=None):
        """Sets the preview of the image.

        Args:
            value: The new preview value, which can be a string or any other type.
            item: The item whose preview is being set."""
        pass

    @property
    def preview_state(self, item) -> PreviewState:
        """Gets the state of the preview of the node.

        Returns:
            The preview state of the item."""
        return GraphModel.PreviewState.NONE

    @preview_state.setter
    def preview_state(self, value: PreviewState, item=None):
        """Sets the state of the preview of the node.

        Args:
            value: The new preview state.
            item: The item whose preview state is being set."""
        pass

    @property
    def add_empty_input_port(self, item) -> bool:
        """Create IsolationGraphModel.EmptyPort for IsolationGraphModel.InputNode's.

        Returns:
            Defines whether or not an empty port should be created."""
        return True

    @property
    def add_empty_output_port(self, item) -> bool:
        """Create IsolationGraphModel.EmptyPort for IsolationGraphModel.OutputNode's.

        Returns:
            Defines whether or not an empty port should be created."""
        return True