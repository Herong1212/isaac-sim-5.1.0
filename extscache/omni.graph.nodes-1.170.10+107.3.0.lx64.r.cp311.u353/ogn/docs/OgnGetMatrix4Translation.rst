.. _omni_graph_nodes_GetMatrix4Translation_1:

.. _omni_graph_nodes_GetMatrix4Translation:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Get Translation
    :keywords: lang-en omnigraph node math:operator threadsafe nodes get-matrix4-translation


Get Translation
===============

.. <description>

Gets the translation of the given matrix4d value which represents a linear transformation. Returns the vector3 translation component

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.nodes<ext_omni_graph_nodes>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Transform (*inputs:matrix*)", "``['matrixd[4]', 'matrixd[4][]']``", "The matrix to extract the translate from.", "None"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Translation (*outputs:translation*)", "``['vectord[3]', 'vectord[3][]']``", "The vector that represents the translation of the transformation.", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.nodes.GetMatrix4Translation"
    "Version", "1"
    "Extension", "omni.graph.nodes"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Get Translation"
    "Categories", "math:operator"
    "Generated Class Name", "OgnGetMatrix4TranslationDatabase"
    "Python Module", "omni.graph.nodes"

