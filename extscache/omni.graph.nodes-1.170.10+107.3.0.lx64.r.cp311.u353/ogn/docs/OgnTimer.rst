.. _omni_graph_nodes_Timer_2:

.. _omni_graph_nodes_Timer:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Timer
    :keywords: lang-en omnigraph node animation nodes timer


Timer
=====

.. <description>

Timer Node is a node that lets you create animation curve(s), plays back and samples the value(s) along its time to output values.

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.nodes<ext_omni_graph_nodes>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Duration (*inputs:duration*)", "``double``", "Number of seconds to play interpolation.", "1.0"
    "End Value (*inputs:endValue*)", "``double``", "Value of the end of the duration.", "1.0"
    "Play (*inputs:play*)", "``execution``", "Signal to the graph that this node is ready for execution. When the node executes with this signal active it plays the clip from the current frame.", "None"
    "Start Value (*inputs:startValue*)", "``double``", "Value of the start of the duration.", "0.0"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Finished (*outputs:finished*)", "``execution``", "When the node has finished the playback, signal to the graph that execution can continue downstream on this path.", "None"
    "Updated (*outputs:updated*)", "``execution``", "When the node is executed, and output value(s) resampled and updated, signal to the graph that execution can continue downstream on this path.", "None"
    "Value (*outputs:value*)", "``double``", "Progress of the Timer node, between 0.0 and 1.0.", "0.0"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.nodes.Timer"
    "Version", "2"
    "Extension", "omni.graph.nodes"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Timer"
    "Categories", "animation"
    "__categoryDescriptions", "animation,Nodes dealing with Animation"
    "Generated Class Name", "OgnTimerDatabase"
    "Python Module", "omni.graph.nodes"

