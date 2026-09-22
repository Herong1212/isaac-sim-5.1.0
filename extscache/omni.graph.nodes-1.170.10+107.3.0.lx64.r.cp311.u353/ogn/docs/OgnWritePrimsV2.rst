.. _omni_graph_nodes_WritePrimsV2_1:

.. _omni_graph_nodes_WritePrimsV2:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Write Prims
    :keywords: lang-en omnigraph node sceneGraph,bundle WriteOnly nodes write-prims-v2


Write Prims
===========

.. <description>

Write back bundle(s) containing multiple prims to the stage.

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
    "Layer Identifier (*inputs:layerIdentifier*)", "``token``", "Identifier of the USD layer to export data to. Identifier can be empty, ""<Session Layer>"", ""<Root Layer>"" or the identifier of a sublayer. If empty or invalid, data will be exported to the current layer. This is only used when ""Persist To USD"" is enabled.", ""
    "Prim Path Pattern (*inputs:pathPattern*)", "``string``", "A list of wildcard patterns used to match primitives by path.  Supported syntax of wildcard pattern:     `*` - match an arbitrary number of any characters     `?` - match any single character     `^` - (caret) is used to define a pattern that is to be excluded  Example of wildcard patterns, input: ['/Cube0', '/Cube1', '/Box']     '*' - match any     '* ^/Box' - match any, but exclude '/Box'     '* ^/Cube*' - match any, but exclude '/Cube0' and '/Cube1'", "*"
    "Prims (*inputs:prims*)", "``target``", "Target(s) to which the prims in 'primsBundle' will be written to. There is a 1:1 mapping between root prims paths in 'primsBundle' and the Target Prims targets *For advanced usage, if 'primsBundle' contains hierarchy, the unique common ancestor paths will have   the 1:1 mapping to Target Prims targets, with the descendant paths remapped. *NOTE* See 'scatterUnderTargets' input for modified exporting behavior *WARNING* this can create new prims on the stage. If attributes or prims are removed from 'primsBundle' in subsequent execution, they will be removed from targets as well.", "None"
    "", "Metadata", "*allowMultiInputs* = 1", ""
    "Prims Bundle (*inputs:primsBundle*)", "``bundle``", "The bundle(s) of multiple prims to be written back. The sourcePrimPath attribute is used to find the destination prim.", "None"
    "", "Metadata", "*allowMultiInputs* = 1", ""
    "Scatter Under Targets (*inputs:scatterUnderTargets*)", "``bool``", "If true, the target prims become the parent prims that the bundled prims will be exported *UNDER*.  If multiple prims targets are provided, the primsBundle will be duplicated *UNDER* each  target prims.", "False"
    "Prim Type Pattern (*inputs:typePattern*)", "``string``", "A list of wildcard patterns used to match primitives by type.  Supported syntax of wildcard pattern:     `*` - match an arbitrary number of any characters     `?` - match any single character     `^` - (caret) is used to define a pattern that is to be excluded  Example of wildcard patterns, input: ['Mesh', 'Cone', 'Cube']     '*' - match any     '* ^Mesh' - match any, but exclude 'Mesh'     '* ^Cone ^Cube' - match any, but exclude 'Cone' and 'Cube'", "*"
    "Persist To USD (*inputs:usdWriteBack*)", "``bool``", "Whether or not the value should be written back to USD, or kept a Fabric only value", "True"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Exec Out (*outputs:execOut*)", "``execution``", "Signal to the graph that execution can continue downstream.", "None"


State
-----
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Attr Names To Export (*state:attrNamesToExport*)", "``string``", "State from previous execution", "*"
    "Layer Identifier (*state:layerIdentifier*)", "``token``", "State from previous execution", ""
    "Path Pattern (*state:pathPattern*)", "``string``", "State from previous execution", "*"
    "Prim Bundle Dirty Id (*state:primBundleDirtyId*)", "``uint64``", "State from previous execution", "None"
    "Scatter Under Targets (*state:scatterUnderTargets*)", "``bool``", "State from previous execution", "False"
    "Type Pattern (*state:typePattern*)", "``string``", "State from previous execution", "*"
    "Usd Write Back (*state:usdWriteBack*)", "``bool``", "State from previous execution", "True"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.nodes.WritePrimsV2"
    "Version", "1"
    "Extension", "omni.graph.nodes"
    "Has State?", "True"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Write Prims"
    "Categories", "sceneGraph,bundle"
    "Generated Class Name", "OgnWritePrimsV2Database"
    "Python Module", "omni.graph.nodes"

