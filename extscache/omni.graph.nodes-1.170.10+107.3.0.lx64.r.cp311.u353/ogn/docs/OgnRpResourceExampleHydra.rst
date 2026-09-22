.. _omni_graph_nodes_RpResourceExampleHydra_1:

.. _omni_graph_nodes_RpResourceExampleHydra:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: GPU Interop Example: RpResource to Hydra
    :keywords: lang-en omnigraph node examples,graph:preRender nodes rp-resource-example-hydra


GPU Interop Example: RpResource to Hydra
========================================

.. <description>

Example Node: Send RpResource to Hydra for rendering.  The node is meant to be used together with OgnRpResourceAllocator and OgnRpResourceDeformer.  For each deformed prim, it is assumed that we have two sets of points to send to hydra for rendering:  one set contains the original positions points of the deformed prims, the second contains the points after the  deformation operation is applied.

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.nodes<ext_omni_graph_nodes>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Point Counts (*inputs:pointCountCollection*)", "``uint64[]``", "Point count for each prim being deformed.  Should match the size of the arrays in the 'Resource Pointer Collection'.", "[]"
    "Prim Paths (*inputs:primPathCollection*)", "``token[]``", "Path for each prim being deformed. Used for input validation during the node computation.", "[]"
    "Resource Pointer Collection (*inputs:resourcePointerCollection*)", "``uint64[]``", "Pointers to RpResources  (two resources per prim are assumed -- one for rest positions and one for deformed positions)", "[]"
    "Send to Hydra (*inputs:sendToHydra*)", "``bool``", "Send the RpResource to hydra using the specified prim path. If set to false,  the node can be used simply as a debug node for the RpResource, if verbose is set to true.", "False"
    "Verbose (*inputs:verbose*)", "``bool``", "If true, the node will log detailed information about the data sent to hydra during the execution.  Can negatively impact performance.", "False"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.nodes.RpResourceExampleHydra"
    "Version", "1"
    "Extension", "omni.graph.nodes"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "GPU Interop Example: RpResource to Hydra"
    "__tokens", "{""points"": ""points"", ""transform"": ""transform"", ""rpResource"": ""rpResource"", ""pointCount"": ""pointCount"", ""uintData"": ""uintData""}"
    "Categories", "examples,graph:preRender"
    "Generated Class Name", "OgnRpResourceExampleHydraDatabase"
    "Python Module", "omni.graph.nodes"

