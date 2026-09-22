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

# pylint: disable=too-many-lines,protected-access,unnecessary-dunder-call,protected-access

import asyncio
import inspect
import uuid
from abc import ABC, abstractmethod
from builtins import NotImplementedError
from functools import partial
from typing import Callable, Dict, Iterable, List, Union

import carb
import omni.graph.core as og
import omni.kit
import omni.kit.async_engine
import omni.usd
import usdrt
import warp as wp
from omni.replicator.core.bindings._omni_replicator_core import Schema_omni_replicator_extinfo_1_0
from omni.syntheticdata import SyntheticData
from pxr import Sdf, Usd

from .annotators import Annotator, AnnotatorRegistry, Augmentation
from .functional.io_functions import write_json
from .trigger import on_condition
from .utils.rng import get_global_seed
from .utils.utils import (
    ReplicatorItem,
    auto_connect,
    create_node,
    get_exec_attr,
    get_graph,
    get_reduced_ref_time,
    send_og_event,
)
from .utils.viewport_manager import HydraTexture

WRITER_EVENT = "omni.replicator.core.writers.writerEvent"
GRAPH_PATH = "/Render/PostProcess/SDGPipeline"
DEFAULT_WRITERS = ["BasicWriter", "CocoWriter", "KittiWriter", "FPSWriter", "CosmosWriter"]
DEFAULT_WRITER_TRIGGER = "omni.replicator.core.OgnOnFrame"


def _connect_execs(upstream_node, downstream_node):
    """Connect first upstream exec attribute to first downstream exec attribute"""
    upstream_exec, downstream_exec = None, None
    for attr in upstream_node.get_attributes():
        if attr.get_port_type() != og.AttributePortType.ATTRIBUTE_PORT_TYPE_OUTPUT:
            continue
        if attr.get_resolved_type().get_role_name() == "execution":
            upstream_exec = attr
            break
    for attr in downstream_node.get_attributes():
        if attr.get_port_type() != og.AttributePortType.ATTRIBUTE_PORT_TYPE_INPUT:
            continue
        if attr.get_resolved_type().get_role_name() == "execution":
            downstream_exec = attr
            break
    if upstream_exec and downstream_exec:
        upstream_exec.connect(downstream_exec, True)


def _create_node_attribute(node, attribute, dtype):
    if node.get_attribute_exists(attribute):
        return
    node.create_attribute(attribute, dtype)


def _set_node_attributes(node, attributes: dict):
    for attr, value in attributes.items():
        if not node.get_attribute_exists(attr):
            continue
        og.AttributeValueHelper(node.get_attribute(attr)).set(value, update_usd=True)


def _get_or_create_node(graph, node_type_id, node_name, attributes=None):
    controller = og.Controller()
    graph_path = graph.get_path_to_graph()
    node = og.get_node_by_path(f"{graph_path}/{node_name}")
    if node is None:
        node = controller.create_node((node_name, graph), node_type_id)

    if attributes:
        _set_node_attributes(node, attributes)
    return node


def _connect_attributes(src_node, dst_node, src_attr, dst_attr):
    if len(src_attr) != len(dst_attr):
        raise ValueError

    for src_attr_name, dst_attr_name in zip(src_attr, dst_attr):
        if not src_node.get_attribute_exists(src_attr_name) or not dst_node.get_attribute_exists(dst_attr_name):
            continue
        src_attr = src_node.get_attribute(src_attr_name)
        dst_attr = dst_node.get_attribute(dst_attr_name)
        if not src_attr.is_connected(dst_attr):
            src_attr.connect(dst_attr, True)


def _connect_to_writer(graph, sync_node, writer_node, annotator, render_product_idxs=None):
    if render_product_idxs is None:
        render_product_idxs = annotator._render_product_idxs

    render_product = [annotator._render_products[rpi] for rpi in render_product_idxs][
        0
    ]  # annotator can be associated with only one render product
    annotator_node = annotator.get_node()
    annotator_name = annotator.name
    with Sdf.ChangeBlock():
        for attr in annotator_node.get_attributes():
            if attr.get_port_type() == og.AttributePortType.ATTRIBUTE_PORT_TYPE_OUTPUT and "outputs" in attr.get_name():
                # If annotator execution attribute
                if attr.get_resolved_type().get_role_name() == "execution":
                    # link to async gate input execution
                    _connect_attributes(annotator_node, sync_node, [attr.get_name()], ["inputs:execIn"])
                    continue

                attr_name = attr.get_name()[8:]

                writer_attr_name = f"inputs:{render_product.split('/')[-1]}:{annotator_name}:{attr_name}"

                _create_node_attribute(writer_node, writer_attr_name, attr.get_resolved_type())
                _connect_attributes(annotator_node, writer_node, [attr.get_name()], [writer_attr_name])


class WriterRegistryError(Exception):
    """Basic exception for errors raised by the writer registry"""

    def __init__(self, msg=None):
        if msg is None:
            msg = "A WriterRegistry error was encountered."
        super().__init__(msg)


class WriterError(Exception):
    """Basic exception for errors raised by a writer"""

    def __init__(self, msg=None):
        if msg is None:
            msg = "A Writer error was encountered."
        super().__init__(msg)


class InvalidWriterError(WriterRegistryError):
    """Exception for writer registration errors"""

    def __init__(self, writer_name, writer, msg=None):
        if msg is None:
            msg = f"The writer `{writer_name}` is invalid."
        super().__init__(msg)
        self.writer_name = writer_name
        self.writer = writer


