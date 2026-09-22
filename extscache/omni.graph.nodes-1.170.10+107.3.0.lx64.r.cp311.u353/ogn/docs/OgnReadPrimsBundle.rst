.. _omni_graph_nodes_ReadPrimsBundle_3:

.. _omni_graph_nodes_ReadPrimsBundle:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Read Prims into Bundle
    :keywords: lang-en omnigraph node sceneGraph,bundle ReadOnly nodes read-prims-bundle


Read Prims into Bundle
======================

.. <description>

Reads primitives and outputs multiple primitive in a bundle.

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.nodes<ext_omni_graph_nodes>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Attributes To Import (*inputs:attrNamesToImport*)", "``string``", "A list of wildcard patterns used to match the attribute names that are to be imported  Supported syntax of wildcard pattern:     '*' - match an arbitrary number of any characters     '?' - match any single character     '^' - (caret) is used to define a pattern that is to be excluded  Example of wildcard patterns, input: ['points', 'faceVertexCount', 'faceVertexIndices', 'size']     '*' - match any     '* ^points' - match any, but exclude 'points'     '* ^face*' - match any, but exclude 'faceVertexCount' and 'faceVertexIndices'", "*"
    "Prim Paths (*inputs:primPaths*)", "``['path', 'token', 'token[]']``", "The paths of the prims to be read from when 'usePaths' is true", "None"
    "Prims (*inputs:prims*)", "``target``", "The prims to be read from when 'usePaths' is false", "None"
    "", "Metadata", "*allowMultiInputs* = 1", ""
    "Time (*inputs:usdTimecode*)", "``timecode``", "The time at which to evaluate the transform of the USD prim. A value of ""NaN"" indicates that the default USD time stamp should be used", "NaN"
    "Use Paths (*inputs:usePaths*)", "``bool``", "When true, the 'primPaths' attribute is used as the path to the prim being read, otherwise it will read the connection at the 'prim' attribute", "False"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Prims Bundle (*outputs:primsBundle*)", "``bundle``", "An output bundle containing multiple prims as children. Each child contains data attributes and two additional token attributes named sourcePrimPath and sourcePrimType which contain the path and the type of the Prim being read", "None"


State
-----
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Attr Names To Import (*state:attrNamesToImport*)", "``string``", "State from previous execution", "None"
    "Prim Paths (*state:primPaths*)", "``uint64[]``", "State from previous execution", "None"
    "Usd Timecode (*state:usdTimecode*)", "``timecode``", "State from previous execution", "NaN"
    "Use Paths (*state:usePaths*)", "``bool``", "State from previous execution", "False"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.nodes.ReadPrimsBundle"
    "Version", "3"
    "Extension", "omni.graph.nodes"
    "Has State?", "True"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "hidden", "true"
    "uiName", "Read Prims into Bundle"
    "Categories", "sceneGraph,bundle"
    "Generated Class Name", "OgnReadPrimsBundleDatabase"
    "Python Module", "omni.graph.nodes"

