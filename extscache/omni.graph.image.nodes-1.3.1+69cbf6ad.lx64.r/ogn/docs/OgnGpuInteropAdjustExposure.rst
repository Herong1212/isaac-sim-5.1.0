.. _omni_graph_examples_cpp_GpuInteropAdjustExposure_2:

.. _omni_graph_examples_cpp_GpuInteropAdjustExposure:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: GPU Interop Example: Adjust Render Exposure
    :keywords: lang-en omnigraph node examples,graph:postRender,rendering cpp gpu-interop-adjust-exposure


GPU Interop Example: Adjust Render Exposure
===========================================

.. <description>

RTX Renderer Postprocess Example: adjust the exposure of the rendered image. The node can be used in a post-render graph to change the brightness of the rendered image. As a CUDA interop node, the node is scheduled for execution as a CUDA command. If the input RenderVar is not a valid texture, the node does not produce a result.

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.image.nodes<ext_omni_graph_image_nodes>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "RenderVar Data (*inputs:cudaMipmappedArray*)", "``uint64``", "The RenderVar data, defined as a CUDA Mipmapped Array.", "0"
    "Exposure (*inputs:exposure*)", "``float``", "Exposure value (in stops). Positive values increase the brightness of the image, while negative values result in darker images.  The default exposure value of 0 results in an unmodified image.  Increasing the value by one unit, results in a doubling of the exposure and a brigher image;  decreasing the value by one unit results in a halving of the exposure, thus a darker image. ", "0"
    "Texture Format (*inputs:format*)", "``uint64``", "The texture format of the input image, matching the values of the enum carb::graphics::Format.", "0"
    "Height (*inputs:height*)", "``uint``", "The height of the input image.", "0"
    "Renderer Time (*inputs:hydraTime*)", "``double``", "The delta time of the renderer in stage.", "0.0"
    "Mip Count (*inputs:mipCount*)", "``uint``", "The number of levels of detail encoded in 'RenderVar Data'.", "0"
    "Simulation Time (*inputs:simTime*)", "``double``", "The delta time of the simulation.", "0.0"
    "Stream (*inputs:stream*)", "``uint64``", "The CUDA Stream used to order the CUDA commands scheduled by this graph execution.", "0"
    "Width (*inputs:width*)", "``uint``", "The width of the input image.", "0"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.examples.cpp.GpuInteropAdjustExposure"
    "Version", "2"
    "Extension", "omni.graph.image.nodes"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "GPU Interop Example: Adjust Render Exposure"
    "Categories", "examples,graph:postRender,rendering"
    "Generated Class Name", "OgnGpuInteropAdjustExposureDatabase"
    "Python Module", "omni.graph.image.nodes"

