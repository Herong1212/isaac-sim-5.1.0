# Copyright (c) 2021-2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

import carb
import omni.ext
import omni.kit.app
import omni.kit.commands
import omni.kit.context_menu
import omni.anim.skelJoint


import carb
import omni.kit.commands
import omni.timeline
import omni.usd
import os
from typing import List, Optional, Tuple, Union
from omni.usd.commands import CreatePrimCommand, DeletePrimsCommand
from pxr import Sdf, UsdSkel
from .annotation.annotation_model import Annotation
from .model.source_model import SourceModel
from omni.kit.usd_undo import UsdLayerUndo


DEFAULT_ANNOTATION_TAG = "New annotation"


__all__ = [
    "AnimationPreviewCommand",
    "AnimationPreviewAddAnnotationCommand",
    "AnimationPreviewAddAnnotationsCommand",
    "AnimationPreviewRemoveAnnotationsCommand",
    "SetupPickupAnnotationCommand",
]


class AnimationPreviewCommand(omni.kit.commands.Command):
    """
    Sends a specified prim to the Preview window.  The prim can be a Skeleton,
    a SkelRoot, or an Xform that has a SkelRoot as a decendent.

    Args:
        path (str): Path to the prim.
    """
    def __init__(self, prim_path: str):
        self._prim_path = prim_path

    def do(self):
        stage = omni.usd.get_context().get_stage()
        prim = stage.GetPrimAtPath(self._prim_path)

        if bool(prim):
            if bool(prim) and prim.IsA(UsdSkel.Skeleton):
                parent = prim.GetParent()
                while parent and not parent.IsA(UsdSkel.Root):
                    parent = parent.GetParent()
                if parent:
                    prim = parent

            from .extension import get_preview_window
            window = get_preview_window()
            if not window.visible:
                window.visible = True
            window.set_skel_prim(str(prim.GetPrimPath()))
            window.focus()
        else:
            carb.log_error(f"-- Unable to send prim for preview: {self._prim_path}")


