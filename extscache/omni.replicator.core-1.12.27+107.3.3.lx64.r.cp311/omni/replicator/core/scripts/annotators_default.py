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

# pylint: disable=too-many-lines, protected-access

import carb
import numpy as np
import omni.usd
import pxr
import usdrt
from omni.syntheticdata import SyntheticData

from .annotators import AnnotatorRegistry
from .settings import REALTIME_ANTIALIASING, RENDER_MODE

NodeTemplate, NodeConnectionTemplate = SyntheticData.NodeTemplate, SyntheticData.NodeConnectionTemplate


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


def on_depth_sensor_attach(node):
    stage = omni.usd.get_context().get_stage()
    with pxr.Usd.EditContext(stage, stage.GetSessionLayer()):
        upstream_node = node.get_attribute("inputs:renderResults").get_upstream_connections()[0].get_node()
        render_product_path = upstream_node.get_attribute("inputs:renderProductPath").get()
        render_product = omni.usd.get_context().get_stage().GetPrimAtPath(render_product_path)

        # Ensure render product has depth sensor API
        if not render_product.HasAPI("OmniSensorDepthSensorSingleViewAPI"):
            carb.log_info(f"Applying 'OmniSensorDepthSensorSingleViewAPI' schema to {render_product_path}")
            render_product.ApplyAPI("OmniSensorDepthSensorSingleViewAPI")

        # Enable depth sensor
        if not render_product.GetAttribute("omni:rtx:post:depthSensor:enabled").Get():
            carb.log_info(f"Enabling depth sensor for render product {render_product_path}")
            render_product.GetAttribute("omni:rtx:post:depthSensor:enabled").Set(True)

    # Depth sensor requires that the omni.usd.schema.render_settings.rtx extension be enabled
    ext_manager = omni.kit.app.get_app().get_extension_manager()
    is_enabled = ext_manager.is_extension_enabled("omni.usd.schema.render_settings.rtx")
    if not is_enabled:
        carb.log_info("Enabling omni.usd.schema.render_settings.rtx extension")
        ext_manager.set_extension_enabled("omni.usd.schema.render_settings.rtx", True)

    # To read render settings from USD/Fabric, ensure the following flags are enabled
    carb.settings.get_settings().set("/app/hydra/renderSettings/useUsdAttributes", True)
    carb.settings.get_settings().set("/app/hydra/renderSettings/useFabricAttributes", True)

    # Remove warning nonce NVBug 5269810 is addressed
    # If the raw color texture does not match the depth sensor texture, an error is raised
    # This prevents the depth sensor from being used with DLSS/DLAA
    carb_settings = carb.settings.get_settings()
    render_mode = carb_settings.get_as_string(RENDER_MODE)
    aa_mode = carb_settings.get_as_int(REALTIME_ANTIALIASING)

    # aa_mode > 2 is DLSS/DLAA
    if render_mode == "RaytracedLighting" and aa_mode > 2:
        carb.log_warn(
            "The first frame produced by the depth sensor may fail to be produced when using raytraced lighting with "
            "DLSS/DLAA. Disable DLSS/DLAA or switch to Pathtracing to avoid this issue."
        )


# Additional AOVs
# Always supported
aovs_common = [
    {"aov": "LdrColor", "output_data_type": np.uint8, "output_channels": 4},
    {"aov": "HdrColor", "output_data_type": np.float16, "output_channels": 4},
    {"aov": "RtxSensorCpu", "output_data_type": np.float32, "output_channels": 1},
    {"aov": "RtxSensorGpu", "output_data_type": np.float32, "output_channels": 1},
    {"aov": "GenericModelOutput", "output_data_type": np.uint8, "output_channels": 1},
    {
        "aov": "DepthSensorDistance",
        "output_data_type": np.float32,
        "output_channels": 1,
        "on_attach_callback": on_depth_sensor_attach,
    },
    {
        "aov": "DepthSensorPointCloudPosition",
        "output_data_type": np.float32,
        "output_channels": 4,
        "on_attach_callback": on_depth_sensor_attach,
    },
    {
        "aov": "DepthSensorPointCloudColor",
        "output_data_type": np.uint8,
        "output_channels": 4,
        "on_attach_callback": on_depth_sensor_attach,
    },
    {
        "aov": "DepthSensorImager",
        "output_data_type": np.float32,
        "output_channels": 1,
        "on_attach_callback": on_depth_sensor_attach,
    },
    {"aov": "RtxSensorMetadata", "output_data_type": np.uint8, "output_channels": 1},
    {"aov": "SemanticOcclusionSD"},
    {"aov": "InstanceIdSegmentationReductionSD"},
    {"aov": "InstanceSegmentationReductionSD"},
    {"aov": "UniqueInstanceSegmentationIdsSD"},
    {
        "aov": "CrossCorrespondenceSD",
        "name": "CrossCorrespondence",
        "output_data_type": np.float32,
        "output_channels": 4,
        "documentation": """
    The cross correspondence annotator outputs a 2D array representing the camera optical flow map of the camera's
    viewport against a reference viewport.

    To enable the cross correspondance annotation, the camera attached to the render product annotated with cross
    correspondance must have the attribute `crossCameraReferenceName` set to the (unique) name (not path) of a second
    camera (itself attached to a second render product). The Projection Type of the two cameras needs to be of type
    `fisheyePolynomial` (Camera --> Fisheye Lens --> Projection Type --> fisheyePolynomial).

    **Output Format**

    The Cross Correspondence annotator produces the cross correspondence between pixels seen from two cameras.

    The components of each entry in the 2D array represent for different values encoded as floating point values:

    * x: dx - difference to the x value of of the corresponding pixel in the reference viewport. This value is
      normalized to ``[-1.0, 1.0]``
    * y: dy - difference to the y value of of the corresponding pixel in the reference viewport.
      This value is normalized to ``[-1.0, 1.0]``
    * z: occlusion mask -  boolean signifying that the pixel is occluded or truncated in one of the cross referenced
      viewports. Floating point value represents a boolean ``(1.0 = True, 0.0 = False)``
    * w: geometric occlusion calculated - boolean signifying that the pixel can or cannot be tested as having occluded
      geometry (e.g. no occlusion testing is performed on missed rays) ``(1.0 = True, 0.0 = False)``

    .. code:: python

        array((height, width, 4), dtype=<np.float32>)

    **Example**

    .. code:: python

        import asyncio
        import omni.replicator.core as rep
        from pxr import Sdf

        async def test_cross_correspondence():
            # Add an object to look at
            rep.create.cone()

            # Add stereo camera pair
            stereo = rep.create.stereo_camera(
                position=(20, 0, 300), projection_type="fisheye_polynomial", stereo_baseline=20
            )

            # Add cross correspondence attribute
            stereo_L_prim = stereo.get_output_prims()["prims"][0].GetChildren()[0].GetChildren()[0]
            stereo_L_prim.CreateAttribute("crossCameraReferenceName", Sdf.ValueTypeNames.String)

            # Set attribute to refer to second camera name - beware of scenes with multiple cameras that share names!
            stereo_L_prim.GetAttribute("crossCameraReferenceName").Set("StereoCam_R")

            render_products = rep.create.render_product(stereo, (512, 512))

            # Add annotator to left render product
            anno = rep.annotators.get("cross_correspondence")
            anno.attach(render_products[0])

            await rep.orchestrator.step_async()
            data = anno.get_data()
            print(data.shape, data.dtype)
            # (512, 512, 4), float32

        asyncio.ensure_future(test_cross_correspondence())

    .. note::

        * Both cameras must have the `cameraProjectionType` attribute set to `fisheyePolynomial`
        * The annotated camera must have the `crossCameraReferenceName` attribute set to the *name* of the second camera
        * To avoid unexpected results, ensure that the referenced camera has a unique name
    """,
    },
    {
        "aov": "TargetMotionSD",
        "name": "MotionVectors",
        "output_data_type": np.float32,
        "output_channels": 4,
        "documentation": """
    Outputs a 2D array of motion vectors representing the relative motion of a pixel in the camera's viewport between
    frames.

    The MotionVectors annotator returns the per-pixel motion vectors in in image space.

    **Output Format**

    .. code:: python

        array((height, width, 4), dtype=<np.float32>)

    The components of each entry in the 2D array represent for different values encoded as floating point values:

    * x: motion distance in the horizontal axis (image width) with movement to the left of the image being positive and
      movement to the right being negative.
    * y: motion distance in the vertical axis (image height) with movement towards the top of the image being positive
      and movement to the bottom being negative.
    * z: unused
    * w: unused

    **Example**

    .. code:: python

        import asyncio
        import omni.replicator.core as rep

        async def test_motion_vectors():
            # Add an object to look at
            cone = rep.create.cone()

            # Add motion to object
            cone_prim = cone.get_output_prims()["prims"][0]
            cone_prim.GetAttribute("xformOp:translate").Set((-100, 0, 0), time=0.0)
            cone_prim.GetAttribute("xformOp:translate").Set((100, 50, 0), time=10.0)

            camera = rep.create.camera()
            render_product = rep.create.render_product(camera, (512, 512))

            motion_vectors_anno = rep.annotators.get("MotionVectors")
            motion_vectors_anno.attach(render_product)

            # Take a step to render the initial state (no movement yet)
            await rep.orchestrator.step_async()

            # Capture second frame (now the timeline is playing)
            await rep.orchestrator.step_async()
            data = motion_vectors_anno.get_data()
            print(data.shape, data.dtype, data.reshape(-1, 4).min(axis=0), data.reshape(-1, 4).max(axis=0))
            # (1024, 512, 4), float32,  [-93.80073 -1.      -1.      -1.     ] [ 0.      23.450201  1.       1.      ]

        asyncio.ensure_future(test_motion_vectors())

    .. note::

        The values represent motion relative to camera space.
    """,
    },
]

# Ray Tracing AOVs
aovs_rt = [
    {"aov": "SmoothNormal", "output_data_type": np.float32, "output_channels": 4},
    {"aov": "BumpNormal", "output_data_type": np.float32, "output_channels": 4},
    {"aov": "AmbientOcclusion", "output_data_type": np.float16, "output_channels": 4},
    {"aov": "Motion2d", "output_data_type": np.float32, "output_channels": 4},
    {"aov": "DiffuseAlbedo", "output_data_type": np.uint8, "output_channels": 4},
    {"aov": "SpecularAlbedo", "output_data_type": np.float16, "output_channels": 4},
    {"aov": "Roughness", "output_data_type": np.uint8, "output_channels": 4},
    {"aov": "DirectDiffuse", "output_data_type": np.float16, "output_channels": 4},
    {"aov": "DirectSpecular", "output_data_type": np.float16, "output_channels": 4},
    {"aov": "Reflections", "output_data_type": np.float32, "output_channels": 4},
    {"aov": "IndirectDiffuse", "output_data_type": np.float16, "output_channels": 4},
    {"aov": "DepthLinearized", "output_data_type": np.float32, "output_channels": 1},
    {"aov": "EmissionAndForegroundMask", "output_data_type": np.float16, "output_channels": 1},
]

# Path Tracing AOVs
aovs_pt = [
    {"aov": "PtDirectIllumation", "output_data_type": np.float16, "output_channels": 4},
    {"aov": "PtGlobalIllumination", "output_data_type": np.float16, "output_channels": 4},
    {"aov": "PtReflections", "output_data_type": np.float16, "output_channels": 4},
    {"aov": "PtRefractions", "output_data_type": np.float16, "output_channels": 4},
    {"aov": "PtSelfIllumination", "output_data_type": np.float16, "output_channels": 4},
    {"aov": "PtBackground", "output_data_type": np.float16, "output_channels": 4},
    {"aov": "PtWorldNormal", "output_data_type": np.float16, "output_channels": 4},
    {"aov": "PtWorldPos", "output_data_type": np.float16, "output_channels": 4},
    {"aov": "PtZDepth", "output_data_type": np.float16, "output_channels": 4},
    {"aov": "PtVolumes", "output_data_type": np.float16, "output_channels": 4},
    {"aov": "PtDiffuseFilter", "output_data_type": np.float16, "output_channels": 4},
    {"aov": "PtReflectionFilter", "output_data_type": np.float16, "output_channels": 4},
    {"aov": "PtRefractionFilter", "output_data_type": np.float16, "output_channels": 4},
    {"aov": "PtMultiMatte0", "output_data_type": np.float16, "output_channels": 4},
    {"aov": "PtMultiMatte1", "output_data_type": np.float16, "output_channels": 4},
    {"aov": "PtMultiMatte2", "output_data_type": np.float16, "output_channels": 4},
    {"aov": "PtMultiMatte3", "output_data_type": np.float16, "output_channels": 4},
    {"aov": "PtMultiMatte4", "output_data_type": np.float16, "output_channels": 4},
    {"aov": "PtMultiMatte5", "output_data_type": np.float16, "output_channels": 4},
    {"aov": "PtMultiMatte6", "output_data_type": np.float16, "output_channels": 4},
    {"aov": "PtMultiMatte7", "output_data_type": np.float16, "output_channels": 4},
]

