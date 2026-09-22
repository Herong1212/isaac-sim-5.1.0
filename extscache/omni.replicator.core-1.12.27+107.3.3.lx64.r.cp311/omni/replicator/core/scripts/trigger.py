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

# pylint: disable=protected-access

import inspect
import sys
import textwrap
from functools import partial
from typing import Callable, Union

import carb
import carb.settings
import omni.graph.core as og
from omni.replicator.core.bindings._omni_replicator_core import Schema_omni_replicator_extinfo_1_0

from .named_nodes import _add_named_node
from .utils import ReplicatorItem, ReplicatorWrapper, create_node, get_graph_type

_telemetry = Schema_omni_replicator_extinfo_1_0()


# TODO Refactor this function (too-complex), or move to C++ if performance is an issue
def register(  # noqa: C901  # pylint: disable=invalid-name  # ignore complexity linting error
    fn: Callable[..., Union[ReplicatorItem, og.Node]], override: bool = True, fn_name: str = None
) -> None:
    """Register a new function under ``omni.replicator.core.trigger``.
    Extend the default capabilities of ``omni.replicator.core.trigger`` by registering new functionality. New functions
    must return a ``ReplicatorItem`` or an ``OmniGraph`` node.

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
            print(f"Overriding function {{{fn_name}}} for replicator.trigger.")
        else:
            raise ValueError()

    wrapped_fn = ReplicatorWrapper(fn)
    setattr(sys.modules[__name__], fn_name, wrapped_fn)


@ReplicatorWrapper
def on_key_press(key: str, modifier: str = None, name: str = None) -> ReplicatorItem:
    """Execute when a keyboard key is input.

    Args:
        key: The key to listen for.
        modifier: Optionally add a modifier [shift, alt, ctrl]
        name: The name of the trigger.

    Example:
        >>> import omni.replicator.core as rep
        >>> spheres = rep.create.sphere(count=10, scale=rep.distribution.uniform(1., 3.))
        >>> with rep.trigger.on_key_press(key="P", modifier="shift"):
        ...    with spheres:
        ...        mod = rep.modify.pose(position=rep.distribution.uniform((-500., -500., -500.), (500., 500., 500.)))
    """
    valid_modifiers = ["shift", "alt", "ctrl"]
    node = create_node("omni.graph.action.OnKeyboardInput", keyIn=key.upper(), onlyPlayback=False)
    if modifier is not None:
        if modifier.lower() in valid_modifiers:
            node.get_attribute(f"inputs:{modifier.lower()}In").set(True)
        else:
            raise ValueError(f"Modifier {modifier} is invalid. Select from [shift, alt, ctrl]")
    _add_named_node(name, node)
    return node


@ReplicatorWrapper
def on_frame(
    interval: int = 1, num_frames: int = 0, name: str = "on_frame", rt_subframes: int = 1, max_execs: int = 0
) -> ReplicatorItem:
    """Execute on a specific generation frame.

    Args:
        interval: The generation frame interval to execute on.
        num_frames: (Will be deprecated) Replaced by ``max_execs``. The number of times to activate the trigger.
            Generation automatically stops when all triggers have reached their maximum activation number. Note that
            this determines the number of times that the trigger is activated and not the number of times data is
            written.
        name: The name of the trigger.
        rt_subframes: If rendering in RTX Realtime mode, specifies the number of subframes to render
            in order to reduce artifacts caused by large changes in the scene.
        max_execs: The number of times to activate the trigger. Generation automatically stops
            when all triggers have reached their maximum activation number.

    Example:
        >>> import omni.replicator.core as rep
        >>> spheres = rep.create.sphere(count=10, scale=rep.distribution.uniform(1., 3.))
        >>> with rep.trigger.on_frame(max_execs=10):
        ...    with spheres:
        ...        mod = rep.modify.pose(position=rep.distribution.uniform((-500., -500., -500.), (500., 500., 500.)))
    """
    # Handle `num_frames` deprecation
    if num_frames > 0 and max_execs == 0:
        carb.log_warn("`trigger.on_frame` argument `num_frames` will be deprecated. Please use `max_execs`.")
        max_execs = num_frames
    elif num_frames > 0 and max_execs > 0 and num_frames != max_execs:
        carb.log_warn(f"`trigger.on_frame` argument `num_frames` ignored. Using `max_execs` value of `{max_execs}`")
    _telemetry.trigger_sendEvent("OnFrameTrigger", interval, max_execs)

    node = create_node(
        "omni.replicator.core.OgnOnFrame", interval=interval, maxExecs=max_execs, rtSubframes=rt_subframes
    )
    _add_named_node(name, node)
    return node


@ReplicatorWrapper
def on_time(
    interval: float = 1,
    num: int = 0,
    name: str = "on_time",
    rt_subframes: int = 32,
    enable_capture_on_play: bool = True,
    reset_physics: bool = True,
    max_execs: int = 0,
) -> ReplicatorItem:
    """Execute on a specific time interval.

    Args:
        interval: The interval of elapsed time to execute on.
        num: (Will be deprecated) Replaced by ``max_execs``. The number of times to activate the trigger.
            Generation automatically stops when all triggers have reached their maximum activation number. Note that
            this determines the number of times that the trigger is activated and not the number of times data is
            written.
        name: The name of the trigger.
        rt_subframes: If rendering in RTX Realtime mode, specifies the number of subframes to render
            in order to reduce artifacts caused by large changes in the scene.
        enable_capture_on_play: Enable ``CaptureOnPlay`` which ties replicator capture with the timeline state. Defaults
            to ``True``.
        reset_physics: If ``True`` physics simulation is reset on each trigger activation. Defaults to ``True``.
        max_execs: The number of times to activate the trigger. Generation automatically stops
            when all triggers have reached their maximum activation number. Note that this determines the number of
            times that the trigger is activated and not the number of times data is written.

    Example:
        >>> import omni.replicator.core as rep
        >>> spheres = rep.create.sphere(count=10, scale=rep.distribution.uniform(1., 3.))
        >>> with rep.trigger.on_time(max_execs=10):
        ...    with spheres:
        ...        mod = rep.modify.pose(position=rep.distribution.uniform((-500., -500., -500.), (500., 500., 500.)))
    """
    # Handle `num` deprecation
    if num > 0 and max_execs == 0:
        carb.log_warn("`trigger.on_time` argument `num` will be deprecated. Please use `max_execs`.")
        max_execs = num
    elif num > 0 and max_execs > 0 and num != max_execs:
        carb.log_warn(f"`trigger.on_time` argument `num` ignored. Using `max_execs` value of `{max_execs}`")
    _telemetry.trigger_sendEvent("OnTimeTrigger", interval, max_execs)

    if enable_capture_on_play:
        carb.settings.get_settings().set("/omni/replicator/captureOnPlay", True)
    node = create_node(
        "omni.replicator.core.OgnOnTime",
        interval=interval,
        maxExecs=max_execs,
        rtSubframes=rt_subframes,
        resetPhysics=reset_physics,
    )
    _add_named_node(name, node)
    return node


@ReplicatorWrapper
def on_time_end(
    interval: float = 1,
    name: str = "on_time_end",
    rt_subframes: int = 32,
    enable_capture_on_play: bool = True,
    max_execs: int = 0,
) -> ReplicatorItem:
    """Execute on the last frame before a specific time interval.

    Unlike `on_time`, `on_time_end` executes on the frame before the time interval is reached. This is useful when used
    in conjunction with a Writer to capture the end state of a simulation.

    Args:
        interval: The interval of elapsed time to execute on. The trigger will activate on the last frame before the
            interval value is reached.
        name: The name of the trigger.
        rt_subframes: If rendering in RTX Realtime mode, specifies the number of subframes to render
            in order to reduce artifacts caused by large changes in the scene.
        enable_capture_on_play: Enable ``CaptureOnPlay`` which ties replicator capture with the timeline state. Defaults
            to ``True``.
        max_execs: The number of times to activate the trigger. Generation automatically stops
            when all triggers have reached their maximum activation number. Note that this determines the number of
            times that the trigger is activated and not the number of times data is written.

    Example:
        >>> import omni.replicator.core as rep
        >>> spheres = rep.create.sphere(count=10, scale=rep.distribution.uniform(1., 3.))
        >>> with rep.trigger.on_time_end(max_execs=10):
        ...    with spheres:
        ...        mod = rep.modify.pose(position=rep.distribution.uniform((-500., -500., -500.), (500., 500., 500.)))
    """
    # Handle `num` deprecation
    _telemetry.trigger_sendEvent("OnTimeEndTrigger", interval, max_execs)

    if enable_capture_on_play:
        carb.settings.get_settings().set("/omni/replicator/captureOnPlay", True)
    node = create_node(
        "omni.replicator.core.OgnOnTime",
        interval=interval,
        maxExecs=max_execs,
        rtSubframes=rt_subframes,
        resetPhysics=False,
        triggerOnLastFrame=True,
    )
    _add_named_node(name, node)
    return node


@ReplicatorWrapper
def on_custom_event(event_name: str) -> ReplicatorItem:
    """Execute when a specified event is received.

    Args:
        event_name: The name of the event to listen for.

    Example:
        >>> import omni.replicator.core as rep
        >>> spheres = rep.create.sphere(count=10, scale=rep.distribution.uniform(1., 3.))
        >>> with rep.trigger.on_custom_event(event_name="Randomize!"):
        ...    with spheres:
        ...        mod = rep.modify.pose(position=rep.distribution.uniform((-500., -500., -500.), (500., 500., 500.)))
        >>> # Send event
        >>> rep.utils.send_og_event("Randomize!")
    """
    _telemetry.trigger_sendEvent("OnEventTrigger", 0.0, 0)
    return create_node("omni.graph.action.OnCustomEvent", eventName=event_name, onlyPlayback=False)


@ReplicatorWrapper
def on_condition(condition: Union[partial, Callable], max_execs: int = 0, rt_subframes: int = 1) -> ReplicatorItem:
    """Execute when a specified condition is met.

    Create a ``OnCondition`` trigger which activates when ``condition`` returns True.

    Args:
        condition: The function or partial defining the condition to be met. Must return a ``bool``. Function parameters
            are automatically added to the node as inputs. If default parameters are provided, these default values will
            be used.
        max_execs: The number of times to activate the trigger. Generation automatically stops when all triggers have
            reached their maximum activation number.
        rt_subframes: If rendering in RTX Realtime mode, specifies the number of subframes to render
            in order to reduce artifacts caused by large changes in the scene. Default is `1`.
    Example:
        >>> import omni.usd
        >>> import omni.replicator.core as rep
        >>> from functools import partial
        >>> # Create a condition that returns ``True`` whenever a prim reaches the specified threshold
        >>> def is_on_ground(prim_paths, threshold=0.):
        ...     import omni.usd
        ...     from pxr import UsdGeom
        ...     stage = omni.usd.get_context().get_stage()
        ...     up_axis = UsdGeom.GetStageUpAxis(stage)
        ...     op = "xformOp:translate"
        ...     idx = 1 if up_axis == "Y" else 2
        ...     for prim_path in prim_paths:
        ...         prim = stage.GetPrimAtPath(str(prim_path))
        ...         if prim.HasAttribute(op) and prim.GetAttribute(op).Get()[idx] <= threshold:
        ...             return True
        ...     return False
        >>> spheres = rep.create.sphere(count=10, scale=rep.distribution.uniform(1., 3.))
        >>> # Reposition the spheres when condition is met
        >>> with rep.trigger.on_condition(condition=partial(is_on_ground, prim_paths=spheres.get_output("prims"))):
        ...    with spheres:
        ...        mod = rep.modify.pose(position=rep.distribution.uniform((-500., 200., 200.), (500., 500., 500.)))
        ...        phys = rep.physics.rigid_body()
    """
    _telemetry.trigger_sendEvent("OnConditionTrigger", 0.0, max_execs)
    if isinstance(condition, ReplicatorItem):
        raise NotImplementedError("Condition must be a callable function or a partial.")

    if isinstance(condition, partial):
        cond_func = condition.func
        parameters = condition.keywords
    elif isinstance(condition, Callable):
        cond_func = condition
        cond_func_params = inspect.signature(cond_func).parameters.items()
        parameters = {name: value.default for name, value in cond_func_params if value is not inspect._empty}

    node = create_node("omni.replicator.core.OgnOnCondition", maxExecs=max_execs, rt_subframes=rt_subframes)
    condition_node = create_node(
        "omni.replicator.core.OgnConditionScript",
        conditionScript=textwrap.dedent(inspect.getsource(cond_func)),
    )
    for keyword, value in parameters.items():
        dtype = get_graph_type(value)
        og.Controller().create_attribute(condition_node, f"inputs:{keyword}", dtype)
        condition_node.get_attribute(f"inputs:{keyword}").set(value)
    condition_node.get_attribute("outputs:isConditionMet").connect(node.get_attribute("inputs:condition"), True)
    return node
