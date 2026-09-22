.. _omni_graph_nodes_GetMatrix4Rotation_2:

.. _omni_graph_nodes_GetMatrix4Rotation:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Get Rotation
    :keywords: lang-en omnigraph node math:operator threadsafe nodes get-matrix4-rotation


Get Rotation
============

.. <description>

Gets the rotation of the given matrix3d, matrix4d or quaternion value which represents a linear transformation. Returns the vector3 rotation in the given rotation order

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.nodes_core<ext_omni_graph_nodes_core>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Input (*inputs:matrix*)", "``['matrixd[3]', 'matrixd[3][]', 'matrixd[4]', 'matrixd[4][]', 'quatd[4]', 'quatd[4][]', 'quatf[4]', 'quatf[4][]', 'quath[4]', 'quath[4][]']``", "The matrix or quaternion to extract the rotation from.", "None"
    "Rotation Order (*inputs:rotationOrder*)", "``token``", "The order of the output rotation angles.", "XYZ"
    "", "Metadata", "*allowedTokens* = XYZ,XZY,YXZ,YZX,ZXY,ZYX", ""


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Rotation (*outputs:rotation*)", "``['vectord[3]', 'vectord[3][]', 'vectorf[3]', 'vectorf[3][]', 'vectorh[3]', 'vectorh[3][]']``", "The vector representing the rotation of the transformation.", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.nodes.GetMatrix4Rotation"
    "Version", "2"
    "Extension", "omni.graph.nodes_core"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Get Rotation"
    "Categories", "math:operator"
    "Generated Class Name", "OgnGetMatrix4RotationDatabase"
    "Python Module", "omni.graph.nodes_core"

