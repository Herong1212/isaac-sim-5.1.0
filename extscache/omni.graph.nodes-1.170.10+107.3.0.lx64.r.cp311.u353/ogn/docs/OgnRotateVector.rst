.. _omni_graph_nodes_RotateVector_1:

.. _omni_graph_nodes_RotateVector:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Rotate Vector
    :keywords: lang-en omnigraph node math:operator threadsafe nodes rotate-vector


Rotate Vector
=============

.. <description>

Rotates a 3d direction vector by a specified rotation. Accepts 3x3 matrices, 4x4 matrices, euler angles (XYZ), or quaternions For 4x4 matrices, the transformation information in the matrix is ignored and the vector is treated as a 4-component vector where the fourth component is zero. The result is then projected back to a 3-vector. Supports mixed array inputs, e.g. a single quaternion and an array of vectors (in which case the quaternion would be applied to each vector in the array).

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.nodes<ext_omni_graph_nodes>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Rotation (*inputs:rotation*)", "``['matrixd[3]', 'matrixd[3][]', 'matrixd[4]', 'matrixd[4][]', 'quatd[4]', 'quatd[4][]', 'quatf[4]', 'quatf[4][]', 'quath[4]', 'quath[4][]', 'vectord[3]', 'vectord[3][]', 'vectorf[3]', 'vectorf[3][]', 'vectorh[3]', 'vectorh[3][]']``", "The rotation to be applied, either in the form of matrices, euler angles, or quaternions. If this input is an array, then the size of that array should match the size of the ""Vector"" array (or only contain a single element), otherwise the node will be unable to perform the computation. For 4x4 matrices, the transformation information in the matrix will be ignored.", "None"
    "Rotation Order (*inputs:rotationOrder*)", "``token``", "The order the rotation should be applied when using euler angles.", "XYZ"
    "", "Metadata", "*allowedTokens* = XYZ,XZY,YXZ,YZX,ZXY,ZYX", ""
    "Vector (*inputs:vector*)", "``['vectord[3]', 'vectord[3][]', 'vectorf[3]', 'vectorf[3][]', 'vectorh[3]', 'vectorh[3][]']``", "The three-dimensional row vector (or array of row vectors) to be rotated.", "None"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Result (*outputs:result*)", "``['vectord[3]', 'vectord[3][]', 'vectorf[3]', 'vectorf[3][]', 'vectorh[3]', 'vectorh[3][]']``", "The transformed three-dimensional row vector (or array of row vectors). This output will have the same shape as the input ""Vector"" attribute.", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.nodes.RotateVector"
    "Version", "1"
    "Extension", "omni.graph.nodes"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Rotate Vector"
    "Categories", "math:operator"
    "Generated Class Name", "OgnRotateVectorDatabase"
    "Python Module", "omni.graph.nodes"

