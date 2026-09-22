# Copyright (c) 2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

from typing import Callable

import omni.kit.app
from usdrt import Rt, Sdf, Usd


class RtChangeTrackerWrapper:
    # Simplified notice object based on return methods in Usd.Notice.ObjectsChanged
    class Notice:
        def __init__(self, resynced_paths: list[Sdf.Path], changed_info_only_paths: list[Sdf.Path]):
            self._resynced_paths = resynced_paths
            self._changed_info_only_paths = changed_info_only_paths

        @property
        def is_fabric(self):
            return True

        def GetResyncedPaths(self):  # noqa: N802
            return self._resynced_paths

        def GetChangedInfoOnlyPaths(self):  # noqa: N802
            return self._changed_info_only_paths

    def __init__(
        self,
        attr_names: list[str],
        prim_paths: list[Sdf.Path],
        callback: Callable[[Notice, Usd.Stage], None],
        stage: Usd.Stage,
    ):

        self._prim_paths = prim_paths
        self._callback = callback
        self._stage = stage
        self._attr_names = attr_names

        self._tracker = Rt.ChangeTracker(stage)

        # Setup tracking for all attribute names
        for attr_name in self._attr_names:
            self._tracker.TrackAttribute(attr_name)

        # Setup update callback
        from carb.eventdispatcher import get_eventdispatcher

        self._update_sub = get_eventdispatcher().observe_event(
            event_name=omni.kit.app.GLOBAL_EVENT_UPDATE,
            on_event=self._on_update,
            observer_name="omni.kit.property.adapter.fabric change_tracker_wrapper update",
        )

    def __del__(self):
        self.destroy()

    def destroy(self):
        self._update_sub = None
        if self._tracker:
            for attr_name in self._attr_names:
                self._tracker.StopTrackingAttribute(attr_name)
            self._tracker = None
        self._attr_names = None

    def _on_update(self, _):
        # Kick out if there is no tracker or the tracker doesn't have any changes
        if not self._tracker:
            return
        if not self._tracker.HasChanges():
            return

        resynced_paths = []
        changed_info_only_paths = []

        # Populate changed_info_only_paths with changes attribute paths.
        for prim_path in self._prim_paths:
            changed_attrs = self._tracker.GetChangedAttributes(prim_path)
            for changed_attr in changed_attrs:
                # Form the full attribute path and put it into changed_info_only_paths
                changed_info_only_paths.append(prim_path.AppendProperty(changed_attr))

        # TODO: Eventually populate resynced_paths list. RtChangeTracker doesn't currently support structural changes.

        # If any path list is not empty, call the callback
        if resynced_paths or changed_info_only_paths:
            # Emulate the callback behavior with a notice object and the stage payload
            notice = RtChangeTrackerWrapper.Notice(resynced_paths, changed_info_only_paths)
            self._callback(notice, self._stage)

        # Clear changes so the tracker can be repopulated with new changes on the next frame
        self._tracker.ClearChanges()
