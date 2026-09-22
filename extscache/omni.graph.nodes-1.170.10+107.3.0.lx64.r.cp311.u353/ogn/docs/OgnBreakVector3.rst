.. _omni_graph_nodes_BreakVector3_1:

.. _omni_graph_nodes_BreakVector3:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Break 3-Vector
    :keywords: lang-en omnigraph node math:conversion threadsafe nodes break-vector3


Break 3-Vector
==============

.. <description>

Split vector into 3 component values.

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.nodes<ext_omni_graph_nodes>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Vector (*inputs:tuple*)", "``['double[3]', 'double[3][]', 'float[3]', 'float[3][]', 'half[3]', 'half[3][]', 'int[3]', 'int[3][]']``", "3-vector to be broken", "None"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "X (*outputs:x*)", "``['double', 'double[]', 'float', 'float[]', 'half', 'half[]', 'int', 'int[]']``", "The first component of the vector", "None"
    "Y (*outputs:y*)", "``['double', 'double[]', 'float', 'float[]', 'half', 'half[]', 'int', 'int[]']``", "The second component of the vector", "None"
    "Z (*outputs:z*)", "``['double', 'double[]', 'float', 'float[]', 'half', 'half[]', 'int', 'int[]']``", "The third component of the vector", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.nodes.BreakVector3"
    "Version", "1"
    "Extension", "omni.graph.nodes"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "tags", "decompose,separate,isolate"
    "uiName", "Break 3-Vector"
    "Categories", "math:conversion"
    "Generated Class Name", "OgnBreakVector3Database"
    "Python Module", "omni.graph.nodes"

