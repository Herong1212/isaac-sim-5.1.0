.. _omni_graph_nodes_SetMatrix4Translation_1:

.. _omni_graph_nodes_SetMatrix4Translation:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Set Translation
    :keywords: lang-en omnigraph node math:operator threadsafe nodes set-matrix4-translation


Set Translation
===============

.. <description>

Sets the translation of the given matrix value which represents a linear transformation. Does not modify the orientation (row 0-2) of the matrix.

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.nodes_core<ext_omni_graph_nodes_core>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Matrix (*inputs:matrix*)", "``['matrixd[4]', 'matrixd[4][]']``", "The matrix to be modified", "None"
    "Translation (*inputs:translation*)", "``['vectord[3]', 'vectord[3][]']``", "The translation that the matrix will apply", "None"


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

    "Unique ID", "omni.graph.nodes.SetMatrix4Translation"
    "Version", "1"
    "Extension", "omni.graph.nodes_core"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Set Translation"
    "Categories", "math:operator"
    "Generated Class Name", "OgnSetMatrix4TranslationDatabase"
    "Python Module", "omni.graph.nodes_core"

