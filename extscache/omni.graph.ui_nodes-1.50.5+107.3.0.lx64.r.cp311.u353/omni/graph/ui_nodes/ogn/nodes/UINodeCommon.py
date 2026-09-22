# Copyright (c) 2022, NVIDIA CORPORATION. All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

import ast
from typing import Dict, List, Optional, Tuple, Type, Union

import carb.events
import omni.client
import omni.graph.core as og
import omni.kit.app
import omni.ui as ui
import omni.usd

# TODO: Uncomment this when Viewport 2.0 becomes the default Viewport
# import omni.kit.viewport.window as vp


class OgnUINodeInternalState:  # pragma: no cover
    # This class is used by old widget nodes which have not yet been converted to use
    # OgWidgetNode. It will be removed once they are all converted.

    def __init__(self):
        self.created_widget = None
        self.created_frame = None


# TODO: Once OgnButton is gone, this class can be removed as well.
class OgWidgetNodeCallbacks:  # pragma: no cover
    """
    !!!BETA: DO NOT USE!!!

    A base class for callbacks used by nodes which create omni.ui widgets.
    """

    @staticmethod
    def get_property_names(widget: ui.Widget, writeable: bool) -> Optional[List[str]]:
        """
        Returns a dictionary containing those properties which are common to all ui.Widget.
        If 'writeable' is True then only those properties whose values can be set will be
        returned, otherwise only those whose value can be read will be returned.

        If 'widget' is not a valid widget a warning will be issued and None returned.
        """
        if not isinstance(widget, ui.Widget):
            carb.log_warn(f"Attempt to retrieve property names from non-widget object '{widget}'.")
            return None

        # Read/write properties
        props = [
            "enabled",  # bool
            "height",  # ui.Length
            "name",  # str
            "opaque_for_mouse_events",  # bool
            "selected",  # bool
            "skip_draw_when_clipped",  # bool
            "style_type_name_override",  # str
            "tooltip",  # str
            "tooltip_offset_x",  # float
            "tooltip_offset_y",  # float
            "visible",  # bool
            "visible_max",  # float
            "visible_min",  # float
            "width",  # ui.Length
        ]
        if not writeable:
            # Read-only properties
            props += [
                "computed_content_height",  # float
                "computed_content_width",  # float
                "computed_height",  # float
                "computed_width",  # float
                "dragging",  # bool
                "identifier",  # str
                "screen_position_x",  # float
                "screen_position_y",  # float
            ]
        return props

    @staticmethod
    def resolve_output_property(widget: ui.Widget, property_name: str, attribute: og.Attribute):
        """
        Resolves the type of an output property based on a widget attribute.
        This assumes the output attribute has the 'unvalidated' metadata set to true

        OmniGraphError raised on failure.
        """
        if not isinstance(widget, ui.Widget):
            raise og.OmniGraphError(f"Attempt to resolve property on non-widget object '{widget}'.")
        widget_desc = widget.identifier or repr(widget)
        if not hasattr(widget, property_name):
            raise og.OmniGraphError(f"Widget '{widget_desc}' has no property '{property_name}'.")
        prop_value = getattr(widget, property_name)
        if isinstance(prop_value, bool):
            out_type = "bool"
        elif isinstance(prop_value, int):
            out_type = "int"
        elif isinstance(prop_value, float):
            out_type = "double"
        elif isinstance(prop_value, (str, ui.Length, ui.Direction)):
            out_type = "string"
        else:
            raise og.OmniGraphError(f"Cannot resolve output type: {type(prop_value)}")

        attr_type = og.AttributeType.type_from_ogn_type_name(out_type)
        attr_type_valid = attr_type.base_type != og.BaseDataType.UNKNOWN
        if attribute.get_resolved_type().base_type != og.BaseDataType.UNKNOWN and (
            not attr_type_valid or attr_type != attribute.get_resolved_type()
        ):
            attribute.set_resolved_type(og.Type(og.BaseDataType.UNKNOWN))
        if attr_type_valid and attribute.get_resolved_type().base_type == og.BaseDataType.UNKNOWN:
            attribute.set_resolved_type(attr_type)

    @staticmethod
    def get_property_value(widget: ui.Widget, property_name: str, attribute: og.RuntimeAttribute):
        """
        Retrieves the value of a property from a widget and writes it to the given node attribute.

        OmniGraphError raised on failure.
        """
        if not isinstance(widget, ui.Widget):
            raise og.OmniGraphError(f"Attempt to get property value from non-widget object '{widget}'.")
        widget_desc = widget.identifier or repr(widget)
        if not hasattr(widget, property_name):
            raise og.OmniGraphError(f"Widget '{widget_desc}' has no property '{property_name}'.")
        prop_value = getattr(widget, property_name)
        prop_type = type(prop_value)
        if prop_type in (bool, int, float, str):
            try:
                attribute.value = prop_value
                return  # Property value is retrieved
            except ValueError:
                pass
        # XXX: To preserve the 'units' (px, fr, %) we may want to split the output of these into a (value, unit) pair
        elif prop_type in (ui.Length, ui.Direction):
            try:
                attribute.value = str(prop_value)
                return
            except ValueError:
                pass
        else:
            raise og.OmniGraphError(f"Unsupported property type: {prop_type}")
        raise og.OmniGraphError(f"Attempt to get property '{property_name}' from widget '{widget_desc}' failed.")

    @staticmethod
    def set_property_value(widget: ui.Widget, property_name: str, attribute: og.RuntimeAttribute):
        """
        Retrieves the value of a node attribute and writes it to the given widget property.

        OmniGraphError raised on failure.
        """
        if not isinstance(widget, ui.Widget):
            raise og.OmniGraphError(f"Attempt to set property value on non-widget object '{widget}'.")
        widget_desc = widget.identifier or repr(widget)
        if not hasattr(widget, property_name):
            raise og.OmniGraphError(f"Widget '{widget_desc}' has no property '{property_name}'.")
        value = attribute.value
        prop_type = type(getattr(widget, property_name))
        if prop_type == str and property_name == "image_url":
            try:
                setattr(widget, property_name, resolve_image_url(prop_type(value)))
                return
            except ValueError:
                pass
        elif prop_type in (bool, int, float, str):
            try:
                setattr(widget, property_name, prop_type(value))
                return
            except ValueError:
                pass
        elif prop_type == ui.Length:
            length = to_ui_length(value)
            if length is not None:
                try:
                    setattr(widget, property_name, length)
                    return
                except ValueError:
                    pass
                return
        elif prop_type == ui.Direction:
            direction = to_ui_direction(value)
            if direction is not None:
                try:
                    setattr(widget, property_name, direction)
                    return
                except ValueError:
                    pass
                return
        else:
            raise og.OmniGraphError(f"Unsupported property type: {prop_type}")

        if prop_type == ui.Length:
            carb.log_warn(
                f"{prop_type} properties may be set from int or float values, or from string values containing "
                "an int or float optionally followed by 'px' for pixels (e.g. '5px'), 'fr' for fractional amounts "
                "('0.3fr') or '%' for percentages ('30%'). If no suffix is given then 'px' is assumed."
            )

        if isinstance(value, str) and prop_type != str:
            raise og.OmniGraphError(
                f"Cannot set value onto widget '{widget_desc}' property '{property_name}': "
                f"string value '{value}' cannot be converted to {prop_type}."
            )

        raise og.OmniGraphError(
            f"Cannot set value of type {type(value)} onto widget '{widget_desc}' "
            f"property '{property_name}' (type {prop_type})"
        )

    @staticmethod
    def get_style_element_names(widget: ui.Widget, writeable: bool) -> List[str]:
        """
        Returns the names of those style elements which are common to all ui.Widget.
        If 'writeable' is True then only those elements whose values can be set will be
        returned, otherwise only those whose value can be read will be returned.

        If 'widget' is not a valid widget a warning will be issued and None returned.
        """
        if not isinstance(widget, ui.Widget):
            carb.log_warn(f"Attempt to retrieve style element names from non-widget object '{widget}'.")
            return None

        # There are currently no style elements common to all widgets.
        return []

    @staticmethod
    def get_style_value(widget: ui.Widget, element_name: str, attribute: og.RuntimeAttribute) -> bool:
        """
        Retrieves the value of a style element from a widget and writes it to the given node attribute.

        Returns True on success, False on failure.
        """
        if not isinstance(widget, ui.Widget):
            carb.log_warn(f"Attempt to get style element from non-widget object '{widget}'.")
            return None
        # TBD
        return False

    @staticmethod
    def set_style_value(widget: ui.Widget, element_name: str, attribute: og.RuntimeAttribute) -> bool:
        """
        Retrieves the value of a style element from a node attribute and sets it on the given widget.

        Returns True on success, False on failure.
        """
        if not isinstance(widget, ui.Widget):
            carb.log_warn(f"Attempt to set style element on non-widget object '{widget}'.")
            return None
        # TBD
        return False


