.. _omni_graph_nodes_EndsWith_1:

.. _omni_graph_nodes_EndsWith:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Ends With
    :keywords: lang-en omnigraph node function threadsafe nodes ends-with


Ends With
=========

.. <description>

Determines if a string ends with a given string value

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.nodes<ext_omni_graph_nodes>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Suffix (*inputs:suffix*)", "``string``", "The suffix to test", ""
    "Value (*inputs:value*)", "``string``", "The string to check", ""


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Is Suffix (*outputs:isSuffix*)", "``bool``", "True if 'value' ends with 'suffix'", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.nodes.EndsWith"
    "Version", "1"
    "Extension", "omni.graph.nodes"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Ends With"
    "Categories", "function"
    "Generated Class Name", "OgnEndsWithDatabase"
    "Python Module", "omni.graph.nodes"

