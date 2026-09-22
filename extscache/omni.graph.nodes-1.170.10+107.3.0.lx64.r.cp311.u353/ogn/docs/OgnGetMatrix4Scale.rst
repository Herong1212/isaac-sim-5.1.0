.. _omni_graph_nodes_GetMatrix4Scale_1:

.. _omni_graph_nodes_GetMatrix4Scale:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Get Scale
    :keywords: lang-en omnigraph node math:operator threadsafe nodes get-matrix4-scale


Get Scale
=========

.. <description>

Gets the scale of the given matrix3d or matrix4d value which represents a linear transformation. Returns the vector3 scale component.

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.nodes<ext_omni_graph_nodes>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Transform (*inputs:matrix*)", "``['matrixd[3]', 'matrixd[3][]', 'matrixd[4]', 'matrixd[4][]']``", "The matrix to extract the scale from.", "None"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Scale (*outputs:scale*)", "``['vectord[3]', 'vectord[3][]']``", "The vector that represents the scale of the transformation.", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.nodes.GetMatrix4Scale"
    "Version", "1"
    "Extension", "omni.graph.nodes"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Get Scale"
    "Categories", "math:operator"
    "Generated Class Name", "OgnGetMatrix4ScaleDatabase"
    "Python Module", "omni.graph.nodes"

