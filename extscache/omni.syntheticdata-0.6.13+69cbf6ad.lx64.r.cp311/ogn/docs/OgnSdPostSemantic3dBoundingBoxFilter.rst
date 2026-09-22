.. _omni_syntheticdata_SdPostSemantic3dBoundingBoxFilter_1:

.. _omni_syntheticdata_SdPostSemantic3dBoundingBoxFilter:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Sd Post Semantic3d Bounding Box Filter
    :keywords: lang-en omnigraph node graph:postRender,rendering syntheticdata sd-post-semantic3d-bounding-box-filter


Sd Post Semantic3d Bounding Box Filter
======================================

.. <description>

Synthetic Data node to cull the semantic 3d bounding boxes.

.. </description>


Installation
------------

To use this node enable :ref:`omni.syntheticdata<ext_omni_syntheticdata>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Exec (*inputs:exec*)", "``execution``", "Trigger", "None"
    "gpuFoundations (*inputs:gpu*)", "``uint64``", "Pointer to shared context containing gpu foundations", "0"
    "Instance Mapping Info SD Ptr (*inputs:instanceMappingInfoSDPtr*)", "``uint64``", "uint buffer pointer containing the following information : [numInstances, minInstanceId, numSemantics, minSemanticId, numProtoSemantic]", "0"
    "Meters Per Scene Unit (*inputs:metersPerSceneUnit*)", "``float``", "Scene units to meters scale", "0.01"
    "renderProduct (*inputs:rp*)", "``uint64``", "Pointer to render product for this view", "0"
    "Sd Sem B Box3d Cam Corners Cuda Ptr (*inputs:sdSemBBox3dCamCornersCudaPtr*)", "``uint64``", "Cuda buffer containing the projection of the 3d bounding boxes on the camera plane represented as a float3=(u,v,z,a) for each bounding box corners", "0"
    "Sd Sem B Box Infos Cuda Ptr (*inputs:sdSemBBoxInfosCudaPtr*)", "``uint64``", "Cuda buffer containing valid bounding boxes infos", "0"
    "Viewport Near Far (*inputs:viewportNearFar*)", "``float[2]``", "near and far plane (in scene units) used to clip the 3d bounding boxes.", "[0.0, -1.0]"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Exec (*outputs:exec*)", "``execution``", "Trigger", "None"
    "Sd Sem B Box Infos Cuda Ptr (*outputs:sdSemBBoxInfosCudaPtr*)", "``uint64``", "Cuda buffer containing valid bounding boxes infos", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.syntheticdata.SdPostSemantic3dBoundingBoxFilter"
    "Version", "1"
    "Extension", "omni.syntheticdata"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "__tokens", "[""SemanticBoundingBox3DInfosSD"", ""SemanticBoundingBox3DFilterInfosSD""]"
    "Categories", "graph:postRender,rendering"
    "Generated Class Name", "OgnSdPostSemantic3dBoundingBoxFilterDatabase"
    "Python Module", "omni.syntheticdata"