class AnimationPreviewAddAnnotationCommand(omni.kit.commands.Command):
    """
    Adds a new annotation to a SkelAnimation prim.
        Tag string and end times may be left empty in which case they are set automatically.
    Args:
        path (Union[str, Sdf.Path]): Path to the SkelAnimation prim.
        tag (str): Tag string of the new annotation.
        start_time (int): Start time of the new annotation in frames. Pass None to set the start time of the timeline.
        end_time (int): End time of the new annotation in frames. Pass None to set the the end time of the timeline.
        select_new_prim (bool): Select the new prim in the stage or not.
        context_name (str): Name of the Usd context which holds the stage and the prim.
            If None is passed, the default context is used.
        timeline_name (str): Name of the timeline to be used to set default time parameters.
            If None is passed, the default timeline is used.
    """

    def __init__(self,
        path: Union[str, Sdf.Path],
        tag: Optional[str] = None,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
        select_new_prim: bool = True,
        context_name: Optional[str] = None,
        timeline_name: Optional[str] = None
    ):
        from .annotation.utils import time_to_timecode

        is_valid_input = True
        class_name = self.__class__.__name__
        if not isinstance(path, (str, Sdf.Path)):
            carb.log_error(f"{class_name}: `path` TypeError: " + \
                f"Expected Union[str, Sdf.Path], got {type(path)}.")
            is_valid_input = False
        if tag is not None and not isinstance(tag, str):
            carb.log_error(f"{class_name}: `tag` TypeError: " + \
                f"Expected str, got {type(tag)}.")
            is_valid_input = False
        if start_time is not None and not isinstance(start_time, int):
            carb.log_error(f"{class_name}: `start_time` TypeError: " + \
                f"Expected int, got {type(start_time)}.")
            is_valid_input = False
        if end_time is not None and not isinstance(end_time, int):
            carb.log_error(f"{class_name}: `end_time` TypeError: " + \
                f"Expected int, got {type(end_time)}.")
            is_valid_input = False
        if not isinstance(select_new_prim, bool):
            carb.log_error(f"{class_name}: `select_new_prim` TypeError: " + \
                f"Expected bool, got {type(select_new_prim)}.")
            is_valid_input = False
        if context_name is not None and not isinstance(context_name, str):
            carb.log_error(f"{class_name}: `context_name` TypeError: " + \
                f"Expected str, got {type(context_name)}.")
            is_valid_input = False
        if timeline_name is not None and not isinstance(timeline_name, str):
            carb.log_error(f"{class_name}: `timeline_name` TypeError: " + \
                f"Expected str, got {type(timeline_name)}.")
            is_valid_input = False

        self._is_valid_input = is_valid_input

        if not self._is_valid_input:
            return

        self._path = path
        if tag is not None:
            self._tag = tag
        else:
            self._tag = DEFAULT_ANNOTATION_TAG

        if context_name is None:
            self._context_name = ""
            self._context = omni.usd.get_context()
        else:
            self._context_name = context_name
            self._context = omni.usd.get_context(context_name)
        if self._context is None:
            carb.log_error('{}: context "{}" does not exist'.format(self.__class__.__name__, context_name))
            self._is_valid_input = False
            return

        if timeline_name is None:
            timeline = omni.timeline.get_timeline_interface()
        else:
            timeline = omni.timeline.get_timeline_interface(timeline_name)

        if start_time is None:
            self._start_time = int(time_to_timecode(timeline.get_start_time(), timeline))
        else:
            self._start_time = start_time
        if end_time is None:
            self._end_time = int(time_to_timecode(timeline.get_end_time(), timeline))
        else:
            self._end_time = end_time

        self._select_new_prim = select_new_prim

        self._create_prim_cmd = None

    def do(self):
        if not self._is_valid_input:
            return False

        from .annotation.utils import add_annotation, get_annotation_prim_type

        stage = self._context.get_stage()
        parent_prim = stage.GetPrimAtPath(self._path)
        if not parent_prim.IsValid():
            carb.log_error('{}: prim at "{}" does not exist'.format(self.__class__.__name__, self._path))
            return False

        if not parent_prim.IsA(UsdSkel.Animation):
            carb.log_error('{}: prim at "{}" is not a skeleton animation'.format(self.__class__.__name__, self._path))
            return False

        tag_str = self._tag.replace(' ', '_')
        target_prim_path = Sdf.Path(self._path).AppendChild(tag_str)
        new_prim_path = Sdf.Path(omni.usd.get_stage_next_free_path(stage, target_prim_path, True))

        self._create_prim_cmd = CreatePrimCommand(
            prim_type=get_annotation_prim_type(),
            prim_path=str(new_prim_path),
            select_new_prim=self._select_new_prim,
            create_default_xform=False,
            stage=stage,
            context_name=self._context_name
        )
        self._create_prim_cmd.do()
        new_prim = stage.GetPrimAtPath(new_prim_path)
        if not new_prim.IsValid():
            carb.log_error('{}: could not create prim at {}'.format(self.__class__.__name__, new_prim_path))
            return False

        source = SourceModel()
        source.set_source_path_in_stage(str(new_prim_path))
        if self._context_name == '':
            source.set_source_url(None, True)
        else:
            stage_url = self._context.get_stage_url()
            source.set_source_url(stage_url, False)
        annotation = Annotation(
            tag=self._tag,
            start=self._start_time,
            end=self._end_time,
            source=source
        )

        add_annotation(new_prim, annotation)

        return True

    def undo(self):
        if self._create_prim_cmd:
            self._create_prim_cmd.undo()


