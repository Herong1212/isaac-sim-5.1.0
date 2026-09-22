.. _omni_graph_nodes_GpuInteropCudaEntry_3:

.. _omni_graph_nodes_GpuInteropCudaEntry:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: GPU Interop: Cuda Entry
    :keywords: lang-en omnigraph node graph:postRender,rendering nodes gpu-interop-cuda-entry


GPU Interop: Cuda Entry
=======================

.. <description>

Entry node for post-processing hydra render results for a single view.  It outputs the properties of a RenderVar as attributes accessible to downstream nodes.  All downstream nodes are scheduled as CUDA commands.

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.image.nodes<ext_omni_graph_image_nodes>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Source Name (*inputs:sourceName*)", "``string``", "The name of the source RenderVar (AOV). The properties of this AOV are the output of this node.", "ldrColor"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Buffer Size (*outputs:bufferSize*)", "``uint``", "Size of the buffer, if the selected RenderVar is a buffer, otherwise it represents the texture depth.", "None"
    "RenderVar Data (*outputs:cudaMipmappedArray*)", "``uint64``", "The RenderVar data, which is represented as a CUDA Mipmapped Array.", "None"
    "External Time Of Simulation Frame (*outputs:externalTimeOfSimFrame*)", "``int64``", "The external time on the master node, matching the simulation frame used to render this frame.  It is only valid if the simulation and rendering are performed at the same, or different but constant rates.", "None"
    "Texture Format (*outputs:format*)", "``uint64``", "The texture format of the input image, matching the values of the enum carb::graphics::Format.  If the RenderVar is a buffer, the value is unknown.", "None"
    "Frame ID (*outputs:frameId*)", "``int64``", "The frame number.  It is only valid if the simulation and rendering are performed at the same, or different but constant rates.", "None"
    "Height (*outputs:height*)", "``uint``", "The width of the selected texture RenderVar.  If the RenderVar is an arbitrary buffer, it is 0.", "None"
    "Renderer Time (*outputs:hydraTime*)", "``double``", "The time difference since the last rendered frame.", "None"
    "Is Buffer (*outputs:isBuffer*)", "``bool``", "True if the entry exposes an arbitrary buffer RenderVar as opposed to a texture RenderVar.", "None"
    "Mip Count (*outputs:mipCount*)", "``uint``", "The number of levels of detail encoded in 'RenderVar Data'. If the RenderVar is not a texture, the value is 0.", "None"
    "Rational Time Of Sim Denominator (*outputs:rationalTimeOfSimDenominator*)", "``uint64``", "The denominator of the simulation time expressed as rational time.  It is always valid and may be used to fetch data from Fabric during the node compute.", "None"
    "Rational Time Of Sim Numerator (*outputs:rationalTimeOfSimNumerator*)", "``int64``", "The numerator of the simulation time expressed as rational time.  It is always valid and may be used to fetch data from Fabric during the node compute.", "None"
    "Simulation Time (*outputs:simTime*)", "``double``", "The time difference since the last simulation frame. May suffer from loss of precision and cannot be used as a deterministic identifier,  for example for fetching data from Fabric during the node compute -  use the Rational Time instead in that case.", "None"
    "Stream (*outputs:stream*)", "``uint64``", "The CUDA Stream used to order the CUDA commands scheduled by this graph execution.", "None"
    "Width (*outputs:width*)", "``uint``", "The width of the selected texture RenderVar.  If the RenderVar is an arbitrary buffer, it is 0.", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.nodes.GpuInteropCudaEntry"
    "Version", "3"
    "Extension", "omni.graph.image.nodes"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "GPU Interop: Cuda Entry"
    "Categories", "graph:postRender,rendering"
    "Generated Class Name", "OgnGpuInteropCudaEntryDatabase"
    "Python Module", "omni.graph.image.nodes"

