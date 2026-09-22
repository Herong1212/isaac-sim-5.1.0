.. _omni_graph_nodes_ReadPrimsV2_1:

.. _omni_graph_nodes_ReadPrimsV2:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Read Prims
    :keywords: lang-en omnigraph node sceneGraph,bundle ReadOnly nodes read-prims-v2


Read Prims
==========

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

    "Debug Stamp (*inputs:_debugStamp*)", "``int``", "For internal testing only, and subject to change. Please do not depend on this attribute! When not zero, this _debugStamp attribute will be copied to root and child bundles that change When a full update is performed, the negative _debugStamp is written. When only derived attributes (like bounding boxes and world matrices) are updated, _debugStamp + 1000000 is written", "0"
    "", "Metadata", "*literalOnly* = 1", ""
    "", "Metadata", "*hidden* = true", ""
    "Apply Skel Binding (*inputs:applySkelBinding*)", "``bool``", "If an input USD prim is skinnable and has the SkelBindingAPI schema applied, read skeletal data and apply SkelBinding to deform the prim. The output bundle will have additional child bundles created to hold data for the skeleton and skel animation prims if present. After execution, deformed points and normals will be written to the `points` and `normals` attributes, while non-deformed points and normals will be copied to the `points:default` and `normals:default` attributes.", "False"
    "Attribute Name Pattern (*inputs:attrNamesToImport*)", "``string``", "A list of wildcard patterns used to match the attribute names that are to be imported  Supported syntax of wildcard pattern:     '*' - match an arbitrary number of any characters     '?' - match any single character     '^' - (caret) is used to define a pattern that is to be excluded  Example of wildcard patterns, input: ['points', 'faceVertexCount', 'faceVertexIndices', 'size']     '*' - match any     '* ^points' - match any, but exclude 'points'     '* ^face*' - match any, but exclude 'faceVertexCount' and 'faceVertexIndices'", "*"
    "Compute Bounding Box (*inputs:computeBoundingBox*)", "``bool``", "For each primitive compute local bounding box and store them as 'bboxMinCorner', 'bboxMaxCorner' and 'bboxTransform' attributes.", "False"
    "Bundle change tracking (*inputs:enableBundleChangeTracking*)", "``bool``", "Enable change tracking for output bundle, its children and attributes. The change tracking system for bundles has some overhead, but enables users to inspect the changes that occurred in a bundle. Through inspecting the type of changes user can mitigate excessive computations.", "False"
    "USD change tracking (*inputs:enableChangeTracking*)", "``bool``", "Should the output bundles only be updated when the associated USD prims change? This uses a USD notice handler, and has a small overhead, so if you know that the imported USD prims will change frequently, you might want to disable this.", "True"
    "Prim Path Pattern (*inputs:pathPattern*)", "``string``", "A list of wildcard patterns used to match the prim paths that are to be imported  Supported syntax of wildcard pattern:     '*' - match an arbitrary number of any characters     '?' - match any single character     '^' - (caret) is used to define a pattern that is to be excluded  Example of wildcard patterns, input: ['/Cube0', '/Cube1', '/Box']     '*' - match any     '* ^/Box' - match any, but exclude '/Box'     '* ^/Cube*' - match any, but exclude '/Cube0' and '/Cube1'", ""
    "Prims (*inputs:prims*)", "``target``", "The root prim(s) that pattern matching uses to search from. If 'pathPattern' input is empty, the directly connected prims will be read. Otherwise, all the subtree (including root) will be tested against pattern matcher inputs, and the matched prims will be read into the output bundle. If no prims are connected, and 'pathPattern' is none empty, absolute root ""/"" will be searched as root prim.", "None"
    "", "Metadata", "*allowMultiInputs* = 1", ""
    "Prim Type Pattern (*inputs:typePattern*)", "``string``", "A list of wildcard patterns used to match the prim types that are to be imported  Supported syntax of wildcard pattern:     '*' - match an arbitrary number of any characters     '?' - match any single character     '^' - (caret) is used to define a pattern that is to be excluded  Example of wildcard patterns, input: ['Mesh', 'Cone', 'Cube']     '*' - match any     '* ^Mesh' - match any, but exclude 'Mesh'     '* ^Cone ^Cube' - match any, but exclude 'Cone' and 'Cube'", "*"
    "Time (*inputs:usdTimecode*)", "``timecode``", "The time at which to evaluate the transform of the USD prim. A value of ""NaN"" indicates that the default USD time stamp should be used", "NaN"


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
    "Enable Bundle Change Tracking (*state:enableBundleChangeTracking*)", "``bool``", "State from previous execution", "False"
    "Enable Change Tracking (*state:enableChangeTracking*)", "``bool``", "State from previous execution", "False"
    "Path Pattern (*state:pathPattern*)", "``string``", "State from previous execution", "None"
    "Type Pattern (*state:typePattern*)", "``string``", "State from previous execution", "None"
    "Usd Timecode (*state:usdTimecode*)", "``timecode``", "State from previous execution", "-1"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.nodes.ReadPrimsV2"
    "Version", "1"
    "Extension", "omni.graph.nodes"
    "Has State?", "True"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Read Prims"
    "Categories", "sceneGraph,bundle"
    "Generated Class Name", "OgnReadPrimsV2Database"
    "Python Module", "omni.graph.nodes"

