.. _omni_replicator_core_OgnAugmentCPU_1:

.. _omni_replicator_core_OgnAugmentCPU:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Augment
    :keywords: lang-en omnigraph node Replicator:Annotators core ogn-augment-c-p-u


Augment
=======

.. <description>

This node performs augmentation on an AOV

.. </description>


Installation
------------

To use this node enable :ref:`omni.replicator.core<ext_omni_replicator_core>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Augmentation Function Name (*inputs:augmentationFunctionName*)", "``token``", "Name of augmentation function to run when computing node", ""
    "Augmentation Script (*inputs:augmentationScript*)", "``string``", "Augmentation script", ""
    "Buffer Size (*inputs:bufferSize*)", "``uint``", "Size (in bytes) of the buffer (0 if the input is a texture)", "0"
    "Cuda Device Index (*inputs:cudaDeviceIndex*)", "``int``", "Index of the device where the data lives (-1 for host data)", "-1"
    "Data (*inputs:data*)", "``uchar[]``", "Input data, can be used instead of dataPtr pattern", "[]"
    "Data Ptr (*inputs:dataPtr*)", "``uint64``", "Pointer to the raw data (cuda device pointer or host pointer)", "0"
    "Data Shape (*inputs:dataShape*)", "``int[]``", "Input array dimensions", "[]"
    "Data Type (*inputs:dataType*)", "``token``", "Defines the data type", ""
    "Exec (*inputs:exec*)", "``execution``", "Execution in", "None"
    "Format (*inputs:format*)", "``uint64``", "Format", "0"
    "Height (*inputs:height*)", "``uint``", "Height", "0"
    "Strides (*inputs:strides*)", "``int[2]``", "Strides (in bytes) ([0,0] if the input is a buffer)", "[0, 0]"
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
    "Data Type (*outputs:dataType*)", "``token``", "Defines the data type", "uint8"
    "Exec (*outputs:exec*)", "``execution``", "Execution out", "None"
    "Format (*outputs:format*)", "``uint64``", "Format", "None"
    "Height (*outputs:height*)", "``uint``", "Shape of the data", "None"
    "Strides (*outputs:strides*)", "``int[2]``", "Strides (in bytes) ([0,0] if the input is a buffer)", "[0, 0]"
    "Width (*outputs:width*)", "``uint``", "Shape of the data", "None"


State
-----
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Omni Initialized (*state:omni_initialized*)", "``bool``", "Hidden state attribute used internally to control when the setup script is executed", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.replicator.core.OgnAugmentCPU"
    "Version", "1"
    "Extension", "omni.replicator.core"
    "Has State?", "True"
    "Implementation Language", "Python"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Augment"
    "Categories", "Replicator:Annotators"
    "__categoryDescriptions", "Replicator:Annotators,Replicator annotator nodes."
    "Generated Class Name", "OgnAugmentCPUDatabase"
    "Python Module", "omni.replicator.core"

