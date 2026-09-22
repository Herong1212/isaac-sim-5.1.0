.. _omni_graph_nodes_RenderPreProcessEntry_3:

.. _omni_graph_nodes_RenderPreProcessEntry:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Render Preprocess Entry
    :keywords: lang-en omnigraph node graph:preRender,rendering nodes render-pre-process-entry


Render Preprocess Entry
=======================

.. <description>

Entry node for pre-processing hydra render results for a single view. All downstream nodes are scheduled as CUDA commands.

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.image.nodes<ext_omni_graph_image_nodes>` in the Extension Manager.


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Renderer Time (*outputs:hydraTime*)", "``double``", "The time difference since the last rendered frame.", "None"
    "Rational Time Of Sim Denominator (*outputs:rationalTimeOfSimDenominator*)", "``uint64``", "The denominator of the simulation time expressed as rational time.  It is always valid and may be used to fetch data from Fabric during the node compute.", "None"
    "Rational Time Of Sim Numerator (*outputs:rationalTimeOfSimNumerator*)", "``int64``", "The numerator of the simulation time expressed as rational time.  It is always valid and may be used to fetch data from Fabric during the node compute.", "None"
    "Simulation Time (*outputs:simTime*)", "``double``", "The time difference since the last simulation frame. May suffer from loss of precision and cannot be used as a deterministic identifier,  for example for fetching data from Fabric during the node compute -  use the Rational Time instead in that case.", "None"
    "Stream (*outputs:stream*)", "``uint64``", "The CUDA Stream used to order the CUDA commands scheduled by this graph execution.", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.nodes.RenderPreProcessEntry"
    "Version", "3"
    "Extension", "omni.graph.image.nodes"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Render Preprocess Entry"
    "Categories", "graph:preRender,rendering"
    "Generated Class Name", "OgnRenderPreprocessEntryDatabase"
    "Python Module", "omni.graph.image.nodes"

