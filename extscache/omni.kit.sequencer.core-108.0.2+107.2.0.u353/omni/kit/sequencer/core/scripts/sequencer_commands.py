import math
from typing import List, Optional

import carb
import omni.kit.commands
import omni.kit.sequencer.usd as usd_sequencer
import omni.usd
from omni.usd.commands import CreateReferenceCommand, DeletePrimsCommand
from pxr import Sdf, Tf, Usd, UsdGeom
import SequenceSchema

from . import sequencer_settings
from .sequencer_track_types import TrackTypes

# ---------------- Track commands --------------------------------------------
DEFAULT_CLIP_LENGTH = 180


def _set_clip_time(clip: SequenceSchema.ClipBase, clip_start: Sdf.TimeCode, clip_end: Sdf.TimeCode):
    clip.GetStartTimeAttr().Set(clip_start)
    clip.GetEndTimeAttr().Set(clip_end)


class SequencerCreateReferenceCommand(omni.kit.commands.Command):
    """
    Wraps the usd command for create reference - returns the referenced prim path.
    """

    def __init__(self, path_to: Sdf.Path, asset_path: str):
        """
        Args:
            path_to (Sdf.Path): Path to create a new prim.
            asset_path (str): Path to the asset.
        """
        super().__init__()
        self._path_to = path_to
        self._asset_path = asset_path
        self._create_ref_cmd = None

    def do(self):
        stage = omni.usd.get_context().get_stage()
        self._path_to = Sdf.Path(omni.usd.get_stage_next_free_path(stage, self._path_to.pathString, False))
        self._create_ref_cmd = CreateReferenceCommand(
            omni.usd.get_context(), path_to=self._path_to, asset_path=self._asset_path
        )
        self._create_ref_cmd.do()
        return self._path_to

    def undo(self):
        if self._create_ref_cmd:
            self._create_ref_cmd.undo()


class SequencerCreatePrimCommandBase(omni.kit.commands.Command):
    """
    Base class to create a prim (and remove when undo)
    Ensures unique name, and handles selection.
    """

    def __init__(
        self, path_to: Sdf.Path, context_name: Optional[str] = "", prepend_default_prim: Optional[bool] = True
    ):
        """
        Args:
            path_to (Sdf.Path): Path to create a new prim.
            prepend_default_prim (bool): Whether or not to prepend default prim path.
            context_name (str): UsdContext name for this command to run on.
        """
        super().__init__()
        self._context_name = context_name
        self._context = omni.usd.get_context(self._context_name)
        self._selection = self._context.get_selection()
        self._previous_selection = None
        stage = self._context.get_stage()
        self._path_to: Sdf.Path = Sdf.Path(omni.usd.get_stage_next_free_path(stage, str(path_to), prepend_default_prim))

    def do(self):
        # Save the selection and select the new prim.
        self._previous_selection = self._selection.get_selected_prim_paths()
        self._selection.set_selected_prim_paths([str(self._path_to)], False)

    @staticmethod
    def _is_tmp_skel_anim(prim):
        return prim.GetTypeName() in ["SkelAnimation", "AnimationData"] and prim.GetName().startswith("__sequence__")

    def undo(self):
        carb.log_info(f"Undo creation of: {self._path_to}")
        if self._path_to:
            stage = self._context.get_stage()
            prim = stage.GetPrimAtPath(self._path_to)
            if prim:
                children = prim.GetChildren()
                if any(children):
                    if not all(map(self._is_tmp_skel_anim, children)):
                        carb.log_warn(f"{self._path_to} has unexpected children: {children}")

                DeletePrimsCommand([self._path_to]).do()

        # Restore selection
        if self._previous_selection is not None:
            self._selection.set_selected_prim_paths(self._previous_selection, False)


class SequencerCreateSequenceCommand(SequencerCreatePrimCommandBase):
    """
    Creates a new Sequencer prim.
    Returns SequenceSchema.Sequence.
    """

    def __init__(self, path_to: Optional[Sdf.Path] = Sdf.Path("/Sequence")):
        """
        Args:
            path_to (Sdf.Path): Path to create a new prim.
        """
        super().__init__(path_to)

    def do(self):
        stage = self._context.get_stage()
        sequence = SequenceSchema.Sequence.Define(stage, self._path_to)
        if not sequence:
            carb.log_error("Sequence failed to create.")
        self._path_to = sequence.GetPrim().GetPath()
        super().do()
        return sequence

    def undo(self):
        # copy prim command will undo
        super().undo()


