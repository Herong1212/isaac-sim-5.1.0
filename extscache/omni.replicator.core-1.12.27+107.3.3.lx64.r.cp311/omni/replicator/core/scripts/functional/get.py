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

import re
from typing import List, Optional, Tuple, Union

import carb
import omni.usd
import pxr
import usdrt

from ..utils import utils
from . import utils as f_utils


def _get_prims(
    stage: Optional[Union[pxr.Usd.Stage, usdrt.Usd.Stage]] = None,
    path_pattern: Optional[str] = None,
    path_match: Optional[str] = None,
    path_pattern_exclusion: Optional[str] = None,
    prim_types: Optional[List[str]] = None,
    prim_types_exclusion: Optional[List[str]] = None,
    semantics: Optional[List[str]] = None,
    semantics_exclusion: Optional[List[str]] = None,
    ignore_case: bool = False,
) -> List[pxr.Usd.Prim]:
    if stage is None:
        stage = omni.usd.get_context().get_stage()

    # regex setup
    re_flags = 0
    if ignore_case:
        re_flags = re.IGNORECASE

    if path_pattern:
        path_pattern_regex = re.compile(path_pattern, flags=re_flags)
    if path_pattern_exclusion:
        path_exclusion_regex = re.compile(path_pattern_exclusion, flags=re_flags)
    if prim_types:
        prim_types = [pt.lower() for pt in prim_types]
    if prim_types_exclusion:
        prim_types_exclusion = [pt.lower() for pt in prim_types_exclusion]

    gathered_prims = []
    if semantics:
        semantics = utils.legacy_semantics_arg_to_new(semantics)
    if semantics_exclusion:
        semantics_exclusion = utils.legacy_semantics_arg_to_new(semantics_exclusion)

    stage_usdrt = usdrt.Usd.Stage.Attach(omni.usd.get_context().get_stage_id())

    prim_list = []
    is_fsd = f_utils.get_is_fsd_enabled()
    if is_fsd:
        # Prefilter list using USDRT
        # Filtering multi-apply schemas (ie. Semantics) does not work without FSD
        if prim_types and semantics:
            for prim_type in prim_types:
                prim_list += stage_usdrt.GetPrimsWithTypeAndAppliedAPIName(
                    prim_type, ["SemanticsAPI", "SemanticsLabelsAPI"]
                )
        elif prim_types:
            for prim_type in prim_types:
                prim_list += stage_usdrt.GetPrimsWithTypeName(prim_type.capitalize())
        elif semantics:
            prim_list += stage_usdrt.GetPrimsWithAppliedAPIName(["SemanticsAPI", "SemanticsLabelsAPI"])
        else:
            prim_list = stage_usdrt.Traverse()
    else:
        prim_list = stage.Traverse()

    for prim in prim_list:
        if isinstance(prim, (pxr.Usd.Prim, usdrt.Usd.Prim)):
            prim_path = str(prim.GetPath())
        else:
            prim_path = str(prim)
            prim = stage_usdrt.GetPrimAtPath(prim)
        prim_type = str(prim.GetTypeName()).lower()
        prim_semantics = None

        if path_match:
            if ignore_case:
                if path_match.lower() not in prim_path.lower():
                    continue
            else:
                if path_match not in prim_path:
                    continue
        if path_pattern:
            if not path_pattern_regex.search(prim_path):
                continue
        if path_pattern_exclusion:
            if path_exclusion_regex.search(prim_path):
                continue
        if prim_types:
            if prim_type not in prim_types:
                continue
        if prim_types_exclusion:
            if prim_type in prim_types_exclusion:
                continue
        if semantics:
            if prim_semantics is None:
                prim_semantics = utils.legacy_semantics_arg_to_new(utils.parse_semantics(prim))
            if prim_semantics is None:
                continue
            if not any((any(pv in v for pv in prim_semantics.get(k, [])) for k, v in semantics.items())):
                continue
        if semantics_exclusion:
            if prim_semantics is None:
                prim_semantics = utils.legacy_semantics_arg_to_new(utils.parse_semantics(prim))
            if prim_semantics is None:
                continue
            if any([prim_semantic in semantics_exclusion for prim_semantic in prim_semantics]):
                continue

        gathered_prims.append(prim)
    return gathered_prims


