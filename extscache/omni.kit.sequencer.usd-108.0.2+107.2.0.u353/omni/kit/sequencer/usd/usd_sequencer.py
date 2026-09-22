import math
from functools import lru_cache
from typing import List, Optional, Tuple

import omni.timeline
import omni.usd
import omni.usd.audio
from pxr import Sdf, Usd
import SequenceSchema

from . import utils
from .sequence_player import g_sequence_player


@lru_cache()
def g_audio_interface():
    return omni.usd.audio.get_stage_audio_interface()


@lru_cache()
def g_timeline_interface():
    return omni.timeline.get_timeline_interface()


def get_sequences(stage=None) -> List[SequenceSchema.Sequence]:
    """Get all sequences in the stage."""
    if stage is None:
        stage = omni.usd.get_context().get_stage()
    if not stage:
        return []
    return [SequenceSchema.Sequence(prim) for prim in stage.Traverse() if prim.IsA(SequenceSchema.Sequence)]


def get_sequence(stage) -> Optional[SequenceSchema.Sequence]:
    """Find first sequence prim"""
    for prim in stage.Traverse():
        if prim.IsA(SequenceSchema.Sequence):
            return SequenceSchema.Sequence(prim)
    # No Sequence found.
    return None


def _get_anim_length(prim) -> float:
    range = _get_anim_start_end(prim)
    if range:
        return range[1] - range[0]
    return 0


def _get_anim_start_end(prim) -> Tuple[float, float]:
    if g_sequence_player is None:
        return 0, 0

    layer = g_sequence_player.cache_anim(prim)
    if layer is None:
        return 0, 0

    if not layer.HasStartTimeCode() or not layer.HasEndTimeCode():
        return 0, 0

    return layer.startTimeCode, layer.endTimeCode


def _get_audio_length(prim) -> Optional[float]:
    """Get audio length in seconds"""
    length = g_audio_interface().get_sound_length(prim, omni.usd.audio.SoundLengthType.ASSET_LENGTH)
    if length == 0.0:
        return None
    return length


def _get_audio_available_range(prim: Usd.Prim) -> Tuple[float, float]:
    frames_per_second = g_timeline_interface().get_time_codes_per_seconds()
    start_time = 0
    audio_length = _get_audio_length(prim)
    if audio_length:
        end_time = audio_length * frames_per_second
        return start_time, end_time
    return 0, 0


def get_prim_available_range(prim) -> Tuple[float, float]:
    """Get the available range of the prim's source media. (start time and end time)"""
    audio_prim = find_prim_of_type(prim, "Sound")
    if audio_prim is not None:
        return _get_audio_available_range(audio_prim)
    if utils.is_curve_node(prim):
        return utils.get_anim_data_range(prim)
    return _get_anim_start_end(prim)


def get_prim_available_length(prim) -> float:
    """Get the available length of the prim's source media in timecodes."""
    audio_prim = find_prim_of_type(prim, "Sound")
    if audio_prim is not None:
        audio_length = _get_audio_length(audio_prim)
        if audio_length:
            return audio_length * g_timeline_interface().get_time_codes_per_seconds()

    if utils.is_curve_node(prim):
        range = utils.get_anim_data_range(prim)
        if range is not None:
            return range[1] - range[0]
        else:
            return 0

    length = _get_anim_length(prim)
    return length


def get_target_prim_from_track(track):
    track_prim = track.GetPrim()
    target_rel = track_prim.GetRelationship("sequencer:trackTarget")
    if target_rel is not None:
        return target_rel.GetTargets()


def get_content_prim_from_sequence(sequence):
    sequence_prim = sequence.GetPrim()
    target_rel = sequence_prim.GetRelationship("sequencer:sourceContent")
    if target_rel is not None:
        return target_rel.GetTargets()


def get_track_target(track_path: str):
    stage = omni.usd.get_context().get_stage()
    track_prim = stage.GetPrimAtPath(track_path)
    track = SequenceSchema.Track(track_prim)
    if track:
        return get_target_prim_from_track(track)


