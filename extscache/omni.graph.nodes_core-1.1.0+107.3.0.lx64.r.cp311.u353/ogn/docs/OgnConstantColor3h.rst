.. _omni_graph_nodes_ConstantColor3h_1:

.. _omni_graph_nodes_ConstantColor3h:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Constant Color3h
    :keywords: lang-en omnigraph node constants nodes constant-color3h


Constant Color3h
================

.. <description>

Container for a half-precision floating-point RGB color value, mainly used to share a common value between several downstream nodes.

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.nodes_core<ext_omni_graph_nodes_core>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Value (*inputs:value*)", "``colorh[3]``", "The value, acting as both input and output.", "[0.0, 0.0, 0.0]"
    "", "Metadata", "*outputOnly* = 1", ""


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.nodes.ConstantColor3h"
    "Version", "1"
    "Extension", "omni.graph.nodes_core"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "Categories", "constants"
    "Generated Class Name", "OgnConstantColor3hDatabase"
    "Python Module", "omni.graph.nodes_core"

