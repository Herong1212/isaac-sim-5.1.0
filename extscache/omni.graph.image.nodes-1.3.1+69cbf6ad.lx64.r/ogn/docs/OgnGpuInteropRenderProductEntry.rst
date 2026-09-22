.. _omni_graph_nodes_GpuInteropRenderProductEntry_2:

.. _omni_graph_nodes_GpuInteropRenderProductEntry:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: GPU Interop: Render Product Entry
    :keywords: lang-en omnigraph node internal,graph:postRender,rendering nodes gpu-interop-render-product-entry


GPU Interop: Render Product Entry
=================================

.. <description>

Entry node for post-processing hydra render results for a single view.  Gives direct access to the RenderProduct and GPU interfaces.

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.image.nodes<ext_omni_graph_image_nodes>` in the Extension Manager.


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Exec (*outputs:exec*)", "``execution``", "Trigger for scheduling dependencies.", "None"
    "GPU Foundations (*outputs:gpu*)", "``uint64``", "The shared context containing GPU foundation interfaces.", "None"
    "Renderer Time (*outputs:hydraTime*)", "``double``", "The time difference since the last rendered frame.", "None"
    "Render Product (*outputs:rp*)", "``uint64``", "The to render product for this view.", "None"
    "Simulation Time (*outputs:simTime*)", "``double``", "The time difference since the last simulation frame. May suffer from loss of precision and cannot be used as a deterministic identifier,  for example for fetching data from Fabric during the node compute.", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.nodes.GpuInteropRenderProductEntry"
    "Version", "2"
    "Extension", "omni.graph.image.nodes"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "hidden", "true"
    "uiName", "GPU Interop: Render Product Entry"
    "Categories", "internal,graph:postRender,rendering"
    "Generated Class Name", "OgnGpuInteropRenderProductEntryDatabase"
    "Python Module", "omni.graph.image.nodes"

