import importlib
import webbrowser
from collections import defaultdict
from functools import partial
from typing import Any, Callable, Optional, Tuple

import omni.graph.core as og
import omni.graph.tools as ogt
import omni.kit
import omni.ui as ui
from omni.kit.widget.graph import IsolationGraphModel
from pxr import Sdf, Usd

from . import graph_config
from .compounds import CompoundUtils
from .graph_model import OmniGraphModel
from .graph_operations import promote_unconnected_to_compound
from .multifield_dialog import MultiFieldDialog
from .virtual_node_helper import VirtualNodeHelper

MENU_GRAPH = "menu_graph.svg"
COMPOUND_SUBGRAPH_NODE_TYPE = "omni.graph.nodes.CompoundSubgraph"


# ---------------------------------------------------------------------------------------
# TODO -- this needs to go into a common utility somewhere
def _get_node_safe(item) -> og.Node:
    try:
        return og.Controller.node(item)
    except og.OmniGraphError:
        return None


# ---------------------------------------------------------------------------------------
def _build_node_context_menu(
    widget, prim: Usd.Prim | None, filter_fn: Optional[Callable[[Sdf.Path, Sdf.PrimSpec], bool]] = None
) -> ui.Menu:  # noqa: C901
    """
    Builds the node context menu

    Args:
        widget: The graph widget
        prim: The item the click occurred on, if any
        filter_fn: Filter applied when pasting, optional

    Returns:
        The context menu to show
    """
    traversal_available = True
    try:
        # The traversal functions may not be available in old versions of kit
        from omni.graph.core import traverse_downstream_graph, traverse_upstream_graph
    except ImportError:
        traversal_available = False

    model = widget.model
    view = widget._graph_view  # noqa: protected-access
    current_graph = widget.current_compound

    def _to_og_prim(item):
        if isinstance(item, (IsolationGraphModel.InputNode, IsolationGraphModel.OutputNode)):
            return item.source
        if model.get_node_from_prim(item):
            return item
        return None

    fallback = [prim] if prim else []

    # the view selected nodes. Includes og nodes, pseudo nodes (notes, backgrounds) and compound graphs
    selected_view_items = view.selection or fallback

    # the current selected og prims. Includes nodes and compound graphs
    selected_og_prims = [_to_og_prim(p) for p in selected_view_items if _to_og_prim(p)]

    # the selection of prims excluding input and output proxy nodes. Includes og nodes and pseudo nodes
    selected_non_graph_items = [p for p in selected_view_items if not VirtualNodeHelper.is_virtual_node(p)]

    # the selection of node only prims
    selected_node_only_prims = [p for p in selected_og_prims if not VirtualNodeHelper.is_virtual_node(p)]

    def _select_all_nodes():
        """Select all the nodes in the graph."""
        model.selection = model[current_graph].nodes

    def _clear_node_selection():
        """Clear the node selection."""
        model.selection = []

    def _copy_selected_nodes():
        """Copy selected nodes."""
        action = omni.kit.actions.core.get_action_registry().get_action("omni.kit.stage.copypaste", "stage_copy")
        action.execute()

    def _paste_nodes():
        """Paste copied nodes"""
        action = omni.kit.actions.core.get_action_registry().get_action("omni.kit.stage.copypaste", "stage_paste")
        if not action:
            return
        # Get the mouse position in canvas space
        canvas_pos = None
        if hasattr(widget, "_get_graph_view_hovered_position") and hasattr(view, "screen_to_canvas"):
            mouse_position = widget._get_graph_view_hovered_position()  # noqa: protected-access
            if mouse_position is not None:
                canvas_pos = view.screen_to_canvas(*mouse_position)

        params = dict(action.parameters)

        def filter_wrapper(prim_spec: Sdf.PrimSpec):
            return filter_fn(current_graph.GetPath(), prim_spec) if filter_fn else True

        if "keep_inputs" in params:
            action.execute(
                root=current_graph.GetPath(), keep_inputs=False, position=canvas_pos, filter_fn=filter_wrapper
            )
        else:
            action.execute()

    def _select_downstream_nodes():
        """Select the nodes downstream from the currently selected nodes."""
        new_selection = traverse_downstream_graph(selected_og_prims)
        model.selection = [og.Controller.prim(p) for p in new_selection]

    def _select_upstream_nodes():
        """Select the nodes upstream of the currently selected nodes."""
        new_selection = traverse_upstream_graph(selected_og_prims)
        model.selection = [og.Controller.prim(p) for p in new_selection]

    def _select_execution_tree():
        """
        Selects the nodes connected by execution ports to the selected nodes,
        both upstream and downstream.
        """
        upstream = traverse_upstream_graph(selected_og_prims, attribute_predicate=model.is_execution)
        downstream = traverse_downstream_graph(selected_og_prims, attribute_predicate=model.is_execution)
        execution_chain = upstream.union(downstream)
        model.selection = [og.Controller.prim(p) for p in execution_chain]

    def _can_delete_selected_nodes():
        """Check if the delete selected nodes can be enabled"""
        # filter out virtual nodes, to avoid deleting them
        return bool(selected_non_graph_items)

    def _delete_selected_nodes():
        """Delete the selected nodes."""
        paths = [n.GetPath() for n in selected_non_graph_items]
        omni.kit.commands.execute("DeletePrims", paths=paths)

    def _can_duplicate_selected_nodes():
        """Check if the duplicate selected nodes can be enabled"""
        # filter out virtual nodes
        return bool(selected_non_graph_items)

    def _duplicate_selected_nodes():
        """Duplicate the selected nodes, maintaining the input connections"""
        paths = [n.GetPath() for n in selected_non_graph_items]
        usd_context = omni.usd.get_context()
        with omni.kit.usd.layers.active_authoring_layer_context(usd_context):
            omni.kit.commands.execute("CopyPrims", paths_from=paths)

    def _can_disconnect_selected_nodes() -> bool:
        """Returns whether the disconnect selected nodes can be enabled"""

        # TODO - handle disconnection for input and output nodes
        return bool(selected_node_only_prims)

    def _disconnect_selected_nodes():
        """
        Disconnect the the selected nodes.
        """
        with omni.kit.undo.group():
            for n in selected_view_items:

                # input/output nodes - TODO handle this disconnection
                if VirtualNodeHelper.is_virtual_node(n):
                    continue

                # pseudo nodes (background, node)
                if not model.get_node_from_prim(n):
                    continue

                for port in model[n].ports:
                    connections = model._connections.get(port, None)  # noqa: protected-access
                    if connections:
                        model.remove_connections(port, connections)
                    output_connections = model.get_output_connections(port)
                    if output_connections:
                        for c in output_connections:
                            model.remove_connections(c, [port])

    def _frame_selected_nodes():
        """If one ore more nodes are selected, frame the selected nodes.
        Otherwise frame all the nodes in the graph."""
        view.focus_on_nodes(selected_view_items)

    def _layout_all_nodes():
        """Apply an automatic layout to the entire graph."""
        with omni.kit.undo.group():
            view.layout_all()

    def _create_backdrop_for_selected_nodes():
        """Create a backdrop covering the selected nodes."""

        # Offset the minimal value of the extent to allow the backdrop to have a "border".
        # The maximum extent does not need to be offset, because it already includes a border.
        # The offset is equal to the HEADER_HEIGHT offset of the Backdrop.
        min_offset = 25

        x_min = float("inf")
        x_max = float("-inf")
        y_min = float("inf")
        y_max = float("-inf")

        for n in selected_view_items:
            p = view._model[n].position  # noqa: protected-access
            # Add the node size offset to the extent
            widget = view._node_widgets[n]  # noqa: protected-access
            s = (widget.computed_width, widget.computed_height)
            x_min = min(x_min, p[0] - min_offset)
            x_max = max(x_max, p[0] + s[0])
            y_min = min(y_min, p[1] - min_offset)
            y_max = max(y_max, p[1] + s[1])

        position = (x_min, y_min)
        size = (x_max - x_min, y_max - y_min)
        graph_path = Sdf.Path(current_graph.GetPrimPath())

        with omni.kit.undo.group():
            omni.kit.commands.execute(
                "CreateUsdUIBackdropCommand",
                parent_path=graph_path,
                identifier="OGBackdrop",
                position=position,
                size=size,
                display_color=(0.3, 0.6, 0.2),
            )

    def _open_help_for_selected_nodes():
        """Open up the help page for the selected nodes. Assume that the documentation exists"""

        if not selected_og_prims:
            return

        for prim in selected_og_prims:
            node = _get_node_safe(prim)
            if not node or CompoundUtils.is_compound_node(node):
                continue

            node_type = node.get_node_type()
            node_type_name = node_type.get_node_type()

            # Build up the URL to point to the docs. The extension and node type name use "-" as
            # separators and the node type name has the extension name stripped from it.
            # Node Type="omni.graph.nodes.BundleInspector", Extension="omni.graph.nodes", Version=1
            # -> URL = .../omni-graph-nodes/BundleInspector-1.html
            # Node Type="omni.deform.mesh", Extension="omni.anim.deformers", Version=2
            # -> URL = .../omni-anim-deformers/omni-deform-mesh-2.html
            url_pattern = "https://docs.omniverse.nvidia.com/prod_extensions/prod_extensions/ext_omnigraph/node-library/nodes/{}/{}-{}.html"
            # When the documentation is built but not yet publicly available uncomment this next
            # line so that you can test before it goes live.
            # url_pattern = "https://omniverse.gitlab-master-pages.nvidia.com/omni-docs/prod_extensions/prod_extensions/ext_omnigraph/node-library/nodes/{}/{}-{}.html"

            version = og.GraphRegistry().get_node_type_version(node_type_name)
            extension = node_type.get_metadata(ogt.ogn.MetadataKeys.EXTENSION)
            extension = extension.replace(".", "-").lower()
            node_type_name = node_type_name.replace(".", "-").replace(extension, "").lower()
            if node_type_name[0] == "-":
                node_type_name = node_type_name[1:]
            url = url_pattern.format(extension, node_type_name, version)
            webbrowser.open(url)

    def _is_help_for_selected_nodes_enabled() -> bool:
        """Returns whether help is enabled for the selected nodes."""
        if not selected_og_prims:
            return False

        for prim in selected_og_prims:
            node = _get_node_safe(prim)
            if not node:
                continue
            if not CompoundUtils.is_compound_node(node):
                return True
        return False

    def _on_create_subgraph_compound_clicked():
        """Callback when the create subgraph compound from selection is checked"""
        widget.model.create_subgraph_compound(selected_node_only_prims)

    def _on_create_empty_compound_subgraph():
        """Callback to create an empty compound subgraph"""
        # Get the mouse position in canvas space
        canvas_pos = (0, 0)
        if hasattr(widget, "_get_graph_view_hovered_position") and hasattr(view, "screen_to_canvas"):
            mouse_position = widget._get_graph_view_hovered_position()  # noqa: protected-access
            if mouse_position is not None:
                canvas_pos = view.screen_to_canvas(*mouse_position)

        widget.model.create_node(
            COMPOUND_SUBGRAPH_NODE_TYPE, str(current_graph.GetPrimPath()), canvas_pos, node_name="compound"
        )

    def _can_create_compound_subgraph_from_selection() -> bool:
        """Validation method to determine if the ability to create a compound subgraph is available"""
        return (
            _can_create_compound()
            and importlib.util.find_spec("omni.graph.core._unstable")
            and hasattr(og._unstable, "cmds")  # noqa: protected-access
            and hasattr(og._unstable.cmds, "ReplaceWithCompoundSubgraph")  # noqa: protected-access
        )

    def _on_create_compound_node_type_clicked():
        """
        Callback when the create compound from selection is checked.
        """

        def _on_create_compound_dialog_ok(dialog: MultiFieldDialog):
            """Callback when the create compound dialog has the ok button click"""
            dialog.hide()
            model.create_compound(dialog.get_values(0), dialog.get_values(1), selected_non_graph_items)

        dialog = MultiFieldDialog(
            title="Create Compound",
            ok_handler=_on_create_compound_dialog_ok,
        )
        dialog.show()

    def _can_create_compound() -> bool:
        """Determines if the on_create_compound_should be active"""
        return all(
            isinstance(i, Usd.Prim) for i in selected_non_graph_items
        ) and CompoundUtils.can_create_compound_from(selected_non_graph_items)

    def _on_edit_compound_clicked() -> bool:
        """Callback when edit selected compound is clicked."""
        widget.enter_compound(selected_non_graph_items[0])

    def _can_edit_selected_compound() -> bool:
        """Determines if on_edit_compound should be active"""
        return len(selected_non_graph_items) == 1 and CompoundUtils.is_compound_node(selected_non_graph_items[0])

    def _can_promote_unconnected() -> bool:
        """Determines if the given node(s) can have its inputs or outputs promoted to the owning compound node"""
        ret = True
        for i in selected_node_only_prims:  # can include nested compounds
            ret &= CompoundUtils.is_node_in_a_compound(i.GetPath())
        return ret

    def _on_promote_unconnected_clicked(inputs: bool):
        """Callback when promote unconnected inputs/outputs is clicked"""
        with omni.kit.undo.group():
            for i in selected_node_only_prims:  # can include nested compounds
                promote_unconnected_to_compound(model, i, inputs, not inputs)

    menu = ui.Menu("Context menu")
    with menu:
        if graph_config.Settings.are_compounds_enabled():
            with ui.Menu("Compounds"):
                if selected_node_only_prims:
                    ui.MenuItem(
                        f' {omni.kit.ui.get_custom_glyph_code("${glyphs}/" + MENU_GRAPH)}   Create Compound Subgraph From Selected',
                        triggered_fn=_on_create_subgraph_compound_clicked,
                        enabled=_can_create_compound_subgraph_from_selection(),
                    )
                else:
                    ui.MenuItem(
                        f' {omni.kit.ui.get_custom_glyph_code("${glyphs}/" + MENU_GRAPH)}   Create Compound Subgraph',
                        triggered_fn=_on_create_empty_compound_subgraph,
                    )
                if graph_config.Settings.are_compound_node_types_enabled():
                    ui.MenuItem(
                        f' {omni.kit.ui.get_custom_glyph_code("${glyphs}/" + MENU_GRAPH)}   Create Compound Node Type From Selected',
                        triggered_fn=_on_create_compound_node_type_clicked,
                        enabled=_can_create_compound(),
                    )
                ui.Separator()
                ui.MenuItem(
                    f'{omni.kit.ui.get_custom_glyph_code("${glyphs}/" + MENU_GRAPH)}   Edit Selected Compound',
                    triggered_fn=_on_edit_compound_clicked,
                    enabled=_can_edit_selected_compound(),
                )
                if selected_node_only_prims and CompoundUtils.is_compound_graph(current_graph):
                    ui.MenuItem(
                        f'{omni.kit.ui.get_custom_glyph_code("${glyphs}/" + MENU_GRAPH)}   Promote Unconnected Inputs to Compound',
                        triggered_fn=lambda: _on_promote_unconnected_clicked(True),
                        enabled=_can_promote_unconnected(),
                    )
                    ui.MenuItem(
                        f'{omni.kit.ui.get_custom_glyph_code("${glyphs}/" + MENU_GRAPH)}   Promote Unconnected Outputs to Compound',
                        triggered_fn=lambda: _on_promote_unconnected_clicked(False),
                        enabled=_can_promote_unconnected(),
                    )
            ui.Separator()
        ui.MenuItem("Select All", triggered_fn=_select_all_nodes, hotkey_text="CTRL + A")
        ui.MenuItem("Select None", triggered_fn=_clear_node_selection, hotkey_text="ESC")
        if traversal_available:
            ui.MenuItem(
                "Select Downstream Nodes", triggered_fn=_select_downstream_nodes, enabled=bool(selected_og_prims)
            )
            ui.MenuItem("Select Upstream Nodes", triggered_fn=_select_upstream_nodes, enabled=bool(selected_og_prims))
            ui.MenuItem("Select Tree", triggered_fn=_select_execution_tree, enabled=bool(selected_og_prims))
        ui.Separator()
        ui.MenuItem(
            "Delete Selection",
            triggered_fn=_delete_selected_nodes,
            enabled=_can_delete_selected_nodes(),
            hotkey_text="DEL",
        )
        ui.MenuItem(
            "Duplicate Selection",
            triggered_fn=_duplicate_selected_nodes,
            enabled=_can_duplicate_selected_nodes(),
            hotkey_text="CTRL + D",
        )
        ui.MenuItem("Disconnect", triggered_fn=_disconnect_selected_nodes, enabled=_can_disconnect_selected_nodes())
        ui.MenuItem("Frame", triggered_fn=_frame_selected_nodes, enabled=bool(selected_view_items), hotkey_text="F")
        ui.Separator()
        ui.MenuItem(
            "Copy", triggered_fn=_copy_selected_nodes, hotkey_text="CTRL + C", enabled=bool(selected_node_only_prims)
        )
        ui.MenuItem("Paste", triggered_fn=_paste_nodes, hotkey_text="CTRL + V")
        ui.Separator()
        ui.MenuItem("Layout All", triggered_fn=_layout_all_nodes)
        ui.Separator()
        ui.MenuItem(
            "Create Backdrop", triggered_fn=_create_backdrop_for_selected_nodes, enabled=bool(selected_view_items)
        )
        ui.Separator()
        ui.MenuItem(
            "Help",
            triggered_fn=_open_help_for_selected_nodes,
            enabled=_is_help_for_selected_nodes_enabled(),
            hotkey_text="F1",
        )

    return menu


