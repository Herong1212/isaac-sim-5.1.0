.. _omni_replicator_core_AugConv2dExp_1:

.. _omni_replicator_core_AugConv2dExp:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Aug Conv2d Exp
    :keywords: lang-en omnigraph node Replicator compute-on-request core aug-conv2d-exp


Aug Conv2d Exp
==============

.. <description>

This node ....

.. </description>


Installation
------------

To use this node enable :ref:`omni.replicator.core<ext_omni_replicator_core>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Alpha (*inputs:alpha*)", "``float``", "strength of convolution", "0.7"
    "Buffer Size (*inputs:bufferSize*)", "``uint``", "Size (in bytes) of the buffer (0 if the input is a texture)", "0"
    "Cuda Device Index (*inputs:cudaDeviceIndex*)", "``int``", "Index of the device where the data lives (-1 for host data)", "-1"
    "Data (*inputs:data*)", "``uchar[]``", "Buffer array data", "[]"
    "Data Ptr (*inputs:dataPtr*)", "``uint64``", "Pointer to the raw data (cuda device pointer or host pointer)", "0"
    "Exec (*inputs:exec*)", "``execution``", "Trigger", "None"
    "Format (*inputs:format*)", "``uint64``", "Format", "0"
    "Height (*inputs:height*)", "``uint``", "Height", "0"
    "Kernel (*inputs:kernel*)", "``float[]``", "size of conv kernel", "[1, 0, -1, 2, 0, -2, 1, 0, -1]"
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

    "Unique ID", "omni.replicator.core.AugConv2dExp"
    "Version", "1"
    "Extension", "omni.replicator.core"
    "Has State?", "True"
    "Implementation Language", "Python"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "Categories", "Replicator"
    "__categoryDescriptions", "Replicator,AugConv2dExp"
    "Generated Class Name", "OgnAugConv2dExpDatabase"
    "Python Module", "omni.replicator.core"

