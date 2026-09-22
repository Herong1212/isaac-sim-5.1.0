.. _omni_graph_nodes_RenderPostProcessEntry_3:

.. _omni_graph_nodes_RenderPostProcessEntry:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Render Postprocess Entry
    :keywords: lang-en omnigraph node internal,graph:postRender nodes render-post-process-entry


Render Postprocess Entry
========================

.. <description>

Deprecated: use OgnGpuInteropCudaEntry instead.

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.image.nodes<ext_omni_graph_image_nodes>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Source Name (*inputs:sourceName*)", "``string``", "Source name of the AOV", "ldrColor"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "cudaMipmappedArray (*outputs:cudaMipmappedArray*)", "``uint64``", "Pointer to the CUDA Mipmapped Array", "None"
    "format (*outputs:format*)", "``uint64``", "Format", "None"
    "height (*outputs:height*)", "``uint``", "Height", "None"
    "hydraTime (*outputs:hydraTime*)", "``double``", "Hydra time in stage", "None"
    "mipCount (*outputs:mipCount*)", "``uint``", "Mip Count", "None"
    "Rational Time Of Sim Denominator (*outputs:rationalTimeOfSimDenominator*)", "``uint64``", "Rational time of simulation used to fetch data from Fabric", "None"
    "Rational Time Of Sim Numerator (*outputs:rationalTimeOfSimNumerator*)", "``int64``", "Rational time of simulation used to fetch data from Fabric", "None"
    "simTime (*outputs:simTime*)", "``double``", "Simulation time", "None"
    "stream (*outputs:stream*)", "``uint64``", "Pointer to the CUDA Stream", "None"
    "width (*outputs:width*)", "``uint``", "Width", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.nodes.RenderPostProcessEntry"
    "Version", "3"
    "Extension", "omni.graph.image.nodes"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Render Postprocess Entry"
    "hidden", "true"
    "Categories", "internal,graph:postRender"
    "Generated Class Name", "OgnRenderPostprocessEntryDatabase"
    "Python Module", "omni.graph.image.nodes"

