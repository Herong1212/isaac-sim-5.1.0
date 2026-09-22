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

import sys
from typing import Callable, List, Optional, Tuple, Union

import omni.graph.core as og
import usdrt
from pxr import Gf, Sdf

from .utils import ReplicatorItem, ReplicatorWrapper, create_node, utils


def register(func: Callable[..., Union[ReplicatorItem, og.Node]], override: bool = True, fn_name: str = None) -> None:
    """Register a new function under ``omni.replicator.core.get``.
    Extend the default capabilities of ``omni.replicator.core.get`` by registering new functionality. New functions
    must return a ``ReplicatorItem`` or an ``OmniGraph`` node.

    Args:
        func: A function that returns a ``ReplicatorItem`` or an ``OmniGraph`` node.
        override: If ``True``, will override existing functions of the same name. If ``False``, an error is raised.
        fn_name: Optional arg that let user choose the function name when registering it in replicator. If not
            specified, the function name is used. ``fn_name`` must follow valid [Python identifier rules]
            (https://docs.python.org/3.10/reference/lexical_analysis.html#identifiers)

    """
    if fn_name is None:
        fn_name = func.__name__

    if not fn_name.isidentifier():
        raise ValueError(
            f"The function name {fn_name} is not a valid Python identifier. fn_name must only contains alphanumeric "
            "letters (a-z), numbers (0-9) or underscores (_) and cannot start with a number or contain any spaces."
        )

    module = sys.modules[__name__]
    if fn_name in dir(module):
        if override:
            print(f"Overriding function {{{fn_name}}} for replicator.get.")
        else:
            raise ValueError()

    wrapped_fn = ReplicatorWrapper(func)
    setattr(sys.modules[__name__], fn_name, wrapped_fn)


@ReplicatorWrapper
def prims(
    path_pattern: str = None,
    path_match: str = None,
    path_pattern_exclusion: str = None,
    prim_types: Union[str, List[str]] = None,
    prim_types_exclusion: Union[str, List[str]] = None,
    semantics: Union[List[Tuple[str, str]], Tuple[str, str]] = None,
    semantics_exclusion: Union[List[Tuple[str, str]], Tuple[str, str]] = None,
    cache_result: bool = True,
    ignore_case: bool = True,
    name: Optional[str] = None,
) -> ReplicatorItem:
    """Get prims based on specified constraints.

    Search the stage for stage paths with matches to the specified constraints.

    Args:
        path_pattern: The RegEx (Regular Expression) path pattern to match.
        path_match: Python string matching.  Faster than regex matching.
        path_pattern_exclusion: The RegEx (Regular Expression) path pattern to ignore.
        prim_types: List of prim types to include
        prim_types_exclusion: List of prim types to ignore
        semantics: Semantic type-value pairs of semantics to include
        semantics_exclusion: Semantic type-value pairs of semantics to ignore
        cache_result: Run get prims a single time, then return the cached result
        ignore_case: Case-insensitive regex matching
        name (optional): A name for the graph node.
    """
    if isinstance(semantics, tuple):
        semantics = [semantics]
    if isinstance(semantics_exclusion, tuple):
        semantics_exclusion = [semantics_exclusion]

    return create_node(
        "omni.replicator.core.OgnGetPrims",
        pathPattern=path_pattern,
        pathMatch=path_match,
        pathPatternExclusion=path_pattern_exclusion,
        primTypes=prim_types,
        primTypesExclusion=prim_types_exclusion,
        semantics=[",".join(s) for s in semantics] if semantics else [],
        semanticsExclusion=[",".join(s) for s in semantics_exclusion] if semantics_exclusion else [],
        cachePrims=cache_result,
        ignoreCase=ignore_case,
        node_name=name,
    )


