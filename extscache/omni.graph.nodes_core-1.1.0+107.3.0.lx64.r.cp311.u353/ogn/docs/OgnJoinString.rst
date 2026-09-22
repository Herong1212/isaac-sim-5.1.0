.. _omni_graph_nodes_JoinString_1:

.. _omni_graph_nodes_JoinString:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Join String
    :keywords: lang-en omnigraph node function threadsafe nodes join-string


Join String
===========

.. <description>

Creates a string from an input array and a delimiter.

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.nodes_core<ext_omni_graph_nodes_core>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Delimiter (*inputs:delimiter*)", "``string``", "The delimiter string used to join the elements.", " "
    "Elements (*inputs:elements*)", "``token[]``", "The string elements to join.", "[]"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "String (*outputs:string*)", "``string``", "The output string.", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.nodes.JoinString"
    "Version", "1"
    "Extension", "omni.graph.nodes_core"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Join String"
    "Categories", "function"
    "Generated Class Name", "OgnJoinStringDatabase"
    "Python Module", "omni.graph.nodes_core"

