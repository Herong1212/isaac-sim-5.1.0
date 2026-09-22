.. _omni_graph_nodes_FindTarget_1:

.. _omni_graph_nodes_FindTarget:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Find Target
    :keywords: lang-en omnigraph node sceneGraph threadsafe nodes find-target


Find Target
===========

.. <description>

Returns the index of the first occurrence of a target, or -1 if not found.

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.nodes<ext_omni_graph_nodes>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Search Target (*inputs:searchTarget*)", "``target``", "The target to search for.", "None"
    "Targets (*inputs:targets*)", "``target``", "The input target array.", "None"
    "", "Metadata", "*allowMultiInputs* = 1", ""


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Index (*outputs:index*)", "``int``", "The index of the first occurrence of ""searchTarget"", or -1 if not found", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.nodes.FindTarget"
    "Version", "1"
    "Extension", "omni.graph.nodes"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Find Target"
    "Categories", "sceneGraph"
    "Generated Class Name", "OgnFindTargetDatabase"
    "Python Module", "omni.graph.nodes"