@ReplicatorWrapper
def camera(
    path_pattern: str = None,
    path_pattern_exclusion: str = None,
    semantics: Union[List[Tuple[str, str]], Tuple[str, str]] = None,
    semantics_exclusion: Union[List[Tuple[str, str]], Tuple[str, str]] = None,
    cache_result: bool = True,
    name: Optional[str] = None,
    path_match: str = None,
) -> ReplicatorItem:
    """Get Usd 'Camera' types based on specified constraints.

    Args:
        path_pattern: The RegEx (Regular Expression) path pattern to match.
        path_pattern_exclusion: The RegEx (Regular Expression) path pattern to ignore.
        semantics: Semantic type-value pairs of semantics to include
        semantics_exclusion: Semantic type-value pairs of semantics to ignore
        cache_result: Run get prims a single time, then return the cached result
        name (optional): A name for the graph node.
        path_match: Python string matching.  Faster than regex matching.
    """
    return prims(
        prim_types=["Camera"],
        path_pattern=path_pattern,
        path_pattern_exclusion=path_pattern_exclusion,
        semantics=semantics,
        semantics_exclusion=semantics_exclusion,
        cache_result=cache_result,
        name=name,
        path_match=path_match,
    )


@ReplicatorWrapper
def curve(
    path_pattern: str = None,
    path_pattern_exclusion: str = None,
    semantics: Union[List[Tuple[str, str]], Tuple[str, str]] = None,
    semantics_exclusion: Union[List[Tuple[str, str]], Tuple[str, str]] = None,
    cache_result: bool = True,
    name: Optional[str] = None,
    path_match: str = None,
) -> ReplicatorItem:
    """Get Usd 'Curve' types based on specified constraints.

    Args:
        path_pattern: The RegEx (Regular Expression) path pattern to match.
        path_pattern_exclusion: The RegEx (Regular Expression) path pattern to ignore.
        semantics: Semantic type-value pairs of semantics to include
        semantics_exclusion: Semantic type-value pairs of semantics to ignore
        cache_result: Run get prims a single time, then return the cached result
        name (optional): A name for the graph node.
        path_match: Python string matching.  Faster than regex matching.
    """
    return prims(
        prim_types=["Curve"],
        path_pattern=path_pattern,
        path_pattern_exclusion=path_pattern_exclusion,
        semantics=semantics,
        semantics_exclusion=semantics_exclusion,
        cache_result=cache_result,
        name=name,
        path_match=path_match,
    )


@ReplicatorWrapper
def geomsubset(
    path_pattern: str = None,
    path_pattern_exclusion: str = None,
    semantics: Union[List[Tuple[str, str]], Tuple[str, str]] = None,
    semantics_exclusion: Union[List[Tuple[str, str]], Tuple[str, str]] = None,
    cache_result: bool = True,
    name: Optional[str] = None,
    path_match: str = None,
) -> ReplicatorItem:
    """Get Usd 'GeomSubset' types based on specified constraints.

    Args:
        path_pattern: The RegEx (Regular Expression) path pattern to match.
        path_pattern_exclusion: The RegEx (Regular Expression) path pattern to ignore.
        semantics: Semantic type-value pairs of semantics to include
        semantics_exclusion: Semantic type-value pairs of semantics to ignore
        cache_result: Run get prims a single time, then return the cached result
        name (optional): A name for the graph node.
        path_match: Python string matching.  Faster than regex matching.
    """
    return prims(
        prim_types=["GeomSubset"],
        path_pattern=path_pattern,
        path_pattern_exclusion=path_pattern_exclusion,
        semantics=semantics,
        semantics_exclusion=semantics_exclusion,
        cache_result=cache_result,
        name=name,
        path_match=path_match,
    )


