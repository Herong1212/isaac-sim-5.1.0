.. _omni_syntheticdata_SdSemanticLabelsMap_1:

.. _omni_syntheticdata_SdSemanticLabelsMap:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Sd Semantic Labels Map
    :keywords: lang-en omnigraph node graph:postRender,graph:action syntheticdata sd-semantic-labels-map


Sd Semantic Labels Map
======================

.. <description>

Synthetic Data node to expose the semantic labels map of a given semantic filter

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
    "Gpu (*inputs:gpu*)", "``uint64``", "Pointer to shared context containing gpu foundations.", "0"
    "Render Product Path (*inputs:renderProductPath*)", "``token``", "RenderProduct prim path", ""
    "Render Results (*inputs:renderResults*)", "``uint64``", "Render results", "0"
    "Semantic Filter Name (*inputs:semanticFilterName*)", "``token``", "Name of the semantic filter to apply to the semanticLabelToken", ""


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Cuda Device Index (*outputs:cudaDeviceIndex*)", "``int``", "Cuda index of the device the cuda buffer is residing in", "-1"
    "Received (*outputs:exec*)", "``execution``", "Executes for each newFrame event received", "None"
    "Last Update Time Denominator (*outputs:lastUpdateTimeDenominator*)", "``uint64``", "Time denominator of the last time the data has changed", "None"
    "Last Update Time Numerator (*outputs:lastUpdateTimeNumerator*)", "``int64``", "Time numerator of the last time the data has changed", "None"
    "Min Semantic Index (*outputs:minSemanticIndex*)", "``uint``", "Lower semantic id. Semantics ids are in [minSemanticIndex, minSemanticIndex+numSemantic-1]", "None"
    "Num Semantics (*outputs:numSemantics*)", "``uint``", "Number of semantics in the scene", "None"
    "Semantic Filter Name (*outputs:semanticFilterName*)", "``token``", "Name of the semantic filter to apply to the semanticLabelToken", "None"
    "Semantic Label Token SD Cuda Ptr (*outputs:semanticLabelTokenSDCudaPtr*)", "``uint64``", "uint64_t cuda buffer pointer of size numSemantics containing the semantic label token", "None"
    "Semantic Label Token SD Host Ptr (*outputs:semanticLabelTokenSDHostPtr*)", "``uint64``", "uint64_t host buffer pointer of size numSemantics containing the semantic label token", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.syntheticdata.SdSemanticLabelsMap"
    "Version", "1"
    "Extension", "omni.syntheticdata"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "__tokens", "[""InstanceMappingInfoSDhost"", ""SemanticLabelTokenSD"", ""SemanticLabelTokenSDhost""]"
    "Categories", "graph:postRender,graph:action"
    "Generated Class Name", "OgnSdSemanticLabelsMapDatabase"
    "Python Module", "omni.syntheticdata"

