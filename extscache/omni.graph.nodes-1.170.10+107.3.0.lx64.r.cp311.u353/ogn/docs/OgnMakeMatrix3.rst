.. _omni_graph_nodes_MakeMatrix3_1:

.. _omni_graph_nodes_MakeMatrix3:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Make Matrix3
    :keywords: lang-en omnigraph node math:conversion threadsafe nodes make-matrix3


Make Matrix3
============

.. <description>

Merge 3 row vectors into a matrix. If the inputs are arrays, the output will be an array of matrices.

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.nodes<ext_omni_graph_nodes>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "First Row (*inputs:x*)", "``['double[3]', 'double[3][]']``", "The first row of the matrix", "None"
    "Second Row (*inputs:y*)", "``['double[3]', 'double[3][]']``", "The second row of the matrix", "None"
    "Third Row (*inputs:z*)", "``['double[3]', 'double[3][]']``", "The third row of the matrix", "None"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Matrix (*outputs:matrix*)", "``['matrixd[3]', 'matrixd[3][]']``", "Matrix formed from the input row vectors", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.nodes.MakeMatrix3"
    "Version", "1"
    "Extension", "omni.graph.nodes"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "tags", "compose,combine,join"
    "uiName", "Make Matrix3"
    "Categories", "math:conversion"
    "Generated Class Name", "OgnMakeMatrix3Database"
    "Python Module", "omni.graph.nodes"

