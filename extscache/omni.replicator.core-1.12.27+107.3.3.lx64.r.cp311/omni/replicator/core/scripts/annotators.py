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

# pylint: disable=too-many-lines,protected-access

import inspect
import json
import os
import re
import secrets
import string
import textwrap
import uuid
from functools import namedtuple
from typing import Any, Callable, Dict, List, Tuple, Union

import carb
import numpy as np
import omni.graph.core as og
import omni.usd
import usdrt
import warp as wp
from omni.hydra.engine.stats import get_device_info
from omni.replicator.core.bindings._omni_replicator_core import Schema_omni_replicator_extinfo_1_0
from omni.syntheticdata import SyntheticData, SyntheticDataException, SyntheticDataStage
from pxr import Usd

from .utils import ReplicatorItem, annotator_utils
from .utils.utils import _get_data_type, add_node_id_attribute
from .utils.viewport_manager import HydraTexture

ANNOTATOR_EVENT = "omni.replicator.core.annotators:AnnotatorEvent"
GRAPH_PATH = "/Render/PostProcess/SDGPipeline"
NodeTemplate, NodeConnectionTemplate = SyntheticData.NodeTemplate, SyntheticData.NodeConnectionTemplate
AnnotatorParams = namedtuple(
    "AnnotatorParams",
    ["template", "data_type", "num_elems", "is_2d_array", "is_gpu_enabled", "hidden", "documentation"],
)
DEFAULT_ANNOTATORS = [
    "camera_params",
    "rgb",
    "normals",
    "motion_vectors",
    "cross_correspondence",
    "occlusion",
    "distance_to_image_plane",
    "distance_to_camera",
    "LdrColor",
    "HdrColor",
    "SmoothNormal",
    "BumpNormal",
    "AmbientOcclusion",
    "Motion2d",
    "DiffuseAlbedo",
    "SpecularAlbedo",
    "Roughness",
    "DirectDiffuse",
    "DirectSpecular",
    "Reflections",
    "IndirectDiffuse",
    "DepthLinearized",
    "EmissionAndForegroundMask",
    "PtDirectIllumation",
    "PtGlobalIllumination",
    "PtReflections",
    "PtRefractions",
    "PtSelfIllumination",
    "PtBackground",
    "PtWorldNormal",
    "PtWorldPos",
    "PtZDepth",
    "PtVolumes",
    "PtDiffuseFilter",
    "PtReflectionFilter",
    "PtRefractionFilter",
    "PtMultiMatte0",
    "PtMultiMatte1",
    "PtMultiMatte2",
    "PtMultiMatte3",
    "PtMultiMatte4",
    "PtMultiMatte5",
    "PtMultiMatte6",
    "PtMultiMatte7",
    "primPaths",
    "SemanticOcclusionPostRender",
    "bounding_box_2d_tight_fast",
    "bounding_box_2d_tight",
    "bounding_box_2d_loose_fast",
    "bounding_box_2d_loose",
    "bounding_box_3d_360",
    "bounding_box_3d_fast",
    "bounding_box_3d",
    "semantic_segmentation",
    "InstanceIdSegmentationPostRender",
    "instance_id_segmentation_fast",
    "instance_id_segmentation",
    "InstanceSegmentationPostRender",
    "instance_segmentation_fast",
    "instance_segmentation",
    "CameraParams",
    "BackgroundRand",
    "skeleton_prims",
    "skeleton_attributes",
    "skeleton_data",
    "pointcloud",
    "DispatchSync",
    "PostProcessDispatcher",
    "PostProcessDispatcherUngated",
]


def _get_docs_dir() -> str:
    cur_dir = os.path.dirname(os.path.abspath(__file__))
    # This while loop ensures that docs build regardless of directory structure
    max_depth = 10
    while max_depth and "docs" not in os.listdir(cur_dir):
        cur_dir = os.path.join(cur_dir, os.pardir)
        max_depth -= 1
    if not max_depth:
        raise ValueError("Unable to find `docs` directory")
    return os.path.join(cur_dir, "docs")


def _move_node(node, new_graph):
    if node.get_graph() == new_graph:
        return node

    node_path = node.get_prim_path()
    node_name = node_path.split("/")[-1]
    node_path_new = "/".join([str(new_graph.get_path_to_graph()), node_name])
    stage = omni.usd.get_context().get_stage()

    if not stage.GetPrimAtPath(node_path_new):
        node_new = og.Controller().create_node(node_path_new, node.get_node_type())
        # copy over attribute values
        for attr_src, attr_dst in zip(node.get_attributes(), node_new.get_attributes()):
            # Only copy over input values
            if attr_src.get_port_type() != og.AttributePortType.ATTRIBUTE_PORT_TYPE_INPUT:
                continue
            try:
                attr_dst.set(attr_src.get())
            except TypeError:
                carb.log_warn(
                    f"Unable to copy over attribute {attr_src.get_name()}. Trigger may not function as expected"
                )

    return og.Controller().node(node_path_new)


def _validate_kwargs(**kwargs):
    _func = kwargs.get("augmentationScript")
    if isinstance(_func, wp.context.Kernel):
        _func = _func.func
    expected_undefined_params = ["data_in", "data_out", "seed"]
    signature = inspect.signature(_func)
    undefined_required_args = []
    for param_name, param in signature.parameters.items():
        if param_name == "augmentationScript":
            continue
        if param_name in expected_undefined_params:
            continue
        if param_name not in kwargs and param.default == inspect._empty:
            undefined_required_args.append(param_name)

    if len(undefined_required_args) > 0:
        raise AugmentationError(f"Augmentation is missing required arguments: {undefined_required_args}")


class AnnotatorRegistryError(Exception):
    """Base exception for errors raised by the annotator registry"""

    def __init__(self, msg=None):
        if msg is None:
            msg = "An Annotator Registry error was encountered."
        super().__init__(msg)


class AnnotatorError(Exception):
    """Base exception for errors raised by annotator"""

    def __init__(self, msg=None):
        if msg is None:
            msg = "An Annotator error was encountered."
        super().__init__(msg)


class AugmentationError(Exception):
    """Base exception for errors raised by augmentation"""

    def __init__(self, msg=None):
        if msg is None:
            msg = "An Augmentation error was encountered."
        super().__init__(msg)


