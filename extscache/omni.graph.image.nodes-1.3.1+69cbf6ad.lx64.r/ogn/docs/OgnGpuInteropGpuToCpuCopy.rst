.. _omni_graph_examples_cpp_GpuInteropGpuToCpuCopy_2:

.. _omni_graph_examples_cpp_GpuInteropGpuToCpuCopy:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: GPU Interop: Gpu To Cpu Copy
    :keywords: lang-en omnigraph node graph:postRender,rendering cpp gpu-interop-gpu-to-cpu-copy


GPU Interop: Gpu To Cpu Copy
============================

.. <description>

Generates a new AOV representing a CPU copy of a GPU buffer

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.image.nodes<ext_omni_graph_image_nodes>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "AOV GPU (*inputs:aovGpu*)", "``string``", "Name of the RenderVar to copy from GPU to CPU.  The RenderVar must be a valid texture on the RenderProduct, otherwise this node will not do anything.", ""
    "GPU Foundations (*inputs:gpu*)", "``uint64``", "The shared context containing GPU foundation interfaces.", "0"
    "Render Product (*inputs:rp*)", "``uint64``", "The render product for this view.", "0"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "AOV CPU (*outputs:aovCpu*)", "``string``", "The name of the RenderVar representing the CPU buffer of the GPU resource.  It is composed from the AOV GPU name with ""_host"" appended at the end.", ""
    "GPU Foundations (*outputs:gpu*)", "``uint64``", "The shared context containing GPU foundation interfaces.", "None"
    "Render Product (*outputs:rp*)", "``uint64``", "The render product for this view.", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.examples.cpp.GpuInteropGpuToCpuCopy"
    "Version", "2"
    "Extension", "omni.graph.image.nodes"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "GPU Interop: Gpu To Cpu Copy"
    "Categories", "graph:postRender,rendering"
    "Generated Class Name", "OgnGpuInteropGpuToCpuCopyDatabase"
    "Python Module", "omni.graph.image.nodes"

