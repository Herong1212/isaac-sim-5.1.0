.. _omni_syntheticdata_SdTestInstanceMapping_1:

.. _omni_syntheticdata_SdTestInstanceMapping:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Sd Test Instance Mapping
    :keywords: lang-en omnigraph node graph:simulation,graph:postRender,graph:action,internal:test syntheticdata sd-test-instance-mapping


Sd Test Instance Mapping
========================

.. <description>

Synthetic Data node to test the instance mapping pipeline

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
    "Instance Map Ptr (*inputs:instanceMapPtr*)", "``uint64``", "Array pointer of numInstances uint16_t containing the semantic index of the instance prim first semantic prim parent", "0"
    "Instance Prim Path Ptr (*inputs:instancePrimPathPtr*)", "``uint64``", "Array pointer of numInstances uint64_t containing the prim path tokens for every instance prims", "0"
    "Min Instance Index (*inputs:minInstanceIndex*)", "``uint``", "Instance index of the first instance prim in the instance arrays", "0"
    "Min Semantic Index (*inputs:minSemanticIndex*)", "``uint``", "Semantic index of the first semantic prim in the semantic arrays", "0"
    "Num Instances (*inputs:numInstances*)", "``uint``", "Number of instances prim in the instance arrays", "0"
    "Num Semantics (*inputs:numSemantics*)", "``uint``", "Number of semantic prim in the semantic arrays", "0"
    "Semantic Label Token Ptrs (*inputs:semanticLabelTokenPtrs*)", "``uint64[]``", "Array containing for every input semantic filters the corresponding array pointer of numSemantics uint64_t representing the semantic label of the semantic prim", "[]"
    "Semantic Local Transform Ptr (*inputs:semanticLocalTransformPtr*)", "``uint64``", "Array pointer of numSemantics 4x4 float matrices containing the transform from world to object space for every semantic prims", "0"
    "Semantic Map Ptr (*inputs:semanticMapPtr*)", "``uint64``", "Array pointer of numSemantics uint16_t containing the semantic index of the semantic prim first semantic prim parent", "0"
    "Semantic Prim Path Ptr (*inputs:semanticPrimPathPtr*)", "``uint64``", "Array pointer of numSemantics uint32_t containing the prim part of the prim path tokens for every semantic prims", "0"
    "Semantic World Transform Ptr (*inputs:semanticWorldTransformPtr*)", "``uint64``", "Array pointer of numSemantics 4x4 float matrices containing the transform from local to world space for every semantic entity", "0"
    "Stage (*inputs:stage*)", "``token``", "Stage in {simulation, postrender, ondemand}", ""
    "Swh Frame Number (*inputs:swhFrameNumber*)", "``uint64``", "Fabric frame number", "0"
    "Test Case Index (*inputs:testCaseIndex*)", "``int``", "Test case index", "-1"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Received (*outputs:exec*)", "``execution``", "Executes when the event is received", "None"
    "Semantic Filter Predicate (*outputs:semanticFilterPredicate*)", "``token``", "The semantic filter predicate : a disjunctive normal form of semantic type and label", "None"
    "Success (*outputs:success*)", "``bool``", "Test value : false if failed", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.syntheticdata.SdTestInstanceMapping"
    "Version", "1"
    "Extension", "omni.syntheticdata"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "__tokens", "[""simulation"", ""postRender"", ""onDemand""]"
    "Categories", "graph:simulation,graph:postRender,graph:action,internal:test"
    "Generated Class Name", "OgnSdTestInstanceMappingDatabase"
    "Python Module", "omni.syntheticdata"

