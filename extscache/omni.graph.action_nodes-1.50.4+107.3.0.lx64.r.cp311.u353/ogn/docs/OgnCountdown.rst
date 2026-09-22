.. _omni_graph_action_Countdown_2:

.. _omni_graph_action_Countdown:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Countdown
    :keywords: lang-en omnigraph node graph:action,flowControl action countdown


Countdown
=========

.. <description>

This type of node will activate when 'Exec In' is first set and will remain active for a total of 'Duration' ticks, where a 'tick' is an execution of the node. Every 'Period' ticks the output 'Tick' will activate and after the final tick 'Finished' will activate.
For example if 'Duration' is set to 10 and 'Period' is set to 3 then after activation the 'Tick' signal will activate after 3, 6, and 9 executions, and 'Finished' will activate after the 10th.
If 'Exec In' is activated again before the current countdown has finished, the countdown will be reset to the start.
The first execution is considered number 0 and does not generate an activation signal.

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.action_nodes<ext_omni_graph_action_nodes>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Duration (*inputs:duration*)", "``int``", "The duration of the delay in ticks.", "5"
    "Exec In (*inputs:execIn*)", "``execution``", "Signal to the graph that this node is ready to be executed.", "None"
    "Period (*inputs:period*)", "``int``", "The period of the pulse in ticks.", "1"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Alpha (*outputs:alpha*)", "``float``", "On first execution this is set to 0, indicating that there is no progress on the countdown. For every subsequent execution it is set to the normalized progress of the countdown as a value between 0 and 1 computed as 'Tick Value'/'Duration'. After the countdown is complete it keeps a value of 1 until the next time the countdown is reset by activating 'Exec In'.", "None"
    "Finished (*outputs:finished*)", "``execution``", "After 'Duration' ticks of this node have completed since 'Exec In' was activated signal the graph that execution can continue downstream.", "None"
    "Tick (*outputs:tick*)", "``execution``", "Every 'Period' ticks after 'Exec In' has been activated signal the graph that execution can continue downstream.", "None"
    "Tick Value (*outputs:tickValue*)", "``int``", "The current tick value, active in the range [1, 'Duration'].", "None"


State
-----
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Count (*state:count*)", "``int``", "The number of ticks elapsed. The first tick is 0. A value of -1 means execution has not yet been activated.", "-1"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.action.Countdown"
    "Version", "2"
    "Extension", "omni.graph.action_nodes"
    "Has State?", "True"
    "Implementation Language", "Python"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "tests"
    "uiName", "Countdown"
    "Categories", "graph:action,flowControl"
    "Generated Class Name", "OgnCountdownDatabase"
    "Python Module", "omni.graph.action_nodes"

