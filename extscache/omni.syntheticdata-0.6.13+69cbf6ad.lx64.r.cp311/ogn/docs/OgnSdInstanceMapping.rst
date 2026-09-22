.. _omni_syntheticdata_SdInstanceMapping_2:

.. _omni_syntheticdata_SdInstanceMapping:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Sd Instance Mapping
    :keywords: lang-en omnigraph node graph:action syntheticdata sd-instance-mapping


Sd Instance Mapping
===================

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

    "Exec (*inputs:exec*)", "``execution``", "Trigger", "None"
    "Lazy (*inputs:lazy*)", "``bool``", "Compute outputs only when connected to a downstream node", "True"
    "Render Results (*inputs:renderResults*)", "``uint64``", "Render results pointer", "0"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Received (*outputs:exec*)", "``execution``", "Executes when the event is received", "None"
    "Sd IM Instance Semantic Map (*outputs:sdIMInstanceSemanticMap*)", "``uchar[]``", "Raw array of uint16_t of size sdIMNumInstances*sdIMMaxSemanticHierarchyDepth containing the mapping from the instances index to their inherited semantic entities", "None"
    "Sd IM Instance Tokens (*outputs:sdIMInstanceTokens*)", "``token[]``", "Instance array containing the token for every instances", "None"
    "Sd IM Last Update Time Denominator (*outputs:sdIMLastUpdateTimeDenominator*)", "``uint64``", "Time denominator of the last time the data has changed", "None"
    "Sd IM Last Update Time Numerator (*outputs:sdIMLastUpdateTimeNumerator*)", "``int64``", "Time numerator of the last time the data has changed", "None"
    "Sd IM Max Semantic Hierarchy Depth (*outputs:sdIMMaxSemanticHierarchyDepth*)", "``uint``", "Maximal number of semantic entities inherited by an instance", "None"
    "Sd IM Min Instance Index (*outputs:sdIMMinInstanceIndex*)", "``uint``", "Instance id of the first instance in the instance arrays", "None"
    "Sd IM Min Semantic Index (*outputs:sdIMMinSemanticIndex*)", "``uint``", "Semantic id of the first semantic entity in the semantic arrays", "None"
    "Sd IM Num Instances (*outputs:sdIMNumInstances*)", "``uint``", "Number of instances in the instance arrays", "None"
    "Sd IM Num Semantic Tokens (*outputs:sdIMNumSemanticTokens*)", "``uint``", "Number of semantics token including the semantic entity path, the semantic entity types and if the number of semantic types is greater than one a ", "None"
    "Sd IM Num Semantics (*outputs:sdIMNumSemantics*)", "``uint``", "Number of semantic entities in the semantic arrays", "None"
    "Sd IM Semantic Local Transform (*outputs:sdIMSemanticLocalTransform*)", "``float[]``", "Semantic array of 4x4 float matrices containing the transform from world to local space for every semantic entity", "None"
    "Sd IM Semantic Token Map (*outputs:sdIMSemanticTokenMap*)", "``token[]``", "Semantic array of token of size numSemantics * numSemanticTypes containing the mapping from the semantic entities to the semantic entity path and semantic types", "None"
    "Sd IM Semantic World Transform (*outputs:sdIMSemanticWorldTransform*)", "``float[]``", "Semantic array of 4x4 float matrices containing the transform from local to world space for every semantic entity", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.syntheticdata.SdInstanceMapping"
    "Version", "2"
    "Extension", "omni.syntheticdata"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "__tokens", "[""InstanceMappingInfoSDhost"", ""InstanceMapSDhost"", ""SemanticLabelTokenSDhost"", ""InstancePrimTokenSDhost"", ""SemanticLocalTransformSDhost"", ""SemanticWorldTransformSDhost""]"
    "Categories", "graph:action"
    "Generated Class Name", "OgnSdInstanceMappingDatabase"
    "Python Module", "omni.syntheticdata"

