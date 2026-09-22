.. _omni_graph_nodes_DeformedPointsToHydra_1:

.. _omni_graph_nodes_DeformedPointsToHydra:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Deformed Points to Hydra
    :keywords: lang-en omnigraph node examples,graph:preRender,internal nodes deformed-points-to-hydra


Deformed Points to Hydra
========================

.. <description>

Deprecated: please refer to the example node RpResourceExampleHydra instead

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.nodes<ext_omni_graph_nodes>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Prim Points (*inputs:points*)", "``float[3][]``", "Points attribute input. Points and a prim path may be supplied directly as an alternative to a bundle input.", "[]"
    "Prim path input (*inputs:primPath*)", "``token``", "Prim path input. Points and a prim path may be supplied directly as an alternative to a bundle input.", ""
    "Send to hydra (*inputs:sendToHydra*)", "``bool``", "send to hydra", "False"
    "stream (*inputs:stream*)", "``uint64``", "Pointer to the CUDA Stream", "0"
    "Verbose (*inputs:verbose*)", "``bool``", "verbose printing", "False"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Reload (*outputs:reload*)", "``bool``", "Force RpResource reload", "False"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.nodes.DeformedPointsToHydra"
    "Version", "1"
    "Extension", "omni.graph.nodes"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "hidden", "true"
    "uiName", "Deformed Points to Hydra"
    "Categories", "examples,graph:preRender,internal"
    "Generated Class Name", "OgnDeformedPointsToHydraDatabase"
    "Python Module", "omni.graph.nodes"

