.. _omni_graph_nodes_GetLookAtRotation_1:

.. _omni_graph_nodes_GetLookAtRotation:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Get Look At Rotation
    :keywords: lang-en omnigraph node math:operator threadsafe nodes get-look-at-rotation


Get Look At Rotation
====================

.. <description>

Computes the rotation angles to align the 'Forward' direction vector to the vector formed by starting at 'From' and pointing at 'Target'. The 'Forward' vector is the current orientation of the Prim being rotated which usually starts at +X or +Z. The 'Up' vector defines the desired orientation of the rotation.

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.nodes_core<ext_omni_graph_nodes_core>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Forward (*inputs:forward*)", "``double[3]``", "The direction vector which is to be aligned", "[0.0, 0.0, 1.0]"
    "From (*inputs:start*)", "``pointd[3]``", "The position to look from", "[0.0, 0.0, 0.0]"
    "Target (*inputs:target*)", "``pointd[3]``", "The position to look at", "[0.0, 0.0, 0.0]"
    "Up (*inputs:up*)", "``double[3]``", "The direction of the up vector, if not specified USD scene-up will be used.", "None"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Orientation (*outputs:orientation*)", "``quatd[4]``", "The calculated orientation quaternion, which is equivalent to 'Rotation (XYZ)'", "None"
    "Rotation (XYZ) (*outputs:rotateXYZ*)", "``double[3]``", "The calculated rotation vector, as XYZ", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.nodes.GetLookAtRotation"
    "Version", "1"
    "Extension", "omni.graph.nodes_core"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Get Look At Rotation"
    "Categories", "math:operator"
    "Generated Class Name", "OgnGetLookAtRotationDatabase"
    "Python Module", "omni.graph.nodes_core"

