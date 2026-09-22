.. _omni_graph_nodes_GraphTarget_1:

.. _omni_graph_nodes_GraphTarget:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Get Graph Target
    :keywords: lang-en omnigraph node sceneGraph threadsafe nodes graph-target


Get Graph Target
================

.. <description>

Access the target prim the graph is being executed on. If the graph is executing itself, this will output the prim path of the graph. Otherwise the graph is being executed via  instancing, then this will output the prim path of the target instance.

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.nodes<ext_omni_graph_nodes>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Target Path (*inputs:targetPath*)", "``token``", "Deprecated. Do not use.", ""
    "", "Metadata", "*hidden* = true", ""


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Prim Path (*outputs:primPath*)", "``token``", "The target prim path", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.nodes.GraphTarget"
    "Version", "1"
    "Extension", "omni.graph.nodes"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Get Graph Target"
    "Categories", "sceneGraph"
    "Generated Class Name", "OgnGraphTargetDatabase"
    "Python Module", "omni.graph.nodes"

