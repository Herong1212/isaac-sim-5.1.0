.. _omni_replicator_core_SemanticSegmentation_1:

.. _omni_replicator_core_SemanticSegmentation:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Semantic Segmentation
    :keywords: lang-en omnigraph node Replicator:Annotators compute-on-request core semantic-segmentation


Semantic Segmentation
=====================

.. <description>

This node outputs the semantic segmentation.

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
    "Exec (*inputs:exec*)", "``execution``", "Trigger", "None"
    "Height (*inputs:height*)", "``uint``", "Shape of the data", "0"
    "Ids (*inputs:ids*)", "``uint[]``", "Unoccluded semantic u ids (or color, if `colorize` is set to True).", "[]"
    "Instance Segmentation Cuda Device Index (*inputs:instanceSegmentationCudaDeviceIndex*)", "``int``", "Index of the device where the data lives (-1 for host data) for instance segmentationSD", "-1"
    "Instance Segmentation Ptr (*inputs:instanceSegmentationPtr*)", "``uint64``", "Pointer to the raw instance segmetation data", "0"
    "Instance Segmentation Strides (*inputs:instanceSegmentationStrides*)", "``int[2]``", "Strides (in bytes) for InstanceSegmentationSD.", "[0, 0]"
    "Labels (*inputs:labels*)", "``token[]``", "Prim path of the prim.", "[]"
    "Mapping (*inputs:mapping*)", "``string``", "Optional mapping enforcing semantics to specific IDs or colors.", "{}"
    "Semantic Filter Name (*inputs:semanticFilterName*)", "``token``", "name of Semantic Filter to use", ""
    "Semantics (*inputs:semantics*)", "``token[]``", "Semantic labels that correspond to the ids.", "[]"
    "Width (*inputs:width*)", "``uint``", "Shape of the data", "0"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Legacy I Ds (*outputs:_legacyIDs*)", "``bool``", "If True, ids will be converted to strings for backwards compatibility", "True"
    "Buffer Size (*outputs:bufferSize*)", "``uint``", "Size (in bytes) of the buffer (0 if the input is a texture)", "None"
    "Cuda Device Index (*outputs:cudaDeviceIndex*)", "``int``", "Index of the device where the data lives (-1 for host data)", "-1"
    "Data Ptr (*outputs:dataPtr*)", "``uint64``", "Pointer to the raw data (host pointer)", "0"
    "Data Shape (*outputs:dataShape*)", "``int[]``", "Desired dimensions of output array", "None"
    "Data Type (*outputs:dataType*)", "``token``", "Defines the data type", "uint8"
    "Exec (*outputs:exec*)", "``execution``", "Trigger", "None"
    "Height (*outputs:height*)", "``uint``", "Shape of the data", "None"
    "Ids (*outputs:ids*)", "``uint[]``", "Unoccluded semantic u ids (or color, if `colorize` is set to True).", "None"
    "Labels (*outputs:labels*)", "``token[]``", "Prim path of the prim.", "None"
    "Strides (*outputs:strides*)", "``int[2]``", "Strides (in bytes).", "None"
    "Width (*outputs:width*)", "``uint``", "Shape of the data", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.replicator.core.SemanticSegmentation"
    "Version", "1"
    "Extension", "omni.replicator.core"
    "Has State?", "True"
    "Implementation Language", "Python"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "Categories", "Replicator:Annotators"
    "__categoryDescriptions", "Replicator:Annotators,Replicator annotator nodes."
    "Generated Class Name", "OgnSemanticSegmentationDatabase"
    "Python Module", "omni.replicator.core"

