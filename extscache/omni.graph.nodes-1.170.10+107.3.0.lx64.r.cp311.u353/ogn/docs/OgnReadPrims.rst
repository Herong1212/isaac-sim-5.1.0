.. _omni_graph_nodes_ReadPrims_3:

.. _omni_graph_nodes_ReadPrims:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Read Prims (Legacy)
    :keywords: lang-en omnigraph node sceneGraph,bundle ReadOnly nodes read-prims


Read Prims (Legacy)
===================

.. <description>

DEPRECATED - use ReadPrimsV2!

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.nodes<ext_omni_graph_nodes>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Apply Skel Binding (*inputs:applySkelBinding*)", "``bool``", "If an input USD prim is skinnable and has the SkelBindingAPI schema applied, read skeletal data and apply SkelBinding to deform the prim. The output bundle will have additional child bundles created to hold data for the skeleton and skel animation prims if present. After execution, deformed points and normals will be written to the `points` and `normals` attributes, while non-deformed points and normals will be copied to the `points:default` and `normals:default` attributes.", "False"
    "Attribute Name Pattern (*inputs:attrNamesToImport*)", "``string``", "A list of wildcard patterns used to match the attribute names that are to be imported  Supported syntax of wildcard pattern:     '*' - match an arbitrary number of any characters     '?' - match any single character     '^' - (caret) is used to define a pattern that is to be excluded  Example of wildcard patterns, input: ['points', 'faceVertexCount', 'faceVertexIndices', 'size']     '*' - match any     '* ^points' - match any, but exclude 'points'     '* ^face*' - match any, but exclude 'faceVertexCount' and 'faceVertexIndices'", "*"
    "Compute Bounding Box (*inputs:computeBoundingBox*)", "``bool``", "For each primitive compute local bounding box and store them as 'bboxMinCorner', 'bboxMaxCorner' and 'bboxTransform' attributes.", "False"
    "Prim Path Pattern (*inputs:pathPattern*)", "``string``", "A list of wildcard patterns used to match the prim paths that are to be imported  Supported syntax of wildcard pattern:     '*' - match an arbitrary number of any characters     '?' - match any single character     '^' - (caret) is used to define a pattern that is to be excluded  Example of wildcard patterns, input: ['/Cube0', '/Cube1', '/Box']     '*' - match any     '* ^/Box' - match any, but exclude '/Box'     '* ^/Cube*' - match any, but exclude '/Cube0' and '/Cube1'", ""
    "Prims (*inputs:prims*)", "``target``", "The prims to be read from when 'useFindPrims' is false", "None"
    "", "Metadata", "*allowMultiInputs* = 1", ""
    "Prim Type Pattern (*inputs:typePattern*)", "``string``", "A list of wildcard patterns used to match the prim types that are to be imported  Supported syntax of wildcard pattern:     '*' - match an arbitrary number of any characters     '?' - match any single character     '^' - (caret) is used to define a pattern that is to be excluded  Example of wildcard patterns, input: ['Mesh', 'Cone', 'Cube']     '*' - match any     '* ^Mesh' - match any, but exclude 'Mesh'     '* ^Cone ^Cube' - match any, but exclude 'Cone' and 'Cube'", "*"
    "Time (*inputs:usdTimecode*)", "``timecode``", "The time at which to evaluate the transform of the USD prim. A value of ""NaN"" indicates that the default USD time stamp should be used", "NaN"
    "Use Find Prims (*inputs:useFindPrims*)", "``bool``", "When true, the 'pathPattern' and 'typePattern' attribute is used as the pattern to search for the prims to read otherwise it will read the connection at the 'prim' attribute.", "False"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Prims Bundle (*outputs:primsBundle*)", "``bundle``", "An output bundle containing multiple prims as children. Each child contains data attributes and two additional token attributes named sourcePrimPath and sourcePrimType which contains the path of the Prim being read", "None"


State
-----
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Apply Skel Binding (*state:applySkelBinding*)", "``bool``", "State from previous execution", "False"
    "Attr Names To Import (*state:attrNamesToImport*)", "``string``", "State from previous execution", "None"
    "Compute Bounding Box (*state:computeBoundingBox*)", "``bool``", "State from previous execution", "False"
    "Path Pattern (*state:pathPattern*)", "``string``", "State from previous execution", "None"
    "Prim Paths (*state:primPaths*)", "``uint64[]``", "State from previous execution", "None"
    "Type Pattern (*state:typePattern*)", "``string``", "State from previous execution", "None"
    "Usd Timecode (*state:usdTimecode*)", "``timecode``", "State from previous execution", "-1"
    "Use Find Prims (*state:useFindPrims*)", "``bool``", "State from previous execution", "False"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.nodes.ReadPrims"
    "Version", "3"
    "Extension", "omni.graph.nodes"
    "Has State?", "True"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "hidden", "true"
    "uiName", "Read Prims (Legacy)"
    "Categories", "sceneGraph,bundle"
    "Generated Class Name", "OgnReadPrimsDatabase"
    "Python Module", "omni.graph.nodes"

