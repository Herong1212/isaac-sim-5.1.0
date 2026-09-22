.. _omni_replicator_core_InstanceIdSegmentationLegacy_1:

.. _omni_replicator_core_InstanceIdSegmentationLegacy:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Instance Id Segmentation Legacy
    :keywords: lang-en omnigraph node Replicator core instance-id-segmentation-legacy


Instance Id Segmentation Legacy
===============================

.. <description>

This node outputs the legacy instance id segmentation data output

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
    "Colorize (*inputs:colorize*)", "``bool``", "If true, convert semantic IDs into colors.", "False"
    "Cuda Device Index (*inputs:cudaDeviceIndex*)", "``int``", "Index of the device where the data lives (-1 for host data)", "-1"
    "Data Ptr (*inputs:dataPtr*)", "``uint64``", "Pointer to the raw instance segmentation reduction data.", "0"
    "Data Type (*inputs:dataType*)", "``token``", "Defines the data type", ""
    "Exec (*inputs:exec*)", "``execution``", "Trigger", "None"
    "Height (*inputs:height*)", "``uint``", "Shape of the data", "0"
    "Ids (*inputs:ids*)", "``uint[]``", "Unoccluded instance ids (or color, if `colorize` is set to True).", "[]"
    "Labels (*inputs:labels*)", "``token[]``", "Prim path of the prim.", "[]"
    "Strides (*inputs:strides*)", "``int[2]``", "Strides (in bytes) for instance segmentation.", "[0, 0]"
    "Width (*inputs:width*)", "``uint``", "Shape of the data", "0"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Buffer Size (*outputs:bufferSize*)", "``uint``", "Size (in bytes) of the buffer (0 if the input is a texture)", "None"
    "Data (*outputs:data*)", "``uchar[]``", "Instance id segmentation data", "[]"
    "Data Shape (*outputs:dataShape*)", "``int[]``", "Desired dimensions of output array", "None"
    "Data Type (*outputs:dataType*)", "``token``", "Defines the data type", "None"
    "Exec (*outputs:exec*)", "``execution``", "Trigger", "None"
    "Height (*outputs:height*)", "``uint``", "Shape of the data", "None"
    "Id To Labels (*outputs:idToLabels*)", "``string``", "Mapping from id to prim paths of the prim.", "None"
    "Width (*outputs:width*)", "``uint``", "Shape of the data", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.replicator.core.InstanceIdSegmentationLegacy"
    "Version", "1"
    "Extension", "omni.replicator.core"
    "Has State?", "True"
    "Implementation Language", "Python"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "Categories", "Replicator"
    "__categoryDescriptions", "Replicator,Instance id segmentation Legacy"
    "Generated Class Name", "OgnInstanceIdSegmentationLegacyDatabase"
    "Python Module", "omni.replicator.core"