def prims(
    stage: Union[pxr.Usd.Stage, usdrt.Usd.Stage],
    path_pattern: str = None,
    path_match: str = None,
    path_pattern_exclusion: str = None,
    prim_types: List[str] = None,
    prim_types_exclusion: List[str] = None,
    semantics: List[str] = None,
    semantics_exclusion: List[str] = None,
    ignore_case: bool = False,
) -> List[pxr.Usd.Prim]:
    return _get_prims(
        stage,
        path_pattern,
        path_match,
        path_pattern_exclusion,
        prim_types,
        prim_types_exclusion,
        semantics,
        semantics_exclusion,
        ignore_case,
    )


def camera(
    stage: Union[pxr.Usd.Stage, usdrt.Usd.Stage],
    path_pattern: str = None,
    path_pattern_exclusion: str = None,
    semantics: Union[List[Tuple[str, str]], Tuple[str, str]] = None,
    semantics_exclusion: Union[List[Tuple[str, str]], Tuple[str, str]] = None,
    path_match: str = None,
    ignore_case: bool = False,
) -> List[pxr.Usd.Prim]:
    """Get Usd 'camera' types based on specified constraints.

    Args:
        stage: The stage to get the material types from.
        path_pattern: The RegEx (Regular Expression) path pattern to match.
        path_pattern_exclusion: The RegEx (Regular Expression) path pattern to ignore.
        semantics: Semantic type-value pairs of semantics to include
        semantics_exclusion: Semantic type-value pairs of semantics to ignore
        cache_result: Run get prims a single time, then return the cached result
        path_match: Python string matching.  Faster than regex matching.
    """
    return _get_prims(
        stage=stage,
        prim_types=["camera"],
        path_pattern=path_pattern,
        path_pattern_exclusion=path_pattern_exclusion,
        semantics=semantics,
        semantics_exclusion=semantics_exclusion,
        path_match=path_match,
        ignore_case=ignore_case,
    )


def curve(
    stage: Union[pxr.Usd.Stage, usdrt.Usd.Stage],
    path_pattern: str = None,
    path_pattern_exclusion: str = None,
    semantics: Union[List[Tuple[str, str]], Tuple[str, str]] = None,
    semantics_exclusion: Union[List[Tuple[str, str]], Tuple[str, str]] = None,
    path_match: str = None,
    ignore_case: bool = False,
) -> List[pxr.Usd.Prim]:
    """Get Usd 'curve' types based on specified constraints.

    Args:
        stage: The stage to get the material types from.
        path_pattern: The RegEx (Regular Expression) path pattern to match.
        path_pattern_exclusion: The RegEx (Regular Expression) path pattern to ignore.
        semantics: Semantic type-value pairs of semantics to include
        semantics_exclusion: Semantic type-value pairs of semantics to ignore
        cache_result: Run get prims a single time, then return the cached result
        path_match: Python string matching.  Faster than regex matching.
    """
    return _get_prims(
        stage=stage,
        prim_types=["curve"],
        path_pattern=path_pattern,
        path_pattern_exclusion=path_pattern_exclusion,
        semantics=semantics,
        semantics_exclusion=semantics_exclusion,
        path_match=path_match,
        ignore_case=ignore_case,
    )


def geomsubset(
    stage: Union[pxr.Usd.Stage, usdrt.Usd.Stage],
    path_pattern: str = None,
    path_pattern_exclusion: str = None,
    semantics: Union[List[Tuple[str, str]], Tuple[str, str]] = None,
    semantics_exclusion: Union[List[Tuple[str, str]], Tuple[str, str]] = None,
    path_match: str = None,
    ignore_case: bool = False,
) -> List[pxr.Usd.Prim]:
    """Get Usd 'geomsubset' types based on specified constraints.

    Args:
        stage: The stage to get the material types from.
        path_pattern: The RegEx (Regular Expression) path pattern to match.
        path_pattern_exclusion: The RegEx (Regular Expression) path pattern to ignore.
        semantics: Semantic type-value pairs of semantics to include
        semantics_exclusion: Semantic type-value pairs of semantics to ignore
        cache_result: Run get prims a single time, then return the cached result
        path_match: Python string matching.  Faster than regex matching.
    """
    return _get_prims(
        stage=stage,
        prim_types=["geomsubset"],
        path_pattern=path_pattern,
        path_pattern_exclusion=path_pattern_exclusion,
        semantics=semantics,
        semantics_exclusion=semantics_exclusion,
        path_match=path_match,
        ignore_case=ignore_case,
    )


