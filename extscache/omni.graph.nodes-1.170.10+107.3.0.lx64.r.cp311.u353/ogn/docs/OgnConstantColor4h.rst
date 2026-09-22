.. _omni_graph_nodes_ConstantColor4h_1:

.. _omni_graph_nodes_ConstantColor4h:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Constant Color4h
    :keywords: lang-en omnigraph node constants nodes constant-color4h


Constant Color4h
================

.. <description>

Container for a half-precision floating-point RGBA color value, mainly used to share a common value between several downstream nodes. The A (alpha) value is not premultiplied.

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.nodes<ext_omni_graph_nodes>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Value (*inputs:value*)", "``colorh[4]``", "The value, acting as both input and output.", "[0.0, 0.0, 0.0, 0.0]"
    "", "Metadata", "*outputOnly* = 1", ""


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.nodes.ConstantColor4h"
    "Version", "1"
    "Extension", "omni.graph.nodes"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "Categories", "constants"
    "Generated Class Name", "OgnConstantColor4hDatabase"
    "Python Module", "omni.graph.nodes"

