.. _omni_graph_action_SendCustomEvent_2:

.. _omni_graph_action_SendCustomEvent:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Send Custom Event
    :keywords: lang-en omnigraph node graph:action,event action send-custom-event


Send Custom Event
=================

.. <description>

Sends a custom event, which will asynchronously trigger any 'On Custom Event' nodes which are listening for the same 'Event Name'.

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.action_nodes<ext_omni_graph_action_nodes>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Bundle (*inputs:bundle*)", "``bundle``", "Bundle of data with information that is to be sent with the event. The payload for the event consists of a dictionary whose keys are the names of the attributes in this bundle and whose values are the values of the named attribute in Python pickled format. Optionally the value of the 'Path' attribute is also added to the payload.", "None"
    "Event Name (*inputs:eventName*)", "``token``", "The name of the custom event to be sent out.", ""
    "Exec In (*inputs:execIn*)", "``execution``", "Signal to the graph that this node is ready to be executed.", "None"
    "Path (*inputs:path*)", "``token``", "The path associated with the event. If specified, the path is added to the payload for the event under the dictionary key '!path'.", ""


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Exec Out (*outputs:execOut*)", "``execution``", "Signal to the graph that execution can continue downstream.", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.action.SendCustomEvent"
    "Version", "2"
    "Extension", "omni.graph.action_nodes"
    "Has State?", "True"
    "Implementation Language", "Python"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Send Custom Event"
    "Categories", "graph:action,event"
    "Generated Class Name", "OgnSendCustomEventDatabase"
    "Python Module", "omni.graph.action_nodes"

