.. _omni_graph_nodes_BreakVector2_1:

.. _omni_graph_nodes_BreakVector2:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Break 2-Vector
    :keywords: lang-en omnigraph node math:conversion threadsafe nodes break-vector2


Break 2-Vector
==============

.. <description>

Split vector into 2 component values.

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.nodes<ext_omni_graph_nodes>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Vector (*inputs:tuple*)", "``['double[2]', 'double[2][]', 'float[2]', 'float[2][]', 'half[2]', 'half[2][]', 'int[2]', 'int[2][]']``", "2-vector to be broken", "None"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "X (*outputs:x*)", "``['double', 'double[]', 'float', 'float[]', 'half', 'half[]', 'int', 'int[]']``", "The first component of the vector", "None"
    "Y (*outputs:y*)", "``['double', 'double[]', 'float', 'float[]', 'half', 'half[]', 'int', 'int[]']``", "The second component of the vector", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.nodes.BreakVector2"
    "Version", "1"
    "Extension", "omni.graph.nodes"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "tags", "decompose,separate,isolate"
    "uiName", "Break 2-Vector"
    "Categories", "math:conversion"
    "Generated Class Name", "OgnBreakVector2Database"
    "Python Module", "omni.graph.nodes"

