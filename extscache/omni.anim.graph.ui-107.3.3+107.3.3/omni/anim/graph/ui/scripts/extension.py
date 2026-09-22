import carb
import omni.ext
from .command import *
from .animation_graph_manager import AnimationGraphManager
from .animation_graph_window import AnimationGraphWindow
from .menu import AnimGraphMenu
from .create_animation_graph_dialog import CreateAnimationGraphDialog
from .properties_widget import AnimGraphProperties
from .anim_graph_preference import AnimGraphPreference
from omni.kit.window.preferences import register_page, unregister_page

ext = None


class PublicExtension(omni.ext.IExt):
    def on_startup(self, ext_id):
        global ext
        ext = self

        self._graph_manager = AnimationGraphManager()
        self._create_graph_dialog = CreateAnimationGraphDialog(self._graph_manager)
        self._graph_window = AnimationGraphWindow(self._graph_manager, self._create_graph_dialog)
        self._menu = AnimGraphMenu(ext_id, self._graph_window, self._create_graph_dialog)
        self._properties = AnimGraphProperties()
        # load all the omni.graph.ui templates
        try:
            import omni.graph.ui
            omni.graph.ui.ComputeNodeWidget.get_instance().add_template_path(__file__)
        except ImportError:
            pass

        self._sample_folder = carb.settings.get_settings().get_as_string("/exts/omni.anim.graph/sample_folder")
        if (self._sample_folder):
            omni.kit.browser.sample.register_sample_folder(self._sample_folder, "Animation/Animation Graph")
        # self._preference_page = AnimGraphPreference()
        # register_page(self._preference_page)

    def on_shutdown(self):
        self._menu.on_shutdown()
        self._menu = None
        self._properties.on_shutdown()
        self._properties = None
        self._graph_window.visible = False
        self._graph_window.destroy()
        self._graph_window = None
        self._create_graph_dialog.destroy()
        self._create_graph_dialog = None
        self._graph_manager.destroy()
        self._graph_manager = None

        if self._sample_folder:
            omni.kit.browser.sample.unregister_sample_folder(self._sample_folder)

        global ext
        ext = None
        # unregister_page(self._preference_page)
        # self._preference_page = None


def get_graph_manager() -> AnimationGraphManager:
    global ext
    return ext._graph_manager


def get_graph_window() -> AnimationGraphWindow:
    global ext
    return ext._graph_window
