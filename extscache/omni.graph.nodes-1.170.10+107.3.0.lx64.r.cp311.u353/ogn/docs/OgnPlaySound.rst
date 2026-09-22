.. _omni_graph_nodes_PlaySound_2:

.. _omni_graph_nodes_PlaySound:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Play Sound
    :keywords: lang-en omnigraph node sound nodes play-sound


Play Sound
==========

.. <description>

Plays a sound

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
    "Prim (*inputs:prim*)", "``target``", "The sound Prim to play", "None"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Exec Out (*outputs:execOut*)", "``execution``", "Signal to the graph that execution can continue downstream.", "None"
    "Sound Id (*outputs:soundId*)", "``uint64``", "The sound identifier", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.nodes.PlaySound"
    "Version", "2"
    "Extension", "omni.graph.nodes"
    "Icon", "ogn/icons/omni.graph.nodes.PlaySound.svg"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "tests"
    "uiName", "Play Sound"
    "Categories", "sound"
    "Generated Class Name", "OgnPlaySoundDatabase"
    "Python Module", "omni.graph.nodes"

