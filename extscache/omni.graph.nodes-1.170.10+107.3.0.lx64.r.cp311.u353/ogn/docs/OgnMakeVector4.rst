.. _omni_graph_nodes_MakeVector4_1:

.. _omni_graph_nodes_MakeVector4:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Make 4-Vector
    :keywords: lang-en omnigraph node math:conversion threadsafe nodes make-vector4


Make 4-Vector
=============

.. <description>

Merge 4 input values into a single output vector. If the inputs are arrays, the output will be an array of vectors.

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.nodes<ext_omni_graph_nodes>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "W (*inputs:w*)", "``['double', 'double[]', 'float', 'float[]', 'half', 'half[]', 'int', 'int[]']``", "The fourth component of the vector", "None"
    "X (*inputs:x*)", "``['double', 'double[]', 'float', 'float[]', 'half', 'half[]', 'int', 'int[]']``", "The first component of the vector", "None"
    "Y (*inputs:y*)", "``['double', 'double[]', 'float', 'float[]', 'half', 'half[]', 'int', 'int[]']``", "The second component of the vector", "None"
    "Z (*inputs:z*)", "``['double', 'double[]', 'float', 'float[]', 'half', 'half[]', 'int', 'int[]']``", "The third component of the vector", "None"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Vector (*outputs:tuple*)", "``['double[4]', 'double[4][]', 'float[4]', 'float[4][]', 'half[4]', 'half[4][]', 'int[4]', 'int[4][]']``", "Output 4-vector", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.nodes.MakeVector4"
    "Version", "1"
    "Extension", "omni.graph.nodes"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "tags", "compose,combine,join"
    "uiName", "Make 4-Vector"
    "Categories", "math:conversion"
    "Generated Class Name", "OgnMakeVector4Database"
    "Python Module", "omni.graph.nodes"

