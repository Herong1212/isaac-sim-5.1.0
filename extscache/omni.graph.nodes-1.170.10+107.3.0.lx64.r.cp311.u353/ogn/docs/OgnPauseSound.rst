.. _omni_graph_nodes_PauseSound_1:

.. _omni_graph_nodes_PauseSound:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Pause Sound
    :keywords: lang-en omnigraph node sound nodes pause-sound


Pause Sound
===========

.. <description>

Pause-unpause playing a sound

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

    "Unique ID", "omni.graph.nodes.PauseSound"
    "Version", "1"
    "Extension", "omni.graph.nodes"
    "Icon", "ogn/icons/omni.graph.nodes.PauseSound.svg"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Pause Sound"
    "Categories", "sound"
    "Generated Class Name", "OgnPauseSoundDatabase"
    "Python Module", "omni.graph.nodes"

