.. _omni_graph_action_OnCustomEvent_3:

.. _omni_graph_action_OnCustomEvent:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: On Custom Event
    :keywords: lang-en omnigraph node graph:action,event compute-on-request action on-custom-event


On Custom Event
===============

.. <description>

Event node which fires when the specified custom event is sent. This node is used in combination with 'omni.graph.action.SendCustomEvent'.

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.action_nodes<ext_omni_graph_action_nodes>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Event Name (*inputs:eventName*)", "``token``", "The name of the custom event.", ""
    "", "Metadata", "*literalOnly* = 1", ""
    "Only Simulate On Play (*inputs:onlyPlayback*)", "``bool``", "When true, the node is only executed while the Stage is being played.", "True"
    "", "Metadata", "*literalOnly* = 1", ""


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Bundle (*outputs:bundle*)", "``bundle``", "Bundle received with the event. The contents of the bundle are determined by the input bundle given to the corresponding 'SendCustomEvent' node.", "None"
    "Received (*outputs:execOut*)", "``execution``", "When the custom event was received signal to the graph that execution can continue downstream.", "None"
    "Path (*outputs:path*)", "``token``", "The path associated with the received custom event", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.action.OnCustomEvent"
    "Version", "3"
    "Extension", "omni.graph.action_nodes"
    "Has State?", "True"
    "Implementation Language", "Python"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "On Custom Event"
    "Categories", "graph:action,event"
    "Generated Class Name", "OgnOnCustomEventDatabase"
    "Python Module", "omni.graph.action_nodes"

