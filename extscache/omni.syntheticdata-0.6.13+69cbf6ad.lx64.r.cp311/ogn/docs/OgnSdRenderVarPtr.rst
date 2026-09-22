.. _omni_syntheticdata_SdRenderVarPtr_2:

.. _omni_syntheticdata_SdRenderVarPtr:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Sd Render Var Ptr
    :keywords: lang-en omnigraph node graph:action syntheticdata sd-render-var-ptr


Sd Render Var Ptr
=================

.. <description>

Synthetic Data node exposing the raw pointer data of a rendervar.

.. </description>


Installation
------------

To use this node enable :ref:`omni.syntheticdata<ext_omni_syntheticdata>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Exec (*inputs:exec*)", "``execution``", "Trigger", "None"
    "Render Results (*inputs:renderResults*)", "``uint64``", "Render results pointer", "0"
    "Render Var (*inputs:renderVar*)", "``token``", "Name of the renderVar", ""


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Buffer Size (*outputs:bufferSize*)", "``uint64``", "Size (in bytes) of the buffer (0 if the input is a texture)", "None"
    "Cuda Device Index (*outputs:cudaDeviceIndex*)", "``int``", "Index of the device where the data lives (-1 for host data)", "-1"
    "Data Ptr (*outputs:dataPtr*)", "``uint64``", "Pointer to the raw data (cuda device pointer or host pointer)", "0"
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

    "Unique ID", "omni.syntheticdata.SdRenderVarPtr"
    "Version", "2"
    "Extension", "omni.syntheticdata"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "tests"
    "Categories", "graph:action"
    "Generated Class Name", "OgnSdRenderVarPtrDatabase"
    "Python Module", "omni.syntheticdata"

