.. _omni_graph_nodes_CapitalizeString_1:

.. _omni_graph_nodes_CapitalizeString:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Capitalize String
    :keywords: lang-en omnigraph node function threadsafe nodes capitalize-string


Capitalize String
=================

.. <description>

Formats a string based on a formatting operation (Upper Case, Lower Case, Capitalize, Title, etc.).

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.nodes_core<ext_omni_graph_nodes_core>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Operation (*inputs:operation*)", "``token``", "The formatting operation.", "UpperCase"
    "", "Metadata", "*literalOnly* = 1", ""
    "", "Metadata", "*allowedTokens* = UpperCase,LowerCase,Capitalize,Title", ""
    "String (*inputs:string*)", "``['string', 'token', 'token[]']``", "The base string.", "None"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "String (*outputs:string*)", "``['string', 'token', 'token[]']``", "The modified string.", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.nodes.CapitalizeString"
    "Version", "1"
    "Extension", "omni.graph.nodes_core"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Capitalize String"
    "Categories", "function"
    "Generated Class Name", "OgnCapitalizeStringDatabase"
    "Python Module", "omni.graph.nodes_core"

