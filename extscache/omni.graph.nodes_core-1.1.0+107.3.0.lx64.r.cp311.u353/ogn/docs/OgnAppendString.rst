.. _omni_graph_nodes_AppendString_1:

.. _omni_graph_nodes_AppendString:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Append String (Deprecated)
    :keywords: lang-en omnigraph node function,internal:test threadsafe nodes append-string


Append String (Deprecated)
==========================

.. <description>

Creates a new token or string by appending the given token or string. token[] inputs will be appended element-wise.

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.nodes_core<ext_omni_graph_nodes_core>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Suffix (*inputs:suffix*)", "``['string', 'token', 'token[]']``", "The string to be appended", "None"
    "Value (*inputs:value*)", "``['string', 'token', 'token[]']``", "The string(s) to be appended to", "None"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Value (*outputs:value*)", "``['string', 'token', 'token[]']``", "The new string(s)", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.nodes.AppendString"
    "Version", "1"
    "Extension", "omni.graph.nodes_core"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "hidden", "true"
    "uiName", "Append String (Deprecated)"
    "Categories", "function,internal:test"
    "Generated Class Name", "OgnAppendStringDatabase"
    "Python Module", "omni.graph.nodes_core"