class Augmentation:
    """Augmentation class

    Augmentations are defined by a python function or warp kernel which manipulates the array held in a required
    ``data_in`` argument. Augmentations can be applied to any annotator which outputs a ``data`` attribute along with
    corresponding ``width`` and ``height`` attributes.

    Args:
        augmentation: Python function or Warp kernel describing the augmentation operation. Details on required and
            supported optional arguments as follows:

                - ``data_in``: Required by both python and warp augmentations and is populated with the input data array
                - ``data_out``: Required by warp functions, holds the output array. Not supported in conjunction with
                  python functions.
                - ``data_out_shape``: Required for warp functions if the shape of the output array does not match that
                  of the input array. An axis value of ``-1`` indicate that the axis matches the input's axis dimension.
                - ``seed``: Optional argument that can be used with both python and warp functions. If set to ``None``
                  or ``<0``, will use Replicator's global seed together with the node identifier to produce a repeatable
                  unique seed. When used with warp kernels, the seed is used to initialize a random number generator
                  that produces a new integer seed value for each warp kernel call.

        data_out_shape: Specifies the shape of the output array if the augmentation is specified as a warp kernel and
            the output array is a different shape than that of the input array. An axis value of ``-1`` indicates that
            the axis is the same size of the corresponding axis in the input array.
        documentation: Optionally document augmentation functionality, input parameters and output format.
        kwargs: Optional parameters specifying the parameters to initialize the augmentation with

    Example:
        >>> import omni.replicator.core as rep
        >>> import warp as wp
        >>> @wp.kernel
        ... def rgba_to_rgb(data_in: wp.array3d(dtype=wp.uint8), data_out: wp.array3d(dtype=wp.uint8)):
        ...    i, j = wp.tid()
        ...    data_out[i, j, 0] = data_in[i, j, 0]
        ...    data_out[i, j, 1] = data_in[i, j, 1]
        ...    data_out[i, j, 2] = data_in[i, j, 2]
        >>> augmentation = rep.annotators.Augmentation.from_function(rgba_to_rgb, data_out_shape=(-1, -1, 3))
    """

    def __init__(self, node_type_id: str, data_out_shape: Tuple[int] = None, documentation: str = None, **kwargs):
        self.node_type_id = node_type_id
        self.data_out_shape = data_out_shape
        self._kwargs = kwargs
        self._documentation = documentation

    @property
    def documentation(self) -> str:
        return self._documentation

    @staticmethod
    def from_node(
        node_type_id: str,
        attributes_mapping: Dict = None,
        data_out_shape: Tuple[int] = None,
        documentation: str = None,
        **kwargs,
    ) -> "Augmentation":
        """Create an augmentation from an existing ``OmniGraph`` node

        When applied to an annotator, corresponding attributes between the annotator and the augmentation node will be
        automatically connected to one another.

        Args:
            node_type_id: Node type ID
            attributes_mapping: Optional attribute mapping to connect non-matching attributes between the augmentation
                and the annotator to which it's applied.
            data_out_shape: Specifies the shape of the output array if the augmentation is specified as a warp kernel
                and the output array is a different shape than that of the input array. An axis value of ``-1``
                indicates that the axis is the same size of the corresponding axis in the input array.
            documentation: Optionally document augmentation functionality, input parameters and output format.
            kwargs: Optional parameters specifying the parameters to initialize the augmentation with

        Example:
            >>> import omni.replicator.core as rep
            >>> augmentation = rep.annotators.Augmentation.from_node("omni.replicator.core.CameraParams")
            >>> anno = rep.annotators.get("PostProcessRenderProductCamera").augment(augmentation)
        """
        return Augmentation(
            node_type_id=node_type_id,
            data_out_shape=data_out_shape,
            attributes_mapping=attributes_mapping,
            documentation=documentation,
            **kwargs,
        )

    @staticmethod
    def from_function(
        augmentation: Union[Callable, wp.context.Kernel],
        data_out_shape: Tuple[int] = None,
        documentation: str = None,
        **kwargs,
    ) -> "Augmentation":
        """Create an augmentation from a python function or warp kernel

        Create an augmentation defined from a python function or warp kernel which manipulates the array held in a
            ``data_in`` argument. Augmentations can be applied to any annotator which outputs a ``data`` attribute along
            with corresponding ``width`` and ``height`` attributes.

        Args:
            augmentation: Python function or Warp kernel describing the augmentation operation. Details on required and
                supported optional arguments as follows:

                    - *data_in*: Required by both python and warp augmentations and is populated with the input data
                      array
                    - *data_out*: Required by warp functions, holds the output array. Not supported in conjunction with
                      python functions.
                    - *data_out_shape*: Required for warp functions if the shape of the output array does not match that
                      of the input array. An axis value of ``-1`` indicate that the axis matches the input's axis
                      dimension.
                    - *seed*: Optional argument that can be used with both python and warp functions. If set to ``None``
                      or ``< 0``, will use Replicator's global seed together with the node identifier to produce a
                      repeatable unique seed. When used with warp kernels, the seed is used to initialize a random
                      number generator that produces a new integer seed value for each warp kernel call.

            data_out_shape: Specifies the shape of the output array if the augmentation is specified as a warp kernel
                and the output array is a different shape than that of the input array. An axis value of ``-1``
                indicates that the axis is the same size of the corresponding axis in the input array.
            documentation: Optionally document augmentation functionality, input parameters and output format.
            kwargs: Optional parameters specifying the parameters to initialize the augmentation with

        Example:
            >>> import omni.replicator.core as rep
            >>> import warp as wp
            >>> @wp.kernel
            ... def rgba_to_rgb(data_in: wp.array3d(dtype=wp.uint8), data_out: wp.array3d(dtype=wp.uint8)):
            ...    i, j = wp.tid()
            ...    data_out[i, j, 0] = data_in[i, j, 0]
            ...    data_out[i, j, 1] = data_in[i, j, 1]
            ...    data_out[i, j, 2] = data_in[i, j, 2]
            >>> augmentation = rep.annotators.Augmentation(rgba_to_rgb, data_out_shape=(-1, -1, 3))
        """
        # TODO detect if USD API used in function, warn user
        if not isinstance(augmentation, (Callable, wp.context.Kernel)):
            raise AugmentationError(f"Unsupported augmentation type {type(augmentation)}")
        if data_out_shape and (not isinstance(data_out_shape, tuple) or not all(type(s) for s in data_out_shape)):
            raise AugmentationError(
                f"Argument `data_out_shape` must be specified as a tuple of integers, got {data_out_shape}"
            )
        aug_node_name = "OgnAugment" if isinstance(augmentation, wp.context.Kernel) else "OgnAugmentCPU"
        return Augmentation(
            node_type_id=f"omni.replicator.core.{aug_node_name}",
            data_out_shape=data_out_shape,
            augmentationScript=augmentation,
            documentation=documentation,
            **kwargs,
        )

    def apply(self, annotator: Union[str, "Annotator"], name: str = None, **kwargs) -> "Annotator":
        """Apply augmentation to annotator

        Args:
            annotator: Annotator to apply the augmentation to.
            name: Optional augmentation name. The augmentation name serves as the key in a writer payload dictionary.
                If set to ``None``, the augmentation will take the name of the annotator. Defaults to ``None``
            kwargs: Optional parameters specifying the parameters with which to initialize the augmentation.
        """
        if isinstance(annotator, str):
            annotator = AnnotatorRegistry.get_annotator(annotator)
        if not isinstance(annotator, Annotator):
            raise AugmentationError(f"Invalid annotator `{annotator}` of type `{type(annotator)}`")
        params = dict(self._kwargs, **kwargs)
        return annotator.augment(augmentation=self, data_out_shape=self.data_out_shape, name=name, **params)


