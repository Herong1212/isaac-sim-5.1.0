# Copyright (c) 2021-2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#


import omni.kit.commands
import omni.kit.undo
import omni.timeline
from .annotation_model import Annotation, AnnotationSet
from .context_menu_common import (
    show_if_not_zoomed,
    show_if_zoomed,
    on_reset_zoom_timeline
)
from .utils import time_to_timecode
from ..model.source_model import SourceModel
from .. import zoom_handler


def show_not_readonly(objects):
    source: SourceModel = objects['source']
    if source is None:
        return False
    return not source.is_read_only()


def on_annotation_delete_clicked(objects):
    source: SourceModel = objects['source']
    if source is not None:
        omni.kit.commands.execute("DeletePrimsCommand", paths=[source.source_path_in_stage])


def on_annotation_set_start_time_clicked(objects):
    annotation: Annotation = objects['annotation']
    timeline_name = objects['timeline_name']
    timeline = omni.timeline.get_timeline_interface(timeline_name)
    time = int(time_to_timecode(timeline.get_current_time(), timeline))
    time_max = int(time_to_timecode(timeline.get_end_time(), timeline))
    with omni.kit.undo.group():
        if annotation.end <= time:
            annotation.end = min(time + annotation.length, time_max)
        annotation.start = time


def on_annotation_set_end_time_clicked(objects):
    annotation: Annotation = objects['annotation']
    timeline_name = objects['timeline_name']
    timeline = omni.timeline.get_timeline_interface(timeline_name)
    time = int(time_to_timecode(timeline.get_current_time(), timeline))
    time_min = int(time_to_timecode(timeline.get_start_time(), timeline))
    with omni.kit.undo.group():
        if time <= annotation.start:
            annotation.start = max(time - annotation.length, time_min)
        annotation.end = time


def on_annotation_zoom_timeline(objects):
    annotation: Annotation = objects['annotation']
    timeline_name = objects['timeline_name']
    zoom_state: zoom_handler.ZoomState = zoom_handler.ZoomHandler().get_zoom(timeline_name=timeline_name)
    zoom_state.zoom(zoom_handler.Range(annotation.start, annotation.end))


def on_annotation_stretch_start_clicked(objects):
    annotation: Annotation = objects['annotation']
    annotation_set: AnnotationSet = objects['all_annotations']
    timeline_name = objects['timeline_name']
    timeline = omni.timeline.get_timeline_interface(timeline_name)
    start_time = int(time_to_timecode(timeline.get_start_time(), timeline))
    annotation_set.stretch_left(annotation, start_time)


def on_annotation_stretch_end_clicked(objects):
    annotation: Annotation = objects['annotation']
    annotation_set: AnnotationSet = objects['all_annotations']
    timeline_name = objects['timeline_name']
    timeline = omni.timeline.get_timeline_interface(timeline_name)
    end_time = int(time_to_timecode(timeline.get_end_time(), timeline))
    annotation_set.stretch_right(annotation, end_time)


def on_annotation_fit_start_clicked(objects):
    annotation: Annotation = objects['annotation']
    annotation_set: AnnotationSet = objects['all_annotations']
    annotation_set.fit_left(annotation)


def on_annotation_fit_end_clicked(objects):
    annotation: Annotation = objects['annotation']
    annotation_set: AnnotationSet = objects['all_annotations']
    annotation_set.fit_right(annotation)


def on_annotation_stretch_both_clicked(objects):
    annotation: Annotation = objects['annotation']
    annotation_set: AnnotationSet = objects['all_annotations']
    timeline_name = objects['timeline_name']
    timeline = omni.timeline.get_timeline_interface(timeline_name)
    start_time = int(time_to_timecode(timeline.get_start_time(), timeline))
    end_time = int(time_to_timecode(timeline.get_end_time(), timeline))
    annotation_set.stretch_bounds(annotation, start_time, end_time)


def on_annotation_fit_both_clicked(objects):
    annotation: Annotation = objects['annotation']
    annotation_set: AnnotationSet = objects['all_annotations']
    annotation_set.fit_bounds(annotation)


annotation_menu_list = [
    {"glyph": "menu_rename.svg", "show_fn": show_not_readonly, "name": {
            'Set start time...':
            [
                {'name': 'Fit', 'onclick_fn': on_annotation_fit_start_clicked, "show_fn": show_not_readonly},
                {'name': 'Stretch', 'onclick_fn': on_annotation_stretch_start_clicked, "show_fn": show_not_readonly},
                {'name': 'To current time', 'onclick_fn': on_annotation_set_start_time_clicked, "show_fn": show_not_readonly}
            ]
        },
    },

    {"glyph": "menu_rename.svg", "show_fn": show_not_readonly, "name": {
            'Set end time...':
            [
                {'name': 'Fit', 'onclick_fn': on_annotation_fit_end_clicked, "show_fn": show_not_readonly},
                {'name': 'Stretch', 'onclick_fn': on_annotation_stretch_end_clicked, "show_fn": show_not_readonly},
                {'name': 'To current time', 'onclick_fn': on_annotation_set_end_time_clicked, "show_fn": show_not_readonly}
            ]
        },
    },

    {"glyph": "menu_rename.svg", "show_fn": show_not_readonly, "name": {
            'Adjust both ends...':
            [
                {'name': 'Fit', 'onclick_fn': on_annotation_fit_both_clicked, "show_fn": show_not_readonly},
                {'name': 'Stretch', 'onclick_fn': on_annotation_stretch_both_clicked, "show_fn": show_not_readonly},
            ]
        },
    },

    {
        "name": "Zoom timeline to Annotation",
        "glyph": "menu_search.svg",
        "show_fn": show_if_not_zoomed,
        "onclick_fn": on_annotation_zoom_timeline,
    },

    {
        "name": "End zoom",
        "glyph": "menu_search.svg",
        "show_fn": show_if_zoomed,
        "onclick_fn": on_reset_zoom_timeline,
    },

    {
        "name": "Delete Annotation",
        "glyph": "menu_delete.svg",
        "show_fn": show_not_readonly,
        "onclick_fn": on_annotation_delete_clicked,
    },
]
