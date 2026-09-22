.. _omni_graph_action_LogMessage_1:

.. _omni_graph_action_LogMessage:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Log Message
    :keywords: lang-en omnigraph node function threadsafe action log-message


Log Message
===========

.. <description>

Logs a string message to a carb logging channel

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.action_nodes_core<ext_omni_graph_action_nodes_core>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Channel (*inputs:channel*)", "``token``", "The channel to push the message to", "omni.graph.nodes_core.plugin"
    "", "Metadata", "*literalOnly* = 1", ""
    "Exec In (*inputs:execIn*)", "``execution``", "Signal to the graph that this node is ready to be executed.", "None"
    "Log Level (*inputs:logLevel*)", "``token``", "The logging level for the message [Verbose, Info, Warn, Error]", "Info"
    "", "Metadata", "*allowedTokens* = Verbose,Info,Warn,Error", ""
    "Message (*inputs:message*)", "``string``", "The message to log", ""


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

    "Unique ID", "omni.graph.action.LogMessage"
    "Version", "1"
    "Extension", "omni.graph.action_nodes_core"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Log Message"
    "Categories", "function"
    "Generated Class Name", "OgnLogMessageDatabase"
    "Python Module", "omni.graph.action_nodes_core"

