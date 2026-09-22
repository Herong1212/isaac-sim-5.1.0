.. _omni_graph_nodes_SetTimeline_1:

.. _omni_graph_nodes_SetTimeline:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Set main timeline
    :keywords: lang-en omnigraph node time compute-on-request nodes set-timeline


Set main timeline
=================

.. <description>

Set properties of the main timeline

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.nodes<ext_omni_graph_nodes>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Execute In (*inputs:execIn*)", "``execution``", "Signal to the graph that this node is ready to be executed.", "None"
    "Property Name (*inputs:propName*)", "``token``", "The name of the property to set.", "Frame"
    "", "Metadata", "*displayGroup* = parameters", ""
    "", "Metadata", "*literalOnly* = 1", ""
    "", "Metadata", "*allowedTokens* = Frame,Time,StartFrame,StartTime,EndFrame,EndTime,FramesPerSecond", ""
    "Property Value (*inputs:propValue*)", "``double``", "The value of the property to set.", "0.0"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Clamp to range (*outputs:clamped*)", "``bool``", "Was the input frame or time clamped to the playback range?", "None"
    "Execute Out (*outputs:execOut*)", "``execution``", "Signal to the graph that execution can continue downstream.", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.nodes.SetTimeline"
    "Version", "1"
    "Extension", "omni.graph.nodes"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Set main timeline"
    "Categories", "time"
    "Generated Class Name", "OgnTimelineSetDatabase"
    "Python Module", "omni.graph.nodes"

