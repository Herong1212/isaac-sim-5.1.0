.. _omni_graph_examples_cpp_ExtractFloat3Array_1:

.. _omni_graph_examples_cpp_ExtractFloat3Array:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Example Node: Extract Float3 Array
    :keywords: lang-en omnigraph node examples threadsafe cpp extract-float3-array


Example Node: Extract Float3 Array
==================================

.. <description>

Outputs a float[3][] attribute extracted from a bundle.

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.examples.cpp<ext_omni_graph_examples_cpp>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Input (*inputs:input*)", "``bundle``", "Bundle containing a float[3][] attribute to be extracted to 'output'", "None"
    "Name Of Attribute (*inputs:nameOfAttribute*)", "``token``", "Name of the attribute in 'input' that is to be extracted to 'output'", ""


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Output (*outputs:output*)", "``float[3][]``", "The float[3][] attribute extracted from 'input'", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.examples.cpp.ExtractFloat3Array"
    "Version", "1"
    "Extension", "omni.graph.examples.cpp"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Example Node: Extract Float3 Array"
    "Categories", "examples"
    "Generated Class Name", "OgnExampleExtractFloat3ArrayDatabase"
    "Python Module", "omni.graph.examples.cpp"