@ReplicatorWrapper
def graph(
    path_pattern: str = None,
    path_pattern_exclusion: str = None,
    semantics: Union[List[Tuple[str, str]], Tuple[str, str]] = None,
    semantics_exclusion: Union[List[Tuple[str, str]], Tuple[str, str]] = None,
    cache_result: bool = True,
    name: Optional[str] = None,
    path_match: str = None,
) -> ReplicatorItem:
    """Get all 'Graph' types based on specified constraints.

    Args:
        path_pattern: The RegEx (Regular Expression) path pattern to match.
        path_pattern_exclusion: The RegEx (Regular Expression) path pattern to ignore.
        semantics: Semantic type-value pairs of semantics to include
        semantics_exclusion: Semantic type-value pairs of semantics to ignore
        cache_result: Run get prims a single time, then return the cached result
        name (optional): A name for the graph node.
        path_match: Python string matching.  Faster than regex matching.
    """
    return prims(
        prim_types=["Graph"],
        path_pattern=path_pattern,
        path_pattern_exclusion=path_pattern_exclusion,
        semantics=semantics,
        semantics_exclusion=semantics_exclusion,
        cache_result=cache_result,
        name=name,
        path_match=path_match,
    )


@ReplicatorWrapper
def light(
    path_pattern: str = None,
    path_pattern_exclusion: str = None,
    semantics: Union[List[Tuple[str, str]], Tuple[str, str]] = None,
    semantics_exclusion: Union[List[Tuple[str, str]], Tuple[str, str]] = None,
    cache_result: bool = True,
    name: Optional[str] = None,
    path_match: str = None,
) -> ReplicatorItem:
    """Get Usd 'light' types based on specified constraints.
       Matches types RectLight, SphereLight, CylinderLight, DiskLight, DistantLight, SphereLight

    Args:
        path_pattern: The RegEx (Regular Expression) path pattern to match.
        path_pattern_exclusion: The RegEx (Regular Expression) path pattern to ignore.
        semantics: Semantic type-value pairs of semantics to include
        semantics_exclusion: Semantic type-value pairs of semantics to ignore
        cache_result: Run get prims a single time, then return the cached result
        name (optional): A name for the graph node.
        path_match: Python string matching.  Faster than regex matching.
    """
    return prims(
        prim_types=["CylinderLight", "DiskLight", "DistantLight", "DomeLight", "RectLight", "SphereLight"],
        path_pattern=path_pattern,
        path_pattern_exclusion=path_pattern_exclusion,
        semantics=semantics,
        semantics_exclusion=semantics_exclusion,
        cache_result=cache_result,
        name=name,
        path_match=path_match,
    )


@ReplicatorWrapper
def listener(
    path_pattern: str = None,
    path_pattern_exclusion: str = None,
    semantics: Union[List[Tuple[str, str]], Tuple[str, str]] = None,
    semantics_exclusion: Union[List[Tuple[str, str]], Tuple[str, str]] = None,
    cache_result: bool = True,
    name: Optional[str] = None,
    path_match: str = None,
) -> ReplicatorItem:
    """Get Usd Listener types based on specified constraints.

    Args:
        path_pattern: The RegEx (Regular Expression) path pattern to match.
        path_pattern_exclusion: The RegEx (Regular Expression) path pattern to ignore.
        semantics: Semantic type-value pairs of semantics to include
        semantics_exclusion: Semantic type-value pairs of semantics to ignore
        cache_result: Run get prims a single time, then return the cached result
        name (optional): A name for the graph node.
        path_match: Python string matching.  Faster than regex matching.
    """
    return prims(
        prim_types=["Listener"],
        path_pattern=path_pattern,
        path_pattern_exclusion=path_pattern_exclusion,
        semantics=semantics,
        semantics_exclusion=semantics_exclusion,
        cache_result=cache_result,
        name=name,
        path_match=path_match,
    )


