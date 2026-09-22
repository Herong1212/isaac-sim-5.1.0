.. _omni_replicator_core_InstanceSegmentation_1:

.. _omni_replicator_core_InstanceSegmentation:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Instance Segmentation
    :keywords: lang-en omnigraph node Replicator:Annotators compute-on-request core instance-segmentation


Instance Segmentation
=====================

.. <description>

This node outputs instance segmentation.

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
    "Data Ptr (*inputs:dataPtr*)", "``uint64``", "Pointer to the raw instance segmentation reduction data. (host pointer)", "0"
    "Exec (*inputs:exec*)", "``execution``", "Trigger", "None"
    "Filtered Semantic Label Token Ptr (*inputs:filteredSemanticLabelTokenPtr*)", "``uint64``", "Array containing filtered semantics of numSemantics uint64_t representing the semantic label of the semantic prim", "0"
    "Height (*inputs:height*)", "``uint``", "Height", "0"
    "Instance Map Ptr (*inputs:instanceMapPtr*)", "``uint64``", "Array pointer of numInstances uint16_t containing the semantic index of the instance prim first semantic prim parent", "0"
    "Min Instance Index (*inputs:minInstanceIndex*)", "``uint``", "Instance id of the first instance in the instance arrays", "0"
    "Min Semantic Index (*inputs:minSemanticIndex*)", "``uint``", "Semantic id of the first instance in the instance arrays", "0"
    "Num Instances (*inputs:numInstances*)", "``uint``", "Number of instances in the instance arrays", "0"
    "Num Semantics (*inputs:numSemantics*)", "``uint``", "Number of semantic entities in the semantic arrays", "0"
    "Semantic Filter Name (*inputs:semanticFilterName*)", "``token``", "name of Semantic Filter to use", ""
    "Semantic Label Token Ptrs (*inputs:semanticLabelTokenPtrs*)", "``uint64[]``", "Array containing for every input semantic filters the corresponding array pointer of numSemantics uint64_t representing the semantic label of the semantic prim", "[]"
    "Semantic Map Ptr (*inputs:semanticMapPtr*)", "``uint64``", "Array pointer of numSemantics uint16_t containing the semantic index of the semantic prim first semantic prim parent", "0"
    "Semantic Prim Path Ptr (*inputs:semanticPrimPathPtr*)", "``uint64``", "Array pointer of numSemantics uint32_t containing the prim part of the prim path tokens for every semantic prims", "0"
    "Semantic Types (*inputs:semanticTypes*)", "``token[]``", "Semantic Types to consider", "['class']"
    "Strides (*inputs:strides*)", "``int[2]``", "Strides (in bytes) for instance segmentation.", "[0, 0]"
    "Unique Instance Segmentation Ids S Dhost Ptr (*inputs:uniqueInstanceSegmentationIdsSDhostPtr*)", "``uint64``", "Pointer to the raw unique instance segmentation ids data. (host pointer)", "0"
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
    "Ids (*outputs:ids*)", "``uint[]``", "Unoccluded semantic u ids (or color, if `colorize` is set to True).", "None"
    "Labels (*outputs:labels*)", "``token[]``", "Prim path of the prim.", "None"
    "Semantics (*outputs:semantics*)", "``token[]``", "Semantic labels that correspeond to the ids.", "None"
    "Strides (*outputs:strides*)", "``int[2]``", "Strides (in bytes) for instance segmentation.", "None"
    "Width (*outputs:width*)", "``uint``", "Shape of the data", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.replicator.core.InstanceSegmentation"
    "Version", "1"
    "Extension", "omni.replicator.core"
    "Has State?", "True"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "Categories", "Replicator:Annotators"
    "__categoryDescriptions", "Replicator:Annotators,Replicator annotator nodes."
    "Generated Class Name", "OgnInstanceSegmentationDatabase"
    "Python Module", "omni.replicator.core"