class AnimationPreviewAddAnnotationsCommand(omni.kit.commands.Command):
    """
    Adds a multiple annotations to a SkelAnimation prim in the default stage.

    Args:
        path (Union[str, Sdf.Path]): Path to the SkelAnimation prim.
        annotations (List[Tuple[str, int, int]]): the list of annotations. Elements of the list:
            - tag (str): Tag string of the new annotation.
            - start_time (int): Start time of the new annotation in frames.
            - end_time (int): End time of the new annotation in frames.
    """

    def __init__(
        self,
        path: Union[str, Sdf.Path],
        annotations: List[Tuple[str, int, int]]
    ):
        is_valid_input = True
        class_name = self.__class__.__name__
        if not isinstance(path, (str, Sdf.Path)):
            carb.log_error(f"{class_name}: `path` TypeError: " + \
                f"Expected Union[str, Sdf.Path], got {type(path)}.")
            is_valid_input = False

        if not isinstance(annotations, list):
            carb.log_error(f"{class_name}: `annotations` TypeError: " + \
                f"Expected List[Tuple[str, int, int]], got {type(annotations)}.")
            is_valid_input = False
        else:
            for i in range(len(annotations)):
                annotation = annotations[i]
                if not isinstance(annotation, Tuple) or len(annotation) != 3 or \
                        not isinstance(annotation[0], str) or not isinstance(annotation[1], (int, float)) or \
                        not isinstance(annotation[2], (int, float)):
                    carb.log_error(f"{class_name}: `annotations[{i}]` TypeError: " + \
                        f"Expected Tuple[str, int, int], got {type(annotation)}.")
                    is_valid_input = False

        self._is_valid_input = is_valid_input

        self._path = path
        self._annotations = annotations

    def do(self):
        if not self._is_valid_input:
            return False

        context_name = ""
        self._cmds = []

        success = True
        for annotation in self._annotations:
            tag = annotation[0]
            start = annotation[1]
            end = annotation[2]
            cmd = AnimationPreviewAddAnnotationCommand(
                path=self._path,
                tag=tag,
                start_time=start,
                end_time=end,
                context_name=context_name
            )
            success = success and cmd.do()
            if not success:
                for cmd in self._cmds:
                    cmd.undo()
                return False

            self._cmds.append(cmd)

        return True

    def undo(self):
        for cmd in self._cmds:
            cmd.undo()


class AnimationPreviewRemoveAnnotationsCommand(omni.kit.commands.Command):
    """
    Removes an annotation with the given parameters from a SkelAnimation prim.
        Only the default context and stage are supported.
    Args:
        path (Union[str, Sdf.Path]): Path to the SkelAnimation prim.
        tag (str): Tag string of the annotation to be removed. None by default.
            If None is passed, all annotations with the given start or end times are removed.
        start_time (int): Start time of the annotation to be removed. None by default.
            If None is passed, all annotations with the given tag and end times are removed.
        end_time (int): End time of the annotation to be removed. None by default.
            If None is passed, all annotations with the given tag and start times are removed.
        exact_times (bool): whether start and end times have to be exact or they represent an interval. True by default.
            False means all annotations that start after start_time and end between end_time are removed.

    Examples:
        # Removes all annotations.
        AnimationPreviewRemoveAnnotationsCommand('/World/my_anim')

        # Removes all annotations with tag "Walk"
        AnimationPreviewRemoveAnnotationsCommand('/World/my_anim', tag='Walk')

         # Removes all annotations that start at time code 50
        AnimationPreviewRemoveAnnotationsCommand('/World/my_anim', start_time=50)

        # Removes all annotations that start at time code 50 or later
        AnimationPreviewRemoveAnnotationsCommand('/World/my_anim', start_time=50, exact_times=False)

        # Removes all annotations that fall in the [50, 100] time code interval
        AnimationPreviewRemoveAnnotationsCommand('/World/my_anim', start_time=50, end_time=100, exact_times=False)
    """

    def __init__(self,
        path: Union[str, Sdf.Path],
        tag: Optional[str] = None,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
        exact_times: bool = True,
    ):
        is_valid_input = True
        class_name = self.__class__.__name__
        if not isinstance(path, (str, Sdf.Path)):
            carb.log_error(f"{class_name}: `path` TypeError: " + \
                f"Expected Union[str, Sdf.Path], got {type(path)}.")
            is_valid_input = False
        if tag is not None and not isinstance(tag, str):
            carb.log_error(f"{class_name}: `tag` TypeError: " + \
                f"Expected str, got {type(tag)}.")
            is_valid_input = False
        if start_time is not None and not isinstance(start_time, int):
            carb.log_error(f"{class_name}: `start_time` TypeError: " + \
                f"Expected int, got {type(start_time)}.")
            is_valid_input = False
        if end_time is not None and not isinstance(end_time, int):
            carb.log_error(f"{class_name}: `end_time` TypeError: " + \
                f"Expected int, got {type(end_time)}.")
            is_valid_input = False
        if not isinstance(exact_times, bool):
            carb.log_error(f"{class_name}: `exact_times` TypeError: " + \
                f"Expected bool, got {type(exact_times)}.")
            is_valid_input = False
        self._is_valid_input = is_valid_input

        self._path = path
        self._tag = tag
        self._start_time = start_time
        self._end_time = end_time
        self._exact_times = exact_times

        self._context = omni.usd.get_context()
        self._remove_prim_cmd = None

    def do(self):
        if not self._is_valid_input:
            return False

        from .annotation.utils import get_annotations

        stage = self._context.get_stage()
        parent_prim = stage.GetPrimAtPath(self._path)
        if not parent_prim.IsValid():
            carb.log_error('{}: prim at "{}" does not exist'.format(self.__class__.__name__, self._path))
            return False

        if not parent_prim.IsA(UsdSkel.Animation):
            carb.log_error('{}: prim at "{}" is not a skeleton animation'.format(self.__class__.__name__, self._path))
            return False

        annotations = get_annotations(
            parent_prim,
            tag=self._tag,
            start_time=self._start_time,
            end_time=self._end_time,
            exact_times=self._exact_times
        )
        paths_to_remove = []
        for annotation in annotations:
            paths_to_remove.append(annotation.source.source_path_in_stage)

        self._remove_prim_cmd = DeletePrimsCommand(paths_to_remove)
        self._remove_prim_cmd.do()

        return True

    def undo(self):
        if self._remove_prim_cmd:
            self._remove_prim_cmd.undo()