@ReplicatorWrapper
def material(
    path_pattern: str = None,
    path_pattern_exclusion: str = None,
    semantics: Union[List[Tuple[str, str]], Tuple[str, str]] = None,
    semantics_exclusion: Union[List[Tuple[str, str]], Tuple[str, str]] = None,
    cache_result: bool = True,
    name: Optional[str] = None,
    path_match: str = None,
) -> ReplicatorItem:
    """Get Usd Material types based on specified constraints.

    Args:
        path_pattern: The RegEx (Regular Expression) path pattern to match.
        path_pattern_exclusion: The RegEx (Regular Expression) path pattern to ignore.
        semantics: Semantic type-value pairs of semantics to include
        semantics_exclusion: Semantic type-value pairs of semantics to ignore
        cache_result: Run get prims a single time, then return the cached result
        name (optional): A name for the graph node.
        path_match: Python string matching.  Faster than regex matching.
    """
    return prims(
        prim_types=["Material"],
        path_pattern=path_pattern,
        path_pattern_exclusion=path_pattern_exclusion,
        semantics=semantics,
        semantics_exclusion=semantics_exclusion,
        cache_result=cache_result,
        name=name,
        path_match=path_match,
    )


@ReplicatorWrapper
def mesh(
    path_pattern: str = None,
    path_pattern_exclusion: str = None,
    semantics: Union[List[Tuple[str, str]], Tuple[str, str]] = None,
    semantics_exclusion: Union[List[Tuple[str, str]], Tuple[str, str]] = None,
    cache_result: bool = True,
    name: Optional[str] = None,
    path_match: str = None,
) -> ReplicatorItem:
    """Get Usd Mesh types based on specified constraints.

    Args:
        path_pattern: The RegEx (Regular Expression) path pattern to match.
        path_pattern_exclusion: The RegEx (Regular Expression) path pattern to ignore.
        semantics: Semantic type-value pairs of semantics to include
        semantics_exclusion: Semantic type-value pairs of semantics to ignore
        cache_result: Run get prims a single time, then return the cached result
        name (optional): A name for the graph node.
        path_match: Python string matching.  Faster than regex matching.
    """
    return prims(
        prim_types=["Mesh"],
        path_pattern=path_pattern,
        path_pattern_exclusion=path_pattern_exclusion,
        semantics=semantics,
        semantics_exclusion=semantics_exclusion,
        cache_result=cache_result,
        name=name,
        path_match=path_match,
    )


@ReplicatorWrapper
def physics(
    path_pattern: str = None,
    path_pattern_exclusion: str = None,
    semantics: Union[List[Tuple[str, str]], Tuple[str, str]] = None,
    semantics_exclusion: Union[List[Tuple[str, str]], Tuple[str, str]] = None,
    cache_result: bool = True,
    name: Optional[str] = None,
    path_match: str = None,
) -> ReplicatorItem:
    """Get Physics/PhysicsScene types based on specified constraints.

    Args:
        path_pattern: The RegEx (Regular Expression) path pattern to match.
        path_pattern_exclusion: The RegEx (Regular Expression) path pattern to ignore.
        semantics: Semantic type-value pairs of semantics to include
        semantics_exclusion: Semantic type-value pairs of semantics to ignore
        cache_result: Run get prims a single time, then return the cached result
        name (optional): A name for the graph node.
        path_match: Python string matching.  Faster than regex matching.
    """
    return prims(
        prim_types=["Physics"],
        path_pattern=path_pattern,
        path_pattern_exclusion=path_pattern_exclusion,
        semantics=semantics,
        semantics_exclusion=semantics_exclusion,
        cache_result=cache_result,
        name=name,
        path_match=path_match,
    )


@ReplicatorWrapper
def renderproduct(
    path_pattern: str = None,
    path_pattern_exclusion: str = None,
    semantics: Union[List[Tuple[str, str]], Tuple[str, str]] = None,
    semantics_exclusion: Union[List[Tuple[str, str]], Tuple[str, str]] = None,
    cache_result: bool = True,
    name: Optional[str] = None,
    path_match: str = None,
) -> ReplicatorItem:
    """Get Usd renderproduct types based on specified constraints.

    Args:
        path_pattern: The RegEx (Regular Expression) path pattern to match.
        path_pattern_exclusion: The RegEx (Regular Expression) path pattern to ignore.
        semantics: Semantic type-value pairs of semantics to include
        semantics_exclusion: Semantic type-value pairs of semantics to ignore
        cache_result: Run get prims a single time, then return the cached result
        name (optional): A name for the graph node.
        path_match: Python string matching.  Faster than regex matching.
    """
    return prims(
        prim_types=["RenderProduct"],
        path_pattern=path_pattern,
        path_pattern_exclusion=path_pattern_exclusion,
        semantics=semantics,
        semantics_exclusion=semantics_exclusion,
        cache_result=cache_result,
        name=name,
        path_match=path_match,
    )


