.. _omni_graph_ui_nodes_SetViewportRenderer_1:

.. _omni_graph_ui_nodes_SetViewportRenderer:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Set Viewport Renderer
    :keywords: lang-en omnigraph node graph:action,viewport ui_nodes set-viewport-renderer


Set Viewport Renderer
=====================

.. <description>

Sets renderer for the target viewport.

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.ui_nodes<ext_omni_graph_ui_nodes>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Exec (*inputs:exec*)", "``execution``", "Signal to the graph that this node is ready to be executed.", "None"
    "Renderer (*inputs:renderer*)", "``token``", "Renderer to be assigned to the target viewport", ""
    "Viewport (*inputs:viewport*)", "``token``", "Name of the viewport, or empty for the default viewport", "Viewport"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Exec (*outputs:exec*)", "``execution``", "Signal to the graph that execution can continue downstream.", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.ui_nodes.SetViewportRenderer"
    "Version", "1"
    "Extension", "omni.graph.ui_nodes"
    "Has State?", "False"
    "Implementation Language", "Python"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "tests"
    "uiName", "Set Viewport Renderer"
    "Categories", "graph:action,viewport"
    "Generated Class Name", "OgnSetViewportRendererDatabase"
    "Python Module", "omni.graph.ui_nodes"

