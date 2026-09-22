.. _omni_graph_examples_cpp_SimpleDeformer_1:

.. _omni_graph_examples_cpp_SimpleDeformer:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Example Node: Simple Sine Wave Deformer
    :keywords: lang-en omnigraph node examples threadsafe cpp simple-deformer


Example Node: Simple Sine Wave Deformer
=======================================

.. <description>

This is an example of a simple deformer.  It calculates a sine wave and deforms the input geometry with it 

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.examples.cpp<ext_omni_graph_examples_cpp>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Multiplier (*inputs:multiplier*)", "``float``", "The multiplier for the amplitude of the sine wave", "1"
    "Points (*inputs:points*)", "``pointf[3][]``", "The input points to be deformed", "[]"
    "Wavelength (*inputs:wavelength*)", "``float``", "The wavelength of the sine wave", "1"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Points (*outputs:points*)", "``pointf[3][]``", "The deformed output points", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.examples.cpp.SimpleDeformer"
    "Version", "1"
    "Extension", "omni.graph.examples.cpp"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Example Node: Simple Sine Wave Deformer"
    "Categories", "examples"
    "Generated Class Name", "OgnExampleSimpleDeformerDatabase"
    "Python Module", "omni.graph.examples.cpp"

