.. _omni_graph_nodes_GetPrimDirectionVector_2:

.. _omni_graph_nodes_GetPrimDirectionVector:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Get Prim Direction Vector
    :keywords: lang-en omnigraph node sceneGraph threadsafe ReadOnly nodes get-prim-direction-vector


Get Prim Direction Vector
=========================

.. <description>

Given a prim, find its direction vectors (up vector, forward vector, right vector, etc.)

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.nodes<ext_omni_graph_nodes>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Prim (*inputs:prim*)", "``target``", "The connection to the input prim - this attribute is used when 'usePath' is false", "None"
    "Prim Path (*inputs:primPath*)", "``token``", "The path of the input prim - this attribute is used when 'usePath' is true", ""
    "Use Path (*inputs:usePath*)", "``bool``", "When true, it will use the 'primPath' attribute as the path to the prim, otherwise it will read the connection at the 'prim' attribute", "True"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Backward Vector (*outputs:backwardVector*)", "``double[3]``", "The backward vector of the prim", "None"
    "Down Vector (*outputs:downVector*)", "``double[3]``", "The down vector of the prim", "None"
    "Forward Vector (*outputs:forwardVector*)", "``double[3]``", "The forward vector of the prim", "None"
    "Left Vector (*outputs:leftVector*)", "``double[3]``", "The left vector of the prim", "None"
    "Right Vector (*outputs:rightVector*)", "``double[3]``", "The right vector of the prim", "None"
    "Up Vector (*outputs:upVector*)", "``double[3]``", "The up vector of the prim", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.nodes.GetPrimDirectionVector"
    "Version", "2"
    "Extension", "omni.graph.nodes"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Get Prim Direction Vector"
    "Categories", "sceneGraph"
    "Generated Class Name", "OgnGetPrimDirectionVectorDatabase"
    "Python Module", "omni.graph.nodes"

