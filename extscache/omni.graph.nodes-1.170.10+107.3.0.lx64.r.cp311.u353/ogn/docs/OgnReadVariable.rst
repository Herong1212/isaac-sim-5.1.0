.. _omni_graph_core_ReadVariable_2:

.. _omni_graph_core_ReadVariable:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Read Variable
    :keywords: lang-en omnigraph node internal threadsafe core read-variable


Read Variable
=============

.. <description>

Node that reads a value from a variable

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.nodes<ext_omni_graph_nodes>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Graph (*inputs:graph*)", "``target``", "Ignored. Do not use", "None"
    "", "Metadata", "*hidden* = true", ""
    "Target Path (*inputs:targetPath*)", "``token``", "Ignored. Do not use.", "None"
    "", "Metadata", "*hidden* = true", ""
    "Variable Name (*inputs:variableName*)", "``token``", "The name of the graph variable to use.", ""
    "", "Metadata", "*hidden* = true", ""
    "", "Metadata", "*literalOnly* = 1", ""


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Value (*outputs:value*)", "``any``", "The variable value that we returned.", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.core.ReadVariable"
    "Version", "2"
    "Extension", "omni.graph.nodes"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "hidden", "true"
    "uiName", "Read Variable"
    "Categories", "internal"
    "Generated Class Name", "OgnReadVariableDatabase"
    "Python Module", "omni.graph.nodes"

