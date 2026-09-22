# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
from pathlib import Path
from typing import List

import omni.graph.core as og
import omni.kit.app
import omni.kit.commands
import omni.kit.test
import omni.ui as ui
from omni.kit import ui_test
from omni.kit.test_suite.helpers import wait_stage_loading
from omni.ui.tests.test_base import OmniUiTest

from .._impl.standalone_attribute_builder import StandaloneAttributeBuilder


class TestOmniWidgets(OmniUiTest):
    """
    Test class for testing omnigraph related widgets
    """

    async def setUp(self):
        await super().setUp()

        self._test_file_dir = Path(__file__).parent / "data"
        self._golden_img_dir = self._test_file_dir / "golden_images"

        import omni.kit.window.property as p

        self._w = p.get_window()

    async def tearDown(self):
        await super().tearDown()

    async def __widget_image_test(
        self,
        file_path: str,
        prims_to_select: List[str],
        golden_img_name: str,
        width=450,
        height=500,
    ):
        """Helper to do generate a widget comparison test on a property panel"""
        usd_context = omni.usd.get_context()

        await self.docked_test_window(
            window=self._w._window,  # noqa: PLE0211,PLW0212
            width=width,
            height=height,
            restore_window=ui.Workspace.get_window("Layer") or ui.Workspace.get_window("Stage"),
            restore_position=ui.DockPosition.BOTTOM,
        )

        test_file_path = self._test_file_dir.joinpath(file_path).absolute()
        await usd_context.open_stage_async(str(test_file_path))
        await wait_stage_loading()

        # Select the prim.
        usd_context.get_selection().set_selected_prim_paths(prims_to_select, True)

        # Need to wait for an additional frames for omni.ui rebuild to take effect
        await ui_test.human_delay(10)

        await self.finalize_test(golden_img_dir=self._golden_img_dir, golden_img_name=golden_img_name, threshold=0.15)

        # Close the stage to avoid dangling references to the graph. (OM-84680)
        await omni.usd.get_context().close_stage_async()

    async def test_compound_node_type_widget_ui(self):
        """Tests the compound node type property pane matches the expected image"""
        await self.__widget_image_test(
            file_path="compound_node_test.usda",
            prims_to_select=["/World/Compounds/TestCompound"],
            golden_img_name="test_compound_widget.png",
            height=600,
        )

    async def test_graph_with_variables_widget(self):
        """Tests the variable property pane on a graph prim"""
        await self.__widget_image_test(
            file_path="test_variables.usda",
            prims_to_select=["/World/ActionGraph"],
            golden_img_name="test_graph_variables.png",
            height=300,
        )

    async def test_instance_with_variables_widget(self):
        """Tests the variable property pane on an instance prim"""
        await self.__widget_image_test(
            file_path="test_variables.usda",
            prims_to_select=["/World/Instance"],
            golden_img_name="test_instance_variables.png",
            height=450,
        )

    async def test_node_quatd_widget(self):
        """Tests quatd attribute widget on node"""
        await self.__widget_image_test(
            file_path="test_node_widgets.usda",
            prims_to_select=["/World/PushGraph/constant_quatd"],
            golden_img_name="test_node_quatd_widget.png",
            height=450,
        )

    async def test_node_quatf_widget(self):
        """Tests quatf attribute widget on node"""
        await self.__widget_image_test(
            file_path="test_node_widgets.usda",
            prims_to_select=["/World/PushGraph/constant_quatf"],
            golden_img_name="test_node_quatf_widget.png",
            height=450,
        )

    async def test_node_quath_widget(self):
        """Tests quath attribute widget on node"""
        await self.__widget_image_test(
            file_path="test_node_widgets.usda",
            prims_to_select=["/World/PushGraph/constant_quath"],
            golden_img_name="test_node_quath_widget.png",
            height=450,
        )

    async def test_node_matrix2d_widget(self):
        """Tests matrix2d attribute widget on node"""
        await self.__widget_image_test(
            file_path="test_node_widgets.usda",
            prims_to_select=["/World/PushGraph/constant_matrix2d"],
            golden_img_name="test_node_matrix2d_widget.png",
            height=450,
        )

    async def test_node_matrix3d_widget(self):
        """Tests matrix3d attribute widget on node"""
        await self.__widget_image_test(
            file_path="test_node_widgets.usda",
            prims_to_select=["/World/PushGraph/constant_matrix3d"],
            golden_img_name="test_node_matrix3d_widget.png",
            height=450,
        )

    async def test_node_matrix4d_widget(self):
        """Tests matrix4d attribute widget on node"""
        await self.__widget_image_test(
            file_path="test_node_widgets.usda",
            prims_to_select=["/World/PushGraph/constant_matrix4d"],
            golden_img_name="test_node_matrix4d_widget.png",
            height=450,
        )

    async def test_node_frame_widget(self):
        """Tests frame attribute widget on node"""
        await self.__widget_image_test(
            file_path="test_node_widgets.usda",
            prims_to_select=["/World/PushGraph/constant_frame"],
            golden_img_name="test_node_frame4d_widget.png",
            height=450,
        )

    async def test_standalone_widgets(self):
        """Tests the attribute widgets outside of the Property Window."""
        usd_context = omni.usd.get_context()
        test_file_path = self._test_file_dir.joinpath("test_node_widgets.usda").absolute()
        await usd_context.open_stage_async(str(test_file_path))
        await wait_stage_loading()

        # The test file contains the more complex constant nodes. Let's add a representative sample of
        # the simpler ones as well.
        graph = og.Controller.graph("/World/PushGraph")
        for node_type, value in (
            ("Bool", True),
            ("Color3d", (0.7, 0.4, 0.2)),
            ("Color3h", (0.2, 0.5, 0.7)),
            ("Color4f", (0.7, 0.4, 0.2, 0.5)),
            ("Double", -6.803),
            ("Double2", (0.01, -801.3)),
            ("Float", 83.07),
            ("Float3", (1.1, -2.7, 3.9)),
            ("Half4", (-7.13, 6.5, 4.8, -0.03)),
            ("Int", -145),
            ("Int64", -1234567890),
            ("String", "Hello, world!"),
            ("Token", "not Butters"),
            ("UChar", 32),
            ("UInt", 145),
            ("UInt64", 1234567890),
        ):
            type_name = "omni.graph.nodes.Constant" + node_type
            node_path = "/World/PushGraph/constant_" + node_type.lower()
            last_node = graph.create_node(node_path, type_name, True)
            last_node.get_attribute("inputs:value").set(value)

        # Sort the nodes by type name to ensure that we always get them in the same order.
        nodes = sorted(graph.get_nodes(), key=lambda node: node.get_type_name())

        window = await self.create_test_window(width=600, height=1000)
        with window.frame:
            with ui.VStack(spacing=5):
                # Create a widget for the 'value' attribute of each constant node in the graph.
                for node in nodes:
                    if node.get_type_name().split(".")[-1].startswith("Constant"):
                        attr = node.get_attribute("inputs:value")
                        widget, _ = StandaloneAttributeBuilder.build_ui(attr)
                        widget.height = ui.Length(0)

                # Create one more widget using kwd args to vary its appearance from the default.
                attr = last_node.get_attribute("inputs:value")
                widget, _ = StandaloneAttributeBuilder.build_ui(
                    attr,
                    label_kwd_args={
                        "alignment": ui.Alignment.LEFT_BOTTOM,
                        "height": ui.Length(40),
                        "style": {"color": 0xFF0000FF, "font_size": 18},
                    },
                    value_kwd_args={
                        "width": 20,
                        "height": ui.Length(30),
                        "no_control_state": True,
                        "style": {"background_color": 0xFF008000},
                    },
                )
                widget.height = ui.Length(0)

                # Create a widget for an unresolved attribute.
                node = graph.create_node("/World/PushGraph/add", "omni.graph.nodes.Add", True)
                attr = node.get_attribute("outputs:sum")
                widget, _ = StandaloneAttributeBuilder.build_ui(attr)
                widget.height = ui.Length(0)

        await ui_test.human_delay(10)
        await self.finalize_test(golden_img_dir=self._golden_img_dir, golden_img_name="test_standalone_widgets.png")

        # Close the stage to avoid dangling references to the graph. (OM-84680)
        await omni.usd.get_context().close_stage_async()

    async def test_token_widget(self):
        """Tests the token widget as a graph variable"""
        await self.__widget_image_test(
            file_path="test_token_widget.usda",
            prims_to_select=["/World/PushGraph_All"],
            golden_img_name="test_token_widget.png",
            height=450,
        )

    async def test_token_widget_match(self):
        """Tests the token widget on two graphs with matching values"""
        await self.__widget_image_test(
            file_path="test_token_widget.usda",
            prims_to_select=["/World/PushGraph_All", "/World/PushGraph_Match"],
            golden_img_name="test_token_widget_match.png",
            height=450,
        )

    async def test_token_widget_mixed(self):
        """Tests the token widget on two graphs with mixed values"""
        await self.__widget_image_test(
            file_path="test_token_widget.usda",
            prims_to_select=["/World/PushGraph_All", "/World/PushGraph_Mixed"],
            golden_img_name="test_token_widget_mixed.png",
            height=450,
        )

    async def test_token_widget_ext_list(self):
        """Tests the token widget with extended attributes"""
        await self.__widget_image_test(
            file_path="test_token_widget.usda",
            prims_to_select=["/World/PushGraph_All/to_string_list"],
            golden_img_name="test_token_widget_ext_list.png",
            height=450,
        )

    async def test_token_widget_ext_enum(self):
        """Tests the token widget & allowedTokens with extended attributes"""
        await self.__widget_image_test(
            file_path="test_token_widget.usda",
            prims_to_select=["/World/PushGraph_All/to_string_enum"],
            golden_img_name="test_token_widget_ext_enum.png",
            height=450,
        )

    async def test_og_context_menu(self):
        await omni.usd.get_context().new_stage_async()

        viewport_window = ui_test.find("Viewport")
        await viewport_window.focus()

        # select context menu
        await viewport_window.right_click()
        await ui_test.select_context_menu("Create/Visual Scripting/Push Graph")

        await ui_test.human_delay(10)
        self.assertIsNotNone(og.Controller.graph("/PushGraph"))