class Annotator:
    """Annotator class
    Annotator instances identify the annotator name, it's initialization parameters, the render products it is tied to,
    as well as the name of the OmniGraph template.

    Initialization parameters can be overridden with `initialize()`, and render products can be set with `attach()`.
    Once attached, the data from an annotator can be retrieved with `get_data()`.

    Args:
        name: Annotator name
        init_params: Optional parameters specifying the parameters to initialize the annotator with
        render_product_idxs: Optionally specify the index of render products to utilize
        device: If set, make annotator data available to specified device if possible. Select from
            ``['cpu', 'cuda', 'cuda:<device_index>']``. Defaults to ``cpu``.
        render_products[List]: If set, attach annotator to specified render products
        template_name: Optional name of the template describing the annotator graph
        do_array_copy: If ``True``, retrieve a copy of the data array. This is recommended for workflows using
            asynchronous backends to manage the data lifetime. Can be set to ``False`` to gain performance if the data
            is expected to be used immediately within the writer. Defaults to ``True``
        public_name: Optional name of the annotator to be used in a writer payload. Defaults to ``None``
    """

    def __init__(
        self,
        name: str,
        init_params: dict = None,
        render_product_idxs: List[int] = None,
        device: str = None,
        render_products: list = None,
        template_name: str = None,
        do_array_copy: bool = True,
        public_name: str = None,
    ) -> None:
        self._name = name
        self._public_name = public_name
        self._template_name = name if template_name is None else template_name
        self._node_path = None
        self._render_products = None
        self._telemetry = Schema_omni_replicator_extinfo_1_0()
        self._do_array_copy = do_array_copy
        self._on_attach_callback = None
        self._prev_semantic_filter = None

        if (
            self._template_name not in SyntheticData._ogn_templates_registry
            and self._template_name not in SyntheticData._ogn_rendervars
        ):
            raise AnnotatorRegistryError(f"The annotator `{name}` with template {self._template_name} is missing")

        if init_params is None:
            init_params = {}
        if isinstance(init_params, dict):
            self.initialize(**init_params)
        else:
            raise AnnotatorRegistryError(f"The value for `init_params` must be a a dict, got {type(init_params)}")

        if isinstance(render_product_idxs, int):
            render_product_idxs = [render_product_idxs]

        self._render_product_idxs = render_product_idxs

        self._params = AnnotatorRegistry._annotators.get(name)
        if self._params:
            self._documentation = self._params.documentation

        self._on_attach_callback = AnnotatorRegistry._annotator_callbacks.get(name)

        # Validate and normalize the requested device string.
        self._device = self._normalize_device(
            device,
            name,
            is_gpu_enabled=self._params.is_gpu_enabled if self._params else True,
        )

        if render_products is not None:
            self.attach(render_products)

    @staticmethod
    def _normalize_device(device: str, annotator_name: str, *, is_gpu_enabled: bool = True) -> str:
        """Return a validated and normalized device identifier.

        Args:
            device: User-specified target device or ``None``.
            annotator_name: Name of the annotator requesting the device (used for error messages).
            is_gpu_enabled: Whether the annotator supports execution on GPU.

        Returns:
            The lowercase, normalized device string (``"cpu"`` or ``"cuda"`` / ``"cuda:<index>"``).

        Raises:
            AnnotatorRegistryError: If the device string is malformed or not supported by the annotator.
        """
        # Default to CPU when device is not specified.
        if device is None:
            return "cpu"

        # Ensure the provided value is a string.
        if not isinstance(device, str):
            raise AnnotatorRegistryError(f"Invalid device `{device}` specified. Device must be a string or ``None``.")

        device_lower = device.lower()

        # CPU is always supported.
        if device_lower == "cpu":
            return "cpu"

        # Handle CUDA devices.
        if device_lower.startswith("cuda"):
            if not is_gpu_enabled:
                raise AnnotatorRegistryError(f"Device {device} is not supported for annotator {annotator_name}")
            return device_lower

        # Any other specification is invalid.
        raise AnnotatorRegistryError(
            f"Invalid device `{device}` specified. Device must be one of ['cpu', 'cuda', 'cuda:<device_index>']"
        )

    def initialize(self, **kwargs) -> None:
        """Initialize annotator parameters
        The initialization parameters of the annotator. Initialize can only be called before the annotator has been
        attached.

        Args:
            kwargs: Optional parameters specifying the parameters to initialize the annotator with
        """
        if self._node_path is not None:
            raise AnnotatorRegistryError("Annotator parameters cannot be initialized, it is already attached.")

        if kwargs.get("semanticTypes") or kwargs.get("semanticFilter"):
            if kwargs.get("semanticTypes"):
                semantic_filter_predicate = ":*; ".join(kwargs.pop("semanticTypes")) + ":*"
            else:
                semantic_filter_predicate = kwargs.pop("semanticFilter")

            if (
                "bounding_box" in self._name
                or "instance_segmentation" in self._name
                or "semantic_segmentation" in self._name
            ):
                # Generate a random string for unique filter name for each annotator, default to length6
                filter_name = "".join([secrets.choice(string.ascii_lowercase) for _ in range(6)])
                kwargs["semanticFilterName"] = filter_name
                SyntheticData.Get().set_semantic_filter(filter_name=filter_name, predicate=semantic_filter_predicate)

            else:
                # Cache current semantic filter so it can be restored if annotator is detached.
                self._prev_semantic_filter = SyntheticData.Get().get_instance_mapping_semantic_filter()
                carb.log_warn(
                    f"Annotator '{self._name}' overriding global semantic filter '{self._prev_semantic_filter}' "
                    f"with '{semantic_filter_predicate}'"
                )

        self._init_params = kwargs

    @property
    def documentation(self) -> str:
        return self._documentation

    @property
    def docs(self) -> str:
        return self._documentation

    @property
    def template_name(self) -> str:
        if (
            self._template_name in SyntheticData._ogn_rendervars
        ):  # TODO: if both replicator CameraParams and SensorRTX CameraParams are registered, it will always return the SensorRTX CameraParams
            if not self._params.is_gpu_enabled and f"{self._template_name}Ptr" in SyntheticData._ogn_templates_registry:
                # Only if the annotator is an aov annotator and is not gpu enabled, return the ptr
                return f"{self._template_name}Ptr"

            is_mgpu = len(get_device_info()) < 2
            kit_version = omni.kit.app.get_app().get_kit_version()
            if is_mgpu and kit_version[:5] == "105.0":
                # multi gpu device indices not supported in Kit 105.0.1
                suffix = "ExportRawArray"
            else:
                suffix = "buffPtr" if self._device.startswith("cuda") else "hostPtr"
            return f"{self._template_name}{suffix}"

        return self._template_name

    @property
    def template(self) -> dict:
        return SyntheticData._ogn_templates_registry.get(self._template_name)

    def _add_auto_sync_gate(self, template_name) -> None:
        template = SyntheticData._ogn_templates_registry[template_name]
        connections = template.connections
        valid_connections = []
        conn_node_ids = []
        for conn in connections:
            node_template_id = conn.node_template_id

            # Recursively create sync gate for upstream replicator annotator nodes if upstream node is a ON_DEMAND node
            if node_template_id in SyntheticData._ogn_templates_registry:
                node_template = SyntheticData._ogn_templates_registry[node_template_id]
                if (
                    node_template_id in AnnotatorRegistry._annotators
                    and node_template_id != "DispatchSync"
                    and node_template_id != "PostProcessDispatch"
                    and node_template.pipeline_stage == SyntheticDataStage.ON_DEMAND
                ):
                    self._add_auto_sync_gate(node_template_id)
                conn_node_ids.append(SyntheticData._ogn_templates_registry[node_template_id].node_type_id)
                valid_connections.append(conn)

        is_sync_gate = template.node_type_id == "omni.graph.action.RationalTimeSyncGate"
        has_sync_gate = any(cid == "omni.graph.action.RationalTimeSyncGate" for cid in conn_node_ids)
        # Check if a sync gate is required
        if len(valid_connections) <= 1 or is_sync_gate or has_sync_gate:
            # No sync gate to add
            return

        sync_connections = [
            NodeConnectionTemplate(
                "PostProcessDispatcher",
                render_product_idxs=(),
                attributes_mapping={
                    "outputs:referenceTimeNumerator": "inputs:rationalTimeNumerator",
                    "outputs:referenceTimeDenominator": "inputs:rationalTimeDenominator",
                },
            )
        ]
        for connection, conn_node_type_id in zip(valid_connections, conn_node_ids):
            is_gpu_interop = connection.node_template_id in SyntheticData._ogn_rendervars
            conn_exec_output = _get_node_exec(conn_node_type_id, input_exec=False)
            if conn_exec_output and not is_gpu_interop:
                conn_template_name = connection.node_template_id
                sync_connections.append(
                    NodeConnectionTemplate(conn_template_name, attributes_mapping={conn_exec_output: "inputs:execIn"})
                )
        if len(sync_connections) <= 2:  # If just on more connection on top of the dispatcher, no sync required
            # No sync gate to add
            return
        sync_gate_template = NodeTemplate(
            pipeline_stage=SyntheticDataStage.AUTO,
            node_type_id="omni.graph.action.RationalTimeSyncGate",
            connections=sync_connections,
        )
        if f"{template_name}_Sync" in SyntheticData._ogn_templates_registry:
            SyntheticData._ogn_templates_registry.pop(f"{template_name}_Sync")
        sync_gate_template_name = f"{template_name}_Sync"

        SyntheticData.register_node_template(node_template=sync_gate_template, template_name=f"{template_name}_Sync")
        exec_in = _get_node_exec(template.node_type_id, input_exec=True)
        if exec_in:
            # add connection from syncgate execOut to the input execution of node
            connections = [
                NodeConnectionTemplate(sync_gate_template_name, attributes_mapping={"outputs:execOut": exec_in})
            ] + connections

            template.connections = connections
        return

    def attach(  # noqa C901 # pylint: disable=too-many-nested-blocks
        self,
        render_products: Union[str, HydraTexture],
        render_product_idxs: List[int] = None,
    ) -> None:
        """Attach annotator to specified render products.
        Creates the OmniGraph nodes and connections.

        Args:
            render_products: Render product to attach the annotator to. Note: a list of render products is currently not
                supported
            render_product_idxs: Optionally specify the index of render products to attach to from the render product
                list provided. Note: Currently not used.
        """
        if render_product_idxs is None:
            render_product_idxs = self._render_product_idxs

        if (
            isinstance(render_products, (List, Tuple))
            and len(render_products) > 1
            and (render_product_idxs is None or len(render_product_idxs) > 1)
        ):
            carb.log_error("Attaching a list of render products is currently not implemented")
            raise NotImplementedError("Attaching a list of render products is currently not implemented")
        self._add_auto_sync_gate(self.template_name)
        if isinstance(render_products, (str, HydraTexture)):
            render_products = [render_products]

        # Get render product paths
        self._render_products = [rp.path if isinstance(rp, HydraTexture) else rp for rp in render_products]
        render_products = [rp.path if isinstance(rp, HydraTexture) else rp for rp in render_products]

        # Disable hydra textures. This lets the annotator function if they are later toggled on/off
        for render_product in render_products:
            if isinstance(render_product, HydraTexture):
                render_product.hydra_texture.set_updates_enabled(False)

        if render_product_idxs is None and self._render_product_idxs is None:
            render_product_idxs = list(range(len(self._render_products)))
        if len(self._render_products) < max(render_product_idxs):
            raise AnnotatorRegistryError(
                f"Expected at least {max(render_product_idxs)} render products, received only "
                f"{len(self._render_products)}"
            )
        render_products_idxed = [self._render_products[rpi] for rpi in render_product_idxs]

        carb.log_info(f"Attaching {self._name} to render product(s) {render_products_idxed}")

        if self._name in AnnotatorRegistry._default_annotators:
            self._telemetry.annotator_sendEvent(self._name)
        else:
            self._telemetry.annotator_sendEvent("Custom annotator")

        sdg_iface = SyntheticData.Get()
        params = {f"inputs:{k}": v for k, v in self._init_params.items()}
        activated_result = sdg_iface.activate_node_template(
            self.template_name, 0, render_products_idxed, attributes=params
        )  # TODO `0` idx needs to be more flexible

        # TODO support more than one render products
        render_product = render_products_idxed[0]
        self._node_path = sdg_iface._get_node_path(self.template_name, render_product)

        # Annotator has already been activated
        if activated_result is None and self._init_params:
            node = og.Controller().node(self._node_path)
            for attr_name, attr_val in self._init_params.items():
                attr = node.get_attribute(f"inputs:{attr_name}")
                if not attr:
                    continue
                cur_val = attr.get()
                if cur_val != attr_val:
                    carb.log_warn(
                        f"Annotator `{self.name}` is already attached at {self._node_path}."
                        f"Modifying `{attr_name}` from `{cur_val}` to `{attr_val}`."
                    )
                sdg_iface.set_node_attributes(self._name, {f"inputs:{attr_name}": attr_val}, render_product)

        # TODO: Find a better way and place to set the input attribute value for post-renderer
        if self._init_params.get("colorize"):
            if "instance_id_segmentation" in self._name:
                # Set the attribute of the post-render graph node.
                SyntheticData.Get().set_node_attributes(
                    "InstanceIdSegmentationPostRender",
                    {"inputs:colorize": self._init_params.get("colorize")},
                    render_product,
                )

                if "fast" not in self._name:
                    SyntheticData.Get().set_node_attributes(
                        "instance_id_segmentation_fast",
                        {"inputs:colorize": self._init_params.get("colorize")},
                        render_product,
                    )
            elif "instance_segmentation" in self._name:
                # Set the attribute of the post-render graph node.
                SyntheticData.Get().set_node_attributes(
                    "InstanceSegmentationPostRender",
                    {"inputs:colorize": self._init_params.get("colorize")},
                    render_product,
                )

                if "fast" not in self._name:
                    SyntheticData.Get().set_node_attributes(
                        "instance_segmentation_fast",
                        {"inputs:colorize": self._init_params.get("colorize")},
                        render_product,
                    )

        if (
            self.template
            and self.template.node_type_id == "omni.replicator.core.FabricReader"
            and self._init_params.get("prims")
            and self._init_params.get("attribute")
        ):
            # Set the attribute of the post-render graph node.
            SyntheticData.Get().set_node_attributes(
                f"{self._name}PR",
                {
                    "inputs:prims": self._init_params.get("prims"),
                    "inputs:attribute": self._init_params.get("attribute"),
                },
                render_product,
            )

        if self.template and self._init_params.get("semanticFilterName"):
            semantic_filter_name = self._init_params.get("semanticFilterName")
            SyntheticData.Get().activate_node_template(f"{semantic_filter_name}SemanticFilterPtr", 0, [render_product])

        # Set up post render graph for instance segmentation
        if (
            self.template
            and ("instance_segmentation" in self._name or "semantic_segmentation" in self._name)
            and self._init_params.get("semanticFilterName")
        ):
            semantic_filter_name = self._init_params.get("semanticFilterName")
            SyntheticData.Get().activate_node_template(f"{semantic_filter_name}SemanticFilterPost", 0, [render_product])

            SyntheticData.Get().connect_node_template(
                f"{semantic_filter_name}SemanticFilterPost",
                "InstanceSegmentationPostRender",
                render_product,
                {"outputs:semanticLabelTokenSDCudaPtr": "inputs:filteredSemanticLabelTokenCudaPtr"},
            )

        if (
            self.template
            and (
                self.template.node_type_id == "omni.replicator.core.BoundingBoxLegacy"
                or self.template.node_type_id == "omni.replicator.core.BoundingBox2D"
                or self.template.node_type_id == "omni.replicator.core.BoundingBox3D"
            )
            and self._init_params.get("semanticFilterName")
        ):
            if "2d_loose" in self._name:
                bbox_type = "2d_loose"
            elif "2d_tight" in self._name:
                bbox_type = "2d_tight"
            else:
                bbox_type = "3d"

            semantic_filter_name = self._init_params.get("semanticFilterName")
            SyntheticData.Get().activate_node_template(f"{semantic_filter_name}SemanticFilterPtr", 0, [render_product])
            SyntheticData.Get().connect_node_template(
                f"{semantic_filter_name}SemanticFilterPtr",
                f"bounding_box_{bbox_type}_fast",
                render_product,
                {"outputs:semanticLabelTokenSDHostPtr": "inputs:filteredSemanticLabelTokenPtr"},
            )

        if (
            self.template
            and (
                self.template.node_type_id == "omni.replicator.core.InstanceSegmentationLegacy"
                or self.template.node_type_id == "omni.replicator.core.InstanceSegmentation"
                or self.template.node_type_id == "omni.replicator.core.SemanticSegmentation"
            )
            and self._init_params.get("semanticFilterName")
        ):
            semantic_filter_name = self._init_params.get("semanticFilterName")
            SyntheticData.Get().activate_node_template(f"{semantic_filter_name}SemanticFilterPtr", 0, [render_product])
            SyntheticData.Get().connect_node_template(
                f"{semantic_filter_name}SemanticFilterPtr",
                f"instance_segmentation_fast",
                render_product,
                {"outputs:semanticLabelTokenSDHostPtr": "inputs:filteredSemanticLabelTokenPtr"},
            )

        # If node is augmentation, add node id
        if "OgnAugment" in self.get_node().get_type_name():
            add_node_id_attribute(self.get_node())

        reftime_gate_node_path = f"{GRAPH_PATH}/DispatchSync"
        enable_reftimegate = carb.settings.get_settings().get("/exts/omni.replicator.core/Orchestrator/enabled")

        # Keep for backwards compatibility
        if carb.settings.get_settings().get("/omni/replicator/disableAnnotatorGate"):
            enable_reftimegate = False

        # Enable frame gate
        if enable_reftimegate and omni.usd.get_context().get_stage().GetPrimAtPath(reftime_gate_node_path):
            stage = omni.usd.get_context().get_stage()
            with Usd.EditContext(stage, stage.GetSessionLayer()):
                reftime_gate_node = og.Controller().node(reftime_gate_node_path)
                og.AttributeValueHelper(reftime_gate_node.get_attribute("inputs:enabled")).set(True, update_usd=True)

        # have to dig back through connections to add dynamic attributes
        def _add_attrs_to_node(template_name, render_products) -> None:
            if template_name not in SyntheticData._ogn_templates_registry or "PostProcessDispatcher" in template_name:
                return
            node_path = SyntheticData._get_node_path(template_name, render_products[0])
            try:
                node = og.Controller().node(node_path)
            except omni.graph.core._impl.errors.OmniGraphValueError:
                # Node path doesn't exist
                return
            if template_name in AnnotatorRegistry._augmentation_attr:
                init_params = AnnotatorRegistry._augmentation_attr[template_name]
                for param, value in init_params.items():
                    if param.endswith("_in") or param.endswith("_out") or value is None:
                        continue

                    if not node.get_attribute_exists(f"inputs:{param}"):
                        if isinstance(value, ReplicatorItem):
                            # Find an input that can be used to determine data type
                            value_inputs = value.get_inputs()
                            if "outputType" in value_inputs and value_inputs["outputType"]:
                                dtype = value_inputs["outputType"]
                            else:
                                for value_input_name, value_input in value_inputs.items():
                                    if value_input_name not in ["numSamples", "seed", "outputType"]:
                                        if isinstance(value_input, np.ndarray):
                                            value_input = value_input.tolist()[0]
                                        dtype = _get_data_type(value_input)
                        else:
                            dtype = _get_data_type(value)

                        stage = omni.usd.get_context().get_stage()
                        session_layer = stage.GetSessionLayer()
                        with Usd.EditContext(stage, session_layer):
                            attr = og.Controller().create_attribute(node, f"inputs:{param}", dtype)

                    attr = node.get_attribute(f"inputs:{param}")
                    if isinstance(value, ReplicatorItem):
                        # TODO simplify once we can specify a graph for replicator items
                        graph = node.get_graph()
                        value_node = _move_node(value.node, graph)
                        if not value_node.get_attribute_exists("outputs:samples"):
                            raise ValueError(
                                f"Only `distribution` Replicator Items can be used with Augmentations, got {value_node}"
                            )
                        value_node.get_attribute("outputs:samples").connect(attr, True)
                    elif value is not None:
                        og.AttributeValueHelper(attr).set(value, update_usd=True)

            # Traverse through connections
            for conn in SyntheticData._ogn_templates_registry[template_name].connections:
                _add_attrs_to_node(conn.node_template_id, render_products_idxed)

        _add_attrs_to_node(self.template_name, render_products_idxed)

        # Add device dynamic attributes
        # Add device attribute
        node = self.get_node()
        if not node.get_attribute_exists("outputs:__device"):
            stage = omni.usd.get_context().get_stage()
            session_layer = stage.GetSessionLayer()
            with Usd.EditContext(stage, session_layer):
                og.Controller().create_attribute(
                    node=node,
                    attr_name="__device",
                    attr_type=og.Type(og.BaseDataType.TOKEN),
                    attr_port=og.AttributePortType.ATTRIBUTE_PORT_TYPE_OUTPUT,
                    attr_default="cpu",
                )
                node.get_attribute("outputs:__device").set(self._device)

        # Add do array copy attribute
        node = self.get_node()
        if not node.get_attribute_exists("outputs:__do_array_copy"):
            stage = omni.usd.get_context().get_stage()
            session_layer = stage.GetSessionLayer()
            with Usd.EditContext(stage, session_layer):
                node.create_attribute(
                    "__do_array_copy", og.Type(og.BaseDataType.BOOL), og.AttributePortType.ATTRIBUTE_PORT_TYPE_OUTPUT
                )
                node.get_attribute("outputs:__do_array_copy").set(self._do_array_copy)

        if self._on_attach_callback:
            self._on_attach_callback(node)

        # Send annotator attached event
        carb.eventdispatcher.get_eventdispatcher().dispatch_event(ANNOTATOR_EVENT, payload={"attached": self._name})

        # Re-enable hydra textures
        for render_product in render_products:
            if isinstance(render_product, HydraTexture):
                render_product.hydra_texture.set_updates_enabled(True)

        return self

    def detach(self, render_products: Union[str, HydraTexture, List[Union[str, HydraTexture]]] = None) -> None:
        """Detach an attached annotator.

        If render products are specified, detach only from those render products.

        Args:
            render_product: Optional list of render products from which the annotator is to be detached. If not
                provided, detach annotator from all attached render products

        """
        if render_products and not isinstance(render_products, List):
            render_products = [render_products]
            render_products = [rp.path if isinstance(rp, HydraTexture) else rp for rp in render_products]

        render_products = render_products or self._render_products

        if render_products:
            # Special case for semantic filters
            # We need to manually remove the filter nodes. Otherwise, they prevent the annotator from being cleaned up
            # completely when the annotator and render product are destroyed.
            try:
                node = self.get_node()
            except AnnotatorRegistryError:
                # Annotator is not attached, nothing to do
                return

            sd = SyntheticData.Get()
            filter_name = None
            if node.get_attribute_exists("inputs:semanticFilterName"):
                filter_name = node.get_attribute("inputs:semanticFilterName").get()

            sd.deactivate_node_template(
                template_name=self.template_name,
                render_product_paths=render_products,
                render_product_path_index=0,
            )

            if filter_name:
                stage = omni.usd.get_context().get_stage()
                for filter_template_name in [f"{filter_name}SemanticFilterPtr", f"{filter_name}SemanticFilterPost"]:
                    filter_node_path = sd._get_node_path(filter_template_name, render_products[0])
                    if not stage.GetPrimAtPath(filter_node_path):
                        continue
                    # Disconnect all connections
                    node = og.Controller().node(filter_node_path)
                    for attr in node.get_attributes():
                        for conn in attr.get_downstream_connections():
                            attr.disconnect(conn, True)
                    sd.deactivate_node_template(
                        template_name=filter_template_name,
                        render_product_paths=render_products,
                        render_product_path_index=0,
                    )

            if self._render_products:
                for render_product in render_products:
                    if render_product in self._render_products:
                        self._render_products.remove(render_product)

                if len(self._render_products) == 0:
                    self._render_products = None
        else:
            raise AnnotatorError("Unable to detach annotator, annotator is not attached to any render products.")

        # Explicitly set annotator to deactivated
        # `_activatedNodePaths` is a list of node paths that were explicitly activated
        # We need to ensure that it is removed to avoid dangling annotators due to deactivation order
        if self._node_path in SyntheticData.Get()._activatedNodePaths:
            SyntheticData.Get()._activatedNodePaths.remove(self._node_path)

    def get_data(self, device: str = None, do_array_copy: bool = False, use_legacy_structure: bool = True) -> Any:
        """Return annotator data.

        Note that if calling `get_data()` immediately after initialization, the annotator output will not yet
        be available. Please allow for at least one update.

        Args:
            device: Device to hold data in. Select from ``['cpu', 'cuda', 'cuda:<device_index>']``. If ``cpu`` is
                specified, the output data is returned in the form of a numpy array. If ``cuda`` is selected, a Warp
                array is returned. Note that only valid datatypes will be moved to the GPU. Defaults to the device
                specified on annotator initialization.
            do_array_copy: If ``True``, return a copy of the data. This is necessary if the data is expected to persist,
                such as when used in conjunction with asynchronous backends.
            use_legacy_structure: Specifies the output structure to return. If ``True``, the legacy structure is
                returned. The legacy structure changes depending on the data being returned:

                - only array data: <array>
                - only non-array data: {<anno_attribute_0>: <anno_output_0>, <anno_attribute_n>: <aanno_output_n>}
                - array data and non-array data: {"data": <array>, "info": {<anno_attribute_0>: <anno_output_0>,
                  <anno_attribute_n>: <aanno_output_n>}}

                If ``False``, a more consistent data structure is returned:

                - all cases: {"data": <array>, <anno_attribute_0>: <anno_output_0>, <anno_attribute_n>:
                  <aanno_output_n>}

                Defaults to ``True``

        Example:
            >>> import omni.replicator.core as rep
            >>> async def capture(ldr_annotator):
            ...     await rep.orchestrator.step_async()
            ...     data_warp = ldr_annotator.get_data(device="cuda")
            ...     data_np = data_warp.numpy()
            ...     data_np2 = ldr_annotator.get_data(deviec="cpu")
        """
        if not self.is_attached:
            raise AnnotatorError("Unable to get data, annotator is not attached to any render products.")
        if device is None:
            device = self._device
        annotator_params = AnnotatorRegistry._annotators.get(self.name)
        return annotator_utils.get_annotator_data(
            self.get_node(),
            annotator_params,
            device=device.lower(),
            annotator_id=str(self.get_node().get_prim_path()),
            do_copy=do_array_copy,
            use_legacy_structure=use_legacy_structure,
        )

    @property
    def is_attached(self) -> bool:
        """Returns ``True`` if annotator is attached to render product(s)"""
        return self._node_path is not None

    @property
    def name(self) -> str:
        """Annotator name to use as writer payload key"""
        if self._public_name:
            return self._public_name
        return self._name

    def get_name(self) -> str:
        """Get annotator name"""
        return self.name

    def get_node(self) -> og.Node:
        """Get annotator node"""
        if self._node_path is None or self._node_path not in SyntheticData.Get()._graphNodes:
            raise AnnotatorRegistryError(f"Annotator {self._name} is not attached to any render products.")
        return SyntheticData.Get()._graphNodes[self._node_path]

    def augment(
        self,
        augmentation: Union[Augmentation, str, Callable, wp.context.Kernel],
        data_out_shape: Tuple[int] = None,
        name: str = None,
        device: str = None,
        **kwargs,
    ) -> "Annotator":
        """Augment annotator

        Add an augmentation operation to the annotator

        Args:
            augmentation: Augmentation operation to apply to the annotator output
            data_out_shape: Specifies the shape of the output array if the augmentation is specified as a warp kernel
                and the output array is a different shape than that of the input array. An axis value of ``-1``
                indicates that the axis is the same size of the corresponding axis in the input array.
            name: Optional augmentation name. The augmentation name serves as the key in a writer payload dictionary.
                If set to ``None``, the augmentation will take the name of the annotator. Defaults to ``None``
            device: Optionally specify the target device. If the augmentation is a warp kernel, the device will
                automatically default to ``"cuda"``.
            kwargs: Parameters specifying the parameters to initialize the augmentation with
        """
        do_reattach = False
        if self.is_attached:
            do_reattach = True

        try:
            is_node = og.ObjectLookup().node_type(augmentation) is not None
        except omni.graph.core._impl.errors.OmniGraphError:
            # Lookup raises error when string is not a valid node type id, ignore
            is_node = False

        if isinstance(augmentation, str) and is_node:
            augmentation = Augmentation.from_node(augmentation, data_out_shape=data_out_shape, **kwargs)
        elif isinstance(augmentation, str) and augmentation in AnnotatorRegistry._augmentations:
            augmentation = AnnotatorRegistry.get_augmentation(augmentation)
        elif isinstance(augmentation, (Callable, wp.context.Kernel)):
            # If no device specified and augmentation is a warp kernel, move annotator over to GPU if possible
            if not device and isinstance(augmentation, wp.context.Kernel) and self._device.lower() == "cpu":
                device = "cuda"
            _validate_kwargs(augmentationScript=augmentation, **kwargs)  # Ensure required args are defined
            augmentation = Augmentation.from_function(augmentation, data_out_shape=data_out_shape, **kwargs)
        elif isinstance(augmentation, str):
            raise AugmentationError(f"No registered augmentation named {augmentation} found.")

        if (
            isinstance(augmentation, Augmentation)
            and augmentation.node_type_id == "omni.replicator.core.OgnAugment"
            and not device
            and self._device.lower() == "cpu"
            and self._params.is_gpu_enabled
        ):
            # If using a warp augmentation and source annotator is on "cpu", automatically
            # move annotator to "cuda" device for improved performance (for gpu compatible annotators)
            device = "cuda"

        if device and device.lower().startswith("cuda") and self._params.is_gpu_enabled:
            self._device = device

        if not isinstance(augmentation, Augmentation):
            raise AugmentationError(f"Unsupported augmentation type {type(augmentation)}")

        kwargs = dict(augmentation._kwargs, **kwargs)
        self._template_name = _create_augmented_template(
            self, augmentation.node_type_id, augmentation.data_out_shape, **kwargs
        )

        # If name is specified, change the public name. Otherwise, use the original annotator's name.
        if name:
            self._public_name = name
        else:
            self._public_name = self.name

        self._name = self._template_name

        if do_reattach and self._render_products:
            self.attach(self._render_products)
        return self

    def augment_compose(self, augmentations: List[Union[Augmentation, str]], name: str = None) -> "Annotator":
        """Augment annotator with multiple augmentation operations

        Augment annotator with a chain one or more augmentation operations

        Args:
            augmentations: List of augmentations to be applied in sequence to the annotator
            name: Optional augmentation name. The augmentation name serves as the key in a writer payload dictionary.
                If set to ``None``, the augmentation will take the name of the annotator. Defaults to ``None``

        Example:
            >>> import omni.replicator.core as rep
            >>> import warp as wp
            >>> @wp.kernel
            ... def rgba_to_rgb(data_in: wp.array3d(dtype=wp.uint8), data_out: wp.array3d(dtype=wp.uint8)):
            ...    i, j = wp.tid()
            ...    data_out[i, j, 0] = data_in[i, j, 0]
            ...    data_out[i, j, 1] = data_in[i, j, 1]
            ...    data_out[i, j, 2] = data_in[i, j, 2]
            >>> def rgb_to_greyscale(data_in):
            ...     r, g, b = data_in[..., 0], data_in[..., 1], data_in[..., 2]
            ...     return (0.299 * r + 0.587 * g + 0.114 * b).astype(np.uint8)
            >>> greyscale_anno = rep.annotators.get("rgb").augment_compose([
            ...     rep.annotators.Augmentation.from_function(rgba_to_rgb, data_out_shape=(-1, -1, 3)),
            ...     rep.annotators.Augmentation.from_function(rgb_to_greyscale),
            ... ])
        """
        if not all(isinstance(a, (str, Augmentation)) for a in augmentations):
            augmentation_types = [type(a) for a in augmentations]
            raise AugmentationError(f"Augmentations must be of type `(str|Augmentation)`, got {augmentation_types}")

        do_reattach = False
        if self.is_attached:
            do_reattach = True
            self.detach()

        augmented_annotator = self
        for augmentation in augmentations:
            if isinstance(augmentation, str):
                augmentation = AnnotatorRegistry.get_augmentation(augmentation)
            augmented_annotator = augmentation.apply(augmented_annotator, name)
        self._template_name = augmented_annotator._template_name

        if name:
            self._public_name = name
        else:
            self._public_name = self.name

        self._name = self._template_name
        if do_reattach:
            self.attach(self._render_products)
        return self


