.. _omni_graph_nodes_ReadPrimAttributes_3:

.. _omni_graph_nodes_ReadPrimAttributes:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Read Prim Attributes
    :keywords: lang-en omnigraph node sceneGraph,bundle ReadOnly nodes read-prim-attributes


Read Prim Attributes
====================

.. <description>

Read Prim attributes and exposes them as dynamic attributes. Produces an output bundle.

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.nodes<ext_omni_graph_nodes>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Attribute Name Pattern (*inputs:attrNamesToImport*)", "``string``", "A list of wildcard patterns used to match the attribute names that are to be imported  Supported syntax of wildcard pattern:     '*' - match an arbitrary number of any characters     '?' - match any single character     '^' - (caret) is used to define a pattern that is to be excluded  Example of wildcard patterns, input: ['points', 'faceVertexCount', 'faceVertexIndices', 'size']     '*' - match any     '* ^points' - match any, but exclude 'points'     '* ^face*' - match any, but exclude 'faceVertexCount' and 'faceVertexIndices'", "*"
    "Prim (*inputs:prim*)", "``target``", "The prim to be read from when 'usePath' is false", "None"
    "Prim Path (*inputs:primPath*)", "``path``", "The path of the prim to be read from when 'usePath' is true", ""
    "Time (*inputs:usdTimecode*)", "``timecode``", "The time at which to evaluate the transform of the USD prim. A value of ""NaN"" indicates that the default USD time stamp should be used", "NaN"
    "Use Path (*inputs:usePath*)", "``bool``", "When true, the 'primPath' attribute is used as the path to the prim being read, otherwise it will read the connection at the 'prim' attribute", "False"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Prim Bundle (*outputs:primBundle*)", "``bundle``", "A bundle of the target Prim attributes. In addition to the data attributes, there are token attributes named sourcePrimPath and sourcePrimType which contains the path of the Prim being read", "None"
    "", "Metadata", "*hidden* = true", ""
    "", "Metadata", "*literalOnly* = 1", ""


State
-----
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Attr Names To Import (*state:attrNamesToImport*)", "``string``", "State from previous execution", "None"
    "Prim Path (*state:primPath*)", "``uint64``", "State from previous execution", "None"
    "Usd Timecode (*state:usdTimecode*)", "``timecode``", "State from previous execution", "NaN"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.nodes.ReadPrimAttributes"
    "Version", "3"
    "Extension", "omni.graph.nodes"
    "Has State?", "True"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Read Prim Attributes"
    "Categories", "sceneGraph,bundle"
    "Generated Class Name", "OgnReadPrimAttributesDatabase"
    "Python Module", "omni.graph.nodes"

