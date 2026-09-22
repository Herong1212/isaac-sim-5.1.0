.. _omni_graph_nodes_ReplaceString_1:

.. _omni_graph_nodes_ReplaceString:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Replace String
    :keywords: lang-en omnigraph node function threadsafe nodes replace-string


Replace String
==============

.. <description>

Replaces the first occurrence of the given value from an array with a new value.  If "replaceAll" is true, replace all occurrences.

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.nodes<ext_omni_graph_nodes>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Replace (*inputs:replace*)", "``['string', 'token']``", "The string to replace within the base string.", "None"
    "Replace All (*inputs:replaceAll*)", "``bool``", "If true, replace all occurrences of the value.", "False"
    "String (*inputs:string*)", "``['string', 'token']``", "The base string.", "None"
    "Value (*inputs:value*)", "``['string', 'token']``", "The sub string to set within the base string. Can be an empty string to remove.", "None"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "String (*outputs:string*)", "``['string', 'token']``", "The output string.", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.nodes.ReplaceString"
    "Version", "1"
    "Extension", "omni.graph.nodes"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Replace String"
    "Categories", "function"
    "Generated Class Name", "OgnReplaceStringDatabase"
    "Python Module", "omni.graph.nodes"