# TODO: Once OgnButton is gone, this class can be removed as well.
class OgWidgetNode(OgWidgetNodeCallbacks):  # pragma: no cover
    """
    !!!BETA: DO NOT USE!!!

    A base class for nodes which create omni.ui widgets.
    """

    @classmethod
    def register_widget(cls, context: og.GraphContext, widget_id: str, widget: omni.ui.Widget):
        """
        Register a widget by the GraphContext in which it was generated and a unique id within that context.
        """
        register_widget(context, widget_id, widget, cls)

    @classmethod
    def deregister_widget(cls, context: og.GraphContext, widget_id: str):
        """
        Deregister a previously registered widget.
        """
        if context and widget_id:
            remove_registered_widgets(context, widget_id)


######################################################################################################
#
# Widget Registry
#
# The widget registry provides a mapping between a widget identifier and the widget itself. Widget
# identifiers are specific to the graph context in which their widgets were created. This helps to avoid clashing
# identifiers, particularly when graphs are instanced.
#
# TODO: Internally we use the widget's full path string to identify the widget uniquely within the application.
#       This is quite inefficient as it requires traversing the entire widget tree of the application each
#       time we want to convert a path to a widget or vice-versa.
#
#       We cannot store the widget object itself in the registry because that would increment its
#       reference count and keep the widget (and its window) alive after they should have been destroyed.
#
#       Using a weak reference won't work either because the widget objects we see in Python are just temporary
#       wrappers around the actual C++ objects. A weak reference would be invalidated as soon as the wrapper was
#       destroyed, even though the widget itself might still be alive.
#
#       get_registered_widget() ensures that the widget registry for a given context does not
#       grow without bound, but we still need a way to either automatically clear a widget's entry when it is
#       destroyed, or completely clear the entries for a given context when that context is destroyed.
#       One approach would be to have the SetViewportMode node clear the registry of all widgets in its graph
#       context when it destroys its OG overlay, however since its extension doesn't depend on this one, it would
#       have to monitor the loading and unloading of the omni.graph.action extension.
def register_widget(
    context: og.GraphContext, widget_id: str, widget: ui.Widget, callbacks: Type[OgWidgetNodeCallbacks]
):  # pragma: no cover
    """
    !!!BETA: DO NOT USE!!!

    Register a widget by the GraphContext in which it was generated and a unique id within that context.

    'callbacks' is either a sub-class of OgWidgetNodeCallbacks or some other object which provides the same set of
    static methods (the class methods are not necessary).
    """
    if context and widget_id and widget:
        path = find_widget_path(widget)
        if path:
            _widget_registry[(context, widget_id)] = path
            _widget_callbacks[path] = callbacks