class NodeWriter:
    """Node Writer class.

    Node writers are writers implemented as OmniGraph nodes. These depend on annotators like python writers, but
    are implemented as nodes and can be written in C++.

    Args:
        node_type_id: The node's type identifier (eg. `'my.extension.OgnCustomNode'`)
        annotators: List of dependent annotators
        kwargs: Node Writer input attribute initialization
    """

    def __init__(self, node_type_id: str, annotators: List[Union[str, Annotator]], **kwargs):
        self.node_type_id = node_type_id
        self._annotators = annotators
        self._kwargs = kwargs
        self._node = None

    def initialize(self, **kwargs) -> None:
        self._kwargs = dict(self._kwargs, **kwargs)

    def __call__(self, **kwargs):
        self.initialize(**kwargs)
        return self

    @property
    def annotators(self) -> List[Union[str, Annotator]]:
        return self._annotators

    def get_node(self):
        """Get writer node"""
        if self._node:
            return self._node

        raise InvalidWriterError(self.node_type_id, self, "Unable to retrieve writer node, writer is not attached.")

    def attach(self, render_products: Union[str, HydraTexture, List[Union[str, HydraTexture]]], **kwargs):
        """Attach node writer to render products

        Attaches the node writer to the render products specified and creates and attaches annotator graphs. If
        a single annotator is attached, input connections will match the annotator's output attribute names, in the
        form of ``inputs:<attribute_name>``. For cases involving more than one annotators, the node writer input
        attributes will be in the form ``inputs:<annotator_name>_<attribute_name>``.

        Args:
            render_products: Render Product ``HydraTexture`` object(s) or prim path(s) to which to attach the writer.
            kwargs: Node ``Writer`` input attribute initialization
        """
        init_params = dict(self._kwargs, **kwargs)
        WriterRegistry.attach(self, render_products, trigger="omni.replicator.core.OgnOnFrame", **init_params)

        # Send writer attached event
        carb.eventdispatcher.get_eventdispatcher().dispatch_event(WRITER_EVENT, payload={"attached": self.node_type_id})

    def on_final_frame(self):
        """Run after final frame is written."""
        pass

    def detach(self):
        """Detach writer"""
        WriterRegistry._detach_by_writer(self)

    def reset(self):
        """Reset writer

        This ensures that cached data does not leak if a reference to the writer remains alive.
        """
        self._node = None


