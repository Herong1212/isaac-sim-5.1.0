.. _omni_graph_nodes_GetPrimsAtPath_1:

.. _omni_graph_nodes_GetPrimsAtPath:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Get Prims At Path (Legacy)
    :keywords: lang-en omnigraph node sceneGraph threadsafe nodes get-prims-at-path


Get Prims At Path (Legacy)
==========================

.. <description>

DEPRECATED - Use ToTarget

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.nodes<ext_omni_graph_nodes>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Path (*inputs:path*)", "``['token', 'token[]']``", "A token or token array to compute representing a path.", "None"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Prims (*outputs:prims*)", "``target``", "The output prim paths", "None"


State
-----
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Path (*state:path*)", "``token``", "Snapshot of previously seen path", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.nodes.GetPrimsAtPath"
    "Version", "1"
    "Extension", "omni.graph.nodes"
    "Has State?", "True"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "hidden", "true"
    "uiName", "Get Prims At Path (Legacy)"
    "Categories", "sceneGraph"
    "Generated Class Name", "OgnGetPrimsAtPathDatabase"
    "Python Module", "omni.graph.nodes"

