.. _omni_graph_ui_nodes_OnWidgetValueChanged_1:

.. _omni_graph_ui_nodes_OnWidgetValueChanged:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: On Widget Value Changed (BETA)
    :keywords: lang-en omnigraph node internal:test compute-on-request ui_nodes on-widget-value-changed


On Widget Value Changed (BETA)
==============================

.. <description>

Event node which fires when a UI widget with the specified identifier has its value changed. This node should be used in combination with UI creation nodes such as OgnSlider.

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.ui_nodes<ext_omni_graph_ui_nodes>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Widget Identifier (*inputs:widgetIdentifier*)", "``token``", "A unique identifier identifying the widget. This should be specified in the UI creation node such as OgnSlider.", ""
    "", "Metadata", "*literalOnly* = 1", ""


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "New Value (*outputs:newValue*)", "``['bool', 'float', 'int', 'string']``", "The new value of the widget", "None"
    "Value Changed (*outputs:valueChanged*)", "``execution``", "When the value of the widget is changed, signal to the graph that execution can continue downstream.", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.ui_nodes.OnWidgetValueChanged"
    "Version", "1"
    "Extension", "omni.graph.ui_nodes"
    "Has State?", "True"
    "Implementation Language", "Python"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "tests"
    "hidden", "True"
    "uiName", "On Widget Value Changed (BETA)"
    "Categories", "internal:test"
    "Generated Class Name", "OgnOnWidgetValueChangedDatabase"
    "Python Module", "omni.graph.ui_nodes"