# --------------------------------------------------------------------------------------
class OmniGraphNodeContextMenu:
    """Implementation of the base node context menu for OmniGraph

    Args:
        widget: The graph widget that owns the context menu
    """

    def __init__(self, widget, filter_fn=None):
        self._widget = widget
        self._menu = None
        self._filter_fn = filter_fn

    def destroy(self):
        if self._menu:
            self._menu.destroy()
            self._menu = None

    def build(self, context_item: Any):
        self.destroy()
        self._menu = _build_node_context_menu(self._widget, context_item, filter_fn=self._filter_fn)

    def show(self, pos: Tuple[float, float] | None = None):
        if self._menu:
            if pos:
                self._menu.show_at(pos[0], pos[1])
            else:
                self._menu.show()

    @property
    def shown(self) -> bool:
        return self._menu and self._menu.shown


# --------------------------------------------------------------------------------------
class OmniGraphPortContextMenuBase:
    """
    Base class for context menus for adding inputs/outputs and changing type.
    Creates menu similar to the Convert to Type context menu.
    """

    preferred_types = ["any", "double", "double[3]", "float", "float[3]", "int", "string", "token"]
    types = []
    type_tree = defaultdict(list)  # The role submenus
    nice_names = {}

    @classmethod
    def build_type_tree(cls):
        cls.types = ogt.ogn.supported_attribute_type_names()
        cls.nice_names = {t: t.replace("[]", " array") for t in cls.types}

        # Partial duplication of code in the Convert to Type menus in omni.graph.ui's utils.py
        # Should ideally be re-factored so they share code
        def _process_type(type_name: str):
            base_type_name, _, _, _ = ogt.ogn.split_attribute_type_name(type_name)
            og_type = og.AttributeType.type_from_ogn_type_name(type_name)
            if og_type.role != og.AttributeRole.NONE:
                base_type = og_type.get_role_name()
            else:
                base_type = base_type_name
            cls.type_tree[base_type].append(type_name)

        for t in sorted(cls.types):
            if t not in cls.preferred_types:
                _process_type(t)

    def __init__(self):
        self._menu = None

    def destroy(self):
        if self._menu:
            self._menu.destroy()
            self._menu = None

    def on_click(self, compound_node: og.Node, type_name: str, is_input: bool):
        pass

    def build(self, port: Sdf.Path, is_input: bool):
        """
        port        The port on the virtual input/output node. Used to get the compound it belongs to
        is_input    True if port to be created is an input to the compound. Otherwise, output port wil be created
        """
        if not OmniGraphPortContextMenuBase.types:
            OmniGraphPortContextMenuBase.build_type_tree()

        graph = og.Controller.graph(port.parent.GetPath())
        compound_node = graph.get_owning_compound_node()

        self.destroy()
        self._menu = ui.Menu("Context menu")
        with self._menu:
            with ui.Menu("All"):
                for base_type_name, type_list in OmniGraphPortContextMenuBase.type_tree.items():
                    if not type_list:
                        continue
                    if len(type_list) == 1:
                        ui.MenuItem(
                            OmniGraphPortContextMenuBase.nice_names[type_list[0]],
                            triggered_fn=partial(self.on_click, compound_node, type_list[0], is_input),
                        )
                    else:  # show sub menus
                        with ui.Menu(base_type_name):
                            for type_name in type_list:
                                ui.MenuItem(
                                    OmniGraphPortContextMenuBase.nice_names[type_name],
                                    triggered_fn=partial(self.on_click, compound_node, type_name, is_input),
                                )
            ui.Separator()
            for type_name in OmniGraphPortContextMenuBase.preferred_types:
                ui.MenuItem(type_name, triggered_fn=partial(self.on_click, compound_node, type_name, is_input))

    def show(self, pos: Tuple[float, float] | None = None):
        if self._menu:
            if pos:
                self._menu.show_at(pos[0], pos[1])
            else:
                self._menu.show()

    @property
    def shown(self) -> bool:
        return self._menu and self._menu.shown


