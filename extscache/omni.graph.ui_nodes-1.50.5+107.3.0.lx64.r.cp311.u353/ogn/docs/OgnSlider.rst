.. _omni_graph_ui_nodes_Slider_1:

.. _omni_graph_ui_nodes_Slider:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Slider (BETA)
    :keywords: lang-en omnigraph node internal:test ui_nodes slider


Slider (BETA)
=============

.. <description>

Create a slider widget on the Viewport

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.ui_nodes<ext_omni_graph_ui_nodes>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Create (*inputs:create*)", "``execution``", "Signal to the graph that this node is ready to create and show the widget.", "None"
    "Disable (*inputs:disable*)", "``execution``", "Signal to the graph that this node is ready to disable this button so that it cannot be pressed.", "None"
    "Enable (*inputs:enable*)", "``execution``", "Signal to the graph that this node is ready enable this button after it has been disabled.", "None"
    "Hide (*inputs:hide*)", "``execution``", "Signal to the graph that this node is ready to hide the widget and all its child widgets.", "None"
    "Max (*inputs:max*)", "``float``", "The maximum value of the slider", "0.0"
    "Min (*inputs:min*)", "``float``", "The minimum value of the slider", "0.0"
    "Parent Widget Path (*inputs:parentWidgetPath*)", "``token``", "The absolute path to the parent widget. If empty, this widget will be created as a direct child of Viewport.", "None"
    "Show (*inputs:show*)", "``execution``", "Signal to the graph that this node is ready to show the widget and all its child widgets after they become hidden.", "None"
    "Step (*inputs:step*)", "``float``", "The step size of the slider", "0.01"
    "Tear Down (*inputs:tearDown*)", "``execution``", "Signal to the graph that this node is ready to tear down the widget and all its child widgets.", "None"
    "Widget Identifier (*inputs:widgetIdentifier*)", "``token``", "An optional unique identifier for the widget. Can be used to refer to this widget in other places such as the OnWidgetClicked node.", "None"
    "Width (*inputs:width*)", "``double``", "The width of the created slider", "100.0"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Created (*outputs:created*)", "``execution``", "When the widget is created, signal to the graph that execution can continue downstream.", "None"
    "Widget Path (*outputs:widgetPath*)", "``token``", "The absolute path to the created widget", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.ui_nodes.Slider"
    "Version", "1"
    "Extension", "omni.graph.ui_nodes"
    "Has State?", "False"
    "Implementation Language", "Python"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "tests"
    "hidden", "True"
    "uiName", "Slider (BETA)"
    "Categories", "internal:test"
    "Generated Class Name", "OgnSliderDatabase"
    "Python Module", "omni.graph.ui_nodes"

