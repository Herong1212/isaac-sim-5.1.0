.. _omni_graph_nodes_MakeMatrix4_1:

.. _omni_graph_nodes_MakeMatrix4:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Make Matrix4
    :keywords: lang-en omnigraph node math:conversion threadsafe nodes make-matrix4


Make Matrix4
============

.. <description>

Merge 4 row vectors into a matrix. If the inputs are arrays, the output will be an array of matrices.

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.nodes_core<ext_omni_graph_nodes_core>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Fourth Row (*inputs:w*)", "``['double[3]', 'double[3][]', 'double[4]', 'double[4][]']``", "The fourth row of the matrix", "None"
    "First Row (*inputs:x*)", "``['double[3]', 'double[3][]', 'double[4]', 'double[4][]']``", "The first row of the matrix", "None"
    "Second Row (*inputs:y*)", "``['double[3]', 'double[3][]', 'double[4]', 'double[4][]']``", "The second row of the matrix", "None"
    "Third Row (*inputs:z*)", "``['double[3]', 'double[3][]', 'double[4]', 'double[4][]']``", "The third row of the matrix", "None"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Matrix (*outputs:matrix*)", "``['matrixd[4]', 'matrixd[4][]']``", "The matrix formed by the input row vectors", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.nodes.MakeMatrix4"
    "Version", "1"
    "Extension", "omni.graph.nodes_core"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "tags", "compose,combine,join"
    "uiName", "Make Matrix4"
    "Categories", "math:conversion"
    "Generated Class Name", "OgnMakeMatrix4Database"
    "Python Module", "omni.graph.nodes_core"