def get_registered_widget(context: og.GraphContext, widget_id: str) -> Optional[ui.Widget]:  # pragma: no cover
    """
    !!!BETA: DO NOT USE!!!

    Returns a widget given the GraphContext in which it was created and its unique id within that context.
    If there is no such widget then None is returned.
    """
    path = _widget_registry.get((context, widget_id))
    if path:
        widget = find_widget_among_all_windows(path)
        if not widget:
            # This must be a deleted widget. Remove it from the registry.
            remove_registered_widgets(context, widget_id)
        return widget
    return None


def get_registered_widgets(
    context: og.GraphContext = None, widget_id: str = None
) -> List[ui.Widget]:  # pragma: no cover
    """
    !!!BETA: DO NOT USE!!!

    Returns all the widgets which match the search parameters. If 'context' is None then all contexts
    will be searched. If 'id' is None then all widgets within the searched context(s) will be returned.
    """
    return [
        find_widget_among_all_windows(path)
        for (_context, _id), path in _widget_registry.items()
        if (context is None or _context == context) and (widget_id is None or _id == widget_id)
    ]


def remove_registered_widgets(context: og.GraphContext, widget_id: str = None):  # pragma: no cover
    """
    !!!BETA: DO NOT USE!!!

    Removes the specified widget from the registry. If 'widget_id' is not specified then all widgets
    registered under the given context will be removed.
    """
    if widget_id:
        keys_to_remove = [(context, widget_id)]
    else:
        keys_to_remove = [(_ctx, _id) for (_ctx, _id) in _widget_registry if _ctx == context]
    for key in keys_to_remove:
        path = _widget_registry.pop(key)
        _widget_callbacks.pop(path, None)


