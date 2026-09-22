.. _omni_graph_nodes_MakeVector2_1:

.. _omni_graph_nodes_MakeVector2:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Make 2-Vector
    :keywords: lang-en omnigraph node math:conversion threadsafe nodes make-vector2


Make 2-Vector
=============

.. <description>

Merge 2 input values into a single output vector. If the inputs are arrays, the output will be an array of vectors.

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.nodes<ext_omni_graph_nodes>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "X (*inputs:x*)", "``['double', 'double[]', 'float', 'float[]', 'half', 'half[]', 'int', 'int[]']``", "The first component of the vector", "None"
    "Y (*inputs:y*)", "``['double', 'double[]', 'float', 'float[]', 'half', 'half[]', 'int', 'int[]']``", "The second component of the vector", "None"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Vector (*outputs:tuple*)", "``['double[2]', 'double[2][]', 'float[2]', 'float[2][]', 'half[2]', 'half[2][]', 'int[2]', 'int[2][]']``", "Output vector(s)", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.nodes.MakeVector2"
    "Version", "1"
    "Extension", "omni.graph.nodes"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "tags", "compose,combine,join"
    "uiName", "Make 2-Vector"
    "Categories", "math:conversion"
    "Generated Class Name", "OgnMakeVector2Database"
    "Python Module", "omni.graph.nodes"

