.. _omni_graph_nodes_GetGraphTargetPrim_1:

.. _omni_graph_nodes_GetGraphTargetPrim:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Get Graph Target Prim
    :keywords: lang-en omnigraph node sceneGraph nodes get-graph-target-prim


Get Graph Target Prim
=====================

.. <description>

Access the target prim the graph is being executed on. If the graph is executing itself, this will output the prim of the graph. Otherwise the graph is being executed via  instancing, then this will output the prim of the target instance.

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.nodes<ext_omni_graph_nodes>` in the Extension Manager.


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Prim (*outputs:prim*)", "``target``", "The graph target as a prim", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.nodes.GetGraphTargetPrim"
    "Version", "1"
    "Extension", "omni.graph.nodes"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Get Graph Target Prim"
    "Categories", "sceneGraph"
    "Generated Class Name", "OgnGetGraphTargetPrimDatabase"
    "Python Module", "omni.graph.nodes"