class Writer(ABC):
    """Base Writer class.

    Writers must specify a list of required annotators which will be called during data collection. Annotator data is
    packaged in a ``data`` dictionary of the form ``<annotator_name>: <annotator_data>`` and passed to the writer's
    ``write`` function.

    ``__init__()`` and ``write()`` must be implemented by custom writers that inherit from this class.

    An optional ``on_final_frame()`` function can be defined to run once data generation is stopped.

    Attributes:
        backend: Optionally specify a rep.backends.Backend object. The backend specified here is used to
            automatically write metadata data.
        version: Writer version number. Defaults to "0.0.0" and initialized through ``__new__()``
        annotators: Required list of annotators to attach to writer. Defaults to an empty list and initialized through
            ``__new__()``
        num_written: Integer that is incremented with every call to ``write()``. Defaults to ``0`` and initialized
            through ``__new__()``
        data_structure: Specifies the writer's output data structure. Valid values: ``["legacy", "annotator",
            "renderProduct"]``
            - annotator: {"annotators": <anno>: {<render_product>: {<annotator_data>}}}
            - renderProduct: {"renderProducts": <render_product>: {<anno>: {<annotator_data>}}}
            - legacy (multi renderProduct): {<render_product>_<anno>: {<annotator_data>}}
            - legacy (single renderProduct): {<anno>: {<annotator_data>}}
    """

    backend = None
    version = "0.0.0"
    annotators = None
    metadata = None
    num_written = None
    data_structure = "legacy"
    _is_metadata_written = False
    _is_warning_version_posted = False
    _is_warning_backend_posted = False
    __data = None
    __schedule = None
    __max_schedule_len = 10

    def __new__(cls, *args, **kwargs):
        """Create instance and seed per-instance defaults"""
        instance = super().__new__(cls)
        instance.num_written = 0
        instance.annotators = []
        instance.version = "0.0.0"
        return instance

    def get_metadata(self):
        """Get writer metadata"""
        if not self._is_warning_version_posted and self.version == "0.0.0":
            carb.log_warn("Writer version not specified in the writer metadata")
            self._is_warning_version_posted = True

        self.metadata = {
            "name": self.__class__.__name__,  # this is the subclass i.e. the writer name
            "version": self.version,
            "replicator_global_seed:": get_global_seed(),
        }

    def write_metadata(self):
        # this saves the metadata that will be used to read the file
        if self.backend is None:
            if not self._is_warning_backend_posted:
                carb.log_warn(
                    "Unable to write metadata, no backend specified. To enable metadata writing, "
                    "either specify a backend or override the ``write_metadata`` function."
                )
                self._is_warning_backend_posted = True
            return
        self.backend.schedule(write_json, data=self.metadata, path="metadata.txt")
        self._is_metadata_written = True

    def reset(self):
        """Clear writer cached data

        This ensures that cached data does not leak if a reference to the writer remains alive.
        """
        self.__data = None
        self.__schedule = None

    @abstractmethod
    def write(self, data: dict):
        """Write ground truth."""
        raise NotImplementedError

    def schedule_write(self):
        """Manually schedule a write call to the writer

        Sends a ``writerTrigger`` event to schedule the writer for the current simulation frame. Used in conjunction
        with writer trigger set to ``None`` (ie. ``writer.attach(<render_product>, trigger=None``).

        .. note::
            The writer will not write data until the scheduled frame is rendered through subsequent ``update`` or
            ``step`` calls.

        Example:
            >>> import omni.replicator.core as rep
            >>> rp = rep.create.render_product(rep.create.camera(), (512, 512))
            >>> writer = rep.writers.get(
            ...     name="BasicWriter",
            ...     init_params={"output_dir": "_out", "rgb": True},
            ...     render_products=rp,
            ...     trigger=None,
            ... )
            >>> # ... initialize/step orchestrator
            >>> writer.schedule_write()
            >>> # ... step/update to render and write scheduled frame
        """
        send_og_event(f"writerTrigger-{self._writer_id}")

    def _schedule(self, ref_time):
        if self.__schedule is None:
            self.__schedule = []
        self.__schedule.append(ref_time)
        while len(self.__schedule) > self.__max_schedule_len:
            self.__schedule.pop(0)

    def _write(self, data: dict):
        is_writer_gate_enabled = carb.settings.get_settings().get("/exts/omni.replicator.core/Orchestrator/enabled")
        if not self._is_metadata_written:
            self.get_metadata()
            self.write_metadata()

        # Cache data so writer can be manually triggered
        self.__data = data

        # If writer is scheduled, call write
        if self.__data is None or (is_writer_gate_enabled and not self.__schedule):
            return

        if not is_writer_gate_enabled or get_reduced_ref_time(*data["reference_time"]) in self.__schedule:
            self.write(data)
            if self.num_written is None:
                self.num_written = 0
            self.num_written += 1

    def get_data(self) -> Dict:
        """Get the writer's current data payload.

        Returns the data payload currently stored in the writer. Note that this payload corresponds to the frame at
        ``data["reference_time"]`` which may be older than the current simulation time. Use
        ``rep.orchestrator.step_async`` to ensure that the simulation state matches the writer payload data.
        """
        return self.__data

    def get_annotators(self) -> Dict:
        """Get Writer Annotators

        Creates a dictionary of annotators indexed by their name.
        """
        annotators = {}
        for anno in self.annotators:
            if isinstance(anno, str):
                annotators[anno] = AnnotatorRegistry.get_annotator(anno)
            else:
                annotators[anno.name] = anno
        return annotators

    def get_attached_annotators(self) -> List:
        """Get all attached annotator instances across all render products

        Args:
            render_product_path: The render product path. If not specified, return all attached annotators.

        Returns:
            List of annotator instances
        """
        return getattr(self, "_attached_annotators", [])

    def get_annotator(self, name: str) -> Dict:
        """Get Writer Annotator

        Get the writer annotator of name ``name`` if it exists. If no annotator is found, return ``None``.

        Args:
            name: Annotator name
        """
        return self.get_annotators().get(name)

    def add_annotator(self, annotator: Annotator, name: str = None) -> None:
        """Add an annotator

        Add an annotator to the writer. If an existing annotator of the same name already exists, replace it.

        Args:
            annotator (Annotator): Annotator providing data to the writer.
            name: Optionally specify an annotator name. The annotator data will be passed to the writer payload indexed
            on this name. If ``name`` is None, the annotator name is used. Defaults to ``None``.
        """
        annotators = self.get_annotators()
        if name:
            annotator._public_name = name

        # Add annotator and replace an existing annotator of the same name
        annotators[annotator.name] = annotator
        self.annotators = list(annotators.values())

    def augment_annotator(
        self, annotator_name: str, augmentation: Union[Augmentation, str, Callable, wp.context.Kernel], **kwargs
    ) -> None:
        """Augment an existing writer annotator

        The augmented annotator will be available under the same annotator name within the data payload. Note that
        care must be taken to ensure that the augmentation applied are compatible with the data processing and I/O
        operations within the writer.

        Args:
            annotator_name: The name of the annotator to be augmented.
            augmentation: Augmentation to be applied to source annotator. Can be specified as an ``Augmentation``, the
                name of a registered augmentation or the node type id of an omnigraph node to be used as augmentation.
            kwargs: Optional parameters specifying the parameters with which to initialize the augmentation.
        """
        annotators = self.get_annotators()

        if annotator_name not in annotators:
            raise WriterError(
                f"Unable to augment annotator `{annotator_name}`, no matching annotator found. Available writer "
                f"annotators: {list(annotators.keys())}"
            )

        annotator = annotators.get(annotator_name)

        # Replace annotator with augmented version
        annotators[annotator.name] = annotator.augment(augmentation, **kwargs)

        # Set new annotator list
        self.annotators = list(annotators.values())

    def on_final_frame(self):
        """Run after final frame is written."""
        if self.__class__.__name__ in DEFAULT_WRITERS:
            WriterRegistry._telemetry.writer_sendEvent(self.__class__.__name__, self.num_written)
        else:
            WriterRegistry._telemetry.writer_sendEvent("Custom Writer", self.num_written)

    def initialize(self, **kwargs):
        """Initialize writer
        If the writer takes initialization arguments, they can be set here.

        Args:
            **kwargs: Writer initialization arguments.
        """
        self.__init__(**kwargs)

    async def __attach_async(self, render_products, trigger: Union[ReplicatorItem, Callable]):
        while any(not rp.done() for rp in render_products if asyncio.isfuture(rp)):
            await omni.kit.app.get_app().next_update_async()

        render_products_results = [rp.result() if asyncio.isfuture(rp) else rp for rp in render_products]
        render_products = []
        while render_products_results:
            rp_r = render_products_results.pop(0)
            if not isinstance(rp_r, List):
                rp_r = [rp_r]

            for render_product in rp_r:
                if isinstance(render_product, (str, Sdf.Path)):
                    render_products.append(str(render_product))
                elif isinstance(rp_r, (str, HydraTexture)):
                    render_products.append(render_product.path)
                else:
                    raise ValueError(f"Received invalid render product of type `{type(render_product)}`")

        WriterRegistry.attach(self, render_products, trigger)

    def attach(
        self,
        render_products: Union[str, HydraTexture, List[Union[str, HydraTexture]]],
        trigger: Union[ReplicatorItem, Callable] = "omni.replicator.core.OgnOnFrame",
    ):
        """Attach writer to specified render products.

        Args:
            render_products: Render Product prim path(s) to which to attach the writer.
            trigger: Function or replicator trigger that triggers the ``write`` function of the writer. If a function
                is supplied, it must return a boolean. If set to ``None``, the writer is set to a manual mode
                where it can be triggered by calling ``writer.schedule_write``.
        """
        if isinstance(render_products, (HydraTexture, asyncio.Task, str)):
            render_products = [render_products]

        if any(asyncio.isfuture(rp) for rp in render_products):
            omni.kit.async_engine.run_coroutine(self.__attach_async(render_products, trigger))
        else:
            WriterRegistry.attach(self, render_products, trigger=trigger)

        self.num_written = 0

    async def attach_async(
        self,
        render_products: Union[str, HydraTexture, List[Union[str, HydraTexture]]],
        trigger: Union[ReplicatorItem, Callable] = "omni.replicator.core.OgnOnFrame",
    ):
        """Attach writer to specified render products and await attachment completed

        Args:
            render_products: Render Product prim path(s) to which to attach the writer.
            trigger: Function or replicator trigger that triggers the ``write()`` function of the writer. If a function
                is supplied, it must return a boolean. If set to ``None``, the writer is set to a manual mode
                where it can be triggered by calling ``writer.schedule_write()``.
        """
        if isinstance(render_products, (HydraTexture, asyncio.Task, str)):
            render_products = [render_products]

        if any(asyncio.isfuture(rp) for rp in render_products):
            await self.__attach_async(render_products, trigger=trigger)
        else:
            WriterRegistry.attach(self, render_products, trigger=trigger)

    def detach(self):
        """Detach writer"""
        WriterRegistry._detach_by_writer(self)

    def get_node(self) -> og.Node:
        """Get writer node"""
        if self._node:
            return self._node

        raise InvalidWriterError(
            self.__class__.__name__, self, "Unable to retrieve writer node, writer is not attached."
        )


