.. _omni_graph_nodes_ConstantQuatf_1:

.. _omni_graph_nodes_ConstantQuatf:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Constant Quatf
    :keywords: lang-en omnigraph node constants nodes constant-quatf


Constant Quatf
==============

.. <description>

Container for a 4-component single-precision floating-point value with the 'quaternion' role, mainly used to share a common value between several downstream nodes. The first component is the real value, the remaining three are the imaginary values.

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.nodes<ext_omni_graph_nodes>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Value (*inputs:value*)", "``quatf[4]``", "The value, acting as both input and output.", "[0.0, 0.0, 0.0, 0.0]"
    "", "Metadata", "*outputOnly* = 1", ""


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.nodes.ConstantQuatf"
    "Version", "1"
    "Extension", "omni.graph.nodes"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "Categories", "constants"
    "Generated Class Name", "OgnConstantQuatfDatabase"
    "Python Module", "omni.graph.nodes"