aovs_sensor_rtx = [
    {"aov": "RtxSensorCpu", "output_data_type": np.uint8, "output_channels": 1, "is_gpu_enabled": False},
    {"aov": "RtxSensorGpu", "output_data_type": np.uint8, "output_channels": 1, "is_gpu_enabled": False},
    {"aov": "GenericModelOutput", "output_data_type": np.uint8, "output_channels": 1, "is_gpu_enabled": False},
    {"aov": "RtxSensorMetadata", "output_data_type": np.uint8, "output_channels": 1, "is_gpu_enabled": False},
    {"aov": "SemanticBoundingBox2DTight", "output_data_type": np.uint8, "output_channels": 1, "is_gpu_enabled": False},
    {"aov": "SemanticBoundingBox2DLoose", "output_data_type": np.uint8, "output_channels": 1, "is_gpu_enabled": False},
    {"aov": "SemanticBoundingBox3D", "output_data_type": np.uint8, "output_channels": 1, "is_gpu_enabled": False},
    {"aov": "SemanticIdMap", "output_data_type": np.uint8, "output_channels": 1, "is_gpu_enabled": False},
    {"aov": "StableIdMap", "output_data_type": np.uint8, "output_channels": 1, "is_gpu_enabled": False},
    {"aov": "StableIdSemanticIdMap", "output_data_type": np.uint8, "output_channels": 1, "is_gpu_enabled": False},
    # {"aov": "CameraParams", "output_data_type": np.uint8, "output_channels": 1}, #TODO: Conflicts with replicator CameraParams annotator
    {"aov": "StableIdMapDeltas", "output_data_type": np.uint8, "output_channels": 1, "is_gpu_enabled": False},
    {"aov": "SemanticIdMapDeltas", "output_data_type": np.uint8, "output_channels": 1, "is_gpu_enabled": False},
]

aovs_sensor_rtx_texture = [
    {"aov": "SemanticSegmentation", "output_data_type": np.uint8, "output_channels": 1},
    {"aov": "SemanticInstanceSegmentation", "output_data_type": np.uint8, "output_channels": 1},
    {"aov": "StableIdSegmentation", "output_data_type": np.uint8, "output_channels": 1},
]

post_render_annotators = [
    # --- InstanceSeg Post Render
    {
        "name": "InstanceSegmentationPostRender",
        "input_rendervars": [
            NodeConnectionTemplate("InstanceSegmentationSD"),
            NodeConnectionTemplate("InstanceMappingPost"),
        ],
        "node_type_id": "omni.replicator.core.InstanceSegmentationReduction",
        "hidden": True,
    },
    {
        "name": "SemanticOcclusionPostRender",
        "input_rendervars": [NodeConnectionTemplate("OcclusionSD"), NodeConnectionTemplate("InstanceMappingPost")],
        "node_type_id": "omni.replicator.core.SemanticOcclusionReduction",
        "hidden": True,
    },
    # --- InstanceIdSeg
    {
        "name": "InstanceIdSegmentationPostRender",
        "input_rendervars": [
            NodeConnectionTemplate("InstanceSegmentationSD"),
            NodeConnectionTemplate("InstanceMappingPost"),
        ],
        "node_type_id": "omni.replicator.core.InstanceIdSegmentationReduction",
        "hidden": True,
    },
]


