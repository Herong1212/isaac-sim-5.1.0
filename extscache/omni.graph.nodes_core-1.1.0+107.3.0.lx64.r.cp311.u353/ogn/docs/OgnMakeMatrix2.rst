.. _omni_graph_nodes_MakeMatrix2_1:

.. _omni_graph_nodes_MakeMatrix2:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Make Matrix2
    :keywords: lang-en omnigraph node math:conversion threadsafe nodes make-matrix2


Make Matrix2
============

.. <description>

Merge 2 row vectors into a matrix. If the inputs are arrays, the output will be an array of matrices.

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.nodes_core<ext_omni_graph_nodes_core>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "First Row (*inputs:x*)", "``['double[2]', 'double[2][]']``", "The first row of the matrix", "None"
    "Second Row (*inputs:y*)", "``['double[2]', 'double[2][]']``", "The second row of the matrix", "None"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Matrix (*outputs:matrix*)", "``['matrixd[2]', 'matrixd[2][]']``", "Matrix formed by 'First Row' and 'Second Row'", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.nodes.MakeMatrix2"
    "Version", "1"
    "Extension", "omni.graph.nodes_core"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "tags", "compose,combine,join"
    "uiName", "Make Matrix2"
    "Categories", "math:conversion"
    "Generated Class Name", "OgnMakeMatrix2Database"
    "Python Module", "omni.graph.nodes_core"

