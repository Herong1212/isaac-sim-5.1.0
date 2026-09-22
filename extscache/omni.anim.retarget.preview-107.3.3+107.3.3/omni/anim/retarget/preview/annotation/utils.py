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
import omni.usd.commands
from pxr import Sdf, Usd, UsdSkel
from typing import Optional
from .annotation_model import Annotation
from ..model.source_model import SourceModel


def get_annotation_prim_type() -> str:
    return 'SkelAnimationAnnotation'


def is_annotation_prim(prim: Usd.Prim) -> bool:
    return prim.GetTypeName() == get_annotation_prim_type()


def get_annotation_property_names() -> list:
    return ['tag', 'start', 'end']


def extract_annotation(prim: Usd.Prim, parent_source: SourceModel = None) -> Annotation:
    if not is_annotation_prim(prim):
        return None
    tag_attr = prim.GetAttribute('tag')
    time_start_attr = prim.GetAttribute('start')
    time_end_attr = prim.GetAttribute('end')
    if not tag_attr.IsValid() or not time_start_attr.IsValid() or not time_end_attr.IsValid():
        return None
    tag = tag_attr.Get()
    time_start = time_start_attr.Get()
    time_end = time_end_attr.Get()
    if tag is None or time_start is None or time_end is None:
        return None
    source = SourceModel()
    source.set_source_path_in_stage(str(prim.GetPath()))
    source_url, exists = None, True
    # Parent came from an external file, not main stage
    if parent_source is not None and parent_source.is_external:
        source_url = parent_source.source_url
        exists = False
    source.set_source_url(source_url, exists=exists)
    annotation = Annotation(tag=tag, start=time_start, end=time_end, source=source)
    return annotation


def extract_annotations(prim: Usd.Prim, source: SourceModel = None) -> list:
    if not prim.IsValid() or not prim.IsA(UsdSkel.Animation):
        return []
    annotations = []
    for child_prim in prim.GetAllChildren():
        annotation = extract_annotation(child_prim, source)
        if annotation is not None:
            annotations.append(annotation)
    return annotations


def get_annotations(
    prim: Usd.Prim,
    tag: Optional[str] = None,
    start_time: Optional[int] = None,
    end_time: Optional[int] = None,
    exact_times: bool = True,
    source: Optional[SourceModel] = None,
) -> list:
    """
    Returns annotations with the given parameters from a SkelAnimation prim.
        Only the default context and stage are supported.
    Args:
        prim (Usd.Prim): The SkelAnimation prim.
        tag (str): Tag string of the annotation. None by default.
            If None is passed, all annotations with the given start or end times are returned.
        start_time (int): Start time of the annotation in frames. None by default.
            If None is passed, all annotations with the given tag and end times are returned.
        end_time (int): End time of the annotation in frames. None by default.
            If None is passed, all annotations with the given tag and start times are returned.
        exact_times (bool): whether start and end times have to be exact or they represent an interval. True by default.
            False means all annotations that start after start_time and end between end_time are returned.
        source (SourceModel): source of 'prim'

    Examples:
        # Returns all annotations.
        get_annotations(my_anim_prim)

        # Returns all annotations with tag "Walk"
        get_annotations(my_anim_prim, tag='Walk')

         # Returns all annotations that start exactly at time code 50
        get_annotations(my_anim_prim, start_time=50)

        # Returns all annotations that start at time code 50 or later
        get_annotations(my_anim_prim, start_time=50, exact_times=False)

        # Returns all annotations that fall in the [50, 100] time code interval
        get_annotations(my_anim_prim, start_time=50, end_time=100, exact_times=False)
    """
    all_annotations = extract_annotations(prim, source)
    result = []
    for annotation in all_annotations:
        annotation: Annotation
        matches = True
        if tag is not None:
            matches = matches and tag == annotation.tag
        if matches and start_time is not None:
            if exact_times:
                matches = matches and start_time == annotation.start
            else:
                matches = matches and start_time <= annotation.start
        if matches and end_time is not None:
            if exact_times:
                matches = matches and end_time == annotation.end
            else:
                matches = matches and end_time >= annotation.end

        if matches:
            result.append(annotation)
    return result


def add_annotation(prim: Usd.Prim, annotation: Annotation):
    # TODO: check if attribute exists
    prim.CreateAttribute('tag', Sdf.ValueTypeNames.Token)
    prim.GetAttribute('tag').Set(annotation.tag)

    prim.CreateAttribute('start', Sdf.ValueTypeNames.Int64)
    prim.GetAttribute('start').Set(annotation.start)

    prim.CreateAttribute('end', Sdf.ValueTypeNames.Int64)
    prim.GetAttribute('end').Set(annotation.end)


def update_annotation(prim: Usd.Prim, annotation: Annotation, stage: Usd.Stage):
    # TODO: check if attribute exists
    attr_names = ['tag', 'start', 'end']
    values = [annotation.tag, annotation.start, annotation.end]
    with omni.kit.undo.group():
        for attr_name, value in zip(attr_names, values):
            attr_path = prim.GetPath().AppendProperty(attr_name)
            omni.kit.commands.execute("ChangePropertyCommand", prop_path=attr_path, value=value, prev=None, usd_context_name=stage)


def time_to_timecode(time: float, timeline: omni.timeline.Timeline = None) -> float:
    if timeline is None:
        timeline = omni.timeline.get_timeline_interface()
    return time * timeline.get_time_codes_per_seconds()


def timecode_to_time(time: int, timeline: omni.timeline.Timeline = None) -> float:
    if timeline is None:
        timeline = omni.timeline.get_timeline_interface()
    return time / timeline.get_time_codes_per_seconds()
