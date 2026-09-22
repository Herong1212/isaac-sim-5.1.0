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
import omni.usd
import usdrt
from pxr import Sdf, Usd

from .orchestrator import _add_named_node
from .utils import ReplicatorItem, ReplicatorWrapper, create_node, set_target_prims
from .utils.rng import ReplicatorRNG
from .utils.utils import _setup_random_attribute


def _get_data_type(data_list):
    first_el = data_list[0]
    stride_length = 1
    if isinstance(first_el, (list, tuple)):
        el_len = len(first_el)
        el_type = type(first_el[0])
    else:
        el_len = ""
        el_type = type(first_el)

    for data in data_list:
        if isinstance(data, (list, tuple)):
            curr_type = type(data[0])
        else:
            curr_type = type(data)

        if curr_type != el_type:
            # Don't raise error if one of the type is float/int and the other is int/float.
            if (curr_type in (int, float)) and (el_type in (int, float)):
                el_type = float
            else:
                raise ValueError("Every element in the items provided must be the same type.")

    if el_type == int:
        base_type = f"int{el_len}"
    elif el_type == float:
        base_type = f"double{el_len}"
    elif el_type == bool:
        base_type = "bool"
        if el_len != "":
            stride_length = int(el_len)
    elif el_type == str:
        base_type = "token"
    else:
        raise ValueError(
            f"Base type {el_type} is not supported. Only elements of type str, bool, int and float are supported."
        )
    return base_type, stride_length


def _has_prims_output(item):
    return isinstance(item, ReplicatorItem) and "prims" in item.get_outputs()


def register(  # pylint: disable=invalid-name
    fn: Callable[..., Union[ReplicatorItem, og.Node]], override: bool = True, fn_name: str = None
) -> None:
    """Register a new function under ``omni.replicator.core.distribution``.
    Extend the default capabilities of ``omni.replicator.core.distribution`` by registering new functionality. New
    functionsmust return a ``ReplicatorItem`` or an ``OmniGraph`` node.

    Args:
        fn: A function that returns a ``ReplicatorItem`` or an ``OmniGraph`` node.
        override: If ``True``, will override existing functions of the same name. If ``False``, an error is raised.
        fn_name: Optional arg that let user choose the function name when registering it in replicator. If not
            specified, the function name is used. ``fn_name`` must follow valid [Python identifier rules]
            (https://docs.python.org/3.10/reference/lexical_analysis.html#identifiers)

    """
    if fn_name is None:
        fn_name = fn.__name__

    if not fn_name.isidentifier():
        raise ValueError(
            f"The function name {fn_name} is not a valid Python identifier. fn_name must only contains alphanumeric "
            "letters (a-z), numbers (0-9) or underscores (_) and cannot start with a number or contain any spaces."
        )

    module = sys.modules[__name__]
    if fn_name in dir(module):
        if override:
            print(f"Overriding function {{{fn_name}}} for replicator.distribution.")
        else:
            raise ValueError()

    wrapped_fn = ReplicatorWrapper(fn)
    setattr(sys.modules[__name__], fn_name, wrapped_fn)


@ReplicatorWrapper
def uniform(
    lower: Tuple, upper: Tuple, num_samples: int = 1, seed: Optional[int] = None, name: Optional[str] = None
) -> ReplicatorItem:
    """Provides sampling with a uniform distribution

    Args:
        lower: Lower end of the distribution.
        upper: Upper end of the distribution.
        num_samples: The number of times to sample.
        seed (optional): A seed to use for the sampling.
        name (optional): A name for the given distribution. Named distributions will have their values available to the
            ``Writer``.
    """
    if not isinstance(lower, (list, tuple)):
        lower = [lower]
    if not isinstance(upper, (list, tuple)):
        upper = [upper]

    sample_node = create_node("omni.replicator.core.OgnSampleUniform", node_name=name)
    if isinstance(num_samples, int):
        og.AttributeValueHelper(sample_node.get_attribute("inputs:numSamples")).set(num_samples, update_usd=True)
    elif isinstance(num_samples, ReplicatorItem):
        num_samples.node.get_attribute("outputs:samples").connect(sample_node.get_attribute("inputs:numSamples"), True)
    og.AttributeValueHelper(sample_node.get_attribute("inputs:lower")).set(lower, update_usd=True)
    og.AttributeValueHelper(sample_node.get_attribute("inputs:upper")).set(upper, update_usd=True)

    if seed:
        og.AttributeValueHelper(sample_node.get_attribute("inputs:seed")).set(seed, update_usd=True)

    if name is not None:
        _add_named_node(name, sample_node)

    return sample_node