class AnnotatorRegistry:
    """Registry of annotators providing groundtruth data to writers."""

    _default_annotators = DEFAULT_ANNOTATORS
    _annotators = {
        "camera_params": AnnotatorParams("CameraParams", None, None, None, True, False, ""),
        "rgb": AnnotatorParams("LdrColorSD", np.uint8, 4, True, True, False, ""),
        "normals": AnnotatorParams("NormalSD", np.float32, 4, True, True, False, ""),
        "motion_vectors": AnnotatorParams("TargetMotionSD", np.float32, 4, True, True, False, ""),
        "cross_correspondence": AnnotatorParams("CrossCorrespondenceSD", np.float32, 4, True, True, False, ""),
        "occlusion": AnnotatorParams(
            "OcclusionSD",
            np.dtype([("instanceId", "<u4"), ("semanticId", "<u4"), ("occlusionRatio", "<f4")]),
            1,
            False,
            True,
            False,
            "",
        ),
        "distance_to_image_plane": AnnotatorParams("DistanceToImagePlaneSD", np.float32, 1, True, True, False, ""),
        "distance_to_camera": AnnotatorParams("DistanceToCameraSD", np.float32, 1, True, True, False, ""),
    }
    _annotator_callbacks = {}
    _visualizers = {}
    _augmentations = {}
    _augmentation_attr = {}

    _fabric_reader_anno_idx = 0  # TODO: Better way to resolve different instances for same type of annotator

    @classmethod
    def _write_augmentation_docs(cls):
        fpath = os.path.join(_get_docs_dir(), "augmentations_docs.rst")
        with open(fpath, "w", encoding="utf-8") as file:
            for aug_name, aug in cls._augmentations.items():
                if not aug.documentation:
                    continue
                file.write(aug_name + "\n")
                file.write("^" * len(aug_name) + "\n")
                file.write(aug.documentation + "\n")

    @classmethod
    def _write_annotator_docs(cls):
        fpath = os.path.join(_get_docs_dir(), "annotators_docs.rst")
        with open(fpath, "w", encoding="utf-8") as file:
            for aug_name, aug in cls._annotators.items():
                if not aug.documentation:
                    continue
                file.write(aug_name + "\n")
                file.write("~" * len(aug_name) + "\n")
                file.write(aug.documentation + "\n")

    @classmethod
    def _write_docs(cls):
        cls._write_annotator_docs()
        cls._write_augmentation_docs()

    @classmethod
    def register_augmentation(cls, name: str, augmentation: Union[Augmentation, str]) -> None:
        """Register an augmentation operation.

        Args:
            name: Name under which to register augmentation
            augmentation: Augmentation to register

        Example:
            >>> import omni.replicator.core as rep
            >>> def make_opaque(data_in):
            ...    data_in[..., 3] = 255
            >>> rep.AnnotatorRegistry.register_augmentation(
            ...     "makeOpaque", rep.annotators.Augmentation.from_function(make_opaque)
            ... )
        """
        if name in cls._augmentations:
            carb.log_warn(f"Augmentation {name} is already registered, overwriting augmentation")
            cls._augmentations.pop(name)

        if isinstance(augmentation, str):
            if augmentation in cls._augmentations:
                augmentation = cls._augmentations[augmentation]
            elif og.ObjectLookup.node_type(augmentation):
                augmentation = Augmentation.from_node(augmentation)
            else:
                raise AugmentationError(f"Unable to register `{name}`, augmentation `{augmentation}` was not found.")
        cls._augmentations[name] = augmentation

    @classmethod
    def unregister_augmentation(cls, name: str) -> None:
        """Register an augmentation operation.

        Args:
            name: Name of augmentation to unregister

        Example:
            >>> import omni.replicator.core as rep
            >>> def make_opaque(data_in):
            ...    data_in[..., 3] = 255
            >>> rep.AnnotatorRegistry.register_augmentation("makeOpaque", make_opaque)
        """
        if name not in AnnotatorRegistry._augmentations:
            carb.log_warn(f"No augmentation found with name `{name}`.")
        cls._augmentations.pop(name)

    @classmethod
    def register_annotator_from_node(
        cls,
        name: str,
        input_rendervars: List[Union[str, list, NodeConnectionTemplate]],
        node_type_id: str,
        init_params: dict = None,
        render_product_idxs: tuple = (0,),
        output_rendervars: List[Union[str, list]] = None,
        output_data_type: Any = None,
        output_is_2d: bool = False,
        output_channels: int = 1,
        is_gpu_enabled: bool = True,
        hidden: bool = False,
        on_attach_callback: Callable = None,
        documentation: str = None,
    ) -> None:
        """Register annotator from an omnigraph node definition.

        Args:
            name: Annotator name. This name will be used to retrieve the annotator from the registry
                and will be used as the key in the data dictionary provided to the writer.
            input_rendervars: List of rendervars or other nodes that supply inputs to the node.
            node_type_id: Node type ID
            init_params: Annotator initialization parameters
            render_product_idxs: Index of render products to utilize
            output_rendervars: Specifies the render vars output by the node
            output_data_type: Specifies the output data type
            output_is_2d: Set to True if output is a 2D array
            output_channels: Specifies the number of output channels of the array. Ignored if
                ``output_is_2d`` is set to ``False``
            is_gpu_enabled: If ``False``, annotator device cannot be set to "cuda" and data will only be provided
                through system memory.
            hidden: If ``True``, annotator is not exposed by calls to ``get`` and ``get_registered_annotators``.
                Intermediate annotator representations should be hidden. Defaults to ``False``
            on_attach_callback: Optional function to call after attaching annotator. Takes annotator node as argument.
            documentation: Optionally document annotator functionality, input parameters and output format.
        """
        if name in SyntheticData._ogn_templates_registry:
            # PostProcessDispatch is overwritten by default on init
            if name != "PostProcessDispatch":
                carb.log_warn(f"Annotator {name} is already registered, overwriting annotator template")
            SyntheticData._ogn_templates_registry.pop(name)

        if init_params is None:
            init_params = {}
        attributes = {f"inputs:{k}": v for k, v in init_params.items()}

        connections = []
        conn_node_ids = []
        for render_var in input_rendervars:
            if isinstance(render_var, str):
                connections.append(NodeConnectionTemplate(render_var))
            elif isinstance(render_var, NodeConnectionTemplate):
                connections.append(render_var)
            else:
                raise AnnotatorRegistryError(
                    f"Error registering node `{name}`. Received an invalid connection `{render_var}`."
                    f"Connection must be of type `str` or `NodeConnectionTemplate`, received {type(render_var)}"
                )
            node_template_id = connections[-1].node_template_id
            if node_template_id in SyntheticData._ogn_templates_registry:
                conn_node_ids.append(SyntheticData._ogn_templates_registry[node_template_id].node_type_id)

        template = NodeTemplate(
            pipeline_stage=SyntheticDataStage.AUTO,
            node_type_id=node_type_id,
            connections=connections,
            attributes=attributes,
        )
        try:
            SyntheticData.register_node_template(
                node_template=template, template_name=name, rendervars=output_rendervars
            )
        except SyntheticDataException as e:
            # Skip error in sphinx build
            if not os.environ.get("SPHINX"):
                raise

        cls._annotators[name] = AnnotatorParams(
            name, output_data_type, output_channels, output_is_2d, is_gpu_enabled, hidden, documentation
        )
        cls._annotator_callbacks[name] = on_attach_callback

    @classmethod
    def register_annotator_from_aov(
        cls,
        aov: str,
        output_data_type: Any = None,
        output_channels: int = 1,
        on_attach_callback: Callable = None,
        name: str = None,
        is_gpu_enabled: bool = True,
        documentation: str = None,
    ) -> None:
        """Register annotator from an Arbitrary Output Variable (AOV).

        Args:
            aov: AOV name
            output_data_type: Specifies the output data type
            output_channels: Specifies the number of output channels of the array. Ignored if
                ``output_is_2d`` is set to ``False``
            name: Optionally provide a name. If a name is not provided, the AOV name is used.
            on_attach_callback: Optional function to call after attaching annotator. Takes annotator node as argument.
            is_gpu_enabled: If ``False``, annotator device cannot be set to "cuda" and data will only be provided
                through system memory.
            documentation: Optionally document annotator functionality, input parameters and output format.
        """
        if aov in SyntheticData._ogn_rendervars:
            SyntheticData._ogn_rendervars.pop(aov)
        if name is None:
            name = aov
        SyntheticData._ogn_rendervars.update({aov: "GpuInteropEntry"})
        SyntheticData.register_export_rendervar_array_templates([aov])
        if not is_gpu_enabled:  # Special case for SensorRTX render vars.
            SyntheticData.register_export_rendervar_ptr_templates([aov])
        else:
            SyntheticData.register_device_rendervar_tex_to_buff_templates([aov])
            SyntheticData.register_device_rendervar_to_host_templates([aov])
            SyntheticData.register_export_rendervar_ptr_templates([f"{aov}buff"])
            SyntheticData.register_export_rendervar_ptr_templates([f"{aov}host"])

        cls._annotators[name] = AnnotatorParams(
            aov, output_data_type, output_channels, True, is_gpu_enabled, False, documentation
        )
        if on_attach_callback is not None:
            cls._annotator_callbacks[name] = on_attach_callback

    @classmethod
    def detach(cls, annotator: Union[str, Annotator], render_products: List[Union[str, HydraTexture]]) -> None:
        """Detach annotator from render products

        Args:
            annotator: Annotator name or Annotator object to be detached
            render_product: List of render products from which the annotator is to be detached
        """
        render_products = [rp.path if isinstance(rp, HydraTexture) else rp for rp in render_products]
        if isinstance(annotator, str):
            annotator = cls.get_annotator(annotator)
        # annotator can be a connection template so deactivate_node_template must be used
        if isinstance(annotator, NodeConnectionTemplate):
            SyntheticData.Get().deactivate_node_template(
                template_name=annotator.node_template_id,
                render_product_paths=render_products,
                render_product_path_index=0,
            )
        else:
            annotator.detach(render_products)

    @classmethod
    def get_registered_annotators(cls) -> List[str]:
        """Returns a list names of registered annotators.

        Note: Hidden annotators are not returned

        Returns:
            List of registered annotators.
        """
        return [k for k, v in cls._annotators.items() if not v[5]]

    @classmethod
    def get_annotator(
        cls,
        name: str,
        init_params: dict = None,
        render_product_idxs: List[int] = None,
        device: str = None,
        do_array_copy: bool = True,
    ) -> Annotator:
        """Create a new annotator instance of given annotator name

        Args:
            name: Name of annotator to be retrieved from registry
            init_params: Annotator initialization parameters
            render_product_idxs: Index of render products to utilize
            device: If set, make annotator data available to specified device if possible. Select from
                `['cpu', 'cuda', 'cuda:<device_index>']`. Defaults to ``cpu``
            do_array_copy: If ``True``, retrieve a copy of the data array. This is recommended for workflows using
                asynchronous backends to manage the data lifetime. Can be set to ``False`` to gain performance if the
                data is expected to be used immediately within the writer. Defaults to ``True``
        """
        if not isinstance(name, str):
            raise AnnotatorRegistryError(f"Invalid name `{name}` or type `{type(name)}`")
        if render_product_idxs and (
            not hasattr(render_product_idxs, "__iter__") or not all(isinstance(rpi, int) for rpi in render_product_idxs)
        ):
            raise AnnotatorRegistryError(
                f"Invalid render product indexes, must be list of integers, got `{render_product_idxs}`"
            )

        # Register Fabric Reader attribute
        # TODO: Better way to resolve different instances for same type of annotator
        if name == "Attribute":
            if cls._fabric_reader_anno_idx > 0:
                suffix = f"{cls._fabric_reader_anno_idx:02d}"
                name = f"{name}_{cls._fabric_reader_anno_idx:02d}"
                _register_fabric_reader_anno(suffix)
            cls._fabric_reader_anno_idx += 1

        if not AnnotatorRegistry._annotators.get(name):
            if name in SyntheticData._ogn_templates_registry:
                return Annotator(
                    name,
                    init_params,
                    render_product_idxs,
                    template_name=name,
                    device=device,
                    do_array_copy=do_array_copy,
                )

            raise AnnotatorRegistryError(
                f"No annotator of name {name} registered. Available annotators: {cls.get_registered_annotators()}"
            )

        template_name = AnnotatorRegistry._annotators.get(name).template
        return Annotator(
            name,
            init_params,
            render_product_idxs,
            template_name=template_name,
            device=device,
            do_array_copy=do_array_copy,
        )

    @classmethod
    def get_augmentation(cls, name: str) -> Augmentation:
        """Get Augmentation from registry

        Args:
            name: Augmentation name
        """
        if not isinstance(name, str):
            raise AnnotatorRegistryError(f"Invalid name `{name}` of type `{type(name)}`")
        if not AnnotatorRegistry._augmentations.get(name):
            raise AnnotatorRegistryError(f"No augmentation of name {name} registered")

        return AnnotatorRegistry._augmentations.get(name)

    @classmethod
    def unregister_annotator(cls, name: str) -> None:
        """Unregister annotator

        Args:
            name: Annotator name
        """
        if not isinstance(name, str):
            raise AnnotatorRegistryError(f"Invalid name `{name}` of type `{type(name)}`")
        if name in cls._annotators:
            SyntheticData.Get().unregister_node_template(name)
            cls._annotators.pop(name)
        else:
            carb.log_warn(f"No annotator name `{name}` in found in registry")

        if name in cls._annotator_callbacks:
            cls._annotator_callbacks.pop(name)

    @classmethod
    def _unregister_nodes(cls):
        while cls._annotators:
            annotator_name = cls._annotators.keys()[0]
            cls.unregister_annotator(annotator_name)


