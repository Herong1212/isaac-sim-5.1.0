.. _omni_graph_nodes_GetTargets_1:

.. _omni_graph_nodes_GetTargets:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Get Targets
    :keywords: lang-en omnigraph node sceneGraph threadsafe nodes get-targets


Get Targets
===========

.. <description>

Returns targets from an array at an index in range [-arrayLength, arrayLength). If the given index is negative it will be an offset from the end of the array.

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.nodes<ext_omni_graph_nodes>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Count (*inputs:count*)", "``int``", "The number of paths to return.  Only returns as many paths as possible until the end of the array.  A value of -1 will return values until the end of the array", "1"
    "Index (*inputs:index*)", "``int``", "The index into the array in range [-arrayLength, arrayLength). A negative value indexes from the end of the array.", "0"
    "Targets (*inputs:targets*)", "``target``", "The input target array.", "None"
    "", "Metadata", "*allowMultiInputs* = 1", ""


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Targets (*outputs:targets*)", "``target``", "The targets found starting at the given index.", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.nodes.GetTargets"
    "Version", "1"
    "Extension", "omni.graph.nodes"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Get Targets"
    "Categories", "sceneGraph"
    "Generated Class Name", "OgnGetTargetsDatabase"
    "Python Module", "omni.graph.nodes"

