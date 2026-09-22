.. _omni_replicator_core_BoundingBox3D_1:

.. _omni_replicator_core_BoundingBox3D:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Bounding Box 3D
    :keywords: lang-en omnigraph node Replicator:Annotators core bounding-box3-d


Bounding Box 3D
===============

.. <description>

This node outputs the 3D bounding box data.

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
    "Data Ptr (*inputs:dataPtr*)", "``uint64``", "Pointer to the raw bbox data (host pointer)", "0"
    "Exec (*inputs:exec*)", "``execution``", "Trigger", "None"
    "Filtered Bbox Info Ptr (*inputs:filteredBboxInfoPtr*)", "``uint64``", "Pointer to the raw bbox info data (host pointer)", "0"
    "Filtered Semantic Label Token Ptr (*inputs:filteredSemanticLabelTokenPtr*)", "``uint64``", "Array containing filtered semantics of numSemantics uint64_t representing the semantic label of the semantic prim", "0"
    "Min Semantic Index (*inputs:minSemanticIndex*)", "``uint``", "Semantic index of the first semantic prim in the semantic arrays", "0"
    "Num Semantics (*inputs:numSemantics*)", "``uint``", "Number of semantic prim in the semantic arrays", "0"
    "Prim Paths (*inputs:primPaths*)", "``token[]``", "Prim paths corresponding to each bounding box.", "[]"
    "Semantic Filter Name (*inputs:semanticFilterName*)", "``token``", "name of Semantic Filter to use", ""
    "Semantic Label Token Ptrs (*inputs:semanticLabelTokenPtrs*)", "``uint64[]``", "Array containing for every input semantic filters the corresponding array pointer of numSemantics uint64_t representing the semantic label of the semantic prim", "[]"
    "Semantic Map Ptr (*inputs:semanticMapPtr*)", "``uint64``", "Array pointer of numSemantics uint16_t containing the semantic index of the semantic prim first semantic prim parent", "0"
    "Semantic Occlusion Ptr (*inputs:semanticOcclusionPtr*)", "``uint64``", "Pointer to the raw occlusion data (host pointer)", "0"
    "Semantic Types (*inputs:semanticTypes*)", "``token[]``", "Semantic Types to consider", "[]"
    "Semantic World Transform Ptr (*inputs:semanticWorldTransformPtr*)", "``uint64``", "Array pointer of numSemantics 4x4 float matrices containing the transform from local to world space for every semantic entity", "0"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Bbox Ids (*outputs:bboxIds*)", "``uint[]``", "Identifier associated with bounding box, used to link different types of bounding boxes to the same (eg. 2D Tight and 3D)", "None"
    "Buffer Size (*outputs:bufferSize*)", "``uint``", "Size (in bytes) of the buffer (0 if the input is a texture)", "None"
    "Data (*outputs:data*)", "``uchar[]``", "Extent data of bounding box.", "None"
    "Exec (*outputs:exec*)", "``execution``", "Trigger", "None"
    "Height (*outputs:height*)", "``uint``", "Shape of the data", "None"
    "Ids (*outputs:ids*)", "``uint[]``", "Unoccluded semantic ids of the bounding box.", "None"
    "Labels (*outputs:labels*)", "``token[]``", "Semantic labels of the bounding box.", "None"
    "Prim Paths (*outputs:primPaths*)", "``token[]``", "Prim paths corresponding to each bounding box.", "None"
    "Width (*outputs:width*)", "``uint``", "Shape of the data", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.replicator.core.BoundingBox3D"
    "Version", "1"
    "Extension", "omni.replicator.core"
    "Has State?", "True"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Bounding Box 3D"
    "Categories", "Replicator:Annotators"
    "__categoryDescriptions", "Replicator:Annotators,Replicator annotator nodes."
    "Generated Class Name", "OgnBoundingBox3DDatabase"
    "Python Module", "omni.replicator.core"

