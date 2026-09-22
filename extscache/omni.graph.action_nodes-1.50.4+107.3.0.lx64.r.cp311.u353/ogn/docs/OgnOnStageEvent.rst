.. _omni_graph_action_OnStageEvent_4:

.. _omni_graph_action_OnStageEvent:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: On Stage Event
    :keywords: lang-en omnigraph node graph:action,event compute-on-request action on-stage-event


On Stage Event
==============

.. <description>

Activates the downstream graph execution when the specified 'Event Name' from the Stage occurs. Stage Events are emitted when certain USD stage-related actions are performed by the system:
Saved: USD file saved.
Selection Changed: USD Prim selection has changed.
Hierarchy Changed: USD stage hierarchy has changed, e.g. a prim is added, deleted or moved.
OmniGraph Start Play: OmniGraph started.
OmniGraph Stop Play: OmniGraph stopped.
Simulation Start Play: Simulation started.
Simulation Stop Play: Simulation stopped.
Animation Start Play: Animation playback has started.
Animation Stop Play: Animation playback has stopped.

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.action_nodes<ext_omni_graph_action_nodes>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Event Name (*inputs:eventName*)", "``token``", "The event of interest", ""
    "", "Metadata", "*allowedTokens* = Saved,Selection Changed,Hierarchy Changed,OmniGraph Start Play,OmniGraph Stop Play,Simulation Start Play,Simulation Stop Play,Animation Start Play,Animation Stop Play", ""
    "", "Metadata", "*default* = Animation Start Play", ""
    "", "Metadata", "*displayGroup* = parameters", ""
    "", "Metadata", "*literalOnly* = 1", ""
    "Only Simulate On Play (*inputs:onlyPlayback*)", "``bool``", "When true, the node is only executed while the Stage is being played.", "True"
    "", "Metadata", "*literalOnly* = 1", ""


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Exec Out (*outputs:execOut*)", "``execution``", "After the stage event is received, signal to the graph that execution can continue downstream.", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.action.OnStageEvent"
    "Version", "4"
    "Extension", "omni.graph.action_nodes"
    "Has State?", "True"
    "Implementation Language", "Python"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "On Stage Event"
    "Categories", "graph:action,event"
    "Generated Class Name", "OgnOnStageEventDatabase"
    "Python Module", "omni.graph.action_nodes"