# --------------------------------------------------------------------------------------
class OmniGraphEmptyPortContextMenu(OmniGraphPortContextMenuBase):
    """
    Base class for for adding inputs/outputs.
    """

    def on_click(self, compound_node: og.Node, type_name: str, is_input: bool):
        """
        Create a new port of the specified type on the given compound node
        """
        port_type = (
            og.AttributePortType.ATTRIBUTE_PORT_TYPE_INPUT
            if is_input
            else og.AttributePortType.ATTRIBUTE_PORT_TYPE_OUTPUT
        )
        is_bundle = type_name == "bundle"
        with omni.kit.undo.group():
            name = CompoundUtils.sanitize_attribute_name(
                f"new_{type_name}", compound_node, port_type, is_bundle, prev_name=None
            )
            extended_type = og.ExtendedAttributeType.REGULAR
            attribute_type = og.AttributeType.type_from_ogn_type_name(type_name)
            if type_name == "any":
                extended_type = og.ExtendedAttributeType.ANY
                attribute_type = og.Type(og.BaseDataType.TOKEN)

            # Note: This should ideally be handled via a command as other compound types will not create new ports the
            # same way
            og.Controller.create_attribute(
                compound_node,
                attr_name=name,
                attr_type=attribute_type,
                attr_port=port_type,
                attr_extended_type=extended_type,
            )


