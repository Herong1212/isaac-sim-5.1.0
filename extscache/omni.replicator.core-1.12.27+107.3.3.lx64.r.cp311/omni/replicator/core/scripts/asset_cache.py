# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import carb
import omni.usd
from pxr import UsdGeom

ASSET_CACHE = None
REPLICATOR_SCOPE = "/Replicator"


class AssetCache:
    def __init__(self, size=None) -> None:
        """Simple cache that keeps assets on the stage for faster loading when randomizing. The cache is sorted from
        least to most recently cached item.

        Args:
            size (optional): number of assets to keep in the cache, default won't delete cached items.
        """
        self.size = size

        self._prim_path = f"{REPLICATOR_SCOPE}/AssetCache"
        self._prim = None
        self._cache_map = {}
        self._cache_map_pi = {}

        self._stage_dirty_state_changed_sub = carb.eventdispatcher.get_eventdispatcher().observe_event(
            event_name=omni.usd.get_context().stage_event_name(omni.usd.StageEventType.DIRTY_STATE_CHANGED),
            on_event=self._on_stage_event,
            observer_name="omni.replicator.core.asset_cache:dirty_state_changed",
        )
        self._stage_closed_sub = carb.eventdispatcher.get_eventdispatcher().observe_event(
            event_name=omni.usd.get_context().stage_event_name(omni.usd.StageEventType.CLOSED),
            on_event=self._on_stage_event,
            observer_name="omni.replicator.core.asset_cache:stage_closed",
        )
        self._stage_opened_sub = carb.eventdispatcher.get_eventdispatcher().observe_event(
            event_name=omni.usd.get_context().stage_event_name(omni.usd.StageEventType.OPENED),
            on_event=self._on_stage_event,
            observer_name="omni.replicator.core.asset_cache:stage_opened",
        )
        self._stage_assets_loaded_sub = carb.eventdispatcher.get_eventdispatcher().observe_event(
            event_name=omni.usd.get_context().stage_event_name(omni.usd.StageEventType.ASSETS_LOADED),
            on_event=self._on_stage_event,
            observer_name="omni.replicator.core.asset_cache:assets_loaded",
        )
        self._stage_assets_load_aborted_sub = carb.eventdispatcher.get_eventdispatcher().observe_event(
            event_name=omni.usd.get_context().stage_event_name(omni.usd.StageEventType.ASSETS_LOAD_ABORTED),
            on_event=self._on_stage_event,
            observer_name="omni.replicator.core.asset_cache:assets_load_aborted",
        )

        stage = omni.usd.get_context().get_stage()

        if not stage:
            carb.log_warn("No stage available!")
            return

    def _on_stage_event(self, event):
        """Stage event subscription logic"""

        stage_event = omni.usd.get_context().stage_event_type(event.event_name)

        # Limit the events that cause the cache to refresh
        if stage_event in (
            omni.usd.StageEventType.ASSETS_LOADED,
            omni.usd.StageEventType.ASSETS_LOAD_ABORTED,
            omni.usd.StageEventType.DIRTY_STATE_CHANGED,
            omni.usd.StageEventType.OPENED,
        ):
            self._refresh()

        # Map becomes invalid when the stage is closed
        if stage_event == omni.usd.StageEventType.CLOSED:
            self._cache_map = {}
            self._cache_map_pi = {}

    def get(self, source_path: str, is_for_point_instancer: bool = False, hide_original: bool = True):
        """Cache the item if not in the cache otherwise return the cached local stage path.

        Args:
            source_path: Path to the USD reference
            is_for_point_instancer: Set to True to return prims that can be used within point instancers.
            hide_original: For internal references to other prims, hide the original referenced prim
        """
        if (
            source_path not in self._cache_map or source_path not in self._cache_map_pi
        ):  # added to ensure pi is populated
            self._add_item(source_path, hide_original)

        if is_for_point_instancer:
            return self._cache_map_pi[source_path]

        return self._cache_map[source_path]

    def clear(self):
        """Removes the cached prims."""
        stage = omni.usd.get_context().get_stage()

        prims_list = stage.GetPrimAtPath(f"{self._prim_path}/Cache").GetChildren()
        prims_list.extend(stage.GetPrimAtPath(f"{self._prim_path}/pi").GetChildren())
        prim_paths = [p.GetPath() for p in prims_list]

        for prim_path in prim_paths:
            stage.RemovePrim(prim_path)
        self._cache_map = {}
        self._cache_map_pi = {}

    def _create(self):
        """Create the top level AssetCache prim"""
        stage = omni.usd.get_context().get_stage()

        if not stage.GetPrimAtPath(REPLICATOR_SCOPE):
            stage.DefinePrim(REPLICATOR_SCOPE, "Scope")

        if not stage.GetPrimAtPath(self._prim_path).IsValid():
            self._prim = stage.DefinePrim(self._prim_path, "Xform")
            cache = stage.DefinePrim(f"{self._prim_path}/Cache", "Xform")
            cache.GetAttribute("visibility").Set("invisible")
            # UsdGeom.PrimvarsAPI(cache).CreatePrimvar("hideForCamera", Sdf.ValueTypeNames.Bool).Set(True)
            # UsdGeom.PrimvarsAPI(cache).CreatePrimvar("doNotCastShadows", Sdf.ValueTypeNames.Bool).Set(True)

            pi_prim = stage.DefinePrim(f"{self._prim_path}/pi", "Xform")
            pi_prim.GetAttribute("visibility").Set("invisible")

    def _refresh(self):
        """Refresh the asset cache mapping"""
        stage = omni.usd.get_context().get_stage()

        if not stage:
            return

        if not stage.GetPrimAtPath(REPLICATOR_SCOPE):
            return

        if not stage.GetPrimAtPath(f"{self._prim_path}/Cache"):
            return

        self._create()

        cache_prims = stage.GetPrimAtPath(f"{self._prim_path}/Cache").GetChildren()

        for xform_prim in cache_prims:
            prim = xform_prim.GetChild("Cached_Prim")
            source_path = prim.GetMetadata("references").GetAddedOrExplicitItems()[0].assetPath
            self._cache_map[source_path] = xform_prim.GetPath()
            UsdGeom.PrimvarsAPI(prim).RemovePrimvar("doNotCastShadows")

        pi_cache_prims = stage.GetPrimAtPath(f"{self._prim_path}/pi").GetChildren()

        for xform_prim_pi in pi_cache_prims:
            prim = xform_prim_pi.GetChild("Cached_Prim_pi")
            if prim:
                source_path = prim.GetMetadata("references").GetAddedOrExplicitItems()[0].assetPath
                self._cache_map_pi[source_path] = prim.GetPath()

    def _add_item(self, item, hide_original):
        stage = omni.usd.get_context().get_stage()
        if self.size is not None and len(self._cache_map) >= self.size:
            self._remove_item()

        if not stage.GetPrimAtPath(f"{self._prim_path}/Cache") or not stage.GetPrimAtPath(f"{self._prim_path}/pi"):
            self._create()

        cached_xform_path = f"{self._prim_path}/Cache/Cached{len(self._cache_map)}_Xform"
        stage.DefinePrim(cached_xform_path)
        cache_path = f"{cached_xform_path}/Cached_Prim"
        cache_prim = stage.DefinePrim(cache_path)

        if str(item).endswith((".usd", ".usda", ".usdc")):
            cache_prim.GetReferences().AddReference(item)
        else:
            cache_prim.GetReferences().AddInternalReference(str(item))
            if hide_original:
                stage.GetPrimAtPath(str(item)).GetAttribute("visibility").Set("invisible")
                cache_prim.GetAttribute("visibility").Set("inherited")

        # Add to cache for PI
        cached_path_pi = f"{self._prim_path}/pi/Cached{len(self._cache_map)}_Prim_pi"
        cache_prim_pi = stage.DefinePrim(cached_path_pi)

        if item.endswith((".usd", ".usda", ".usdc")):
            cache_prim_pi.GetReferences().AddReference(item)
            # cache_prim_pi.SetInstanceable(True)
        else:
            cache_prim_pi.GetReferences().AddInternalReference(item)
            if hide_original:
                stage.GetPrimAtPath(item).GetAttribute("visibility").Set("invisible")
                cache_prim_pi.GetAttribute("visibility").Set("inherited")

        self._cache_map[item] = cached_xform_path
        self._cache_map_pi[item] = cached_path_pi

        return cache_path

    def _remove_item(self):
        item_key, item_to_remove = self._cache_map.popitem()
        item_to_remove_pi = self._cache_map_pi.pop(item_key)

        stage = omni.usd.get_context().get_stage()
        stage.RemovePrim(item_to_remove)
        stage.RemovePrim(item_to_remove_pi)

        carb.log_info(f"Cache full, deleting {item_to_remove[0]} from cache.")


# This needs to be global
def get_asset_cache() -> AssetCache:
    global ASSET_CACHE

    if not ASSET_CACHE:
        ASSET_CACHE = AssetCache()

    return ASSET_CACHE  # noqa: R504