def graph(
    stage: Union[pxr.Usd.Stage, usdrt.Usd.Stage],
    path_pattern: str = None,
    path_pattern_exclusion: str = None,
    semantics: Union[List[Tuple[str, str]], Tuple[str, str]] = None,
    semantics_exclusion: Union[List[Tuple[str, str]], Tuple[str, str]] = None,
    path_match: str = None,
    ignore_case: bool = False,
) -> List[pxr.Usd.Prim]:
    """Get all 'graph' types based on specified constraints.

    Args:
        stage: The stage to get the material types from.
        path_pattern: The RegEx (Regular Expression) path pattern to match.
        path_pattern_exclusion: The RegEx (Regular Expression) path pattern to ignore.
        semantics: Semantic type-value pairs of semantics to include
        semantics_exclusion: Semantic type-value pairs of semantics to ignore
        cache_result: Run get prims a single time, then return the cached result
        path_match: Python string matching.  Faster than regex matching.
    """
    return _get_prims(
        stage=stage,
        prim_types=["graph"],
        path_pattern=path_pattern,
        path_pattern_exclusion=path_pattern_exclusion,
        semantics=semantics,
        semantics_exclusion=semantics_exclusion,
        path_match=path_match,
        ignore_case=ignore_case,
    )


def light(
    stage: Union[pxr.Usd.Stage, usdrt.Usd.Stage],
    path_pattern: str = None,
    path_pattern_exclusion: str = None,
    semantics: Union[List[Tuple[str, str]], Tuple[str, str]] = None,
    semantics_exclusion: Union[List[Tuple[str, str]], Tuple[str, str]] = None,
    path_match: str = None,
    ignore_case: bool = False,
) -> List[pxr.Usd.Prim]:
    """Get Usd 'light' types based on specified constraints.
       Matches types RectLight, SphereLight, CylinderLight, DiskLight, DistantLight, SphereLight

    Args:
        stage: The stage to get the material types from.
        path_pattern: The RegEx (Regular Expression) path pattern to match.
        path_pattern_exclusion: The RegEx (Regular Expression) path pattern to ignore.
        semantics: Semantic type-value pairs of semantics to include
        semantics_exclusion: Semantic type-value pairs of semantics to ignore
        cache_result: Run get prims a single time, then return the cached result
        path_match: Python string matching.  Faster than regex matching.
    """
    return _get_prims(
        stage=stage,
        prim_types=["cylinderlight", "disklight", "distantlight", "domelight", "rectlight", "spherelight"],
        path_pattern=path_pattern,
        path_pattern_exclusion=path_pattern_exclusion,
        semantics=semantics,
        semantics_exclusion=semantics_exclusion,
        path_match=path_match,
        ignore_case=ignore_case,
    )


def listener(
    stage: Union[pxr.Usd.Stage, usdrt.Usd.Stage],
    path_pattern: str = None,
    path_pattern_exclusion: str = None,
    semantics: Union[List[Tuple[str, str]], Tuple[str, str]] = None,
    semantics_exclusion: Union[List[Tuple[str, str]], Tuple[str, str]] = None,
    path_match: str = None,
    ignore_case: bool = False,
) -> List[pxr.Usd.Prim]:
    """Get Usd listener types based on specified constraints.

    Args:
        stage: The stage to get the material types from.
        path_pattern: The RegEx (Regular Expression) path pattern to match.
        path_pattern_exclusion: The RegEx (Regular Expression) path pattern to ignore.
        semantics: Semantic type-value pairs of semantics to include
        semantics_exclusion: Semantic type-value pairs of semantics to ignore
        cache_result: Run get prims a single time, then return the cached result
        path_match: Python string matching.  Faster than regex matching.
    """
    return _get_prims(
        stage=stage,
        prim_types=["listener"],
        path_pattern=path_pattern,
        path_pattern_exclusion=path_pattern_exclusion,
        semantics=semantics,
        semantics_exclusion=semantics_exclusion,
        path_match=path_match,
        ignore_case=ignore_case,
    )