node_annotators = [
    {
        "name": "rpFabricTime",
        "input_rendervars": [
            NodeConnectionTemplate(
                "PostProcessDispatch",
                attributes_mapping={
                    "outputs:exec": "inputs:exec",
                    "outputs:renderResults": "inputs:rp",
                },
            ),
        ],
        "node_type_id": "omni.replicator.core.ReadRpFabricTime",
    },
    {
        "name": "fabricTime",
        "input_rendervars": [],
        "node_type_id": "omni.replicator.core.ReadFabricTime",
    },
    {
        "name": "primPaths",
        "input_rendervars": ["InstanceMappingPtr"],
        "node_type_id": "omni.replicator.core.OgnPrimPaths",
    },
    # --- BBox2DTight
    {
        "name": "bounding_box_2d_tight_fast",
        "input_rendervars": [
            NodeConnectionTemplate(
                "SemanticBoundingBox2DExtentTightSDhostPtr",
                attributes_mapping={
                    "outputs:dataPtr": "inputs:dataPtr",
                    "outputs:bufferSize": "inputs:bufferSize",
                },
            ),
            "InstanceMappingPtr",
            "primPaths",
            NodeConnectionTemplate(
                "SemanticOcclusionSDhostPtr",
                attributes_mapping={
                    "outputs:dataPtr": "inputs:semanticOcclusionPtr",
                },
            ),
        ],
        "node_type_id": "omni.replicator.core.BoundingBox2D",
        "output_data_type": np.dtype(
            [
                ("semanticId", "<u4"),
                ("x_min", "<i4"),
                ("y_min", "<i4"),
                ("x_max", "<i4"),
                ("y_max", "<i4"),
                ("occlusionRatio", "<f4"),
            ]
        ),
        "output_is_2d": False,
        "is_gpu_enabled": False,
        "documentation": """Outputs tight 2d bounding box of each entity with semantics in the camera's viewport. Tight
        bounding boxes bound only the visible pixels of entities. Completely occluded entities are ommited.

    **Initialization Parameters**

    * semanticTypes: List of allowed semantic types the types. For example, if semantic_types is ``["class"]``, only the
      bounding boxes for prims with semantics of type ``"class"`` will be retrieved.
    * semanticFilter: String expressing semantif filter predicate. For example, filter ``"class:car|pedestrian"`` will return only the
      bounding boxes with the semantic type ``"class"`` and with a value of either ``"car"`` or ``"pedestrian"``.

    **Output Format**

    The bounding box annotator returns a dictionary with the bounds and semantic id found under the "data" key, while
    other information is under the "info" key: "idToLabels", "bboxIds" and "primPaths".

    .. code:: python

        {
            "data": np.dtype(
                [
                    ("semanticId", "<u4"),
                    ("x_min", "<i4"),
                    ("y_min", "<i4"),
                    ("x_max", "<i4"),
                    ("y_max", "<i4"),
                ],
            "info": {
                "idToLabels": {<semanticId>: <semantic_labels>},    # mapping from integer semantic ID to a comma
                                                                    # delimited list of associated semantics
                "bboxIds": [<bbox_id_0>, ..., <bbox_id_n>],         # ID specific to bounding box annotators allowing
                                                                    # easy mapping between different bounding box
                                                                    # annotators.
                "primPaths": [<prim_path_0>, ... <prim_path_n>],    # prim path tied to each bounding box
            }
        }

    .. note::

            `bounding_box_2d_tight_fast` bounds only visible pixels.

    **Example**

    .. code:: python

        import omni.replicator.core as rep

        async def test_bbox_2d_tight_fast():
            cone = rep.create.cone(semantics=[("prim", "cone")], position=(100, 0, 0))
            sphere = rep.create.sphere(semantics=[("prim", "sphere")], position=(-100, 0, 0))
            invalid_type = rep.create.cube(semantics=[("shape", "boxy")], position=(0, 100, 0))

            cam = rep.create.camera(position=(500,500,500), look_at=cone)
            rp = rep.create.render_product(cam, (1024, 512))

            bbox_2d_tight_fast = rep.AnnotatorRegistry.get_annotator(
                "bounding_box_2d_tight_fast", init_params={"semanticFilter": "*:cone|boxy"}
            )
            bbox_2d_tight_fast.attach(rp)

            await rep.orchestrator.step_async()
            data = bbox_2d_tight_fast.get_data()
            print(data)
            # {
            #     'data': array([
            #         (0, 442, 198, 581, 357, 0.),
            #         (1, 284,   0, 500, 203, 0.)],
            #         dtype=[('semanticId', '<u4'),
            #                ('x_min', '<i4'),
            #                ('y_min', '<i4'),
            #                ('x_max', '<i4'),
            #                ('y_max', '<i4'),
            #                ('occlusionRatio', '<f4')]),
            #     'info': {
            #         'bboxIds': array([0, 2], dtype=uint32),
            #         'idToLabels': {0: {'prim': 'cone'}, 1: {'shape': 'boxy'}},
            #         'primPaths': ['/Replicator/Cone_Xform', '/Replicator/Cube_Xform']
            #     }
            # }

        import asyncio
        asyncio.ensure_future(test_bbox_2d_tight_fast())
    """,
    },
    {
        "name": "bounding_box_2d_tight",
        "input_rendervars": ["bounding_box_2d_tight_fast"],
        "node_type_id": "omni.replicator.core.BoundingBoxLegacy",
        "output_data_type": np.dtype(
            [
                ("semanticId", "<u4"),
                ("x_min", "<i4"),
                ("y_min", "<i4"),
                ("x_max", "<i4"),
                ("y_max", "<i4"),
                ("occlusionRatio", "<f4"),
            ]
        ),
        "output_is_2d": False,
        "is_gpu_enabled": False,
        "documentation": """Outputs tight 2d bounding box of each entity with semantics in the camera's viewport. Tight
        bounding boxes bound only the visible pixels of entities. Completely occluded entities are ommited.

    **Initialization Parameters**

    * semanticTypes: List of allowed semantic types the types. For example, if semantic_types is ``["class"]``, only the
      bounding boxes for prims with semantics of type ``"class"`` will be retrieved.
    * semanticFilter: String expressing semantif filter predicate. For example, filter ``"class:car|pedestrian"`` will return only the
      bounding boxes with the semantic type ``"class"`` and with a value of either ``"car"`` or ``"pedestrian"``.

    **Output Format**

    The bounding box annotator returns a dictionary with the bounds and semantic id found under the "data" key, while
    other information is under the "info" key: "idToLabels", "bboxIds" and "primPaths".

    .. code:: python

        {
            "data": np.dtype(
                [
                    ("semanticId", "<u4"),
                    ("x_min", "<i4"),
                    ("y_min", "<i4"),
                    ("x_max", "<i4"),
                    ("y_max", "<i4"),
                    ("occlusionRatio", "<f4"),
                ],
            "info": {
                "idToLabels": {<semanticId>: <semantic_labels>},    # mapping from integer semantic ID to a comma
                                                                    # delimited list of associated semantics
                "bboxIds": [<bbox_id_0>, ..., <bbox_id_n>],         # ID specific to bounding box annotators allowing
                                                                    # easy mapping between different bounding box
                                                                    # annotators.
                "primPaths": [<prim_path_0>, ... <prim_path_n>],    # prim path tied to each bounding box
            }
        }

    .. note::

        `bounding_box_2d_tight` bounds only visible pixels.

    **Example**

    .. code:: python

        import omni.replicator.core as rep

        async def test_bbox_2d_tight():
            cone = rep.create.cone(semantics=[("prim", "cone")], position=(100, 0, 0))
            sphere = rep.create.sphere(semantics=[("prim", "sphere")], position=(-100, 0, 0))
            invalid_type = rep.create.cube(semantics=[("shape", "boxy")], position=(0, 100, 0))

            cam = rep.create.camera(position=(500,500,500), look_at=cone)
            rp = rep.create.render_product(cam, (1024, 512))

            bbox_2d_tight = rep.AnnotatorRegistry.get_annotator(
                "bounding_box_2d_tight", init_params={"semanticFilter": "*:cone|boxy"}
            )
            bbox_2d_tight.attach(rp)

            await rep.orchestrator.step_async()
            data = bbox_2d_tight.get_data()
            print(data)
            # {
            #     'data': array([
            #         (0, 442, 198, 581, 357, 0.),
            #         (1, 284,   0, 500, 203, 0.)],
            #         dtype=[('semanticId', '<u4'),
            #                ('x_min', '<i4'),
            #                ('y_min', '<i4'),
            #                ('x_max', '<i4'),
            #                ('y_max', '<i4'),
            #                ('occlusionRatio', '<f4')]),
            #     'info': {
            #         'bboxIds': array([0, 2], dtype=uint32),
            #         'idToLabels': {0: {'prim': 'cone'}, 1: {'shape': 'boxy'}},
            #         'primPaths': ['/Replicator/Cone_Xform', '/Replicator/Cube_Xform']
            #     }
            # }

        import asyncio
        asyncio.ensure_future(test_bbox_2d_tight())
    """,
    },
    # --- BBox2DLoose
    {
        "name": "bounding_box_2d_loose_fast",
        "input_rendervars": [
            NodeConnectionTemplate(
                "SemanticBoundingBox2DExtentLooseSDhostPtr",
                attributes_mapping={
                    "outputs:dataPtr": "inputs:dataPtr",
                    "outputs:bufferSize": "inputs:bufferSize",
                },
            ),
            "InstanceMappingPtr",
            "InstanceMapping",
            "primPaths",
            NodeConnectionTemplate(
                "SemanticOcclusionSDhostPtr",
                attributes_mapping={
                    "outputs:dataPtr": "inputs:semanticOcclusionPtr",
                },
            ),
        ],
        "node_type_id": "omni.replicator.core.BoundingBox2D",
        "output_data_type": np.dtype(
            [
                ("semanticId", "<u4"),
                ("x_min", "<i4"),
                ("y_min", "<i4"),
                ("x_max", "<i4"),
                ("y_max", "<i4"),
                ("occlusionRatio", "<f4"),
            ]
        ),
        "output_is_2d": False,
        "is_gpu_enabled": False,
        "documentation": """Outputs loose 2d bounding box of each entity with semantics in the camera's field of view.
        Loose bounding boxes bound the entire entity regardless of occlusions.

    **Initialization Parameters**

    * semanticTypes: List of allowed semantic types the types. For example, if semantic_types is ``["class"]``, only the
      bounding boxes for prims with semantics of type ``"class"`` will be retrieved.
    * semanticFilter: String expressing semantif filter predicate. For example, filter ``"class:car|pedestrian"`` will return only the
      bounding boxes with the semantic type ``"class"`` and with a value of either ``"car"`` or ``"pedestrian"``.

    **Output Format**

    The bounding box annotator returns a dictionary with the bounds and semantic id found under the "data" key, while
    other information is under the "info" key: "idToLabels", "bboxIds" and "primPaths".

    .. code:: python

        {
            "data": np.dtype(
                [
                    ("semanticId", "<u4"),
                    ("x_min", "<i4"),
                    ("y_min", "<i4"),
                    ("x_max", "<i4"),
                    ("y_max", "<i4"),
                    ("occlusionRatio", "<f4"),
                ],
            "info": {
                "idToLabels": {<semanticId>: <semantic_labels>},    # mapping from integer semantic ID to a comma
                                                                    # delimited list of associated semantics
                "bboxIds": [<bbox_id_0>, ..., <bbox_id_n>],         # ID specific to bounding box annotators allowing
                                                                    # easy mapping between different bounding box
                                                                    # annotators.
                "primPaths": [<prim_path_0>, ... <prim_path_n>],    # prim path tied to each bounding box
            }
        }

    .. note::

        `bounding_box_2d_loose` will produce the loose 2d bounding box of any prim in the viewport, no matter
        if is partially occluded or fully occluded.

    **Example**

    .. code:: python

        import omni.replicator.core as rep

        async def test_bbox_2d_loose_fast():
            cone = rep.create.cone(semantics=[("prim", "cone")], position=(100, 0, 0))
            sphere = rep.create.sphere(semantics=[("prim", "sphere")], position=(-100, 0, 0))
            invalid_type = rep.create.cube(semantics=[("shape", "boxy")], position=(0, 100, 0))

            cam = rep.create.camera(position=(500,500,500), look_at=cone)
            rp = rep.create.render_product(cam, (1024, 512))

            bbox_2d_loose_fast = rep.AnnotatorRegistry.get_annotator(
                "bounding_box_2d_loose_fast",
                init_params={"semanticFilter": "prim:*"},
            )
            bbox_2d_loose_fast.attach(rp)

            await rep.orchestrator.step_async()
            data = bbox_2d_loose_fast.get_data()
            print(data)
            # {
            #     'data': array([
            #         (0, 442, 198, 581, 357, 0.),
            #         (1, 245,  92, 375, 220, 0.3823)],
            #         dtype=[('semanticId', '<u4'),
            #                ('x_min', '<i4'),
            #                ('y_min', '<i4'),
            #                ('x_max', '<i4'),
            #                ('y_max', '<i4'),
            #                ('occlusionRatio', '<f4')]),
            #     'info': {
            #         'bboxIds': array([0, 2], dtype=uint32),
            #         'idToLabels': {0: {'prim': 'cone'}, 1: {'shape': 'boxy'}},
            #         'primPaths': ['/Replicator/Cone_Xform', '/Replicator/Cube_Xform']
            #     }
            # }

        import asyncio
        asyncio.ensure_future(test_bbox_2d_loose_fast())
    """,
    },
    {
        "name": "bounding_box_2d_loose",
        "input_rendervars": ["bounding_box_2d_loose_fast"],
        "node_type_id": "omni.replicator.core.BoundingBoxLegacy",
        "output_data_type": np.dtype(
            [
                ("semanticId", "<u4"),
                ("x_min", "<i4"),
                ("y_min", "<i4"),
                ("x_max", "<i4"),
                ("y_max", "<i4"),
                ("occlusionRatio", "<f4"),
            ]
        ),
        "output_is_2d": False,
        "is_gpu_enabled": False,
        "documentation": """Outputs loose 2d bounding box of each entity with semantics in the camera's field of view.
        Loose bounding boxes bound the entire entity regardless of occlusions.

    **Initialization Parameters**

    * semanticTypes: List of allowed semantic types the types. For example, if semantic_types is ``["class"]``, only the
      bounding boxes for prims with semantics of type ``"class"`` will be retrieved.
    * semanticFilter: String expressing semantif filter predicate. For example, filter ``"class:car|pedestrian"`` will return only the
      bounding boxes with the semantic type ``"class"`` and with a value of either ``"car"`` or ``"pedestrian"``.

    **Output Format**

    The bounding box annotator returns a dictionary with the bounds and semantic id found under the "data" key, while
    other information is under the "info" key: "idToLabels", "bboxIds" and "primPaths".

    .. code:: python

        {
            "data": np.dtype(
                [
                    ("semanticId", "<u4"),
                    ("x_min", "<i4"),
                    ("y_min", "<i4"),
                    ("x_max", "<i4"),
                    ("y_max", "<i4"),
                    ("occlusionRatio", "<f4"),
                ],
            "info": {
                "idToLabels": {<semanticId>: <semantic_labels>},    # mapping from integer semantic ID to a comma
                                                                    # delimited list of associated semantics
                "bboxIds": [<bbox_id_0>, ..., <bbox_id_n>],         # ID specific to bounding box annotators allowing
                                                                    # easy mapping between different bounding box
                                                                    # annotators.
                "primPaths": [<prim_path_0>, ... <prim_path_n>],    # prim path tied to each bounding box
            }
        }

    .. note::

        `bounding_box_2d_loose` will produce the loose 2d bounding box of any prim in the viewport, no matter if
        is partially occluded or fully occluded.

    **Example**

    .. code:: python

        import omni.replicator.core as rep

        async def test_bbox_2d_loose():
            cone = rep.create.cone(semantics=[("prim", "cone")], position=(100, 0, 0))
            sphere = rep.create.sphere(semantics=[("prim", "sphere")], position=(-100, 0, 0))
            invalid_type = rep.create.cube(semantics=[("shape", "boxy")], position=(0, 100, 0))

            cam = rep.create.camera(position=(500,500,500), look_at=cone)
            rp = rep.create.render_product(cam, (1024, 512))

            bbox_2d_loose = rep.AnnotatorRegistry.get_annotator(
                "bounding_box_2d_loose", init_params={"semanticFilter": "prim:*"},
            )
            bbox_2d_loose.attach(rp)

            await rep.orchestrator.step_async()
            data = bbox_2d_loose.get_data()
            print(data)
            # {
            #   'data': array([
            #       (0, 442, 198, 581, 357, 0.),
            #       (1, 245,  92, 375, 220, 0.38),
            #       dtype=[('semanticId', '<u4'),
            #              ('x_min', '<i4'),
            #              ('y_min', '<i4'),
            #              ('x_max', '<i4'),
            #              ('y_max', '<i4')]),
            #              ("occlusionRatio", "<f4"),
            #   'info': {
            #       'bboxIds': array([0, 1], dtype=uint32),
            #       'idToLabels': {'0': {'prim': 'cone'}, '1': {'prim': 'sphere'}},
            #       'primPaths': ['/Replicator/Cone_Xform', '/Replicator/Sphere_Xform']}
            #   }
            # }

        import asyncio
        asyncio.ensure_future(test_bbox_2d_loose())
    """,
    },
    # --- BBox3D
    {
        "name": "bounding_box_3d_360",
        "input_rendervars": [
            NodeConnectionTemplate(
                "SemanticBoundingBox3DExtentSDhostPtr",
                attributes_mapping={
                    "outputs:dataPtr": "inputs:dataPtr",
                    "outputs:bufferSize": "inputs:bufferSize",
                },
            ),
            NodeConnectionTemplate(
                "SemanticBoundingBox3DInfosSDhostPtr",
                attributes_mapping={
                    "outputs:dataPtr": "inputs:filteredBboxInfoPtr",
                },
            ),
            NodeConnectionTemplate(
                "SemanticOcclusionSDhostPtr",
                attributes_mapping={
                    "outputs:dataPtr": "inputs:semanticOcclusionPtr",
                },
            ),
            "InstanceMappingPtrWithTransforms",
            "InstanceMapping",
            "primPaths",
        ],
        "node_type_id": "omni.replicator.core.BoundingBox3D",
        "output_data_type": np.dtype(
            [
                ("semanticId", "<u4"),
                ("x_min", "<f4"),
                ("y_min", "<f4"),
                ("z_min", "<f4"),
                ("x_max", "<f4"),
                ("y_max", "<f4"),
                ("z_max", "<f4"),
                ("transform", "<f4", (4, 4)),
                ("occlusionRatio", "<f4"),
            ]
        ),
        "output_is_2d": False,
        "is_gpu_enabled": False,
        "documentation": """Outputs 3D bounding box of each entity with semantics for the entire world including outside
        the sensor's field of view

    **Initialization Parameters**

    * semanticFilter: String expressing semantif filter predicate. For example, filter ``"class:car|pedestrian"`` will return only the
      bounding boxes with the semantic type ``"class"`` and with a value of either ``"car"`` or ``"pedestrian"``.

    **Output Format**

    The bounding box annotator returns a dictionary with the bounds and semantic id found under the "data" key, while
    other information is under the "info" key: "idToLabels", "bboxIds" and "primPaths".

    .. code:: python

        {
            "data": np.dtype(
                [
                    ('x_min', '<f4'),               # Min bound in x axis in local ref frame (in world units)
                    ('y_min', '<f4'),               # Min bound in y axis in local ref frame (in world units)
                    ('z_min', '<f4'),               # Min bound in z axis in local ref frame (in world units)
                    ('x_max', '<f4'),               # Max bound in x axis in local ref frame (in world units)
                    ('y_max', '<f4'),               # Max bound in y axis in local ref frame (in world units)
                    ('z_max', '<f4'),               # Max bound in z axis in local ref frame (in world units)
                    ('transform', '<f4', (4, 4)),   # World to local transformation matrix (transforms the
                                                    # bounds from world frame to local frame)
                    ('occlusionRatio', '<f4')]),    # Occlusion (visible pixels / total pixels), where `0.0` is
                                                    # fully visible and `1.0` is fully occluded. See additional
                                                    # notes below.
                ],
            "info": {
                "idToLabels": {<semanticId>: <semantic_labels>},    # mapping from integer semantic ID to a comma
                                                                    # delimited list of associated semantics
                "bboxIds": [<bbox_id_0>, ..., <bbox_id_n>],         # ID specific to bounding box annotators allowing
                                                                    # easy mapping between different bounding box
                                                                    # annotators.
                "primPaths": [<prim_path_0>, ... <prim_path_n>],    # prim path tied to each bounding box
            }
        }

    .. note::

        * bounding boxes are retrieved regardless of occlusion.
        * bounding box dimensions (<axis>_min, <axis>_max) are expressed in stage units.
        * ``occlusionRatio`` can only provide valid values for prims composed of a single mesh. Multi-mesh
          labelled prims will return a value of -1 indicating that no occlusion value is available.

    **Example**

    .. code:: python

        import omni.replicator.core as rep

        async def test_bbox_3d_360():
            cone = rep.create.cone(semantics=[("prim", "cone")], position=(100, 0, 0))
            sphere = rep.create.sphere(semantics=[("prim", "sphere")], position=(-100, 0, 0))
            cube = rep.create.cube(semantics=[("prim", "cube")], position=(1000, 1000, 1000))

            cam = rep.create.camera(position=(500,500,500), look_at=cone)
            rp = rep.create.render_product(cam, (1024, 512))

            bbox_3d_360 = rep.AnnotatorRegistry.get_annotator("bounding_box_3d_360")
            bbox_3d_360.attach(rp)

            await rep.orchestrator.step_async()
            data = bbox_3d_360.get_data()
            print(data)
            #   {
            #       'data': array([
            #           (
            #               0,
            #               -50.,
            #               -50.,
            #               50.,
            #               50.,
            #               50.,
            #               [
            #                   [   1.,    0.,    0.,    0.],
            #                   [   0.,    1.,    0.,    0.],
            #                   [   0.,    0.,    1.,    0.],
            #                   [ 100.,    0.,    0.,    1.]
            #               ],
            #               0.
            #           ),
            #           (
            #               1,
            #               -50.,
            #               -50.,
            #               -50.,
            #               50.,
            #               50.,
            #               50.,
            #               [
            #                  [   1.,    0.,    0.,    0.],
            #                  [   0.,    1.,    0.,    0.],
            #                  [   0.,    0.,    1.,    0.],
            #                  [-100.,    0.,    0.,    1.]
            #               ],
            #               0.38
            #           ),
            #           (
            #               2,
            #               -50.,
            #               -50.,
            #               -50.,
            #               50.,
            #               50.,
            #               50.,
            #               [
            #                  [   1.,    0.,    0.,    0.],
            #                  [   0.,    1.,    0.,    0.],
            #                  [   0.,    0.,    1.,    0.],
            #                  [1000., 1000., 1000.,    1.]
            #               ],
            #               nan
            #           ),
            #               ],
            #           dtype=[
            #               ('semanticId', '<u4'),
            #               ('x_min', '<f4'),
            #               ('y_min', '<f4'),
            #               ('z_min', '<f4'),
            #               ('x_max', '<f4'),
            #               ('y_max', '<f4'),
            #               ('z_max', '<f4'),
            #               ('transform', '<f4', (4, 4)),
            #               ('occlusionRatio', '<f4')]),
            #       'info': {
            #           'bboxIds': array([0, 1, 2], dtype=uint32),
            #           'idToLabels': {0: {'prim': 'cone'}, 1: {'prim': 'sphere'}, 2: {'prim': 'cube'}},
            #           'primPaths': ['/Replicator/Cone_Xform', '/Replicator/Sphere_Xform', '/Replicator/Cube_Xform']
            #       }
            #   }

        import asyncio
        asyncio.ensure_future(test_bbox_3d_360())

    """,
    },
    {
        "name": "bounding_box_3d_fast",
        "input_rendervars": [
            NodeConnectionTemplate(
                "SemanticBoundingBox3DExtentSDhostPtr",
                attributes_mapping={
                    "outputs:dataPtr": "inputs:dataPtr",
                    "outputs:bufferSize": "inputs:bufferSize",
                },
            ),
            NodeConnectionTemplate(
                "SemanticBoundingBox3DFilterInfosSDhostPtr",
                attributes_mapping={
                    "outputs:dataPtr": "inputs:filteredBboxInfoPtr",
                },
            ),
            NodeConnectionTemplate(
                "SemanticOcclusionSDhostPtr",
                attributes_mapping={
                    "outputs:dataPtr": "inputs:semanticOcclusionPtr",
                },
            ),
            "InstanceMappingPtrWithTransforms",
            "primPaths",
        ],
        "node_type_id": "omni.replicator.core.BoundingBox3D",
        "output_data_type": np.dtype(
            [
                ("semanticId", "<u4"),
                ("x_min", "<f4"),
                ("y_min", "<f4"),
                ("z_min", "<f4"),
                ("x_max", "<f4"),
                ("y_max", "<f4"),
                ("z_max", "<f4"),
                ("transform", "<f4", (4, 4)),
                ("occlusionRatio", "<f4"),
            ]
        ),
        "output_is_2d": False,
        "is_gpu_enabled": False,
        "documentation": """Outputs 3D bounding box of each entity with semantics for entities within the sensor's field
        of view.

    **Initialization Parameters**

    * semanticFilter: String expressing semantif filter predicate. For example, filter ``"class:car|pedestrian"`` will return only the
      bounding boxes with the semantic type ``"class"`` and with a value of either ``"car"`` or ``"pedestrian"``.

    **Output Format**

    The bounding box annotator returns a dictionary with the bounds and semantic id found under the "data" key, while
    other information is under the "info" key: "idToLabels", "bboxIds" and "primPaths".

    .. code:: python

        {
            "data": np.dtype(
                [
                    ("semanticId", "<u4"),
                    ("x_min", "<i4"),
                    ("y_min", "<i4"),
                    ("x_max", "<i4"),
                    ("y_max", "<i4"),
                    ("z_min", "<i4"),
                    ("z_max", "<i4"),
                    ("transform", "<i4"),
                ],
            "info": {
                "idToLabels": {<semanticId>: <semantic_labels>},    # mapping from integer semantic ID to a comma
                                                                    # delimited list of associated semantics
                "bboxIds": [<bbox_id_0>, ..., <bbox_id_n>],         # ID specific to bounding box annotators allowing
                                                                    # easy mapping between different bounding box
                                                                    # annotators.
                "primPaths": [<prim_path_0>, ... <prim_path_n>],    # prim path tied to each bounding box
            }
        }

    .. note::

        * bounding boxes are retrieved regardless of occlusion.
        * bounding box dimensions (<axis>_min, <axis>_max) are expressed in stage units.

    **Example**

    .. code:: python

        import omni.replicator.core as rep

        async def test_bbox_3d_fast():
            cone = rep.create.cone(semantics=[("prim", "cone")], position=(100, 0, 0))
            sphere = rep.create.sphere(semantics=[("prim", "sphere")], position=(-100, 0, 0))
            cube = rep.create.cube(semantics=[("prim", "cube")], position=(1000, 1000, 1000))

            cam = rep.create.camera(position=(500,500,500), look_at=cone)
            rp = rep.create.render_product(cam, (1024, 512))

            bbox_3d_fast = rep.AnnotatorRegistry.get_annotator("bounding_box_3d_fast")
            bbox_3d_fast.attach(rp)

            await rep.orchestrator.step_async()
            data = bbox_3d_fast.get_data()
            print(data)
            #   {
            #       'data': array([
            #           (
            #               0,
            #               -50.,
            #               -50.,
            #               -50.,
            #               50.,
            #               50.,
            #               50.,
            #               [
            #                   [   1.,    0.,    0.,    0.],
            #                   [   0.,    1.,    0.,    0.],
            #                   [   0.,    0.,    1.,    0.],
            #                   [ 100.,    0.,    0.,    1.]
            #               ],
            #               0.
            #           ),
            #           (
            #               1,
            #               -50.,
            #               -50.,
            #               -50.,
            #               50.,
            #               50.,
            #               50.,
            #               [
            #                   [   1.,    0.,    0.,    0.],
            #                   [   0.,    1.,    0.,    0.],
            #                   [   0.,    0.,    1.,    0.],
            #                   [-100.,    0.,    0.,    1.]
            #               ],
            #               0.38
            #           ),
            #           dtype=[
            #               ('semanticId', '<u4'),
            #               ('x_min', '<f4'),
            #               ('y_min', '<f4'),
            #               ('z_min', '<f4'),
            #               ('x_max', '<f4'),
            #               ('y_max', '<f4'),
            #               ('z_max', '<f4'),
            #               ('transform', '<f4', (4, 4)),
            #               ('occlusionRatio', '<f4')]),
            #       'info': {
            #           'bboxIds': array([0, 1, 2], dtype=uint32),
            #           'idToLabels': {0: {'prim': 'cone'}, 1: {'prim': 'sphere'}}},
            #           'primPaths': ['/Replicator/Cone_Xform', '/Replicator/Sphere_Xform']
            #       }
            #   }

        import asyncio
        asyncio.ensure_future(test_bbox_3d_fast())

    """,
    },
    {
        "name": "bounding_box_3d",
        "input_rendervars": ["bounding_box_3d_fast"],
        "node_type_id": "omni.replicator.core.BoundingBoxLegacy",
        "output_data_type": np.dtype(
            [
                ("semanticId", "<u4"),
                ("x_min", "<f4"),
                ("y_min", "<f4"),
                ("z_min", "<f4"),
                ("x_max", "<f4"),
                ("y_max", "<f4"),
                ("z_max", "<f4"),
                ("transform", "<f4", (4, 4)),
                ("occlusionRatio", "<f4"),
            ]
        ),
        "output_is_2d": False,
        "is_gpu_enabled": False,
        "documentation": """Outputs 3D bounding box of each entity with semantics for entities within the sensor's field
        of view.

    **Initialization Parameters**

    * semanticFilter: String expressing semantif filter predicate. For example, filter ``"class:car|pedestrian"`` will return only the
      bounding boxes with the semantic type ``"class"`` and with a value of either ``"car"`` or ``"pedestrian"``.

    **Output Format**

    The bounding box annotator returns a dictionary with the bounds and semantic id found under the "data" key, while
    other information is under the "info" key: "idToLabels", "bboxIds" and "primPaths".

    .. code:: python

        {
            "data": np.dtype(
                [
                    ("semanticId", "<u4"),
                    ("x_min", "<i4"),
                    ("y_min", "<i4"),
                    ("x_max", "<i4"),
                    ("y_max", "<i4"),
                    ("z_min", "<i4"),
                    ("z_max", "<i4"),
                    ("transform", "<i4"),
                ],
            "info": {
                "idToLabels": {<semanticId>: <semantic_labels>},    # mapping from integer semantic ID to a comma
                                                                    # delimited list of associated semantics
                "bboxIds": [<bbox_id_0>, ..., <bbox_id_n>],         # ID specific to bounding box annotators allowing
                                                                    # easy mapping between different bounding box
                                                                    # annotators.
                "primPaths": [<prim_path_0>, ... <prim_path_n>],    # prim path tied to each bounding box
            }
        }

    .. note::

        * bounding boxes are retrieved regardless of occlusion.
        * bounding box dimensions (<axis>_min, <axis>_max) are expressed in stage units.

    **Example**

    .. code:: python

        import omni.replicator.core as rep

        async def test_bbox_3d():
            cone = rep.create.cone(semantics=[("prim", "cone")], position=(100, 0, 0))
            sphere = rep.create.sphere(semantics=[("prim", "sphere")], position=(-100, 0, 0))
            cube = rep.create.cube(semantics=[("prim", "cube")], position=(1000, 1000, 1000))

            cam = rep.create.camera(position=(500,500,500), look_at=cone)
            rp = rep.create.render_product(cam, (1024, 512))

            bbox_3d = rep.AnnotatorRegistry.get_annotator("bounding_box_3d")
            bbox_3d.attach(rp)

            await rep.orchestrator.step_async()
            data = bbox_3d.get_data()
            print(data)
            #   {
            #       'data': array([
            #           (
            #               0,
            #               -50.,
            #               -50.,
            #               -50.,
            #               50.,
            #               50.,
            #               50.,
            #               [
            #                   [   1.,    0.,    0.,    0.],
            #                   [   0.,    1.,    0.,    0.],
            #                   [   0.,    0.,    1.,    0.],
            #                   [ 100.,    0.,    0.,    1.]
            #               ],
            #               0.
            #           ),
            #           (
            #               1,
            #               -50.,
            #               -50.,
            #               -50.,
            #               50.,
            #               50.,
            #               [
            #                   [   1.,    0.,    0.,    0.],
            #                   [   0.,    1.,    0.,    0.],
            #                   [   0.,    0.,    1.,    0.],
            #                   [-100.,    0.,    0.,    1.]
            #               ],
            #               0.38
            #           ),
            #           dtype=[
            #               ('semanticId', '<u4'),
            #               ('x_min', '<f4'),
            #               ('y_min', '<f4'),
            #               ('z_min', '<f4'),
            #               ('x_max', '<f4'),
            #               ('y_max', '<f4'),
            #               ('z_max', '<f4'),
            #               ('transform', '<f4', (4, 4)),
            #               ('occlusionRatio', '<f4')]),
            #       'info': {
            #           'bboxIds': array([0, 1, 2], dtype=uint32),
            #           'idToLabels': {0: {'prim': 'cone'}, 1: {'prim': 'sphere'}}},
            #           'primPaths': ['/Replicator/Cone_Xform', '/Replicator/Sphere_Xform']
            #       }
            #   }

        import asyncio
        asyncio.ensure_future(test_bbox_3d())

    """,
    },
    # --- InstanceIdSeg action-graph
    {
        "name": "instance_id_segmentation_fast",
        "input_rendervars": [
            NodeConnectionTemplate(
                "InstanceIdSegmentationReductionSDbuffPtr",
                attributes_mapping={
                    "outputs:dataPtr": "inputs:dataPtr",
                    "outputs:strides": "inputs:strides",
                    "outputs:cudaDeviceIndex": "inputs:cudaDeviceIndex",
                    "outputs:height": "inputs:height",
                    "outputs:width": "inputs:width",
                    "outputs:bufferSize": "inputs:bufferSize",
                },
            ),
            NodeConnectionTemplate(
                "InstanceIdTokenMapSDPtr", attributes_mapping={"outputs:dataPtr": "inputs:instanceIdTokenPtr"}
            ),
        ],
        "node_type_id": "omni.replicator.core.InstanceIdSegmentation",
        "output_data_type": np.uint32,
        "output_channels": 1,
        "output_is_2d": True,
        "hidden": True,
        "documentation": """Development segmentation node
    Instance segmentation that returns the renderer instance ID - used for debugging
    """,
    },
    {
        "name": "instance_id_segmentation",
        "input_rendervars": ["instance_id_segmentation_fast"],
        "node_type_id": "omni.replicator.core.InstanceIdSegmentationLegacy",
        "output_data_type": np.uint32,
        "output_channels": 1,
        "output_is_2d": True,
        "hidden": True,
        "documentation": """Development segmentation node
        Instance segmentation that returns the renderer instance ID - used for debugging
        """,
    },
    # --- InstanceSeg
    {
        "name": "instance_segmentation_fast",
        "input_rendervars": [
            NodeConnectionTemplate(
                "InstanceSegmentationReductionSDbuffPtr",
                attributes_mapping={
                    "outputs:dataPtr": "inputs:dataPtr",
                    "outputs:strides": "inputs:strides",
                    "outputs:cudaDeviceIndex": "inputs:cudaDeviceIndex",
                    "outputs:height": "inputs:height",
                    "outputs:width": "inputs:width",
                    "outputs:bufferSize": "inputs:bufferSize",
                },
            ),
            NodeConnectionTemplate(
                "UniqueInstanceSegmentationIdsSDhostPtr",
                attributes_mapping={
                    "outputs:dataPtr": "inputs:uniqueInstanceSegmentationIdsSDhostPtr",
                },
            ),
            "InstanceMappingPtr",
        ],
        "node_type_id": "omni.replicator.core.InstanceSegmentation",
        "output_data_type": np.uint32,
        "output_channels": 1,
        "output_is_2d": True,
        "documentation": """Outputs instance segmentation of each entity in the camera's viewport. Only semantically
        labelled entities are returned.

    **Initialization Parameters**

    * Colorize (bool): whether to output colorized instance segmentation or non-colorized one.

    **Output Format**

    .. code:: python

        {
            "data": array((height, width), dtype=<np.uint32>),

            "info": {
                "idToLabels": {<semanticId>: <prim_path>},    # mapping from instance ID to the instance's prim path
                "idToSemantic":{<instanceId>: <semantic_labels>},    # mapping from instance ID to a comma delimited
                                                                     # list of associated semantics
            }
        }


    .. note::

        * Two prims with same semantic labels but live in different USD path will have different ids.
        * If two prims have no semantic labels, and they have a same parent which has semantic labels, they will be
          classified as the same instance.
        * The semantic labels of an entity will be the semantic labels of itself, plus all the semantic labels it
          inherit from its parent and semantic labels with same type will be concatenated, separated by comma. For
          example, if an entity has a semantic label of [{"class": "cube"}], and its parent has [{"class": "rectangle"}].
          Then the final semantic labels of that entity will be [{"class": "rectangle, cube"}].


    .. code:: python

        import omni.replicator.core as rep

        async def test_instance_segmentation_fast():
            cone = rep.create.cone(semantics=[("prim", "cone")], position=(100, 0, 0))
            sphere = rep.create.sphere(semantics=[("prim", "sphere")], position=(-100, 0, 0))
            invalid_type = rep.create.cube(semantics=[("shape", "boxy")], position=(0, 100, 0))

            cam = rep.create.camera(position=(500,500,500), look_at=cone)
            rp = rep.create.render_product(cam, (1024, 512))

            instance_seg = rep.AnnotatorRegistry.get_annotator("instance_segmentation_fast")
            instance_seg.attach(rp)

            await rep.orchestrator.step_async()
            data = instance_seg.get_data()
            print(data)
            # {
            #   'data': array([[0, 0, 0, ..., 0, 0, 0],
            #       [0, 0, 0, ..., 0, 0, 0],
            #       [0, 0, 0, ..., 0, 0, 0],
            #       ...,
            #       [0, 0, 0, ..., 0, 0, 0],
            #       [0, 0, 0, ..., 0, 0, 0],
            #       [0, 0, 0, ..., 0, 0, 0]],
            #   'info': {
            #       'idToLabels': {
            #           0: 'BACKGROUND',
            #           1: 'UNLABELLED',
            #           3: '/Replicator/Sphere_Xform',
            #           2: '/Replicator/Cone_Xform',
            #           4: '/Replicator/Cube_Xform'
            #       },
            #       'idToSemantics': {
            #           0: {'class': 'BACKGROUND'},
            #           1: {'class': 'UNLABELLED'},
            #           3: {'prim': 'sphere'},
            #           2: {'prim': 'cone'},
            #           4: {'shape': 'boxy'}
            #       },
            #   }
            # }

        import asyncio
        asyncio.ensure_future(test_instance_segmentation_fast())

    """,
    },
    {
        "name": "instance_segmentation",
        "input_rendervars": ["instance_segmentation_fast"],
        "node_type_id": "omni.replicator.core.InstanceSegmentationLegacy",
        "output_data_type": np.uint32,
        "output_channels": 1,
        "output_is_2d": True,
        "documentation": """Outputs instance segmentation of each entity in the camera's viewport. Only semantically
        labelled entities are returned.

    **Initialization Parameters**

    * Colorize (bool): whether to output colorized instance segmentation or non-colorized one.

    **Output Format**

    .. code:: python

        {
            "data": array((height, width), dtype=<np.uint32>),

            "info": {
                "idToLabels": {<semanticId>: <prim_path>},    # mapping from instance ID to the instance's prim path
                "idToSemantic":{<instanceId>: <semantic_labels>},    # mapping from instance ID to a comma delimited
                                                                     # list of associated semantics
            }
        }


    .. note::

        * Two prims with same semantic labels but live in different USD path will have different ids.
        * If two prims have no semantic labels, and they have a same parent which has semantic labels, they will be
          classified as the same instance.
        * The semantic labels of an entity will be the semantic labels of itself, plus all the semantic labels it
          inherit from its parent and semantic labels with same type will be concatenated, separated by comma. For
          example, if an entity has a semantic label of [{"class": "cube"}], and its parent has [{"class": "rectangle"}].
          Then the final semantic labels of that entity will be [{"class": "rectangle, cube"}].


    .. code:: python

        import omni.replicator.core as rep

        async def test_instance_segmentation():
            cone = rep.create.cone(semantics=[("prim", "cone")], position=(100, 0, 0))
            sphere = rep.create.sphere(semantics=[("prim", "sphere")], position=(-100, 0, 0))
            invalid_type = rep.create.cube(semantics=[("shape", "boxy")], position=(0, 100, 0))

            cam = rep.create.camera(position=(500,500,500), look_at=cone)
            rp = rep.create.render_product(cam, (1024, 512))

            instance_seg = rep.AnnotatorRegistry.get_annotator("instance_segmentation")
            instance_seg.attach(rp)

            await rep.orchestrator.step_async()
            data = instance_seg.get_data()
            print(data)
            # {
            #   'data': array([[0, 0, 0, ..., 0, 0, 0],
            #       [0, 0, 0, ..., 0, 0, 0],
            #       [0, 0, 0, ..., 0, 0, 0],
            #       ...,
            #       [0, 0, 0, ..., 0, 0, 0],
            #       [0, 0, 0, ..., 0, 0, 0],
            #       [0, 0, 0, ..., 0, 0, 0]],
            #   'info': {
            #       'idToLabels': {
            #           0: 'BACKGROUND',
            #           1: 'UNLABELLED',
            #           3: '/Replicator/Sphere_Xform',
            #           2: '/Replicator/Cone_Xform',
            #           4: '/Replicator/Cube_Xform'
            #       },
            #       'idToSemantics': {
            #           0: {'class': 'BACKGROUND'},
            #           1: {'class': 'UNLABELLED'},
            #           3: {'prim': 'sphere'},
            #           2: {'prim': 'cone'},
            #           4: {'shape': 'boxy'}
            #       },
            #   }
            # }

        import asyncio
        asyncio.ensure_future(test_instance_segmentation())

    """,
    },
    # --- SemanticSeg
    {
        "name": "semantic_segmentation",
        "input_rendervars": [
            NodeConnectionTemplate(
                "instance_segmentation_fast",
                attributes_mapping={
                    "outputs:exec": "inputs:exec",
                    "outputs:height": "inputs:height",
                    "outputs:width": "inputs:width",
                    "outputs:bufferSize": "inputs:bufferSize",
                    "outputs:dataPtr": "inputs:instanceSegmentationPtr",
                    "outputs:strides": "inputs:instanceSegmentationStrides",
                    "outputs:cudaDeviceIndex": "inputs:instanceSegmentationCudaDeviceIndex",
                    "outputs:ids": "inputs:ids",
                    "outputs:labels": "inputs:labels",
                    "outputs:semantics": "inputs:semantics",
                },
            ),
        ],
        "node_type_id": "omni.replicator.core.SemanticSegmentation",
        "output_data_type": np.uint32,
        "output_channels": 1,
        "output_is_2d": True,
        "documentation": """Outputs semantic segmentation of each entity in the camera's field of view that has semantic
        labels.

    **Initialization Parameters**

    * Colorize (bool): whether to output colorized semantic segmentation or non-colorized one.

    **Output Format**

    .. code:: python

        {
            "data": array((height, width), dtype=<np.uint32>),

            "info": {
                "idToLabels": {<semanticId>: <semantic_labels>},    # mapping from semantic ID to a comma delimited list
                                                                    # of associated semantics
            }
        }

    * data (semantic segmentation array):
        * If ``colorize`` is set to ``True``, the image will be a 2d array of types ``np.uint8`` with 4 channels. The
          uint32 array can be converted using `semantic_seg_data["data"].view(np.uint8).reshape(height, width, -1)`
        * Different colors represent different semantic labels.
        * If ``colorize`` is set to ``False``, the image will be a 2d array of types ``np.uint32`` with 1 channel, which
          is the semantic id of the entities.

    * info:
        * ``idToLabels``
        * If ``colorize`` is set to ``True``, it will be the mapping from color to semantic labels.
        * If ``colorize`` is set to ``False``, it will be the mapping from semantic id to semantic labels.

    .. note::
        The semantic labels of an entity will be the semantic labels of itself, plus all the semantic labels it
        inherit from its parent and semantic labels with same type will be concatenated, separated by comma.
        For example, if an entity has a semantic label of ``[{class": "cube"}]``, and its parent has
        ``[{class": "rectangle"}]``. Then the final semantic labels of that entity will be
        ``[{class": "rectangle, cube"}]``.

    .. code:: python

        import omni.replicator.core as rep

        async def test_semantic_segmentation():
            cone = rep.create.cone(semantics=[("prim", "cone")], position=(100, 0, 0))
            sphere = rep.create.sphere(semantics=[("prim", "sphere")], position=(-100, 0, 0))
            invalid_type = rep.create.cube(semantics=[("shape", "boxy")], position=(0, 100, 0))

            cam = rep.create.camera(position=(500,500,500), look_at=cone)
            rp = rep.create.render_product(cam, (1024, 512))

            semantic_seg = rep.AnnotatorRegistry.get_annotator("semantic_segmentation")
            semantic_seg.attach(rp)

            await rep.orchestrator.step_async()
            data = semantic_seg.get_data()
            print(data)
            # {
            #   'data': array([[0, 0, 0, ..., 0, 0, 0],
            #       [0, 0, 0, ..., 0, 0, 0],
            #       [0, 0, 0, ..., 0, 0, 0],
            #       ...,
            #       [0, 0, 0, ..., 0, 0, 0],
            #       [0, 0, 0, ..., 0, 0, 0],
            #       [0, 0, 0, ..., 0, 0, 0]],
            #   'info': {
            #       'idToLabels': {
            #           0: {'class': 'BACKGROUND'},
            #           2: {'prim': 'cone'},
            #           3: {'shape': 'boxy'},
            #           4: {'prim': 'sphere'}
            #       },
            #   }
            # }

        import asyncio
        asyncio.ensure_future(test_semantic_segmentation())


    """,
    },
    # --- Camera Params
    # --- CameraParamsOpenCV TODO: Remove this when kit has been updated.
    # Register the post-render node
    {
        "name": "CameraParamsOpenCVPR",
        "input_rendervars": [
            NodeConnectionTemplate(
                "GpuInteropEntry",
                attributes_mapping={
                    "outputs:rp": "inputs:renderResults",
                    "outputs:exec": "inputs:exec",
                    "outputs:gpu": "inputs:gpu",
                },
            ),
            NodeConnectionTemplate("RenderProductCameraPrimPath", attributes_mapping={"outputs:exec": "inputs:exec"}),
        ],
        "node_type_id": "omni.replicator.core.CameraParamsOpenCV",
    },
    # Register the post-process node
    # Post Process Attribute Reader
    {
        "name": "CameraParamsOpenCV",
        "input_rendervars": [
            NodeConnectionTemplate(
                "PostProcessDispatch",
                attributes_mapping={"outputs:renderResults": "inputs:renderResults"},
            ),
            NodeConnectionTemplate("CameraParamsOpenCVPR", attributes_mapping={"outputs:exec": "inputs:exec"}),
        ],
        "node_type_id": "omni.replicator.core.CameraParamsOpenCV",
    },
    {
        "name": "CameraParams",
        "input_rendervars": [
            "PostProcessRenderProductCamera",
            NodeConnectionTemplate(
                "CameraParamsOpenCV",
                attributes_mapping={
                    "outputs:cameraOpenCVFx": "inputs:cameraOpenCVFx",
                    "outputs:cameraOpenCVFy": "inputs:cameraOpenCVFy",
                    "outputs:isPinholeOpenCV": "inputs:isPinholeOpenCV",
                },
            ),
        ],
        "node_type_id": "omni.replicator.core.CameraParams",
        "documentation": """The Camera Parameters annotator returns the camera details for the camera corresponding to
        the render product to which the annotator is attached.

    **Data Details**

    * cameraFocalLength: Camera focal length
    * cameraFocusDistance: Camera focus distance
    * cameraFStop: Camera fStop value
    * cameraAperture: Camera horizontal and vertical aperture
    * cameraApertureOffset: Camera horizontal and vertical aperture offset
    * renderProductResolution: RenderProduct resolution
    * cameraModel: Camera model name
    * cameraViewTransform: Camera to world transformation matrix
    * cameraProjection: Camera projection matrix
    * cameraFisheyeNominalWidth: Camera fisheye nominal width
    * cameraFisheyeNominalHeight: Camera fisheye nominal height
    * cameraFisheyeOpticalCentre: Camera fisheye optical centre
    * cameraFisheyeMaxFOV: Camera fisheye maximum field of view
    * cameraFisheyePolynomial: Camera fisheye polynomial
    * cameraNearFar: Camera near/far clipping range

    **Example**

    .. code:: python

        import asyncio
        import omni.replicator.core as rep

        async def test_camera_params():
            camera_1 = rep.create.camera()
            camera_2 = rep.create.camera(
                position=(100, 0, 0),
                projection_type="fisheye_polynomial"
            )

            render_product_1 = rep.create.render_product(camera_1, (1024, 512))
            render_product_2 = rep.create.render_product(camera_2, (800, 600))


            anno_1 = rep.annotators.get("CameraParams").attach(render_product_1)
            anno_2 = rep.annotators.get("CameraParams").attach(render_product_2)

            await rep.orchestrator.step_async()

            print(anno_1.get_data())
            # {'cameraAperture': array([20.95 , 15.29], dtype=float32),
            #     'cameraApertureOffset': array([0., 0.], dtype=float32),
            #     'cameraFisheyeLensP': array([], dtype=float32),
            #     'cameraFisheyeLensS': array([], dtype=float32),
            #     'cameraFisheyeMaxFOV': 0.0,
            #     'cameraFisheyeNominalHeight': 0,
            #     'cameraFisheyeNominalWidth': 0,
            #     'cameraFisheyeOpticalCentre': array([0., 0.], dtype=float32),
            #     'cameraFisheyePolynomial': array([0., 0., 0., 0., 0.], dtype=float32),
            #     'cameraFocalLength': 24.0,
            #     'cameraFocusDistance': 400.0,
            #     'cameraFStop': 0.0,
            #     'cameraModel': 'pinhole',
            #     'cameraNearFar': array([1., 1000000.], dtype=float32),
            #     'cameraProjection': array([ 2.29,  0.  ,  0.  ,  0.  ,
            #                                 0.  ,  4.58,  0.  ,  0.  ,
            #                                 0.  ,  0.  ,  0.  , -1.  ,
            #                                 0.  ,  0.  ,  1.  ,  0.  ]),
            #     'cameraViewTransform': array([1., 0., 0., 0., 0., 1., 0., 0., 0., 0., 1., 0., 0., 0., 0., 1.]),
            #     'metersPerSceneUnit': 0.009999999776482582,
            #     'renderProductResolution': array([1024, 512], dtype=int32)
            # }

            print(anno_2.get_data())
            # {
            #     'cameraAperture': array([20.955 , 15.291], dtype=float32),
            #     'cameraApertureOffset': array([0., 0.], dtype=float32),
            #     'cameraFisheyeLensP': array([-0., -0.], dtype=float32),
            #     'cameraFisheyeLensS': array([-0., -0.,  0., -0.], dtype=float32),
            #     'cameraFisheyeMaxFOV': 200.0,
            #     'cameraFisheyeNominalHeight': 1216,
            #     'cameraFisheyeNominalWidth': 1936,
            #     'cameraFisheyeOpticalCentre': array([970.9424, 600.375 ], dtype=float32),
            #     'cameraFisheyePolynomial': array([0.     , 0.002, 0.     , 0.     , 0.     ], dtype=float32),
            #     'cameraFocalLength': 24.0,
            #     'cameraFocusDistance': 400.0,
            #     'cameraFStop': 0.0,
            #     'cameraModel': 'fisheyePolynomial',
            #     'cameraNearFar': array([1., 1000000.], dtype=float32),
            #     'cameraProjection': array([ 2.29,  0.  ,  0.  ,  0.  ,
            #                                 0.  ,  3.05,  0.  ,  0.  ,
            #                                 0.  ,  0.  ,  0.  , -1.  ,
            #                                 0.  ,  0.  ,  1.  ,  0.  ]),
            #     'cameraViewTransform': array([1., 0., 0., 0., 0., 1., 0., 0., 0., 0., 1., 0., -100., 0., 0., 1.]),
            #   'metersPerSceneUnit': 0.009999999776482582,
            #   'renderProductResolution': array([800, 600], dtype=int32)
            #  }

        asyncio.ensure_future(test_camera_params())

    """,
    },
    # --- Skeleton Data
    {
        "name": "skeleton_prims",
        "input_rendervars": ["PostProcessDispatch"],
        "node_type_id": "omni.replicator.core.OgnGetSkeletonPrims",
        "hidden": True,
    },
    # Register the post-render node
    {
        "name": "skeleton_attributes_pr",
        "input_rendervars": [NodeConnectionTemplate("GpuInteropEntry")],
        "node_type_id": "omni.replicator.core.OgnGetSkeletonAttributes",
    },
    # Register the action-graph node
    {
        "name": "skeleton_attributes",
        "input_rendervars": [
            NodeConnectionTemplate(
                "PostProcessDispatch",
                attributes_mapping={"outputs:renderResults": "inputs:rp"},
            ),
            NodeConnectionTemplate("skeleton_attributes_pr", attributes_mapping={"outputs:exec": "inputs:exec"}),
        ],
        "node_type_id": "omni.replicator.core.OgnGetSkeletonAttributes",
    },
    {
        "name": "skeleton_data",
        "input_rendervars": [
            "CameraParams",
            "PostProcessDispatch",
            NodeConnectionTemplate("skeleton_prims", attributes_mapping={"outputs:prims": "inputs:prims"}),
            NodeConnectionTemplate(
                "skeleton_attributes",
                attributes_mapping={
                    "outputs:primPaths": "inputs:fabricPrims",
                    "outputs:jointPaths": "inputs:fabricJoints",
                    "outputs:primWorldPositions": "inputs:primWorldPositions",
                    "outputs:primWorldOrientations": "inputs:primWorldOrientations",
                    "outputs:primWorldScales": "inputs:primWorldScales",
                    "outputs:jointWorldPositions": "inputs:jointWorldPositions",
                    "outputs:jointWorldOrientations": "inputs:jointWorldOrientations",
                    "outputs:jointWorldScales": "inputs:jointWorldScales",
                },
            ),
            NodeConnectionTemplate(
                "instance_segmentation_fast",
                attributes_mapping={
                    "outputs:dataPtr": "inputs:instanceSegmentationPtr",
                    "outputs:strides": "inputs:instanceSegmentationStrides",
                    "outputs:cudaDeviceIndex": "inputs:instanceSegmentationCudaDeviceIndex",
                    "outputs:height": "inputs:instanceSegmentationHeight",
                    "outputs:width": "inputs:instanceSegmentationWidth",
                    "outputs:ids": "inputs:instanceSegmentationIds",
                    "outputs:semantics": "inputs:instanceSegmentationSemantics",
                    "outputs:labels": "inputs:instanceSegmentationLabels",
                },
            ),
        ],
        "node_type_id": "omni.replicator.core.OgnGetSkeletonData",
        "documentation": """The skeleton data annotator outputs pose information about the skeletons in the scene view.

    **Output Format**

    =========================== ======================================== ===============================================
    Parameter                   Data Type                                Description
    =========================== ======================================== ===============================================
    animationVariant            list(<num_skeletons>, dtype=str)         Animation variant name for each skeleton
    assetPath                   list(<num_skeletons>, dtype=str)         Asset path for each skeleton
    globalTranslations          array((<num_joints>, 3), dtype=float32)  Global translation of each joint
    globalTranslationsSizes     array(<num_skeletons>, dtype=int32)      Size of each set of joints per skeleton
    inView                      array(<num_skeletons>, dtype=bool)       If the skeleton is in view of the camera
    jointOcclusions             array(<num_joints>, dtype=bool)          For each joint, True if joint is occluded,
                                                                         otherwise False
    jointOcclusionsSizes        array(<num_skeletons>, dtype=int32)      Size of each set of joints per skeleton
    localRotations              array((<num_joints>, 4), dtype=float32)  Local rotation of each joint
    localRotationsSizes         array(<num_skeletons>, dtype=int32)      Size of each set of joints per skeleton
    numSkeletons                <num_skeletons>                          Number of skeletons in scene
    occlusionTypes              list(str)                                For each joint, the type of occlusion
    occlusionTypesSizes         array([<num_skeletons>], dtype=int32)    Size of each set of joints per skeleton
    restGlobalTranslations      array((<num_joints>, 3), dtype=float32)  Global translation for each joint at rest
    restGlobalTranslationsSizes array([<num_skeletons>], dtype=int32)    Size of each set of joints per skeleton
    restLocalRotations          array((<num_joints>, 4), dtype=float32)  Local rotation of each join at rest
    restLocalRotationsSizes     array(<num_skeletons>, dtype=int32)      Size of each set of joints per skeleton
    restLocalTranslations       array((<num_joints>, 3), dtype=float32)  Local translation of each join at rest
    restLocalTranslationsSizes  array(<num_skeletons>, dtype=int32)      Size of each set of joints per skeleton
    skeletonJoints              list(str)                                List of skeleton joints, encoded as a string
    skeletonParents             array(<num_joints>, dtype=int32)         Which joint is the parent of the index, -1 is
                                                                         root
    skeletonParentsSizes        array(<num_skeletons>, dtype=int32)      Size of each set of joints per skeleton
    skelName                    list(<num_skeletons>, dtype=str)         Name of each skeleton
    skelPath                    list(<num_skeletons>, dtype=str)         Path of each skeleton prim
    translations2d              array((<num_joints>, 2), dtype=float32)  Screen space joint position in pixels
    translations2dSizes         array(<num_skeletons>, dtype=int32)      Size of each set of joints per skeleton
    =========================== ======================================== ===============================================

    This annotator returns additional data as a single string held in a dictionary with the key ``skeleton_data`` for
    backwards compatibility with the original implementation of this annotator. Use ``eval(data["skeleton_data"])`` to
    extract the attributes from this string.

    **Example**

    Below is an example script that outputs 10 images with skeleton pose annotation.

    .. code:: python

        import asyncio
        import omni.replicator.core as rep

        # Define paths for the character
        PERSON_SRC = 'omniverse://localhost/NVIDIA/Assets/Characters/Reallusion/Worker/Worker.usd'

        async def test_skeleton_data():
            # Human Model
            person = rep.create.from_usd(PERSON_SRC, semantics=[('class', 'person')])
            # Area to scatter cubes in
            area = rep.create.cube(scale=2, position=(0.0, 0.0, 100.0), visible=False)

            # Create the camera and render product
            camera = rep.create.camera(position=(25, -421.0, 182.0), rotation=(77.0, 0.0, 3.5))
            render_product = rep.create.render_product(camera, (1024, 1024))

            def randomize_spheres():
                spheres = rep.create.sphere(scale=0.1, count=100)
                with spheres:
                    rep.randomizer.scatter_3d(area)
                return spheres.node

            rep.randomizer.register(randomize_spheres)

            with rep.trigger.on_frame(interval=10, max_execs=5):
                rep.randomizer.randomize_spheres()

            # Attach annotator
            skeleton_anno = rep.annotators.get("skeleton_data")
            skeleton_anno.attach(render_product)

            await rep.orchestrator.step_async()

            data = skeleton_anno.get_data()
            print(data)
            # {
            #     'animationVariant': ['None'],
            #     'assetPath': ['Bones/Worker.StandingDiscussion_LookingDown_M.usd'],
            #     'globalTranslations': array([[  0.  ,   0.  ,   0.  ], ..., [-21.64,   2.58, 129.8 ]], dtype=float32),
            #     'globalTranslationsSizes': array([101], dtype=int32),
            #     'inView': array([ True]),
            #     'jointOcclusions': array([ True, False, ..., False, False]),
            #     'jointOcclusionsSizes': array([101], dtype=int32),
            #     'localRotations': array([[ 1. , 0. , 0. , 0.  ], ..., [ 1. , 0. , -0.09 , -0. ]], dtype=float32),
            #     'localRotationsSizes': array([101], dtype=int32),
            #     'numSkeletons': 1,
            #     'occlusionTypes': ["['BACKGROUND', 'None', ..., 'None', 'None']"],
            #     'occlusionTypesSizes': array([101], dtype=int32),
            #     'restGlobalTranslations': array([[ 0. ,  0. ,  0.  ], ..., [-31.86,  8.96, 147.72]], dtype=float32),
            #     'restGlobalTranslationsSizes': array([101], dtype=int32),
            #     'restLocalRotations': array([[ 1. , 0. , 0. , 0.  ], ..., [ 1. , 0. , 0. , -0.  ]], dtype=float32),
            #     'restLocalRotationsSizes': array([101], dtype=int32),
            #     'restLocalTranslations': array([[ 0. ,  0. ,  0.  ], ..., [ -0. ,  12.92,  0.01]], dtype=float32),
            #     'restLocalTranslationsSizes': array([101], dtype=int32),
            #     'skeletonJoints': [
            #         'RL_BoneRoot',
            #         'RL_BoneRoot/Hip',
            #         ...,
            #         'RL_BoneRoot/Hip/Waist/Spine01/Spine02/R_Clavicle/R_Upperarm/R_UpperarmTwist01/R_UpperarmTwist02'
            #     ],
            #     'skeletonParents': array([-1,  0,  1, ..., 97, 78, 99], dtype=int32),
            #     'skeletonParentsSizes': array([101], dtype=int32),
            #     'skelName': ['Worker'],
            #     'skelPath': ['/Replicator/Ref_Xform/Ref/ManRoot/Worker/Worker'],
            #     'translations2d': array([[513.94, 726.03],
            #                              [514.42, 480.42],
            #                              [514.42, 480.42],
            #                              ...,
            #                              [499.45, 450.9 ],
            #                              [466.3 , 354.6 ],
            #                              [455.09, 388.56]], dtype=float32),
            #    'translations2dSizes': array([101], dtype=int32),
            #    'skeletonData': ...   # string data representation for backward compatibility
            # }

        asyncio.ensure_future(test_skeleton_data())
    """,
    },
    {
        "name": "pointcloud",
        "input_rendervars": [
            NodeConnectionTemplate(
                "LdrColorbuffPtr",
                attributes_mapping={
                    "outputs:dataPtr": "inputs:rgbPtr",
                    "outputs:height": "inputs:height",
                    "outputs:width": "inputs:width",
                    "outputs:strides": "inputs:rgbStrides",
                    "outputs:cudaDeviceIndex": "inputs:rgbCudaDeviceIndex",
                },
            ),
            NodeConnectionTemplate(
                "NormalSDbuffPtr",
                attributes_mapping={
                    "outputs:dataPtr": "inputs:normalsPtr",
                    "outputs:strides": "inputs:normalsStrides",
                    "outputs:cudaDeviceIndex": "inputs:normalsCudaDeviceIndex",
                },
            ),
            NodeConnectionTemplate(
                "CameraParams",
                attributes_mapping={
                    "outputs:cameraViewTransform": "inputs:cameraViewTransform",
                },
            ),
            NodeConnectionTemplate(
                "Camera3dPositionSDbuffPtr",
                attributes_mapping={
                    "outputs:dataPtr": "inputs:camera3dPositionsPtr",
                    "outputs:strides": "inputs:camera3dPositionsStrides",
                    "outputs:cudaDeviceIndex": "inputs:camera3dPositionsCudaDeviceIndex",
                },
            ),
            NodeConnectionTemplate(
                "semantic_segmentation",
                attributes_mapping={
                    "outputs:dataPtr": "inputs:semanticSegmentationPtr",
                    "outputs:strides": "inputs:semanticSegmentationStrides",
                    "outputs:cudaDeviceIndex": "inputs:semanticSegmentationCudaDeviceIndex",
                },
            ),
            NodeConnectionTemplate(
                "instance_segmentation_fast",
                attributes_mapping={
                    "outputs:dataPtr": "inputs:instanceSegmentationPtr",
                    "outputs:strides": "inputs:instanceSegmentationStrides",
                    "outputs:cudaDeviceIndex": "inputs:instanceSegmentationCudaDeviceIndex",
                },
            ),
        ],
        "output_data_type": np.float32,
        "output_channels": 3,
        "node_type_id": "omni.replicator.core.OgnPointCloudGenerator",
        "documentation": """

    Outputs a 2D array of shape (N, 3) representing the points sampled on the surface of the prims in the viewport,
    where N is the number of point.

    **Output Format**

    The pointcloud annotator returns positions of the points found under the "data" key, while other information is
    under the "info" key: "pointRgb", "pointNormals", "pointSemantic" and "pointInstance".

    .. code:: python

        {
            'data': array([...], shape=(<num_points>, 3), dtype=float32),
            'info': {
                'pointNormals': array([...], shape=(<num_points> * 4), dtype=float32),
                'pointRgb': array([...], shape=(<num_points> * 4), dtype=uint8),
                'pointSemantic': array([...], shape=(<num_points>), dtype=uint8),
                'pointInstance': array([...], shape=(<num_points>), dtype=uint8),
            }
        }

    **Data Details**

    * Point positions are in the world space.
    * Sample resolution is determined by the resolution of the render product.

    .. note::

        To get the mapping from semantic id to semantic labels, pointcloud annotator is better used with semantic
        segmentation annotator, and users can extract the ``idToLabels`` data from the semantic segmentation
        annotator.

    **Example 1**

    Pointcloud annotator captures prims seen in the camera, and sampled the points on the surface of the prims, based on
    the resolution of the render product attached to the camera.  Additional to the points sampled, it also outputs rgb,
    normals and semantic id values associated to the prim where that point belongs to. For prims without any valid
    semantic labels, pointcloud annotator will ignore it.

    .. code:: python

        import asyncio
        import omni.replicator.core as rep

        async def test_pointcloud():
            # Pointcloud only capture prims with valid semantics
            W, H = (1024, 512)
            cube = rep.create.cube(position=(0, 0, 0), semantics=[("class", "cube")])
            camera = rep.create.camera(position=(200., 200., 200.), look_at=cube)
            render_product = rep.create.render_product(camera, (W, H))

            pointcloud_anno = rep.annotators.get("pointcloud")
            pointcloud_anno.attach(render_product)

            await rep.orchestrator.step_async()

            pc_data = pointcloud_anno.get_data()
            print(pc_data)
            # {
            #   'data': array([[-49.96,  50.  , -49.28],
            #                  [-49.74,  50.  , -49.51],
            #                  [-49.51,  50.  , -49.74],
            #                  ...,
            #                  [ 50.  , -49.33,  27.51],
            #                  [ 50.  , -49.67,  27.08],
            #                  [ 50.  , -50.  ,  26.65]], dtype=float32),
            #   'info': {
            #       'pointNormals': array([ 0.,  1., -0., ...,  0., -0.,  1.], dtype=float32),
            #       'pointRgb': array([154, 154, 154, ...,  24,  24, 255], dtype=uint8),
            #       'pointSemantic': array([2, 2, 2, ..., 2, 2, 2], dtype=uint8)},
            #       'pointInstance': array([1, 1, 1, ..., 1, 1, 1], dtype=uint8)}
            # }

        asyncio.ensure_future(test_pointcloud())


    **Example 2**

    In this example, we demonstrate a scenario where multiple camera captures are taken to produce a more complete
    pointcloud, utilizing the excellent ``open3d`` library to export a coloured ``ply`` file.

    .. code:: python

        import os
        import asyncio
        import omni.replicator.core as rep
        import open3d as o3d
        import numpy as np

        async def test_pointcloud():
            # Pointcloud only capture prims with valid semantics
            cube = rep.create.cube(semantics=[("class", "cube")])
            camera = rep.create.camera()
            render_product = rep.create.render_product(camera, (1024, 512))

            pointcloud_anno = rep.annotators.get("pointcloud")
            pointcloud_anno.attach(render_product)

            # Camera positions to capture the cube
            camera_positions = [(500, 500, 0), (-500, -500, 0), (500, 0, 500), (-500, 0, -500)]

            with rep.trigger.on_frame(max_execs=len(camera_positions)):
                with camera:
                    rep.modify.pose(
                        position=rep.distribution.sequence(camera_positions),
                        look_at=cube,
                    )  # make the camera look at the cube

            # Accumulate points
            points = []
            points_rgb = []
            for _ in range(len(camera_positions)):
                await rep.orchestrator.step_async()

                pc_data = pointcloud_anno.get_data()
                points.append(pc_data["data"])
                points_rgb.append(pc_data["info"]["pointRgb"].reshape(-1, 4)[:, :3])

            # Output pointcloud as .ply file
            ply_out_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "out")
            os.makedirs(ply_out_dir, exist_ok=True)

            pc_data = np.concatenate(points)
            pc_rgb = np.concatenate(points_rgb)

            pcd = o3d.geometry.PointCloud()
            pcd.points = o3d.utility.Vector3dVector(pc_data)
            pcd.colors = o3d.utility.Vector3dVector(pc_rgb)
            o3d.io.write_point_cloud(os.path.join(ply_out_dir, "pointcloud.ply"), pcd)

        asyncio.ensure_future(test_pointcloud())

    """,
    },
    {
        "name": "DispatchSync",
        "input_rendervars": [
            NodeConnectionTemplate(
                "PostProcessDispatcher",
                render_product_idxs=(),  # This ensures that duplicates dispatchers aren't created for each RP
                attributes_mapping={
                    "outputs:exec": "inputs:exec",
                    "outputs:referenceTimeNumerator": "inputs:referenceTimeNumerator",
                    "outputs:referenceTimeDenominator": "inputs:referenceTimeDenominator",
                },
            )
        ],
        "node_type_id": "omni.replicator.core.OgnRefTimeGate",
        "hidden": True,
    },
    # {
    #     "DispatchTriggerSync",
    #     "input_rendervars": [
    #         NodeConnectionTemplate(
    #             "DispatchSync",
    #             attributes_mapping={
    #                 "outputs:exec": "inputs:exec",
    #                 "outputs:syncValue": "inputs:syncValue",
    #             },
    #         )
    #     ],
    #     "node_type_id": "omni.replicator.core.OgnTriggerGate",
    # )
    {
        "name": "PostProcessDispatch",
        "input_rendervars": [
            NodeConnectionTemplate("DispatchSync", render_product_idxs=(), attributes_mapping={}),
            # "DispatchTriggerSync",
            NodeConnectionTemplate(
                "PostProcessDispatcher",
                render_product_idxs=(),  # This ensures that duplicates dispatchers aren't created for each RP
                attributes_mapping={
                    "outputs:renderProductDataPtrs": "inputs:renderProductDataPtrs",
                    "outputs:renderProductPaths": "inputs:renderProductPaths",
                },
            ),
        ],
        "node_type_id": "omni.syntheticdata.SdOnNewRenderProductFrame",
        "hidden": True,
    },
    {
        "name": "PostProcessDispatchUngated",
        "input_rendervars": [
            NodeConnectionTemplate(
                "PostProcessDispatcher",
                render_product_idxs=(),  # This ensures that duplicates dispatchers aren't created for each RP
            )
        ],
        "node_type_id": "omni.syntheticdata.SdOnNewRenderProductFrame",
        "hidden": True,
    },
    {
        "name": "ReferenceTime",
        "input_rendervars": [
            NodeConnectionTemplate(
                "PostProcessDispatcher",
                render_product_idxs=(),  # This ensures that duplicates simtime annotators aren't created for each RP
            )
        ],
        "node_type_id": "omni.replicator.core.OgnRefTime",
        "hidden": True,
        "documentation": """
    Outputs the reference time corresponding to the render and associated annotations.

    **Output Format**

    The reference time annotator returns a numerator and denominator representing the time corresponding to the render
    and associated annotations.

    .. code:: python

        {
            'referenceTimeNumerator': int,
            'referenceTimeDenominator': int,
        }

    **Example**

    .. code:: python

        import asyncio
        import omni.replicator.core as rep

        async def test_reference_time():
            W, H = (1024, 512)
            camera = rep.create.camera()
            render_product = rep.create.render_product(camera, (W, H))

            ref_time_anno = rep.annotators.get("ReferenceTime")
            ref_time_anno.attach(render_product)

            await rep.orchestrator.step_async()

            ref_time_data = ref_time_anno.get_data()
            print(ref_time_data)
            # {
            #   'referenceTimeNumerator': <numerator>,
            #   'referenceTimeDenominator': <denominator>,
            # }

        asyncio.ensure_future(test_reference_time())
    """,
    },
    # Post Render Attribute Reader
    {
        "name": "AttributePR",  # post-renderer part of the node
        "input_rendervars": [NodeConnectionTemplate("GpuInteropEntry")],
        "node_type_id": "omni.replicator.core.FabricReader",
        "hidden": True,
    },
    # Post Process Attribute Reader
    {
        "name": "Attribute",
        "input_rendervars": [
            NodeConnectionTemplate(
                "PostProcessDispatch",
                attributes_mapping={"outputs:renderResults": "inputs:rp"},
            ),
            NodeConnectionTemplate("AttributePR", attributes_mapping={"outputs:exec": "inputs:exec"}),
        ],
        "node_type_id": "omni.replicator.core.FabricReader",
        "on_attach_callback": on_attribute_anno_attach,
        "documentation": """
    Outputs the value of an attribute attached to one of more prims.

    The Attribute annotator retrieves the attribute value(s) of one or more prims at the time of render. On attach,
    the attribute specified will be automatically pushed to Fabric to ensure it can be retrieved. Note that the
    output type of the attribute must be identical in all specified prims.

    **Output Format**

    .. code:: python

        array((attribute_size x number_of_prims, 1))

    The Attribute annotator retrieves the data from the attribute and flattens them, creating a 1D array of shape
    (attribute_size x number_of_prims, 1).

    Currently it can retrieve the attribute with following Sdf data types:

    * Int, IntArray, Int2, Int2Array, Int3, Int3Array
    * Float, FloatArray, Float2, Float2Array, Float3, Float3Array
    * Double, DoubleArray, Double2, Double2Array, Double3, Double3Array

    **Example**

    .. code:: python

        import asyncio
        import omni.replicator.core as rep
        from pxr import Sdf

        async def test_attribute_anno():
            cube1 = rep.create.cube(as_mesh=False)
            cube2 = rep.create.cube(as_mesh=False)
            cube_prim_path = "/Replicator/Cube_Xform/Cube"
            cube_prim_path_2 = "/Replicator/Cube_Xform_01/Cube"

            for path in [cube_prim_path, cube_prim_path_2]:
                stage = omni.usd.get_context().get_stage()
                cube_prim = stage.GetPrimAtPath(path)
                cube_prim.CreateAttribute(
                    "float2Arr",
                    Sdf.ValueTypeNames.Float2Array,
                ).Set([(12.34, 56.78), (56.78, 12.34)])

            await omni.kit.app.get_app().next_update_async()

            rp = rep.create.render_product("/OmniverseKit_Persp", (1024, 1024))

            fabric_reader_anno = rep.annotators.get(
                "Attribute",
                init_params={
                    "prims": [cube_prim_path, cube_prim_path_2],
                    "attribute": "float2Arr",
                },
            )
            fabric_reader_anno.attach(rp)

            await rep.orchestrator.step_async()

            data = fabric_reader_anno.get_data()
            print(data, data.shape, data.dtype)
            # [12.34 56.78 56.78 12.34 12.34 56.78 56.78 12.34] (8,) float32

        asyncio.ensure_future(test_attribute_anno())
    """,
    },
    {
        "name": "shaded_instance_id_segmentation",
        "input_rendervars": [
            NodeConnectionTemplate(
                "instance_id_segmentation_fast",
                attributes_mapping={
                    "outputs:dataPtr": "inputs:segmentationDataPtr",
                    "outputs:strides": "inputs:segmentationStrides",
                    "outputs:bufferSize": "inputs:segmentationBufferSize",
                    "outputs:cudaDeviceIndex": "inputs:segmentationCudaDeviceIndex",
                    "outputs:width": "inputs:width",
                    "outputs:height": "inputs:height",
                },
            ),
            NodeConnectionTemplate(
                "NormalSDbuffPtr",
                attributes_mapping={
                    "outputs:dataPtr": "inputs:normalDataPtr",
                    "outputs:strides": "inputs:normalStrides",
                    "outputs:bufferSize": "inputs:normalBufferSize",
                    "outputs:cudaDeviceIndex": "inputs:normalCudaDeviceIndex",
                },
            ),
        ],
        "node_type_id": "omni.replicator.core.OgnAugShadeSegmentation",
        "output_data_type": np.uint8,
        "output_channels": 3,
        "output_is_2d": True,
        "is_gpu_enabled": True,
        "documentation": """
            Apply shading to instance id segmentation using surface normals.

            **Output Format**

            * shaded_segmentation: Shaded instance id segmentation image (H,W,3)

            **Example**

            .. code:: python

                import asyncio
                import omni.replicator.core as rep

                async def test_shaded_segmentation():
                    # Add an object to look at
                    cone = rep.create.cone(semantics=[("prim", "cone")])
                    sphere = rep.create.sphere(semantics=[("prim", "sphere")])

                    cam = rep.create.camera(position=(500,500,500), look_at=cone)
                    rp = rep.create.render_product(cam, (1024, 512))

                    shaded_segmentation = rep.annotators.get("shaded_instance_id_segmentation")
                    shaded_segmentation.attach(rp)

                    await rep.orchestrator.step_async()
                    data = shaded_segmentation.get_data()
                    print(data.shape, data.dtype)
                    # (512, 1024, 3), uint8

                asyncio.ensure_future(test_shaded_segmentation())

        """,
    },
    {
        "name": "shaded_instance_segmentation",
        "input_rendervars": [
            NodeConnectionTemplate(
                "instance_segmentation_fast",
                attributes_mapping={
                    "outputs:dataPtr": "inputs:segmentationDataPtr",
                    "outputs:strides": "inputs:segmentationStrides",
                    "outputs:bufferSize": "inputs:segmentationBufferSize",
                    "outputs:cudaDeviceIndex": "inputs:segmentationCudaDeviceIndex",
                    "outputs:width": "inputs:width",
                    "outputs:height": "inputs:height",
                },
            ),
            NodeConnectionTemplate(
                "NormalSDbuffPtr",
                attributes_mapping={
                    "outputs:dataPtr": "inputs:normalDataPtr",
                    "outputs:strides": "inputs:normalStrides",
                    "outputs:bufferSize": "inputs:normalBufferSize",
                    "outputs:cudaDeviceIndex": "inputs:normalCudaDeviceIndex",
                },
            ),
        ],
        "node_type_id": "omni.replicator.core.OgnAugShadeSegmentation",
        "output_data_type": np.uint8,
        "output_channels": 3,
        "output_is_2d": True,
        "is_gpu_enabled": True,
        "documentation": """
            Apply shading to instance segmentation using surface normals.

            **Output Format**

            * shaded_segmentation: Shaded instance segmentation image (H,W,3)

            **Example**

            .. code:: python

                import asyncio
                import omni.replicator.core as rep

                async def test_shaded_segmentation():
                    # Add an object to look at
                    cone = rep.create.cone(semantics=[("prim", "cone")])
                    sphere = rep.create.sphere(semantics=[("prim", "sphere")])

                    cam = rep.create.camera(position=(500,500,500), look_at=cone)
                    rp = rep.create.render_product(cam, (1024, 512))

                    shaded_segmentation = rep.annotators.get("shaded_instance_segmentation")
                    shaded_segmentation.attach(rp)

                    await rep.orchestrator.step_async()
                    data = shaded_segmentation.get_data()
                    print(data.shape, data.dtype)
                    # (512, 1024, 3), uint8

                asyncio.ensure_future(test_shaded_segmentation())

        """,
    },
    {
        "name": "shaded_semantic_segmentation",
        "input_rendervars": [
            NodeConnectionTemplate(
                "semantic_segmentation",
                attributes_mapping={
                    "outputs:dataPtr": "inputs:segmentationDataPtr",
                    "outputs:strides": "inputs:segmentationStrides",
                    "outputs:bufferSize": "inputs:segmentationBufferSize",
                    "outputs:cudaDeviceIndex": "inputs:segmentationCudaDeviceIndex",
                    "outputs:width": "inputs:width",
                    "outputs:height": "inputs:height",
                },
            ),
            NodeConnectionTemplate(
                "NormalSDbuffPtr",
                attributes_mapping={
                    "outputs:dataPtr": "inputs:normalDataPtr",
                    "outputs:strides": "inputs:normalStrides",
                    "outputs:bufferSize": "inputs:normalBufferSize",
                    "outputs:cudaDeviceIndex": "inputs:normalCudaDeviceIndex",
                },
            ),
        ],
        "node_type_id": "omni.replicator.core.OgnAugShadeSegmentation",
        "output_data_type": np.uint8,
        "output_channels": 3,
        "output_is_2d": True,
        "is_gpu_enabled": True,
        "documentation": """
            Apply shading to semantic segmentation using surface normals.

            **Output Format**

            * shaded_segmentation: Shaded semantic segmentation image (H,W,3)

            **Example**

            .. code:: python

                import asyncio
                import omni.replicator.core as rep

                async def test_shaded_segmentation():
                    # Add an object to look at
                    cone = rep.create.cone(semantics=[("prim", "cone")])
                    sphere = rep.create.sphere(semantics=[("prim", "sphere")])

                    cam = rep.create.camera(position=(500,500,500), look_at=cone)
                    rp = rep.create.render_product(cam, (1024, 512))

                    shaded_segmentation = rep.annotators.get("shaded_semantic_segmentation")
                    shaded_segmentation.attach(rp)

                    await rep.orchestrator.step_async()
                    data = shaded_segmentation.get_data()
                    print(data.shape, data.dtype)
                    # (512, 1024, 3), uint8

                asyncio.ensure_future(test_shaded_segmentation())
        """,
    },
]


