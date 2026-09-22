.. _omni_syntheticdata_SdInstanceMappingPtr_2:

.. _omni_syntheticdata_SdInstanceMappingPtr:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Sd Instance Mapping Ptr
    :keywords: lang-en omnigraph node graph:action syntheticdata sd-instance-mapping-ptr


Sd Instance Mapping Ptr
=======================

.. <description>

Synthetic Data node to expose the scene instances semantic hierarchy information

.. </description>


Installation
------------

To use this node enable :ref:`omni.syntheticdata<ext_omni_syntheticdata>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Cuda Ptr (*inputs:cudaPtr*)", "``bool``", "If true, return cuda device pointer instead of host pointer", "False"
    "Exec (*inputs:exec*)", "``execution``", "Trigger", "None"
    "Render Results (*inputs:renderResults*)", "``uint64``", "Render results pointer", "0"
    "Semantic Filer Tokens (*inputs:semanticFilerTokens*)", "``token[]``", "Tokens identifying the semantic filters applied to the output semantic labels. Each token should correspond to an activated SdSemanticFilter node", "[]"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Cuda Device Index (*outputs:cudaDeviceIndex*)", "``int``", "If the data is on the device it is the cuda index of this device otherwise it is set to -1", "-1"
    "Received (*outputs:exec*)", "``execution``", "Executes when the event is received", "None"
    "Instance Map Ptr (*outputs:instanceMapPtr*)", "``uint64``", "Array pointer of numInstances uint16_t containing the semantic index of the instance prim first semantic prim parent", "None"
    "Instance Prim Path Ptr (*outputs:instancePrimPathPtr*)", "``uint64``", "Array pointer of numInstances uint64_t containing the prim path tokens for every instance prims", "None"
    "Last Update Time Denominator (*outputs:lastUpdateTimeDenominator*)", "``uint64``", "Time denominator of the last time the data has changed", "None"
    "Last Update Time Numerator (*outputs:lastUpdateTimeNumerator*)", "``int64``", "Time numerator of the last time the data has changed", "None"
    "Min Instance Index (*outputs:minInstanceIndex*)", "``uint``", "Instance index of the first instance prim in the instance arrays", "None"
    "Min Semantic Index (*outputs:minSemanticIndex*)", "``uint``", "Semantic index of the first semantic prim in the semantic arrays", "None"
    "Num Instances (*outputs:numInstances*)", "``uint``", "Number of instances prim in the instance arrays", "None"
    "Num Semantics (*outputs:numSemantics*)", "``uint``", "Number of semantic prim in the semantic arrays", "None"
    "Semantic Label Token Ptrs (*outputs:semanticLabelTokenPtrs*)", "``uint64[]``", "Array containing for every input semantic filters the corresponding array pointer of numSemantics uint64_t representing the semantic label of the semantic prim", "None"
    "Semantic Local Transform Ptr (*outputs:semanticLocalTransformPtr*)", "``uint64``", "Array pointer of numSemantics 4x4 float matrices containing the transform from world to object space for every semantic prims", "None"
    "Semantic Map Ptr (*outputs:semanticMapPtr*)", "``uint64``", "Array pointer of numSemantics uint16_t containing the semantic index of the semantic prim first semantic prim parent", "None"
    "Semantic Prim Path Ptr (*outputs:semanticPrimPathPtr*)", "``uint64``", "Array pointer of numSemantics uint32_t containing the prim part of the prim path tokens for every semantic prims", "None"
    "Semantic World Transform Ptr (*outputs:semanticWorldTransformPtr*)", "``uint64``", "Array pointer of numSemantics 4x4 float matrices containing the transform from local to world space for every semantic entity", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.syntheticdata.SdInstanceMappingPtr"
    "Version", "2"
    "Extension", "omni.syntheticdata"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "__tokens", "[""InstanceMappingInfoSDhost"", ""InstancePrimTokenSDhost"", ""InstancePrimTokenSD"", ""SemanticPrimTokenSDhost"", ""SemanticPrimTokenSD"", ""InstanceMapSDhost"", ""InstanceMapSD"", ""SemanticMapSDhost"", ""SemanticMapSD"", ""SemanticWorldTransformSDhost"", ""SemanticWorldTransformSD"", ""SemanticLocalTransformSDhost"", ""SemanticLocalTransformSD"", ""SemanticLabelTokenSDhost"", ""SemanticLabelTokenSD""]"
    "Categories", "graph:action"
    "Generated Class Name", "OgnSdInstanceMappingPtrDatabase"
    "Python Module", "omni.syntheticdata"

