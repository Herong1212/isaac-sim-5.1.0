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

import os
import uuid

import omni.usd
import usdrt
from pxr import Sdf

from ..asset_cache import get_asset_cache
from ..functional import modify

REPLICATOR_SCOPE = "/Replicator"
VALID_POPULATION_MODES = ["scene_instance", "point_instance", "reference"]


class PopulationError(Exception):
    pass


class Population:
    def __init__(
        self,
        usd_paths=None,
        mode="scene_instance",
        population_name="",
        use_cache=True,
        hide_originals=True,
        semantics=[],
    ) -> None:
        """A collection of all the possible assets for randomization

        Args:
            usd_paths: A list of the paths to use as the source prims to sample from.
            mode: Select from [`point_instance`, `scene_instance`]. Point instancers allow for much faster randomization
                at the expense of flexibility in how each instance can be modified.
            population_name (optional): String to prepend to the created population prim.
            use_cache: If ``True``, cache the assets in ``paths`` to speed up randomization. Set to False
                if the size of the population is too large to be cached. Default: True.
            hide_originals: If ``True`` usd paths point to prims in the stage, make prims invisible. Default: True.

        Returns:
            ``None``
        """

        if mode not in VALID_POPULATION_MODES:
            raise PopulationError(
                f"No valid population mode! Valid options are: {', '.join(m for m in VALID_POPULATION_MODES)}"
            )

        self.usd_paths = usd_paths
        self.mode = mode
        self.use_cache = use_cache
        self.hide_originals = hide_originals
        self.semantics = semantics

        self._uuid = str(uuid.uuid1())[:8]
        self._root = f"{REPLICATOR_SCOPE}/SampledAssets"
        self._population_name = f"Population_{self._uuid}"
        self._sample_paths = []
        self._cache = get_asset_cache()
        self._references = {}
        self._population_prim_path = None

    @property
    def population_prim_path(self):
        if not self._population_prim_path:
            self._population_prim_path = f"{self._root}/{self._population_name}"
        return self._population_prim_path

    @population_prim_path.setter
    def population_prim_path(self, value):
        if not isinstance(value, (str, Sdf.Path, usdrt.Sdf.Path)):
            raise ValueError(f"Unable to set population prim path, expected `str`, got `{type(value)}")
        self._population_prim_path = str(value)

    @property
    def uuid(self):
        """The UUID of this population"""
        return self._uuid

    def set_population_name(self, population_name=None):
        """Set a custom name for the population."""
        if population_name:
            self._population_name = f"{population_name}_{self._uuid}"

    def clear_sampled(self):
        """Clears the sampled prims of this population"""
        stage = omni.usd.get_context().get_stage()
        for sample_path in self._sample_paths:
            stage.RemovePrim(sample_path)
        if self._population_prim and self.mode == "point_instance":
            stage.RemovePrim(self._population_prim.GetPath())
        self._sample_paths = []

    def populate(self):
        """Populate the scene using the paths.

        Returns:
            A list of prim paths that have been populated. For point instance mode, the prim path to
            the point instancer is returned instead.

        Raises:
            ``PopulationError`` if the population mode is not valid.
        """
        self._sample_paths = []

        items = self.usd_paths

        stage = omni.usd.get_context().get_stage()
        if not stage.GetPrimAtPath(self._root):
            root_prim = stage.DefinePrim(self._root, "Scope")
            # UsdGeom.PrimvarsAPI(root_prim).CreatePrimvar("hideForCamera", Sdf.ValueTypeNames.Bool).Set(False)

        if self.mode == "scene_instance":
            self._scene_instance(items, True)

        elif self.mode == "point_instance":
            self._point_instance(items)

        # NOTE Can lead to MATERIAL LOADING ISSUE
        elif self.mode == "reference":
            self._scene_instance(items, False)

        else:
            raise PopulationError(
                "No valid population mode! Valid options are: " f"{', '.join(m for m in VALID_POPULATION_MODES)}"
            )

        return self._sample_paths

    def _get_ref(self, idx):
        stage = omni.usd.get_context().get_stage()
        while idx > len(self._references) - 1:
            ref = stage.DefinePrim(f"{self._population_prim.GetPath().pathString}/Ref{len(self._references)}")
            self._references.append(ref)
        return self._references[idx]

    def _populate_references(self):
        stage = omni.usd.get_context().get_stage()
        population_prim = stage.GetPrimAtPath(self.population_prim_path)
        if not population_prim:
            return {}
        for child in population_prim.GetChildren():
            child_path = str(child.GetPath())
            child_ref = stage.GetPrimAtPath(f"{child_path}/Ref")
            if child_ref:
                references = child_ref.GetMetadata("references").GetAddedOrExplicitItems()
                if references:
                    ref_path = references[0].assetPath if references[0].assetPath else references[0].primPath
                    self._references.setdefault(str(ref_path), []).append(child)

    def _scene_instance(self, items, instanceable):
        stage = omni.usd.get_context().get_stage()
        population_prim = stage.GetPrimAtPath(self.population_prim_path)
        if not population_prim:
            population_prim = stage.DefinePrim(self.population_prim_path, "Xform")
            # UsdGeom.PrimvarsAPI(population_prim).CreatePrimvar("hideForCamera", Sdf.ValueTypeNames.Bool).Set(False)

        # Populate reference cache if empty
        if not self._references:
            self._populate_references()

        used_references = {}
        for idx, item in enumerate(items):
            # Internal Reference
            if not item.endswith((".usd", ".usda", ".usdc")):
                # NOTE: move the target prim into new path for invisibility
                prim_name = item.split("/")[-1]
                if not stage.GetPrimAtPath(REPLICATOR_SCOPE):
                    stage.DefinePrim(REPLICATOR_SCOPE, "Scope")

                internal_ref_path = f"{REPLICATOR_SCOPE}/InternalReference"

                if not stage.GetPrimAtPath(internal_ref_path).IsValid():
                    internal_ref_prim = stage.DefinePrim(internal_ref_path, "Xform")
                    internal_ref_prim.GetAttribute("visibility").Set("invisible")

                new_path = internal_ref_path + "/" + prim_name

                # Move prim
                omni.usd.duplicate_prim(stage, item, new_path)
                stage.RemovePrim(item)

                item = new_path

            path = self._cache.get(item) if self.use_cache else item
            if not str(path).endswith((".usd", ".usda", ".usdc")):
                path = f"{path}/Cached_Prim"

            available_refs = self._references.get(str(path))
            xform_ref_path = None

            if available_refs:
                xform_ref = available_refs.pop()
                ref = xform_ref.GetChild("Ref")
            else:
                xform_ref_path = omni.usd.get_stage_next_free_path(
                    stage, f"{population_prim.GetPath().pathString}/Ref_Xform_{idx}", False
                )
                xform_ref = stage.DefinePrim(xform_ref_path, "Xform")
                xform_ref.CreateAttribute("replicatorXform", Sdf.ValueTypeNames.Bool).Set(
                    True
                )  # tells replicator that this is a parent xform
                ref_path = f"{xform_ref_path}/Ref"
                ref = stage.DefinePrim(ref_path)

            if str(path).endswith((".usd", ".usda", ".usdc")):
                ref.GetReferences().AddReference(path)
            else:
                # Add reference to existing prim.
                ref.GetReferences().AddInternalReference(str(path))
                ref.SetInstanceable(instanceable)

            if self.semantics and xform_ref_path:
                modify.semantics(xform_ref, self.semantics)

            used_references.setdefault(str(path), []).append(xform_ref)  # previous
            self._sample_paths.append(xform_ref.GetPath())

        for _, refs in self._references.items():
            for ref in refs:
                stage.RemovePrim(str(ref.GetPath()))

        self._references = used_references

    def _point_instance(self, items):
        """Create a point instancer with only the indices set"""
        stage = omni.usd.get_context().get_stage()
        population_prim = stage.GetPrimAtPath(self.population_prim_path)
        if not population_prim:
            population_prim = stage.DefinePrim(f"{self._root}/{self._population_name}", "PointInstancer")

        cached_prototypes = [self._cache.get(item, True) for item in set(self.usd_paths)]
        cached_items = [self._cache.get(item, True) for item in items]
        prototypes = sorted(list(set(cached_prototypes)))
        indices = [prototypes.index(path) for path in cached_items]

        # Copy a single copy of each prototype prim under the PointInstancer to support instance segmentation
        protopaths = [os.path.basename(child.GetPath().pathString) for child in population_prim.GetChildren()]
        new_prototypes = []
        for proto in prototypes:
            if os.path.basename(proto) not in protopaths:
                new_path = f"{population_prim.GetPath()}/{os.path.basename(proto)}"
                # Duplicate prim will cause asset to become invisible
                omni.usd.duplicate_prim(stage, proto, new_path)
                new_prim = stage.GetPrimAtPath(new_path)
                new_prim.GetAttribute("visibility").Set("inherited")
                if self.semantics:
                    modify.semantics(new_prim, self.semantics)
                new_prototypes.append(Sdf.Path(new_path))

        # Set point instancer attributes
        # Setting prototypes is expensive, only do it if prototypes have changed
        if new_prototypes:
            cur_prototypes = population_prim.GetRelationship("prototypes").GetTargets()
            total_prototypes = set(cur_prototypes + new_prototypes)
            population_prim.GetRelationship("prototypes").SetTargets(sorted(total_prototypes))

        # Make sure indices match point instancer prototype order
        targets = population_prim.GetRelationship("prototypes").GetTargets()
        targets_base = [os.path.basename(str(t)) for t in targets]
        indices = [targets_base.index(os.path.basename(ci)) for ci in cached_items]
        population_prim.GetAttribute("protoIndices").Set(indices)
        population_prim.GetAttribute("positions").Set([[0.0, 0.0, 0.0]] * len(indices))

        # Point instancer contains proto paths so return the path of the point instancer instead
        self._sample_paths.append(population_prim.GetPath())
