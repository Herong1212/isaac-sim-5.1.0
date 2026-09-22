## Copyright (c) 2018-2024, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##

from omni.kit.widget.graph import GraphView, GraphNodeDelegate
from omni.ui.tests.test_base import OmniUiTest
from .test_graph import Model
import omni.kit.ui_test as ui_test


class SelectionModel(Model):
    def __init__(self):
        super().__init__()
        self._selected_nodes = []

    @property
    def selection(self):
        """return the selected node"""
        return self._selected_nodes

    @selection.setter
    def selection(self, value):
        """set the selection"""
        if value and value != self._selected_nodes:
            self._selected_nodes = value
        elif len(value) == 0:
            self._selected_nodes = []

        self._selection_changed()


class TestSelection(OmniUiTest):
    async def test_selection(self):
        """Testing selection in graph view"""
        # Need this ui.WINDOW_FLAGS_NO_MOVE. Otherwise, emulate_mouse_drag_and_drop will move the window
        import omni.ui as ui
        flags = ui.WINDOW_FLAGS_NO_MOVE | ui.WINDOW_FLAGS_NO_SCROLLBAR | ui.WINDOW_FLAGS_NO_TITLE_BAR
        window = await self.create_test_window(768, 512, window_flags= flags, block_devices=False)

        style = GraphNodeDelegate.get_style()
        # Don't use the image because the image scaling looks different in editor and kit-mini
        style["Graph.Node.Footer.Image"]["image_url"] = ""
        style["Graph.Node.Header.Collapse"]["image_url"] = ""
        style["Graph.Node.Header.Collapse::Minimized"]["image_url"] = ""
        style["Graph.Node.Header.Collapse::Closed"]["image_url"] = ""

        with window.frame:
            delegate = GraphNodeDelegate()
            model = SelectionModel()
            graph_view = GraphView(
                model=model,
                delegate=delegate,
                style=style,
                pan_x=600,
                pan_y=170,
                rectangle_selection=True,
            )

        # normal selection
        human_delay_speed = 5
        await ui_test.emulate_mouse_move(ui_test.Vec2(600, 260), human_delay_speed=5)
        await ui_test.human_delay(human_delay_speed)
        await ui_test.emulate_mouse_click()
        await ui_test.human_delay(human_delay_speed)
        self.assertEqual(model.selection, ["First"])

        # rectangle selection
        await ui_test.human_delay(human_delay_speed)
        await ui_test.emulate_mouse_drag_and_drop(ui_test.Vec2(50, 50), ui_test.Vec2(400, 450))
        await ui_test.human_delay(human_delay_speed)
        self.assertEqual(model.selection, ["Second", "Third"])

        # restore the test
        model.selection = []
        graph_view.destroy()
        window.destroy()
