.. _omni_graph_nodes_ConstantHalf4_1:

.. _omni_graph_nodes_ConstantHalf4:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Constant Half4
    :keywords: lang-en omnigraph node constants nodes constant-half4


Constant Half4
==============

.. <description>

Container for a 4-component half-precision floating-point value, mainly used to share a common value between several downstream nodes.

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.nodes_core<ext_omni_graph_nodes_core>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Value (*inputs:value*)", "``half[4]``", "The value, acting as both input and output.", "[0.0, 0.0, 0.0, 0.0]"
    "", "Metadata", "*outputOnly* = 1", ""


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.nodes.ConstantHalf4"
    "Version", "1"
    "Extension", "omni.graph.nodes_core"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "Categories", "constants"
    "Generated Class Name", "OgnConstantHalf4Database"
    "Python Module", "omni.graph.nodes_core"

