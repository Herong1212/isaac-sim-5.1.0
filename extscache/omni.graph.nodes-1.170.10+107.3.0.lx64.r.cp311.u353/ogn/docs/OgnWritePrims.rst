.. _omni_graph_nodes_WritePrims_1:

.. _omni_graph_nodes_WritePrims:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Write Prims (Legacy)
    :keywords: lang-en omnigraph node sceneGraph,bundle WriteOnly nodes write-prims


Write Prims (Legacy)
====================

.. <description>

DEPRECATED - use WritePrimsV2!

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.nodes<ext_omni_graph_nodes>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Attribute Name Pattern (*inputs:attrNamesToExport*)", "``string``", "A list of wildcard patterns used to match primitive attributes by name.  Supported syntax of wildcard pattern:     `*` - match an arbitrary number of any characters     `?` - match any single character     `^` - (caret) is used to define a pattern that is to be excluded  Example of wildcard patterns, input: ['xFormOp:translate', 'xformOp:scale','radius']     '*' - match any     'xformOp:*' - matches 'xFormOp:translate' and 'xformOp:scale'     '* ^radius' - match any, but exclude 'radius'     '* ^xformOp*' - match any, but exclude 'xFormOp:translate', 'xformOp:scale'", "*"
    "Exec In (*inputs:execIn*)", "``execution``", "Signal to the graph that this node is ready to be executed.", "None"
    "Prim Path Pattern (*inputs:pathPattern*)", "``string``", "A list of wildcard patterns used to match primitives by path.  Supported syntax of wildcard pattern:     `*` - match an arbitrary number of any characters     `?` - match any single character     `^` - (caret) is used to define a pattern that is to be excluded  Example of wildcard patterns, input: ['/Cube0', '/Cube1', '/Box']     '*' - match any     '* ^/Box' - match any, but exclude '/Box'     '* ^/Cube*' - match any, but exclude '/Cube0' and '/Cube1'", "*"
    "Prims Bundle (*inputs:primsBundle*)", "``bundle``", "The bundle(s) of multiple prims to be written back. The sourcePrimPath attribute is used to find the destination prim.", "None"
    "", "Metadata", "*allowMultiInputs* = 1", ""
    "Prim Type Pattern (*inputs:typePattern*)", "``string``", "A list of wildcard patterns used to match primitives by type.  Supported syntax of wildcard pattern:     `*` - match an arbitrary number of any characters     `?` - match any single character     `^` - (caret) is used to define a pattern that is to be excluded  Example of wildcard patterns, input: ['Mesh', 'Cone', 'Cube']     '*' - match any     '* ^Mesh' - match any, but exclude 'Mesh'     '* ^Cone ^Cube' - match any, but exclude 'Cone' and 'Cube'", "*"
    "Persist To USD (*inputs:usdWriteBack*)", "``bool``", "Whether or not the value should be written back to USD, or kept a Fabric only value", "False"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Exec Out (*outputs:execOut*)", "``execution``", "Signal to the graph that execution can continue downstream.", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.nodes.WritePrims"
    "Version", "1"
    "Extension", "omni.graph.nodes"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "hidden", "true"
    "uiName", "Write Prims (Legacy)"
    "Categories", "sceneGraph,bundle"
    "Generated Class Name", "OgnWritePrimsDatabase"
    "Python Module", "omni.graph.nodes"

