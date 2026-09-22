.. _omni_graph_ui_nodes_LockViewportRender_1:

.. _omni_graph_ui_nodes_LockViewportRender:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Lock Viewport Render
    :keywords: lang-en omnigraph node graph:action,viewport ui_nodes lock-viewport-render


Lock Viewport Render
====================

.. <description>

Locks and unlocks viewport render. Viewport render is frozen at the frame when it is locked, while computation and UI update are still executed as normal. It fades out back to the current frame when it is unlocked, two output execution attributes - fadeStarted and fadeComplete - will be triggered separately during the fading progress. The node manages the lock state for its target viewport and takes action according to the lock state when an input execution attribute is triggered. A node is able to unlock the target viewort only if it has locked the target viewport.

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.ui_nodes<ext_omni_graph_ui_nodes>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Fade Time (*inputs:fadeTime*)", "``double``", "The duration of fading in time (seconds) when being unlocked", "1.0"
    "Lock (*inputs:lock*)", "``execution``", "Signal to the graph that this node is ready to be executed for locking the viewport render.", "None"
    "Unlock (*inputs:unlock*)", "``execution``", "Signal to the graph that this node is ready to be executed for unlocking the viewport render.", "None"
    "Viewport (*inputs:viewport*)", "``token``", "Name of the viewport, or empty for the default viewport", ""


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Fade Complete (*outputs:fadeComplete*)", "``execution``", "When fading is complete, signal to the graph that execution can continue downstream on this path.", "None"
    "Fade Started (*outputs:fadeStarted*)", "``execution``", "When fading is started, signal to the graph that execution can continue downstream on this path.", "None"
    "Locked (*outputs:locked*)", "``execution``", "When viewport render is locked, signal to the graph that execution can continue downstream on this path.", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.ui_nodes.LockViewportRender"
    "Version", "1"
    "Extension", "omni.graph.ui_nodes"
    "Has State?", "False"
    "Implementation Language", "Python"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "tests"
    "uiName", "Lock Viewport Render"
    "Categories", "graph:action,viewport"
    "Generated Class Name", "OgnLockViewportRenderDatabase"
    "Python Module", "omni.graph.ui_nodes"