class WriterRegistry:
    """
    This class stores a list of available registered writers and which writers are attached to render products.

    One or more writers can be attached simultaneously to the same render product to simultaneously write ground truth
    in multiple formats.

    Register a writer with ``WriterRegistry.register(ExampleWriter)``
    Attach a writer to a render_product with ``WriterRegistry.attach("Example", "/World/Render Product")``
    Detach a writer with ``WriterRegistry.detach("Example")``
    """

    _writers = {}
    _writer_init_params = {}
    _categories = {}
    _active_writers = {}
    _telemetry = Schema_omni_replicator_extinfo_1_0()
    _default_writers = DEFAULT_WRITERS

    @classmethod
    def register(cls, writer: Writer, category: str = None) -> None:
        """Register a writer.

        Registered writers can be retrieved with ``WriterRegistry.get(<writer_name>)``

        Args:
            writer: Instance of class ``Writer``.
            category: Optionally specify a category of writer to group writers together.
        """
        writer_name = writer.__name__
        if not issubclass(writer, Writer):
            raise InvalidWriterError(writer_name, writer, f"Writer must be of class `Writer`, got {type(writer)}")
        if writer_name in cls._writers:
            carb.log_warn(f"Writer already exists. Overwriting writer {writer_name}.")
        cls._writers[writer_name] = writer

        if category:
            cls._categories.setdefault(category, []).append(writer_name)

    @classmethod
    def register_node_writer(
        cls, name: str, node_type_id: str, annotators: List[Union[str, Annotator]], category: str = None, **kwargs
    ) -> None:
        """Register a Node Writer

        Register a writer implemented as an omnigraph node.

        Args:
            node_type_id: The node's type identifier (eg. ``'my.extension.OgnCustomNode'``)
            annotators: List of dependent annotators
            category: Optionally specify a category of writer to group writers together.
            kwargs: Node Writer input attribute initialization
        """
        if not isinstance(name, str):
            raise WriterRegistryError(f"Invalid writer name ``{name}`` of type `{type(name)}`.")
        if not all(isinstance(a, (str, Annotator, SyntheticData.NodeConnectionTemplate)) for a in annotators):
            raise WriterRegistryError(f"Got one or more invalid annotators in {annotators}.")
        if name in cls._writers:
            carb.log_warn(f"Writer already exists. Overwriting writer {name}.")
        cls._writers[name] = NodeWriter
        cls._writer_init_params[name] = {"node_type_id": node_type_id, "annotators": annotators, **kwargs}

        if category:
            cls._categories.setdefault(category, []).append(name)

    @classmethod
    def unregister(cls, writer_name) -> None:
        """
        Unregister a writer with specified name if it exists.

        Args:
            writer_name: Name of registered writer.
        """
        if writer_name not in cls._writers:
            raise WriterRegistryError(f"No writer with name `{writer_name}` was found in registry.")

        cls.detach(writer_name)
        del cls._writers[writer_name]
        if writer_name in cls._writer_init_params:
            del cls._writer_init_params[writer_name]
        for _, writers_names in cls._categories.items():
            if writer_name in writers_names:
                writers_names.remove(writer_name)

    @classmethod
    def attach(  # pylint: disable=too-many-nested-blocks
        cls,
        writer: Union[Writer, NodeWriter],
        render_products: Union[str, HydraTexture, List[Union[str, HydraTexture]]],
        init_params: Dict = None,
        trigger: Union[ReplicatorItem, Callable] = DEFAULT_WRITER_TRIGGER,
        **kwargs,
    ) -> None:
        """
        Attach writer with specified name to ``render_products``.

        Args:
            writer: Writer instance
            render_products: Render Product prim path(s).
            init_params: (Deprecated) Dictionary of initialization parameters.
            trigger: Function or replicator trigger that triggers the ``write()`` function of the writer. If a function
                is supplied, it must return a boolean. If set to ``None``, the writer is set to a manual mode
                where it can be triggered by calling ``writer.schedule_write()``.
            kwargs: Additional initialization parameters.
        """
        if isinstance(render_products, (HydraTexture, str)):
            render_products = [render_products]

        if not isinstance(writer.annotators, Iterable):
            msg = f"Writer annotators must be specified as a list of annotators. Got {type(writer.annotators)}"
            raise InvalidWriterError(writer.__class__.__name__, writer, msg)

        if init_params:
            carb.log_warn("`init_params` will be deprecated. Initialization parameters can now be set using kwargs")
        elif init_params is None:
            init_params = {}

        # fix for OM-124604 - use move up render_product_paths and use in cls._attach()
        # Get render product paths
        render_product_paths = [rp.path if isinstance(rp, HydraTexture) else rp for rp in render_products]

        writer_name = writer.__class__.__name__
        active_writer_id = f"{writer_name}_{str(uuid.uuid1())}"
        combined_kwargs = dict(init_params, **kwargs)
        stage = omni.usd.get_context().get_stage()
        if stage:
            session_layer = stage.GetSessionLayer()
            with Usd.EditContext(stage, session_layer):
                writer_node = cls._attach(writer, active_writer_id, render_product_paths, **combined_kwargs)
        else:
            raise WriterRegistryError("Invalid USD stage, unable to attach writer")

        for render_product in render_product_paths:
            cls._active_writers.setdefault((render_product,), {})[active_writer_id] = writer

            if writer_name in cls._default_writers:
                cls._telemetry.writer_sendEvent(writer_name, -1)
            else:
                cls._telemetry.writer_sendEvent("Custom writer", -1)
        writer._writer_id = active_writer_id
        writer._node = writer_node

        # Writer schedule graph should exist only in the session layer
        with Usd.EditContext(stage, stage.GetSessionLayer()):
            # Hide graph if using default or none
            if trigger in [None, DEFAULT_WRITER_TRIGGER]:
                graph = get_graph("/WriterOrchestrator", is_hidden=True)
            else:
                graph = None

            # NodeWriters don't get scheduled
            if isinstance(writer, Writer):
                # Attach ScheduleWriter node to output
                if trigger is None:
                    # Default to event trigger
                    trigger = create_node(
                        "omni.graph.action.OnCustomEvent",
                        graph=graph,
                        eventName=f"writerTrigger-{writer._writer_id}",
                        onlyPlayback=False,
                    )
                elif isinstance(trigger, str):
                    try:
                        trigger = create_node(trigger, graph)
                    except og.OmniGraphError as err:
                        raise WriterError(f"Unable to create writer trigger. {err}") from err
                elif isinstance(trigger, Callable):
                    # TODO jlafleche: enable specifying target graph
                    # Create on condition trigger
                    trigger = on_condition(trigger)

                if isinstance(trigger, (ReplicatorItem, og.Node)):
                    trigger_node = trigger.node if isinstance(trigger, ReplicatorItem) else trigger
                    trigger_graph = trigger_node.get_graph()
                    schedule_node = create_node(
                        "omni.replicator.core.OgnScheduleWriter", trigger_graph, writer_id=writer._writer_id
                    )
                    ref_time_node = create_node("omni.replicator.core.ReadFabricTime", trigger_graph)
                    ref_time_node.get_attribute("outputs:fabricFrameTimeNumerator").connect(
                        schedule_node.get_attribute("inputs:rationalTimeOfSimNumerator"), True
                    )
                    ref_time_node.get_attribute("outputs:fabricFrameTimeDenominator").connect(
                        schedule_node.get_attribute("inputs:rationalTimeOfSimDenominator"), True
                    )
                    get_exec_attr(trigger_node, on_input=False).connect(
                        schedule_node.get_attribute("inputs:exec"), True
                    )
                elif trigger is not None:
                    raise ValueError(f"Invalid trigger specified of type `{type(trigger)}`.")

        # Send writer attached event
        carb.eventdispatcher.get_eventdispatcher().dispatch_event(WRITER_EVENT, payload={"attached": writer._writer_id})

    # TODO: Refactor this function (too-complex), or move to C++ if performance is an issue
    @classmethod
    def _attach(  # noqa: C901  # pylint: disable=too-many-nested-blocks
        cls, writer, writer_id, render_products: Union[str, HydraTexture, List[Union[str, HydraTexture]]], **kwargs
    ) -> None:
        writer_name = writer.__class__.__name__
        controller = og.Controller()
        stage = omni.usd.get_context().get_stage()
        if not stage:
            raise WriterRegistryError

        # Get render product paths
        render_product_paths = [rp.path if isinstance(rp, HydraTexture) else rp for rp in render_products]

        # Check graph through omnigraph
        # It still exists in the authoring layer due to sim time deltas
        if og.get_graph_by_path(GRAPH_PATH):
            graph = controller.graph(GRAPH_PATH)
        else:
            SyntheticData.Get().activate_node_template("DispatchSync")
            graph = controller.graph(GRAPH_PATH)

        if isinstance(render_products, HydraTexture):
            writer_node_name = f"{render_products.split('/')[-1]}_{writer_name}Writer"
        # If multiple render products
        if len(render_products) > 1:
            writer_node_name = f"MultipleRenderProducts_{len(render_products)}Products_{writer_name}Writer"
        else:
            writer_node_name = f"{render_product_paths[0].split('/')[-1]}_{writer_name}Writer"

        writer_node_path = omni.usd.get_stage_next_free_path(stage, f"{GRAPH_PATH}/{writer_node_name}", False)
        if isinstance(writer, NodeWriter):
            writer_node = controller.create_node(writer_node_path, writer.node_type_id)
            writer_exec = get_exec_attr(writer_node, on_input=True)
            _create_node_attribute(writer_node, "inputs:writerId", og.Type(og.BaseDataType.TOKEN, 1, 0))
            og.AttributeValueHelper(writer_node.get_attribute("inputs:writerId")).set(writer_id, update_usd=True)
            if writer_exec is None:
                raise InvalidWriterError(
                    writer.node_type_id,
                    writer,
                    "Writer is missing an input execution attribute.",
                )
            writer_exec_in = writer_exec.get_name()
        else:
            writer_node = controller.create_node(writer_node_path, "omni.replicator.core.OgnWriter")
            og.AttributeValueHelper(writer_node.get_attribute("inputs:writerId")).set(writer_id, update_usd=True)
            og.AttributeValueHelper(writer_node.get_attribute("inputs:writerName")).set(writer_name, update_usd=True)
            og.AttributeValueHelper(writer_node.get_attribute("inputs:renderProducts")).set(
                render_product_paths, update_usd=True
            )
            og.AttributeValueHelper(writer_node.get_attribute("inputs:dataStructure")).set(
                writer.data_structure, update_usd=True
            )
            writer_exec_in = "inputs:exec"

        # Set static writer parameters
        for attribute_name, value in kwargs.items():
            attribute_name = f"inputs:{attribute_name.replace('inputs:', '')}"
            if not writer_node.get_attribute_exists(attribute_name):
                raise WriterRegistryError(
                    f"Invalid attribute `{attribute_name}` provided does not exist in writer `{writer_name}`"
                )
            og.AttributeValueHelper(writer_node.get_attribute(attribute_name)).set(value, update_usd=True)

        # Create SyncGate and trigger gate, attach to OgnWriter
        sync_gate_path = omni.usd.get_stage_next_free_path(stage, f"{GRAPH_PATH}/WriterSyncGate", False)
        sync_gate_node = controller.create_node(sync_gate_path, "omni.graph.action.RationalTimeSyncGate")
        _connect_attributes(
            sync_gate_node, writer_node, ["outputs:rationalTimeNumerator"], ["inputs:referenceTimeNumerator"]
        )
        _connect_attributes(
            sync_gate_node, writer_node, ["outputs:rationalTimeDenominator"], ["inputs:referenceTimeDenominator"]
        )
        _connect_attributes(sync_gate_node, writer_node, ["outputs:execOut"], [writer_exec_in])

        # Add resolution and cameras from render products as Writer node attributes
        _create_node_attribute(writer_node, "inputs:render_products:resolution", og.Type(og.BaseDataType.INT, 2, 1))
        _create_node_attribute(writer_node, "inputs:render_products:name", og.Type(og.BaseDataType.TOKEN, 1, 1))
        _create_node_attribute(writer_node, "inputs:render_products:camera", og.Type(og.BaseDataType.TOKEN, 1, 1))

        names = []
        resolutions = []
        cameras = []

        for render_product in render_product_paths:
            names.append(render_product.split("/")[-1])
            render_product_prim = stage.GetPrimAtPath(render_product)
            resolutions.append(render_product_prim.GetAttribute("resolution").Get())
            camera = render_product_prim.GetRelationship("camera").GetTargets()
            camera = str(camera[0]) if len(camera) else ""
            cameras.append(camera)

        og.AttributeValueHelper(writer_node.get_attribute("inputs:render_products:resolution")).set(
            resolutions, update_usd=True
        )
        og.AttributeValueHelper(writer_node.get_attribute("inputs:render_products:name")).set(names, update_usd=True)
        og.AttributeValueHelper(writer_node.get_attribute("inputs:render_products:camera")).set(
            cameras, update_usd=True
        )

        # Create and/or connect annotators to writer
        for annotator_spec in writer.annotators:
            if isinstance(annotator_spec, str):
                annotator = AnnotatorRegistry.get_annotator(annotator_spec)
            elif isinstance(annotator_spec, SyntheticData.NodeConnectionTemplate):
                annotator = Annotator(
                    annotator_spec.node_template_id,
                    render_product_idxs=annotator_spec.render_product_idxs,
                    template_name=annotator_spec.node_template_id,
                )
            elif isinstance(annotator_spec, Annotator):
                annotator = annotator_spec
            else:
                msg = f"The annotator specified by writer {writer_name} is not registered: {annotator}"
                raise InvalidWriterError(writer_name, writer, msg)

            if not hasattr(writer, "_attached_annotators"):
                writer._attached_annotators = []

            if isinstance(writer, NodeWriter):
                # For NodeWriter, handle as before since they attach to all render products
                if isinstance(annotator_spec, SyntheticData.NodeConnectionTemplate):
                    attributes_mapping = annotator_spec.attributes_mapping
                    annotator.attach(render_products)

                    # Connect
                    for a_up, a_dwn in attributes_mapping.items():
                        if annotator.get_node().get_attribute_exists(a_up) and writer_node.get_attribute_exists(a_dwn):
                            attr_upstream = annotator.get_node().get_attribute(a_up)
                            if attr_upstream.get_resolved_type().get_role_name() == "execution":
                                attr_upstream.connect(sync_gate_node.get_attribute("inputs:execIn"))
                            else:
                                attr_upstream.connect(writer_node.get_attribute(a_dwn), True)
                elif isinstance(annotator, Annotator):
                    annotator.attach(render_products)

                auto_connect(annotator.get_node(), writer_node, no_exec=True)
                _connect_execs(annotator.get_node(), sync_gate_node)
                # Store annotator instance per render product
                writer._attached_annotators.append(annotator)
            else:
                # For regular Writer, create separate annotator instances for each render product if no indices provided
                if annotator._render_product_idxs is None:
                    for render_product in render_product_paths:
                        # Create a new annotator instance from the annotator spec
                        annotator_rp = Annotator(
                            name=annotator._name,
                            init_params=annotator._init_params,
                            render_product_idxs=annotator._render_product_idxs,
                            device=annotator._device,
                            render_products=annotator._render_products,
                            template_name=annotator._template_name,
                            do_array_copy=annotator._do_array_copy,
                            public_name=annotator._public_name,
                        )
                        annotator_rp.attach(render_product, [0])
                        _connect_to_writer(graph, sync_gate_node, writer_node, annotator_rp, [0])
                        # Store annotator instance per render product
                        writer._attached_annotators.append(annotator_rp)
                else:
                    # If indices are provided, pass all render products to anntotator
                    annotator.attach(render_product_paths)
                    _connect_to_writer(graph, sync_gate_node, writer_node, annotator)
                    writer._attached_annotators.append(annotator)

        # Connect trigger to dispatch gate
        dispatcher_node_path = f"{GRAPH_PATH}/PostProcessDispatcher"
        try:
            dispatcher_node = controller.node(dispatcher_node_path)
        except og.OmniGraphValueError:
            SyntheticData.Get().activate_node_template("DispatchSync")
            dispatcher_node = controller.node(dispatcher_node_path)

        # Connect time to SyncGate rational
        _connect_attributes(
            dispatcher_node, sync_gate_node, ["outputs:referenceTimeNumerator"], ["inputs:rationalTimeNumerator"]
        )
        _connect_attributes(
            dispatcher_node, sync_gate_node, ["outputs:referenceTimeDenominator"], ["inputs:rationalTimeDenominator"]
        )

        # Enable frame gate
        frame_gate_node_path = f"{GRAPH_PATH}/DispatchSync"
        frame_gate_node = controller.node(frame_gate_node_path)
        frame_gate_node.get_attribute("inputs:enabled").set(True)

        return writer_node

    @classmethod
    def detach(
        cls, writer_name: str, render_products: Union[str, HydraTexture, List[Union[str, HydraTexture]]] = None
    ) -> None:
        """
        Detach active writer with specified id from ``render_products``.

        Args:
            writer_name: Name of writer(s) to be detached.
            render_products: List of render product prim paths from which to disable the
                specified writer. If not provided, writers of matching ``writer_name`` will be disabled
                from all render products.
        """
        writers_to_detach = []
        if render_products:
            if isinstance(render_products, str):
                render_products = (render_products,)
            elif isinstance(render_products, HydraTexture):
                render_products = (render_products.path,)
            elif isinstance(render_products, (tuple, list)):
                render_products = tuple(rp.path if isinstance(rp, HydraTexture) else rp for rp in render_products)
            else:
                raise ValueError(
                    f"Invalid value for `render_products`, expected `str` or `HydraTexture`, got "
                    f"`{type(render_products)}`"
                )
        for active_rps, writers in cls._active_writers.items():
            if render_products and active_rps[0] not in render_products:
                continue
            for writer_id, cur_writer in writers.items():
                if cur_writer.__class__.__name__ == writer_name:
                    writers_to_detach.append(writer_id)

        for writer_id in writers_to_detach:
            cls._detach_by_writer_id(writer_id)

    # TODO: Refactor this function (too-complex), or move to C++ if performance is an issue
    @classmethod
    def _detach_by_writer_id(cls, writer_id: str) -> None:  # noqa: C901  # ignore complexity linting error
        """
        Detach active writer with specified id from render_products.

        Args:
            writer_id: Id of activated writer.
        """
        render_products_to_remove = []
        stage = omni.usd.get_context().get_stage()
        if not stage:
            raise WriterRegistryError("Invalid USD stage, unable to attach writer")

        session_layer = stage.GetSessionLayer()
        graph = None
        with Usd.EditContext(stage, session_layer):
            for render_products, writers in cls._active_writers.items():
                if writer_id in writers:
                    # Destroy sync gate and writer
                    writer_node = cls._get_attached_writer_node(writer_id)
                    if writer_node:
                        graph = writer_node.get_graph()
                        writer_exec = get_exec_attr(writer_node, on_input=True)
                        sync_gate = writer_exec.get_upstream_connections()[0].get_node()
                        graph.destroy_node(writer_node.get_prim_path(), True)
                        graph.destroy_node(sync_gate.get_prim_path(), True)

                    writer = writers.pop(writer_id)
                    writer.reset()

                    # Deactivate Annotators - handle per-render-product annotator instances
                    if hasattr(writer, "_attached_annotators"):
                        for annotator_instance in writer._attached_annotators:
                            annotator_instance.detach()
                        # Remove the render product from tracking
                        writer._attached_annotators = []
                    else:
                        # Fallback for writers without per-render-product tracking (legacy behavior)
                        for annotator in writer.annotators:
                            AnnotatorRegistry.detach(annotator, render_products)

                    # If no writers left, log the render products to be cleaned up
                    if not writers:
                        render_products_to_remove.append(render_products)

        # if only dispatchers and syncs left, remove them
        if graph:
            remaining_nodes = graph.get_nodes()
            non_annotators = ["omni.syntheticdata.SdOnNewFrame", "omni.replicator.core.OgnRefTimeGate"]
            if all(node.get_type_name() in non_annotators for node in remaining_nodes):
                with Usd.EditContext(stage, session_layer):
                    for node in remaining_nodes:
                        graph.destroy_node(node.get_prim_path(), True)

                    SyntheticData.Get().reset()  # Clear activation history
                    if stage.GetPrimAtPath("Render/PostProcess/SDGPipeline"):
                        stage.RemovePrim("Render/PostProcess/SDGPipeline")

                # Destroy from current authoring layer as well
                with Usd.EditContext(stage, stage.GetEditTarget()):
                    stage.RemovePrim("Render/PostProcess/SDGPipeline")

            # Destroy writer scheduler nodes tied to writer
            with Usd.EditContext(stage, session_layer):
                usdrt_stage = usdrt.Usd.Stage.Attach(omni.usd.get_context().get_stage_id())
                for node_path in usdrt_stage.GetPrimsWithTypeName("OmniGraphNode"):
                    try:
                        # Handle case where node is no longer in graph
                        node = og.Controller().node(str(node_path))
                    except og.OmniGraphValueError:
                        continue

                    node_graph = node.get_graph()
                    if (
                        node.get_type_name() == "omni.replicator.core.OgnScheduleWriter"
                        and node.get_attribute("inputs:writer_id").get() == writer_id
                    ):
                        fabric_read_node = (
                            node.get_attribute("inputs:rationalTimeOfSimDenominator")
                            .get_upstream_connections()[0]
                            .get_node()
                        )
                        writer_trigger = node.get_attribute("inputs:exec").get_upstream_connections()[0].get_node()

                        node_graph.destroy_node(fabric_read_node.get_prim_path(), True)
                        node_graph.destroy_node(writer_trigger.get_prim_path(), True)
                        node_graph.destroy_node(node.get_prim_path(), True)

                        # If graph is empty, remove it
                        if not node_graph.get_nodes():
                            stage.RemovePrim(node_graph.get_path_to_graph())
                        break

        # Clean up render_products if they are not associated with any writer
        for render_products in render_products_to_remove:
            cls._active_writers.pop(render_products)

    @classmethod
    def _detach_by_writer(cls, writer: Writer) -> None:
        """
        Detach active writer with specified id from render_products.

        Args:
            writer: Writer instance
        """
        writers_to_detach = []
        for _active_rps, writers in cls._active_writers.items():
            for writer_id, cur_writer in writers.items():
                if cur_writer == writer:
                    writers_to_detach.append(writer_id)

        for writer_id in writers_to_detach:
            cls._detach_by_writer_id(writer_id)

    @classmethod
    def get_writers(cls, category: str = None) -> dict:
        """
        Return dictionary of registered writers with mapping ``{writer_name: writer}``.

        Args:
            category: Optionally specify the category of the writers to retrieve.
        """
        if category:
            writer_names = cls._categories.get(category, [])
            return {name: cls._writers[name] for name in writer_names}

        return dict(cls._writers)

    @classmethod
    def get(
        cls,
        writer_name: str,
        init_params: Dict = None,
        render_products: List[Union[str, HydraTexture]] = None,
        trigger: Union[ReplicatorItem, Callable] = "omni.replicator.core.OgnOnFrame",
    ) -> Writer:
        """Get a registered writer

        Args:
            writer_name: Writer name
            init_params: Dictionary of initialization parameters with which to initialize writer
            render_products: List of render products to attach to writer
            trigger: Function or replicator trigger that triggers the ``write()`` function of the writer. If a function
                is supplied, it must return a boolean. If set to ``None``, the writer is set to a manual mode
                where it can be triggered by calling ``writer.schedule_write()``.
        """
        if writer_name not in cls._writers:
            raise WriterRegistryError(f"No writer with name `{writer_name}` was found in registry.")
        if issubclass(cls._writers[writer_name], NodeWriter):
            writer = cls._writers[writer_name](**cls._writer_init_params.get(writer_name, {}))
        elif issubclass(cls._writers[writer_name], Writer):
            writer = cls._writers[writer_name].__new__(cls._writers[writer_name])
        else:
            raise WriterRegistryError(f"No writer named `{writer_name}` found in registry.")
        if init_params:
            writer.initialize(**init_params)
        if render_products:
            writer.attach(render_products, trigger=trigger)
        return writer

    @classmethod
    def _on_final_frame(cls):
        for _, writers in cls._active_writers.items():
            for _, writer in writers.items():
                writer.on_final_frame()

    @classmethod
    def _get_attached_writer_node(cls, writer_id):
        stage = omni.usd.get_context().get_stage()
        if not stage.GetPrimAtPath(GRAPH_PATH):
            return None
        for node_prim in stage.GetPrimAtPath(GRAPH_PATH).GetChildren():
            # Skip non-nodes
            try:
                node = og.Controller().node(node_prim)
            except og.OmniGraphValueError:
                continue
            if (
                node.get_attribute_exists("inputs:writerId")
                and node.get_attribute("inputs:writerId").get() == writer_id
            ):
                return node

        return None

    @classmethod
    def get_attached_writers(
        cls, render_products: Union[str, HydraTexture, List[Union[str, HydraTexture]]] = None
    ) -> dict:
        """
        Return dictionary of enabled writers with mapping ``{writer_name: writer}``.

        Args:
            render_products ([string, list[string]], optional): Render Product prim path(s).
        """
        if render_products is None:
            raise WriterRegistryError("Render products must be defined")

        writers = {}
        enabled_writers = set()
        if isinstance(render_products, (str, HydraTexture)):
            render_products = [render_products]
        render_products = [rp.path if isinstance(rp, HydraTexture) else rp for rp in render_products]
        for render_product in render_products:
            enabled_writers = enabled_writers.union(cls._active_writers.get((render_product,), {}))

            for writer_id in enabled_writers:
                writer_name = cls._active_writers[(render_product,)][writer_id].__class__.__name__
                if writer_name not in writers:
                    writers[writer_name] = cls._active_writers[(render_product,)][writer_id]
                else:
                    carb.log_warn(
                        "Deprecated: Multiple writers of the same type not supported with this function. Returning "
                        "first instance"
                    )

        return writers

    @classmethod
    def get_attached_writer(
        cls, writer_name: str, render_products: Union[str, HydraTexture, List[Union[str, HydraTexture]]]
    ) -> Writer:
        """
        Return the Writer object of ``writer_name`` on ``render_products``.

        Args:
            writer_name: Writer name
            render_products: Render Product prim path(s)
        """
        if isinstance(render_products, (str, HydraTexture)):
            render_products = [render_products]
        render_products = [rp.path if isinstance(rp, HydraTexture) else rp for rp in render_products]

        writer = None
        for render_product in render_products:
            if (render_product,) not in cls._active_writers:
                raise WriterRegistryError(
                    f"No writer named {writer_name} found attached to the render products {render_products}"
                )

            # Set writer to the first match and break
            for writer_id in cls._active_writers[(render_product,)]:
                if cls._active_writers[(render_product,)][writer_id].__class__.__name__ == writer_name and not writer:
                    writer = cls._active_writers[(render_product,)][writer_id]
                else:
                    carb.log_warn(
                        f"Deprecated: Multiple {writer_name} writers on {render_product}. Returning the first "
                        f"{writer_name} writer on the render product {render_product}."
                    )
                    break

        return writer

    @classmethod
    def _get_attached_writer(cls, writer_id: str = None) -> Writer:
        if writer_id is None:
            raise WriterRegistryError("Writer ID must be defined.")

        writer = None
        for _rps, writers in cls._active_writers.items():
            if writer_id in writers:
                writer = writers[writer_id]
                break

        if writer:
            return writer

        raise WriterRegistryError(f"No writer with ID {writer_id} found attached to the render products.")

    @classmethod
    def get_writer_render_products(cls) -> set:
        """
        Return set of all ``render_products`` that are associated with one or more enabled writers.
        """
        return set(cls._active_writers.keys())

    @classmethod
    def get_annotators(cls, render_products: Union[str, HydraTexture, List[Union[str, HydraTexture]]] = None) -> set:
        """
        Return a set of annotators required by all enabled writers associated with ``render_products``.

        Args:
            render_products: Render Product prim path(s).
        """
        return {
            annotator
            for writer in cls.get_attached_writers(render_products).values()
            for annotator in writer.annotators
        }

    @classmethod
    async def initialize_annotators(
        cls, render_products: Union[str, HydraTexture, List[Union[str, HydraTexture]]] = None
    ) -> None:
        """
        Call the ``initialize_fn`` of the annotators associated with ``render_products``, if available.

        Args:
            render_products: Render Product prim path(s).
        """
        vp_iface = omni.kit.viewport.get_viewport_interface()
        viewport_instances = vp_iface.get_instance_list()

        # Get render_product to viewport mapping
        render_product_vp_mapping = {}
        for vpi in viewport_instances:
            viewport = vp_iface.get_viewport_window(vpi)
            render_product_vp_mapping[viewport.get_active_render_product()] = viewport

        if render_products is None:
            render_products = list(cls.get_writer_render_products())
        elif isinstance(render_products, (str, HydraTexture)):
            render_products = [render_products]

        for render_product in render_products:
            viewport = render_product_vp_mapping.get(render_product)
            if not viewport:
                raise WriterRegistryError(f"No viewport attached to render_product `{render_product}`")

            for annotator in cls.get_annotators(render_product):
                init_fn = AnnotatorRegistry.get_initialize_fn(annotator)
                if AnnotatorRegistry.get_is_viewport_annotator(annotator):
                    args = [viewport]
                else:
                    args = []

                if inspect.iscoroutinefunction(init_fn) or (
                    isinstance(init_fn, partial) and inspect.iscoroutinefunction(init_fn.func)
                ):
                    await init_fn(*args)
                else:
                    init_fn(*args)

    @classmethod
    def detach_all(cls) -> None:
        """Detach all active writers"""
        writers_to_detach = []
        for writer_dict in cls._active_writers.values():
            for writer in writer_dict.values():
                writers_to_detach.append(writer)

        for writer in writers_to_detach:
            cls._detach_by_writer(writer)

    @classmethod
    def _reset(cls):
        """Clears stored active writers

        Clears active writer but does not affect the graph."""
        cls._active_writers.clear()


