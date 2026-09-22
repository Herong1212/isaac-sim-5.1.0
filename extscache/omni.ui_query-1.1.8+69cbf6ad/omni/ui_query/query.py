from typing import Dict, Optional, Union, List, Tuple, Callable
import omni.ui as ui
import carb


class OmniUIQuery:
    """A class for querying and retrieving widget information in Omni UI applications.

    This class provides class methods that assist in navigating and extracting details from widget hierarchies, including those found in Omni UI windows and containers. It supports operations such as obtaining widget paths, searching for widgets based on path queries, and processing widget tokens with wildcard options. The query system accepts widget path expressions that may include exact names, indices, and attribute predicates to refine search results.

    The methods in this class allow users to retrieve single or multiple widget instances by parsing and evaluating structured query strings. This functionality is useful for debugging user interface layouts and for dynamically exploring complex widget trees. The class leverages underlying Omni UI capabilities to iterate over widget children and evaluate widget attributes, making it easier to verify the structure and properties of UI components.

    Example usage:
    .. code-block:: python

        query = 'MainWindow//Frame/Button[0]'
        widget = OmniUIQuery.find_widget(query)
    """

    def __init__(self) -> None:
        """Initializes the OmniUIQuery instance."""
        pass

    @classmethod
    def _child_widget(cls, widget: ui.Widget, path_segment: str, show_warnings=True) -> Union[ui.Widget, None]:
        """
        Find a widget from a path given a starting widget
        """
        # print ("looking for", path_segment, "child of, ", widget)
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
            # NOTE: Wait until we have identifier support before activating this
            if adjusted_path_segment == a_child.identifier and index == None:
                return a_child
            elif adjusted_path_segment == a_child.__class__.__name__:
                if index == counter:
                    return a_child
                else:
                    counter += 1

        if not widget.__class__.__name__ == adjusted_path_segment:
            if show_warnings:
                carb.log_warn(f"Widget {widget} does not match path segment {adjusted_path_segment}")
            return None

        if not index:
            index = 0

        if index >= len(children):
            if show_warnings:
                carb.log_warn(f"Widget {widget} only has {len(children)} children, asked for index {index}")
            return None

        return children[index]

    @classmethod
    def _find_children_by_type(cls, widget: ui.Widget, path_segment: str) -> List[ui.Widget]:
        """
        given a starting widget, look at it's children to find the path segment requested, where
        the path segment index has a wildcard (e.g [*])
        Assumes input path_segment is like "Type[*]"
        """

        adjusted_path_segment = path_segment[: path_segment.find("[")]
        children = ui.Inspector.get_children(widget)
        children_of_type = [c for c in children if c.__class__.__name__ == adjusted_path_segment]
        return children_of_type

    @classmethod
    def get_widget_path(cls, window: ui.Window, widget: ui.Widget) -> Union[str, None]:
        """Given a Window and a Widget in that window, get its path.

        Args:
            window (ui.Window): Window instance to extract widget path.
            widget (ui.Widget): Widget instance to compute its path.

        Returns:
            Union[str, None]: Widget path if found, else None.
        """

        def traverse_widget_tree_for_match(
            starting_widget: ui.Widget, current_path: str, searched_widget: ui.Widget
        ) -> Union[str, None]:
            current_index = 0
            current_children = ui.Inspector.get_children(starting_widget)
            current_children = [c for c in current_children if c]

            type_frequencies = dict(zip([a.__class__ for a in current_children], [0] * len(current_children)))

            for a_child in current_children:
                class_name = a_child.__class__.__name__
                current_index = type_frequencies[a_child.__class__]
                widget_name = f"{class_name}[{current_index}]"
                type_frequencies[a_child.__class__] += 1

                if a_child == searched_widget:
                    p = f"{current_path}/{widget_name}"
                    return p

                if isinstance(a_child, ui.Container) or isinstance(a_child, ui.TreeView):
                    path = traverse_widget_tree_for_match(a_child, f"{current_path}/{widget_name}", searched_widget)
                    if path:
                        return path
            return None

        if window:
            start_path = f"{window.title}//Frame"
            return traverse_widget_tree_for_match(window.frame, start_path, widget)
        else:
            return None

    @classmethod
    def get_widget_children_with_path(cls, widget: ui.Widget, path: str) -> Dict[ui.Widget, str]:
        """Given a widget and its path, get all its child widgets with path.

        Args:
            widget (ui.Widget): Starting widget to retrieve children.
            path (str): Path for computing child widget paths.

        Returns:
            Dict[ui.Widget, str]: Mapping of child widgets to their paths.
        """
        widget_paths = {}
        current_children = ui.Inspector.get_children(widget)
        current_children = [c for c in current_children if c]
        type_frequencies = dict(zip([a.__class__ for a in current_children], [0] * len(current_children)))
        for a_child in current_children:
            class_name = a_child.__class__.__name__
            current_index = type_frequencies[a_child.__class__]
            widget_name = f"{class_name}[{current_index}]"
            widget_path = f"{path}/{widget_name}"
            widget_paths[a_child] = widget_path
            type_frequencies[a_child.__class__] += 1

        return widget_paths

    @classmethod
    def get_window_widget_paths(
        cls, window: ui.Window, widget_postfix_fn: Optional[Callable[[ui.Widget], str]] = None
    ) -> List[str]:
        """Given a window, get all its widgets' paths.

        Args:
            window (ui.Window): Window from which widget paths are derived.
            widget_postfix_fn (Optional[Callable[[ui.Widget], str]]): Optional function to add postfix to widget name.

        Returns:
            List[str]: List of widget paths for the window.
        """
        stack = [(window.frame, f"{window.title}//Frame")]
        widget_paths = [stack[0][1]]

        while len(stack) > 0:
            children = [c for c in ui.Inspector.get_children(stack[-1][0]) if c]

            type_frequencies = dict(zip([a.__class__ for a in children], [0] * len(children)))
            current_widget_paths = []

            for child in children:
                class_name = child.__class__.__name__
                current_index = type_frequencies[child.__class__]
                if widget_postfix_fn:
                    widget_postfix = widget_postfix_fn(child)
                else:
                    widget_postfix = ""
                widget_name = f"{class_name}[{current_index}]"
                widget_path = f"{stack[-1][1]}/{widget_name}{widget_postfix}"
                type_frequencies[child.__class__] += 1
                current_widget_paths.append(widget_path)
            stack.pop()
            stack += list(zip(children, current_widget_paths))
            widget_paths += current_widget_paths

        return widget_paths

    @classmethod
    def find_menu_item(cls, query: str) -> Optional[ui.Widget]:
        """TODO: This may now be legacy functionality after https://gitlab-master.nvidia.com/omniverse/kit/-/merge_requests/10402 is merged so need to see if its actually being used on 102 tests etc.

        Args:
            query (str): Query string to locate the menu item.

        Returns:
            Optional[ui.Widget]: Found menu item widget, or None if not found.
        """

        from omni.kit.mainwindow import get_main_window

        main_menu_bar = get_main_window().get_main_menu_bar()
        if not main_menu_bar:
            carb.log_warn("Current App doesn't have a MainMenuBar")
            return None

        tokens = query.split("/")
        print(tokens)
        current_children = main_menu_bar
        for i in range(1, len(tokens)):
            last = i == len(tokens) - 1
            print(tokens[i])
            child = cls._child_widget(current_children, tokens[i])
            if not child != 1:
                carb.log_warn(f"find_menu_item: Failed to find Child Widget at level {tokens[i]}")
                return None

            current_children = child

        return current_children

    @classmethod
    def _parse_input(cls, query: str) -> Tuple[bool, Union[ui.Widget, None], List[str], str]:
        """
        parse and validate the input.
        return widge tokens only ie sans window
        """
        # TODO Replace w regex
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
                carb.log_warn(f'Failed to find window: "{window_name}"')
                return False, None, [], widget_predicate

            if len(window_list) == 1:
                window = window_list[0]
            else:
                carb.log_warn(
                    f'found {len(window_list)} windows named "{window_name}". Using first visible window found'
                )
                window = None
                for win in window_list:
                    if win.visible:
                        window = win
                        break
                if not window:
                    carb.log_warn(f'Failed to find visible window: "{window_name}"')
                    return False, None, [], widget_predicate

            if not isinstance(window, ui.Window) and not isinstance(window, ui.ToolBar):
                carb.log_warn(f"window: {window_name} is not a ui.Window, query only works on ui.Window")
                return False, None, [], widget_predicate

        widget_tokens = widget_path.split("/")

        if window and not (widget_tokens[0] == "Frame" or widget_tokens[0] == "Frame[0]"):
            carb.log_warn("Query with a window currently only supports '<WindowName>//Frame/* type query")
            return False, None, [], widget_predicate

        if widget_tokens[-1] == "":
            widget_tokens = widget_tokens[:-1]

        return True, window, widget_tokens, widget_predicate

    @classmethod
    def _initialize_current_kids(cls, root_widgets, window):
        if root_widgets:
            return root_widgets
        return [window.frame] if window else []

    @classmethod
    def _process_widget_tokens(cls, curr_kids, widget_tokens, predicate, find_first) -> List[ui.Widget]:
        def _get_descendants(widget: ui.Widget) -> List[ui.Widget]:
            kids = []
            local_kids = ui.Inspector.get_children(widget)
            kids.extend(local_kids)
            for k in local_kids:
                child_kids = _get_descendants(k)
                kids.extend(child_kids)
            return kids

        def _get_descendants_with_predicate(widget: ui.Widget, predicate) -> Tuple[List[ui.Widget], bool]:
            stack = [widget]
            descendants = []
            attribute = ""
            if predicate:
                attribute = predicate.split("=")[0]
            while stack:
                current = stack.pop()
                children = ui.Inspector.get_children(current)
                if predicate:
                    for w in children:
                        if w and hasattr(w, attribute) and eval("w." + predicate):
                            return ([w], True)
                descendants.extend(children)
                stack.extend(children)

            return (descendants, False)

        curr_kids_tmp = []
        for i in range(len(widget_tokens)):
            if widget_tokens[i] == "Frame":
                continue

            curr_kids_tmp = []
            for current_child in curr_kids:
                if isinstance(current_child, ui.Window):
                    current_child = current_child.frame

                if widget_tokens[i] == "*":
                    curr_kids_tmp.extend(ui.Inspector.get_children(current_child))
                elif "[*]" in widget_tokens[i]:
                    curr_kids_tmp.extend(cls._find_children_by_type(current_child, widget_tokens[i]))
                elif widget_tokens[i] == "**":
                    if find_first:
                        children, found = _get_descendants_with_predicate(current_child, predicate)
                        if found:
                            return children
                        curr_kids_tmp.extend(children)
                    else:
                        curr_kids_tmp.extend(_get_descendants(current_child))
                else:
                    child = cls._child_widget(current_child, widget_tokens[i], show_warnings=False)
                    if child:
                        curr_kids_tmp.append(child)

            curr_kids = [kid for kid in curr_kids_tmp if ui.Inspector.get_children(kid)]
        return [w for w in curr_kids_tmp if w is not None]

    @classmethod
    def find_widgets(cls, query: str, root_widgets=[]) -> List[ui.Widget]:
        """Find a set of widgets that match our query.

        Args:
            query (str): Query string used to match widgets.
            root_widgets (list): List of root widgets to begin the search.

        Returns:
            List[ui.Widget]: List of widgets that match the query.
        """
        validate_status, window, widget_tokens, predicate = cls._parse_input(query)
        if not validate_status:
            return []

        curr_kids = cls._initialize_current_kids(root_widgets, window)
        if not curr_kids:
            return []

        curr_kids_tmp = cls._process_widget_tokens(curr_kids, widget_tokens, predicate, find_first=False)
        if predicate:
            curr_kids_tmp = [w for w in curr_kids_tmp if eval("w." + predicate)]
        return curr_kids_tmp

    @classmethod
    def find_first_widget(cls, query: str, root_widgets=[]) -> ui.Widget:
        """Find the first widget that matches our query.

        Args:
            query (str): Query string used to locate the widget.
            root_widgets (list): List of root widgets to begin the search.

        Returns:
            ui.Widget: The first matching widget if found, else None.
        """
        validate_status, window, widget_tokens, predicate = cls._parse_input(query)
        if not validate_status:
            return None

        curr_kids = cls._initialize_current_kids(root_widgets, window)
        if not curr_kids:
            return None

        curr_kids_tmp = cls._process_widget_tokens(curr_kids, widget_tokens, predicate, find_first=True)
        if predicate:
            curr_kids_tmp = [w for w in curr_kids_tmp if eval("w." + predicate)]
        return curr_kids_tmp[0] if curr_kids_tmp else None

    @classmethod
    def find_widget(cls, query: str) -> Union[ui.Widget, None]:
        """find a single widget given a full widget path

        Args:
            query (str): Full widget path string.

        Returns:
            Union[ui.Widget, None]: The widget matching the path, or None if not found.
        """

        validate_status, window, widget_tokens, _ = cls._parse_input(query)
        if not validate_status:
            return None

        if len(widget_tokens) == 1:
            return window.frame

        current_child = window.frame

        for i in range(1, len(widget_tokens)):
            child = cls._child_widget(current_child, widget_tokens[i])
            if not child:
                carb.log_warn(f'find_widget: from query "{query}" Failed to widget {widget_tokens[i]}')
                actual_kids = ui.Inspector.get_children(current_child)
                names = [a.identifier or f"{a.__class__.__name__}" for a in actual_kids]
                carb.log_warn(f"find_widget: did find widgets {names}")
                return None

            current_child = child

        return current_child
