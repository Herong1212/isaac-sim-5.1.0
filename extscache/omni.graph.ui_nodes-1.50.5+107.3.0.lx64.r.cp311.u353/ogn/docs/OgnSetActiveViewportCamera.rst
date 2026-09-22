.. _omni_graph_ui_nodes_SetActiveViewportCamera_1:

.. _omni_graph_ui_nodes_SetActiveViewportCamera:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Set Active Camera
    :keywords: lang-en omnigraph node sceneGraph:camera ReadOnly ui_nodes set-active-viewport-camera


Set Active Camera
=================

.. <description>

Sets Viewport's actively bound camera to given camera at give path

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.ui_nodes<ext_omni_graph_ui_nodes>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "In (*inputs:execIn*)", "``execution``", "Signal to the graph that this node is ready to be executed.", "None"
    "Camera Path (*inputs:primPath*)", "``token``", "Path of the camera to bind", ""
    "Viewport (*inputs:viewport*)", "``token``", "Name of the viewport, or empty for the default viewport", ""


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Out (*outputs:execOut*)", "``execution``", "Signal to the graph that execution can continue downstream.", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.ui_nodes.SetActiveViewportCamera"
    "Version", "1"
    "Extension", "omni.graph.ui_nodes"
    "Has State?", "False"
    "Implementation Language", "Python"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "tests"
    "uiName", "Set Active Camera"
    "Categories", "sceneGraph:camera"
    "Generated Class Name", "OgnSetActiveViewportCameraDatabase"
    "Python Module", "omni.graph.ui_nodes"