@ReplicatorWrapper
def sequence(
    items: Union[List, ReplicatorItem],
    ordered: Optional[bool] = True,
    seed: Optional[int] = -1,
    name: Optional[str] = None,
    stride: Optional[int] = None,
) -> ReplicatorItem:
    """Provides sampling sequentially

    Args:
        items: Ordered list of items to sample sequentially.
        ordered: Whether to return item in order.
        seed (optional): A seed to use for the sampling.
        name (optional): A name for the given distribution. Named distributions will have their values available to the
            ``Writer``.
        stride (optional): Number of values to 'chunk' per sample.  Default=None (auto calculate stride)

    Example:
        >>> import omni.replicator.core as rep
        >>> cube = rep.create.cube(count=1)
        >>> with cube:
        ...     rep.modify.pose(
        ...         position=rep.distribution.sequence(
        ...             [(0.0, 0.0, 200.0), (0.0, 200.0, 0.0), (200.0, 0.0, 0.0)]
        ...         )
        ...     )
        omni.replicator.core.distribution.sequence
    """
    is_items_prims = False
    stage = omni.usd.get_context().get_stage()
    if isinstance(items, list) and items:
        # If the list contains ReplicatorItems, raise an error early.
        if all(isinstance(c, ReplicatorItem) for c in items):
            sample_node = create_node(
                "omni.replicator.core.OgnSampleSequence", ordered=ordered, seed=seed, node_name=name
            )

            array_node = create_node("omni.replicator.core.OgnArray", arrayType="int")
            array_node.get_attribute("inputs:array").set(list(range(len(items))))
            array_node.get_attribute("inputs:array").connect(sample_node.get_attribute("inputs:items"), True)

            select_switch_node = create_node("omni.replicator.core.OgnSelectSwitch", node_name=name)

            for i, replicator_item_node in enumerate(items):
                _setup_random_attribute(
                    write_node=select_switch_node,
                    attribute_value=replicator_item_node,
                    input_name=f"data{i}",
                )

            sample_node.get_attribute("outputs:samples").connect(
                select_switch_node.get_attribute("inputs:condition"), True
            )
            return select_switch_node

        if any(isinstance(c, ReplicatorItem) for c in items):
            raise ValueError(
                "A list of ReplicatorItems mixed with other data types is not supported as input to a `sequence`"
                "distribution. Sequence input must be grouped into a single `ReplicatorItem` object."
            )

        # Detect if items correspond to USD prims provided as paths, strings, or prim objects.
        prim_items = (
            isinstance(items[0], (Sdf.Path, usdrt.Sdf.Path))
            or (
                all(isinstance(c, str) for c in items)
                and all(Sdf.Path.IsValidPathString(c) for c in items)
                and all(stage.GetPrimAtPath(c) for c in items)
            )
            or any(isinstance(c, (Sdf.Path, usdrt.Sdf.Path, Usd.Prim)) for c in items)
        )

        if prim_items:
            is_items_prims = True
        else:
            data_type, stride_length = _get_data_type(items)
            if stride:
                stride_length = stride
            array_node = create_node("omni.replicator.core.OgnArray", arrayType=data_type, node_name=name)
            og.AttributeValueHelper(array_node.get_attribute("inputs:array")).set(items, update_usd=True)
            sample_node = create_node(
                "omni.replicator.core.OgnSampleSequence",
                ordered=ordered,
                seed=seed,
                node_name=name,
                stride=stride_length,
            )
            array_node.get_attribute("inputs:array").connect(sample_node.get_attribute("inputs:items"), True)
    elif isinstance(items, ReplicatorItem) and items.get_output_prims():
        is_items_prims = True
    else:
        raise ValueError(f"Invalid value for `items`: {type(items)}")

    if is_items_prims:
        sample_node = create_node(
            "omni.replicator.core.OgnSampleSequencePrim", ordered=ordered, seed=seed, node_name=name
        )
        if isinstance(items, ReplicatorItem) and items.get_output_prims():
            output_prims = items.get_output_prims()
            if len(output_prims) == 1:
                items.node.get_attribute(f"outputs:{list(output_prims.keys())[0]}").connect(
                    sample_node.get_attribute("inputs:items"), True
                )
            else:
                raise ValueError(
                    f"Ambiguous value for `items`, ReplicatorItem `{items}` contains multiple possible output prim "
                    "attributes."
                )
        set_target_prims(sample_node, "inputs:items", items)

    if name is not None:
        _add_named_node(name, sample_node)

    return sample_node


