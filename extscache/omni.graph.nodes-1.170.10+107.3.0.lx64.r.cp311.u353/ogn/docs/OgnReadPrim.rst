.. _omni_graph_nodes_ReadPrim_9:

.. _omni_graph_nodes_ReadPrim:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Read Prim
    :keywords: lang-en omnigraph node sceneGraph,bundle ReadOnly nodes read-prim


Read Prim
=========

.. <description>

DEPRECATED - use ReadPrimAttributes!

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.nodes<ext_omni_graph_nodes>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Attributes To Import (*inputs:attrNamesToImport*)", "``token``", "A list of wildcard patterns used to match the attribute names that are to be imported  Supported syntax of wildcard pattern:     '*' - match an arbitrary number of any characters     '?' - match any single character     '^' - (caret) is used to define a pattern that is to be excluded  Example of wildcard patterns, input: ['points', 'faceVertexCount', 'faceVertexIndices', 'size']     '*' - match any     '* ^points' - match any, but exclude 'points'     '* ^face*' - match any, but exclude 'faceVertexCount' and 'faceVertexIndices'", "*"
    "Compute Bounding Box (*inputs:computeBoundingBox*)", "``bool``", "For each primitive compute local bounding box and store them as 'bboxMinCorner', 'bboxMaxCorner' and 'bboxTransform' attributes.", "False"
    "Prim (*inputs:prim*)", "``bundle``", "The prims to be read from when 'usePathPattern' is false", "None"
    "Time (*inputs:usdTimecode*)", "``timecode``", "The time at which to evaluate the transform of the USD prim. A value of ""NaN"" indicates that the default USD time stamp should be used", "NaN"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Prim Bundle (*outputs:primBundle*)", "``bundle``", "A bundle of the target Prim attributes. In addition to the data attributes, there is a token attribute named sourcePrimPath which contains the path of the Prim being read", "None"


State
-----
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Attr Names To Import (*state:attrNamesToImport*)", "``uint64``", "State from previous execution", "None"
    "Compute Bounding Box (*state:computeBoundingBox*)", "``bool``", "State from previous execution", "False"
    "Prim Path (*state:primPath*)", "``uint64``", "State from previous execution", "None"
    "Prim Types (*state:primTypes*)", "``uint64``", "State from previous execution", "None"
    "Usd Timecode (*state:usdTimecode*)", "``timecode``", "State from previous execution", "NaN"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.nodes.ReadPrim"
    "Version", "9"
    "Extension", "omni.graph.nodes"
    "Has State?", "True"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "hidden", "true"
    "uiName", "Read Prim"
    "Categories", "sceneGraph,bundle"
    "Generated Class Name", "OgnReadPrimDatabase"
    "Python Module", "omni.graph.nodes"