# TODO: Better way to resolve different instances for same type of annotator
def _register_fabric_reader_anno(suffix):
    def on_attribute_anno_attach(node):
        prims = node.get_attribute("inputs:prims").get()
        attribute = node.get_attribute("inputs:attribute").get()

        if len(prims) == 0:
            raise ValueError(f"No prims specified to Attribute annotator {node}")
        if not attribute:
            raise ValueError(f"No attribute specified to Attribute annotator {node}")

        # Push to fabric
        usdrt_stage = usdrt.Usd.Stage.Attach(omni.usd.get_context().get_stage_id())
        for prim in prims:
            usdrt_prim = usdrt_stage.GetPrimAtPath(str(prim))
            usdrt_prim.CreateAttribute("fc_exportToRingbuffer", usdrt.Sdf.ValueTypeNames.Tag, True)

    # Post Render Attribute Reader
    AnnotatorRegistry.register_annotator_from_node(
        name=f"Attribute_{suffix}PR",  # post-renderer part of the node
        input_rendervars=[NodeConnectionTemplate("GpuInteropEntry")],
        node_type_id="omni.replicator.core.FabricReader",
        hidden=True,
    )

    # Post Process Attribute Reader
    AnnotatorRegistry.register_annotator_from_node(
        name=f"Attribute_{suffix}",
        input_rendervars=[
            NodeConnectionTemplate(
                "PostProcessDispatch",
                attributes_mapping={"outputs:renderResults": "inputs:rp"},
            ),
            NodeConnectionTemplate(f"Attribute_{suffix}PR", attributes_mapping={"outputs:exec": "inputs:exec"}),
        ],
        node_type_id="omni.replicator.core.FabricReader",
        on_attach_callback=on_attribute_anno_attach,
    )


