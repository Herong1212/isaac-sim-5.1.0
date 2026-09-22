.. _omni_replicator_core_AugContrastExp_1:

.. _omni_replicator_core_AugContrastExp:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Aug Contrast Exp
    :keywords: lang-en omnigraph node Replicator compute-on-request core aug-contrast-exp


Aug Contrast Exp
================

.. <description>

This node adds contrast to an image.

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
    "Contrast Factor (*inputs:contrastFactor*)", "``float``", "Contrast factor. A value of 1.0 will produce the unchanged input image, 2.0 an image  with double the contrast, 0.5 one with half the contrast and 0 will produce a solid  grey image.", "0.5"
    "Cuda Device Index (*inputs:cudaDeviceIndex*)", "``int``", "Index of the device where the data lives (-1 for host data)", "-1"
    "Data (*inputs:data*)", "``uchar[]``", "Buffer array data", "[]"
    "Data Ptr (*inputs:dataPtr*)", "``uint64``", "Pointer to the raw data (cuda device pointer or host pointer)", "0"
    "Exec (*inputs:exec*)", "``execution``", "Trigger", "None"
    "Format (*inputs:format*)", "``uint64``", "Format", "0"
    "Height (*inputs:height*)", "``uint``", "Height", "0"
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

    "Unique ID", "omni.replicator.core.AugContrastExp"
    "Version", "1"
    "Extension", "omni.replicator.core"
    "Has State?", "True"
    "Implementation Language", "Python"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "Categories", "Replicator"
    "__categoryDescriptions", "Replicator,AugContrastExp"
    "Generated Class Name", "OgnAugContrastExpDatabase"
    "Python Module", "omni.replicator.core"

