.. _omni_graph_nodes_ToBool_1:

.. _omni_graph_nodes_ToBool:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: To Bool
    :keywords: lang-en omnigraph node math:conversion threadsafe nodes to-bool


To Bool
=======

.. <description>

Convert the numeric input to a boolean value. Scalar inputs will output a single boolean value, and array inputs will output an equivalently-sized array of booleans. Non-zero values convert to a boolean value of true, and zero values convert to a boolean value of false.

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.nodes<ext_omni_graph_nodes>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Value (*inputs:value*)", "``['bool', 'bool[]', 'double', 'double[]', 'float', 'float[]', 'half', 'half[]', 'int', 'int64', 'int64[]', 'int[]', 'uchar', 'uchar[]', 'uint', 'uint64', 'uint64[]', 'uint[]']``", "The input value to convert to boolean.", "None"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Bool (*outputs:converted*)", "``['bool', 'bool[]']``", "The converted boolean value or array of boolean values.", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.nodes.ToBool"
    "Version", "1"
    "Extension", "omni.graph.nodes"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "To Bool"
    "Categories", "math:conversion"
    "Generated Class Name", "OgnToBoolDatabase"
    "Python Module", "omni.graph.nodes"