class SequencerTrackCreateCommand(SequencerCreatePrimCommandBase):
    """
    Creates a new Sequencer Track prim.
    Returns SequenceSchema.Track
    """

    def __init__(self, sequence_path: Sdf.Path, track_type: str, track_name: Optional[str] = "", location: int = -1):
        """
        Args:
            sequence_path (Sdf.Path): Parent Sequence prim.
            track_type (str): Type of track
            track_name (str, optional): Track name. If not specified, it will named track_type.
            location (int, optional): Child location in hierarchy.
        """

        # Track name is optional - use track type as predicate.
        self._track_type = track_type
        self._track_name: str = track_name or track_type or "Track"
        self._track_location = location

        if not self._track_type:
            raise ValueError("SequencerTrackCreateCommand: Track type not specified.")
        if self._track_type not in TrackTypes.values():
            raise ValueError(f"SequencerTrackCreateCommand: Invalid track type: {self._track_type}.")

        self._sequence_path = sequence_path
        _path_to = sequence_path.AppendElementString(Tf.MakeValidIdentifier(self._track_name))
        super().__init__(_path_to)

    @staticmethod
    def define_track(stage: Usd.Stage, path_to: Sdf.Path, name: str, type: str):
        track = SequenceSchema.Track.Define(stage, path_to)
        if not track:
            carb.log_error(f"Track creation failed: {path_to}:{track}")
            return None

        track.CreateLabelAttr().Set(name)
        track.CreateTrackTypeAttr().Set(type)
        return track

    def do(self):
        self._usd_context = omni.usd.get_context()
        stage = self._usd_context.get_stage()

        # get sequence
        sequence_prim: Usd.Prim = stage.GetPrimAtPath(self._sequence_path)
        if not sequence_prim or not sequence_prim.IsA(SequenceSchema.Sequence):
            raise ValueError(f"Specified sequence path is not valid: {self._sequence_path}")

        previous_children_order = [child.GetName() for child in sequence_prim.GetChildren()]

        track = self.define_track(stage, self._path_to, self._path_to.name, self._track_type)
        self._path_to = track.GetPrim().GetPath()
        if not track:
            carb.log_error("SequencerTrackCreateCommand: Track creation failed.")
            return

        new_children_order = previous_children_order.copy()
        if self._track_location < 0:
            new_children_order.append(self._path_to.name)
        else:
            new_children_order.insert(self._track_location, self._path_to.name)

        SequencerSetNameChildrenOrder(self._sequence_path, new_children_order, previous_children_order).do()

        super().do()
        return track

    def undo(self):
        super().undo()


class SequencerSetNameChildrenOrder(omni.kit.commands.Command):
    """Sets the children order of a prim by name."""

    def __init__(self, parent_path: str, children_order: List[str], previous_order: Optional[List[str]] = None):
        """
        Args:
            parent_path (str): Parent prim path.
            children_order (List[str]): List of children names to set.
            previous_order (List[str]): Optional list for the previous order.
        """
        super().__init__()
        self._parent_path = Sdf.Path(parent_path)
        self._new_order = children_order
        self._previous_order = previous_order
        self._edit_target = []

    @staticmethod
    def set_children_order(stage: Usd.Stage, edit_layer: Sdf.Layer, parent_path: Sdf.Path, children_order: List[str]):
        edit_target: Usd.EditTarget = stage.GetEditTargetForLocalLayer(edit_layer)
        with Usd.EditContext(stage, edit_target):
            sdf_parent_prim: Sdf.PrimSpec = edit_layer.GetPrimAtPath(parent_path)
            sdf_parent_prim.nameChildrenOrder = children_order

    def do(self):
        stage: Usd.Stage = omni.usd.get_context().get_stage()
        edit_target: Usd.EditTarget = stage.GetEditTarget()
        edit_layer: Sdf.Layer = edit_target.GetLayer()
        if not self._previous_order:
            sdf_parent_prim: Sdf.PrimSpec = edit_layer.GetPrimAtPath(self._parent_path)
            self._previous_order = sdf_parent_prim.nameChildrenOrder

        self.set_children_order(stage, edit_layer, self._parent_path, self._new_order)

    def undo(self):
        stage: Usd.Stage = omni.usd.get_context().get_stage()
        edit_target: Usd.EditTarget = stage.GetEditTarget()
        edit_layer: Sdf.Layer = edit_target.GetLayer()
        self.set_children_order(stage, edit_layer, self._parent_path, self._previous_order)


