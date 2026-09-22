.. _omni_graph_nodes_MakeVector3_1:

.. _omni_graph_nodes_MakeVector3:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Make 3-Vector
    :keywords: lang-en omnigraph node math:conversion threadsafe nodes make-vector3


Make 3-Vector
=============

.. <description>

Merge 3 input values into a single output vector. If the inputs are arrays, the output will be an array of vectors.

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
    "Z (*inputs:z*)", "``['double', 'double[]', 'float', 'float[]', 'half', 'half[]', 'int', 'int[]']``", "The third component of the vector", "None"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Vector (*outputs:tuple*)", "``['double[3]', 'double[3][]', 'float[3]', 'float[3][]', 'half[3]', 'half[3][]', 'int[3]', 'int[3][]']``", "Output 3-vector(s)", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.nodes.MakeVector3"
    "Version", "1"
    "Extension", "omni.graph.nodes"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "tags", "compose,combine,join"
    "uiName", "Make 3-Vector"
    "Categories", "math:conversion"
    "Generated Class Name", "OgnMakeVector3Database"
    "Python Module", "omni.graph.nodes"

