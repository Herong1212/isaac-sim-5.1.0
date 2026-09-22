.. _omni_syntheticdata_SdLinearArrayToTexture_1:

.. _omni_syntheticdata_SdLinearArrayToTexture:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Sd Linear Array To Texture
    :keywords: lang-en omnigraph node graph:action syntheticdata sd-linear-array-to-texture


Sd Linear Array To Texture
==========================

.. <description>

Synthetic Data node to copy the input buffer array into a texture for visualization

.. </description>


Installation
------------

To use this node enable :ref:`omni.syntheticdata<ext_omni_syntheticdata>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Data (*inputs:data*)", "``float[4][]``", "Buffer array data", "[]"
    "Exec (*inputs:exec*)", "``execution``", "Trigger", "None"
    "Height (*inputs:height*)", "``uint``", "Buffer array height", "0"
    "Sd Display Cuda Mipmapped Array (*inputs:sdDisplayCudaMipmappedArray*)", "``uint64``", "Visualization texture CUDA mipmapped array pointer", "0"
    "Sd Display Format (*inputs:sdDisplayFormat*)", "``uint64``", "Visualization texture format", "0"
    "Sd Display Height (*inputs:sdDisplayHeight*)", "``uint``", "Visualization texture Height", "0"
    "Sd Display Stream (*inputs:sdDisplayStream*)", "``uint64``", "Visualization texture CUDA stream pointer", "0"
    "Sd Display Width (*inputs:sdDisplayWidth*)", "``uint``", "Visualization texture width", "0"
    "Stream (*inputs:stream*)", "``uint64``", "Pointer to the CUDA Stream", "0"
    "Width (*inputs:width*)", "``uint``", "Buffer array width", "0"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Cuda Ptr (*outputs:cudaPtr*)", "``uint64``", "Display texture CUDA pointer", "None"
    "Received (*outputs:exec*)", "``execution``", "Executes when the event is received", "None"
    "Format (*outputs:format*)", "``uint64``", "Display texture format", "None"
    "Handle Ptr (*outputs:handlePtr*)", "``uint64``", "Display texture handle reference", "None"
    "Height (*outputs:height*)", "``uint``", "Display texture height", "None"
    "Stream (*outputs:stream*)", "``uint64``", "Output texture CUDA stream pointer", "None"
    "Width (*outputs:width*)", "``uint``", "Display texture width", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.syntheticdata.SdLinearArrayToTexture"
    "Version", "1"
    "Extension", "omni.syntheticdata"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "tests"
    "Categories", "graph:action"
    "Generated Class Name", "OgnSdLinearArrayToTextureDatabase"
    "Python Module", "omni.syntheticdata"

