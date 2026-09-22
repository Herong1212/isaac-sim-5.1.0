.. _omni_graph_nodes_InsertTargets_1:

.. _omni_graph_nodes_InsertTargets:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Insert Targets
    :keywords: lang-en omnigraph node sceneGraph threadsafe nodes insert-targets


Insert Targets
==============

.. <description>

Inserts a target or target array to a target array at an index. Index is clamped in the range [0:arrayLength].

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.nodes<ext_omni_graph_nodes>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Index (*inputs:index*)", "``int``", "The array index clamped in the range [0:arrayLength] to insert the targets.", "0"
    "Insert Targets (*inputs:insertTargets*)", "``target``", "The targets to insert.", "None"
    "", "Metadata", "*allowMultiInputs* = 1", ""
    "Targets (*inputs:targets*)", "``target``", "The input target array.", "None"
    "", "Metadata", "*allowMultiInputs* = 1", ""


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Targets (*outputs:targets*)", "``target``", "The modified target array.", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.nodes.InsertTargets"
    "Version", "1"
    "Extension", "omni.graph.nodes"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Insert Targets"
    "Categories", "sceneGraph"
    "Generated Class Name", "OgnInsertTargetsDatabase"
    "Python Module", "omni.graph.nodes"