def get_unique_widget_identifier(db: og.Database) -> str:  # pragma: no cover
    """
    !!!BETA: DO NOT USE!!!

    Returns a widget identifier which is unique within the current GraphContext.
    The identifier is taken from the 'widgetIdentifier' input attribute, or the name
    of the node if 'widgetIdentifier' is not set. If the identifier is already in
    use then a suffix will be added to make it unique.
    """
    base_id = db.inputs.widgetIdentifier or db.node.get_prim_path().replace("/", ":")

    counter = 0
    final_id = base_id
    while get_registered_widget(db.abi_context, final_id) is not None:
        counter += 1
        final_id = base_id + "_" + str(counter)

    return final_id


# Mapping between widget identifiers and widgets.
#
# Key: (graph context, widget identifier)
# Value: full path to the widget
_widget_registry: Dict[Tuple[og.GraphContext, str], str] = {}


# Callbacks to operate on per-widget data (e.g. properties)
#
# Key: full path to the widget
# Value: class object derived from OgWidgetNodeCallbacks
_widget_callbacks: Dict[str, Type[OgWidgetNodeCallbacks]] = {}


######################################################################################################


def to_ui_direction(value: str) -> ui.Direction:  # pragma: no cover
    """
    !!!BETA: DO NOT USE!!!

    Convert the input value to a ui.Direction.
    """
    if value == "LEFT_TO_RIGHT":
        return ui.Direction.LEFT_TO_RIGHT
    if value == "RIGHT_TO_LEFT":
        return ui.Direction.RIGHT_TO_LEFT
    if value == "TOP_TO_BOTTOM":
        return ui.Direction.TOP_TO_BOTTOM
    if value == "BOTTOM_TO_TOP":
        return ui.Direction.BOTTOM_TO_TOP
    if value == "BACK_TO_FRONT":
        return ui.Direction.BACK_TO_FRONT
    if value == "FRONT_TO_BACK":
        return ui.Direction.FRONT_TO_BACK
    return None


def to_ui_length(value: Union[float, int, str]) -> ui.Length:  # pragma: no cover
    """
    !!!BETA: DO NOT USE!!!

    Convert the input value to a ui.Length.
    """
    if isinstance(value, (float, int)):
        return ui.Length(value)
    if not isinstance(value, str):
        return None
    unit_type = ui.UnitType.PIXEL
    if value.endswith("fr"):
        unit_type = ui.UnitType.FRACTION
        value = value[:-2]
    elif value.endswith("%"):
        unit_type = ui.UnitType.PERCENT
        value = value[:-1]
    elif value.endswith("px"):
        value = value[:-2]
    try:
        return ui.Length(int(value), unit_type)
    except ValueError:
        try:
            return ui.Length(float(value), unit_type)
        except ValueError:
            return None


def resolve_image_url(url: str) -> str:  # pragma: no cover
    if not url:
        return url

    edit_layer = omni.usd.get_context().get_stage().GetEditTarget().GetLayer()
    if edit_layer.anonymous:
        return url

    return omni.client.combine_urls(edit_layer.realPath, url).replace("\\", "/")


