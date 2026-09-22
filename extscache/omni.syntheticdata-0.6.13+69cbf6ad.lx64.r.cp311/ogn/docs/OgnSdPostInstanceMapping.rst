.. _omni_syntheticdata_SdPostInstanceMapping_2:

.. _omni_syntheticdata_SdPostInstanceMapping:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Sd Post Instance Mapping
    :keywords: lang-en omnigraph node graph:postRender,rendering syntheticdata sd-post-instance-mapping


Sd Post Instance Mapping
========================

.. <description>

Synthetic Data node to compute and store scene instances semantic hierarchy information

.. </description>


Installation
------------

To use this node enable :ref:`omni.syntheticdata<ext_omni_syntheticdata>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Exec (*inputs:exec*)", "``execution``", "Trigger", "None"
    "gpuFoundations (*inputs:gpu*)", "``uint64``", "Pointer to shared context containing gpu foundations", "0"
    "renderProduct (*inputs:rp*)", "``uint64``", "Pointer to render product for this view", "0"
    "Semantic Filter Name (*inputs:semanticFilterName*)", "``token``", "Name of the semantic filter to apply to the semanticLabelToken", "default"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Exec (*outputs:exec*)", "``execution``", "Trigger", "None"
    "Instance Map SD Cuda Ptr (*outputs:instanceMapSDCudaPtr*)", "``uint64``", "cuda uint16_t buffer pointer of size numInstances containing the instance parent semantic index", "None"
    "Instance Mapping Info SD Ptr (*outputs:instanceMappingInfoSDPtr*)", "``uint64``", "uint buffer pointer containing the following information : [ numInstances, minInstanceId, numSemantics, minSemanticId, numProtoSemantic,   lastUpdateTimeNumeratorHigh, lastUpdateTimeNumeratorLow, , lastUpdateTimeDenominatorHigh, lastUpdateTimeDenominatorLow ]", "None"
    "Instance Prim Token SD Cuda Ptr (*outputs:instancePrimTokenSDCudaPtr*)", "``uint64``", "cuda uint64_t buffer pointer of size numInstances containing the instance path token", "None"
    "Last Update Time Denominator (*outputs:lastUpdateTimeDenominator*)", "``uint64``", "Time denominator of the last time the data has changed", "None"
    "Last Update Time Numerator (*outputs:lastUpdateTimeNumerator*)", "``int64``", "Time numerator of the last time the data has changed", "None"
    "Semantic Label Token SD Cuda Ptr (*outputs:semanticLabelTokenSDCudaPtr*)", "``uint64``", "cuda uint64_t buffer pointer of size numSemantics containing the semantic label token", "None"
    "Semantic Local Transform SD Cuda Ptr (*outputs:semanticLocalTransformSDCudaPtr*)", "``uint64``", "cuda float44 buffer pointer of size numSemantics containing the local semantic transform", "None"
    "Semantic Map SD Cuda Ptr (*outputs:semanticMapSDCudaPtr*)", "``uint64``", "cuda uint16_t buffer pointer of size numSemantics containing the semantic parent semantic index", "None"
    "Semantic Prim Token SD Cuda Ptr (*outputs:semanticPrimTokenSDCudaPtr*)", "``uint64``", "cuda uint32_t buffer pointer of size numSemantics containing the prim part of the semantic path token", "None"
    "Semantic World Transform SD Cuda Ptr (*outputs:semanticWorldTransformSDCudaPtr*)", "``uint64``", "cuda float44 buffer pointer of size numSemantics containing the world semantic transform", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.syntheticdata.SdPostInstanceMapping"
    "Version", "2"
    "Extension", "omni.syntheticdata"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "__tokens", "[""InstanceMappingInfoSDhost"", ""SemanticMapSD"", ""SemanticMapSDhost"", ""SemanticPrimTokenSD"", ""SemanticPrimTokenSDhost"", ""InstanceMapSD"", ""InstanceMapSDhost"", ""InstancePrimTokenSD"", ""InstancePrimTokenSDhost"", ""SemanticLabelTokenSD"", ""SemanticLabelTokenSDhost"", ""SemanticLocalTransformSD"", ""SemanticLocalTransformSDhost"", ""SemanticWorldTransformSD"", ""SemanticWorldTransformSDhost""]"
    "Categories", "graph:postRender,rendering"
    "Generated Class Name", "OgnSdPostInstanceMappingDatabase"
    "Python Module", "omni.syntheticdata"

