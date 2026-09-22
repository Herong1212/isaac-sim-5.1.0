.. _omni_graph_nodes_RpResourceExampleDeformer_1:

.. _omni_graph_nodes_RpResourceExampleDeformer:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: GPU Interop Example: RpResource Deformer
    :keywords: lang-en omnigraph node examples,graph:preRender nodes rp-resource-example-deformer


GPU Interop Example: RpResource Deformer
========================================

.. <description>

Example node showcasing the deformation of a set of prims in a pre-render graph. The node is meant to be used together with RpResourceExampleAllocator and RpResourceExampleHydra.  The deformation function translates the input points on a sinusoidal path against the z axis.

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.nodes<ext_omni_graph_nodes>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Deform Scale (*inputs:deformScale*)", "``float``", "Multiplier used to control the scale of the deformation.  Incresing the value beyond 1 will increase the offset between the position at rest  and the deformed position, for a given deformation.  Negative values will flip the point posion agains the displacement axis.", "1.0"
    "Point Counts (*inputs:pointCountCollection*)", "``uint64[]``", "Point count for each prim being deformed. The size of the array is equal to the number prims being deformed.", "[]"
    "Position Scale (*inputs:positionScale*)", "``float``", "Determines the offset applied on the deformed points in each iteration of the node compute. Larger values will result in a more pronounced deformation over multiple frames.", "1.0"
    "Prim Paths (*inputs:primPathCollection*)", "``token[]``", "The paths of the prims being deformed.", "[]"
    "Resource Pointer Collection (*inputs:resourcePointerCollection*)", "``uint64[]``", "Pointers to the allocated RpResources. Two resources are expected per prim: one for the rest positions and one for deformed positions.", "[]"
    "Run Deformer (*inputs:runDeformerKernel*)", "``bool``", "If true, performs the deformation of the prims.  Can be toggled off to stop the deformation at an arbitrary point in time.", "True"
    "Simulation Frame Time (*inputs:simTime*)", "``double``", "The time difference since the last simulation frame. May suffer from loss of precision and cannot be used as a deterministic identifier,  for example for fetching data from Fabric during the node compute.", "0.0"
    "Stream (*inputs:stream*)", "``uint64``", "The CUDA Stream used to order the CUDA commands scheduled by this graph execution.", "0"
    "Time Scale (*inputs:timeScale*)", "``float``", "Determines the offset applied on the deformed points in each iteration of the node compute. Larger values will result in a more pronounced deformation over multiple frames.", "0.01"
    "Verbose (*inputs:verbose*)", "``bool``", "If true, the node will log detailed messages during the execution.  Can negatively impact performance.", "False"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Point Counts (*outputs:pointCountCollection*)", "``uint64[]``", "Point count for each prim being deformed. The size of the array is equal to the number prims being deformed.", "None"
    "Prim Paths (*outputs:primPathCollection*)", "``token[]``", "The paths of the prims being deformed.", "None"
    "Resource Pointer Collection (*outputs:resourcePointerCollection*)", "``uint64[]``", "Pointers to the allocated RpResources. Two resources are expected per prim: one for the rest positions and one for deformed positions.", "None"
    "Stream (*outputs:stream*)", "``uint64``", "The CUDA Stream used to order the CUDA commands scheduled by this graph execution.", "None"


State
-----
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Sequence Counter (*state:sequenceCounter*)", "``double``", "Represents the time T of the deformation computation.  Stores the number of frames since the start of the deformation if the 'Simulation Frame Time' attribute is 0.  If the 'Simulation Frame Time' attribute is not 0, the value of this state attribute is equal to the simulation time. ", "0"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.nodes.RpResourceExampleDeformer"
    "Version", "1"
    "Extension", "omni.graph.nodes"
    "Has State?", "True"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "GPU Interop Example: RpResource Deformer"
    "__tokens", "{""points"": ""points"", ""transform"": ""transform"", ""rpResource"": ""rpResource"", ""pointCount"": ""pointCount"", ""primPath"": ""primPath"", ""testToken"": ""testToken"", ""uintData"": ""uintData""}"
    "Categories", "examples,graph:preRender"
    "Generated Class Name", "OgnRpResourceExampleDeformerDatabase"
    "Python Module", "omni.graph.nodes"