def material(
    stage: Union[pxr.Usd.Stage, usdrt.Usd.Stage],
    path_pattern: str = None,
    path_pattern_exclusion: str = None,
    semantics: Union[List[Tuple[str, str]], Tuple[str, str]] = None,
    semantics_exclusion: Union[List[Tuple[str, str]], Tuple[str, str]] = None,
    path_match: str = None,
    ignore_case: bool = False,
) -> List[pxr.Usd.Prim]:
    """Get Usd material types based on specified constraints.

    Args:
        stage: The stage to get the material types from.
        path_pattern: The RegEx (Regular Expression) path pattern to match.
        path_pattern_exclusion: The RegEx (Regular Expression) path pattern to ignore.
        semantics: Semantic type-value pairs of semantics to include
        semantics_exclusion: Semantic type-value pairs of semantics to ignore
        cache_result: Run get prims a single time, then return the cached result
        path_match: Python string matching.  Faster than regex matching.
    """
    return _get_prims(
        stage=stage,
        prim_types=["material"],
        path_pattern=path_pattern,
        path_pattern_exclusion=path_pattern_exclusion,
        semantics=semantics,
        semantics_exclusion=semantics_exclusion,
        path_match=path_match,
        ignore_case=ignore_case,
    )


def mesh(
    stage: Union[pxr.Usd.Stage, usdrt.Usd.Stage],
    path_pattern: str = None,
    path_pattern_exclusion: str = None,
    semantics: Union[List[Tuple[str, str]], Tuple[str, str]] = None,
    semantics_exclusion: Union[List[Tuple[str, str]], Tuple[str, str]] = None,
    path_match: str = None,
    ignore_case: bool = False,
) -> List[pxr.Usd.Prim]:
    """Get Usd mesh types based on specified constraints.

    Args:
        stage: The stage to get the material types from.
        path_pattern: The RegEx (Regular Expression) path pattern to match.
        path_pattern_exclusion: The RegEx (Regular Expression) path pattern to ignore.
        semantics: Semantic type-value pairs of semantics to include
        semantics_exclusion: Semantic type-value pairs of semantics to ignore
        cache_result: Run get prims a single time, then return the cached result
        path_match: Python string matching.  Faster than regex matching.
    """
    return _get_prims(
        stage=stage,
        prim_types=["mesh"],
        path_pattern=path_pattern,
        path_pattern_exclusion=path_pattern_exclusion,
        semantics=semantics,
        semantics_exclusion=semantics_exclusion,
        path_match=path_match,
        ignore_case=ignore_case,
    )


def physics(
    stage: Union[pxr.Usd.Stage, usdrt.Usd.Stage],
    path_pattern: str = None,
    path_pattern_exclusion: str = None,
    semantics: Union[List[Tuple[str, str]], Tuple[str, str]] = None,
    semantics_exclusion: Union[List[Tuple[str, str]], Tuple[str, str]] = None,
    path_match: str = None,
    ignore_case: bool = False,
) -> List[pxr.Usd.Prim]:
    """Get physics/physicsscene types based on specified constraints.

    Args:
        stage: The stage to get the material types from.
        path_pattern: The RegEx (Regular Expression) path pattern to match.
        path_pattern_exclusion: The RegEx (Regular Expression) path pattern to ignore.
        semantics: Semantic type-value pairs of semantics to include
        semantics_exclusion: Semantic type-value pairs of semantics to ignore
        cache_result: Run get prims a single time, then return the cached result
        path_match: Python string matching.  Faster than regex matching.
    """
    return _get_prims(
        stage=stage,
        prim_types=["physics"],
        path_pattern=path_pattern,
        path_pattern_exclusion=path_pattern_exclusion,
        semantics=semantics,
        semantics_exclusion=semantics_exclusion,
        path_match=path_match,
        ignore_case=ignore_case,
    )


