import carb
import omni.kit.ui
import omni.ui as ui

from .file_loading_panel import SelectAssetFolderPanel
from .setting_panel import CaptionSettingPanel
from .caption_results_panel import CaptionResultsPanel
from .model_setting_panel import ModelSettingPanel

from ..stage_info_manager import StageInfoManager


class DataCollectionPanel:
    """
    The supervisor of ui components.
    """

    def __init__(self):
        """initialize the sub composes"""
        # panel to set output root folder
        self.file_loading_panel = SelectAssetFolderPanel()
        # panel to set model settings
        self.model_setting_panel = ModelSettingPanel()
        # control panel
        self.setting_panel = CaptionSettingPanel()
        self.setting_panel.parent_ui = self  # Set parent reference
        # panel to display caption results
        self.caption_results_panel = CaptionResultsPanel()
        StageInfoManager.get_instance().refresh_configs()
        # build the ui
        self._build_ui()

    def _build_ui(self):
        """build the ui"""
        with ui.VStack(spacing=5, height=0):
            # # build the input panel
            # self.file_loading_panel._build_content()
            # build the control panel
            self.setting_panel._build_content()
            # build the model setting panel
            self.model_setting_panel._build_ui()
            # build the caption results panel
            self.caption_results_panel._build_ui()
