.. _omni_graph_nodes_BreakMatrix4_1:

.. _omni_graph_nodes_BreakMatrix4:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Break Matrix4
    :keywords: lang-en omnigraph node math:conversion threadsafe nodes break-matrix4


Break Matrix4
=============

.. <description>

Split matrix into 4 vectors. If the input is an array, the output will be arrays of vectors.

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.nodes<ext_omni_graph_nodes>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Matrix (*inputs:matrix*)", "``['matrixd[4]', 'matrixd[4][]']``", "Input matrix(s)", "None"
    "Output Type (*inputs:outputType*)", "``token``", "The type of output vector: Double3 or Double4", "double[4]"
    "", "Metadata", "*literalOnly* = 1", ""
    "", "Metadata", "*allowedTokens* = double[3],double[4]", ""


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "W (*outputs:w*)", "``['double[3]', 'double[3][]', 'double[4]', 'double[4][]']``", "The fourth row of the matrix", "None"
    "X (*outputs:x*)", "``['double[3]', 'double[3][]', 'double[4]', 'double[4][]']``", "The first row of the matrix", "None"
    "Y (*outputs:y*)", "``['double[3]', 'double[3][]', 'double[4]', 'double[4][]']``", "The second row of the matrix", "None"
    "Z (*outputs:z*)", "``['double[3]', 'double[3][]', 'double[4]', 'double[4][]']``", "The third row of the matrix", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.nodes.BreakMatrix4"
    "Version", "1"
    "Extension", "omni.graph.nodes"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "tags", "decompose,separate,isolate"
    "uiName", "Break Matrix4"
    "Categories", "math:conversion"
    "Generated Class Name", "OgnBreakMatrix4Database"
    "Python Module", "omni.graph.nodes"

