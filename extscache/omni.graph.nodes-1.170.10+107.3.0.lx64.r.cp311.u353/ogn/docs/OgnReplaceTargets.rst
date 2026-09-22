.. _omni_graph_nodes_ReplaceTargets_1:

.. _omni_graph_nodes_ReplaceTargets:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Replace Targets
    :keywords: lang-en omnigraph node sceneGraph threadsafe nodes replace-targets


Replace Targets
===============

.. <description>

Replaces all occurrences of the given targets with new targets in the input array.  Targets are replaced element-wise.

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.nodes<ext_omni_graph_nodes>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Replace Targets (*inputs:replaceTargets*)", "``target``", "The targets to replace.", "None"
    "", "Metadata", "*allowMultiInputs* = 1", ""
    "Set Targets (*inputs:setTargets*)", "``target``", "The new targets to set. If empty, targets will be removed.", "None"
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

    "Unique ID", "omni.graph.nodes.ReplaceTargets"
    "Version", "1"
    "Extension", "omni.graph.nodes"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Replace Targets"
    "Categories", "sceneGraph"
    "Generated Class Name", "OgnReplaceTargetsDatabase"
    "Python Module", "omni.graph.nodes"

