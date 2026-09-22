.. _omni_graph_nodes_GetPrimPaths_1:

.. _omni_graph_nodes_GetPrimPaths:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Get Prim Paths
    :keywords: lang-en omnigraph node sceneGraph threadsafe nodes get-prim-paths


Get Prim Paths
==============

.. <description>

Generates a path array from the specified relationship. This is useful when absolute prim paths may change.

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.nodes<ext_omni_graph_nodes>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Prims (*inputs:prims*)", "``target``", "Relationship to prims on the stage", "None"
    "", "Metadata", "*allowMultiInputs* = 1", ""


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Prim Paths (*outputs:primPaths*)", "``token[]``", "The absolute paths of the given prims as a token array", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.nodes.GetPrimPaths"
    "Version", "1"
    "Extension", "omni.graph.nodes"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Get Prim Paths"
    "Categories", "sceneGraph"
    "Generated Class Name", "OgnGetPrimPathsDatabase"
    "Python Module", "omni.graph.nodes"

