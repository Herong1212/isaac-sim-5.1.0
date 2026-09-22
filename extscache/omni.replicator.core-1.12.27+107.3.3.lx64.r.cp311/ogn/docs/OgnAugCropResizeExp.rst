.. _omni_replicator_core_AugCropResizeExp_1:

.. _omni_replicator_core_AugCropResizeExp:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Aug Crop Resize Exp
    :keywords: lang-en omnigraph node Replicator compute-on-request core aug-crop-resize-exp


Aug Crop Resize Exp
===================

.. <description>

This node crops and resizes an image.

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
    "Crop Factor (*inputs:cropFactor*)", "``float``", "Value between 0 and 1 specifying the crop factor", "0.5"
    "Cuda Device Index (*inputs:cudaDeviceIndex*)", "``int``", "Index of the device where the data lives (-1 for host data)", "-1"
    "Data (*inputs:data*)", "``uchar[]``", "Buffer array data", "[]"
    "Data Ptr (*inputs:dataPtr*)", "``uint64``", "Pointer to the raw data (cuda device pointer or host pointer)", "0"
    "Exec (*inputs:exec*)", "``execution``", "Trigger", "None"
    "Format (*inputs:format*)", "``uint64``", "Format", "0"
    "Height (*inputs:height*)", "``uint``", "Height", "0"
    "Offset Factor (*inputs:offsetFactor*)", "``float[2]``", "Value between -1 and 1 specifying the offset factor. (+<value>, +<value>) indicate up and right, (-<value>, -<value>) indicates down and left.", "[0.5, 0.5]"
    "Strides (*inputs:strides*)", "``int[2]``", "Strides (in bytes) ([0,0] if the input is a buffer)", "[0, 0]"
    "Width (*inputs:width*)", "``uint``", "Width", "0"
    "Xform (*inputs:xform*)", "``matrixd[3]``", "Input augmentation transform", "[[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Buffer Size (*outputs:bufferSize*)", "``uint``", "Size (in bytes) of the buffer (0 if the input is a texture)", "None"
    "Cuda Device Index (*outputs:cudaDeviceIndex*)", "``int``", "Index of the device where the data lives (-1 for host data)", "-1"
    "Data Ptr (*outputs:dataPtr*)", "``uint64``", "Pointer to the raw data (cuda device pointer or host pointer)", "0"
    "Exec (*outputs:exec*)", "``execution``", "Trigger", "None"
    "Format (*outputs:format*)", "``uint64``", "Format", "None"
    "Height (*outputs:height*)", "``uint``", "Shape of the data", "None"
    "Strides (*outputs:strides*)", "``int[2]``", "Strides (in bytes) ([0,0] if the input is a buffer)", "None"
    "Width (*outputs:width*)", "``uint``", "Shape of the data", "None"
    "Xform (*outputs:xform*)", "``matrixd[3]``", "Output augmentation transform", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.replicator.core.AugCropResizeExp"
    "Version", "1"
    "Extension", "omni.replicator.core"
    "Has State?", "True"
    "Implementation Language", "Python"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "Categories", "Replicator"
    "__categoryDescriptions", "Replicator,AugCropResizeExp"
    "Generated Class Name", "OgnAugCropResizeExpDatabase"
    "Python Module", "omni.replicator.core"

