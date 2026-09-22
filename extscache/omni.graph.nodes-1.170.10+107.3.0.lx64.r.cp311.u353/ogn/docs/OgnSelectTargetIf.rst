.. _omni_graph_nodes_SelectTargetIf_1:

.. _omni_graph_nodes_SelectTargetIf:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Select Target If
    :keywords: lang-en omnigraph node flowControl threadsafe nodes select-target-if


Select Target If
================

.. <description>

Selects a target from the given inputs based on a boolean condition. If condition is a scalar, result will either be "ifTrue" or "ifFalse". If it is an array, select between each input element-wise (if arrays are the same length).

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.nodes<ext_omni_graph_nodes>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Condition (*inputs:condition*)", "``['bool', 'bool[]']``", "The boolean condition used to select between ""ifTrue"" and ""ifFalse"". If a scalar, result will either be ""ifTrue"" or ""ifFalse"". If an array, select between each input element-wise (if arrays are the same length).", "None"
    "If False (*inputs:ifFalse*)", "``target``", "The targets if condition is ""False"".", "None"
    "", "Metadata", "*allowMultiInputs* = 1", ""
    "If True (*inputs:ifTrue*)", "``target``", "The targets if condition is ""True"".", "None"
    "", "Metadata", "*allowMultiInputs* = 1", ""


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Result (*outputs:result*)", "``target``", "The selected targets from ifTrue and ifFalse", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.nodes.SelectTargetIf"
    "Version", "1"
    "Extension", "omni.graph.nodes"
    "Icon", "ogn/icons/omni.graph.nodes.SelectTargetIf.svg"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Select Target If"
    "Categories", "flowControl"
    "Generated Class Name", "OgnSelectTargetIfDatabase"
    "Python Module", "omni.graph.nodes"