@ReplicatorWrapper
def normal(
    mean: Tuple, std: Tuple, num_samples: int = 1, seed: Optional[int] = None, name: Optional[str] = None
) -> ReplicatorItem:
    """Provides sampling with a normal distribution

    Args:
        mean: Average value for the distribution.
        std: Standard deviation value for the distribution.
        num_samples: The number of times to sample.
        seed (optional): A seed to use for the sampling.
        name (optional): A name for the given distribution. Named distributions will have their values available to the
            ``Writer``.
    """
    if not isinstance(mean, (list, tuple)):
        mean = [mean]
    if not isinstance(std, (list, tuple)):
        std = [std]

    sample_node = create_node("omni.replicator.core.OgnSampleNormal", node_name=name)
    if isinstance(num_samples, int):
        og.AttributeValueHelper(sample_node.get_attribute("inputs:numSamples")).set(num_samples, update_usd=True)
    elif isinstance(num_samples, ReplicatorItem):
        num_samples.node.get_attribute("outputs:samples").connect(sample_node.get_attribute("inputs:numSamples"), True)
    og.AttributeValueHelper(sample_node.get_attribute("inputs:mean")).set(mean, update_usd=True)
    og.AttributeValueHelper(sample_node.get_attribute("inputs:std")).set(std, update_usd=True)

    if seed:
        og.AttributeValueHelper(sample_node.get_attribute("inputs:seed")).set(seed, update_usd=True)

    if name is not None:
        _add_named_node(name, sample_node)

    return sample_node