def renderproduct(
    stage: Union[pxr.Usd.Stage, usdrt.Usd.Stage],
    path_pattern: str = None,
    path_pattern_exclusion: str = None,
    semantics: Union[List[Tuple[str, str]], Tuple[str, str]] = None,
    semantics_exclusion: Union[List[Tuple[str, str]], Tuple[str, str]] = None,
    path_match: str = None,
    ignore_case: bool = False,
) -> List[pxr.Usd.Prim]:
    """Get Usd renderproduct types based on specified constraints.

    Args:
        stage: The stage to get the material types from.
        path_pattern: The RegEx (Regular Expression) path pattern to match.
        path_pattern_exclusion: The RegEx (Regular Expression) path pattern to ignore.
        semantics: Semantic type-value pairs of semantics to include
        semantics_exclusion: Semantic type-value pairs of semantics to ignore
        cache_result: Run get prims a single time, then return the cached result
        path_match: Python string matching.  Faster than regex matching.
    """
    return _get_prims(
        stage=stage,
        prim_types=["renderproduct"],
        path_pattern=path_pattern,
        path_pattern_exclusion=path_pattern_exclusion,
        semantics=semantics,
        semantics_exclusion=semantics_exclusion,
        path_match=path_match,
        ignore_case=ignore_case,
    )


def rendervar(
    stage: Union[pxr.Usd.Stage, usdrt.Usd.Stage],
    path_pattern: str = None,
    path_pattern_exclusion: str = None,
    semantics: Union[List[Tuple[str, str]], Tuple[str, str]] = None,
    semantics_exclusion: Union[List[Tuple[str, str]], Tuple[str, str]] = None,
    path_match: str = None,
    ignore_case: bool = False,
) -> List[pxr.Usd.Prim]:
    """Get Usd rendervar types based on specified constraints.

    Args:
        stage: The stage to get the material types from.
        path_pattern: The RegEx (Regular Expression) path pattern to match.
        path_pattern_exclusion: The RegEx (Regular Expression) path pattern to ignore.
        semantics: Semantic type-value pairs of semantics to include
        semantics_exclusion: Semantic type-value pairs of semantics to ignore
        cache_result: Run get prims a single time, then return the cached result
        path_match: Python string matching.  Faster than regex matching.
    """
    return _get_prims(
        stage=stage,
        prim_types=["rendervar"],
        path_pattern=path_pattern,
        path_pattern_exclusion=path_pattern_exclusion,
        semantics=semantics,
        semantics_exclusion=semantics_exclusion,
        path_match=path_match,
        ignore_case=ignore_case,
    )


def scope(
    stage: Union[pxr.Usd.Stage, usdrt.Usd.Stage],
    path_pattern: str = None,
    path_pattern_exclusion: str = None,
    semantics: Union[List[Tuple[str, str]], Tuple[str, str]] = None,
    semantics_exclusion: Union[List[Tuple[str, str]], Tuple[str, str]] = None,
    path_match: str = None,
    ignore_case: bool = False,
) -> List[pxr.Usd.Prim]:
    """Get Usd 'scope' types based on specified constraints.

    Args:
        stage: The stage to get the material types from.
        path_pattern: The RegEx (Regular Expression) path pattern to match.
        path_pattern_exclusion: The RegEx (Regular Expression) path pattern to ignore.
        semantics: Semantic type-value pairs of semantics to include
        semantics_exclusion: Semantic type-value pairs of semantics to ignore
        cache_result: Run get prims a single time, then return the cached result
        path_match: Python string matching.  Faster than regex matching.
    """
    return _get_prims(
        stage=stage,
        prim_types=["scope"],
        path_pattern=path_pattern,
        path_pattern_exclusion=path_pattern_exclusion,
        semantics=semantics,
        semantics_exclusion=semantics_exclusion,
        path_match=path_match,
        ignore_case=ignore_case,
    )