def resolve_style_image_urls(style_dict: Optional[Dict]) -> Optional[Dict]:  # pragma: no cover
    if not style_dict:
        return style_dict

    edit_layer = omni.usd.get_context().get_stage().GetEditTarget().GetLayer()
    if edit_layer.anonymous:
        return style_dict

    for value in style_dict.values():
        if isinstance(value, dict):
            url = value.get("image_url")
            if url:
                value["image_url"] = omni.client.combine_urls(edit_layer.realPath, url).replace("\\", "/")

    return style_dict


def to_ui_style(style_string: str) -> Optional[Dict]:  # pragma: no cover
    """
    !!!BETA: DO NOT USE!!!

    Converts a string containing a style description into a Python dictionary suitable for use with
    ui.Widget.set_style().

    Returns None if style_string is empty.

    Raises SyntaxError if the string contains invalid style syntax.
    Raises ValueError if 'style_string' is not a string.
    """

    def fmt_syntax_err(err):
        # Syntax errors are not very descriptive. Let's do a bit better.
        msg = "Invalid style syntax"
        # Don't include the message if it's just "invalid syntax".
        if err.msg.lower() != "invalid syntax":
            msg += " (" + err.msg + ")"
        # Include the text of the line where the error was found, with an indicator at the point of the error.
        # It would be nice to output this as two lines with the indicator indented beneath the error, but by the
        # time the message reached the node's tooltip all such formatting would be lost. So we settle for an
        # inline indicator.
        text = err.text[: err.offset] + "^^^" + err.text[err.offset :]
        # If the line is too long, elide the start and/or end of it.
        if len(text) > 50:
            right = min(err.offset + 25, len(text))
            left = max(right - 50, 0)
            if len(text) - right > 5:
                text = text[:right] + "..."
            if left > 5:
                text = "..." + text[left:]
        # Include the line number and offset so that the callers don't all have to do it themselves.
        return msg + f": line {err.lineno} offset {err.offset}:  " + text

    def fmt_value_err(err):
        # Value errors generally reflect some bad internal state of the parser. They only give us a message with
        # no indication of where in input the error occurred.
        return f"Invalid style syntax ({err.args[0]})."

    if not style_string:
        return None
    if not isinstance(style_string, str):
        raise ValueError(f"Style must be a string, not type {type(style_string)}.")

    try:
        return resolve_style_image_urls(ast.literal_eval(style_string))
    except SyntaxError as err:
        err.msg = fmt_syntax_err(err)
        raise
    except ValueError as err:
        syn_err = SyntaxError(fmt_value_err(err))
        syn_err.text = style_string
        raise syn_err from err


######################################################################################################
# All code in this block deal with Viewport 1.0
# TODO: Remove this block of code when Viewport 2.0 becomes the default Viewport


def _parse_input(query, search_among_all_windows=False):  # pragma: no cover
    """A variation of OmniUIQuery._parse_input that allows you to search among all windows with the same name"""

    tokens = query.split("//")
    window_name = tokens[0] if len(tokens) > 1 else None
    widget_predicate = ""
    widget_part = tokens[1] if len(tokens) > 1 else tokens[0]
    widget_part_list = widget_part.split(".", maxsplit=1)
    widget_path = widget_part_list[0]
    if len(widget_part_list) > 1:
        widget_predicate = widget_part_list[1]

    window = None

    if window_name:
        windows = ui.Workspace.get_windows()
        window_list = []
        for window in windows:
            if window.title == window_name:
                window_list.append(window)

        if not window_list:
            carb.log_warn(f"Failed to find window: '{window_name}'")
            return False, None, [], widget_predicate

        if search_among_all_windows:
            window = []
            for current_window in window_list:
                if isinstance(current_window, ui.Window):
                    window.append(current_window)

            if len(window) == 0:
                carb.log_warn(f"Failed to find a ui.Window named {window_name}, query only works on ui.Window")
                return False, None, [], widget_predicate

        else:
            if len(window_list) == 1:
                window = window_list[0]

            else:
                carb.log_warn(
                    f"found {len(window_list)} windows named '{window_name}'. Using first visible window found"
                )
                window = None
                for win in window_list:
                    if win.visible:
                        window = win
                        break
                if not window:
                    carb.log_warn(f"Failed to find visible window: '{window_name}'")
                    return False, None, [], widget_predicate

            if not isinstance(window, ui.Window) and not isinstance(window, ui.ToolBar):
                carb.log_warn(f"window: {window_name} is not a ui.Window, query only works on ui.Window")
                return False, None, [], widget_predicate

    widget_tokens = widget_path.split("/")

    if window and not (widget_tokens[0] == "Frame" or widget_tokens[0] == "Frame[0]"):
        carb.log_warn("Query with a window currently only supports '<WindowName>//Frame/*' type query")
        return False, None, [], widget_predicate

    if widget_tokens[-1] == "":
        widget_tokens = widget_tokens[:-1]

    return True, window, widget_tokens, widget_predicate