@ReplicatorWrapper
def choice(
    choices: List[str],
    weights: List[float] = None,
    num_samples: Union[ReplicatorItem, int] = 1,
    seed: Optional[int] = -1,
    with_replacements: bool = True,
    name: Optional[str] = None,
) -> ReplicatorItem:
    """Provides sampling from a list of values

    Args:
        choices: Values in the distribution to choose from.
        weights: Matching list of weights for each choice.
        num_samples: The number of times to sample.
        seed (optional): A seed to use for the sampling.
        with_replacements: If ``True``, allow re-sampling the same element. If ``False``, each element can only be
            sampled once. Note that in this case, the size of the elements being sampled must be larger than the
            sampling size. Default is True.
        name (optional): A name for the given distribution. Named distributions will have their values available to the
            ``Writer``.
    """
    stage = omni.usd.get_context().get_stage()
    choice_node = "omni.replicator.core.OgnSampleChoice"

    # Must determine whether to use a choicePrim node or a generic choice node
    if isinstance(choices, ReplicatorItem):
        if _has_prims_output(choices):
            choice_node = "omni.replicator.core.OgnSampleChoicePrim"
    elif choices and isinstance(choices, list):
        # If list of all ReplicatorItems
        if all(isinstance(c, ReplicatorItem) for c in choices):
            if all(_has_prims_output(c) for c in choices):
                choice_node = "omni.replicator.core.OgnSampleChoicePrim"
            else:
                # Choice ReplicatorItem with no prims output, return an index to select from the list of ReplicatorItems
                choice_node = "omni.replicator.core.OgnSampleChoice"
                sample_node = create_node(
                    choice_node,
                    seed=seed,
                    numSamples=1,
                    weights=weights,
                    withReplacements=with_replacements,
                    node_name=name,
                )
                array_node = create_node("omni.replicator.core.OgnArray", arrayType="int")
                array_node.get_attribute("inputs:array").set(list(range(len(choices))))
                array_node.get_attribute("inputs:array").connect(sample_node.get_attribute("inputs:choices"), True)

                select_switch_node = create_node("omni.replicator.core.OgnSelectSwitch", node_name=name)

                for i, replicator_item_node in enumerate(choices):
                    _setup_random_attribute(
                        write_node=select_switch_node,
                        attribute_value=replicator_item_node,
                        input_name=f"data{i}",
                    )

                sample_node.get_attribute("outputs:samples").connect(
                    select_switch_node.get_attribute("inputs:condition"), True
                )

                return select_switch_node

        # If list is entirely composed of prim-like objects OR strings/paths that resolve to valid prims.
        elif all(isinstance(c, (Usd.Prim, Sdf.Path, usdrt.Sdf.Path)) for c in choices) or all(
            (
                Sdf.Path.IsValidPathString(str(c)) and stage.GetPrimAtPath(str(c)).IsValid()
                if isinstance(c, (str, Sdf.Path, usdrt.Sdf.Path))
                else isinstance(c, (Usd.Prim, ReplicatorItem))
            )
            for c in choices
        ):
            choice_node = "omni.replicator.core.OgnSampleChoicePrim"
        else:
            # List contains non-prims or non-prim-path strings
            data_type, stride_length = _get_data_type(choices)
            array_node = create_node("omni.replicator.core.OgnArray", arrayType=data_type)
            array_node.get_attribute("inputs:array").set(choices)
    else:
        raise ValueError(f"Invalid value for `choices`: {type(choices)}")

    if isinstance(num_samples, int):
        sample_node = create_node(
            choice_node,
            numSamples=num_samples,
            seed=seed,
            weights=weights,
            withReplacements=with_replacements,
            node_name=name,
        )
    elif isinstance(num_samples, ReplicatorItem):
        sample_node = create_node(
            choice_node, seed=seed, weights=weights, withReplacements=with_replacements, node_name=name
        )
        num_samples.node.get_attribute("outputs:samples").connect(sample_node.get_attribute("inputs:numSamples"), True)

    if isinstance(choices, ReplicatorItem):
        if _has_prims_output(choices):
            choices.node.get_attribute("outputs:prims").connect(sample_node.get_attribute("inputs:choices"), True)
        elif "samples" in choices.get_outputs():
            choices.node.get_attribute("outputs:samples").connect(sample_node.get_attribute("inputs:choices"), True)
        else:
            raise ValueError(
                f"Got unsupported choice value {choices.node}, expected a node with either [prims, samples] outputs."
            )
    else:
        if choice_node.endswith("Prim"):
            set_target_prims(sample_node, "inputs:choices", choices)
        else:
            array_node.get_attribute("inputs:array").connect(sample_node.get_attribute("inputs:choices"), True)

    if name is not None:
        _add_named_node(name, sample_node)

    return sample_node


