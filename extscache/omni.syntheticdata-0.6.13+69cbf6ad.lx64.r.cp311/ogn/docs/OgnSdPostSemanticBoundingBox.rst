.. _omni_syntheticdata_SdPostSemanticBoundingBox_1:

.. _omni_syntheticdata_SdPostSemanticBoundingBox:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Sd Post Semantic Bounding Box
    :keywords: lang-en omnigraph node graph:postRender,rendering syntheticdata sd-post-semantic-bounding-box


Sd Post Semantic Bounding Box
=============================

.. <description>

Synthetic Data node to compute the bounding boxes of the scene semantic entities.

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
    "Instance Map SD Cuda Ptr (*inputs:instanceMapSDCudaPtr*)", "``uint64``", "cuda uint16_t buffer pointer of size numInstances containing the instance parent semantic index", "0"
    "Instance Mapping Info SD Ptr (*inputs:instanceMappingInfoSDPtr*)", "``uint64``", "uint buffer pointer containing the following information : [numInstances, minInstanceId, numSemantics, minSemanticId, numProtoSemantic]", "0"
    "Render Product Resolution (*inputs:renderProductResolution*)", "``int[2]``", "RenderProduct resolution", "[0, 0]"
    "Render Var (*inputs:renderVar*)", "``token``", "Name of the BoundingBox RenderVar to process", ""
    "renderProduct (*inputs:rp*)", "``uint64``", "Pointer to render product for this view", "0"
    "Semantic Local Transform SD Cuda Ptr (*inputs:semanticLocalTransformSDCudaPtr*)", "``uint64``", "cuda float44 buffer pointer of size numSemantics containing the local semantic transform", "0"
    "Semantic Map SD Cuda Ptr (*inputs:semanticMapSDCudaPtr*)", "``uint64``", "cuda uint16_t buffer pointer of size numSemantics containing the semantic parent semantic index", "0"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Exec (*outputs:exec*)", "``execution``", "Trigger", "None"
    "Sd Sem B Box Extent Cuda Ptr (*outputs:sdSemBBoxExtentCudaPtr*)", "``uint64``", "Cuda buffer containing the extent of the bounding boxes as a float4=(u_min,v_min,u_max,v_max) for 2D or a float6=(xmin,ymin,zmin,xmax,ymax,zmax) in object space for 3D", "None"
    "Sd Sem B Box Infos Cuda Ptr (*outputs:sdSemBBoxInfosCudaPtr*)", "``uint64``", "Cuda buffer containing valid bounding boxes infos", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.syntheticdata.SdPostSemanticBoundingBox"
    "Version", "1"
    "Extension", "omni.syntheticdata"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "__tokens", "[""BoundingBox2DLooseSD"", ""BoundingBox2DTightSD"", ""SemanticBoundingBox2DExtentLooseSD"", ""SemanticBoundingBox2DInfosLooseSD"", ""SemanticBoundingBox2DExtentTightSD"", ""SemanticBoundingBox2DInfosTightSD"", ""BoundingBox3DSD"", ""SemanticBoundingBox3DExtentSD"", ""SemanticBoundingBox3DInfosSD""]"
    "Categories", "graph:postRender,rendering"
    "Generated Class Name", "OgnSdPostSemanticBoundingBoxDatabase"
    "Python Module", "omni.syntheticdata"

