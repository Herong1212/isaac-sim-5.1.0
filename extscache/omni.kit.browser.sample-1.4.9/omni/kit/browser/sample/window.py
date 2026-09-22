# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
import omni.ui as ui

from .browser_widget import SampleTreeFolderBrowserWidget
from .model import SampleBrowserModel


class SampleBrowserWindow(ui.Window):  # pylint: disable=too-few-public-methods
    """Window that shows all different types of Samples."""

    WINDOW_TITLE = "Examples"

    def __init__(self, model: SampleBrowserModel):
        """Browser Window takes a SampleBrowserModel and displays a FolderBrowserWidget.

        Args:
            model: SampleBrowserModel that contains data for the folder hierarchy.
        """
        super().__init__(self.WINDOW_TITLE)

        self._widget = None
        self._browser_model = model

        self.frame.set_build_fn(self._build_ui)

        # Dock it to the same space where Stage is docked.
        self.deferred_dock_in("Content")

    def _build_ui(self):
        with self.frame:
            with ui.VStack(spacing=15):
                self._widget = SampleTreeFolderBrowserWidget(
                    self._browser_model,
                )
