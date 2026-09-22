.. _omni_graph_nodes_GetString_1:

.. _omni_graph_nodes_GetString:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Get String
    :keywords: lang-en omnigraph node function threadsafe nodes get-string


Get String
==========

.. <description>

Return a string in a base string at index with count.

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.nodes_core<ext_omni_graph_nodes_core>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Count (*inputs:count*)", "``int``", "The number of characters to return.  When set to -1, the length of ""string"" will be used.", "-1"
    "Index (*inputs:index*)", "``int``", "The index of the string in the range [-stringLength, stringLength).  Negative values index from the end of the string, and values out of range will result in an error.", "0"
    "String (*inputs:string*)", "``['string', 'token']``", "The base string.", "None"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "String (*outputs:string*)", "``['string', 'token']``", "The extracted string.", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.nodes.GetString"
    "Version", "1"
    "Extension", "omni.graph.nodes_core"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Get String"
    "Categories", "function"
    "Generated Class Name", "OgnGetStringDatabase"
    "Python Module", "omni.graph.nodes_core"

