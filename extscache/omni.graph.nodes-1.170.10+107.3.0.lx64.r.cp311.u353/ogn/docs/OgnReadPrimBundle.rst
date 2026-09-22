.. _omni_graph_nodes_ReadPrimBundle_7:

.. _omni_graph_nodes_ReadPrimBundle:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Read Prim into Bundle
    :keywords: lang-en omnigraph node sceneGraph,bundle ReadOnly nodes read-prim-bundle


Read Prim into Bundle
=====================

.. <description>

DEPRECATED - use ReadPrims!

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
    "Prim (*inputs:prim*)", "``target``", "The prims to be read from when 'usePath' is false", "None"
    "Prim Path (*inputs:primPath*)", "``token``", "The paths of the prims to be read from when 'usePath' is true", ""
    "Time (*inputs:usdTimecode*)", "``timecode``", "The time at which to evaluate the transform of the USD prim. A value of ""NaN"" indicates that the default USD time stamp should be used", "NaN"
    "Use Path (*inputs:usePath*)", "``bool``", "When true, the 'primPath' attribute is used as the path to the prim being read, otherwise it will read the connection at the 'prim' attribute", "False"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Prim Bundle (*outputs:primBundle*)", "``bundle``", "A bundle containing multiple prims as children. Each child contains data attributes and two additional token attributes named sourcePrimPath and sourcePrimType which contain the path and the type of the Prim being read", "None"


State
-----
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Attr Names To Import (*state:attrNamesToImport*)", "``uint64``", "State from previous execution", "None"
    "Compute Bounding Box (*state:computeBoundingBox*)", "``bool``", "State from previous execution", "False"
    "Prim Path (*state:primPath*)", "``uint64``", "State from previous execution", "None"
    "Usd Timecode (*state:usdTimecode*)", "``timecode``", "State from previous execution", "NaN"
    "Use Path (*state:usePath*)", "``bool``", "State from previous execution", "False"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.nodes.ReadPrimBundle"
    "Version", "7"
    "Extension", "omni.graph.nodes"
    "Icon", "ogn/icons/omni.graph.nodes.ReadPrimBundle.svg"
    "Has State?", "True"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "hidden", "true"
    "uiName", "Read Prim into Bundle"
    "Categories", "sceneGraph,bundle"
    "Generated Class Name", "OgnReadPrimBundleDatabase"
    "Python Module", "omni.graph.nodes"

