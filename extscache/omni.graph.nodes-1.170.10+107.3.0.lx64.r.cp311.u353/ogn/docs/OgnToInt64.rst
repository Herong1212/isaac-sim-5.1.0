.. _omni_graph_nodes_ToInt64_1:

.. _omni_graph_nodes_ToInt64:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: To Int64
    :keywords: lang-en omnigraph node math:conversion threadsafe nodes to-int64


To Int64
========

.. <description>

Convert the given input to signed 64-bit integer. Array and tuple inputs are converted element-wise to arrays and tuples of the same shape. Conversion of floating-point values is performed by truncation towards zero.

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.nodes<ext_omni_graph_nodes>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Value (*inputs:value*)", "``['bool', 'bool[]', 'double', 'double[]', 'float', 'float[]', 'half', 'half[]', 'int', 'int64', 'int64[]', 'int[]', 'uchar', 'uchar[]', 'uint', 'uint64', 'uint64[]', 'uint[]']``", "The numeric or boolean value to convert.", "None"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Int64 (*outputs:converted*)", "``['int64', 'int64[]']``", "The value converted to 64-bit integer form.", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.nodes.ToInt64"
    "Version", "1"
    "Extension", "omni.graph.nodes"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "To Int64"
    "Categories", "math:conversion"
    "Generated Class Name", "OgnToInt64Database"
    "Python Module", "omni.graph.nodes"

