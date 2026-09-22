.. _omni_graph_nodes_ToUchar_1:

.. _omni_graph_nodes_ToUchar:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: To UChar
    :keywords: lang-en omnigraph node math:conversion threadsafe nodes to-uchar


To UChar
========

.. <description>

Converts the input to 8-bit unsigned integer. Array inputs are converted element-wise to arrays of the same shape. Conversion of floating-point values is performed by truncation towards zero. Conversion of negative values is performed by subtracting the converted positive value from 256.

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.nodes_core<ext_omni_graph_nodes_core>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Value (*inputs:value*)", "``['bool', 'bool[]', 'double', 'double[]', 'float', 'float[]', 'half', 'half[]', 'int', 'int64', 'int64[]', 'int[]', 'string', 'uchar', 'uchar[]', 'uint', 'uint64', 'uint64[]', 'uint[]']``", "The numeric or boolean value to convert.", "None"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "UChar (*outputs:converted*)", "``['uchar', 'uchar[]']``", "The value converted to 8-bit unsigned integer form.", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.nodes.ToUchar"
    "Version", "1"
    "Extension", "omni.graph.nodes_core"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "To UChar"
    "Categories", "math:conversion"
    "Generated Class Name", "OgnToUcharDatabase"
    "Python Module", "omni.graph.nodes_core"

