.. _omni_graph_nodes_BlendVariants_2:

.. _omni_graph_nodes_BlendVariants:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Blend Variants
    :keywords: lang-en omnigraph node graph:action,sceneGraph,variants ReadOnly nodes blend-variants


Blend Variants
==============

.. <description>

Add new variant by blending two variants

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.nodes<ext_omni_graph_nodes>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Blend (*inputs:blend*)", "``double``", "The blend value in [0.0, 1.0]", "0.0"
    "Exec In (*inputs:execIn*)", "``execution``", "Signal to the graph that this node is ready to be executed.", "None"
    "Layer Identifier (*inputs:layerIdentifier*)", "``token``", "Identifier of the USD layer to export data to. Identifier can be empty, ""<Session Layer>"", ""<Root Layer>"" or the identifier of a sublayer. If empty or invalid, data will be exported to the current layer.", ""
    "Prim (*inputs:prim*)", "``target``", "The prim with the variantSet", "None"
    "Set Variant (*inputs:setVariant*)", "``bool``", "Sets the variant selection when finished rather than writing to the attribute values", "False"
    "Variant Name A (*inputs:variantNameA*)", "``token``", "The first variant name", ""
    "Variant Name B (*inputs:variantNameB*)", "``token``", "The second variant name", ""
    "Variant Set Name (*inputs:variantSetName*)", "``token``", "The variantSet name", ""


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Bundle (*outputs:bundle*)", "``bundle``", "Output bundle with blended attributes", "None"
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

    "Unique ID", "omni.graph.nodes.BlendVariants"
    "Version", "2"
    "Extension", "omni.graph.nodes"
    "Icon", "ogn/icons/omni.graph.nodes.BlendVariants.svg"
    "Has State?", "True"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Blend Variants"
    "Categories", "graph:action,sceneGraph,variants"
    "Generated Class Name", "OgnBlendVariantsDatabase"
    "Python Module", "omni.graph.nodes"

