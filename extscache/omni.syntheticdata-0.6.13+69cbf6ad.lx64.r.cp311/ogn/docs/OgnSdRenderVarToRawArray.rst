.. _omni_syntheticdata_SdRenderVarToRawArray_2:

.. _omni_syntheticdata_SdRenderVarToRawArray:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Sd Render Var To Raw Array
    :keywords: lang-en omnigraph node graph:action syntheticdata sd-render-var-to-raw-array


Sd Render Var To Raw Array
==========================

.. <description>

Synthetic Data action node to copy the input rendervar into an output raw array

.. </description>


Installation
------------

To use this node enable :ref:`omni.syntheticdata<ext_omni_syntheticdata>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Cuda Stream (*inputs:cudaStream*)", "``uint64``", "Pointer to the CUDA stream", "0"
    "Exec (*inputs:exec*)", "``execution``", "Trigger", "None"
    "Render Results (*inputs:renderResults*)", "``uint64``", "Render results pointer", "0"
    "Render Var (*inputs:renderVar*)", "``token``", "Name of the renderVar", ""


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Buffer Size (*outputs:bufferSize*)", "``uint64``", "Size (in bytes) of the buffer (0 if the input is a texture)", "None"
    "Cuda Stream (*outputs:cudaStream*)", "``uint64``", "Pointer to the CUDA stream", "None"
    "Data (*outputs:data*)", "``uchar[]``", "Buffer array data", "[]"
    "Received (*outputs:exec*)", "``execution``", "Executes when the event is received", "None"
    "Format (*outputs:format*)", "``uint64``", "Format", "None"
    "Height (*outputs:height*)", "``uint``", "Height  (0 if the input is a buffer)", "None"
    "Strides (*outputs:strides*)", "``int[2]``", "Strides (in bytes) ([0,0] if the input is a buffer)", "None"
    "Width (*outputs:width*)", "``uint``", "Width  (0 if the input is a buffer)", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.syntheticdata.SdRenderVarToRawArray"
    "Version", "2"
    "Extension", "omni.syntheticdata"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "tests"
    "Categories", "graph:action"
    "Generated Class Name", "OgnSdRenderVarToRawArrayDatabase"
    "Python Module", "omni.syntheticdata"

