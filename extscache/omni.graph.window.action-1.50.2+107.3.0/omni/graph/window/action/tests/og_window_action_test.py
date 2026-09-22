from pathlib import Path

import carb
import carb.settings
import omni.graph.core as og
import omni.kit.test
import omni.ui as ui
import omni.usd
from omni.kit import ui_test
from omni.ui.tests.test_base import OmniUiTest

from ..action_catalog_model import OgActionTestCatalogModel
from ..action_graph_widget import ActionGraphWidget
from ..action_graph_window import ActionGraphWindow

EXT_PATH = Path(carb.tokens.get_tokens_interface().resolve("${omni.graph.window.action}"))


class OgActionTestGraphWidget(ActionGraphWidget):
    def on_build_startup(self):
        # We don't want the initial Edit/Create selection widgets, just a blank graph.
        pass


class OgActionTestWindow(ActionGraphWindow):
    def on_build_window(self):
        catalog_model = OgActionTestCatalogModel(
            (
                "omni.graph.action.OnTick",  # Event
                "omni.graph.action.Counter",  # Function
                "omni.graph.action_nodes.OnTick",  # Event (Renamed)
                "omni.graph.action_nodes.Counter",  # Function (Renamed)
                "omni.graph.nodes.ToString",  # Function
                "omni.graph.ui.PrintText",  # Debug
                "omni.graph.ui_nodes.PrintText",  # Debug (Renamed)
            )
        )
        self._main_widget = OgActionTestGraphWidget(catalog_model=catalog_model)  # noqa: protected-access


class TestOgWindowActionUI(OmniUiTest):
    def __init__(self, tests=()):
        super().__init__(tests)
        self.settings = carb.settings.get_settings()
        self.TEST_GRAPH_PATH = "/World/TestGraph"
        self.wait_frames_for_visual_update = 5

        # It takes 6 frames for the nodes and connections to all draw in their proper positions.
        self.wait_frames_for_graph_draw = 6

        # Wait 10 frames for commands to execute and the graph to update
        self.wait_frames_for_commands = 10

    async def setUp(self):
        """Set up test environment, to be torn down when done"""
        await super().setUp()
        self._golden_img_dir = EXT_PATH.absolute().resolve().joinpath("data/tests")

        await omni.usd.get_context().new_stage_async()
        self.stage = omni.usd.get_context().get_stage()

    async def tearDown(self):
        self._golden_img_dir = None
        await super().tearDown()

        omni.usd.get_context().close_stage()  # Activate OnClosing node

    async def create_graph_window(self, title, x=0, y=0, width=1200, height=800):
        graph_window = OgActionTestWindow(
            title,
            flags=ui.WINDOW_FLAGS_NO_SCROLLBAR | ui.WINDOW_FLAGS_NO_TITLE_BAR,
            position_x=x,
            position_y=y,
            width=width,
            height=height,
        )
        await ui_test.wait_n_updates(self.wait_frames_for_visual_update)

        # Create an execution graph.
        graph_window._main_widget.create_graph("execution", self.TEST_GRAPH_PATH, use_dialog=False)  # noqa: PLW0212

        # Close the catalog so that our golden images don't break whenever the categories or node counts change.
        graph_window._main_widget._splitter_left._button.call_clicked_fn()  # noqa: PLW0212

        for _ in range(5):
            await omni.kit.app.get_app().next_update_async()

        return graph_window

    async def test_simple_graph(self):
        window = await self.create_test_window(width=1200, height=800)
        graph_window = await self.create_graph_window("OgWindowActionTest")

        # Populate the graph.
        # Note that 'print_text' has both 'tick' and and 'counter' feeding its execIn pin,
        # so it will print each count twice, except for the first one.
        keys = og.Controller.Keys
        (graph, _, _, _) = og.Controller.edit(
            self.TEST_GRAPH_PATH,
            {
                keys.CREATE_NODES: [
                    ("tick", "omni.graph.action.OnTick"),
                    ("counter", "omni.graph.action.Counter"),
                    ("to_string", "omni.graph.nodes.ToString"),
                    ("print_text", "omni.graph.ui.PrintText"),
                ],
                keys.CONNECT: [
                    ("tick.outputs:tick", "counter.inputs:execIn"),
                    ("tick.outputs:tick", "print_text.inputs:execIn"),
                    ("counter.outputs:execOut", "print_text.inputs:execIn"),
                    ("counter.outputs:count", "to_string.inputs:value"),
                    ("to_string.outputs:converted", "print_text.inputs:text"),
                ],
            },
        )

        graph_window._import_prims(None, [og.Controller.prim(graph.get_path_to_graph())])  # noqa: PLW0212
        await ui_test.wait_n_updates(self.wait_frames_for_graph_draw)

        await self.finalize_test(
            golden_img_dir=self._golden_img_dir,
            golden_img_name="omni.graph.window.action.test_simple_graph.png",
        )

        graph_window.destroy()
        window.destroy()