# --------------------------------------------------------------------------------------
class MapToTargetMenuFunctor:
    """
    Functor class for the map to target menu

    Args:
        model: The ui model invoking this functor
        port: Sdf.Path of the port to apply the mapping to
    """

    def __init__(self, model: OmniGraphModel, port: Sdf.Path):
        self._port = port
        self._model = model

    def __call__(self):
        dialog = MultiFieldDialog(
            title="Select Target Attribute Mapping",
            items=[("Attribute Name", ui.StringField, "xformOp:translate", None)],
            ok_handler=self._on_dialog_ok_clicked,
        )
        dialog.show()

    def _on_dialog_ok_clicked(self, dialog: MultiFieldDialog):
        """Callback when the create compound dialog has the ok button click"""
        mapping = dialog.get_values(0)
        dialog.hide()
        og.cmds.MapAttr(attr=self._port, mapping=mapping)

        # TODO -- this doesn't properly force the property to redraw because
        # the node hasn't really changed. So the tooltip is not being updated.
        self._model._item_changed(None)  # noqa: protected-access


# --------------------------------------------------------------------------------------
class ClearTargetMenuFunctor:
    """
    Menu object class that clears the mapping on a port

    Args:
        model: The ui model invoking this functor
        port: Sdf.Path of the port to clear
    """

    def __init__(self, model: OmniGraphModel, port: Sdf.Path):
        self._port = port
        self._model = model

    def __call__(self):
        og.cmds.MapAttr(attr=self._port, mapping="")
        # TODO -- this doesn't properly force the property to redraw because
        # the node hasn't really changed. So the tooltip is not being updated.
        self._model._item_changed(None)  # noqa: protected-access

    @staticmethod
    def should_display(port: Sdf.Path):
        attr = og.Controller.attribute(port)
        return attr and attr.target_mapping
