.. _omni_graph_nodes_ConstantTexCoord2f_1:

.. _omni_graph_nodes_ConstantTexCoord2f:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Constant Tex Coord2f
    :keywords: lang-en omnigraph node constants nodes constant-tex-coord2f


Constant Tex Coord2f
====================

.. <description>

Container for a 2-component single-precision floating-point UV texture coordinate value, mainly used to share a common value between several downstream nodes.

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.nodes_core<ext_omni_graph_nodes_core>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Value (*inputs:value*)", "``texcoordf[2]``", "The value, acting as both input and output.", "[0.0, 0.0]"
    "", "Metadata", "*outputOnly* = 1", ""


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.nodes.ConstantTexCoord2f"
    "Version", "1"
    "Extension", "omni.graph.nodes_core"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "Categories", "constants"
    "Generated Class Name", "OgnConstantTexCoord2fDatabase"
    "Python Module", "omni.graph.nodes_core"

