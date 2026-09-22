.. _omni_replicator_core_BoundingBoxLegacy_1:

.. _omni_replicator_core_BoundingBoxLegacy:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Bounding Box Legacy
    :keywords: lang-en omnigraph node Replicator:Annotators core bounding-box-legacy


Bounding Box Legacy
===================

.. <description>

This node outputs the legacy bounding box data output

.. </description>


Installation
------------

To use this node enable :ref:`omni.replicator.core<ext_omni_replicator_core>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Bbox Ids (*inputs:bboxIds*)", "``uint[]``", "Identifier associated with bounding box, used to link different types of bounding boxes to the same (eg. 2D Tight and 3D)", "[]"
    "Buffer Size (*inputs:bufferSize*)", "``uint``", "Size (in bytes) of the buffer (0 if the input is a texture)", "0"
    "Data (*inputs:data*)", "``uchar[]``", "Extent data of bounding box.", "[]"
    "Exec (*inputs:exec*)", "``execution``", "Trigger", "None"
    "Height (*inputs:height*)", "``uint``", "Shape of the data", "0"
    "Ids (*inputs:ids*)", "``uint[]``", "Unoccluded semantic ids of the bounding box.", "[]"
    "Labels (*inputs:labels*)", "``token[]``", "Semantic labels of the bounding box.", "[]"
    "Prim Paths (*inputs:primPaths*)", "``token[]``", "Prim paths corresponding to each bounding box.", "[]"
    "Semantic Filter Name (*inputs:semanticFilterName*)", "``token``", "name of Semantic Filter to use", ""
    "Semantic Types (*inputs:semanticTypes*)", "``token[]``", "Legacy attribute, ignored", "['class']"
    "Width (*inputs:width*)", "``uint``", "Shape of the data", "0"


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
    "Id To Labels (*outputs:idToLabels*)", "``string``", "Mapping from id to semantic labels.", "None"
    "Prim Paths (*outputs:primPaths*)", "``token[]``", "Prim paths corresponding to each bounding box.", "None"
    "Width (*outputs:width*)", "``uint``", "Shape of the data", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.replicator.core.BoundingBoxLegacy"
    "Version", "1"
    "Extension", "omni.replicator.core"
    "Has State?", "True"
    "Implementation Language", "Python"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "Categories", "Replicator:Annotators"
    "__categoryDescriptions", "Replicator:Annotators,Replicator annotator nodes."
    "Generated Class Name", "OgnBoundingBoxLegacyDatabase"
    "Python Module", "omni.replicator.core"

