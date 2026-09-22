.. _omni_graph_nodes_ArrayLength_1:

.. _omni_graph_nodes_ArrayLength:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Extract Attribute Array Length
    :keywords: lang-en omnigraph node math:array threadsafe nodes array-length


Extract Attribute Array Length
==============================

.. <description>

Outputs the length of a specified array attribute in an input bundle, or 1 if the attribute is not an array attribute

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.nodes<ext_omni_graph_nodes>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Attribute Name (*inputs:attrName*)", "``token``", "Name of the attribute whose array length will be queried", "points"
    "Attribute Bundle (*inputs:data*)", "``bundle``", "Collection of attributes that may contain the named attribute", "None"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Array Length (*outputs:length*)", "``uint64``", "The length of the array attribute in the input bundle", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.nodes.ArrayLength"
    "Version", "1"
    "Extension", "omni.graph.nodes"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Extract Attribute Array Length"
    "Categories", "math:array"
    "Generated Class Name", "OgnArrayLengthDatabase"
    "Python Module", "omni.graph.nodes"

