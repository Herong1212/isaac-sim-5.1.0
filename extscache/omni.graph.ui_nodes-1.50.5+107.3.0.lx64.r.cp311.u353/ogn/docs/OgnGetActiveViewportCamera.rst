.. _omni_graph_ui_nodes_GetActiveViewportCamera_2:

.. _omni_graph_ui_nodes_GetActiveViewportCamera:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Get Active Camera
    :keywords: lang-en omnigraph node sceneGraph:camera ui_nodes get-active-viewport-camera


Get Active Camera
=================

.. <description>

Gets the path of the camera bound to a viewport

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.ui_nodes<ext_omni_graph_ui_nodes>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Viewport (*inputs:viewport*)", "``token``", "Name of the viewport, or empty for the default viewport", ""


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Camera (*outputs:camera*)", "``token``", "Path of the active camera", "None"
    "Camera Prim (*outputs:cameraPrim*)", "``target``", "The prim of the active camera", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.ui_nodes.GetActiveViewportCamera"
    "Version", "2"
    "Extension", "omni.graph.ui_nodes"
    "Has State?", "False"
    "Implementation Language", "Python"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "tests"
    "uiName", "Get Active Camera"
    "Categories", "sceneGraph:camera"
    "Generated Class Name", "OgnGetActiveViewportCameraDatabase"
    "Python Module", "omni.graph.ui_nodes"