def shader(
    stage: Union[pxr.Usd.Stage, usdrt.Usd.Stage],
    path_pattern: str = None,
    path_pattern_exclusion: str = None,
    semantics: Union[List[Tuple[str, str]], Tuple[str, str]] = None,
    semantics_exclusion: Union[List[Tuple[str, str]], Tuple[str, str]] = None,
    path_match: str = None,
    ignore_case: bool = False,
) -> List[pxr.Usd.Prim]:
    """Get Usd 'shader' types based on specified constraints.

    Args:
        stage: The stage to get the material types from.
        path_pattern: The RegEx (Regular Expression) path pattern to match.
        path_pattern_exclusion: The RegEx (Regular Expression) path pattern to ignore.
        semantics: Semantic type-value pairs of semantics to include
        semantics_exclusion: Semantic type-value pairs of semantics to ignore
        cache_result: Run get prims a single time, then return the cached result
        path_match: Python string matching.  Faster than regex matching.
    """
    return _get_prims(
        stage=stage,
        prim_types=["shader"],
        path_pattern=path_pattern,
        path_pattern_exclusion=path_pattern_exclusion,
        semantics=semantics,
        semantics_exclusion=semantics_exclusion,
        path_match=path_match,
        ignore_case=ignore_case,
    )


def shape(
    stage: Union[pxr.Usd.Stage, usdrt.Usd.Stage],
    path_pattern: str = None,
    path_pattern_exclusion: str = None,
    semantics: Union[List[Tuple[str, str]], Tuple[str, str]] = None,
    semantics_exclusion: Union[List[Tuple[str, str]], Tuple[str, str]] = None,
    path_match: str = None,
    ignore_case: bool = False,
) -> List[pxr.Usd.Prim]:
    """Get Usd 'shape' types based on specified constraints.
       Includes Capsule, Cone, Cube, Cylinder, Plane, Sphere

    Args:
        stage: The stage to get the material types from.
        path_pattern: The RegEx (Regular Expression) path pattern to match.
        path_pattern_exclusion: The RegEx (Regular Expression) path pattern to ignore.
        semantics: Semantic type-value pairs of semantics to include
        semantics_exclusion: Semantic type-value pairs of semantics to ignore
        cache_result: Run get prims a single time, then return the cached result
        path_match: Python string matching.  Faster than regex matching.
    """
    return _get_prims(
        stage=stage,
        prim_types=["capsule", "cone", "cube", "cylinder", "plane", "sphere"],
        path_pattern=path_pattern,
        path_pattern_exclusion=path_pattern_exclusion,
        semantics=semantics,
        semantics_exclusion=semantics_exclusion,
        path_match=path_match,
        ignore_case=ignore_case,
    )


def sound(
    stage: Union[pxr.Usd.Stage, usdrt.Usd.Stage],
    path_pattern: str = None,
    path_pattern_exclusion: str = None,
    semantics: Union[List[Tuple[str, str]], Tuple[str, str]] = None,
    semantics_exclusion: Union[List[Tuple[str, str]], Tuple[str, str]] = None,
    path_match: str = None,
    ignore_case: bool = False,
) -> List[pxr.Usd.Prim]:
    """Get Usd 'sound' types based on specified constraints.

    Args:
        stage: The stage to get the material types from.
        path_pattern: The RegEx (Regular Expression) path pattern to match.
        path_pattern_exclusion: The RegEx (Regular Expression) path pattern to ignore.
        semantics: Semantic type-value pairs of semantics to include
        semantics_exclusion: Semantic type-value pairs of semantics to ignore
        cache_result: Run get prims a single time, then return the cached result
        path_match: Python string matching.  Faster than regex matching.
    """
    return _get_prims(
        stage=stage,
        prim_types=["sound"],
        path_pattern=path_pattern,
        path_pattern_exclusion=path_pattern_exclusion,
        semantics=semantics,
        semantics_exclusion=semantics_exclusion,
        path_match=path_match,
        ignore_case=ignore_case,
    )


