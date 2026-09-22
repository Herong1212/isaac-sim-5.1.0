.. _omni_graph_nodes_ConstantTexCoord2d_1:

.. _omni_graph_nodes_ConstantTexCoord2d:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Constant Tex Coord2d
    :keywords: lang-en omnigraph node constants nodes constant-tex-coord2d


Constant Tex Coord2d
====================

.. <description>

Container for a 2-component double-precision floating-point UV texture coordinate value, mainly used to share a common value between several downstream nodes.

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.nodes_core<ext_omni_graph_nodes_core>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Value (*inputs:value*)", "``texcoordd[2]``", "The value, acting as both input and output.", "[0.0, 0.0]"
    "", "Metadata", "*outputOnly* = 1", ""


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.nodes.ConstantTexCoord2d"
    "Version", "1"
    "Extension", "omni.graph.nodes_core"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "Categories", "constants"
    "Generated Class Name", "OgnConstantTexCoord2dDatabase"
    "Python Module", "omni.graph.nodes_core"

