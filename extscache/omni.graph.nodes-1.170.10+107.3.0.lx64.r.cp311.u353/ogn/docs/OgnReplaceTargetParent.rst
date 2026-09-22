.. _omni_graph_nodes_ReplaceTargetParent_1:

.. _omni_graph_nodes_ReplaceTargetParent:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Replace Target Parent
    :keywords: lang-en omnigraph node sceneGraph threadsafe nodes replace-target-parent


Replace Target Parent
=====================

.. <description>

Replaces the old parent with a new parent in every target in an array.  If the old parent is not found, the target is unmodified.

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.nodes<ext_omni_graph_nodes>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "New Parent (*inputs:newParent*)", "``target``", "The new target parent. If empty, use the stage.", "None"
    "Old Parent (*inputs:oldParent*)", "``target``", "The target parent to replace. If the old parent is not found, the target is unmodified.", "None"
    "Targets (*inputs:targets*)", "``target``", "The target array to be modified", "None"
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

    "Unique ID", "omni.graph.nodes.ReplaceTargetParent"
    "Version", "1"
    "Extension", "omni.graph.nodes"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Replace Target Parent"
    "Categories", "sceneGraph"
    "Generated Class Name", "OgnReplaceTargetParentDatabase"
    "Python Module", "omni.graph.nodes"

