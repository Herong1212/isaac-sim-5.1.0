.. _omni_syntheticdata_SdTextureToLinearArray_1:

.. _omni_syntheticdata_SdTextureToLinearArray:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Sd Texture To Linear Array
    :keywords: lang-en omnigraph node internal syntheticdata sd-texture-to-linear-array


Sd Texture To Linear Array
==========================

.. <description>

SyntheticData node to copy the input texture into a linear array buffer

.. </description>


Installation
------------

To use this node enable :ref:`omni.syntheticdata<ext_omni_syntheticdata>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Cuda Mipmapped Array (*inputs:cudaMipmappedArray*)", "``uint64``", "Pointer to the CUDA Mipmapped Array", "0"
    "Format (*inputs:format*)", "``uint64``", "Format", "0"
    "Height (*inputs:height*)", "``uint``", "Height", "0"
    "Hydra Time (*inputs:hydraTime*)", "``double``", "Hydra time in stage", "0.0"
    "Mip Count (*inputs:mipCount*)", "``uint``", "Mip Count", "0"
    "Output Height (*inputs:outputHeight*)", "``uint``", "Requested output height", "0"
    "Output Width (*inputs:outputWidth*)", "``uint``", "Requested output width", "0"
    "Sim Time (*inputs:simTime*)", "``double``", "Simulation time", "0.0"
    "Stream (*inputs:stream*)", "``uint64``", "Pointer to the CUDA Stream", "0"
    "Width (*inputs:width*)", "``uint``", "Width", "0"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Data (*outputs:data*)", "``float[4][]``", "Buffer array data", "[]"
    "Height (*outputs:height*)", "``uint``", "Buffer array height", "None"
    "Hydra Time (*outputs:hydraTime*)", "``double``", "Hydra time in stage", "None"
    "Sim Time (*outputs:simTime*)", "``double``", "Simulation time", "None"
    "Stream (*outputs:stream*)", "``uint64``", "Pointer to the CUDA Stream", "None"
    "Width (*outputs:width*)", "``uint``", "Buffer array width", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.syntheticdata.SdTextureToLinearArray"
    "Version", "1"
    "Extension", "omni.syntheticdata"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "tests"
    "Categories", "internal"
    "Generated Class Name", "OgnSdTextureToLinearArrayDatabase"
    "Python Module", "omni.syntheticdata"

