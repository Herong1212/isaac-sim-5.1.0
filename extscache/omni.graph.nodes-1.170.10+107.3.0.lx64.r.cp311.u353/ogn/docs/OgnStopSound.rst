.. _omni_graph_nodes_StopSound_1:

.. _omni_graph_nodes_StopSound:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Stop Sound
    :keywords: lang-en omnigraph node sound nodes stop-sound


Stop Sound
==========

.. <description>

Stop playing a sound primitive

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.nodes<ext_omni_graph_nodes>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Exec In (*inputs:execIn*)", "``execution``", "Signal to the graph that this node is ready to be executed.", "None"
    "Sound Id (*inputs:soundId*)", "``uint64``", "The sound identifier", "0"


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

    "Unique ID", "omni.graph.nodes.StopSound"
    "Version", "1"
    "Extension", "omni.graph.nodes"
    "Icon", "ogn/icons/omni.graph.nodes.StopSound.svg"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Stop Sound"
    "Categories", "sound"
    "Generated Class Name", "OgnStopSoundDatabase"
    "Python Module", "omni.graph.nodes"

