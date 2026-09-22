# Copyright (c) 2021-2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#


import asyncio
import omni.kit.app
import omni.kit.undo
import omni.ui as ui
import omni.usd
from typing import Optional
from pxr import Sdf, Usd, Tf
from omni.kit.widget.layers import LayerUtils
from ..model.source_model import SourceModel

ALLOW_OVERLAP = True


class Annotation(ui.AbstractValueModel):
    def __init__(self, tag: str, start, end, source: SourceModel = None, color: int = None):
        self._tag = ui.SimpleStringModel(tag)
        self._start = ui.SimpleIntModel(start)
        self._end = ui.SimpleIntModel(end)
        self.color = color
        self.source = source
        self._tag_changed_sub = self._tag.add_end_edit_fn(self._on_value_changed)
        self._start_changed_sub = self._start.add_end_edit_fn(self._on_value_changed)
        self._end_changed_sub = self._end.add_end_edit_fn(self._on_value_changed)
        super().__init__()

    @property
    def tag(self) -> str:
        return self._tag.as_string

    @tag.setter
    def tag(self, value: str):
        if self._tag.as_string != value:
            self._tag.set_value(value)
            self._value_changed()

    @property
    def start(self):
        return self._start.as_int

    @start.setter
    def start(self, value):
        if self._start.as_int != value:
            self._start.set_value(value)
            self._value_changed()

    @property
    def end(self):
        return self._end.as_int

    @end.setter
    def end(self, value):
        if self._end.as_int != value:
            self._end.set_value(value)
            self._value_changed()

    @property
    def tag_model(self) -> ui.SimpleStringModel:
        return self._tag

    @property
    def start_model(self) -> ui.SimpleIntModel:
        return self._start

    @property
    def end_model(self) -> ui.SimpleIntModel:
        return self._end

    @property
    def length(self):
        return self.end - self.start

    @property
    def name(self):
        source_path = 'unknown path' if self.source is None else self.source.source_path_in_stage
        return "{}_{}-{} ({})".format(self.tag, self.start, self.end, source_path)

    @property
    def parent_path(self) -> Sdf.Path:
        if self.source is None:
            return None
        return Sdf.Path(self.source.source_path_in_stage).GetParentPath()

    def get_value_as_string(self) -> str:
        return self.name

    def get_value_as_bool(self) -> bool:
        return True

    def get_value_as_float(self) -> float:
        return float(self.length)

    def get_value_as_int(self) -> int:
        return self.length

    def set_values_without_usd_sync(self, tag: str, start, end) -> bool:
        ''' Sets values without syncing back to USD
        Returns:
            True if any attributes are changed
        '''
        values_changed = False
        if tag != self.tag:
            self._tag.set_value(tag)
            values_changed = True
        if start != self.start:
            self._start.set_value(round(start))
            values_changed = True
        if end != self.end:
            self._end.set_value(round(end))
            values_changed = True
        return values_changed

    def set_values(self, tag: str, start, end) -> bool:
        changed = self.set_values_without_usd_sync(tag, start, end)
        if changed:
            self._value_changed()
        return changed

    def write_to_usd(self):
        from .utils import is_annotation_prim, update_annotation
        if self.source and not self.source.is_external:
            stage = omni.usd.get_context().get_stage()
            prim = stage.GetPrimAtPath(self.source.source_path_in_stage)
            if prim.IsValid() and is_annotation_prim(prim):
                # change the payload usd file instead of over in current stage
                payload_url = omni.usd.get_url_from_prim(prim.GetParent())
                if payload_url is None:
                    return
                payload_stage = Usd.Stage.Open(payload_url)
                if payload_stage is None :
                    return
                if payload_stage.HasDefaultPrim():
                    root_path = payload_stage.GetDefaultPrim().GetPath()
                else:
                    root_path = Sdf.Path.absoluteRootPath

                payload_prim_path = root_path.AppendChild(self.source.path_name)
                payload_prim = payload_stage.GetPrimAtPath(payload_prim_path)
                if payload_prim:
                    update_annotation(payload_prim, self, payload_stage)
                    # the stage window show the prim name instead of tag, so we change name too.
                    # the payload stage has't context, so write layer directly instead of by command
                    if self.source.path_name != self.tag:
                        path_from = payload_prim_path
                        path_to = path_from.GetParentPath().AppendChild(self.tag)
                        edit_target_layer = payload_stage.GetEditTarget().GetLayer()
                        with Usd.EditContext(payload_stage, edit_target_layer):
                            Sdf.CreatePrimInLayer(edit_target_layer, path_to)
                            Sdf.CopySpec(edit_target_layer, path_from, edit_target_layer, path_to)
                            LayerUtils.remove_prim_spec(edit_target_layer, path_from)
                payload_stage.Save()

    def _on_value_changed(self, value):
        self._value_changed()

    def _value_changed(self) -> None:
        self.write_to_usd()
        return super()._value_changed()

    def __del__(self):
        self.destroy()

    def destroy(self):
        self._tag = None
        self._start = None
        self._end = None
        self.source = None
        self.color = None
        self._tag_changed_sub = None
        self._start_changed_sub = None
        self._end_changed_sub = None


