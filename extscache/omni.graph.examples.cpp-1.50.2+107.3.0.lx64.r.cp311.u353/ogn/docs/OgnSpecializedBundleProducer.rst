.. _omni_graph_examples_cpp_SpecializedBundleProducer_1:

.. _omni_graph_examples_cpp_SpecializedBundleProducer:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Example Node: Specialized Bundle Producer
    :keywords: lang-en omnigraph node examples threadsafe cpp specialized-bundle-producer


Example Node: Specialized Bundle Producer
=========================================

.. <description>

Minimal compute node example that produces specialized bundle

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.examples.cpp<ext_omni_graph_examples_cpp>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Diameter (*inputs:diameter*)", "``float``", "Diameter of produced specialized bundle", "0.0"
    "Product Type (*inputs:productType*)", "``token``", "Product type produced by this node", "Circle"
    "", "Metadata", "*allowedTokens* = Circle,Sphere", ""


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Bundle (*outputs:bundle*)", "``bundle``", "Produced output", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.examples.cpp.SpecializedBundleProducer"
    "Version", "1"
    "Extension", "omni.graph.examples.cpp"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Example Node: Specialized Bundle Producer"
    "Categories", "examples"
    "Generated Class Name", "OgnSpecializedBundleProducerDatabase"
    "Python Module", "omni.graph.examples.cpp"