# This is a slightly simplified version of omni.ui_query.OmniUiQuery._child_widget(). We've copied it here
# because omni.ui_query isn't part of Kit Core so we shouldn't have a dependency on it.
def __find_child_widget(widget: ui.Widget, path_segment: str) -> Optional[ui.Widget]:
    """
    Find a widget from a path given a starting widget
    """
    adjusted_path_segment = path_segment
    # when we don't have index we assume it is the first one
    index = None
    if "[" in adjusted_path_segment:
        index = int(adjusted_path_segment.split("[")[-1].split("]")[0])
        adjusted_path_segment = adjusted_path_segment.split("[")[0]

    children = ui.Inspector.get_children(widget)

    counter = 0
    for a_child in children:
        if not a_child:
            continue
        if adjusted_path_segment == a_child.identifier and index is None:
            return a_child
        if adjusted_path_segment == a_child.__class__.__name__ and index == counter:
            return a_child
        counter += 1

    if widget.__class__.__name__ != adjusted_path_segment:
        return None

    if not index:
        index = 0

    if index >= len(children):
        return None

    return children[index]


# This is a duplicate of omni.ui_query.OmniUiQuery.get_widget_path(). We've copied it here
# because omni.ui_query isn't part of Kit Core so we shouldn't have a dependency on it.
def __get_widget_path(window: ui.Window, widget: ui.Widget) -> Optional[str]:
    """
    Given a Window and a Widget in that window, get its path
    """

    def traverse_widget_tree_for_match(
        starting_widget: ui.Widget, current_path: str, searched_widget: ui.Widget
    ) -> Optional[str]:
        current_index = 0
        current_children = ui.Inspector.get_children(starting_widget)
        current_children = [c for c in current_children if c]

        type_frequencies = dict(zip([a.__class__ for a in current_children], [0] * len(current_children)))

        for a_child in current_children:
            class_name = a_child.__class__.__name__
            current_index = type_frequencies[a_child.__class__]
            widget_name = a_child.identifier or f"{class_name}[{current_index}]"
            type_frequencies[a_child.__class__] += 1

            if a_child == searched_widget:
                p = f"{current_path}/{widget_name}"
                return p

            if isinstance(a_child, (ui.Container, ui.TreeView)):
                path = traverse_widget_tree_for_match(a_child, f"{current_path}/{widget_name}", searched_widget)
                if path:
                    return path
        return None

    if window:
        start_path = f"{window.title}//Frame"
        return traverse_widget_tree_for_match(window.frame, start_path, widget)
    return None


def __search_for_widget_in_window(
    window: ui.Window, widget_tokens: List[str]
) -> Optional[ui.Widget]:  # pragma: no cover
    current_child = window.frame

    for token in widget_tokens[1:]:
        child = __find_child_widget(current_child, token)
        if not child:  # Unable to find the widget in the current window
            return None
        current_child = child

    return current_child


def find_widget_among_all_windows(query):  # pragma: no cover
    """Find a single widget given a full widget path.
    If there are multiple windows with the same name, search among all of them."""

    validate_status, windows, widget_tokens, _ = _parse_input(query, search_among_all_windows=True)
    if not validate_status:
        return None

    if len(widget_tokens) == 1:
        return windows[0].frame

    for window in windows:
        search_result = __search_for_widget_in_window(window, widget_tokens)
        if search_result is not None:
            return search_result

    return None


