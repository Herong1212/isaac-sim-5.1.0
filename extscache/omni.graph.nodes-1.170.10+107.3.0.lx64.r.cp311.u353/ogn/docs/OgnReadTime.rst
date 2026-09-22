.. _omni_graph_nodes_ReadTime_1:

.. _omni_graph_nodes_ReadTime:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Read Time
    :keywords: lang-en omnigraph node time threadsafe nodes read-time


Read Time
=========

.. <description>

Holds the values related to the current global time and the timeline.

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.nodes<ext_omni_graph_nodes>` in the Extension Manager.


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Absolute Simulation Time (Seconds) (*outputs:absoluteSimTime*)", "``double``", "The accumulated total of elapsed times between rendered frames.", "None"
    "Delta (Seconds) (*outputs:deltaSeconds*)", "``double``", "The number of seconds elapsed since the last OmniGraph update.", "None"
    "Animation Time (Frames) (*outputs:frame*)", "``double``", "The global animation time in frames, equivalent to (time * fps), during playback.", "None"
    "Is Playing (*outputs:isPlaying*)", "``bool``", "True during global animation timeline playback.", "None"
    "Animation Time (Seconds) (*outputs:time*)", "``double``", "The global animation time in seconds during playback.", "None"
    "Time Since Start (Seconds) (*outputs:timeSinceStart*)", "``double``", "Elapsed time since the App started.", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.nodes.ReadTime"
    "Version", "1"
    "Extension", "omni.graph.nodes"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Read Time"
    "Categories", "time"
    "Generated Class Name", "OgnReadTimeDatabase"
    "Python Module", "omni.graph.nodes"