class SequencerSetChildLocation(omni.kit.commands.Command):
    """
    Set prim child location.
    """

    def __init__(self, parent_path: str, child_path: str, to_location: int = -1, from_location: int = None):
        """
        Args:
            parent_path (str): Parent prim path.
            child_path (str): Child prim path.
            to_location (int, optional): Location to set child to. Defaults to -1.
            from_location (int, optional): Previous location for undo. Defaults to None.
        """
        super().__init__()
        self._parent_path = parent_path
        self._child_path = child_path
        self._to_location = to_location
        self._from_location = from_location
        self._moved = False

    def set_child_prim_location(self, parent_prim: Usd.Prim, child_name: str, location: int):
        children = parent_prim.GetChildren()
        children_order: List[str] = [child.GetName() for child in children]
        try:
            index = children_order.index(child_name)
        except ValueError:
            carb.log_error(f"{child_name} not child of {parent_prim}.")
            return False

        if index == location:
            # Already in this location
            return False

        # store off old location
        if not self._from_location:
            self._from_location = index

        if location < 0:
            children_order.pop(index)
            children_order.append(child_name)
        else:
            if index < location:
                location = location - 1
            children_order.insert(location, children_order.pop(index))

        stage = omni.usd.get_context().get_stage()
        edit_target = stage.GetEditTarget()
        edit_layer = edit_target.GetLayer()
        new_target = stage.GetEditTargetForLocalLayer(edit_layer)
        with Usd.EditContext(stage, new_target):
            sdf_parent_prim = edit_layer.GetPrimAtPath(parent_prim.GetPath())
            sdf_parent_prim.nameChildrenOrder = children_order

        return True

    def do(self):
        self._do(self._to_location)

    def _do(self, to_location: int):
        stage = omni.usd.get_context().get_stage()
        parent_path = Sdf.Path(self._parent_path)
        child_path = Sdf.Path(self._child_path)
        if not child_path.GetParentPath().pathString == parent_path.pathString:
            carb.log_error(f"{child_path} is not child of {parent_path}")
            return

        parent_prim = stage.GetPrimAtPath(parent_path)
        if parent_prim:
            self._moved = self.set_child_prim_location(parent_prim, child_path.name, to_location)
        else:
            carb.log_error(f"No prim at path: {self._parent_path}")
            return

    def undo(self):
        if not self._moved:
            return
        self._do(self._from_location)


class SequencerTrackMoveCommand(omni.kit.commands.Command):
    """
    Move track position in Sequencer up or down.
    """

    def __init__(self, track_path: str, move_vector: int = 0):
        """
        Args:
            track_path (str): Path to the sequencer track prim.
            move_vector (int, optional): Move up (1) or down (-1). Defaults to 0.
        """
        super().__init__()
        self._track_path = track_path
        self._move_vector = move_vector
        self._moved = 0

    # -------------------- Track functions
    @staticmethod
    def move_track_by_number(track: SequenceSchema.Track, move_vector: int):
        prim = track.GetPrim()
        num_moved = move_vector
        sequence = prim.GetParent()
        if sequence.IsA(SequenceSchema.Sequence):
            stage = omni.usd.get_context().get_stage()
            parent_prim = sequence.GetPrim()
            edit_target = stage.GetEditTarget()
            edit_layer = edit_target.GetLayer()
            new_target = stage.GetEditTargetForLocalLayer(edit_layer)
            with Usd.EditContext(stage, new_target):
                children = parent_prim.GetChildren()
                name = prim.GetName()
                xchildren = []
                for px in children:
                    xchildren.append(px.GetName())
                index = xchildren.index(name)
                item = xchildren.pop(index)
                new_index = index + move_vector
                if new_index < 0:
                    num_moved = move_vector - new_index
                    new_index = 0
                if new_index > len(xchildren):
                    num_moved = new_index - len(xchildren)
                    new_index = len(xchildren)

                xchildren.insert(new_index, item)
                sdf_parent_prim = edit_layer.GetPrimAtPath(parent_prim.GetPath())
                sdf_parent_prim.nameChildrenOrder = xchildren
        return num_moved

    def do(self):
        stage = omni.usd.get_context().get_stage()
        track = usd_sequencer.get_track_from_path(stage, self._track_path)
        if track:
            self._moved = self.move_track_by_number(track, self._move_vector)
        else:
            carb.log_error(f"No track at path: {self._track_path}")
            return

    def undo(self):
        stage = omni.usd.get_context().get_stage()
        track = usd_sequencer.get_track_from_path(stage, self._track_path)
        if track:
            self.move_track_by_number(track, -self._moved)


