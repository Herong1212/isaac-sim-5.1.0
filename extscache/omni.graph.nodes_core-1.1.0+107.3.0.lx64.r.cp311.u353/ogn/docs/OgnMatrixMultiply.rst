.. _omni_graph_nodes_MatrixMultiply_1:

.. _omni_graph_nodes_MatrixMultiply:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Matrix Multiply
    :keywords: lang-en omnigraph node math:operator threadsafe nodes matrix-multiply


Matrix Multiply
===============

.. <description>

Computes the matrix product of the inputs. Inputs must be compatible.  Also accepts tuples (treated as vectors) as inputs. Tuples in input 'A' will be treated as row vectors.  Tuples in input 'B' will be treated as column vectors.  Arrays of inputs will be computed element-wise with broadcasting if necessary. 

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.nodes_core<ext_omni_graph_nodes_core>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "A (*inputs:a*)", "``['colord[3]', 'colord[4]', 'colorf[3]', 'colorf[4]', 'colorh[3]', 'colorh[4]', 'double[2]', 'double[2][]', 'double[3]', 'double[3][]', 'double[4]', 'double[4][]', 'float[2]', 'float[2][]', 'float[3]', 'float[3][]', 'float[4]', 'float[4][]', 'frame[4]', 'half[2]', 'half[2][]', 'half[3]', 'half[3][]', 'half[4]', 'half[4][]', 'matrixd[2]', 'matrixd[2][]', 'matrixd[3]', 'matrixd[3][]', 'matrixd[4]', 'matrixd[4][]', 'normald[3]', 'normalf[3]', 'normalh[3]', 'pointd[3]', 'pointf[3]', 'pointh[3]', 'quatd[4]', 'quatf[4]', 'quath[4]', 'texcoordd[2]', 'texcoordd[3]', 'texcoordf[2]', 'texcoordf[3]', 'texcoordh[2]', 'texcoordh[3]', 'transform[4]', 'vectord[3]', 'vectorf[3]', 'vectorh[3]']``", "First matrix or row vector to multiply as A*B", "None"
    "B (*inputs:b*)", "``['colord[3]', 'colord[4]', 'colorf[3]', 'colorf[4]', 'colorh[3]', 'colorh[4]', 'double[2]', 'double[2][]', 'double[3]', 'double[3][]', 'double[4]', 'double[4][]', 'float[2]', 'float[2][]', 'float[3]', 'float[3][]', 'float[4]', 'float[4][]', 'frame[4]', 'half[2]', 'half[2][]', 'half[3]', 'half[3][]', 'half[4]', 'half[4][]', 'matrixd[2]', 'matrixd[2][]', 'matrixd[3]', 'matrixd[3][]', 'matrixd[4]', 'matrixd[4][]', 'normald[3]', 'normalf[3]', 'normalh[3]', 'pointd[3]', 'pointf[3]', 'pointh[3]', 'quatd[4]', 'quatf[4]', 'quath[4]', 'texcoordd[2]', 'texcoordd[3]', 'texcoordf[2]', 'texcoordf[3]', 'texcoordh[2]', 'texcoordh[3]', 'transform[4]', 'vectord[3]', 'vectorf[3]', 'vectorh[3]']``", "Second matrix or column vector to multiply as A*B", "None"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Product (*outputs:output*)", "``['colord[3]', 'colord[4]', 'colorf[3]', 'colorf[4]', 'colorh[3]', 'colorh[4]', 'double', 'double[2]', 'double[2][]', 'double[3]', 'double[3][]', 'double[4]', 'double[4][]', 'double[]', 'float', 'float[2]', 'float[2][]', 'float[3]', 'float[3][]', 'float[4]', 'float[4][]', 'float[]', 'frame[4]', 'half', 'half[2]', 'half[2][]', 'half[3]', 'half[3][]', 'half[4]', 'half[4][]', 'half[]', 'matrixd[2]', 'matrixd[2][]', 'matrixd[3]', 'matrixd[3][]', 'matrixd[4]', 'matrixd[4][]', 'normald[3]', 'normalf[3]', 'normalh[3]', 'pointd[3]', 'pointf[3]', 'pointh[3]', 'quatd[4]', 'quatf[4]', 'quath[4]', 'texcoordd[2]', 'texcoordd[3]', 'texcoordf[2]', 'texcoordf[3]', 'texcoordh[2]', 'texcoordh[3]', 'transform[4]', 'vectord[3]', 'vectorf[3]', 'vectorh[3]']``", "Product of the two matrices/vectors A*B", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.nodes.MatrixMultiply"
    "Version", "1"
    "Extension", "omni.graph.nodes_core"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Matrix Multiply"
    "Categories", "math:operator"
    "Generated Class Name", "OgnMatrixMultiplyDatabase"
    "Python Module", "omni.graph.nodes_core"