def xform(
    stage: Union[pxr.Usd.Stage, usdrt.Usd.Stage],
    path_pattern: str = None,
    path_pattern_exclusion: str = None,
    semantics: Union[List[Tuple[str, str]], Tuple[str, str]] = None,
    semantics_exclusion: Union[List[Tuple[str, str]], Tuple[str, str]] = None,
    path_match: str = None,
    ignore_case: bool = False,
) -> List[pxr.Usd.Prim]:
    """Get Usd 'xform' types based on specified constraints.

    Args:
        stage: The stage to get the material types from.
        path_pattern: The RegEx (Regular Expression) path pattern to match.
        path_pattern_exclusion: The RegEx (Regular Expression) path pattern to ignore.
        semantics: Semantic type-value pairs of semantics to include
        semantics_exclusion: Semantic type-value pairs of semantics to ignore
        cache_result: Run get prims a single time, then return the cached result
        path_match: Python string matching.  Faster than regex matching.
    """
    return _get_prims(
        stage=stage,
        prim_types=["xform"],
        path_pattern=path_pattern,
        path_pattern_exclusion=path_pattern_exclusion,
        semantics=semantics,
        semantics_exclusion=semantics_exclusion,
        path_match=path_match,
        ignore_case=ignore_case,
    )


def skelanimation(
    stage: Union[pxr.Usd.Stage, usdrt.Usd.Stage],
    path_pattern: str = None,
    path_pattern_exclusion: str = None,
    semantics: Union[List[Tuple[str, str]], Tuple[str, str]] = None,
    semantics_exclusion: Union[List[Tuple[str, str]], Tuple[str, str]] = None,
    path_match: str = None,
    ignore_case: bool = False,
) -> List[pxr.Usd.Prim]:
    """Get Usd 'skelanimation' types based on specified constraints.

    Args:
        stage: The stage to get the material types from.
        path_pattern: The RegEx (Regular Expression) path pattern to match.
        path_pattern_exclusion: The RegEx (Regular Expression) path pattern to ignore.
        semantics: Semantic type-value pairs of semantics to include
        semantics_exclusion: Semantic type-value pairs of semantics to ignore
        cache_result: Run get prims a single time, then return the cached result
        path_match: Python string matching.  Faster than regex matching.
    """
    return _get_prims(
        stage=stage,
        prim_types=["skelanimation"],
        path_pattern=path_pattern,
        path_pattern_exclusion=path_pattern_exclusion,
        semantics=semantics,
        semantics_exclusion=semantics_exclusion,
        path_match=path_match,
        ignore_case=ignore_case,
    )


def skeleton(
    stage: Union[pxr.Usd.Stage, usdrt.Usd.Stage],
    path_pattern: str = None,
    path_pattern_exclusion: str = None,
    semantics: Union[List[Tuple[str, str]], Tuple[str, str]] = None,
    semantics_exclusion: Union[List[Tuple[str, str]], Tuple[str, str]] = None,
    path_match: str = None,
    ignore_case: bool = False,
) -> List[pxr.Usd.Prim]:
    """Get Usd 'skeleton' types based on specified constraints.

    Args:
        stage: The stage to get the material types from.
        path_pattern: The RegEx (Regular Expression) path pattern to match.
        path_pattern_exclusion: The RegEx (Regular Expression) path pattern to ignore.
        semantics: Semantic type-value pairs of semantics to include
        semantics_exclusion: Semantic type-value pairs of semantics to ignore
        cache_result: Run get prims a single time, then return the cached result
        path_match: Python string matching.  Faster than regex matching.
    """
    return _get_prims(
        stage=stage,
        prim_types=["skeleton"],
        path_pattern=path_pattern,
        path_pattern_exclusion=path_pattern_exclusion,
        semantics=semantics,
        semantics_exclusion=semantics_exclusion,
        path_match=path_match,
        ignore_case=ignore_case,
    )


def prim_at_paths(
    stage: Union[pxr.Usd.Stage, usdrt.Usd.Stage],
    paths: Union[str, List[str]],
) -> List[pxr.Usd.Prim]:
    """Get the prim at the exact path


    Args:
        stage: The stage to get the material types from.
        path: USD path to the desired prim. Defaults to None.
    """
    if isinstance(paths, (str, pxr.Sdf.Path, usdrt.Sdf.Path)):
        return [stage.GetPrimAtPath(str(paths))]
    elif isinstance(paths, (list, tuple)):
        return [stage.GetPrimAtPath(str(p)) for p in paths]
    else:
        raise TypeError(f"Expect path to be either str or list of str or ReplicatorItem, but got {type(paths)}")
