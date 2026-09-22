.. _omni_graph_nodes_SetMatrix4Scale_1:

.. _omni_graph_nodes_SetMatrix4Scale:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Set Scale
    :keywords: lang-en omnigraph node math:operator threadsafe nodes set-matrix4-scale


Set Scale
=========

.. <description>

Sets the scale of the given matrix value which represents a linear transformation. Does not modify the orientation (row 0-2) of the matrix.

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.nodes_core<ext_omni_graph_nodes_core>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Matrix (*inputs:matrix*)", "``['matrixd[3]', 'matrixd[3][]', 'matrixd[4]', 'matrixd[4][]']``", "The matrix to be modified", "None"
    "Scale (*inputs:scale*)", "``['vectord[3]', 'vectord[3][]']``", "The scale that the matrix will apply", "None"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Matrix (*outputs:matrix*)", "``['matrixd[3]', 'matrixd[3][]', 'matrixd[4]', 'matrixd[4][]']``", "The updated matrix", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.nodes.SetMatrix4Scale"
    "Version", "1"
    "Extension", "omni.graph.nodes_core"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Set Scale"
    "Categories", "math:operator"
    "Generated Class Name", "OgnSetMatrix4ScaleDatabase"
    "Python Module", "omni.graph.nodes_core"

