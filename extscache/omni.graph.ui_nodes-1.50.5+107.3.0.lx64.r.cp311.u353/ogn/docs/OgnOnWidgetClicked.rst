.. _omni_graph_ui_nodes_OnWidgetClicked_1:

.. _omni_graph_ui_nodes_OnWidgetClicked:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: On Widget Clicked (BETA)
    :keywords: lang-en omnigraph node internal:test compute-on-request ui_nodes on-widget-clicked


On Widget Clicked (BETA)
========================

.. <description>

Event node which fires when a UI widget with the specified identifier is clicked. This node should be used in combination with UI creation nodes such as OgnButton.

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.ui_nodes<ext_omni_graph_ui_nodes>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Widget Identifier (*inputs:widgetIdentifier*)", "``token``", "A unique identifier identifying the widget. This should be specified in the UI creation node such as OgnButton.", ""
    "", "Metadata", "*literalOnly* = 1", ""


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Clicked (*outputs:clicked*)", "``execution``", "When the widget is clicked, signal to the graph that execution can continue downstream.", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.ui_nodes.OnWidgetClicked"
    "Version", "1"
    "Extension", "omni.graph.ui_nodes"
    "Has State?", "True"
    "Implementation Language", "Python"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "tests"
    "hidden", "True"
    "uiName", "On Widget Clicked (BETA)"
    "Categories", "internal:test"
    "Generated Class Name", "OgnOnWidgetClickedDatabase"
    "Python Module", "omni.graph.ui_nodes"

