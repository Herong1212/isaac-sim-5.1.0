.. _omni_graph_ui_nodes_SetViewportMode_1:

.. _omni_graph_ui_nodes_SetViewportMode:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Set Viewport Mode (BETA)
    :keywords: lang-en omnigraph node graph:action,ui ui_nodes set-viewport-mode


Set Viewport Mode (BETA)
========================

.. <description>

Sets the mode of a specified viewport window to 'Scripted' mode or 'Default' mode when executed.
'Scripted' mode disables default viewport interaction and enables placing UI elements over the viewport. 'Default' mode is the default state of the viewport, and entering it will destroy any UI elements on the viewport.
Executing with 'Enable Viewport Mouse Events' set to true in 'Scripted' mode is required to allow the specified viewport to be targeted by viewport mouse event nodes, including 'On Viewport Dragged' and 'Read Viewport Drag State'.
Executing with 'Enable Picking' set to true in 'Scripted' mode is required to allow the specified viewport to be targeted by the 'On Picked' and 'Read Pick State' nodes.

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.ui_nodes<ext_omni_graph_ui_nodes>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Enable Picking (*inputs:enablePicking*)", "``bool``", "Enable/Disable picking prims in the specified viewport when in 'Scripted' mode", "False"
    "Enable Viewport Mouse Events (*inputs:enableViewportMouseEvents*)", "``bool``", "Enable/Disable viewport mouse events on the specified viewport when in 'Scripted' mode", "False"
    "Exec In (*inputs:execIn*)", "``execution``", "Signal to the graph that this node is ready to be executed.", "None"
    "Mode (*inputs:mode*)", "``int``", "The mode to set the specified viewport to when this node is executed (0: 'Default', 1: 'Scripted')", "0"
    "Pass Clicks Thru (*inputs:passClicksThru*)", "``bool``", "Allow mouse clicks to affect the viewport while in 'Scripted' mode.  In 'Scripted' mode mouse clicks are prevented from reaching the viewport to avoid accidentally selecting prims or interacting with the viewport's own UI. Setting this attribute true will allow clicks to reach the viewport. This is in addition to interacting with the widgets created by UI nodes so if a button widget appears on top of some geometry in the viewport, clicking on the button will not only trigger the button but could also select the geometry. To avoid this, put the button inside a Stack widget and use a WriteWidgetProperty node to set the Stack's 'content_clipping' property to 1.", "False"
    "Viewport (*inputs:viewport*)", "``token``", "Name of the viewport window to set the mode of", "Viewport"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Default Mode (*outputs:defaultMode*)", "``execution``", "When this node is successfully executed with 'Mode' set to 'Default', signal to the graph that execution can continue downstream on this path.", "None"
    "Scripted Mode (*outputs:scriptedMode*)", "``execution``", "When this node is successfully executed with 'Mode' set to 'Scripted', signal to the graph that execution can continue downstream on this path.", "None"
    "Widget Path (*outputs:widgetPath*)", "``token``", "When the viewport enters 'Scripted' mode, a container widget is created under which other UI may be parented. This attribute provides the absolute path to that widget, which can be used as the 'parentWidgetPath' input to various UI nodes, such as Button. When the viewport exits 'Scripted' mode, the container widget and all the UI within it will be destroyed.", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.ui_nodes.SetViewportMode"
    "Version", "1"
    "Extension", "omni.graph.ui_nodes"
    "Has State?", "False"
    "Implementation Language", "Python"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "tests"
    "uiName", "Set Viewport Mode (BETA)"
    "Categories", "graph:action,ui"
    "Generated Class Name", "OgnSetViewportModeDatabase"
    "Python Module", "omni.graph.ui_nodes"

