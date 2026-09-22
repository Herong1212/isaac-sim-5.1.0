.. _omni_graph_examples_cpp_Smooth_1:

.. _omni_graph_examples_cpp_Smooth:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Example Node: Smooth Points
    :keywords: lang-en omnigraph node cpp smooth


Example Node: Smooth Points
===========================

.. <description>

Smooths data in a very simple way by averaging values with neighbors.

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.examples.cpp<ext_omni_graph_examples_cpp>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Iterations (*inputs:iterations*)", "``int``", "Number of times to average neighboring values", "5"
    "Mesh (*inputs:mesh*)", "``bundle``", "Bundle containing data to be smoothed and neighbor arrays.", "None"
    "Name Of Attribute To Smooth (*inputs:nameOfAttributeToSmooth*)", "``token``", "Name of the attribute in 'mesh' containing the data to be smoothed", "points"
    "Name Of Neighbor Starts Input Attribute (*inputs:nameOfNeighborStartsInputAttribute*)", "``token``", "Name of the 'int[]' attribute in 'mesh' containing the beginning index of neighbors of each point in the array attribute specified by 'nameOfNeighborsInputAttribute'", "neighborStarts"
    "Name Of Neighbors Input Attribute (*inputs:nameOfNeighborsInputAttribute*)", "``token``", "Name of the 'int[]' attribute in 'mesh' containing the neighbors of all points.  The beginnings of each point's neighbors within this array are provided in the attribute specified by 'nameOfNeighborStartsInputAttribute'.", "neighbors"
    "Use GPU (*inputs:useGPU*)", "``bool``", "When this option is on, the node will use the GPU to perform the smoothing computation.", "True"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Mesh (*outputs:mesh*)", "``bundle``", "A copy of 'mesh' with the specified attribute smoothed.", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.examples.cpp.Smooth"
    "Version", "1"
    "Extension", "omni.graph.examples.cpp"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Example Node: Smooth Points"
    "Generated Class Name", "OgnExampleSmoothDatabase"
    "Python Module", "omni.graph.examples.cpp"

