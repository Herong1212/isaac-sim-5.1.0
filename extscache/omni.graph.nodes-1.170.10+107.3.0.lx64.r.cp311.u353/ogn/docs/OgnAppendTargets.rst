.. _omni_graph_nodes_AppendTargets_1:

.. _omni_graph_nodes_AppendTargets:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Append Targets
    :keywords: lang-en omnigraph node sceneGraph threadsafe nodes append-targets


Append Targets
==============

.. <description>

Combines the input target arrays into a single array. Duplicates are skipped unless "allowDuplicates" is true.

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.nodes<ext_omni_graph_nodes>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Allow Duplicates (*inputs:allowDuplicates*)", "``bool``", "If false, the path will only be added the first time it is encountered. If true, all paths will be added in order.", "False"
    "Input0 (*inputs:input0*)", "``target``", "Input target array.", "None"
    "", "Metadata", "*allowMultiInputs* = 1", ""
    "Input1 (*inputs:input1*)", "``target``", "Input target array.", "None"
    "", "Metadata", "*allowMultiInputs* = 1", ""


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Targets (*outputs:targets*)", "``target``", "The output target array.", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.nodes.AppendTargets"
    "Version", "1"
    "Extension", "omni.graph.nodes"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Append Targets"
    "Categories", "sceneGraph"
    "Generated Class Name", "OgnAppendTargetsDatabase"
    "Python Module", "omni.graph.nodes"

