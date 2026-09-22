.. _omni_graph_nodes_GetMatrix4Quaternion_2:

.. _omni_graph_nodes_GetMatrix4Quaternion:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Get Rotation Quaternion
    :keywords: lang-en omnigraph node math:operator threadsafe nodes get-matrix4-quaternion


Get Rotation Quaternion
=======================

.. <description>

Gets the rotation of the given matrix or rotation angles value which represents a linear transformation. Returns the quaternion orientation component.

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.nodes_core<ext_omni_graph_nodes_core>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Input (*inputs:matrix*)", "``['matrixd[3]', 'matrixd[3][]', 'matrixd[4]', 'matrixd[4][]', 'vectord[3]', 'vectord[3][]', 'vectorf[3]', 'vectorf[3][]', 'vectorh[3]', 'vectorh[3][]']``", "The matrix or rotation angles to extract the quaternion from.", "None"
    "Rotation Order (*inputs:rotationOrder*)", "``token``", "The order the rotation should be applied when using rotation angles.", "XYZ"
    "", "Metadata", "*allowedTokens* = XYZ,XZY,YXZ,YZX,ZXY,ZYX", ""


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Orientation (*outputs:quaternion*)", "``['quatd[4]', 'quatd[4][]', 'quatf[4]', 'quatf[4][]', 'quath[4]', 'quath[4][]']``", "The quaternion representing the orientation of the transformation.", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.nodes.GetMatrix4Quaternion"
    "Version", "2"
    "Extension", "omni.graph.nodes_core"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Get Rotation Quaternion"
    "Categories", "math:operator"
    "Generated Class Name", "OgnGetMatrix4QuaternionDatabase"
    "Python Module", "omni.graph.nodes_core"