def get(
    name: str,
    init_params: dict = None,
    render_product_idxs: List[int] = None,
    device: str = None,
    do_array_copy: bool = True,
) -> Annotator:
    """Get annotator from registry

    Args:
        name: Name of annotator to be retrieved from registry
        init_params: Annotator initialization parameters
        render_product_idxs: Index of render products to utilize
        device: If set, make annotator data available to specified device if possible.
            Select from ``['cpu', 'cuda', 'cuda:<device_index>']``. Defaults to ``cpu``
        do_array_copy: If ``True``, retrieve a copy of the data array. This is recommended for workflows using
            asynchronous backends to manage the data lifetime. Can be set to ``False`` to gain performance if the data
            is expected to be used immediately within the writer. Defaults to ``True``
    """
    return AnnotatorRegistry.get_annotator(
        name=name,
        init_params=init_params,
        render_product_idxs=render_product_idxs,
        device=device,
        do_array_copy=do_array_copy,
    )


def get_augmentation(name: str) -> Augmentation:
    """Get Augmentation from registry

    Args:
        name: Name of augmentation to retrieve from registry
    """
    return AnnotatorRegistry.get_augmentation(name=name)


def _get_node_attrs(node_type_id, on_input: bool = True):
    port_type = "Inputs" if on_input else "Outputs"
    conn_json = og.OmniGraphInspector().as_json(og.ObjectLookup.node_type(node_type_id), flags=["attributes"])

    # FIXME json output is invalid, need to sanitize it
    def fix_json(conn_json):
        conn_json = re.sub(" +", " ", conn_json).replace("\n", "")

        try:
            conn_attributes = json.loads(conn_json)
        except json.decoder.JSONDecodeError:
            conn_json = conn_json.replace('[ "', '[{"').replace("} ]", "} }]").replace(":,", ":")
            conn_attributes = json.loads(conn_json)
        return conn_attributes

    # EndFIXME
    # FIXME inspect does not work on python nodes - assume python nodes are replicator and have outputs:exec
    if conn_json in ("", "{}"):
        if node_type_id.startswith("omni.replicator"):
            if port_type == "Outputs":
                conn_json = '{"NodeType": {"Outputs": [{"outputs:exec": {"Type": "execution"}}]}}'
            else:
                conn_json = '{"NodeType": {"Inputs": [{"inputs:exec": {"Type": "execution"}}]}}'
        else:
            conn_json = '{"NodeType": {"' + port_type + '": []}}'
    # EndFIXME
    conn_attributes = fix_json(conn_json)
    return conn_attributes["NodeType"][port_type]


