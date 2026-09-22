.. _omni_graph_nodes_GetPrimPath_3:

.. _omni_graph_nodes_GetPrimPath:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Get Prim Path
    :keywords: lang-en omnigraph node sceneGraph threadsafe nodes get-prim-path


Get Prim Path
=============

.. <description>

Generates a path from the specified relationship. This is useful when an absolute prim path may change.

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.nodes<ext_omni_graph_nodes>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Prim (*inputs:prim*)", "``target``", "The prim to determine the path of", "None"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Path (*outputs:path*)", "``path``", "The absolute path of the given prim as a string", "None"
    "Prim Path (*outputs:primPath*)", "``token``", "The absolute path of the given prim as a token", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.nodes.GetPrimPath"
    "Version", "3"
    "Extension", "omni.graph.nodes"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Get Prim Path"
    "Categories", "sceneGraph"
    "Generated Class Name", "OgnGetPrimPathDatabase"
    "Python Module", "omni.graph.nodes"