def register_annotators():
    # TODO: Make registering a new rendervar as a replicator function.
    for post_render_anno_description in post_render_annotators:
        AnnotatorRegistry.register_annotator_from_node(**post_render_anno_description)

    # Register from aovs
    for aov_anno_description in aovs_common + aovs_rt + aovs_pt + aovs_sensor_rtx + aovs_sensor_rtx_texture:
        AnnotatorRegistry.register_annotator_from_aov(**aov_anno_description)

    # Override the default rendervar node
    SyntheticData._ogn_rendervars.update({"InstanceSegmentationReductionSD": "InstanceSegmentationPostRender"})
    SyntheticData._ogn_rendervars.update({"UniqueInstanceSegmentationIdsSD": "InstanceSegmentationPostRender"})
    SyntheticData._ogn_rendervars["InstanceIdSegmentationReductionSD"] = "InstanceIdSegmentationPostRender"
    SyntheticData._ogn_rendervars.update({"SemanticOcclusionSD": "SemanticOcclusionPostRender"})

    # Register from nodes
    for node_anno_description in node_annotators:
        AnnotatorRegistry.register_annotator_from_node(**node_anno_description)

    # Move the display nodes to a custom ungated dispatcher
    for _, node_template in SyntheticData._ogn_templates_registry.items():
        if node_template.node_type_id != "omni.syntheticdata.SdRenderVarDisplayTexture":
            continue
        for conn in node_template.connections:
            if conn.node_template_id == "PostProcessDispatch":
                conn.node_template_id = "PostProcessDispatchUngated"
