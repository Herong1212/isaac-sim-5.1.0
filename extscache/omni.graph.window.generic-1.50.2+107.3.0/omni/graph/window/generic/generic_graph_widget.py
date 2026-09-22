# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.

from functools import partial
from pathlib import Path

import omni.graph.core as og
import omni.ui as ui
from omni.graph.window.core import OmniGraphWidget

EXT_PATH = Path(__file__).parent.parent.parent.parent.parent
ICON_PATH = EXT_PATH.joinpath("icons")
ICON_SIZE = 120

DEFAULT_GRAPH_PREFIX = "PushGraph"
DEFAULT_GRAPH_EVALUATOR = "push"


class GenericGraphWidget(OmniGraphWidget):
    def is_graph_editable(self, graph: og.Graph) -> bool:
        """Override: Returns True if the given graph is editable by this widget"""
        try:
            settings = og.get_graph_settings(graph)
            return settings.evaluator_type != "execution" or (settings.are_compounds_enabled() and graph.is_compound())
        except AttributeError:
            # Temporary fix for 2022.1 build
            return True

    def on_build_startup(self):
        """Overridden from base to customize startup panel UI"""
        with ui.ZStack():
            ui.Rectangle(style_type_name_override="Graph")
            with ui.HStack(content_clipping=True):
                with ui.VStack():
                    ui.Spacer()
                    with ui.HStack():
                        ui.Spacer()
                        ui.Button(
                            "Edit Graph",
                            name="Edit Graph",
                            height=0,
                            width=ICON_SIZE,
                            style_type_name_override="Graph",
                            image_width=ICON_SIZE,
                            image_height=ICON_SIZE,
                            image_url=f"{ICON_PATH}/push_graph_edit_dark.svg",
                            spacing=5,
                            clicked_fn=self._on_edit_graph_action,
                        )
                        ui.Button(
                            "New Push Graph",
                            name="New Graph",
                            height=0,
                            width=ICON_SIZE,
                            style_type_name_override="Graph",
                            image_width=ICON_SIZE,
                            image_height=ICON_SIZE,
                            image_url=f"{ICON_PATH}/push_graph_new_dark.svg",
                            spacing=5,
                            clicked_fn=partial(self.create_graph, DEFAULT_GRAPH_EVALUATOR, DEFAULT_GRAPH_PREFIX),
                        )
                        ui.Spacer()
                    ui.Spacer()

    def on_toolbar_create_graph_clicked(self):
        """Override to change type of graph created"""
        self.create_graph(DEFAULT_GRAPH_EVALUATOR, DEFAULT_GRAPH_PREFIX, use_dialog=False)
