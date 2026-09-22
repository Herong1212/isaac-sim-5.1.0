.. _omni_graph_nodes_ExtractBundle_3:

.. _omni_graph_nodes_ExtractBundle:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Extract Bundle
    :keywords: lang-en omnigraph node bundle nodes extract-bundle


Extract Bundle
==============

.. <description>

Exposes readable attributes for a bundle as outputs on this node. When this node computes it will read the latest attribute values from the target bundle into these node attributes

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.nodes<ext_omni_graph_nodes>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Bundle (*inputs:bundle*)", "``bundle``", "The bundle to be read from.", "None"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Pass Through (*outputs:passThrough*)", "``bundle``", "The input bundle passed as-is", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.nodes.ExtractBundle"
    "Version", "3"
    "Extension", "omni.graph.nodes"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Extract Bundle"
    "Categories", "bundle"
    "Generated Class Name", "OgnExtractBundleDatabase"
    "Python Module", "omni.graph.nodes"

