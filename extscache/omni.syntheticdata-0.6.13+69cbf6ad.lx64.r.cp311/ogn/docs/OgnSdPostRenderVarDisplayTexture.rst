.. _omni_syntheticdata_SdPostRenderVarDisplayTexture_1:

.. _omni_syntheticdata_SdPostRenderVarDisplayTexture:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Sd Post Render Var Display Texture
    :keywords: lang-en omnigraph node graph:postRender,rendering,internal syntheticdata sd-post-render-var-display-texture


Sd Post Render Var Display Texture
==================================

.. <description>

Synthetic Data node to copy the input aov texture into the corresponding visualization texture

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
    "Camera Near Far (*inputs:cameraNearFar*)", "``float[2]``", "Camera near/far clipping range", "[0.0, 0.0]"
    "Exec (*inputs:exec*)", "``execution``", "Trigger", "None"
    "gpuFoundations (*inputs:gpu*)", "``uint64``", "Pointer to shared context containing gpu foundations", "0"
    "Instance Map SD Cuda Ptr (*inputs:instanceMapSDCudaPtr*)", "``uint64``", "cuda uint16_t buffer pointer of size numInstances containing the instance parent semantic index", "0"
    "Instance Mapping Info SD Ptr (*inputs:instanceMappingInfoSDPtr*)", "``uint64``", "uint buffer pointer containing the following information : [numInstances, minInstanceId, numSemantics, minSemanticId, numProtoSemantic]", "0"
    "Meters Per Scene Unit (*inputs:metersPerSceneUnit*)", "``float``", "Scene units to meters scale", "0.0"
    "Mode (*inputs:mode*)", "``token``", "Display mode", "autoMode"
    "Parameters (*inputs:parameters*)", "``float[4]``", "Display parameters", "[0.0, 5.0, 0.33, 0.27]"
    "Render Var (*inputs:renderVar*)", "``token``", "Name of the input RenderVar to display", ""
    "Render Var Display (*inputs:renderVarDisplay*)", "``token``", "Name of the output display RenderVar", ""
    "renderProduct (*inputs:rp*)", "``uint64``", "Pointer to render product for this view", "0"
    "Sd Display Height (*inputs:sdDisplayHeight*)", "``uint``", "Visualization texture Height", "0"
    "Sd Display Width (*inputs:sdDisplayWidth*)", "``uint``", "Visualization texture width", "0"
    "Sd Sem B Box3d Cam Corners Cuda Ptr (*inputs:sdSemBBox3dCamCornersCudaPtr*)", "``uint64``", "Cuda buffer containing the projection of the 3d bounding boxes on the camera plane represented as a float3=(u,v,z,a) for each bounding box corners", "0"
    "Sd Sem B Box3d Cam Extent Cuda Ptr (*inputs:sdSemBBox3dCamExtentCudaPtr*)", "``uint64``", "Cuda buffer containing the 2d extent of the 3d bounding boxes on the camera plane represented as a float6=(u_min,u_max,v_min,v_max,z_min,z_max)", "0"
    "Sd Sem B Box Extent Cuda Ptr (*inputs:sdSemBBoxExtentCudaPtr*)", "``uint64``", "Cuda buffer containing the extent of the bounding boxes as a float4=(u_min,v_min,u_max,v_max) for 2D or a float6=(xmin,ymin,zmin,xmax,ymax,zmax) in object space for 3D", "0"
    "Sd Sem B Box Infos Cuda Ptr (*inputs:sdSemBBoxInfosCudaPtr*)", "``uint64``", "Cuda buffer containing valid bounding boxes infos", "0"
    "Semantic Label Token SD Cuda Ptr (*inputs:semanticLabelTokenSDCudaPtr*)", "``uint64``", "cuda uint64_t buffer pointer of size numSemantics containing the semantic label token", "0"
    "Semantic Map SD Cuda Ptr (*inputs:semanticMapSDCudaPtr*)", "``uint64``", "cuda uint16_t buffer pointer of size numSemantics containing the semantic parent semantic index", "0"
    "Semantic Prim Token SD Cuda Ptr (*inputs:semanticPrimTokenSDCudaPtr*)", "``uint64``", "cuda uint64_t buffer pointer of size numSemantics containing the semantic path token", "0"
    "Semantic World Transform SD Cuda Ptr (*inputs:semanticWorldTransformSDCudaPtr*)", "``uint64``", "cuda float44 buffer pointer of size numSemantics containing the world semantic transform", "0"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Cuda Ptr (*outputs:cudaPtr*)", "``uint64``", "Display texture CUDA pointer", "None"
    "Exec (*outputs:exec*)", "``execution``", "Trigger", "None"
    "Format (*outputs:format*)", "``uint64``", "Display texture format", "None"
    "Height (*outputs:height*)", "``uint``", "Display texture height", "None"
    "Render Var Display (*outputs:renderVarDisplay*)", "``token``", "Name of the output display RenderVar", "None"
    "Width (*outputs:width*)", "``uint``", "Display texture width", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.syntheticdata.SdPostRenderVarDisplayTexture"
    "Version", "1"
    "Extension", "omni.syntheticdata"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "__tokens", "[""LdrColorSD"", ""Camera3dPositionSD"", ""DistanceToImagePlaneSD"", ""DistanceToCameraSD"", ""InstanceSegmentationSD"", ""SemanticSegmentationSD"", ""NormalSD"", ""TargetMotionSD"", ""BoundingBox2DTightSD"", ""BoundingBox2DLooseSD"", ""BoundingBox3DSD"", ""OcclusionSD"", ""TruncationSD"", ""CrossCorrespondenceSD"", ""SemanticBoundingBox2DExtentTightSD"", ""SemanticBoundingBox2DInfosTightSD"", ""SemanticBoundingBox2DExtentLooseSD"", ""SemanticBoundingBox2DInfosLooseSD"", ""SemanticBoundingBox3DExtentSD"", ""SemanticBoundingBox3DInfosSD"", ""SemanticBoundingBox3DCamCornersSD"", ""SemanticBoundingBox3DDisplayAxesSD"", ""autoMode"", ""colorMode"", ""scaled3dVectorMode"", ""clippedValueMode"", ""normalized3dVectorMode"", ""segmentationMapMode"", ""instanceMapMode"", ""semanticPathMode"", ""semanticLabelMode"", ""semanticBoundingBox2dMode"", ""rawBoundingBox2dMode"", ""semanticProjBoundingBox3dMode"", ""semanticBoundingBox3dMode"", ""rawBoundingBox3dMode"", ""pinhole"", ""perspective"", ""orthographic"", ""fisheyePolynomial""]"
    "Categories", "graph:postRender,rendering,internal"
    "Generated Class Name", "OgnSdPostRenderVarDisplayTextureDatabase"
    "Python Module", "omni.syntheticdata"

