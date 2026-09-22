.. _omni_graph_nodes_SetMatrix4Rotation_2:

.. _omni_graph_nodes_SetMatrix4Rotation:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Set Rotation
    :keywords: lang-en omnigraph node math:operator threadsafe nodes set-matrix4-rotation


Set Rotation
============

.. <description>

Sets the rotation of the given matrix4d value which represents a linear transformation. Does not modify the translation (row 3) of the matrix. Accepts an angle/axis combination, Euler angles, quaternions or rotation matrices

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.nodes_core<ext_omni_graph_nodes_core>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Rotation Axis (*inputs:fixedRotationAxis*)", "``token``", "The axis of the given rotation", "Y"
    "", "Metadata", "*allowedTokens* = X,Y,Z,Custom", ""
    "Matrix (*inputs:matrix*)", "``['matrixd[4]', 'matrixd[4][]']``", "The matrix to be modified", "None"
    "Rotation (*inputs:rotationAngle*)", "``['double', 'double[]', 'matrixd[3]', 'matrixd[3][]', 'quatd[4]', 'quatd[4][]', 'vectord[3]', 'vectord[3][]']``", "The rotation to be applied to the matrix.  This can be a angle about an axis, euler angles,  quaternion or a rotation matrix.", "None"
    "Custom Rotation Axis (*inputs:rotationAxis*)", "``vectord[3]``", "The axis of rotation when fixedRotationAxis is set to Custom", "[0, 1, 0]"
    "Rotation Order (*inputs:rotationOrder*)", "``token``", "The order the rotation should be applied when using euler angles.", "XYZ"
    "", "Metadata", "*allowedTokens* = XYZ,XZY,YXZ,YZX,ZXY,ZYX", ""


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Matrix (*outputs:matrix*)", "``['matrixd[4]', 'matrixd[4][]']``", "The updated matrix", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.nodes.SetMatrix4Rotation"
    "Version", "2"
    "Extension", "omni.graph.nodes_core"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Set Rotation"
    "Categories", "math:operator"
    "Generated Class Name", "OgnSetMatrix4RotationDatabase"
    "Python Module", "omni.graph.nodes_core"

