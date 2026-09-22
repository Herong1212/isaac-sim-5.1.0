# Copyright (c) 2018-2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = ["MaterialGraphView"]

import asyncio

import omni.kit.app
from omni.kit.widget.graph import GraphView
from pxr import UsdShade


class MaterialGraphView(GraphView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Derek: I have noticed that if these values are not
        # clamped then we get will get an error in carb.graphics-direct3d.plugin
        self.zoom_min = 0.03
        self.zoom_max = 10.0

        # our default node size, chosen to fit a
        # material node framed in the editor.
        self.__default_node_size = 192

        self.__do_serialize_positions = False
        self.__post_delayed_build_layout_subscription = self.subscribe_post_delayed_build_layout(
            self.__serialize_positions
        )

    def __serialize_positions(self):
        """Serialze updated positions to models"""
        if not self.__do_serialize_positions:
            return

        self.__do_serialize_positions = False

        for node, placer in self._node_placers.items():
            if node.IsValid():
                self._model[node].position = (float(placer.offset_x), float(placer.offset_y))
                self._model.position_end_edit(node)

    def layout_all(self):
        """Reset positions of all the nodes in the model"""
        for node in self._model.nodes:
            position = None
            if node.IsA(UsdShade.Material):
                position = (-0.5 * self.__default_node_size, 0.0)

            self._model[node].position = position

        self.__do_serialize_positions = True
        self._model._item_changed(None)

    def get_bbox_of_nodes(self, nodes: list):
        """Get the bounding box of nodes.
        This is a copy of the same method in the super class,
        the only difference is the fallback value returned in the
        else clause.  These values center the material node in the
        graph.
        """
        if not nodes:
            nodes = self._model.nodes
        if not nodes:
            return

        min_pos_x = None
        min_pos_x_node = None
        min_pos_y = None
        min_pos_y_node = None
        max_pos_x = None
        max_pos_x_node = None
        max_pos_y = None
        max_pos_y_node = None
        for node in nodes:
            if node not in self._node_widgets:
                continue
            pos = self._model[node].position
            if pos is None:
                continue
            if min_pos_x is None:
                min_pos_x = pos[0]
                min_pos_x_node = node
                min_pos_y = pos[1]
                min_pos_y_node = node
                max_pos_x = pos[0]
                max_pos_x_node = node
                max_pos_y = pos[1]
                max_pos_y_node = node
                continue
            if pos[0] < min_pos_x:
                min_pos_x = pos[0]
                min_pos_x_node = node
            previous_max_max_x = max_pos_x + self._node_widgets[max_pos_x_node].computed_width
            if pos[0] + self._node_widgets[node].computed_width < previous_max_max_x:
                pass
            else:
                max_pos_x = pos[0]
                max_pos_x_node = node
            if pos[1] < min_pos_y:
                min_pos_y = pos[1]
                min_pos_y_node = node
            previous_max_max_y = max_pos_y + self._node_widgets[max_pos_y_node].computed_height
            if pos[1] + self._node_widgets[node].computed_height < previous_max_max_y:
                pass
            else:
                max_pos_y = pos[1]
                max_pos_y_node = node

        if max_pos_x_node in self._node_widgets:
            computed_width = (max_pos_x + self._node_widgets[max_pos_x_node].computed_width) - min_pos_x
            computed_height = (max_pos_y + self._node_widgets[max_pos_y_node].computed_height) - min_pos_y
        else:
            min_pos_x = -0.5 * self.__default_node_size
            min_pos_y = 0
            computed_height = self.__default_node_size
            computed_width = self.__default_node_size

        return computed_width, computed_height, min_pos_x, min_pos_y
