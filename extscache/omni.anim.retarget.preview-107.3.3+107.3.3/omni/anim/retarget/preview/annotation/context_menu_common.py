# Copyright (c) 2021-2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#


from .. import zoom_handler


def show_if_zoomed(objects):
    timeline_name = objects['timeline_name']
    return zoom_handler.ZoomHandler().get_zoom(timeline_name).zoomed


def show_if_not_zoomed(objects):
    return not show_if_zoomed(objects)


def on_reset_zoom_timeline(objects):
    timeline_name = objects['timeline_name']
    zoom_state: zoom_handler.ZoomState = zoom_handler.ZoomHandler().get_zoom(timeline_name=timeline_name)
    zoom_state.reset_zoom()
