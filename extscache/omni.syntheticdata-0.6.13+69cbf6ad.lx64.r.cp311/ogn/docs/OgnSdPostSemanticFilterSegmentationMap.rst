.. _omni_syntheticdata_SdPostSemanticFilterSegmentationMap_1:

.. _omni_syntheticdata_SdPostSemanticFilterSegmentationMap:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Sd Post Semantic Filter Segmentation Map
    :keywords: lang-en omnigraph node graph:postRender syntheticdata sd-post-semantic-filter-segmentation-map


Sd Post Semantic Filter Segmentation Map
========================================

.. <description>

Synthetic Data node to create an texture AOV : the semantic segmentation map corresponding to an input semantic filter

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
    "Gpu (*inputs:gpu*)", "``uint64``", "Pointer to shared context containing gpu foundations", "0"
    "Instance Mapping Info SD Ptr (*inputs:instanceMappingInfoSDPtr*)", "``uint64``", "uint buffer pointer containing the following information : [numInstances, minInstanceId, numSemantics, minSemanticId, numProtoSemantic]", "0"
    "Render Product Resolution (*inputs:renderProductResolution*)", "``int[2]``", "RenderProduct resolution", "[0, 0]"
    "Rp (*inputs:rp*)", "``uint64``", "Render results", "0"
    "Semantic Filter Name (*inputs:semanticFilterName*)", "``token``", "Name of the semantic filter", ""
    "Semantic Label Token SD Cuda Ptr (*inputs:semanticLabelTokenSDCudaPtr*)", "``uint64``", "uint64_t cuda buffer pointer of size numSemantics containing the semantic label token", "0"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Received (*outputs:exec*)", "``execution``", "Executes for each newFrame event received", "None"
    "Semantic Filter Segmentation Map Cuda Ptr (*outputs:semanticFilterSegmentationMapCudaPtr*)", "``uint64``", "uint64_t cuda array containing the segmentation map associated to the input semantic filter", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.syntheticdata.SdPostSemanticFilterSegmentationMap"
    "Version", "1"
    "Extension", "omni.syntheticdata"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "__tokens", "[""InstanceMapSD"", ""InstanceSegmentationSD""]"
    "Categories", "graph:postRender"
    "Generated Class Name", "OgnSdPostSemanticFilterSegmentationMapDatabase"
    "Python Module", "omni.syntheticdata"