@ReplicatorWrapper
def rendervar(
    path_pattern: str = None,
    path_pattern_exclusion: str = None,
    semantics: Union[List[Tuple[str, str]], Tuple[str, str]] = None,
    semantics_exclusion: Union[List[Tuple[str, str]], Tuple[str, str]] = None,
    cache_result: bool = True,
    name: Optional[str] = None,
    path_match: str = None,
) -> ReplicatorItem:
    """Get Usd RenderVar types based on specified constraints.

    Args:
        path_pattern: The RegEx (Regular Expression) path pattern to match.
        path_pattern_exclusion: The RegEx (Regular Expression) path pattern to ignore.
        semantics: Semantic type-value pairs of semantics to include
        semantics_exclusion: Semantic type-value pairs of semantics to ignore
        cache_result: Run get prims a single time, then return the cached result
        name (optional): A name for the graph node.
        path_match: Python string matching.  Faster than regex matching.
    """
    return prims(
        prim_types=["RenderVar"],
        path_pattern=path_pattern,
        path_pattern_exclusion=path_pattern_exclusion,
        semantics=semantics,
        semantics_exclusion=semantics_exclusion,
        cache_result=cache_result,
        name=name,
        path_match=path_match,
    )


@ReplicatorWrapper
def scope(
    path_pattern: str = None,
    path_pattern_exclusion: str = None,
    semantics: Union[List[Tuple[str, str]], Tuple[str, str]] = None,
    semantics_exclusion: Union[List[Tuple[str, str]], Tuple[str, str]] = None,
    cache_result: bool = True,
    name: Optional[str] = None,
    path_match: str = None,
) -> ReplicatorItem:
    """Get Usd 'Scope' types based on specified constraints.

    Args:
        path_pattern: The RegEx (Regular Expression) path pattern to match.
        path_pattern_exclusion: The RegEx (Regular Expression) path pattern to ignore.
        semantics: Semantic type-value pairs of semantics to include
        semantics_exclusion: Semantic type-value pairs of semantics to ignore
        cache_result: Run get prims a single time, then return the cached result
        name (optional): A name for the graph node.
        path_match: Python string matching.  Faster than regex matching.
    """
    return prims(
        prim_types=["Scope"],
        path_pattern=path_pattern,
        path_pattern_exclusion=path_pattern_exclusion,
        semantics=semantics,
        semantics_exclusion=semantics_exclusion,
        cache_result=cache_result,
        name=name,
        path_match=path_match,
    )


@ReplicatorWrapper
def shader(
    path_pattern: str = None,
    path_pattern_exclusion: str = None,
    semantics: Union[List[Tuple[str, str]], Tuple[str, str]] = None,
    semantics_exclusion: Union[List[Tuple[str, str]], Tuple[str, str]] = None,
    cache_result: bool = True,
    name: Optional[str] = None,
    path_match: str = None,
) -> ReplicatorItem:
    """Get Usd 'Shader' types based on specified constraints.

    Args:
        path_pattern: The RegEx (Regular Expression) path pattern to match.
        path_pattern_exclusion: The RegEx (Regular Expression) path pattern to ignore.
        semantics: Semantic type-value pairs of semantics to include
        semantics_exclusion: Semantic type-value pairs of semantics to ignore
        cache_result: Run get prims a single time, then return the cached result
        name (optional): A name for the graph node.
        path_match: Python string matching.  Faster than regex matching.
    """
    return prims(
        prim_types=["Shader"],
        path_pattern=path_pattern,
        path_pattern_exclusion=path_pattern_exclusion,
        semantics=semantics,
        semantics_exclusion=semantics_exclusion,
        cache_result=cache_result,
        name=name,
        path_match=path_match,
    )