class AnnotationSet(ui.AbstractValueModel):
    def __init__(self,
        time_codes_per_second,
        parent_anim: Optional[SourceModel] = None,
        source_context: Optional[omni.usd.UsdContext] = None
    ):
        if source_context is None:
            self._source_context = omni.usd.get_context()
        else:
            self._source_context = source_context
        self._parent_anim = parent_anim
        self._annotations = []
        self._tracks = {}
        self._dirty_tracks = False
        self._value_changed_signal_enabled = True  # sometimes we do not want to send events for all changes
        self._usd_listener = Tf.Notice.Register(Usd.Notice.ObjectsChanged, self._process_usd_change, None)
        self._time_codes_per_second = time_codes_per_second
        super().__init__()

    def add_annotation(self, annotation: Annotation):
        self._annotations.append(annotation)
        self._dirty_tracks = True
        if self._value_changed_signal_enabled:
            self._sort_annotations()
            self._value_changed()

    def set_annotations(self, annotations):
        self._annotations = annotations
        self._dirty_tracks = True
        if self._value_changed_signal_enabled:
            self._sort_annotations()
            self._value_changed()

    def remove_annotation(self, annotation: Annotation):
        self._annotations.remove(annotation)
        self._dirty_tracks = True
        if self._value_changed_signal_enabled:
            self._value_changed()

    def set_color(self, color_on_time_overlap: int, color_base: int, time: int):
        """ Sets color of all annotations based based on whether they overlap with a given time
        Args:
            color_on_time_overlap (int): Color code to use if the annotation overlaps with the given time
            color_base (int): Color code to use if the annotation does not overlap with the given time
            time (int): time code
        """
        for annotation in self._annotations:
            if annotation.start <= time <= annotation.end:
                annotation.color = color_on_time_overlap
            else:
                if color_base is not None:
                    annotation.color = color_base

    def is_empty(self) -> bool:
        return len(self._annotations) == 0

    @property
    def annotations(self):
        return self._annotations

    @property
    def tracks(self):
        if self._dirty_tracks:
            self._rebuild_tracks()
            self._dirty_tracks = False
        return self._tracks

    @property
    def parent_anim(self) -> SourceModel:
        return self._parent_anim

    @property
    def time_codes_per_second(self) -> float:
        return self._time_codes_per_second

    def stretch_right(self, annotation: Annotation, timeline_end: int):
        if annotation not in self._annotations:
            return

        found = False
        for a in self._annotations:
            if annotation.end <= a.start:
                annotation.end = a.start
                found = True
                break  # annotations are sorted by start time
        if not found:
            annotation.end = timeline_end

        self._sort_annotations()
        self._dirty_tracks = True

    def stretch_left(self, annotation: Annotation, timeline_start: int):
        if annotation not in self._annotations:
            return

        t_max = timeline_start
        for a in self._annotations:
            if t_max < a.end <= annotation.start:
                t_max = a.end
            if annotation.start <= a.start:
                break  # annotations are sorted by start time
        if annotation.start == t_max:
            return
        annotation.start = t_max
        self._sort_annotations()
        self._dirty_tracks = True

    def fit_right(self, annotation: Annotation):
        if annotation not in self._annotations:
            return

        t_min = annotation.end
        for a in self._annotations:
            if annotation.start < a.start < annotation.end:
                t_min = min(t_min, a.start)
            if annotation.end < a.start:
                break  # annotations are sorted by start time
        if annotation.end == t_min:
            return

        annotation.end = t_min
        self._sort_annotations()
        self._dirty_tracks = True

    def fit_left(self, annotation: Annotation):
        if annotation not in self._annotations:
            return

        t_max = annotation.start
        for a in self._annotations:
            if annotation.start < a.end < annotation.end:
                t_max = max(t_max, a.end)
            if annotation.end < a.start:
                break  # annotations are sorted by start time
        if annotation.start == t_max:
            return

        annotation.start = t_max
        self._sort_annotations()
        self._dirty_tracks = True

    def stretch_bounds(self, annotation: Annotation, timeline_start: int, timeline_end: int):
        with omni.kit.undo.group():
            self.stretch_left(annotation, timeline_start)
            self.stretch_right(annotation, timeline_end)

    def fit_bounds(self, annotation: Annotation):
        with omni.kit.undo.group():
            self.fit_left(annotation)
            self.fit_right(annotation)

    def _rebuild_tracks(self):
        if len(self._annotations) == 0:
            self._tracks = {}
            return
        tracks = {}
        if ALLOW_OVERLAP:  # Create multiple tracks when annotations overlap
            tracks[self._track_name(0)] = []
            track_ends = [self._annotations[0].start - 1]
            i = 0
            for annotation in self._annotations:
                i = i + 1
                current_track = 0  # Always try to place to the first track then try from top to bottom
                while current_track < len(track_ends) and track_ends[current_track] > annotation.start:
                    current_track = current_track + 1
                if current_track == len(track_ends):  # create a new track
                    tracks[self._track_name(current_track)] = []
                    track_ends.append(annotation.end)
                tracks[self._track_name(current_track)].append(annotation)
                track_ends[current_track] = annotation.end
        else:  # Put all annotations into a single track if overlapping is allowed
            tracks[self._track_name(0)] = self._annotations
        self._tracks = tracks

    def _track_name(self, track_index: int) -> str:
        return str(track_index + 1)

    def _process_usd_change(self, objects, stage):
        if self._source_context is None or stage != self._source_context.get_stage():
            return

        modified_paths = objects.GetResyncedPaths()

        # To detect if the parent SkelAnim was also moved
        parent_path = None
        if self._parent_anim is not None and not self._parent_anim.is_external:
            parent_path = self._parent_anim.source_path_in_stage
        if len(self._annotations) > 0:
            is_parent_renamed = False
            parent_path = self._annotations[0].parent_path
            assert(parent_path is not None)
            parent_path = str(parent_path)
            parent_path_new = parent_path
            if not self._annotations[0].source.is_external and parent_path in modified_paths \
                    and not stage.GetPrimAtPath(parent_path).IsValid():
                if len(modified_paths) == 2:
                    if modified_paths[0] == parent_path \
                            and stage.GetPrimAtPath(modified_paths[1]).IsValid():
                        parent_path_new = modified_paths[1]
                        is_parent_renamed = True
                    elif modified_paths[1] == parent_path \
                            and stage.GetPrimAtPath(modified_paths[0]).IsValid():
                        parent_path_new = modified_paths[0]
                        is_parent_renamed = True
            if is_parent_renamed:
                for annotation in self._annotations:
                    source = annotation.source
                    source.source_path_in_stage =\
                        str(Sdf.Path(source.source_path_in_stage).ReplacePrefix(parent_path, parent_path_new))
                return

        def remove_if_exists(a_list, item):
            return [x for x in a_list if x is not item]

        # Prim structural changes
        annotations_to_remove = []
        potential_new_prims = []
        for path in modified_paths:
            if path.IsPrimPath() and stage.GetPrimAtPath(path).IsValid():
                potential_new_prims.append(path)
        value_changed = False
        for annotation in self._annotations:
            source = annotation.source
            if source is not None and not source.is_external and source.exists_in_source_stage:
                prim = stage.GetPrimAtPath(source.source_path_in_stage)
                if not prim.IsValid():
                    # We can detect rename/move only when paths contain the old and the new paths, nothing else
                    is_rename = False
                    rename_from = source.source_path_in_stage
                    if len(modified_paths) == 2:
                        if modified_paths[0] == source.source_path_in_stage \
                                and stage.GetPrimAtPath(modified_paths[1]).IsValid():
                            source.set_source_path_in_stage(str(modified_paths[1]))
                            is_rename = True
                            potential_new_prims = remove_if_exists(potential_new_prims, modified_paths[1])
                        elif modified_paths[1] == source.source_path_in_stage \
                                and stage.GetPrimAtPath(modified_paths[0]).IsValid():
                            source.set_source_path_in_stage(str(modified_paths[0]))
                            is_rename = True
                            potential_new_prims = remove_if_exists(potential_new_prims, modified_paths[0])
                    if is_rename:
                        rename_to = source.source_path_in_stage
                        if str(Sdf.Path(rename_from).GetParentPath()) == str(Sdf.Path(rename_to).GetParentPath()):
                            #  renamed the prim, but it stayed under the same SkelAnim
                            continue  # source path is already refresehd, no further action needed.
                        else:
                            pass  # don't care
                    # It's a deletion from this annotation prim's perspective.
                    value_changed = True
                    annotations_to_remove.append(annotation)
                    source.set_removed()
                    potential_new_prims = remove_if_exists(potential_new_prims, prim.GetPath())

        self._value_changed_signal_enabled = False
        from .utils import extract_annotation, get_annotation_property_names
        for new_prim_path in potential_new_prims:
            prim = stage.GetPrimAtPath(new_prim_path)
            if new_prim_path.IsPrimPath() and parent_path is not None and\
                    str(new_prim_path.GetParentPath()) == parent_path and prim.IsValid():
                # TODO: do we need to check if we already have that annotation?
                annotation = extract_annotation(prim)
                # Prim does not have an annotation yet, create a dummy annotation
                # We need to support this case to make annotation prim work.
                if annotation is None:
                    source = SourceModel()
                    source.set_source_path_in_stage(str(new_prim_path))
                    # TODO: this work only in the main stage, add external file support if needed
                    source.set_source_url(None, True)
                    annotation = Annotation('New annotation', 0, 0, source)
                self.add_annotation(annotation)
                value_changed = True

        # Property changes
        # We handle it here and not in the Annotation so that Annotation does not need to store the stage
        for resync_path in objects.GetChangedInfoOnlyPaths():
            if resync_path.IsPropertyPath():
                prim_path = resync_path.GetPrimPath()
                prim = stage.GetPrimAtPath(prim_path)
                attribute_name = str(resync_path).split('.')[-1]
                if attribute_name not in get_annotation_property_names():
                    continue
                if prim.IsValid():
                    for annotation in self._annotations:
                        source = annotation.source
                        if source is not None and source.exists_in_source_stage \
                                and source.source_path_in_stage == prim_path:
                            changed_annotation = extract_annotation(prim)
                            if changed_annotation is None:
                                continue
                            annotation.set_values_without_usd_sync(
                                changed_annotation.tag,
                                changed_annotation.start,
                                changed_annotation.end
                            )
                            value_changed = True

        for annotation in annotations_to_remove:
            self.remove_annotation(annotation)

        self._value_changed_signal_enabled = True
        if value_changed:
            self._sort_annotations()
            self._dirty_tracks = True
            asyncio.ensure_future(self._value_changed_async())

    async def _value_changed_async(self):
        await omni.kit.app.get_app().next_update_async()
        self._value_changed()

    def _sort_annotations(self):
        self._annotations.sort(key=lambda annotation: annotation.start)

    def destroy(self):
        self._annotations = []
        self._tracks = {}
        self._dirty_tracks = False
        self._value_changed_signal_enabled = True
        if self._usd_listener:
            self._usd_listener.Revoke()
        self._usd_listener = None
