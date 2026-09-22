.. _omni_replicator_core_InstanceIdSegmentation_1:

.. _omni_replicator_core_InstanceIdSegmentation:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Instance Id Segmentation
    :keywords: lang-en omnigraph node Replicator:Annotators compute-on-request core instance-id-segmentation


Instance Id Segmentation
========================

.. <description>

This node outputs the instance id segmentation.

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
    "Colorize (*inputs:colorize*)", "``bool``", "If true, convert instance IDs into colors.", "False"
    "Cuda Device Index (*inputs:cudaDeviceIndex*)", "``int``", "Index of the device where the data lives (-1 for host data)", "-1"
    "Data Ptr (*inputs:dataPtr*)", "``uint64``", "Pointer to the raw instance ID segmentation reduction data. (host pointer)", "0"
    "Exec (*inputs:exec*)", "``execution``", "Trigger", "None"
    "Height (*inputs:height*)", "``uint``", "Height", "0"
    "Instance Id Token Ptr (*inputs:instanceIdTokenPtr*)", "``uint64``", "Pointer to the map from raw instance id to prim path.", "0"
    "Sd IM Instance Tokens (*inputs:sdIMInstanceTokens*)", "``token[]``", "Instance array containing the token for every instances", "[]"
    "Sd IM Min Instance Index (*inputs:sdIMMinInstanceIndex*)", "``uint``", "Instance id of the first instance in the instance arrays", "0"
    "Sd IM Num Instances (*inputs:sdIMNumInstances*)", "``uint``", "Number of instances in the instance arrays", "0"
    "Strides (*inputs:strides*)", "``int[2]``", "Strides (in bytes) for instance segmentation.", "[0, 0]"
    "Width (*inputs:width*)", "``uint``", "Width", "0"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Buffer Size (*outputs:bufferSize*)", "``uint``", "Size (in bytes) of the buffer (0 if the input is a texture)", "None"
    "Cuda Device Index (*outputs:cudaDeviceIndex*)", "``int``", "Index of the device where the data lives (-1 for host data)", "-1"
    "Data Ptr (*outputs:dataPtr*)", "``uint64``", "Pointer to the raw instance segmentation reduction data. (host pointer)", "0"
    "Data Type (*outputs:dataType*)", "``token``", "Defines the data type", "None"
    "Exec (*outputs:exec*)", "``execution``", "Trigger", "None"
    "Height (*outputs:height*)", "``uint``", "Shape of the data", "None"
    "Ids (*outputs:ids*)", "``uint[]``", "Unoccluded instance ids (or color, if `colorize` is set to True).", "None"
    "Labels (*outputs:labels*)", "``token[]``", "Prim path of the prim.", "None"
    "Strides (*outputs:strides*)", "``int[2]``", "Strides (in bytes) for instance segmentation.", "None"
    "Width (*outputs:width*)", "``uint``", "Shape of the data", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.replicator.core.InstanceIdSegmentation"
    "Version", "1"
    "Extension", "omni.replicator.core"
    "Has State?", "True"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "Categories", "Replicator:Annotators"
    "__categoryDescriptions", "Replicator:Annotators,Replicator annotator nodes."
    "Generated Class Name", "OgnInstanceIdSegmentationDatabase"
    "Python Module", "omni.replicator.core"

