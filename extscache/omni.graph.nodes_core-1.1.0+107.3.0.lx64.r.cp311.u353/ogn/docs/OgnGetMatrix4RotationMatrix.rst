.. _omni_graph_nodes_GetMatrix4RotationMatrix_1:

.. _omni_graph_nodes_GetMatrix4RotationMatrix:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Get Rotation Matrix
    :keywords: lang-en omnigraph node math:operator threadsafe nodes get-matrix4-rotation-matrix


Get Rotation Matrix
===================

.. <description>

Gets the rotation matrix of the given matrix4d, rotation angles or quaternion value which represents a linear transformation. Returns the matrix3d rotation matrix.

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.nodes_core<ext_omni_graph_nodes_core>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Input (*inputs:matrix*)", "``['matrixd[4]', 'matrixd[4][]', 'quatd[4]', 'quatd[4][]', 'vectord[3]', 'vectord[3][]']``", "The matrix, rotation angles or quaternion to extract the rotation from.", "None"
    "Rotation Order (*inputs:rotationOrder*)", "``token``", "The order the rotation should be applied when using rotation angles.", "XYZ"
    "", "Metadata", "*allowedTokens* = XYZ,XZY,YXZ,YZX,ZXY,ZYX", ""


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Rotation (*outputs:rotation*)", "``['matrixd[3]', 'matrixd[3][]']``", "The matrix representing the rotation of the transformation.", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.nodes.GetMatrix4RotationMatrix"
    "Version", "1"
    "Extension", "omni.graph.nodes_core"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Get Rotation Matrix"
    "Categories", "math:operator"
    "Generated Class Name", "OgnGetMatrix4RotationMatrixDatabase"
    "Python Module", "omni.graph.nodes_core"

