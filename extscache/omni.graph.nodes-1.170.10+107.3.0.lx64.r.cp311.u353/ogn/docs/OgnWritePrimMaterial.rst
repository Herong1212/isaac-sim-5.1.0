.. _omni_graph_nodes_WritePrimMaterial_2:

.. _omni_graph_nodes_WritePrimMaterial:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Write Prim Material
    :keywords: lang-en omnigraph node sceneGraph WriteOnly nodes write-prim-material


Write Prim Material
===================

.. <description>

Given a path to a prim and a path to a material on the current USD stage,  assigns the material to the prim.  Gives an error if the given prim or material  can not be found.

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.nodes<ext_omni_graph_nodes>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Exec In (*inputs:execIn*)", "``execution``", "Signal to the graph that this node is ready to be executed.", "None"
    "Layer Identifier (*inputs:layerIdentifier*)", "``token``", "Identifier of the USD layer to export data to. Identifier can be empty, ""<Session Layer>"", ""<Root Layer>"" or the identifier of a sublayer. If empty or invalid, data will be exported to the current layer.", ""
    "Material (*inputs:material*)", "``target``", "The material to be assigned to the prim", "None"
    "Material Path (*inputs:materialPath*)", "``path``", "The path of the material to be assigned to the prim", ""
    "Prim (*inputs:prim*)", "``target``", "Prim to be assigned a material.", "None"
    "Prim Path (*inputs:primPath*)", "``path``", "Path of the prim to be assigned a material.", ""


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Exec Out (*outputs:execOut*)", "``execution``", "Signal to the graph that execution can continue downstream.", "None"


State
-----
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Layer Identifier (*state:layerIdentifier*)", "``token``", "The prefetched layer Identifier.", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.nodes.WritePrimMaterial"
    "Version", "2"
    "Extension", "omni.graph.nodes"
    "Has State?", "True"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "tests"
    "uiName", "Write Prim Material"
    "Categories", "sceneGraph"
    "Generated Class Name", "OgnWritePrimMaterialDatabase"
    "Python Module", "omni.graph.nodes"