@ReplicatorWrapper
def shape(
    path_pattern: str = None,
    path_pattern_exclusion: str = None,
    semantics: Union[List[Tuple[str, str]], Tuple[str, str]] = None,
    semantics_exclusion: Union[List[Tuple[str, str]], Tuple[str, str]] = None,
    cache_result: bool = True,
    name: Optional[str] = None,
    path_match: str = None,
) -> ReplicatorItem:
    """Get Usd 'shape' types based on specified constraints.
       Includes Capsule, Cone, Cube, Cylinder, Plane, Sphere

    Args:
        path_pattern: The RegEx (Regular Expression) path pattern to match.
        path_pattern_exclusion: The RegEx (Regular Expression) path pattern to ignore.
        semantics: Semantic type-value pairs of semantics to include
        semantics_exclusion: Semantic type-value pairs of semantics to ignore
        cache_result: Run get prims a single time, then return the cached result
        name (optional): A name for the graph node.
        path_match: Python string matching.  Faster than regex matching.
    """
    return prims(
        prim_types=["Capsule", "Cone", "Cube", "Cylinder", "Plane", "Sphere"],
        path_pattern=path_pattern,
        path_pattern_exclusion=path_pattern_exclusion,
        semantics=semantics,
        semantics_exclusion=semantics_exclusion,
        cache_result=cache_result,
        name=name,
        path_match=path_match,
    )


@ReplicatorWrapper
def sound(
    path_pattern: str = None,
    path_pattern_exclusion: str = None,
    semantics: Union[List[Tuple[str, str]], Tuple[str, str]] = None,
    semantics_exclusion: Union[List[Tuple[str, str]], Tuple[str, str]] = None,
    cache_result: bool = True,
    name: Optional[str] = None,
    path_match: str = None,
) -> ReplicatorItem:
    """Get Usd 'Sound' types based on specified constraints.

    Args:
        path_pattern: The RegEx (Regular Expression) path pattern to match.
        path_pattern_exclusion: The RegEx (Regular Expression) path pattern to ignore.
        semantics: Semantic type-value pairs of semantics to include
        semantics_exclusion: Semantic type-value pairs of semantics to ignore
        cache_result: Run get prims a single time, then return the cached result
        name (optional): A name for the graph node.
        path_match: Python string matching.  Faster than regex matching.
    """
    return prims(
        prim_types=["Sound"],
        path_pattern=path_pattern,
        path_pattern_exclusion=path_pattern_exclusion,
        semantics=semantics,
        semantics_exclusion=semantics_exclusion,
        cache_result=cache_result,
        name=name,
        path_match=path_match,
    )


@ReplicatorWrapper
def xform(
    path_pattern: str = None,
    path_pattern_exclusion: str = None,
    semantics: Union[List[Tuple[str, str]], Tuple[str, str]] = None,
    semantics_exclusion: Union[List[Tuple[str, str]], Tuple[str, str]] = None,
    cache_result: bool = True,
    name: Optional[str] = None,
    path_match: str = None,
) -> ReplicatorItem:
    """Get Usd 'Xform' types based on specified constraints.

    Args:
        path_pattern: The RegEx (Regular Expression) path pattern to match.
        path_pattern_exclusion: The RegEx (Regular Expression) path pattern to ignore.
        semantics: Semantic type-value pairs of semantics to include
        semantics_exclusion: Semantic type-value pairs of semantics to ignore
        cache_result: Run get prims a single time, then return the cached result
        name (optional): A name for the graph node.
        path_match: Python string matching.  Faster than regex matching.
    """
    return prims(
        prim_types=["Xform"],
        path_pattern=path_pattern,
        path_pattern_exclusion=path_pattern_exclusion,
        semantics=semantics,
        semantics_exclusion=semantics_exclusion,
        cache_result=cache_result,
        name=name,
        path_match=path_match,
    )


