.. _omni_graph_nodes_CompareTargets_1:

.. _omni_graph_nodes_CompareTargets:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Compare Targets
    :keywords: lang-en omnigraph node math:condition threadsafe nodes compare-targets


Compare Targets
===============

.. <description>

Outputs the value of a comparison operation on target arrays.

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.nodes<ext_omni_graph_nodes>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "A (*inputs:a*)", "``target``", "Input A", "None"
    "", "Metadata", "*allowMultiInputs* = 1", ""
    "B (*inputs:b*)", "``target``", "Input B", "None"
    "", "Metadata", "*allowMultiInputs* = 1", ""
    "Compare Each (*inputs:compareEach*)", "``bool``", "If true, compare each array per-element. If false, compare the entire array and output a single value.", "False"
    "Operation (*inputs:operation*)", "``token``", "The comparison operation to perform (==,!=))", "=="
    "", "Metadata", "*allowedTokens* = ==,!=", ""


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Result (*outputs:result*)", "``['bool', 'bool[]']``", "The result of the comparison operation", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.nodes.CompareTargets"
    "Version", "1"
    "Extension", "omni.graph.nodes"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Compare Targets"
    "Categories", "math:condition"
    "Generated Class Name", "OgnCompareTargetsDatabase"
    "Python Module", "omni.graph.nodes"