def get_widget_window(widget_or_path: Union[ui.Widget, str]) -> Optional[ui.Window]:  # pragma: no cover
    if isinstance(widget_or_path, ui.Widget):
        for window in ui.Workspace.get_windows():
            if isinstance(window, ui.Window) and __get_widget_path(window, widget_or_path) is not None:
                return window
    elif isinstance(widget_or_path, str):
        found_it, windows, widget_tokens, _ = _parse_input(widget_or_path, search_among_all_windows=True)
        if not found_it:
            return None

        if len(widget_tokens) == 1:
            return windows[0]

        for window in windows:
            search_result = __search_for_widget_in_window(window, widget_tokens)
            if search_result is not None:
                return window

    return None


def get_parent_widget(db: og.Database):  # pragma: no cover
    """Given the path to the parent widget db.inputs.parentWidgetPath, find the parent widget at that path.
    If the path is empty, then the parent widget will be the viewport frame."""
    parent_widget_path = db.inputs.parentWidgetPath

    if not parent_widget_path:
        # This widget is a direct child of the viewport frame
        if not hasattr(db.per_instance_state, "window"):
            db.per_instance_state.window = ui.Window("Viewport")
        db.per_instance_state.window.visible = True
        parent_widget = db.per_instance_state.window.frame
        return parent_widget

    # This widget is nested under some other widget
    parent_widget = find_widget_among_all_windows(parent_widget_path)
    if not parent_widget:
        db.log_error("Cannot find the parent widget at the specified path!")
        return None
    return parent_widget


def find_widget_path(widget: ui.Widget, window: Optional[ui.Widget] = None):  # pragma: no cover
    """Find the path to the widget within the given window. If no window is provided then search all windows."""
    if window:
        return __get_widget_path(window, widget)

    for w in ui.Workspace.get_windows():
        if isinstance(w, ui.Window):
            query_result = __get_widget_path(w, widget)
            if query_result is not None:
                return query_result
    return None


######################################################################################################
# All code in this block deal with Viewport 2.0
# TODO: Uncomment this block of code when Viewport 2.0 becomes the default Viewport
# def get_unique_frame_identifier(db):
#     """Return a unique identifier for the created viewport frame"""
#     unique_widget_identifier = get_unique_widget_identifier(db)
#     return "omni.graph.action.ui_node." + unique_widget_identifier
#
#
# def get_default_viewport_window():
#     default_viewport_name = vp.ViewportWindowExtension.WINDOW_NAME
#     for window in vp.get_viewport_window_instances():
#         if window.name == default_viewport_name:
#             return window
#     return None
#
#
# def get_parent_widget(db):
#     """Given the path to the parent widget db.inputs.parentWidgetPath, find the parent widget at that path.
#     If the path is empty, then the parent widget will be the viewport frame."""
#     parent_widget_path = db.inputs.parentWidgetPath
#
#     if not parent_widget_path:
#         # This widget is a direct child of the viewport frame
#         viewport_window = get_default_viewport_window()
#         if not viewport_window:
#             db.log_error("Cannot find the default viewport window!")
#             return None
#         frame_identifier = get_unique_frame_identifier(db)
#         viewport_frame = viewport_window.get_frame(frame_identifier)
#         return viewport_frame
#
#     else:
#         # This widget is nested under some other widget
#         parent_widget = OmniUIQuery.find_widget(parent_widget_path)
#         if not parent_widget:
#             db.log_error("Cannot find the parent widget at the specified path!")
#             return None
#         return parent_widget
#
#
# def find_widget_path(widget: ui.Widget):
#     """Given a widget in the default viewport window, find the path to the widget"""
#     viewport_window = get_default_viewport_window()
#     if not viewport_window:
#         return None
#     return __get_widget_path(viewport_window, widget)
######################################################################################################


def tear_down_widget(db: og.Database) -> bool:  # pragma: no cover
    if db.per_instance_state.created_widget is None:
        db.log_error("Cannot tear down a widget that has not been created")
        return False

    # Since ui.Frame can only have one child, this code effectively replaces the previous child of ui.Frame
    # with an empty ui.Placer, and the previous child will be automatically garbage collected.
    # Due to the limitations of omni.ui, we cannot remove child widgets from the parent, so this is the best we can do.
    db.per_instance_state.created_widget = None
    with db.per_instance_state.created_frame:
        ui.Placer()
    db.per_instance_state.created_frame = None

    db.outputs.created = og.ExecutionAttributeState.DISABLED
    db.outputs.widgetPath = ""
    return True