class AnimationPreviewSetupPickupAnnotationCommand(omni.kit.commands.Command):
    """
    Add a list of annotations for the given parameters from a SkelAnimation prim.
        Only the default context and stage are supported.
    Args:
        path (Union[str, Sdf.Path]): Path to the SkelAnimation prim.
        handtype (str) : handtype - RightHand, LeftHand, BothHands

        - Rename the file to usda without skel
        - Rename the root to the file name
        - Add tags by type
    """

    def __init__(self,
        path: Union[str, Sdf.Path],
        hand_type: [str],
        height_type: [str]

    ):
        self._path = path
        #self._hand_type = hand_type
        #self._height_type = height_type
        self._usd_undo = None
        self._annotations = ["Pickup", "Putdown", "EnableIK", "Attach", "DisableIK", "Detach", hand_type, height_type]

    def do(self):
        # Rename the file to usda without skel
        context = omni.usd.get_context()
        stage = context.get_stage()
        # Get the current root layer of the stage
        root_layer = stage.GetRootLayer()

        old_stage_name = root_layer.realPath
        default_name = os.path.basename(root_layer.realPath)[:-13]

        # Define the new name for the stage
        new_stage_name = old_stage_name[:-13] + ".usda"

        # Rename the root layer file to the new name
        #root_layer.TransferOwnership(Sdf.Layer.CreateNew())

        # Save the modified stage
        #stage.GetRootLayer().Save()

        self._usd_undo = UsdLayerUndo(stage.GetEditTarget().GetLayer())

        # Rename the root to the file name
        default_prim = root_layer.defaultPrim

        self._path = "/" + default_name

        omni.kit.commands.execute("MovePrim", path_from="/" + default_prim, path_to=self._path)

        self._cmds = []

        success = True

        # Add annotations
        for annotation in self._annotations:
            tag = annotation
            cmd = AnimationPreviewAddAnnotationCommand(
                path=self._path,
                tag=tag,
                context_name=context.get_name()
            )

            success = success and cmd.do()
            if not success:
                for cmd in self._cmds:
                    cmd.undo()
                return False

            self._cmds.append(cmd)

        context.save_as_stage(new_stage_name)

        return True

    def undo(self):
        if self._usd_undo is not None:
            self._usd_undo.undo()

        for cmd in self._cmds:
            cmd.undo()
