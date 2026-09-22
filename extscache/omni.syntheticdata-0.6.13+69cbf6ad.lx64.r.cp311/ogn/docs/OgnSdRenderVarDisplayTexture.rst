.. _omni_syntheticdata_SdRenderVarDisplayTexture_2:

.. _omni_syntheticdata_SdRenderVarDisplayTexture:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Sd Render Var Display Texture
    :keywords: lang-en omnigraph node graph:action,rendering,internal syntheticdata sd-render-var-display-texture


Sd Render Var Display Texture
=============================

.. <description>

Synthetic Data node to expose texture resource of a visualization render variable

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
    "Render Var Display (*inputs:renderVarDisplay*)", "``token``", "Name of the renderVar", ""


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Cuda Ptr (*outputs:cudaPtr*)", "``uint64``", "Display texture CUDA pointer", "None"
    "Exec (*outputs:exec*)", "``execution``", "Trigger", "None"
    "Format (*outputs:format*)", "``uint64``", "Display texture format", "None"
    "Height (*outputs:height*)", "``uint``", "Display texture height", "None"
    "Reference Time Denominator (*outputs:referenceTimeDenominator*)", "``uint64``", "Reference time represented as a rational number : denominator", "None"
    "Reference Time Numerator (*outputs:referenceTimeNumerator*)", "``int64``", "Reference time represented as a rational number : numerator", "None"
    "Rp Resource Ptr (*outputs:rpResourcePtr*)", "``uint64``", "Display texture RpResource pointer", "None"
    "Width (*outputs:width*)", "``uint``", "Display texture width", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.syntheticdata.SdRenderVarDisplayTexture"
    "Version", "2"
    "Extension", "omni.syntheticdata"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "Categories", "graph:action,rendering,internal"
    "Generated Class Name", "OgnSdRenderVarDisplayTextureDatabase"
    "Python Module", "omni.syntheticdata"

