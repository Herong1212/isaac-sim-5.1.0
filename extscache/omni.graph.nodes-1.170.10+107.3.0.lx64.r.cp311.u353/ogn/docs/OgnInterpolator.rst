.. _omni_graph_nodes_Interpolator_1:

.. _omni_graph_nodes_Interpolator:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Interpolator
    :keywords: lang-en omnigraph node math:operator threadsafe nodes interpolator


Interpolator
============

.. <description>

Time sample interpolator

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.nodes<ext_omni_graph_nodes>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Knot Array (*inputs:knots*)", "``float[]``", "Array of knots on the time sample curve", "[]"
    "Interpolation Point (*inputs:param*)", "``float``", "Time sample interpolation point", "0.0"
    "Value Array (*inputs:values*)", "``float[]``", "Array of time sample values", "[]"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Interpolated Value (*outputs:value*)", "``float``", "Value in the time samples, interpolated at the given parameter location", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.nodes.Interpolator"
    "Version", "1"
    "Extension", "omni.graph.nodes"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Interpolator"
    "Categories", "math:operator"
    "Generated Class Name", "OgnInterpolatorDatabase"
    "Python Module", "omni.graph.nodes"

