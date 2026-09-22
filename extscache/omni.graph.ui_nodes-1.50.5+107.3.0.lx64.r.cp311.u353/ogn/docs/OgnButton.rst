.. _omni_graph_ui_nodes_Button_1:

.. _omni_graph_ui_nodes_Button:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Button (BETA)
    :keywords: lang-en omnigraph node internal:test ui_nodes button


Button (BETA)
=============

.. <description>

Create a button widget on the Viewport

.. </description>

Here is an example of a button that was created using the text ``Press Me``:

.. image:: ../../../../../source/extensions/omni.graph.ui_nodes/docs/PressMe.png
    :alt: "Press Me" Button


Installation
------------

To use this node enable :ref:`omni.graph.ui_nodes<ext_omni_graph_ui_nodes>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Create (*inputs:create*)", "``execution``", "Input execution to create and show the widget", "None"
    "Parent Widget Path (*inputs:parentWidgetPath*)", "``token``", "The absolute path to the parent widget.", ""
    "Size (*inputs:size*)", "``double[2]``", "The width and height of the created widget. Value of 0 means the created widget will be just large enough to fit everything.", "[0.0, 0.0]"
    "Start Hidden (*inputs:startHidden*)", "``bool``", "Determines whether the button will initially be visible (False) or not (True).", "False"
    "Style (*inputs:style*)", "``string``", "Style to be applied to the button. This can later be changed with the WriteWidgetStyle node.", "None"
    "Text (*inputs:text*)", "``string``", "The text that is displayed on the button", "None"
    "Widget Identifier (*inputs:widgetIdentifier*)", "``token``", "An optional unique identifier for the widget. Can be used to refer to this widget in other places such as the OnWidgetClicked node.", "None"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Created (*outputs:created*)", "``execution``", "Executed when the widget is created", "None"
    "Widget Path (*outputs:widgetPath*)", "``token``", "The absolute path to the created widget", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.ui_nodes.Button"
    "Version", "1"
    "Extension", "omni.graph.ui_nodes"
    "Has State?", "False"
    "Implementation Language", "Python"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "tests"
    "hidden", "True"
    "uiName", "Button (BETA)"
    "Categories", "internal:test"
    "Generated Class Name", "OgnButtonDatabase"
    "Python Module", "omni.graph.ui_nodes"

Further information on the button operation can be found in the documentation of :py:class:`omni.ui.Button`.

