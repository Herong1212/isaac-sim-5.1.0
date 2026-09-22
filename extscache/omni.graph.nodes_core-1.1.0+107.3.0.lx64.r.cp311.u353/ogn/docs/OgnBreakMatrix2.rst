.. _omni_graph_nodes_BreakMatrix2_1:

.. _omni_graph_nodes_BreakMatrix2:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Break Matrix2
    :keywords: lang-en omnigraph node math:conversion threadsafe nodes break-matrix2


Break Matrix2
=============

.. <description>

Split matrix into 2 vectors. If the input is an array, the output will be arrays of vectors.

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.nodes_core<ext_omni_graph_nodes_core>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Matrix (*inputs:matrix*)", "``['matrixd[2]', 'matrixd[2][]']``", "Input matrix(s)", "None"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "X (*outputs:x*)", "``['double[2]', 'double[2][]']``", "The first row of the matrix", "None"
    "Y (*outputs:y*)", "``['double[2]', 'double[2][]']``", "The second row of the matrix", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.nodes.BreakMatrix2"
    "Version", "1"
    "Extension", "omni.graph.nodes_core"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "tags", "decompose,separate,isolate"
    "uiName", "Break Matrix2"
    "Categories", "math:conversion"
    "Generated Class Name", "OgnBreakMatrix2Database"
    "Python Module", "omni.graph.nodes_core"

