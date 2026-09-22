.. _omni_graph_examples_cpp_SimpleIk_1:

.. _omni_graph_examples_cpp_SimpleIk:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Example Node: Simple IK
    :keywords: lang-en omnigraph node examples threadsafe cpp simple-ik


Example Node: Simple IK
=======================

.. <description>

Example node that employs a simple IK algorithm to match a three-joint limb to a goal

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.examples.cpp<ext_omni_graph_examples_cpp>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Goal Transform (*inputs:goal*)", "``matrixd[4]``", "Transform of the IK goal", "[[1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0], [0.0, 0.0, 1.0, 0.0], [0.0, 0.0, 0.0, 1.0]]"


State
-----
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Ankle Transform (*state:ankle*)", "``matrixd[4]``", "Computed transform of the ankle joint", "None"
    "Hip Transform (*state:hip*)", "``matrixd[4]``", "Computed transform of the hip joint", "None"
    "Knee Transform (*state:knee*)", "``matrixd[4]``", "Computed transform of the knee joint", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.examples.cpp.SimpleIk"
    "Version", "1"
    "Extension", "omni.graph.examples.cpp"
    "Has State?", "True"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Example Node: Simple IK"
    "Categories", "examples"
    "Generated Class Name", "OgnIKDatabase"
    "Python Module", "omni.graph.examples.cpp"

