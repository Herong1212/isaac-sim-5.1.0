.. _omni_replicator_core_OgnGetSkeletonData_2:

.. _omni_replicator_core_OgnGetSkeletonData:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Get Skeleton Data
    :keywords: lang-en omnigraph node Replicator:Annotators compute-on-request core ogn-get-skeleton-data


Get Skeleton Data
=================

.. <description>

This node retrieves skeleton data given skeleton prims and camera paramters

.. </description>


Installation
------------

To use this node enable :ref:`omni.replicator.core<ext_omni_replicator_core>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Camera Aperture (*inputs:cameraAperture*)", "``float[2]``", "Camera horizontal and vertical aperture", "[0.0, 0.0]"
    "Camera Fisheye Max FOV (*inputs:cameraFisheyeMaxFOV*)", "``float``", "Camera fisheye maximum field of view", "0.0"
    "Camera Fisheye Nominal Height (*inputs:cameraFisheyeNominalHeight*)", "``int``", "Camera fisheye nominal height", "0"
    "Camera Fisheye Nominal Width (*inputs:cameraFisheyeNominalWidth*)", "``int``", "Camera fisheye nominal width", "0"
    "Camera Fisheye Optical Centre (*inputs:cameraFisheyeOpticalCentre*)", "``float[2]``", "Camera fisheye optical centre", "[0.0, 0.0]"
    "Camera Fisheye Polynomial (*inputs:cameraFisheyePolynomial*)", "``float[]``", "Camera fisheye polynomial", "[]"
    "Camera Focal Length (*inputs:cameraFocalLength*)", "``float``", "Camera focal length", "0.0"
    "Camera Model (*inputs:cameraModel*)", "``token``", "Camera model (pinhole or fisheye models)", ""
    "Camera Near Far (*inputs:cameraNearFar*)", "``float[2]``", "Camera near/far clipping range", "[0.0, 0.0]"
    "Camera Projection (*inputs:cameraProjection*)", "``matrixd[4]``", "Camera projection matrix", "[[1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0], [0.0, 0.0, 1.0, 0.0], [0.0, 0.0, 0.0, 1.0]]"
    "Camera View Transform (*inputs:cameraViewTransform*)", "``matrixd[4]``", "Camera view matrix", "[[1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0], [0.0, 0.0, 1.0, 0.0], [0.0, 0.0, 0.0, 1.0]]"
    "Exec (*inputs:exec*)", "``execution``", "exec", "None"
    "Fabric Joints (*inputs:fabricJoints*)", "``token[]``", "list of fabric joint prim paths", "[]"
    "Fabric Prims (*inputs:fabricPrims*)", "``token[]``", "list of fabric skeleton root prim paths", "[]"
    "Instance Segmentation Cuda Device Index (*inputs:instanceSegmentationCudaDeviceIndex*)", "``int``", "Index of the device where the data lives (-1 for host data)", "-1"
    "Instance Segmentation Height (*inputs:instanceSegmentationHeight*)", "``uint``", "Instance Segmentation buffer height", "0"
    "Instance Segmentation Ids (*inputs:instanceSegmentationIds*)", "``uint[]``", "Mapping from id to semantic labels.", "[]"
    "Instance Segmentation Labels (*inputs:instanceSegmentationLabels*)", "``token[]``", "Mapping from id to prim paths.", "[]"
    "Instance Segmentation Ptr (*inputs:instanceSegmentationPtr*)", "``uint64``", "Pointer to the raw instance segmentation data (host pointer)", "0"
    "Instance Segmentation Semantics (*inputs:instanceSegmentationSemantics*)", "``token[]``", "Mapping from id to semantic labels.", "[]"
    "Instance Segmentation Strides (*inputs:instanceSegmentationStrides*)", "``int[2]``", "Strides (in bytes) for instance segmentation.", "[0, 0]"
    "Instance Segmentation Width (*inputs:instanceSegmentationWidth*)", "``uint``", "Instance Segmentation buffer width", "0"
    "Joint World Orientations (*inputs:jointWorldOrientations*)", "``float[4][]``", "World rotations for skeleton prims from fabric", "[]"
    "Joint World Positions (*inputs:jointWorldPositions*)", "``double[3][]``", "World translations for skeleton prims from fabric", "[]"
    "Joint World Scales (*inputs:jointWorldScales*)", "``float[3][]``", "World scales for skeleton prims from fabric", "[]"
    "Prim World Orientations (*inputs:primWorldOrientations*)", "``float[4][]``", "World rotations for skeleton prims from fabric", "[]"
    "Prim World Positions (*inputs:primWorldPositions*)", "``double[3][]``", "World translations for skeleton prims from fabric", "[]"
    "Prim World Scales (*inputs:primWorldScales*)", "``float[3][]``", "World scales for skeleton prims from fabric", "[]"
    "Prims (*inputs:prims*)", "``token[]``", "list of skeleton prim paths", "[]"
    "Render Product Path (*inputs:renderProductPath*)", "``token``", "Path of the render product to use for 2d projections", ""
    "Use Skel Joints (*inputs:useSkelJoints*)", "``bool``", "Get skeleton joint information using the skelJoints information", "False"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Animation Variant (*outputs:animationVariant*)", "``token[]``", "The name of the animation variant assigned.", "None"
    "Asset Path (*outputs:assetPath*)", "``token[]``", "The referenced asset path.", "None"
    "Exec (*outputs:exec*)", "``execution``", "exec", "None"
    "Global Translations (*outputs:globalTranslations*)", "``float[3][]``", "The skeleton joint translations in global space.", "None"
    "Global Translations Sizes (*outputs:globalTranslationsSizes*)", "``int[]``", "The size of each skeleton globalTranslations array.", "None"
    "In View (*outputs:inView*)", "``bool[]``", "Whether the skeleton is in the camera view.", "None"
    "Joint Occlusions (*outputs:jointOcclusions*)", "``bool[]``", "Whether the joint is occluded.", "None"
    "Joint Occlusions Sizes (*outputs:jointOcclusionsSizes*)", "``int[]``", "The size of each skeleton jointOcclusions array.", "None"
    "Local Rotations (*outputs:localRotations*)", "``float[4][]``", "The skeleton joint rotations in local space.", "None"
    "Local Rotations Sizes (*outputs:localRotationsSizes*)", "``int[]``", "The size of each skeleton localRotations array.", "None"
    "Num Skeletons (*outputs:numSkeletons*)", "``int``", "The number of skeletons in output data.", "None"
    "Occlusion Types (*outputs:occlusionTypes*)", "``token[]``", "The semantic name of the object occluding the joint.", "None"
    "Occlusion Types Sizes (*outputs:occlusionTypesSizes*)", "``int[]``", "The size of each skeleton occlusionTypes array.", "None"
    "Rest Global Translations (*outputs:restGlobalTranslations*)", "``float[3][]``", "The rest skeleton joint translations in global space.", "None"
    "Rest Global Translations Sizes (*outputs:restGlobalTranslationsSizes*)", "``int[]``", "The size of each skeleton restGlobalTranslations array.", "None"
    "Rest Local Rotations (*outputs:restLocalRotations*)", "``float[4][]``", "The rest skeleton joint rotations in local space.", "None"
    "Rest Local Rotations Sizes (*outputs:restLocalRotationsSizes*)", "``int[]``", "The size of each skeleton restLocalRotations array.", "None"
    "Rest Local Translations (*outputs:restLocalTranslations*)", "``float[3][]``", "The rest skeleton joint translations in local space.", "None"
    "Rest Local Translations Sizes (*outputs:restLocalTranslationsSizes*)", "``int[]``", "The size of each skeleton restLocalTranslations array.", "None"
    "Skel Name (*outputs:skelName*)", "``token[]``", "The skeleton name.", "None"
    "Skel Path (*outputs:skelPath*)", "``token[]``", "The USD stage path to the skeleton.", "None"
    "Skeleton Data (*outputs:skeletonData*)", "``string``", "Skeleton Data", "{}"
    "Skeleton Joints (*outputs:skeletonJoints*)", "``token[]``", "The paths of all the skeleton joints.", "None"
    "Skeleton Parents (*outputs:skeletonParents*)", "``int[]``", "The ID of all the skeleton joints.", "None"
    "Skeleton Parents Sizes (*outputs:skeletonParentsSizes*)", "``int[]``", "The size of each skeleton skeletonParents array.", "None"
    "Translations2D (*outputs:translations2d*)", "``float[2][]``", "The 2D projected skeleton joint positions.", "None"
    "Translations2D Sizes (*outputs:translations2dSizes*)", "``int[]``", "The size of each skeleton translations2d array.", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.replicator.core.OgnGetSkeletonData"
    "Version", "2"
    "Extension", "omni.replicator.core"
    "Has State?", "False"
    "Implementation Language", "Python"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Get Skeleton Data"
    "Categories", "Replicator:Annotators"
    "__categoryDescriptions", "Replicator:Annotators,Replicator annotator nodes."
    "Generated Class Name", "OgnGetSkeletonDataDatabase"
    "Python Module", "omni.replicator.core"

