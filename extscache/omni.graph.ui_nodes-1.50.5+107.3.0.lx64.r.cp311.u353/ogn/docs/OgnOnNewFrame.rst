.. _omni_graph_ui_nodes_OnNewFrame_1:

.. _omni_graph_ui_nodes_OnNewFrame:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: On New Frame
    :keywords: lang-en omnigraph node graph:action,event compute-on-request ui_nodes on-new-frame


On New Frame
============

.. <description>

Triggers when there is a new frame available for the given viewport. Note that the graph will run asynchronously to the new frame event

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
    "", "Metadata", "*displayGroup* = parameters", ""


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Exec Out (*outputs:execOut*)", "``execution``", "Signal to the graph that execution can continue downstream.", "None"
    "Frame Number (*outputs:frameNumber*)", "``int``", "The number of the frame which is available", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.ui_nodes.OnNewFrame"
    "Version", "1"
    "Extension", "omni.graph.ui_nodes"
    "Has State?", "True"
    "Implementation Language", "Python"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "tests"
    "uiName", "On New Frame"
    "Categories", "graph:action,event"
    "Generated Class Name", "OgnOnNewFrameDatabase"
    "Python Module", "omni.graph.ui_nodes"

