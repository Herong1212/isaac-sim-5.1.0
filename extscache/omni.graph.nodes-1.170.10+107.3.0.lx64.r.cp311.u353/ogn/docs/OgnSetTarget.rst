.. _omni_graph_nodes_SetTarget_1:

.. _omni_graph_nodes_SetTarget:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Set Target
    :keywords: lang-en omnigraph node sceneGraph threadsafe nodes set-target


Set Target
==========

.. <description>

Sets a target in a target array at an index in range [-arrayLength, arrayLength). If the given index is negative it will be an offset from the end of the array.

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.nodes<ext_omni_graph_nodes>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Index (*inputs:index*)", "``int``", "The index into the array in range [-arrayLength, arrayLength). A negative value indexes from the end of the array.", "0"
    "Set Target (*inputs:setTarget*)", "``target``", "The target to set at the given index.", "None"
    "Targets (*inputs:targets*)", "``target``", "The input target array.", "None"
    "", "Metadata", "*allowMultiInputs* = 1", ""


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Targets (*outputs:targets*)", "``target``", "The modified target array.", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.nodes.SetTarget"
    "Version", "1"
    "Extension", "omni.graph.nodes"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Set Target"
    "Categories", "sceneGraph"
    "Generated Class Name", "OgnSetTargetDatabase"
    "Python Module", "omni.graph.nodes"

