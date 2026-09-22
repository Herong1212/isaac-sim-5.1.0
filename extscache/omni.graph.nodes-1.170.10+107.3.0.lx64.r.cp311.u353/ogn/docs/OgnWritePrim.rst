.. _omni_graph_nodes_WritePrim_4:

.. _omni_graph_nodes_WritePrim:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Write Prim Attributes
    :keywords: lang-en omnigraph node sceneGraph WriteOnly nodes write-prim


Write Prim Attributes
=====================

.. <description>

Exposes attributes for a single Prim on the USD stage as inputs to this node. When this node computes it writes any of these connected inputs to the target Prim. Any inputs which are not connected will not be written.

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
    "Prim (*inputs:prim*)", "``target``", "The prim to be written to", "None"
    "Persist To USD (*inputs:usdWriteBack*)", "``bool``", "Whether or not the value should be written back to USD, or kept a Fabric only value", "True"


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
    "Resolved Layer Identifier (*state:resolvedLayerIdentifier*)", "``token``", "The prefetched resolved layer Identifier.", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.nodes.WritePrim"
    "Version", "4"
    "Extension", "omni.graph.nodes"
    "Has State?", "True"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Write Prim Attributes"
    "Categories", "sceneGraph"
    "Generated Class Name", "OgnWritePrimDatabase"
    "Python Module", "omni.graph.nodes"