def get_target_prim_from_clip(clip) -> Usd.Prim:
    if not clip:
        return None
    relationship = None
    if SequenceSchema.AssetClipBase(clip):
        relationship = SequenceSchema.AssetClipBase(clip).GetAssetPrimRel()
    if not relationship:
        return None
    paths = relationship.GetTargets()
    if len(paths) <= 0:
        return None
    stage = omni.usd.get_context().get_stage()
    prim = stage.GetPrimAtPath(paths[0])
    if prim and prim.IsValid():
        return prim


def _get_animation_prim_from_clip(clip):
    if not clip:
        return None
    anim_rel = SequenceSchema.AssetClipBase(clip).GetAnimationRel()
    targets = anim_rel.GetTargets()
    if len(targets) <= 0:
        return None
    stage = omni.usd.get_context().get_stage()
    prim = stage.GetPrimAtPath(targets[0])
    if prim and prim.IsValid():
        return prim


def get_ancestor_sequence_from_prim(prim):
    parent = prim.GetParent()
    while parent:
        if parent.IsA(SequenceSchema.Sequence):
            return SequenceSchema.Sequence(parent)
        parent = parent.GetParent()


def find_prim_of_type(root_prim, type) -> Usd.Prim:
    """Find first prim of type, starting from target prim and searching children."""
    if not root_prim or not root_prim.IsValid():
        return None
    this_type = root_prim.GetTypeName()
    if this_type == type:
        return root_prim
    for p in root_prim.GetChildren():
        ret = find_prim_of_type(p, type)
        if ret is not None:
            return ret
    return None


def get_clip_length(clip) -> float:
    """Returns clip length in timecodes"""
    clip_start = clip.GetStartTimeAttr().Get()
    clip_end = clip.GetEndTimeAttr().Get()
    return clip_end - clip_start


def get_clip_source_length(clip: SequenceSchema.ClipBase) -> float:
    """Returns the clip source length if set (playEnd - playStart)"""
    play_start = clip.GetPlayStartAttr().Get()
    play_end = clip.GetPlayEndAttr().Get()
    if not math.isnan(play_start) and not math.isnan(play_end):
        return play_end - play_start
    return 0


def get_clip_anim_source_prim(clip: SequenceSchema.ClipBase) -> Optional[Usd.Prim]:
    """Get the current source input prim for animation."""
    anim_prim = _get_animation_prim_from_clip(clip)
    if anim_prim:
        return anim_prim
    target_prim = get_target_prim_from_clip(clip)
    if target_prim:
        return target_prim
    return None


def get_clip_available_range(clip: SequenceSchema.ClipBase) -> Tuple[float, float]:
    animation_prim = _get_animation_prim_from_clip(clip)
    if animation_prim:
        return get_prim_available_range(animation_prim)
    target_prim = get_target_prim_from_clip(clip)
    if target_prim:
        return get_prim_available_range(target_prim)
    return (0, 0)


def get_clip_available_length(clip: SequenceSchema.ClipBase) -> float:
    """Get the clip source length, if any."""
    target_prim = get_target_prim_from_clip(clip)
    animation_prim = _get_animation_prim_from_clip(clip)
    length = 0.0
    # check anim length first
    if animation_prim:
        length = get_prim_available_length(animation_prim)
    if length:
        return length
    # now check target prim length
    if target_prim:
        length = get_prim_available_length(target_prim)
    return length


def calculate_clip_length(clip, min_length=1) -> float:
    """Calculate default clip length from target/animation prims"""
    clip_start = clip.GetStartTimeAttr().Get()
    clip_end = clip.GetEndTimeAttr().Get()
    if clip_start is None or clip_end is None:
        return float(min_length)

    source_length = get_clip_available_length(clip)
    if source_length:
        return max(min_length, source_length)

    return float(min_length)