def get(
    name: str,
    init_params: Dict = None,
    render_products: List[Union[str, HydraTexture]] = None,
    trigger: Union[ReplicatorItem, Callable] = "omni.replicator.core.OgnOnFrame",
) -> Writer:
    """Get writer instance from registered writers

    Args:
        name: Writer name
        init_params: Dictionary of initialization parameters with which to initialize writer
        render_products: List of render products to attach to writer
        trigger: Function or replicator trigger that triggers the ``write()`` function of the writer. If a function
                is supplied, it must return a boolean. If set to ``None``, the writer is set to a manual mode
                where it can be triggered by calling ``writer.schedule_write()``.

    Example:
        >>> import omni.replicator.core as rep
        >>> rp = rep.create.render_product(rep.create.camera(), (512, 512))
        >>> writer = rep.writers.get(
        ...     name="BasicWriter",
        ...     init_params={"output_dir": "_out", "rgb": True},
        ...     render_products=rp,
        ...     trigger=None,
        ... )
    """
    return WriterRegistry.get(name, init_params, render_products, trigger)


def unregister_writer(writer_name) -> None:
    """
    Unregister a writer with specified name if it exists.

    Args:
        writer_name: Name of registered writer.

    Example:
        >>> import omni.replicator.core as rep
        >>> class MyWriter(rep.Writer):
        ...     def __init__(self):
        ...         self.annotators = ["LdrColor"]
        ...         self.frame_id
        ...     def write(self, data):
        ...         print(f"I have data #{self.frame_id}!")
        ...         self.frame_id += 1
        >>> rep.writers.register_writer(MyWriter)
        >>> rep.writers.unregister_writer("MyWriter")
    """
    WriterRegistry.unregister(writer_name)


