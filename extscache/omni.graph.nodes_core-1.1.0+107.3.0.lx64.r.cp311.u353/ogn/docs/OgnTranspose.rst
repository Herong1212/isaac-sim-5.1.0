.. _omni_graph_nodes_Transpose_1:

.. _omni_graph_nodes_Transpose:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Transpose
    :keywords: lang-en omnigraph node math:operator threadsafe nodes transpose


Transpose
=========

.. <description>

Computes the transposed matrix from an input matrix (or array of matrices) and outputs the result in an entirely-new matrix (or array of matrices) - the original inputs are not mutated in-place. The transpose of a matrix is an operation that "flips" a matrix over its diagonal, i.e. it switches the rows the columns of the matrix. For example, the transpose of the 2x3 matrix [[0, 1], [2, 3], [4, 5]] is the 3x2 matrix [[0, 2, 4], [1, 3, 5]].

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.nodes_core<ext_omni_graph_nodes_core>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Matrix (*inputs:matrix*)", "``['matrixd[2]', 'matrixd[2][]', 'matrixd[3]', 'matrixd[3][]', 'matrixd[4]', 'matrixd[4][]']``", "Input matrix or matrices. For arrays of matrices, the transpose will be computed for each member matrix.", "None"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Result (*outputs:result*)", "``['matrixd[2]', 'matrixd[2][]', 'matrixd[3]', 'matrixd[3][]', 'matrixd[4]', 'matrixd[4][]']``", "The transposed matrix or matrices, with the same typing and size as the input(s).", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.nodes.Transpose"
    "Version", "1"
    "Extension", "omni.graph.nodes_core"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Transpose"
    "Categories", "math:operator"
    "Generated Class Name", "OgnTransposeDatabase"
    "Python Module", "omni.graph.nodes_core"

