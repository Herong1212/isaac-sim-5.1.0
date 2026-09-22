.. _omni_syntheticdata_SdOnNewFrame_1:

.. _omni_syntheticdata_SdOnNewFrame:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Sd On New Frame
    :keywords: lang-en omnigraph node graph:action,flowControl syntheticdata sd-on-new-frame


Sd On New Frame
===============

.. <description>

Synthetic Data postprocess node to execute pipeline after the NewFrame event has been received

.. </description>


Installation
------------

To use this node enable :ref:`omni.syntheticdata<ext_omni_syntheticdata>` in the Extension Manager.


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Cuda Stream (*outputs:cudaStream*)", "``uint64``", "Cuda stream", "None"
    "Exec (*outputs:exec*)", "``execution``", "Executes for each newFrame event received", "None"
    "Reference Time Denominator (*outputs:referenceTimeDenominator*)", "``uint64``", "Reference time represented as a rational number : denominator", "None"
    "Reference Time Numerator (*outputs:referenceTimeNumerator*)", "``int64``", "Reference time represented as a rational number : numerator", "None"
    "Render Product Data Ptrs (*outputs:renderProductDataPtrs*)", "``uint64[]``", "HydraRenderProduct data pointer.", "None"
    "Render Product Paths (*outputs:renderProductPaths*)", "``token[]``", "Render product path tokens.", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.syntheticdata.SdOnNewFrame"
    "Version", "1"
    "Extension", "omni.syntheticdata"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "Categories", "graph:action,flowControl"
    "Generated Class Name", "OgnSdOnNewFrameDatabase"
    "Python Module", "omni.syntheticdata"

