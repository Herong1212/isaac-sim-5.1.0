.. _omni_graph_examples_cpp_Deformer2_1:

.. _omni_graph_examples_cpp_Deformer2:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Example Node: Z Threshold Deformer
    :keywords: lang-en omnigraph node examples threadsafe cpp deformer2


Example Node: Z Threshold Deformer
==================================

.. <description>

Example deformer that limits the Z point positions to a threshold

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.examples.cpp<ext_omni_graph_examples_cpp>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Points (*inputs:points*)", "``pointf[3][]``", "Set of points to be deformed", "[]"
    "Threshold (*inputs:threshold*)", "``float``", "Z value to limit points", "0.0"


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

    "Unique ID", "omni.graph.examples.cpp.Deformer2"
    "Version", "1"
    "Extension", "omni.graph.examples.cpp"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Example Node: Z Threshold Deformer"
    "Categories", "examples"
    "Generated Class Name", "OgnDeformer2_CPUDatabase"
    "Python Module", "omni.graph.examples.cpp"