@ReplicatorWrapper
def skelanimation(
    path_pattern: str = None,
    path_pattern_exclusion: str = None,
    semantics: Union[List[Tuple[str, str]], Tuple[str, str]] = None,
    semantics_exclusion: Union[List[Tuple[str, str]], Tuple[str, str]] = None,
    cache_result: bool = True,
    name: Optional[str] = None,
    path_match: str = None,
) -> ReplicatorItem:
    """Get Usd 'SkelAnimation' types based on specified constraints.

    Args:
        path_pattern: The RegEx (Regular Expression) path pattern to match.
        path_pattern_exclusion: The RegEx (Regular Expression) path pattern to ignore.
        semantics: Semantic type-value pairs of semantics to include
        semantics_exclusion: Semantic type-value pairs of semantics to ignore
        cache_result: Run get prims a single time, then return the cached result
        name (optional): A name for the graph node.
        path_match: Python string matching.  Faster than regex matching.
    """
    return prims(
        prim_types=["SkelAnimation"],
        path_pattern=path_pattern,
        path_pattern_exclusion=path_pattern_exclusion,
        semantics=semantics,
        semantics_exclusion=semantics_exclusion,
        cache_result=cache_result,
        name=name,
        path_match=path_match,
    )


@ReplicatorWrapper
def skeleton(
    path_pattern: str = None,
    path_pattern_exclusion: str = None,
    semantics: Union[List[Tuple[str, str]], Tuple[str, str]] = None,
    semantics_exclusion: Union[List[Tuple[str, str]], Tuple[str, str]] = None,
    cache_result: bool = True,
    name: Optional[str] = None,
    path_match: str = None,
) -> ReplicatorItem:
    """Get Usd 'skeleton' types based on specified constraints.

    Args:
        path_pattern: The RegEx (Regular Expression) path pattern to match.
        path_pattern_exclusion: The RegEx (Regular Expression) path pattern to ignore.
        semantics: Semantic type-value pairs of semantics to include
        semantics_exclusion: Semantic type-value pairs of semantics to ignore
        cache_result: Run get prims a single time, then return the cached result
        name (optional): A name for the graph node.
        path_match: Python string matching.  Faster than regex matching.
    """
    return prims(
        prim_types=["Skeleton"],
        path_pattern=path_pattern,
        path_pattern_exclusion=path_pattern_exclusion,
        semantics=semantics,
        semantics_exclusion=semantics_exclusion,
        cache_result=cache_result,
        name=name,
        path_match=path_match,
    )


@ReplicatorWrapper
def prim_at_path(path: Union[str, List[str], ReplicatorItem], name: Optional[str] = None) -> ReplicatorItem:
    """Get the prim at the exact path


    Args:
        path: USD path to the desired prim. Defaults to None.
        name (optional): A name for the graph node.
    """
    node = create_node("omni.replicator.core.OgnGetPrimAtPath", node_name=name)

    if isinstance(path, ReplicatorItem):
        path.node.get_attribute("outputs:samples").connect(node.get_attribute("inputs:paths"), True)
    elif isinstance(path, (str, Sdf.Path, usdrt.Sdf.Path)):
        node.get_attribute("inputs:paths").set([str(path)])
    elif isinstance(path, (list, tuple)):
        node.get_attribute("inputs:paths").set(path)
    else:
        raise TypeError(f"Expect path to be either str or list of str or ReplicatorItem, but got {type(path)}")

    return node


@ReplicatorWrapper
def normalized_decal_position(
    bounds: Gf.Vec3d = (0, 0, 0),
    offset: float = 0.01,
    rotation: Gf.Vec3d = (0, 0, 0),
    input_prims: Union[ReplicatorItem, List[str]] = None,
):
    node = create_node(
        "omni.replicator.core.OgnNormalizeMeshBoundsPlacement", boundsVector=bounds, offset=offset, rotation=rotation
    )

    if input_prims:
        utils.set_target_prims(node, "inputs:prims", input_prims)

    return node
