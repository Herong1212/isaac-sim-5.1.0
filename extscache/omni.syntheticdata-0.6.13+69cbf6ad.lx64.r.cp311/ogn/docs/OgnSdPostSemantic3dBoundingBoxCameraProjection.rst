.. _omni_syntheticdata_SdPostSemantic3dBoundingBoxCameraProjection_1:

.. _omni_syntheticdata_SdPostSemantic3dBoundingBoxCameraProjection:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Sd Post Semantic3d Bounding Box Camera Projection
    :keywords: lang-en omnigraph node graph:postRender,rendering syntheticdata sd-post-semantic3d-bounding-box-camera-projection


Sd Post Semantic3d Bounding Box Camera Projection
=================================================

.. <description>

Synthetic Data node to project 3d bounding boxes data in camera space.

.. </description>


Installation
------------

To use this node enable :ref:`omni.syntheticdata<ext_omni_syntheticdata>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Camera Fisheye Params (*inputs:cameraFisheyeParams*)", "``float[]``", "Camera fisheye projection parameters", "[]"
    "Camera Model (*inputs:cameraModel*)", "``int``", "Camera model (pinhole or fisheye models)", "0"
    "Camera Near Far (*inputs:cameraNearFar*)", "``float[2]``", "Camera near/far clipping range", "[1.0, 10000000.0]"
    "Exec (*inputs:exec*)", "``execution``", "Trigger", "None"
    "gpuFoundations (*inputs:gpu*)", "``uint64``", "Pointer to shared context containing gpu foundations", "0"
    "Instance Mapping Info SD Ptr (*inputs:instanceMappingInfoSDPtr*)", "``uint64``", "uint buffer pointer containing the following information : [numInstances, minInstanceId, numSemantics, minSemanticId, numProtoSemantic]", "0"
    "Meters Per Scene Unit (*inputs:metersPerSceneUnit*)", "``float``", "Scene units to meters scale", "0.01"
    "Render Product Resolution (*inputs:renderProductResolution*)", "``int[2]``", "RenderProduct resolution", "[65536, 65536]"
    "renderProduct (*inputs:rp*)", "``uint64``", "Pointer to render product for this view", "0"
    "Sd Sem B Box Extent Cuda Ptr (*inputs:sdSemBBoxExtentCudaPtr*)", "``uint64``", "Cuda buffer containing the extent of the bounding boxes as a float4=(u_min,v_min,u_max,v_max) for 2D or a float6=(xmin,ymin,zmin,xmax,ymax,zmax) in object space for 3D", "0"
    "Sd Sem B Box Infos Cuda Ptr (*inputs:sdSemBBoxInfosCudaPtr*)", "``uint64``", "Cuda buffer containing valid bounding boxes infos", "0"
    "Semantic World Transform SD Cuda Ptr (*inputs:semanticWorldTransformSDCudaPtr*)", "``uint64``", "cuda float44 buffer pointer of size numSemantics containing the world semantic transform", "0"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Exec (*outputs:exec*)", "``execution``", "Trigger", "None"
    "Sd Sem B Box3d Cam Corners Cuda Ptr (*outputs:sdSemBBox3dCamCornersCudaPtr*)", "``uint64``", "Cuda buffer containing the projection of the 3d bounding boxes on the camera plane represented as a float4=(u,v,z,a) for each bounding box corners", "None"
    "Sd Sem B Box3d Cam Extent Cuda Ptr (*outputs:sdSemBBox3dCamExtentCudaPtr*)", "``uint64``", "Cuda buffer containing the 2d extent of the 3d bounding boxes on the camera plane represented as a float6=(u_min,u_max,v_min,v_max,z_min,z_max)", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.syntheticdata.SdPostSemantic3dBoundingBoxCameraProjection"
    "Version", "1"
    "Extension", "omni.syntheticdata"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "__tokens", "[""SemanticBoundingBox3DInfosSD"", ""SemanticBoundingBox3DCamCornersSD"", ""SemanticBoundingBox3DCamExtentSD""]"
    "Categories", "graph:postRender,rendering"
    "Generated Class Name", "OgnSdPostSemantic3dBoundingBoxCameraProjectionDatabase"
    "Python Module", "omni.syntheticdata"