class SequencerTrackVisibleSetCommand(omni.kit.commands.Command):
    """Set visibility of a Track."""

    def __init__(self, track_path: Sdf.Path = None, is_visible=True):
        """
        Args:
            track_path (Sdf.Path, optional): Track prim path. Defaults to None.
            is_visible (bool, optional): Visibility value. Defaults to True.
        """
        super().__init__()
        self._track_path = track_path
        self._is_visible = is_visible
        self._stage = omni.usd.get_context().get_stage()

    def _set_visibility(self, visibile):
        prim = self._stage.GetPrimAtPath(self._track_path)
        imageable = UsdGeom.Imageable(prim)
        visibility_attr: Usd.Attribute = imageable.GetVisibilityAttr()
        if visibile:
            visibility_attr.Set(UsdGeom.Tokens.inherited)
        else:
            visibility_attr.Set(UsdGeom.Tokens.invisible)

    def do(self):
        self._set_visibility(self._is_visible)

    def undo(self):
        self._set_visibility(not self._is_visible)


class SequencerSetTargetCommand(omni.kit.commands.Command):
    """Set the prim target of a prim relationship."""

    def __init__(self, prim_path: str, target_prim: str, relationship_name: str):
        """
        Args:
            prim_path (str): Prim path with the relationship.
            target_prim (str): Desired target prim path.
            relationship_name (str): Name of the relationship.
        """
        super().__init__()
        self._prim_path = prim_path
        self._target_prim = target_prim
        self._relationship_name = relationship_name
        self._prev_targets = None

    def do(self):
        stage = omni.usd.get_context().get_stage()
        prim = stage.GetPrimAtPath(self._prim_path)
        if not prim:
            carb.log_error(f"Prim not found at path {self._prim_path}")
            return
        if self._target_prim and not Sdf.Path.IsValidPathString(self._target_prim):
            carb.log_error(f"Invalid target path {self._target_prim}")
            return

        target_rel = prim.GetRelationship(self._relationship_name)
        if target_rel is None:
            res, _ = omni.kit.commands.execute(
                "AddRelationshipTargetCommand", relationship=target_rel.GetPath(), target=self._target_prim
            )
            if not res:
                carb.log_error(f"Failed to add relationship {self._prim_path}")
                return

        self._prev_targets = target_rel.GetTargets()
        if not self._target_prim:
            target_rel.ClearTargets(True)
        else:
            target_rel.SetTargets([self._target_prim])

    def undo(self):
        stage = omni.usd.get_context().get_stage()
        prim = stage.GetPrimAtPath(self._prim_path)
        target_rel = prim.GetRelationship(self._relationship_name)
        if not target_rel:
            carb.log_error(f"Failed to undo, '{self._relationship_name}' relationship not found at: {self._prim_path}")
            return

        if not self._prev_targets:
            target_rel.ClearTargets(True)
        else:
            target_rel.SetTargets(self._prev_targets)


# ---------------- Clip commands ---------------------------------------------


