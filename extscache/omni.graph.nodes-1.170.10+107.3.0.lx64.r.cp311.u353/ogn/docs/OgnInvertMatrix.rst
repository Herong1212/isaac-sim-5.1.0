.. _omni_graph_nodes_OgnInvertMatrix_1:

.. _omni_graph_nodes_OgnInvertMatrix:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Invert Matrix
    :keywords: lang-en omnigraph node math:operator threadsafe nodes ogn-invert-matrix


Invert Matrix
=============

.. <description>

Invert a matrix or an array of matrices. Returns the FLOAT_MAX * identity if the matrix is singular.

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.nodes<ext_omni_graph_nodes>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Input (*inputs:matrix*)", "``['matrixd[2]', 'matrixd[2][]', 'matrixd[3]', 'matrixd[3][]', 'matrixd[4]', 'matrixd[4][]']``", "The input matrix or matrices to invert", "None"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Inverse (*outputs:invertedMatrix*)", "``['matrixd[2]', 'matrixd[2][]', 'matrixd[3]', 'matrixd[3][]', 'matrixd[4]', 'matrixd[4][]']``", "The resulting inverted matrix or matrices", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.nodes.OgnInvertMatrix"
    "Version", "1"
    "Extension", "omni.graph.nodes"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Invert Matrix"
    "Categories", "math:operator"
    "Generated Class Name", "OgnInvertMatrixDatabase"
    "Python Module", "omni.graph.nodes"

