.. _omni_graph_nodes_SplitString_1:

.. _omni_graph_nodes_SplitString:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Split String
    :keywords: lang-en omnigraph node function threadsafe nodes split-string


Split String
============

.. <description>

Returns a list of elements from a string based on a delimiter.

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.nodes<ext_omni_graph_nodes>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Delimiter (*inputs:delimiter*)", "``string``", "The string to use as a delimiter to split the string.", " "
    "String (*inputs:string*)", "``string``", "The input string.", ""


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Elements (*outputs:elements*)", "``token[]``", "The string elements.", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.nodes.SplitString"
    "Version", "1"
    "Extension", "omni.graph.nodes"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Split String"
    "Categories", "function"
    "Generated Class Name", "OgnSplitStringDatabase"
    "Python Module", "omni.graph.nodes"

