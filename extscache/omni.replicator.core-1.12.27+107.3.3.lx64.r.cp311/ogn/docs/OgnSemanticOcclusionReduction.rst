.. _omni_replicator_core_SemanticOcclusionReduction_1:

.. _omni_replicator_core_SemanticOcclusionReduction:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Semantic Occlusion Reduction
    :keywords: lang-en omnigraph node Replicator:Annotators core semantic-occlusion-reduction


Semantic Occlusion Reduction
============================

.. <description>

This node outputs mapping from semantic u id to occlusion value.

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
    "gpuFoundations (*inputs:gpu*)", "``uint64``", "Pointer to shared context containing gpu foundations", "0"
    "Instance Map SD Cuda Ptr (*inputs:instanceMapSDCudaPtr*)", "``uint64``", "cuda uint16_t buffer pointer of size numInstances containing the instance parent semantic index", "0"
    "Instance Mapping Info SD Ptr (*inputs:instanceMappingInfoSDPtr*)", "``uint64``", "uint buffer pointer containing the following information : [numInstances, minInstanceId, numSemantics, minSemanticId, numProtoSemantic]", "0"
    "renderProduct (*inputs:rp*)", "``uint64``", "Pointer to render product for this view", "0"
    "Semantic Map SD Cuda Ptr (*inputs:semanticMapSDCudaPtr*)", "``uint64``", "cuda uint16_t buffer pointer of size numSemantics containing the semantic parent semantic index", "0"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Exec (*outputs:exec*)", "``execution``", "Trigger", "None"
    "Semantic Num Children SD Cuda Ptr (*outputs:semanticNumChildrenSDCudaPtr*)", "``uint64``", "Cuda int buffer containing the number of children of each semantic entities (excluding itself).", "None"
    "Semantic Occlusion SD Cuda Ptr (*outputs:semanticOcclusionSDCudaPtr*)", "``uint64``", "Cuda float* buffer containing the occlusion ratio of each semantic entities", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.replicator.core.SemanticOcclusionReduction"
    "Version", "1"
    "Extension", "omni.replicator.core"
    "Has State?", "True"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "__tokens", "[""InstanceMapSD"", ""OcclusionSD"", ""SemanticOcclusionSD"", ""SemanticNumChildrenSD""]"
    "Categories", "Replicator:Annotators"
    "__categoryDescriptions", "Replicator:Annotators,Replicator annotator nodes."
    "Generated Class Name", "OgnSemanticOcclusionReductionDatabase"
    "Python Module", "omni.replicator.core"

