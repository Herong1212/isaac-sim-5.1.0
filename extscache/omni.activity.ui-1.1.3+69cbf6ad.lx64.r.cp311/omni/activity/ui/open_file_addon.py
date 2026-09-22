# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
import omni.ui as ui
import asyncio
from .activity_progress_bar import ProgressBarWidget


class OpenFileAddon:
    def __init__(self):
        self._stop_event = asyncio.Event()

        # The progress
        with ui.Frame(height=355):
            self.activity_widget = ProgressBarWidget()

    def new(self, model):
        self.activity_widget.new(model)

    def __del__(self):
        self.activity_widget.destroy()
        self._stop_event.set()

    def mouse_pressed(self, *args):
        # Bind this class to the rectangle, so when Rectangle is deleted, the
        # class is deleted as well
        pass

    def start_timer(self):
        self.activity_widget.reset_timer()

    def stop_timer(self):
        self.activity_widget.stop_timer()
