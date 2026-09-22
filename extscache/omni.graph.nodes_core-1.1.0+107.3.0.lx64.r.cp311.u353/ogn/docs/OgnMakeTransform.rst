.. _omni_graph_nodes_MakeTransform_2:

.. _omni_graph_nodes_MakeTransform:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Make Transformation Matrix from TRS
    :keywords: lang-en omnigraph node math:operator threadsafe nodes make-transform


Make Transformation Matrix from TRS
===================================

.. <description>

Make a transformation matrix that performs a translation, rotation (in euler angles), and scale in that order

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.nodes_core<ext_omni_graph_nodes_core>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Rotation Order (*inputs:rotationOrder*)", "``token``", "The order the rotation should be applied", "XYZ"
    "", "Metadata", "*allowedTokens* = XYZ,XZY,YXZ,YZX,ZXY,ZYX", ""
    "Rotation (*inputs:rotationXYZ*)", "``vectord[3]``", "The desired orientation in euler angles XYZ", "[0, 0, 0]"
    "Scale (*inputs:scale*)", "``vectord[3]``", "The desired scaling factor about the X, Y, and Z axis respectively", "[1, 1, 1]"
    "Translation (*inputs:translation*)", "``vectord[3]``", "The desired translation as a vector", "[0, 0, 0]"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Transform (*outputs:transform*)", "``matrixd[4]``", "The computed transformation matrix", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.nodes.MakeTransform"
    "Version", "2"
    "Extension", "omni.graph.nodes_core"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Make Transformation Matrix from TRS"
    "Categories", "math:operator"
    "Generated Class Name", "OgnMakeTransformDatabase"
    "Python Module", "omni.graph.nodes_core"