@ReplicatorWrapper
def combine(
    distributions: List[Union[ReplicatorItem, Tuple[ReplicatorItem]]], name: Optional[str] = None
) -> ReplicatorItem:
    """Combine input from different distributions.

    Args:
        distributions: List of Replicator distribution nodes or numbers.
        name (optional): A name for the given distribution. Named distributions will have their values available to the
            ``Writer``.
    """
    if len(distributions) == 0:
        raise ValueError("There are not distribution nodes in the input list.")

    sample_node = create_node("omni.replicator.core.OgnSampleCombine", node_name=name)
    og.AttributeValueHelper(sample_node.get_attribute("inputs:numInputNodes")).set(len(distributions), update_usd=True)

    for i, dist in enumerate(distributions):
        attribute_name = f"inputs:sample_{i}"

        if isinstance(dist, ReplicatorItem):
            input_node = dist.node
        elif isinstance(dist, og.Node):
            input_node = dist
        elif isinstance(dist, float):
            attr = og.Controller.create_attribute(sample_node, attribute_name, "float[]")
            og.AttributeValueHelper(attr).set([dist], update_usd=True)
        elif isinstance(dist, int):
            attr = og.Controller.create_attribute(sample_node, attribute_name, "int[]")
            og.AttributeValueHelper(attr).set([dist], update_usd=True)
        elif isinstance(dist, bool):
            attr = og.Controller.create_attribute(sample_node, attribute_name, "bool[]")
            og.AttributeValueHelper(attr).set([dist], update_usd=True)
        elif isinstance(dist, str):
            attr = og.Controller.create_attribute(sample_node, attribute_name, "token[]")
            og.AttributeValueHelper(attr).set([dist], update_usd=True)
        else:
            raise ValueError(f"The type {type(dist)} is not supported.")

        if isinstance(dist, (ReplicatorItem, og.Node)):
            upstream_attr = input_node.get_attribute("outputs:samples")

            # Create downstream attribute based on upstream attribute
            # TODO: workaround of the bug of setting type to any.
            downstream_attr = og.Controller.create_attribute(
                sample_node, attribute_name, "any", attr_extended_type=og.ExtendedAttributeType.EXTENDED_ATTR_TYPE_ANY
            )
            og.AttributeValueHelper(downstream_attr).resolve_type(og.Type(og.BaseDataType.UNKNOWN))

            if not upstream_attr.is_connected(downstream_attr):
                og.Controller.connect(upstream_attr, downstream_attr)

            # Set num sample of combine
            og.Controller.connect(
                input_node.get_attribute("outputs:numSamples"), sample_node.get_attribute("inputs:numSamples")
            )

    if name is not None:
        _add_named_node(name, sample_node)

    return sample_node


@ReplicatorWrapper
def log_uniform(
    lower: Tuple, upper: Tuple, num_samples: int = 1, seed: Optional[int] = None, name: Optional[str] = None
) -> ReplicatorItem:
    """Provides sampling with a log uniform distribution

    Args:
        lower: Lower end of the distribution.
        upper: Upper end of the distribution.
        num_samples: The number of times to sample.
        seed (optional): A seed to use for the sampling.
        name (optional): A name for the given distribution. Named distributions will have their values available to the
            ``Writer``.
    """
    if not isinstance(lower, (list, tuple)):
        lower = [lower]
    if not isinstance(upper, (list, tuple)):
        upper = [upper]

    sample_node = create_node("omni.replicator.core.OgnSampleLogUniform", node_name=name)
    if isinstance(num_samples, int):
        og.AttributeValueHelper(sample_node.get_attribute("inputs:numSamples")).set(num_samples, update_usd=True)
    elif isinstance(num_samples, ReplicatorItem):
        num_samples.node.get_attribute("outputs:samples").connect(sample_node.get_attribute("inputs:numSamples"), True)
    og.AttributeValueHelper(sample_node.get_attribute("inputs:lower")).set(lower, update_usd=True)
    og.AttributeValueHelper(sample_node.get_attribute("inputs:upper")).set(upper, update_usd=True)

    if seed:
        og.AttributeValueHelper(sample_node.get_attribute("inputs:seed")).set(seed, update_usd=True)

    if name is not None:
        _add_named_node(name, sample_node)

    return sample_node
