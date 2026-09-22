.. _omni_graph_nodes_TransformVector_1:

.. _omni_graph_nodes_TransformVector:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Transform Vector
    :keywords: lang-en omnigraph node math:operator threadsafe nodes transform-vector


Transform Vector
================

.. <description>

Applies a transformation matrix to a row vector, returning the result. returns 'Vector' * 'Matrix'. If the vector is one dimension smaller than the matrix (eg a 4x4 matrix and a 3d vector),  the last component of the vector will be treated as a 1. The result is then projected back to a 3-vector.  Supports mixed array inputs, eg a single matrix and an array of vectors.

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.nodes_core<ext_omni_graph_nodes_core>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Matrix (*inputs:matrix*)", "``['matrixd[3]', 'matrixd[3][]', 'matrixd[4]', 'matrixd[4][]']``", "The transformation matrix to be applied", "None"
    "Vector (*inputs:vector*)", "``['vectord[3]', 'vectord[3][]', 'vectorf[3]', 'vectorf[3][]', 'vectorh[3]', 'vectorh[3][]']``", "The row vector(s) to be translated", "None"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Vector (*outputs:result*)", "``['vectord[3]', 'vectord[3][]', 'vectorf[3]', 'vectorf[3][]', 'vectorh[3]', 'vectorh[3][]']``", "The transformed row vector(s)", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.nodes.TransformVector"
    "Version", "1"
    "Extension", "omni.graph.nodes_core"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Transform Vector"
    "Categories", "math:operator"
    "Generated Class Name", "OgnTransformVectorDatabase"
    "Python Module", "omni.graph.nodes_core"

