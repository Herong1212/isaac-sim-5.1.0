.. _omni_graph_nodes_ReadPrimMaterial_2:

.. _omni_graph_nodes_ReadPrimMaterial:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Read Prim Material
    :keywords: lang-en omnigraph node sceneGraph threadsafe ReadOnly nodes read-prim-material


Read Prim Material
==================

.. <description>

Given a path to a  prim on the current USD stage,  outputs the material of the prim.  Gives an error if the given prim  can not be found.

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.nodes<ext_omni_graph_nodes>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Prim (*inputs:prim*)", "``target``", "The prim with the material to be read. If both this and primPath inputs are set, this input takes priority.", "None"
    "Prim Path (*inputs:primPath*)", "``path``", "Path of the prim with the material to be read.", ""


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Material Path (*outputs:material*)", "``path``", "The material of the input prim", "None"
    "Material (*outputs:materialPrim*)", "``target``", "The prim containing the material of the input prim", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.nodes.ReadPrimMaterial"
    "Version", "2"
    "Extension", "omni.graph.nodes"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "tests"
    "uiName", "Read Prim Material"
    "Categories", "sceneGraph"
    "Generated Class Name", "OgnReadPrimMaterialDatabase"
    "Python Module", "omni.graph.nodes"

