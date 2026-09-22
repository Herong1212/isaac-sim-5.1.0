.. _omni_replicator_core_OgnAugShadeSegmentation_1:

.. _omni_replicator_core_OgnAugShadeSegmentation:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Ogn Aug Shade Segmentation
    :keywords: lang-en omnigraph node Replicator compute-on-request core ogn-aug-shade-segmentation


Ogn Aug Shade Segmentation
==========================

.. <description>

This node randomizes the background using alpha channel.

.. </description>


Installation
------------

To use this node enable :ref:`omni.replicator.core<ext_omni_replicator_core>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Exec (*inputs:exec*)", "``execution``", "Trigger", "None"
    "Format (*inputs:format*)", "``uint64``", "Format", "0"
    "Height (*inputs:height*)", "``uint``", "Height", "0"
    "Light Source (*inputs:lightSource*)", "``float[3]``", "Light source direction", "[0.0, 0.0, 1.0]"
    "Normal Buffer Size (*inputs:normalBufferSize*)", "``uint``", "Size (in bytes) of the buffer (0 if the input is a texture)", "0"
    "Normal Cuda Device Index (*inputs:normalCudaDeviceIndex*)", "``int``", "Index of the device where the data lives (-1 for host data)", "-1"
    "Normal Data (*inputs:normalData*)", "``uchar[]``", "Buffer array data", "[]"
    "Normal Data Ptr (*inputs:normalDataPtr*)", "``uint64``", "Pointer to the raw data (cuda device pointer or host pointer)", "0"
    "Normal Strides (*inputs:normalStrides*)", "``int[2]``", "Strides (in bytes) ([0,0] if the input is a buffer)", "[0, 0]"
    "Segmentation Buffer Size (*inputs:segmentationBufferSize*)", "``uint``", "Size (in bytes) of the buffer (0 if the input is a texture)", "0"
    "Segmentation Cuda Device Index (*inputs:segmentationCudaDeviceIndex*)", "``int``", "Index of the device where the data lives (-1 for host data)", "-1"
    "Segmentation Data (*inputs:segmentationData*)", "``uchar[]``", "Buffer array data", "[]"
    "Segmentation Data Ptr (*inputs:segmentationDataPtr*)", "``uint64``", "Pointer to the raw data (cuda device pointer or host pointer)", "0"
    "Segmentation Strides (*inputs:segmentationStrides*)", "``int[2]``", "Strides (in bytes) ([0,0] if the input is a buffer)", "[0, 0]"
    "Use Candy Colours (*inputs:useCandyColours*)", "``bool``", "If true, replace segmentation colours with random candy colours", "False"
    "Width (*inputs:width*)", "``uint``", "Width", "0"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Buffer Size (*outputs:bufferSize*)", "``uint``", "Size (in bytes) of the buffer (0 if the input is a texture)", "None"
    "Cuda Device Index (*outputs:cudaDeviceIndex*)", "``int``", "Index of the device where the data lives (-1 for host data)", "-1"
    "Data Ptr (*outputs:dataPtr*)", "``uint64``", "Pointer to the raw data (cuda device pointer or host pointer)", "0"
    "Exec (*outputs:exec*)", "``execution``", "Trigger", "None"
    "Format (*outputs:format*)", "``uint``", "Format", "None"
    "Height (*outputs:height*)", "``uint``", "Shape of the data", "None"
    "Strides (*outputs:strides*)", "``int[2]``", "Strides (in bytes) ([0,0] if the input is a buffer)", "None"
    "Width (*outputs:width*)", "``uint``", "Shape of the data", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.replicator.core.OgnAugShadeSegmentation"
    "Version", "1"
    "Extension", "omni.replicator.core"
    "Has State?", "True"
    "Implementation Language", "Python"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "Categories", "Replicator"
    "__categoryDescriptions", "Replicator,OgnAugShadeSegmentation"
    "Generated Class Name", "OgnAugShadeSegmentationDatabase"
    "Python Module", "omni.replicator.core"