class SequencerClipCreateCommand(SequencerCreatePrimCommandBase):
    """Create a clip on a track."""

    def __init__(
        self,
        track_path: str,
        clip_name: str = "",
        prim_path: str = "",
        clip_start: float = 0,
        clip_end: float = None,
        select_prim=False,
    ):
        """
        Args:
            track_path (str): Track prim path.
            clip_name (str, optional): Clip name, if not specified "Clip" is used. Defaults to "".
            prim_path (str, optional): Clip target prim path. Defaults to "".
            clip_start (float, optional): Start time (in timecodes) of the clip. Defaults to 0.
            clip_end (float, optional): End time (in timecodes) of the clip. Defaults to None.
            select_prim (bool, optional): If true, select the prim upon creation. Defaults to False.
        """
        self._track_path = track_path
        self._prim_path = prim_path
        self._clip_name = clip_name
        self._clip_start = clip_start
        self._clip_end = clip_end
        self._select_prim = select_prim  # unused
        self._path_to = Sdf.Path(track_path).AppendElementString(self._clip_name or "Clip")
        super().__init__(self._path_to)

    # ------------------- Clip functions
    @staticmethod
    def generate_clip_name(
        clip_schema: SequenceSchema.ClipBase, asset_prim_path: str = None, anim_prim_path: str = None
    ):
        """Consolidated method to generate clip name."""
        predicate = "Clip"
        if clip_schema == SequenceSchema.ShotClip:
            predicate = "Shot"
        clip_name = f"{predicate}"
        if anim_prim_path:
            clip_name = f"{Sdf.Path(anim_prim_path).name}_{predicate}"
        elif asset_prim_path:
            clip_name = f"{Sdf.Path(asset_prim_path).name}_{predicate}"
        return clip_name

    @staticmethod
    def add_clip(track_path: str, clip_name: str, prim_path: str, clip_start: float, clip_end: float = None):
        """Instantiate a clip on track_path"""
        stage = omni.usd.get_context().get_stage()
        track = usd_sequencer.get_track_from_path(stage, track_path)
        if not track:
            carb.log_warn(f"Track not found: {track_path}")
            return None

        track_type = track.GetTrackTypeAttr().Get()
        clip_schema = SequenceSchema.AssetClip
        if track_type == TrackTypes.SHOT:
            clip_schema = SequenceSchema.ShotClip

        if not clip_name:
            clip_name = SequencerClipCreateCommand.generate_clip_name(clip_schema, asset_prim_path=prim_path)

        prim_name = Tf.MakeValidIdentifier(clip_name)
        clip_path = track.GetPath().AppendElementString(prim_name)
        clip_path = omni.usd.get_stage_next_free_path(stage, clip_path.pathString, False)
        clip = clip_schema.Define(stage, clip_path)

        if prim_path:
            clip.CreateAssetPrimRel().SetTargets([prim_path])
        else:
            # Initialize the asset prim target from the track target
            track_targets = usd_sequencer.get_target_prim_from_track(track)
            if track_targets:
                clip.CreateAssetPrimRel().SetTargets(track_targets)

        clip.GetStartTimeAttr().Set(Sdf.TimeCode(clip_start))
        if clip_end is None:
            length = usd_sequencer.calculate_clip_length(clip, 0)
            if length == 0:
                length = DEFAULT_CLIP_LENGTH
            clip_end = clip_start + length
        clip.GetEndTimeAttr().Set(Sdf.TimeCode(clip_end))

        return clip

    def do(self):
        clip = self.add_clip(self._track_path, self._clip_name, self._prim_path, self._clip_start, self._clip_end)
        self._path_to = clip.GetPrim().GetPath()
        super().do()
        return clip


class SequencerClipSplitCommand(omni.kit.commands.Command):
    """Command to split clips at specified time."""

    def __init__(self, clip_paths: List[str], split_at_time: float):
        """
        Args:
            clip_paths (List[str]): Clip paths to split.
            split_at_time (float): Time (in timecodes) at which to split.
        """
        super().__init__()
        self._clip_paths = clip_paths
        self._split_at_time = split_at_time

    def do(self):
        new_clips = []
        _context = omni.usd.get_context()
        _stage = _context.get_stage()
        _selection = _context.get_selection()
        _selection_before = _selection.get_selected_prim_paths()
        for clip_path in self._clip_paths:
            clip = usd_sequencer.get_asset_clip_from_path(_stage, clip_path)
            if not clip:
                carb.log_warn(f"Path is not a clip: {clip_path}")
                continue
            clip_start = clip.GetStartTimeAttr().Get()
            clip_end = clip.GetEndTimeAttr().Get()

            # Make sure that clip play start/end is set
            play_start = clip.GetPlayStartAttr().Get().GetValue()
            play_end = clip.GetPlayEndAttr().Get().GetValue()
            if math.isnan(play_start) or math.isnan(play_end):
                anim_source = usd_sequencer.get_clip_anim_source_prim(clip)
                if anim_source:
                    available_start, available_end = usd_sequencer.get_prim_available_range(anim_source)
                    omni.kit.commands.execute(
                        "SequencerClipUpdateTrimCommand",
                        clip_id=clip_path,
                        play_start=available_start,
                        play_end=available_end,
                    )

            # check that the split time is in the clip range
            if clip_start >= self._split_at_time or clip_end <= self._split_at_time:
                # split time is outside clip range
                carb.log_warn(f"Split time is outside range of clip: {clip}")
                continue

            source_time = usd_sequencer.get_clip_source_time_from_parent_time(clip, self._split_at_time)
            # duplicate original - undoable
            res, new_clip = omni.kit.commands.execute(
                "SequencerClipDuplicateCommand", clip_id=clip_path, inherit_translation=True
            )
            # Clip the original - undoable
            res, _ = omni.kit.commands.execute(
                "SequencerClipUpdateTimeCommand",
                clip_id=clip_path,
                clip_start=float(clip_start),
                clip_end=float(self._split_at_time),
            )

            # Clip the duplicate
            _set_clip_time(new_clip, Sdf.TimeCode(self._split_at_time), clip_end)
            # Offset the new clip
            new_asset_clip = SequenceSchema.AssetClipBase(new_clip.GetPrim())
            new_asset_clip.GetPlayOffsetAttr().Set(source_time.time)
            new_clips.append(new_asset_clip)
        if new_clips:
            new_selection_paths = [new_clip.GetPrim().GetPath().pathString for new_clip in new_clips]
            res, _ = omni.kit.commands.execute(
                "SelectPrimsCommand",
                old_selected_paths=_selection_before,
                new_selected_paths=new_selection_paths,
                expand_in_stage=False,
            )
        return new_clips

    def undo(self):
        pass


