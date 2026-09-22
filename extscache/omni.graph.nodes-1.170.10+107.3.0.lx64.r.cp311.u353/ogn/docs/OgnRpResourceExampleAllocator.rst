.. _omni_graph_nodes_RpResourceExampleAllocator_1:

.. _omni_graph_nodes_RpResourceExampleAllocator:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: GPU Interop Example: RpResource Allocator
    :keywords: lang-en omnigraph node examples,graph:preRender nodes rp-resource-example-allocator


GPU Interop Example: RpResource Allocator
=========================================

.. <description>

Example node showing how to allocate a CUDA-interoperable RpResource in a pre-render graph.  The node allocates two new RpResources for the supplied prim which match the size of the array of points of the prim.  One RpResource can be used to deform and render the prim, without actually mutating the input prim,  while the other holds the original point values.

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.nodes<ext_omni_graph_nodes>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Prim Points (*inputs:points*)", "``float[3][]``", "The array of points of the input prim meshes.", "[]"
    "Prim Path (*inputs:primPath*)", "``token``", "The path of the prim for which we allocate a new RpResources.", ""
    "Reload (*inputs:reload*)", "``bool``", "Setting this to true will force the reallocation of the RpResource.  This should be used when changing the input prims.", "False"
    "Stream (*inputs:stream*)", "``uint64``", "The CUDA Stream used to order the CUDA commands scheduled by this graph execution.", "0"
    "Verbose (*inputs:verbose*)", "``bool``", "If true, the node will log detailed messages during the execution.  Can negatively impact performance.", "False"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Point Counts (*outputs:pointCountCollection*)", "``uint64[]``", "Point count for each prim being deformed. The size of the array is equal to the number of allocator nodes of this type found in the graph.", "None"
    "Prim Paths (*outputs:primPathCollection*)", "``token[]``", "Path for each prim for which a new RpResource was allocated.  The size of the array is equal to the number of allocator nodes of this type found in the graph.", "None"
    "Reload (*outputs:reload*)", "``bool``", "If true, the RpResources will be reallocated during the node compute.", "False"
    "Resource Pointer Collection (*outputs:resourcePointerCollection*)", "``uint64[]``", "Pointers to the allocated RpResources. Two resources are allocated per prim: one for the rest positions and one for deformed positions.", "None"
    "Stream (*outputs:stream*)", "``uint64``", "The CUDA Stream used to order the CUDA commands scheduled by this graph execution.", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.nodes.RpResourceExampleAllocator"
    "Version", "1"
    "Extension", "omni.graph.nodes"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "GPU Interop Example: RpResource Allocator"
    "Categories", "examples,graph:preRender"
    "Generated Class Name", "OgnRpResourceExampleAllocatorDatabase"
    "Python Module", "omni.graph.nodes"

