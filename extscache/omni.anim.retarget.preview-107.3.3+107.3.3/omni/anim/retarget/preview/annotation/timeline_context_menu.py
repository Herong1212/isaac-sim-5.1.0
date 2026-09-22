# Copyright (c) 2021-2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#


import omni.kit.commands
import omni.timeline
from .annotation_model import AnnotationSet
from .context_menu_common import (
    show_if_zoomed,
    on_reset_zoom_timeline
)
from .utils import time_to_timecode


def show_if_parent_is_valid(objects):
    annotations: AnnotationSet = objects['annotations']
    return annotations is not None and annotations.parent_anim is not None and\
        not annotations.parent_anim.is_read_only()


def show_if_has_animations(objects):
    annotations: AnnotationSet = objects['annotations']
    return annotations is not None and len(annotations.annotations) > 0


def on_annotation_create_clicked(objects):
    annotations: AnnotationSet = objects['annotations']
    parent_path = annotations.parent_anim.source_path_in_stage
    omni.kit.commands.execute('AnimationPreviewAddAnnotationCommand',
        path=parent_path,
        timeline_name=objects['timeline_name']
    )


def on_annotation_create_from_current_time_clicked(objects):
    annotations: AnnotationSet = objects['annotations']
    parent_path = annotations.parent_anim.source_path_in_stage
    timeline_name = objects['timeline_name']
    timeline = omni.timeline.get_timeline_interface(timeline_name)
    start_time = int(time_to_timecode(timeline.get_current_time(), timeline))
    omni.kit.commands.execute('AnimationPreviewAddAnnotationCommand',
        path=parent_path,
        start_time=start_time,
        timeline_name=timeline_name
    )


def on_annotations_clear_clicked(objects):
    annotations: AnnotationSet = objects['annotations']
    parent_path = annotations.parent_anim.source_path_in_stage
    omni.kit.commands.execute('AnimationPreviewRemoveAnnotationsCommand', path=parent_path)


timeline_menu_list = [
    {
        "name": "Create new Annotation",
        "glyph": "menu_plus.svg",
        "show_fn": show_if_parent_is_valid,
        "onclick_fn": on_annotation_create_clicked,
    },

    {
        "name": "Create new Annotation from current time",
        "glyph": "menu_plus.svg",
        "show_fn": show_if_parent_is_valid,
        "onclick_fn": on_annotation_create_from_current_time_clicked,
    },

    {
        "name": "End zoom",
        "glyph": "menu_search.svg",
        "show_fn": show_if_zoomed,
        "onclick_fn": on_reset_zoom_timeline,
    },

    {
        "name": "Delete all Annotations",
        "glyph": "menu_delete.svg",
        "show_fn": [show_if_parent_is_valid, show_if_has_animations],
        "onclick_fn": on_annotations_clear_clicked,
    },
]
