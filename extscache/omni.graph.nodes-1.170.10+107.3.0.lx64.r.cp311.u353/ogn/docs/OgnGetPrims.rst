.. _omni_graph_nodes_GetPrims_2:

.. _omni_graph_nodes_GetPrims:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Get Prims
    :keywords: lang-en omnigraph node bundle nodes get-prims


Get Prims
=========

.. <description>

Filters primitives in the input bundle by path and type.

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.nodes<ext_omni_graph_nodes>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Bundle (*inputs:bundle*)", "``bundle``", "The bundle to be read from", "None"
    "Inverse (*inputs:inverse*)", "``bool``", "By default all primitives matching the path patterns and types are added to the output bundle; when this option is on, all mismatching primitives will be added instead.", "False"
    "Path Pattern (*inputs:pathPattern*)", "``string``", "A list of wildcard patterns used to match primitive path.  Supported syntax of wildcard pattern:     `*` - match an arbitrary number of any characters     `?` - match any single character     `^` - (caret) is used to define a pattern that is to be excluded  Example of wildcard patterns, input: ['/Cube0', '/Cube1', '/Box']     '*' - match any     '* ^/Box' - match any, but exclude '/Box'     '* ^/Cube*' - match any, but exclude '/Cube0' and '/Cube1'", "*"
    "Prims (*inputs:prims*)", "``target``", "The prim to be extracted from Multiple Primitives in Bundle.", "None"
    "", "Metadata", "*allowMultiInputs* = 1", ""
    "Type Pattern (*inputs:typePattern*)", "``string``", "A list of wildcard patterns used to match primitive type.  Supported syntax of wildcard pattern:     `*` - match an arbitrary number of any characters     `?` - match any single character     `^` - (caret) is used to define a pattern that is to be excluded  Example of wildcard patterns, input: ['Mesh', 'Cone', 'Cube']     '*' - match any     '* ^Mesh' - match any, but exclude 'Mesh'     '* ^Cone ^Cube' - match any, but exclude 'Cone' and 'Cube'", "*"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Bundle (*outputs:bundle*)", "``bundle``", "The output bundle that contains filtered primitives", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.nodes.GetPrims"
    "Version", "2"
    "Extension", "omni.graph.nodes"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Get Prims"
    "Categories", "bundle"
    "Generated Class Name", "OgnGetPrimsDatabase"
    "Python Module", "omni.graph.nodes"