def get_track_from_path(stage, prim_path) -> Optional[SequenceSchema.Track]:
    if stage:
        prim = stage.GetPrimAtPath(prim_path)
        if prim:
            return SequenceSchema.Track(prim)
    return None


def get_clip_from_path(stage, prim_path):
    if stage:
        prim = stage.GetPrimAtPath(prim_path)
        if prim:
            return SequenceSchema.ClipBase(prim)
    return None


def get_asset_clip_from_path(stage, prim_path):
    if stage:
        prim = stage.GetPrimAtPath(prim_path)
        if prim:
            return SequenceSchema.AssetClipBase(prim)
    return None


def get_clip_animations(clip):
    anim_rel = None
    if SequenceSchema.AssetClipBase(clip):
        anim_rel = SequenceSchema.AssetClipBase(clip).GetAnimationRel()
    if anim_rel is not None:
        return anim_rel.GetTargets()
    return None


def set_clip_animations(clip, targets):
    if SequenceSchema.AssetClipBase(clip):
        anim_rel = SequenceSchema.AssetClipBase(clip).GetAnimationRel()
        if targets:
            anim_rel.SetTargets(targets)
        else:
            anim_rel.ClearTargets(True)


def get_clip_targets(clip):
    rel = SequenceSchema.AssetClipBase(clip).GetAssetPrimRel()
    if rel is not None:
        return rel.GetTargets()
    return None


def set_clip_targets(clip, targets):
    if SequenceSchema.AssetClipBase(clip):
        prim_rel = SequenceSchema.AssetClipBase(clip).GetAssetPrimRel()
        if targets:
            prim_rel.SetTargets(targets)
        else:
            prim_rel.ClearTargets(True)


def _get_clip_trim(clip: SequenceSchema.AssetClip) -> Tuple[Optional[Sdf.TimeCode], Optional[Sdf.TimeCode]]:
    """Returns the clip play end and play start"""
    play_start = clip.GetPlayStartAttr().Get()
    play_end = clip.GetPlayEndAttr().Get()
    return play_start, play_end


def get_clip_source_time_from_parent_time(clip: SequenceSchema.AssetClip, parent_time: float):
    start_time = clip.GetStartTimeAttr().Get().GetValue()
    play_rate = abs(clip.GetPlayRateAttr().Get())
    play_start, play_end = _get_clip_trim(clip)
    play_offset = clip.GetPlayOffsetAttr().Get()
    if math.isnan(play_offset):
        play_offset = 0
    looping = clip.GetLoopAttr().Get()
    return utils.get_source_time_from_parent_time(
        float(parent_time),
        start_time,
        play_rate,
        float(play_start),
        float(play_end),
        float(play_offset),
        looping=looping,
    )


def sequence_schema_plugin_loaded():
    def _getSchemaPrimDef(schema):
        isApi = Usd.SchemaRegistry().IsAppliedAPISchema(schema)
        schemaToken = (
            Usd.SchemaRegistry().GetAPISchemaTypeName(schema)
            if isApi
            else Usd.SchemaRegistry().GetConcreteSchemaTypeName(schema)
        )
        # carb.log_verbose(f"schema: {schema}, isApi: {isApi}, schemaToken: {schemaToken}")
        return (
            Usd.SchemaRegistry().FindAppliedAPIPrimDefinition(schemaToken)
            if isApi
            else Usd.SchemaRegistry().FindConcretePrimDefinition(schemaToken)
        )

    expected_prim_types = [
        SequenceSchema.Sequence,
        SequenceSchema.Track,
        SequenceSchema.AssetClip,
        SequenceSchema.ShotClip,
    ]

    for prim_type in expected_prim_types:
        if not _getSchemaPrimDef(prim_type):
            return False
    return True


def get_anim_data_from_tgt_prim(prim):
    if utils.anim_curve is None:
        return None

    curve_prims = utils.anim_curve.get_curve_plugin().get_curve_prims(str(prim.GetPath()))
    if curve_prims:
        return curve_prims[0]

    return None