def register_writer(writer: Writer, category: str = None) -> None:
    """Register a writer.

    Registered writers can be retrieved with ``WriterRegistry.get(<writer_name>)``

    Args:
        writer: Instance of class ``Writer``.
        category: Optionally specify a category of writer to group writers together.

    Example:
        >>> import omni.replicator.core as rep
        >>> class MyWriter(rep.Writer):
        ...     def __init__(self):
        ...         self.annotators = ["LdrColor"]
        ...         self.frame_id
        ...     def write(self, data):
        ...         print(f"I have data #{self.frame_id}!")
        ...         self.frame_id += 1
        >>> rep.writers.register_writer(MyWriter)
    """
    WriterRegistry.register(writer, category)


def register_node_writer(name: str, node_type_id: str, annotators: List, category: str = None, **kwargs) -> None:
    """Register a Node Writer

    Register a writer implemented as an omnigraph node.

    Args:
        node_type_id: The node's type identifier (eg. ``'my.extension.OgnCustomNode'``)
        annotators: List of dependent annotators
        category: Optionally specify a category of writer to group writers together.
        kwargs: Node Writer input attribute initialization
    """
    WriterRegistry.register_node_writer(
        name=name, annotators=annotators, node_type_id=node_type_id, category=category, **kwargs
    )
