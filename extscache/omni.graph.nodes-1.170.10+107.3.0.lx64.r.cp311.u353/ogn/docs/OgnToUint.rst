.. _omni_graph_nodes_ToUint_1:

.. _omni_graph_nodes_ToUint:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: To UInt
    :keywords: lang-en omnigraph node math:conversion threadsafe nodes to-uint


To UInt
=======

.. <description>

Converts the input to 32-bit unsigned integer. Array inputs are converted element-wise to arrays of the same shape. Conversion of floating-point values is performed by truncation towards zero. Conversion of negative values is performed by subtracting the converted positive value from the value 2e32.

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

    "UInt (*outputs:converted*)", "``['uint', 'uint[]']``", "The value converted to 32-bit unsigned integer form.", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.nodes.ToUint"
    "Version", "1"
    "Extension", "omni.graph.nodes"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "To UInt"
    "Categories", "math:conversion"
    "Generated Class Name", "OgnToUintDatabase"
    "Python Module", "omni.graph.nodes"