def _get_node_exec(node_type_id, input_exec: bool = True):
    conn_outputs = _get_node_attrs(node_type_id, input_exec)
    conn_exec = None
    for output in conn_outputs:
        if "Name" in output:
            if output["Type"] == "execution":
                conn_exec = output["Name"]
        else:
            for conn_attr_name, conn_output in output.items():
                if conn_output["Type"] == "execution":
                    conn_exec = conn_attr_name
                    break
    return conn_exec


# TODO Refactor this function (too-complex), or move to C++ if performance is an issue
def _create_augmented_template(  # noqa C901
    source_annotator: Annotator,
    node_type_id: str,
    data_out_shape: Tuple = None,
    name: str = None,
    attributes_mapping: Dict = None,
    source_params: Dict = None,
    **kwargs,
) -> str:
    if attributes_mapping is None:
        attributes_mapping = {}

    if isinstance(source_annotator, Annotator):
        source_template_name = source_annotator.template_name
        source_template_name_simple = source_template_name

        # These suffixes are applied to AOVs based on how the data is prepared in the post render graph
        # Remove suffix to get to the simple AOV name so that annotator params can be retrieved.
        for suffix in ["SD", "SDExportRawArray", "SDhostPtr", "SDbuffPtr", "hostPtr", "buffPtr", "ExportRawArray"]:
            if source_template_name.endswith(suffix):
                source_template_name_simple = source_template_name.split(suffix)[0]
                break
        source_params = AnnotatorRegistry._annotators.get(source_template_name_simple)
        if source_params is None:
            source_params = AnnotatorRegistry._annotators.get(source_annotator._name)
    else:
        raise AnnotatorError(f"Expected source annotator of type string or Annotator, got {type(source_annotator)}")
    if source_template_name in SyntheticData._ogn_templates_registry:
        source_node_type_id = SyntheticData._ogn_templates_registry[source_template_name].node_type_id
    elif source_template_name in SyntheticData._ogn_rendervars:
        if source_template_name.endswith("buff") or source_template_name.endswith("host"):
            source_node_type_id = "omni.syntheticdata.SdRenderVarPtr"
            source_template_name += "Ptr"
        else:
            source_node_type_id = "omni.graph.nodes.GpuInteropRenderProductEntry"
            source_template_name += "ExportRawArray"
    else:
        raise ValueError(
            f"No annotator of name {source_annotator} registered. Available annotators: "
            f"{AnnotatorRegistry.get_registered_annotators()}"
        )

    if node_type_id.startswith("omni.replicator.core.OgnAugment"):
        # Find exec out attribute name if using augmentation node
        if source_node_type_id:
            source_exec_out = _get_node_exec(source_node_type_id, input_exec=False)
            if source_exec_out:
                attributes_mapping.update(
                    {
                        source_exec_out: "inputs:exec",
                    }
                )

            # OG bug inspecting python node attributes, so hard coded for augment node
            augment_node_input_attr_names = [
                "dataPtr",
                "data",
                "width",
                "height",
                "format",
                "bufferSize",
                "cudaDeviceIndex",
                "strides",
                "dataType",
                "dataShape",
            ]
            if source_node_type_id.startswith("omni.replicator.core.OgnAugment"):
                source_node_output_attr_names = [
                    "dataPtr",
                    "dataType",
                    "dataShape",
                    "width",
                    "height",
                    "format",
                    "bufferSize",
                    "cudaDeviceIndex",
                    "strides",
                ]
            else:
                source_node_output_attrs = _get_node_attrs(source_node_type_id, on_input=False)
                source_node_output_attr_names = [
                    a["Name"].split(":")[-1] for a in source_node_output_attrs if "Name" in a
                ]

            for attr in source_node_output_attr_names:
                if attr in augment_node_input_attr_names:
                    attributes_mapping[f"outputs:{attr}"] = f"inputs:{attr}"

        func = kwargs.get("augmentationScript")
        # convert function into source code
        if isinstance(func, wp.context.Kernel):
            # Warp kernel, need a GPU node
            func = func.func
        elif isinstance(func, Callable) and source_params:
            # If function is not warp kernel, input datatype is not necessarily defined
            # Capture data input type if user-specified
            kwargs["dataType"] = np.dtype(source_params.data_type).name
        else:
            raise ValueError(f"Unable to convert augmentation function of type {type(func)} into a valid augmentation.")

        fname = func.__name__
        kwargs["augmentationScript"] = textwrap.dedent(inspect.getsource(func))
        kwargs["augmentationFunctionName"] = fname
        for param_name, param in inspect.signature(func).parameters.items():
            default_value = param.default
            if default_value == inspect._empty:
                default_value = None
            value = kwargs.get(param_name, default_value)
            kwargs[param_name] = value
    else:
        fname = node_type_id.split(".")[-1]

    augmentation_id = "".join(map(str.title, fname.split("_"))) + "_" + str(uuid.uuid1()).replace("-", "")
    if name is None:
        augmentation_template_name = augmentation_id
    else:
        # TODO sanitize name
        augmentation_template_name = name

    if data_out_shape:
        kwargs["dataOutShape"] = data_out_shape

    if name in AnnotatorRegistry._augmentations:
        carb.log_warn(f"Annotator {name} is already registered, overwriting annotator template")

    if source_params:
        output_data_type = source_params.data_type
        output_is_2d = source_params.is_2d_array
    else:
        output_data_type, output_is_2d = None, None

    AnnotatorRegistry.register_annotator_from_node(
        name=augmentation_template_name,
        input_rendervars=[NodeConnectionTemplate(source_template_name, attributes_mapping=attributes_mapping)],
        # init_params=kwargs,   # init params can't be set, as attributes may need to be created dynamically
        node_type_id=node_type_id,
        output_data_type=output_data_type,
        output_is_2d=output_is_2d,
    )
    # cache init params to be created dynamically after node is created
    AnnotatorRegistry._augmentation_attr[augmentation_template_name] = kwargs
    return augmentation_template_name


