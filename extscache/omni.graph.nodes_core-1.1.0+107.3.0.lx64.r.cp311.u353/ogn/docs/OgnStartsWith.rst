.. _omni_graph_nodes_StartsWith_1:

.. _omni_graph_nodes_StartsWith:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Starts With
    :keywords: lang-en omnigraph node function threadsafe nodes starts-with


Starts With
===========

.. <description>

Determines if a string starts with a given string value

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.nodes_core<ext_omni_graph_nodes_core>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Prefix (*inputs:prefix*)", "``string``", "The prefix to test", ""
    "Value (*inputs:value*)", "``string``", "The string to check", ""


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Is Prefix (*outputs:isPrefix*)", "``bool``", "True if 'value' starts with 'prefix'", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.nodes.StartsWith"
    "Version", "1"
    "Extension", "omni.graph.nodes_core"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Starts With"
    "Categories", "function"
    "Generated Class Name", "OgnStartsWithDatabase"
    "Python Module", "omni.graph.nodes_core"

