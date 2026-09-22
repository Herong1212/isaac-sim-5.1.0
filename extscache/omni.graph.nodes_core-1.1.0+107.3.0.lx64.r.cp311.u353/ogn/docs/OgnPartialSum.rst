.. _omni_graph_nodes_PartialSum_1:

.. _omni_graph_nodes_PartialSum:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Compute Integer Array Partial Sums
    :keywords: lang-en omnigraph node math:operator threadsafe nodes partial-sum


Compute Integer Array Partial Sums
==================================

.. <description>

Compute the partial sums of the input integer array named "Array" and put the result in an output integer array named "PartialSum". A partial sum is the sum of all of the elements up to but not including a certain point in an array, so output element 0 is always 0, element 1 is array[0], element 2 is array[0] + array[1], etc.

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.nodes_core<ext_omni_graph_nodes_core>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Array (*inputs:array*)", "``int[]``", "List of integers whose partial sum is to be computed.", "[]"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Partial Sum (*outputs:partialSum*)", "``int[]``", "Array whose nth value equals the nth partial sum of the input ""Array"".", "[]"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.nodes.PartialSum"
    "Version", "1"
    "Extension", "omni.graph.nodes_core"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Compute Integer Array Partial Sums"
    "Categories", "math:operator"
    "Generated Class Name", "OgnPartialSumDatabase"
    "Python Module", "omni.graph.nodes_core"

