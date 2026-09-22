.. _omni_graph_ui_nodes_SetViewportResolution_1:

.. _omni_graph_ui_nodes_SetViewportResolution:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Set Viewport Resolution
    :keywords: lang-en omnigraph node graph:action,viewport ui_nodes set-viewport-resolution


Set Viewport Resolution
=======================

.. <description>

Sets the resolution of the target viewport.

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
    "Resolution (*inputs:resolution*)", "``int[2]``", "The new resolution of the target viewport", "[512, 512]"
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

    "Unique ID", "omni.graph.ui_nodes.SetViewportResolution"
    "Version", "1"
    "Extension", "omni.graph.ui_nodes"
    "Has State?", "False"
    "Implementation Language", "Python"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "tests"
    "uiName", "Set Viewport Resolution"
    "Categories", "graph:action,viewport"
    "Generated Class Name", "OgnSetViewportResolutionDatabase"
    "Python Module", "omni.graph.ui_nodes"

