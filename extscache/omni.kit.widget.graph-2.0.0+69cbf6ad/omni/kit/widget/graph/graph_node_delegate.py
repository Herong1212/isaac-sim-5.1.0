# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

"""This module provides the GraphNodeDelegate class with styling and routing functionality for graph node representations in NVIDIA's Omniverse applications."""


__all__ = ["GraphNodeDelegate"]

from .graph_model import GraphModel
from .graph_node_delegate_closed import GraphNodeDelegateClosed
from .graph_node_delegate_full import GraphNodeDelegateFull
from .graph_node_delegate_router import GraphNodeDelegateRouter
from pathlib import Path
import omni.ui as ui

CURRENT_PATH = Path(__file__).parent
ICON_PATH = CURRENT_PATH.parent.parent.parent.parent.joinpath("icons")

# The main colors
LABEL_COLOR = 0xFFB4B4B4
BACKGROUND_COLOR = 0xFF34302A
BORDER_DEFAULT = 0xFFDBA656
BORDER_SELECTED = 0xFFFFFFFF
CONNECTION = 0xFF80C280
NODE_BACKGROUND = 0xFF675853
NODE_BACKGROUND_SELECTED = 0xFF7F6C66


class GraphNodeDelegate(GraphNodeDelegateRouter):
    """A class providing styling and routing for graph node representations in Omniverse applications.

    This delegate offers a customizable interface for nodes within a graph, allowing them to be displayed with a unified Omniverse design. It supports both fully expanded and collapsed states for the nodes.
    """

    def __init__(self):
        """Initialize the GraphNodeDelegate with full and collapsed states."""
        super().__init__()

        def is_closed(model, node):
            expansion_state = model[node].expansion_state
            return expansion_state == GraphModel.ExpansionState.CLOSED

        # Initial setup is the delegates for full and closed states.
        self.add_route(GraphNodeDelegateFull())
        self.add_route(GraphNodeDelegateClosed(), expression=is_closed)

    @staticmethod
    def get_style():
        """Gets the style dictionary for the graph node delegate.

        Returns:
            dict: A dictionary containing the style configuration for the graph node delegate."""
        style = {
            "Graph": {"background_color": BACKGROUND_COLOR},
            "Graph.Connection": {"color": CONNECTION, "background_color": CONNECTION, "border_width": 2.0},
            # Node
            "Graph.Node.Background": {"background_color": NODE_BACKGROUND},
            "Graph.Node.Background:selected": {"background_color": NODE_BACKGROUND_SELECTED},
            "Graph.Node.Border": {"background_color": BORDER_DEFAULT},
            "Graph.Node.Border:selected": {"background_color": BORDER_SELECTED},
            "Graph.Node.Resize": {"background_color": BORDER_DEFAULT},
            "Graph.Node.Resize:selected": {"background_color": BORDER_SELECTED},
            "Graph.Node.Description": {"color": LABEL_COLOR},
            "Graph.Node.Description.Edit": {"color": LABEL_COLOR, "background_color": NODE_BACKGROUND},
            # Header Input
            "Graph.Node.Input": {
                "background_color": BORDER_DEFAULT,
                "border_color": BORDER_DEFAULT,
                "border_width": 3.0,
            },
            # Header
            "Graph.Node.Header.Label": {"color": 0xFFB4B4B4, "margin_height": 5.0, "font_size": 14.0},
            "Graph.Node.Header.Label::Degenerated": {"font_size": 22.0},
            "Graph.Node.Header.Collapse": {
                "background_color": 0x0,
                "padding": 0,
                "image_url": f"{ICON_PATH}/hamburger-open.svg",
            },
            "Graph.Node.Header.Collapse::Minimized": {"image_url": f"{ICON_PATH}/hamburger-minimized.svg"},
            "Graph.Node.Header.Collapse::Closed": {"image_url": f"{ICON_PATH}/hamburger-closed.svg"},
            # Header Output
            "Graph.Node.Output": {
                "background_color": BACKGROUND_COLOR,
                "border_color": BORDER_DEFAULT,
                "border_width": 3.0,
            },
            # Port Group
            "Graph.Node.Port.Group": {"color": 0xFFB4B4B4},
            "Graph.Node.Port.Group::Plus": {"image_url": f"{ICON_PATH}/Plus.svg"},
            "Graph.Node.Port.Group::Minus": {"image_url": f"{ICON_PATH}/Minus.svg"},
            # Port Input
            "Graph.Node.Port.Input": {
                "background_color": BORDER_DEFAULT,
                "border_color": BORDER_DEFAULT,
                "border_width": 3.0,
            },
            "Graph.Node.Port.Input:selected": {"border_color": BORDER_SELECTED},
            "Graph.Node.Port.Input.CustomColor": {"background_color": 0x0},
            # Port
            "Graph.Node.Port.Branch": {
                "color": 0xFFB4B4B4,
                "border_width": 0.75,
            },
            "Graph.Node.Port.Label": {
                "color": 0xFFB4B4B4,
                "margin_width": 5.0,
                "margin_height": 3.0,
                "font_size": 14.0,
            },
            "Graph.Node.Port.Label::output": {"alignment": ui.Alignment.RIGHT},
            # Port Output
            "Graph.Node.Port.Output": {
                "background_color": BACKGROUND_COLOR,
                "border_color": BORDER_DEFAULT,
                "border_width": 3.0,
            },
            "Graph.Node.Port.Output.CustomColor": {"background_color": 0x0, "border_color": 0x0, "border_width": 3.0},
            # Footer
            "Graph.Node.Footer": {
                "background_color": BACKGROUND_COLOR,
                "border_color": BORDER_DEFAULT,
                "border_width": 3.0,
                "border_radius": 8.0,
            },
            "Graph.Node.Footer:selected": {"border_color": BORDER_SELECTED},
            "Graph.Node.Footer.Image": {"image_url": f"{ICON_PATH}/0101.svg", "color": BORDER_DEFAULT},
            "Graph.Selecion.Rect": {
                "background_color": ui.color(1.0, 1.0, 1.0, 0.1),
                "border_color": ui.color(1.0, 1.0, 1.0, 0.5),
                "border_width": 1,
            },
        }

        return style

    @staticmethod
    def specialized_color_style(name, color, icon, icon_tint_color=None):
        """Return part of the style that has everything to color special node type.

        Args:
            name (str): Node type
            color (int): Node color
            icon (str): Filename to the icon the node type should display
            icon_tint_color (int, optional): Icon tint color

        Returns:
            dict: A dictionary containing the specialized color style for a node type."""
        style = {
            # Node
            f"Graph.Node.Border::{name}": {"background_color": color},
            # Header Input
            f"Graph.Node.Input::{name}": {"background_color": color, "border_color": color},
            # Header Output
            f"Graph.Node.Output::{name}": {"border_color": color},
            # Port Input
            f"Graph.Node.Port.Input::{name}": {"background_color": color, "border_color": color},
            f"Graph.Node.Port.Input::{name}:selected": {"background_color": color, "BORDER_SELECTED": color},
            # Port Output
            f"Graph.Node.Port.Output::{name}": {"border_color": color},
            # Footer
            f"Graph.Node.Footer::{name}": {"border_color": color},
            f"Graph.Node.Footer.Image::{name}": {"image_url": icon, "color": icon_tint_color or color},
        }
        return style

    @staticmethod
    def specialized_port_style(name, color):
        """Return part of the style that has everything to color the customizable part of the port.

        Args:
            name (str): Port type
            color (int): Port color

        Returns:
            dict: A dictionary containing the specialized port style configuration."""
        style = {
            f"Graph.Node.Port.Input.CustomColor::{name}": {"background_color": color},
            f"Graph.Node.Port.Output.CustomColor::{name}": {"background_color": color, "border_color": color},
            f"Graph.Connection::{name}": {"color": color, "background_color": color},
        }
        return style
