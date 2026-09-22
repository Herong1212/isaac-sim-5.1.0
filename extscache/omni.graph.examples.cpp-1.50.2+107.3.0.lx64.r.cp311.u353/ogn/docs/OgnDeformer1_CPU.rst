.. _omni_graph_examples_cpp_Deformer1_1:

.. _omni_graph_examples_cpp_Deformer1:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Example Node: Sine Wave Deformer
    :keywords: lang-en omnigraph node examples threadsafe cpp deformer1


Example Node: Sine Wave Deformer
================================

.. <description>

Example deformer node that applies a sine wave to a mesh

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.examples.cpp<ext_omni_graph_examples_cpp>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Multiplier (*inputs:multiplier*)", "``float``", "Amplitude of sinusoidal deformer function", "0.7"
    "Points (*inputs:points*)", "``pointf[3][]``", "Set of points to be deformed", "[]"
    "Wavelength (*inputs:wavelength*)", "``float``", "Wavelength of sinusoidal deformer function", "50.0"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Points (*outputs:points*)", "``pointf[3][]``", "Set of deformed points", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.examples.cpp.Deformer1"
    "Version", "1"
    "Extension", "omni.graph.examples.cpp"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Example Node: Sine Wave Deformer"
    "Categories", "examples"
    "Generated Class Name", "OgnDeformer1_CPUDatabase"
    "Python Module", "omni.graph.examples.cpp"