class SequencerClipDuplicateCommand(omni.kit.commands.Command):
    """Command to duplicate a Sequence clip."""

    def __init__(self, clip_id: str, inherit_translation: bool = False):
        """

        Args:
            clip_id (str): Clip path to duplicate.
            inherit_translation (bool, optional): Whether or not the duplicated clip should inherit the position (in time) of the original clip. Defaults to False.
        """
        super().__init__()
        self._clip_id = clip_id
        self._new_clip_id = None
        self._inherit_translation = inherit_translation
        self._selection = omni.usd.get_context().get_selection()
        self._previously_selected_paths = None

    @staticmethod
    def duplicate_clip(clip_id, inherit_translation=False):
        # First, get the existing clip
        stage = omni.usd.get_context().get_stage()
        clip = SequenceSchema.ClipBase.Get(stage, clip_id)
        if not clip:
            carb.log_warn("Clip ({}) not found for duplicating.".format(clip_id))
            return

        old_prim_path = clip.GetPath().pathString
        new_prim_path = omni.usd.get_stage_next_free_path(stage, old_prim_path, False)
        omni.kit.commands.execute("CopyPrimCommand", path_from=old_prim_path, path_to=new_prim_path)
        new_prim = stage.GetPrimAtPath(new_prim_path)
        new_clip = SequenceSchema.ClipBase(new_prim)
        if not inherit_translation:
            # we start at the end
            start_time = clip.GetStartTimeAttr().Get()
            end_time = clip.GetEndTimeAttr().Get()
            length = end_time - start_time

            new_start = end_time
            new_end = new_start + length
            _set_clip_time(new_clip, new_start, new_end)
        return new_clip

    def do(self):
        self._previously_selected_paths = self._selection.get_selected_prim_paths()
        new_clip = self.duplicate_clip(self._clip_id)
        if new_clip:
            self._new_clip_id = new_clip.GetPrim().GetPath().pathString
        else:
            carb.log_error(f"No clip created when duplicating: {self._clip_id}")
        return new_clip

    def undo(self):
        if not self._new_clip_id:
            return
        stage = omni.usd.get_context().get_stage()
        stage.RemovePrim(self._new_clip_id)

        if self._previously_selected_paths:
            self._selection.set_selected_prim_paths(self._previously_selected_paths, False)


