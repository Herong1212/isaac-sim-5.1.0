.. _omni_graph_nodes_BreakVector4_1:

.. _omni_graph_nodes_BreakVector4:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Break 4-Vector
    :keywords: lang-en omnigraph node math:conversion threadsafe nodes break-vector4


Break 4-Vector
==============

.. <description>

Split vector into 4 component values.

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.nodes_core<ext_omni_graph_nodes_core>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Vector (*inputs:tuple*)", "``['double[4]', 'double[4][]', 'float[4]', 'float[4][]', 'half[4]', 'half[4][]', 'int[4]', 'int[4][]']``", "4-vector to be broken", "None"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "W (*outputs:w*)", "``['double', 'double[]', 'float', 'float[]', 'half', 'half[]', 'int', 'int[]']``", "The fourth component of the vector", "None"
    "X (*outputs:x*)", "``['double', 'double[]', 'float', 'float[]', 'half', 'half[]', 'int', 'int[]']``", "The first component of the vector", "None"
    "Y (*outputs:y*)", "``['double', 'double[]', 'float', 'float[]', 'half', 'half[]', 'int', 'int[]']``", "The second component of the vector", "None"
    "Z (*outputs:z*)", "``['double', 'double[]', 'float', 'float[]', 'half', 'half[]', 'int', 'int[]']``", "The third component of the vector", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.nodes.BreakVector4"
    "Version", "1"
    "Extension", "omni.graph.nodes_core"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "tags", "decompose,separate,isolate"
    "uiName", "Break 4-Vector"
    "Categories", "math:conversion"
    "Generated Class Name", "OgnBreakVector4Database"
    "Python Module", "omni.graph.nodes_core"

