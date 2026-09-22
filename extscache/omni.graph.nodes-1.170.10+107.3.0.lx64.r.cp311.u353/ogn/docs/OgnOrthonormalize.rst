.. _omni_graph_nodes_Orthonormalize_1:

.. _omni_graph_nodes_Orthonormalize:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Orthonormalize
    :keywords: lang-en omnigraph node math:operator threadsafe nodes orthonormalize


Orthonormalize
==============

.. <description>

Computes the orthonormalized matrix from an input matrix or array of matrices. In practice, this involves treating the columns (or rows, depending on whether column-major or row-major semantics are being utilized for matrix descriptions - in mathematics the former is often used, while in computer graphics the latter tends to be preferred) of each input matrix as independent vectors that span some N-dimensional space (N being the number of column or row vectors in the matrix) and finding another set of mutually-perpendicular vectors that span the same space before normalizing each one (hence the term "orthonormal"; also see the so-called "Gram-Schmidt Process" that details exactly how one can go about performing this computation); these new sets of vectors can then be combined to form the "orthonormal" versions of each input matrix.

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.nodes<ext_omni_graph_nodes>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Matrix (*inputs:matrix*)", "``['matrixd[3]', 'matrixd[3][]', 'matrixd[4]', 'matrixd[4][]']``", "Input matrix or array of matrices to orthonormalize.", "None"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Result (*outputs:result*)", "``['matrixd[3]', 'matrixd[3][]', 'matrixd[4]', 'matrixd[4][]']``", "The orthonormalized matrix or array of matrices (with preserved typing).", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.nodes.Orthonormalize"
    "Version", "1"
    "Extension", "omni.graph.nodes"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Orthonormalize"
    "Categories", "math:operator"
    "Generated Class Name", "OgnOrthonormalizeDatabase"
    "Python Module", "omni.graph.nodes"

