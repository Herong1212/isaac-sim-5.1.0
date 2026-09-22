.. _omni_graph_nodes_SetVariantSelection_3:

.. _omni_graph_nodes_SetVariantSelection:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Set Variant Selection
    :keywords: lang-en omnigraph node graph:action,sceneGraph,variants WriteOnly nodes set-variant-selection


Set Variant Selection
=====================

.. <description>

Set the variant selection on a prim

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
    "Prim (*inputs:prim*)", "``target``", "The prim with the variantSet", "None"
    "Set Variant (*inputs:setVariant*)", "``bool``", "Sets the variant selection when finished rather than writing to the attribute values", "False"
    "Variant Name (*inputs:variantName*)", "``token``", "The variant name", ""
    "Variant Set Name (*inputs:variantSetName*)", "``token``", "The variantSet name", ""


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

    "Layer Identifier (*state:layerIdentifier*)", "``token``", "The prefetched layer identifier.", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.nodes.SetVariantSelection"
    "Version", "3"
    "Extension", "omni.graph.nodes"
    "Icon", "ogn/icons/omni.graph.nodes.SetVariantSelection.svg"
    "Has State?", "True"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Set Variant Selection"
    "Categories", "graph:action,sceneGraph,variants"
    "Generated Class Name", "OgnSetVariantSelectionDatabase"
    "Python Module", "omni.graph.nodes"

