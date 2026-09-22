.. _omni_graph_nodes_ReplaceTargetName_1:

.. _omni_graph_nodes_ReplaceTargetName:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Replace Target Name
    :keywords: lang-en omnigraph node sceneGraph threadsafe nodes replace-target-name


Replace Target Name
===================

.. <description>

Replaces the target name (the last element) with the specified name. Array inputs will be appended element-wise.

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.nodes<ext_omni_graph_nodes>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "New Name (*inputs:newName*)", "``['string', 'token', 'token[]']``", "The new name to replace the current name.  Array inputs will be appended element-wise.", "None"
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

    "Unique ID", "omni.graph.nodes.ReplaceTargetName"
    "Version", "1"
    "Extension", "omni.graph.nodes"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Replace Target Name"
    "Categories", "sceneGraph"
    "Generated Class Name", "OgnReplaceTargetNameDatabase"
    "Python Module", "omni.graph.nodes"

