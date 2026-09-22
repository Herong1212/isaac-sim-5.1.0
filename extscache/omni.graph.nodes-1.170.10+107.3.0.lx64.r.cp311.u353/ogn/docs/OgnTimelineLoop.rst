.. _omni_graph_nodes_LoopTimeline_1:

.. _omni_graph_nodes_LoopTimeline:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Set playback looping
    :keywords: lang-en omnigraph node time compute-on-request nodes loop-timeline


Set playback looping
====================

.. <description>

Controls looping playback of the main timeline

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
    "Loop (*inputs:loop*)", "``bool``", "Enable or disable playback looping?", "False"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Execute Out (*outputs:execOut*)", "``execution``", "Signal to the graph that execution can continue downstream.", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.nodes.LoopTimeline"
    "Version", "1"
    "Extension", "omni.graph.nodes"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Set playback looping"
    "Categories", "time"
    "Generated Class Name", "OgnTimelineLoopDatabase"
    "Python Module", "omni.graph.nodes"

