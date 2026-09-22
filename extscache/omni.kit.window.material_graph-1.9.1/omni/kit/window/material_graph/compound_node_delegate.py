# Copyright (c) 2018-2021, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
from functools import partial

import omni.ui as ui
from omni.kit.graph.delegate.default.compound_node_delegate import CompoundInputOutputNodeDelegate as CompDelegateBase
from omni.kit.graph.delegate.default.compound_node_delegate import CompoundNodeDelegate as CompoundNodeDelegateBase
from omni.kit.widget.graph import GraphNodeDescription, GraphNodeLayout
from omni.kit.widget.graph.graph_model import GraphModel

from .export_utils import Export
from .svg_picker import SvgPicker


class CompoundNodeDelegate(CompoundNodeDelegateBase):
    """
    The delegate for the compound nodes.
    """

    def __init__(self):
        super().__init__()
        self.__export = Export()
        self.__svg = SvgPicker()
        self.__context_menu: Optional[ui.Menu] = None

    def destroy(self):
        self.__export.destroy()
        self.__export = None
        self.__svg.destroy()
        self.__svg = None
        self.__context_menu = None

    def get_node_layout(self, model, node_desc: GraphNodeDescription):
        """Called to determine the node layout"""
        return GraphNodeLayout.COLUMNS

    def node_background(self, model, node_desc: GraphNodeDescription):
        """Called to create widgets of the node background"""
        with ui.Frame(mouse_pressed_fn=partial(self._mouse_pressed_fn, model, node_desc.node)):
            super().node_background(model, node_desc)

    def _mouse_pressed_fn(self, model, node, x, y, button, modifier):
        if button != 1:
            return

        self.__context_menu = ui.Menu("Node Context Menu")
        with self.__context_menu:
            ui.MenuItem("Export to USD", triggered_fn=partial(self.__export.export, [node]))
            ui.MenuItem("Select SVG", triggered_fn=partial(self.__svg.set_icon, node))
        self.__context_menu.show()


class CompoundInputOutputNodeDelegate(CompDelegateBase):
    def node_background(self, model, node_desc: GraphNodeDescription):
        """Called to create widgets of the node background"""
        with ui.Frame(mouse_pressed_fn=partial(self._mouse_pressed_fn, model, node_desc.node)):
            super().node_background(model, node_desc)

    def _mouse_pressed_fn(self, model, node, x, y, button, modifier):
        # Temporarly disable Live Preview mode
        return

        if button != 1:
            return

        def toggle_preview(model, node):
            is_open = not model[node].preview_state & GraphModel.PreviewState.OPEN
            model[node].preview_state = GraphModel.PreviewState.OPEN if is_open else GraphModel.PreviewState.NONE

        self.__context_menu = ui.Menu("Compund Node Context Menu")
        with self.__context_menu:
            ui.MenuItem("Toggle Live Preview", triggered_fn=partial(toggle_preview, model, node))
        self.__context_menu.show()
