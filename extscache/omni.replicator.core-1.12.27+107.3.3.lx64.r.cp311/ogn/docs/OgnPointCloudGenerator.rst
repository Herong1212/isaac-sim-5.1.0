.. _omni_replicator_core_OgnPointCloudGenerator_1:

.. _omni_replicator_core_OgnPointCloudGenerator:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Get Pointcloud Python
    :keywords: lang-en omnigraph node Replicator:Annotators core ogn-point-cloud-generator


Get Pointcloud Python
=====================

.. <description>

This node generates pointcloud from rgb, normals, distance_to_camera and semantic sgementations.

.. </description>


Installation
------------

To use this node enable :ref:`omni.replicator.core<ext_omni_replicator_core>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Buffer Size (*inputs:bufferSize*)", "``uint``", "Size (in bytes) of the buffer (0 if the input is a texture)", "0"
    "Camera3D Positions Cuda Device Index (*inputs:camera3dPositionsCudaDeviceIndex*)", "``int``", "Index of the device where the data lives (-1 for host data)", "-1"
    "Camera3D Positions Ptr (*inputs:camera3dPositionsPtr*)", "``uint64``", "Pointer to the raw camera 3d position data (host pointer)", "0"
    "Camera3D Positions Strides (*inputs:camera3dPositionsStrides*)", "``int[2]``", "Strides (in bytes) for Camera3dPosition.", "[0, 0]"
    "Camera View Transform (*inputs:cameraViewTransform*)", "``matrixd[4]``", "Camera view matrix", "[[1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0], [0.0, 0.0, 1.0, 0.0], [0.0, 0.0, 0.0, 1.0]]"
    "Exec (*inputs:exec*)", "``execution``", "Trigger", "None"
    "Height (*inputs:height*)", "``uint``", "Height", "0"
    "Include Unlabelled (*inputs:includeUnlabelled*)", "``bool``", "If set to true, prim with no semantics will also be in output", "False"
    "Instance Segmentation Cuda Device Index (*inputs:instanceSegmentationCudaDeviceIndex*)", "``int``", "Index of the device where the data lives (-1 for host data)", "-1"
    "Instance Segmentation Ptr (*inputs:instanceSegmentationPtr*)", "``uint64``", "Pointer to the raw instance segmentation data (host pointer)", "0"
    "Instance Segmentation Strides (*inputs:instanceSegmentationStrides*)", "``int[2]``", "Strides (in bytes) for instance segmentation.", "[0, 0]"
    "Normals Cuda Device Index (*inputs:normalsCudaDeviceIndex*)", "``int``", "Index of the device where the data lives (-1 for host data)", "-1"
    "Normals Ptr (*inputs:normalsPtr*)", "``uint64``", "Pointer to the raw normals data (host pointer)", "0"
    "Normals Strides (*inputs:normalsStrides*)", "``int[2]``", "Strides (in bytes) for normals.", "[0, 0]"
    "Rgb Cuda Device Index (*inputs:rgbCudaDeviceIndex*)", "``int``", "Index of the device where the data lives (-1 for host data)", "-1"
    "Rgb Ptr (*inputs:rgbPtr*)", "``uint64``", "Pointer to the raw rgb data (host pointer)", "0"
    "Rgb Strides (*inputs:rgbStrides*)", "``int[2]``", "Strides (in bytes) for LdrColor.", "[0, 0]"
    "Semantic Segmentation Cuda Device Index (*inputs:semanticSegmentationCudaDeviceIndex*)", "``int``", "Index of the device where the data lives (-1 for host data)", "-1"
    "Semantic Segmentation Ptr (*inputs:semanticSegmentationPtr*)", "``uint64``", "Pointer to the raw semantic segmentation data (host pointer)", "0"
    "Semantic Segmentation Strides (*inputs:semanticSegmentationStrides*)", "``int[2]``", "Strides (in bytes) for semanticSegmentation.", "[0, 0]"
    "Width (*inputs:width*)", "``uint``", "Width", "0"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Buffer Size (*outputs:bufferSize*)", "``uint``", "Size (in bytes) of the buffer (0 if the input is a texture)", "None"
    "Cuda Device Index (*outputs:cudaDeviceIndex*)", "``int``", "Index of the device where the data lives (-1 for host data)", "-1"
    "Data Ptr (*outputs:dataPtr*)", "``uint64``", "Pointer to the raw data (cuda device pointer or host pointer)", "0"
    "Data Shape (*outputs:dataShape*)", "``int[]``", "Desired dimensions of output array", "None"
    "Data Type (*outputs:dataType*)", "``token``", "Defines the data type", "float32"
    "Exec (*outputs:exec*)", "``execution``", "Trigger", "None"
    "Height (*outputs:height*)", "``uint``", "Shape of the data", "None"
    "Point Instance Buffer Size (*outputs:pointInstanceBufferSize*)", "``uint``", "Size (in bytes) of the buffer (0 if the input is a texture)", "None"
    "Point Instance Cuda Device Index (*outputs:pointInstanceCudaDeviceIndex*)", "``int``", "Index of the device where the data lives (-1 for host data)", "-1"
    "Point Instance Data Shape (*outputs:pointInstanceDataShape*)", "``int[]``", "Desired dimensions of output array", "None"
    "Point Instance Data Type (*outputs:pointInstanceDataType*)", "``token``", "Defines the data type", "uint32"
    "Point Instance Ptr (*outputs:pointInstancePtr*)", "``uint64``", "Pointer to the raw data (cuda device pointer or host pointer)", "0"
    "Point Normals Buffer Size (*outputs:pointNormalsBufferSize*)", "``uint``", "Size (in bytes) of the buffer (0 if the input is a texture)", "None"
    "Point Normals Cuda Device Index (*outputs:pointNormalsCudaDeviceIndex*)", "``int``", "Index of the device where the data lives (-1 for host data)", "-1"
    "Point Normals Data Shape (*outputs:pointNormalsDataShape*)", "``int[]``", "Desired dimensions of output array", "None"
    "Point Normals Data Type (*outputs:pointNormalsDataType*)", "``token``", "Defines the data type", "float32"
    "Point Normals Ptr (*outputs:pointNormalsPtr*)", "``uint64``", "Pointer to the raw data (cuda device pointer or host pointer)", "0"
    "Point Rgb Buffer Size (*outputs:pointRgbBufferSize*)", "``uint``", "Size (in bytes) of the buffer (0 if the input is a texture)", "None"
    "Point Rgb Cuda Device Index (*outputs:pointRgbCudaDeviceIndex*)", "``int``", "Index of the device where the data lives (-1 for host data)", "-1"
    "Point Rgb Data Shape (*outputs:pointRgbDataShape*)", "``int[]``", "Desired dimensions of output array", "None"
    "Point Rgb Data Type (*outputs:pointRgbDataType*)", "``token``", "Defines the data type", "uint8"
    "Point Rgb Ptr (*outputs:pointRgbPtr*)", "``uint64``", "Pointer to the raw data (cuda device pointer or host pointer)", "0"
    "Point Semantic Buffer Size (*outputs:pointSemanticBufferSize*)", "``uint``", "Size (in bytes) of the buffer (0 if the input is a texture)", "None"
    "Point Semantic Cuda Device Index (*outputs:pointSemanticCudaDeviceIndex*)", "``int``", "Index of the device where the data lives (-1 for host data)", "-1"
    "Point Semantic Data Shape (*outputs:pointSemanticDataShape*)", "``int[]``", "Desired dimensions of output array", "None"
    "Point Semantic Data Type (*outputs:pointSemanticDataType*)", "``token``", "Defines the data type", "uint32"
    "Point Semantic Ptr (*outputs:pointSemanticPtr*)", "``uint64``", "Pointer to the raw data (cuda device pointer or host pointer)", "0"
    "Width (*outputs:width*)", "``uint``", "Shape of the data", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.replicator.core.OgnPointCloudGenerator"
    "Version", "1"
    "Extension", "omni.replicator.core"
    "Has State?", "False"
    "Implementation Language", "Python"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Get Pointcloud Python"
    "Categories", "Replicator:Annotators"
    "__categoryDescriptions", "Replicator:Annotators,Replicator annotator nodes."
    "Generated Class Name", "OgnPointCloudGeneratorDatabase"
    "Python Module", "omni.replicator.core"