class SequencerClipUpdateTimeCommand(omni.kit.commands.Command):
    """Commmand to set clip start/end times."""

    def __init__(
        self,
        clip_id: Sdf.Path,
        clip_start: float,
        clip_end: float,
        old_clip_start: float = None,
        old_clip_end: float = None,
    ):
        """
        Args:
            clip_id (Sdf.Path): Clip path.
            clip_start (float): New start time in timecodes.
            clip_end (float): New end time in timecodes.
            old_clip_start (float, optional): Old clip start time in timecodes (for undo). Defaults to None.
            old_clip_end (float, optional): Old clip end time in timecodes (for undo). Defaults to None.
        """
        super().__init__()
        self._clip_id = clip_id
        self._clip_start = clip_start
        self._clip_end = clip_end
        self._old_start = old_clip_start
        self._old_end = old_clip_end

    def do(self):
        stage = omni.usd.get_context().get_stage()
        clip = SequenceSchema.ClipBase.Get(stage, self._clip_id)
        if self._old_start is None:
            self._old_start = clip.GetStartTimeAttr().Get().GetValue()
        if self._old_end is None:
            self._old_end = clip.GetEndTimeAttr().Get().GetValue()
        _set_clip_time(clip, Sdf.TimeCode(self._clip_start), Sdf.TimeCode(self._clip_end))

    def undo(self):
        stage = omni.usd.get_context().get_stage()
        clip = SequenceSchema.ClipBase.Get(stage, self._clip_id)
        if clip:
            _set_clip_time(clip, Sdf.TimeCode(self._old_start), Sdf.TimeCode(self._old_end))


class SequencerClipUpdateTrimCommand(omni.kit.commands.Command):
    """Command to set play start/end times."""

    def __init__(
        self, clip_id: str, play_start: float, play_end: float, old_play_start: float = None, old_play_end: float = None
    ):
        """
        Args:
            clip_id (str): Clip prim path.
            play_start (float): New clip Play Start time in timecodes.
            play_end (float): New clip Play End time in timecodes.
            old_play_start (float, optional): Old play start time in timecodes for undo. Defaults to None.
            old_play_end (float, optional): Old play end time in timecodes for undo. Defaults to None.
        """
        super().__init__()
        self._clip_id = clip_id
        self._play_start = play_start
        self._play_end = play_end
        self._old_play_start = old_play_start
        self._old_play_end = old_play_end

    @staticmethod
    def update_clip_trim(clip: SequenceSchema.ClipBase, play_start: float, play_end: float):
        if not math.isnan(play_start):
            play_start = Sdf.TimeCode(play_start)
        if not math.isnan(play_end):
            play_end = Sdf.TimeCode(play_end)

        clip.GetPlayStartAttr().Set(play_start)
        clip.GetPlayEndAttr().Set(play_end)

    def do(self):
        stage = omni.usd.get_context().get_stage()
        clip = SequenceSchema.AssetClipBase.Get(stage, self._clip_id)
        if self._old_play_start is None:
            self._old_play_start = clip.GetPlayStartAttr().Get().GetValue()
        if self._old_play_end is None:
            self._old_play_end = clip.GetPlayEndAttr().Get().GetValue()
        self.update_clip_trim(clip, self._play_start, self._play_end)

    def undo(self):
        stage = omni.usd.get_context().get_stage()
        clip = SequenceSchema.AssetClipBase.Get(stage, self._clip_id)
        if clip:
            self.update_clip_trim(clip, self._old_play_start, self._old_play_end)


class SequencerClipSetTargetCommand(omni.kit.commands.Command):
    """Set Clip target prim."""

    def __init__(self, clip_path: Sdf.Path, asset_prim_path: Sdf.Path, update_time: bool = False):
        """
        Args:
            clip_path (Sdf.Path): Clip prim path.
            asset_prim_path (Sdf.Path): Asset prim path to target.
            update_time (bool, optional): Update clip time to match that of target. Defaults to False.
        """
        super().__init__()
        self._clip_path = clip_path
        self._asset_prim_path = asset_prim_path
        self._old_clip_targets = None
        self._update_time = update_time

    def do(self):
        stage = omni.usd.get_context().get_stage()
        clip_prim = stage.GetPrimAtPath(self._clip_path)
        if not clip_prim:
            carb.log_error(f"Clip path not valid: {self._clip_path}.")
            return
        if not clip_prim.IsA(SequenceSchema.AssetClipBase):
            carb.log_error(f"Clip not AssetClip: {self._clip_path}.")
            return
        if self._asset_prim_path is not None:
            target_prim = stage.GetPrimAtPath(self._asset_prim_path)
            if not target_prim:
                carb.log_error(f"Target Asset Prim path not valid: {self._asset_prim_path}.")
                return

        clip = usd_sequencer.get_clip_from_path(stage, self._clip_path)
        self._old_clip_targets = usd_sequencer.get_clip_targets(clip)
        if self._asset_prim_path:
            usd_sequencer.set_clip_targets(clip, [self._asset_prim_path])
        else:
            usd_sequencer.set_clip_targets(clip, None)

        if self._update_time:
            self.update_clip_time(clip)

    def update_clip_time(self, clip):
        anim_source = usd_sequencer.get_clip_anim_source_prim(clip)
        if not anim_source:
            anim_source = self._asset_prim_path
        if not anim_source:
            return
        available_range = usd_sequencer.get_prim_available_range(anim_source)

        if available_range:
            play_start, play_end = available_range
            if play_end - play_start:
                SequencerClipUpdateTrimCommand(self._clip_path, play_start, play_end).do()
                return

        SequencerClipUpdateTrimCommand(self._clip_path, math.nan, math.nan).do()

    def undo(self):
        stage = omni.usd.get_context().get_stage()
        clip = usd_sequencer.get_clip_from_path(stage, self._clip_path)
        if clip:
            usd_sequencer.set_clip_targets(clip, self._old_clip_targets)


