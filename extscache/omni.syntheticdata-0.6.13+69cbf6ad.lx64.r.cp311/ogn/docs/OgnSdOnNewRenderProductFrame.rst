.. _omni_syntheticdata_SdOnNewRenderProductFrame_1:

.. _omni_syntheticdata_SdOnNewRenderProductFrame:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Sd On New Render Product Frame
    :keywords: lang-en omnigraph node graph:action,flowControl syntheticdata sd-on-new-render-product-frame


Sd On New Render Product Frame
==============================

.. <description>

Synthetic Data postprocess node to execute pipeline after the NewFrame event has been received on the given renderProduct

.. </description>


Installation
------------

To use this node enable :ref:`omni.syntheticdata<ext_omni_syntheticdata>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Received (*inputs:exec*)", "``execution``", "Executes for each newFrame event received", "None"
    "Render Product Data Ptrs (*inputs:renderProductDataPtrs*)", "``uint64[]``", "HydraRenderProduct data pointers.", "[]"
    "Render Product Path (*inputs:renderProductPath*)", "``token``", "Path of the renderProduct to wait for being rendered", ""
    "Render Product Paths (*inputs:renderProductPaths*)", "``token[]``", "Render product path tokens.", "[]"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Cuda Stream (*outputs:cudaStream*)", "``uint64``", "Cuda stream", "None"
    "Received (*outputs:exec*)", "``execution``", "Executes for each newFrame event received", "None"
    "Render Product Path (*outputs:renderProductPath*)", "``token``", "Path of the renderProduct to wait for being rendered", "None"
    "Render Results (*outputs:renderResults*)", "``uint64``", "Render results", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.syntheticdata.SdOnNewRenderProductFrame"
    "Version", "1"
    "Extension", "omni.syntheticdata"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "Categories", "graph:action,flowControl"
    "Generated Class Name", "OgnSdOnNewRenderProductFrameDatabase"
    "Python Module", "omni.syntheticdata"

