# Copyright (c) 2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
"""
Omni Timeline
---------------------

The Omni Timeline extension provides a programming interface for managing timeline operations within Omniverse. 
This extension enables developers to programmatically control the playback and timing of the main timeline, as well as to create custom timeline instances for special use cases. 
It supports the registration of callback functions, which are triggered upon various timeline state changes, such as updates to the current time. 
"""

from ._timeline import *


def get_timeline_interface(timeline_name: str='') -> Timeline:
    """Returns the timeline with the given name via cached :class:`omni.timeline.ITimeline` interface"""

    if not hasattr(get_timeline_interface, "timeline"):
        get_timeline_interface.timeline = acquire_timeline_interface()
    return get_timeline_interface.timeline.get_timeline(timeline_name)

def destroy_timeline(timeline_name: str):
    """Destroys a timeline object with the given name, if it is not the default timeline and it is not in use."""

    if not hasattr(get_timeline_interface, "timeline"):
        get_timeline_interface.timeline = acquire_timeline_interface()
    return get_timeline_interface.timeline.destroy_timeline(timeline_name)