def augment(
    source_annotator: Union[Annotator, str],
    augmentation: Union[str, Augmentation],
    data_out_shape: Tuple = None,
    name: str = None,
    device: str = None,
    **kwargs,
) -> Annotator:
    """Create an augmented annotator

    Args:
        source_annotator: Annotator to be augmented
        augmentation: Augmentation to be applied to source annotator. Can be specified as an ``Augmentation``, the
            name of a registered augmentation or the node type id of an omnigraph node to be used as an augmentation.
        data_out_shape: Specifies the shape of the output array if the augmentation is specified as a warp kernel and
            the output array is a different shape than that of the input array. An axis value of ``-1`` indicates that
            the axis is the same size of the corresponding axis in the input array.
        name: Optional augmentation name. The augmentation name serves as the key in a writer payload dictionary.
            If set to ``None``, the augmentation will take the name of the source annotator. Defaults to ``None``
        device: Optionally specify the target device. If the augmentation is a warp kernel, the device will
            automatically default to ``"cuda"``.
        kwargs: Optional parameters specifying the parameters with which to initialize the augmentation.

    Example:
        >>> import omni.replicator.core as rep
        >>> @wp.kernel
        ... def rgba_to_rgb(data_in: wp.array3d(dtype=wp.uint8), data_out: wp.array3d(dtype=wp.uint8)):
        ...    i, j = wp.tid()
        ...    data_out[i, j, 0] = data_in[i, j, 0]
        ...    data_out[i, j, 1] = data_in[i, j, 1]
        ...    data_out[i, j, 2] = data_in[i, j, 2]
        >>> rgb_anno = rep.annotators.augment(
        ...     source_annotator="rgb",
        ...     augmentation=rep.annotators.Augmentation.from_function(rgba_to_rgb)
        ... )
    """
    if not isinstance(source_annotator, (str, Annotator)):
        raise AnnotatorError(f"Source annotator must be of type `(str|Annotator)`, got {type(source_annotator)}")
    if isinstance(source_annotator, str):
        if not device:
            device = "cuda" if isinstance(augmentation, wp.Kernel) else "cpu"

        source_params = AnnotatorRegistry._annotators.get(source_annotator)
        if source_params and source_params.is_gpu_enabled:
            source_annotator = AnnotatorRegistry.get_annotator(source_annotator, device=device)
        else:
            source_annotator = AnnotatorRegistry.get_annotator(source_annotator, device="cpu")

    return source_annotator.augment(augmentation, data_out_shape, name, **kwargs)


def augment_compose(
    source_annotator: Union[Annotator, str], augmentations: List[Union[str, Augmentation]], name: str = None
) -> Annotator:
    """Compose an augmentated Annotator from multiple augmentation operations

    Chain one or more augmentation operations together to be applied to a source annotator.

    Args:
        source_annotator: Annotator to be augmented
        augmentations: List of augmentations to be applied in sequence to the source annotator
        name: Optional augmentation name. The augmentation name serves as the key in a writer payload dictionary.
            If set to ``None``, the augmentation will take the name of the source annotator. Defaults to ``None``

    Example:
        >>> import omni.replicator.core as rep
        >>> @wp.kernel
        ... def rgba_to_rgb(data_in: wp.array3d(dtype=wp.uint8), data_out: wp.array3d(dtype=wp.uint8)):
        ...    i, j = wp.tid()
        ...    data_out[i, j, 0] = data_in[i, j, 0]
        ...    data_out[i, j, 1] = data_in[i, j, 1]
        ...    data_out[i, j, 2] = data_in[i, j, 2]
        >>> def rgb_to_greyscale(data_in):
        ...     r, g, b = data_in[..., 0], data_in[..., 1], data_in[..., 2]
        ...     return (0.299 * r + 0.587 * g + 0.114 * b).astype(np.uint8)
        >>> greyscale_anno = rep.annotators.augment_compose(
        ...     source_annotator="rgb",
        ...     augmentations=[
        ...         rep.annotators.Augmentation.from_function(rgba_to_rgb),
        ...         rep.annotators.Augmentation.from_function(rgb_to_greyscale),
        ...     ]
        ... )
    """
    if not isinstance(source_annotator, (str, Annotator)):
        raise AnnotatorError(f"Source annotator must be of type `(str|Annotator)`, got {type(source_annotator)}")
    if isinstance(source_annotator, str):
        source_annotator = AnnotatorRegistry.get_annotator(source_annotator)
    return source_annotator.augment_compose(augmentations, name=name)


def _get_augmentation_func(augmentation_name):
    return AnnotatorRegistry._augmentations[augmentation_name]


def _copy_annotator(cur_name, new_name):
    AnnotatorRegistry._annotators[new_name] = AnnotatorRegistry._annotators[cur_name]
    SyntheticData._ogn_templates_registry[new_name] = SyntheticData._ogn_templates_registry[cur_name]


def get_registered_annotators() -> List[str]:
    """Returns a list names of registered annotators.

    Returns:
        List of registered annotators.
    """
    return AnnotatorRegistry.get_registered_annotators()


def register(name: str, annotator: Union[Annotator, str]) -> None:
    """Register annotator

    Args:
        name: Name under which to register annotator
        annotator: Annotator to be registered
    """
    if name in SyntheticData._ogn_templates_registry:
        carb.log_warn(f"Annotator {name} is already registered, overwriting annotator")
        SyntheticData._ogn_templates_registry.pop(name)

    if isinstance(annotator, Annotator):
        _copy_annotator(annotator._name, name)
    elif isinstance(annotator, str):
        if annotator not in AnnotatorRegistry._annotators:
            raise AnnotatorRegistryError(
                f"Unable to register annotator `{name}`, No annotator of name `{annotator}` found in registry."
            )
        _copy_annotator(annotator, name)
    else:
        raise AnnotatorRegistryError(f"Annotator must be a string or `Annotator`, got `{type(annotator)}`")


def register_augmentation(name: str, augmentation: Union[Augmentation, str]) -> None:
    """Register an augmentation operation.

    Args:
        name: Name under which to register augmentation
        augmentation: Augmentation to be registered. Can be specified as an ``Augmentation``, the
            name of a registered augmentation or the node type id of an omnigraph node to be used as an augmentation.

    Example:
        >>> import omni.replicator.core as rep
        >>> def make_opaque(data_in):
        ...    data_in[..., 3] = 255
        >>> rep.annotators.register_augmentation("makeOpaque", rep.annotators.Augmentation(make_opaque))
    """
    AnnotatorRegistry.register_augmentation(name=name, augmentation=augmentation)


def unregister_augmentation(name: str) -> None:
    """Unregister a registered augmentation

    Args:
        name: Name of augmentation to unregister
    """
    AnnotatorRegistry.unregister_augmentation(name=name)