class SequencerClipSetAnimationCommand(omni.kit.commands.Command):
    """Set clip animation source to prim"""

    def __init__(self, clip_path: Sdf.Path, anim_prim_path: Sdf.Path, update_clip_time: bool = True):
        """
        Args:
            clip_path (Sdf.Path): Clip prim path.
            anim_prim_path (Sdf.Path): Animation source prim path.
            update_clip_time (bool, optional): Option to update clip time to match that of the target prim. Defaults to True.
        """
        super().__init__()
        self._clip_path = clip_path
        self._anim_prim_path = anim_prim_path
        self._update_clip_time = update_clip_time
        self._old_clip_animations = None

    def do(self):
        context = omni.usd.get_context()
        stage = context.get_stage()

        clip_prim = stage.GetPrimAtPath(self._clip_path)
        if not clip_prim:
            carb.log_error(f"Clip path not valid: {self._clip_path}.")
            return
        if not clip_prim.IsA(SequenceSchema.AssetClipBase):
            carb.log_error(f"Clip not AssetClip: {self._clip_path}.")
            return

        if self._anim_prim_path is not None:
            anim_prim = stage.GetPrimAtPath(self._anim_prim_path)
            if not anim_prim:
                carb.log_error(f"Anim Prim path not valid: {self._anim_prim_path}.")
                return

        clip = SequenceSchema.AssetClipBase(clip_prim)
        self._old_clip_animations = usd_sequencer.get_clip_animations(clip)
        targets = [self._anim_prim_path] if self._anim_prim_path else None
        usd_sequencer.set_clip_animations(clip, targets)

        # update clip length
        if self._update_clip_time:
            start_time = clip.GetStartTimeAttr().Get().GetValue()
            length = usd_sequencer.get_clip_available_length(clip)
            if length == 0:
                length = DEFAULT_CLIP_LENGTH
            end_time = start_time + length
            omni.kit.commands.execute(
                "SequencerClipUpdateTimeCommand", clip_id=self._clip_path, clip_start=start_time, clip_end=end_time
            )

        clip_source_length = usd_sequencer.get_clip_source_length(clip)
        if not clip_source_length:
            available_range = usd_sequencer.get_clip_available_range(clip)
            if available_range:
                play_start, play_end = available_range
                omni.kit.commands.execute(
                    "SequencerClipUpdateTrimCommand", clip_id=self._clip_path, play_start=play_start, play_end=play_end
                )
            else:
                carb.log_warn(f"Clip available range is not defined: {clip}")

    def undo(self):
        stage = omni.usd.get_context().get_stage()
        clip = usd_sequencer.get_clip_from_path(stage, self._clip_path)
        if clip:
            usd_sequencer.set_clip_animations(clip, self._old_clip_animations)


class SequencerSettingsSetSnapToFrameCommand(omni.kit.commands.Command):
    """Command to set Snap to Frame option.
    Args:
        on (bool, optional): Snap To Frame value. Defaults to True.
    """

    def __init__(self, on=True):
        super().__init__()
        self._snap_to_frame = on

    def do(self):
        self._previous_setting = sequencer_settings.snap_to_frame
        sequencer_settings.snap_to_frame = self._snap_to_frame
        return

    def undo(self):
        sequencer_settings.snap_to_frame = self._previous_setting
        pass
