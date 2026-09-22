# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
import omni.ui as ui


class ImageView:
    """The widget that shows the image with the ability to navigate"""

    def __init__(self, filename, **kwargs):
        with ui.CanvasFrame(style_type_name_override="ImageView", **kwargs):
            self.__image = ui.Image(filename)

    def set_progress_changed_fn(self, fn):
        """Callback that is called when control state is changed"""
        self.__image.set_progress_changed_fn(fn)

    def destroy(self):
        if self.__image:
            self.__image.destroy()
        self.__image = None
