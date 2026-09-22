.. _omni_graph_examples_cpp_GpuInteropCpuToDisk_2:

.. _omni_graph_examples_cpp_GpuInteropCpuToDisk:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: GPU Interop: Cpu To Disk
    :keywords: lang-en omnigraph node graph:postRender,rendering cpp gpu-interop-cpu-to-disk


GPU Interop: Cpu To Disk
========================

.. <description>

Saves the specified CPU buffer to disk.  The node assumes that the RenderVar (AOV) has already been copied to the host (CPU) memory.

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.image.nodes<ext_omni_graph_image_nodes>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Active Reset (*inputs:active*)", "``bool``", "If true, the node computes once, then resets to false.  It is useful to use in runtime scripts or tests, where a single frame should be captured at a time.", "False"
    "AOV CPU (*inputs:aovCpu*)", "``string``", "Name of AOV representing the CPU buffer of GPU resource.  It is assumed that the CPU RenderVar is a copy of the GPU data. If the CPU AOV is invalid, the node does not output anything.", ""
    "AOV GPU (*inputs:aovGpu*)", "``string``", "Name of AOV representing the GPU resource, used for querying format and properties.", ""
    "Auto File Number (*inputs:autoFileNumber*)", "``int``", "If non zero, this number will be the starting number for export. Each invocation of this node increases the number by 1.", "-1"
    "File Name (*inputs:fileName*)", "``string``", "Optional, name given to the output file. If specified the output filename will be 'File Name_{aovGpu}.{fileType}'.", ""
    "File Number (*inputs:fileNumber*)", "``int``", "Number that will be appended to the exported filename. If -1 then the render product's frame number will be used.", "-1"
    "File Type (*inputs:fileType*)", "``string``", "The file type of the saved images. The valid types are bmp, png and exr.", "png"
    "Frame Count (*inputs:frameCount*)", "``int64``", "Number of frames to capture. If set to -1, the node execution never stops.", "-1"
    "GPU Foundations (*inputs:gpu*)", "``uint64``", "The shared context containing GPU foundation interfaces.", "0"
    "Max Concurrent Writes (*inputs:maxInflightWrites*)", "``int``", "Specifies the maximum allowed concurrent asynchronous file write operations dispatched by the node,  preventing potential blocking on file I/O for the Render thread.  This attribute controls the number of writes before waiting to dispatch a new I/O command. If the number of concurrent writes is reached, the Render Thread waits for the existing write commands to complete  before dispatching new commands.", "2"
    "Render Product (*inputs:rp*)", "``uint64``", "The render product for this view.", "0"
    "Save Flags (*inputs:saveFlags*)", "``uint64``", "Flags that will be passed to carb::imaging::IImaging for file saving.", "0"
    "Save Location (*inputs:saveLocation*)", "``string``", "The path to save AOVs as AOV_FrameNumber.{exr,png}", ""
    "Skip Inactive Nodes (*inputs:skipInactive*)", "``bool``", "If true, the node will early out if 'isactive' is false.  If false, the node will be triggered even if 'active' is False but only  if the frame number of the render product is smaller than 'startFrame',  and if the 'frameCount' is larger or equal to the internal capture count.", "False"
    "Start Frame (*inputs:startFrame*)", "``uint64``", "Frame number to begin saving to disk.", "0"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "GPU Foundations (*outputs:gpu*)", "``uint64``", "The shared context containing GPU foundation interfaces.", "None"
    "Render Product (*outputs:rp*)", "``uint64``", "The render product for this view.", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.examples.cpp.GpuInteropCpuToDisk"
    "Version", "2"
    "Extension", "omni.graph.image.nodes"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "GPU Interop: Cpu To Disk"
    "Categories", "graph:postRender,rendering"
    "Generated Class Name", "OgnGpuInteropCpuToDiskDatabase"
    "Python Module", "omni.graph.image.nodes"

