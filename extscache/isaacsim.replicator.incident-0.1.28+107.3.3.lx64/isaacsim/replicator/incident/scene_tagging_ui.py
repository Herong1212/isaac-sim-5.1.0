import omni
import omni.ui as ui
from omni.kit.menu.utils import MenuHelperWindow
import carb

from .ui_definitions import get_collapsable_frame_style
from .topple_demon.scene_tagging_ui_panel import ToppleSceneTaggingUIMenu
from .pyro_demon.pyro_scene_tagging_panel import PyroSceneTaggingUIMenu
from .spill_demon.spill_scene_tagging_panel import SpillSceneTaggingUIMenu
class SceneTaggingUIMenu(MenuHelperWindow):
    """
    This class is the windown housing all of the scene tagging UI.
    """

    def __init__(self):
        super().__init__(title="Event Scene Tagger", width=250, height=500, dockPreference=ui.DockPreference.RIGHT)
        self.canvas = None
        self.scene_view = None

        self._test_panel = None
        self._topple_scene_tagging_ui_menu = ToppleSceneTaggingUIMenu()
        self._pyro_scene_tagging_ui_menu = PyroSceneTaggingUIMenu()
        self._spill_scene_tagging_ui_menu = SpillSceneTaggingUIMenu()

        self._stage_event_sub = None

        self._setup_stage_subscription()

        self.frame.set_build_fn(self._build_ui)

    def _setup_stage_subscription(self):
        ctx = omni.usd.get_context()
        self._stage_event_sub = ctx.get_stage_event_stream().create_subscription_to_pop(
            self._on_stage_event,
            name="My Stage Subscription"
        )

    def destroy_menus(self):
        if self._topple_scene_tagging_ui_menu:
            self._topple_scene_tagging_ui_menu.destroy()
        if self._pyro_scene_tagging_ui_menu:
            self._pyro_scene_tagging_ui_menu.destroy()
        if self._spill_scene_tagging_ui_menu:
            self._spill_scene_tagging_ui_menu.destroy()

        self._topple_scene_tagging_ui_menu = None
        self._pyro_scene_tagging_ui_menu = None
        self._spill_scene_tagging_ui_menu = None

    def init_menus(self):
        self.destroy_menus()
        self._topple_scene_tagging_ui_menu = ToppleSceneTaggingUIMenu()
        self._pyro_scene_tagging_ui_menu = PyroSceneTaggingUIMenu()
        self._spill_scene_tagging_ui_menu = SpillSceneTaggingUIMenu()

    def _on_stage_event(self, event):
        if event.type == int(omni.usd.StageEventType.OPENED):
            self.init_menus()
            self._build_ui()
            self._topple_scene_tagging_ui_menu.read_scene_tagging_data_from_stage()
            self._pyro_scene_tagging_ui_menu.read_scene_tagging_data_from_stage()
            self._spill_scene_tagging_ui_menu.read_scene_tagging_data_from_stage()

        elif event.type == int(omni.usd.StageEventType.CLOSED):
            self.destroy_menus()

        # TODO: Add events for when prims are created or destroyed

    def _build_ui(self):
        self.deferred_dock_in("Stage", ui.DockPolicy.CURRENT_WINDOW_IS_ACTIVE)
        self.dock_order = 7
        with self.frame:
            with ui.ScrollingFrame():
                with ui.VStack(spacing=0, height=0):
                    if self._topple_scene_tagging_ui_menu:
                        self._topple_scene_tagging_ui_menu.build_ui_frame()
                    if self._pyro_scene_tagging_ui_menu:
                        self._pyro_scene_tagging_ui_menu.build_ui_frame()
                    if self._spill_scene_tagging_ui_menu:
                        self._spill_scene_tagging_ui_menu.build_ui_frame()

    def destroy(self):
        self.destroy_menus()
        self._stage_event_sub.unsubscribe()
