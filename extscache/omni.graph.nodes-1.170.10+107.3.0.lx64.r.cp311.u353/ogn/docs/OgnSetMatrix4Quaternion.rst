.. _omni_graph_nodes_SetMatrix4Quaternion_1:

.. _omni_graph_nodes_SetMatrix4Quaternion:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Set Rotation Quaternion (Legacy)
    :keywords: lang-en omnigraph node math:operator threadsafe nodes set-matrix4-quaternion


Set Rotation Quaternion (Legacy)
================================

.. <description>

DEPRECATED - PLEASE USE SetMatrix4Rotation Sets the rotation of the given matrix4d value which represents a linear transformation. Does not modify the translation (row 3) of the matrix.

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.nodes<ext_omni_graph_nodes>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Matrix (*inputs:matrix*)", "``['matrixd[4]', 'matrixd[4][]']``", "The matrix to be modified", "None"
    "Quaternion (*inputs:quaternion*)", "``['quatd[4]', 'quatd[4][]']``", "The quaternion the matrix will apply about the given rotationAxis.", "None"


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

    "Unique ID", "omni.graph.nodes.SetMatrix4Quaternion"
    "Version", "1"
    "Extension", "omni.graph.nodes"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "hidden", "true"
    "uiName", "Set Rotation Quaternion (Legacy)"
    "Categories", "math:operator"
    "Generated Class Name", "OgnSetMatrix4QuaternionDatabase"
    "Python Module", "omni.graph.nodes"

