.. _omni_graph_core_WriteVariable_2:

.. _omni_graph_core_WriteVariable:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Write Variable
    :keywords: lang-en omnigraph node internal WriteOnly core write-variable


Write Variable
==============

.. <description>

Node that writes a value to a variable

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.nodes<ext_omni_graph_nodes>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Exec In (*inputs:execIn*)", "``execution``", "Signal to the graph that this node is ready to be executed.", "None"
    "Graph (*inputs:graph*)", "``target``", "Ignored. Do not use", "None"
    "", "Metadata", "*hidden* = true", ""
    "Target Path (*inputs:targetPath*)", "``token``", "Ignored. Do not use.", "None"
    "", "Metadata", "*hidden* = true", ""
    "Value (*inputs:value*)", "``any``", "The new value to be written", "None"
    "Variable Name (*inputs:variableName*)", "``token``", "The name of the graph variable to use.", ""
    "", "Metadata", "*hidden* = true", ""
    "", "Metadata", "*literalOnly* = 1", ""


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Exec Out (*outputs:execOut*)", "``execution``", "Signal to the graph that execution can continue downstream.", "None"
    "Value (*outputs:value*)", "``any``", "The value written to the variable.", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.core.WriteVariable"
    "Version", "2"
    "Extension", "omni.graph.nodes"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "hidden", "true"
    "uiName", "Write Variable"
    "Categories", "internal"
    "Generated Class Name", "OgnWriteVariableDatabase"
    "Python Module", "omni.graph.nodes"

