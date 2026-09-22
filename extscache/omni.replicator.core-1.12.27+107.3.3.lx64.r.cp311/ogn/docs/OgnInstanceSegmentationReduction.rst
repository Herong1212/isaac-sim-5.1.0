.. _omni_replicator_core_InstanceSegmentationReduction_1:

.. _omni_replicator_core_InstanceSegmentationReduction:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Instance Segmentation Reduction
    :keywords: lang-en omnigraph node Replicator:Annotators core instance-segmentation-reduction


Instance Segmentation Reduction
===============================

.. <description>

This node outputs reduced instance segmentation.

.. </description>


Installation
------------

To use this node enable :ref:`omni.replicator.core<ext_omni_replicator_core>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Colorize (*inputs:colorize*)", "``bool``", "If true, convert instance IDs into colors.", "False"
    "Exec (*inputs:exec*)", "``execution``", "Trigger", "None"
    "Filtered Semantic Label Token Cuda Ptr (*inputs:filteredSemanticLabelTokenCudaPtr*)", "``uint64``", "Array containing filtered semantics of numSemantics uint64_t representing the semantic label of the semantic prim", "0"
    "gpuFoundations (*inputs:gpu*)", "``uint64``", "Pointer to shared context containing gpu foundations", "0"
    "Instance Map SD Cuda Ptr (*inputs:instanceMapSDCudaPtr*)", "``uint64``", "cuda uint16_t buffer pointer of size numInstances containing the instance parent semantic index", "0"
    "Instance Mapping Info SD Ptr (*inputs:instanceMappingInfoSDPtr*)", "``uint64``", "uint buffer pointer containing the following information : [numInstances, minInstanceId, numSemantics, minSemanticId, numProtoSemantic]", "0"
    "Instance Prim Token SD Cuda Ptr (*inputs:instancePrimTokenSDCudaPtr*)", "``uint64``", "cuda uint64_t buffer pointer of size numInstances containing the instance path token", "0"
    "renderProduct (*inputs:rp*)", "``uint64``", "Pointer to render product for this view", "0"
    "Semantic Map SD Cuda Ptr (*inputs:semanticMapSDCudaPtr*)", "``uint64``", "cuda uint16_t buffer pointer of size numSemantics containing the semantic parent semantic index", "0"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Exec (*outputs:exec*)", "``execution``", "Trigger", "None"
    "Instance Segmentation Reduction SD Cuda Ptr (*outputs:instanceSegmentationReductionSDCudaPtr*)", "``uint64``", "Cuda buffer containing the reduced instance ids of the viewport.", "None"
    "Unique Instance Segmentation Ids SD Cuda Ptr (*outputs:uniqueInstanceSegmentationIdsSDCudaPtr*)", "``uint64``", "Cuda buffer containing the unique instance ids of the viewport.", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.replicator.core.InstanceSegmentationReduction"
    "Version", "1"
    "Extension", "omni.replicator.core"
    "Has State?", "True"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "__tokens", "[""InstanceSegmentationSD"", ""InstanceMapSD"", ""InstanceSegmentationReductionSD"", ""UniqueInstanceSegmentationIdsSD""]"
    "Categories", "Replicator:Annotators"
    "__categoryDescriptions", "Replicator:Annotators,Replicator annotator nodes."
    "Generated Class Name", "OgnInstanceSegmentationReductionDatabase"
    "Python Module", "omni.replicator.core"

