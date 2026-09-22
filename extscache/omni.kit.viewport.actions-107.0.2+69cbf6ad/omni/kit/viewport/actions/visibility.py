# Copyright (c) 2021-2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

__all__ = ["VisibilityEdit"]


import carb
import omni.usd
from pxr import Usd, UsdGeom, Sdf
from typing import Callable, Optional, Sequence


def _get_usd_rt_stage(stage: Usd.Stage):
    try:
        from pxr import UsdUtils
        from usdrt import Usd as UsdRtUsd

        stage_id = UsdUtils.StageCache.Get().GetId(stage).ToLongInt()
        fabric_active_for_stage = UsdRtUsd.Stage.StageWithHistoryExists(stage_id)
        if fabric_active_for_stage:
            return UsdRtUsd.Stage.Attach(stage_id)
    except (ImportError, ModuleNotFoundError):
        pass
    return None


class VisibilityEdit:
    def __init__(self, stage, types_to_show: Optional[Sequence[str]] = None, types_to_hide: Optional[Sequence[str]] = None):
        # Sdf.Path.FindLongestPrefix require Sdf.PathVector (i.e. list) so we cannot use a dict
        self.__path_to_change = {}
        self.__stage = stage
        self.__types_to_show = types_to_show
        self.__types_to_hide = types_to_hide
        self.__ignore_hidden_in_stage = carb.settings.get_settings().get("/exts/omni.kit.viewport.actions/visibilityToggle/ignoreStageWindowHidden")

    def run(self):
        if self.__gather_prims():
            self.__hide_prims()

    @carb.profiler.profile
    def __get_prim_iterator(self, predicate):
        # Early exit for request to do nothing
        if not bool(self.__types_to_show) and not bool(self.__types_to_hide):
            return

        # Local function to filter Usd.Prim, returns None to ignore it or the Usd.Prim otherwise
        def filter_prim(prim: Usd.Prim):
            if self.__ignore_hidden_in_stage and omni.usd.editor.is_hide_in_stage_window(prim):
                return None
            return prim

        # If UsdRt is available, use it to pre-prune the traversal to only given types
        rt_stage = _get_usd_rt_stage(self.__stage)
        if rt_stage:
            # Merge all the prim-types of interest into one set for querying
            if self.__types_to_show:
                prim_types = set(self.__types_to_show)
                if self.__types_to_hide:
                    prim_types = prim_types.union(set(self.__types_to_hide))
            else:
                prim_types = set(self.__types_to_hide)

            for prim_type in prim_types:
                for prim_path in rt_stage.GetPrimsWithTypeName(prim_type):
                    prim = filter_prim(self.__stage.GetPrimAtPath(prim_path.GetString()))
                    if prim:
                        yield prim
            return

        iterator = iter(self.__stage.Traverse(predicate))
        for prim in iterator:
            # Prune anything that is hide_in_stage_window
            # Not sure why, but this matches legacy behavior
            if filter_prim(prim) is None:
                iterator.PruneChildren()
                continue

            yield prim

    @property
    def predicate(self):
        return Usd.TraverseInstanceProxies(Usd.PrimDefaultPredicate)

    def __get_visibility(self, prim: Usd.Prim, prim_path: Sdf.Path):
        type_name = prim.GetTypeName()
        make_visible = type_name in self.__types_to_show if self.__types_to_show else False
        make_invisible = type_name in self.__types_to_hide if self.__types_to_hide else False
        return (make_visible, make_invisible)

    @carb.profiler.profile
    def __gather_prims(self):
        path_to_change = {}

        # Traverse the stage, gathering the prims that have requested a visibility change
        # This is a two-phase process to allow hiding leaves of instances by hiding the
        # top-most un-instanced parent whose leaves are all of a hide-able type
        for prim in self.__get_prim_iterator(self.predicate):
            prim_path = prim.GetPath()
            make_visible, make_invisible = self.__get_visibility(prim, prim_path)

            # If not making this type visible or invisible, then nothing to do
            if (make_visible is False) and (make_invisible is False):
                continue

            if prim.IsInstanceProxy():
                is_child = False
                for path in path_to_change.keys():
                    if path.GetCommonPrefix(prim_path) == path:
                        is_child = True
                        break
                if is_child:
                    continue

                parent = prim.GetParent()
                while parent and not parent.IsInstance():
                    parent = parent.GetParent()
                # Insert the parent now and validate all children in the second phase
                if parent:
                    path_to_change[parent.GetPath()] = True
            else:
                path_to_change[prim_path] = False

        self.__path_to_change = path_to_change
        return len(self.__path_to_change) != 0

    @carb.profiler.profile
    def __hide_prims(self):
        # Traverse the instanced prims, making sure that all children are of the proper type
        # or an allowed 'intermediate' type of Xform or Scope.
        # If all children pass that test, then the instance can safely be hidden, otherwise
        # it contains children that are not being requested as hidden, so the instance is left alone.

        predicate = self.predicate
        # UsdGeom.Imageabales that are acceptable intermediate children
        allowed_imageables = set(("Xform", "Scope"))
        # Setup the edit-context once, and batch all changes
        session_layer = self.__stage.GetSessionLayer()
        with Usd.EditContext(self.__stage, session_layer):
            with Sdf.ChangeBlock():
                for prim_path, is_instance in self.__path_to_change.items():
                    prim = self.__stage.GetPrimAtPath(prim_path)
                    if not prim:
                        continue
                    if prim.IsInstanceProxy():
                        carb.log_error(f"Unexpected instance in list of prims to toggle visibility: {prim.GetPath()}")
                        continue

                    # Assume success
                    toggle_error = None
                    visible = None

                    # If its an instance, traverse all children and make sure that
                    # they are of the right type, not a UsdImageable, or an allowed intermediate.
                    if is_instance:
                        for child_prim in prim.GetFilteredChildren(predicate):
                            child_type = child_prim.GetTypeName()
                            child_show, child_hide = self.__get_visibility(child_prim, child_prim.GetPath())
                            if (not child_show) and (not child_hide):
                                # If child is in neither list, than it must be an allowed intermediate type (or not an Imagaeable)
                                if (not UsdGeom.Imageable(child_prim)) or (child_type in allowed_imageables):
                                    continue
                                toggle_error = "it contains at least one child with a type not being requested to hide."
                                break
                            # First loop iteration, set visible to proper state
                            if visible is None:
                                visible = child_show
                            if child_show != visible:
                                toggle_error = "its hierarchy is too heterogeneous for this action."
                                break
                    else:
                        visible = prim.GetTypeName() in self.__types_to_show if self.__types_to_show else False

                    if toggle_error:
                        visible_verb = 'show' if visible else 'hide'
                        carb.log_warn(f"Will not {visible_verb} '{prim_path}', {toggle_error}")
                        continue

                    if visible:
                        # as the session layer overrides all other layers, remove the primSpec
                        prim_spec = session_layer.GetPrimAtPath(prim_path)
                        property = session_layer.GetPropertyAtPath(prim_path.AppendProperty(UsdGeom.Tokens.visibility)) if prim_spec else None
                        if property:
                            prim_spec.RemoveProperty(property)
                    else:
                        imageable = UsdGeom.Imageable(prim)
                        if imageable:
                            imageable.GetVisibilityAttr().Set(UsdGeom.Tokens.invisible)
