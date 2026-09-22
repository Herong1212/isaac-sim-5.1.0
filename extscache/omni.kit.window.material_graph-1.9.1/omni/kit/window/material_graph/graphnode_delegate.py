# Copyright (c) 2018-2021, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = ["GraphNodeDelegate"]

import re
from functools import partial

import omni.ui as ui
from omni.kit.graph.delegate.default.delegate import GraphNodeDelegate as GraphNodeDelegateBase
from omni.kit.graph.delegate.default.delegate_full import TEXT_VISIBLE_MIN
from omni.kit.widget.graph.abstract_graph_node_delegate import GraphNodeDescription


class GraphNodeDelegate(GraphNodeDelegateBase):
    def __init__(self):
        super().__init__()

        self._subscription = None

    def node_header(self, model, node_desc: GraphNodeDescription):
        """Called to create widgets of the top of the node"""
        # From delegate_full.py _common_node_node_background
        MARGIN_WIDTH = 7.5
        BORDER_THICKNESS = 3.0

        # Offset according to the design of the default delegate
        vertical_offset = (MARGIN_WIDTH + BORDER_THICKNESS) / 4
        horizontal_offset = (-MARGIN_WIDTH + BORDER_THICKNESS) - 0.25 / 4

        def make_valid_name(tmp_name: str):
            # replace non-alphanumeric characters
            return re.sub("[^0-9a-zA-Z]+", "_", tmp_name)

        def end_edit(self, graph_model, graph_node, widget: ui.Widget, value_model: ui.AbstractValueModel):
            """Called when the user pressed Enter"""
            widget.visible = False

            old_name = graph_model[graph_node].name
            new_name = value_model.as_string
            if old_name != new_name:
                # Rename
                graph_model[graph_node].name = make_valid_name(new_name)

            # Clear subscription
            self._subscription = None

        def begin_edit(self, graph_model, graph_node, field: ui.Widget, *_):
            """Called to start editing"""
            field.visible = True
            value_model = field.model

            self._subscription = value_model.subscribe_end_edit_fn(
                partial(end_edit, self, graph_model, graph_node, field)
            )

        with ui.ZStack():
            super().node_header(model, node_desc)

            placer = ui.Placer(
                height=17,
                stable_size=True,
                offset_x=horizontal_offset,
                offset_y=vertical_offset,
                visible_min=TEXT_VISIBLE_MIN,
            )
            with placer:
                field = ui.StringField(visible=False)
                node_name = model[node_desc.node].name
                field.model.as_string = node_name

            # If we rename input/output node, the widget target should also be
            # changed. It's impossible ATM. It's temporarly blocked.
            # TODO: Invent a way to solve it.
            input_suffix = " (input)"
            output_suffix = " (output)"
            block_rename = False
            for s in [input_suffix, output_suffix]:
                if node_name.endswith(s):
                    block_rename = True
                    break

            if not block_rename:
                placer.set_mouse_double_clicked_fn(partial(begin_edit, self, model, node_desc.node, field))
