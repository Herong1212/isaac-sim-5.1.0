.. _omni_graph_nodes_WritePrimRelationship_2:

.. _omni_graph_nodes_WritePrimRelationship:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Write Prim Relationship
    :keywords: lang-en omnigraph node sceneGraph WriteOnly nodes write-prim-relationship


Write Prim Relationship
=======================

.. <description>

Writes the target(s) to a relationship on a given prim

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
    "Layer Identifier (*inputs:layerIdentifier*)", "``token``", "Identifier of the USD layer to export data to. Identifier can be empty, ""<Session Layer>"", ""<Root Layer>"" or the identifier of a sublayer. If empty or invalid, data will be exported to the current layer. This is only used when ""Persist To USD"" is enabled.", ""
    "Relationship Name (*inputs:name*)", "``token``", "The name of the relationship to write", ""
    "Prim (*inputs:prim*)", "``target``", "The prim to write the relationship to", "None"
    "Persist To USD (*inputs:usdWriteBack*)", "``bool``", "Whether or not the value should be written back to USD, or kept a Fabric only value", "True"
    "Value (*inputs:value*)", "``target``", "The target(s) to write to the relationship", "None"
    "", "Metadata", "*allowMultiInputs* = 1", ""


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

    "Correctly Setup (*state:correctlySetup*)", "``bool``", "Whether or not the instance is properly setup", "False"
    "Layer Identifier (*state:layerIdentifier*)", "``token``", "The prefetched layer identifier.", "None"
    "Name (*state:name*)", "``token``", "The prefetched relationship name", "None"
    "Prim (*state:prim*)", "``target``", "The currently prefetched prim", "None"
    "Resolved Layer Identifier (*state:resolvedLayerIdentifier*)", "``token``", "The prefetched full layer path.", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.nodes.WritePrimRelationship"
    "Version", "2"
    "Extension", "omni.graph.nodes"
    "Has State?", "True"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "usd"
    "uiName", "Write Prim Relationship"
    "Categories", "sceneGraph"
    "Generated Class Name", "OgnWritePrimRelationshipDatabase"
    "Python Module", "omni.graph.nodes"

