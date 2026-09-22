.. _omni_graph_nodes_GetParentPrims_1:

.. _omni_graph_nodes_GetParentPrims:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Get Target Parents
    :keywords: lang-en omnigraph node sceneGraph threadsafe nodes get-parent-prims


Get Target Parents
==================

.. <description>

Generates parent paths from one or more targeted paths (ex. /World/Cube -> /World)

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.nodes<ext_omni_graph_nodes>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Targets (*inputs:prims*)", "``target``", "Input paths (ex. /World/Cube)", "None"
    "", "Metadata", "*allowMultiInputs* = 1", ""


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Target Parents (*outputs:parentPrims*)", "``target``", "Computed parent paths (ex. /World)", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.nodes.GetParentPrims"
    "Version", "1"
    "Extension", "omni.graph.nodes"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Get Target Parents"
    "Categories", "sceneGraph"
    "Generated Class Name", "OgnGetParentPrimsDatabase"
    "Python Module", "omni.graph.nodes"

