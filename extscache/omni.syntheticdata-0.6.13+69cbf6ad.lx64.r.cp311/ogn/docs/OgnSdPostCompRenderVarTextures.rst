.. _omni_syntheticdata_SdPostCompRenderVarTextures_1:

.. _omni_syntheticdata_SdPostCompRenderVarTextures:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Sd Post Comp Render Var Textures
    :keywords: lang-en omnigraph node graph:postRender,rendering,internal syntheticdata sd-post-comp-render-var-textures


Sd Post Comp Render Var Textures
================================

.. <description>

Synthetic Data node to compose a front renderVar texture into a back renderVar texture

.. </description>


Installation
------------

To use this node enable :ref:`omni.syntheticdata<ext_omni_syntheticdata>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Cuda Ptr (*inputs:cudaPtr*)", "``uint64``", "Front texture CUDA pointer", "0"
    "Format (*inputs:format*)", "``uint64``", "Front texture format", "0"
    "gpuFoundations (*inputs:gpu*)", "``uint64``", "Pointer to shared context containing gpu foundations", "0"
    "Height (*inputs:height*)", "``uint``", "Front texture height", "0"
    "Mode (*inputs:mode*)", "``token``", "Mode : grid, line", "line"
    "Parameters (*inputs:parameters*)", "``float[3]``", "Parameters", "[0, 0, 0]"
    "Render Var (*inputs:renderVar*)", "``token``", "Name of the back RenderVar", "LdrColor"
    "renderProduct (*inputs:rp*)", "``uint64``", "Pointer to render product for this view", "0"
    "Width (*inputs:width*)", "``uint``", "Front texture width", "0"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.syntheticdata.SdPostCompRenderVarTextures"
    "Version", "1"
    "Extension", "omni.syntheticdata"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "__tokens", "[""line"", ""grid""]"
    "Categories", "graph:postRender,rendering,internal"
    "Generated Class Name", "OgnSdPostCompRenderVarTexturesDatabase"
    "Python Module", "omni.syntheticdata"

