.. _omni_graph_nodes_MakeTransformLookAt_1:

.. _omni_graph_nodes_MakeTransformLookAt:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Make Transformation Matrix Look At
    :keywords: lang-en omnigraph node math:operator threadsafe nodes make-transform-look-at


Make Transformation Matrix Look At
==================================

.. <description>

Make a transformation matrix from eye and center world-space positions and an up vector. Forward vector is negative Z direction computed from (eye - center) and normalized. Up is positive Y direction. Right is the positive X direction.

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.nodes<ext_omni_graph_nodes>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Center (*inputs:center*)", "``vectord[3]``", "The position of the center or target-position in world-space", "[0, 0, 0]"
    "Eye (*inputs:eye*)", "``vectord[3]``", "The position of the eye, or from-position in world-space", "[1, 0, 0]"
    "Up (*inputs:up*)", "``vectord[3]``", "The direction of the up vector", "[0, 1, 0]"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Transform (*outputs:transform*)", "``matrixd[4]``", "The calculated transformation matrix", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.nodes.MakeTransformLookAt"
    "Version", "1"
    "Extension", "omni.graph.nodes"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Make Transformation Matrix Look At"
    "Categories", "math:operator"
    "Generated Class Name", "OgnMakeTransformLookAtDatabase"
    "Python Module", "omni.graph.nodes"