def show_widget(db: og.Database) -> bool:  # pragma: no cover
    if db.per_instance_state.created_widget is None:
        db.log_error("Cannot show a widget that has not been created")
        return False
    db.per_instance_state.created_widget.visible = True
    db.outputs.created = og.ExecutionAttributeState.DISABLED
    # Keep db.outputs.widgetPath unchanged
    return True


def hide_widget(db: og.Database) -> bool:  # pragma: no cover
    if db.per_instance_state.created_widget is None:
        db.log_error("Cannot hide a widget that has not been created")
        return False
    db.per_instance_state.created_widget.visible = False
    db.outputs.created = og.ExecutionAttributeState.DISABLED
    # Keep db.outputs.widgetPath unchanged
    return True


def enable_widget(db: og.Database) -> bool:  # pragma: no cover
    if db.per_instance_state.created_widget is None:
        db.log_error("Cannot enable a widget that has not been created")
        return False
    db.per_instance_state.created_widget.enabled = True
    db.outputs.created = og.ExecutionAttributeState.DISABLED
    # Keep db.outputs.widgetPath unchanged
    return True


def disable_widget(db: og.Database) -> bool:  # pragma: no cover
    if db.per_instance_state.created_widget is None:
        db.log_error("Cannot disable a widget that has not been created")
        return False
    db.per_instance_state.created_widget.enabled = False
    db.outputs.created = og.ExecutionAttributeState.DISABLED
    # Keep db.outputs.widgetPath unchanged
    return True


def registered_event_name(event_name):  # pragma: no cover
    """Returns the internal name used for the given custom event name"""
    n = "omni.graph.action." + event_name
    return carb.events.type_from_string(n)


# TODO: Once OgnOnWidgetClicked and OgnOnWidgetValueChanged are gone, this class can be removed as well.
class OgnUIEventNodeInternalState:  # pragma: no cover
    def __init__(self):
        """Instantiate the per-node state information."""
        # This subscription object controls the lifetime of our callback,
        # it will be cleaned up automatically when our node is destroyed
        self.sub = None
        # Set when the callback has triggered
        self.is_set = False
        # The last payload received
        self.payload = None
        # The event name we used to subscribe
        self.sub_event_name = ""
        # The node instance handle
        self.node = None

    def on_event(self, custom_event):
        """The event callback"""
        if custom_event is None:
            return
        self.is_set = True
        self.payload = custom_event.payload
        # Tell the evaluator we need to be computed
        if self.node.is_valid():
            self.node.request_compute()

    def first_time_subscribe(self, node: og.Node, event_name: str) -> bool:
        """Checked call to set up carb subscription
        Args:
            node: The node instance
            event_name: The name of the carb event
        Returns:
            True if we subscribed, False if we are already subscribed
        """
        if self.sub is not None and self.sub_event_name != event_name:
            # event name changed since we last subscribed, unsubscribe
            self.sub.unsubscribe()
            self.sub = None

        if self.sub is None:
            # Add a subscription for the given event name. This is a pop subscription,
            # so we expect a 1-frame lag between send and receive
            reg_event_name = registered_event_name(event_name)
            message_bus = omni.kit.app.get_app().get_message_bus_event_stream()
            self.sub = message_bus.create_subscription_to_pop_by_type(reg_event_name, self.on_event)
            self.sub_event_name = event_name
            self.node = node
            return True

        return False

    def try_pop_event(self):
        """Pop the payload of the last event received, or None if there is no event to pop"""
        if self.is_set:
            self.is_set = False
            payload = self.payload
            self.payload = None
            return payload
        return None

    def release(self):
        # Unsubscribe right away instead of waiting for GC cleanup, we don't want our callback firing
        # after the node has been released.
        if self.sub:
            self.sub.unsubscribe()
        self.sub = None
