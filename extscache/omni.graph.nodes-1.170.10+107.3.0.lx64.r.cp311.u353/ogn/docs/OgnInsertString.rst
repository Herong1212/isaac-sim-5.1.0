.. _omni_graph_nodes_InsertString_1:

.. _omni_graph_nodes_InsertString:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Insert String
    :keywords: lang-en omnigraph node function threadsafe nodes insert-string


Insert String
=============

.. <description>

Insert a string into a base string at an index.

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.nodes<ext_omni_graph_nodes>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Index (*inputs:index*)", "``int``", "The index of the string in the range [0, stringLength].  Index will be clamped to the valid range.", "0"
    "String (*inputs:string*)", "``['string', 'token']``", "The base string.", "None"
    "Value (*inputs:value*)", "``['string', 'token']``", "The string to insert.", "None"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "String (*outputs:string*)", "``['string', 'token']``", "The modified string.", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.nodes.InsertString"
    "Version", "1"
    "Extension", "omni.graph.nodes"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Insert String"
    "Categories", "function"
    "Generated Class Name", "OgnInsertStringDatabase"
    "Python Module", "omni.graph.nodes"

