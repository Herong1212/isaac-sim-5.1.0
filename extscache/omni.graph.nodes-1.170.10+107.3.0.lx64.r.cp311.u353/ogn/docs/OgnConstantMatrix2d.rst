.. _omni_graph_nodes_ConstantMatrix2d_1:

.. _omni_graph_nodes_ConstantMatrix2d:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Constant Matrix2d
    :keywords: lang-en omnigraph node constants nodes constant-matrix2d


Constant Matrix2d
=================

.. <description>

Container for a 2x2 double-precision floating-point matrix value, mainly used to share a common value between several downstream nodes.

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.nodes<ext_omni_graph_nodes>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Value (*inputs:value*)", "``matrixd[2]``", "The value, acting as both input and output.", "[[1.0, 0.0], [0.0, 1.0]]"
    "", "Metadata", "*outputOnly* = 1", ""


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.nodes.ConstantMatrix2d"
    "Version", "1"
    "Extension", "omni.graph.nodes"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "Categories", "constants"
    "Generated Class Name", "OgnConstantMatrix2dDatabase"
    "Python Module", "omni.graph.nodes"

