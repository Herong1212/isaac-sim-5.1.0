.. _omni_graph_nodes_FindString_1:

.. _omni_graph_nodes_FindString:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Find String
    :keywords: lang-en omnigraph node function threadsafe nodes find-string


Find String
===========

.. <description>

Find the index of a substring in a base string starting at pos, or -1 if the string is not found.

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.nodes<ext_omni_graph_nodes>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Pos (*inputs:pos*)", "``int``", "The starting position to search for the string.", "0"
    "String (*inputs:string*)", "``['string', 'token']``", "The base string.", "None"
    "Value (*inputs:value*)", "``['string', 'token']``", "The string to search for.", "None"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Index (*outputs:index*)", "``int``", "The index of the first occurrence of string, or -1 if not found.", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.nodes.FindString"
    "Version", "1"
    "Extension", "omni.graph.nodes"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Find String"
    "Categories", "function"
    "Generated Class Name", "OgnFindStringDatabase"
    "Python Module", "omni.graph.nodes"

