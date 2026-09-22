.. _omni_graph_nodes_ReadGamepadState_1:

.. _omni_graph_nodes_ReadGamepadState:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Read Gamepad State
    :keywords: lang-en omnigraph node input:gamepad threadsafe nodes read-gamepad-state


Read Gamepad State
==================

.. <description>

Reads the current state of the ID-specified gamepad device (i.e. which buttons are being pressed, the orientation of the joystick(s), etc.).

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.nodes<ext_omni_graph_nodes>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Deadzone (*inputs:deadzone*)", "``float``", "Threshold from [0, 1] that the value must pass for it to be registered as input.", "0.1"
    "Element (*inputs:gamepadElement*)", "``token``", "The gamepad element whose state is to be checked.", "Left Stick X Axis"
    "", "Metadata", "*displayGroup* = parameters", ""
    "", "Metadata", "*allowedTokens* = Left Stick X Axis,Left Stick Y Axis,Right Stick X Axis,Right Stick Y Axis,Left Trigger,Right Trigger,Face Button Bottom,Face Button Right,Face Button Left,Face Button Top,Left Shoulder,Right Shoulder,Special Left,Special Right,Left Stick Button,Right Stick Button,D-Pad Up,D-Pad Right,D-Pad Down,D-Pad Left", ""
    "Gamepad ID (*inputs:gamepadId*)", "``uint``", "Gamepad ID number starting from 0. Used to identify a given gamepad device.", "0"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Is Pressed (*outputs:isPressed*)", "``bool``", "True if the gamepad element is currently pressed, false otherwise.", "None"
    "Value (*outputs:value*)", "``float``", "Value denoting how ""much"" the gamepad element is being pressed. Valid ranges are [0, 1] for buttons and [-1, 1] for stick and trigger.", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.nodes.ReadGamepadState"
    "Version", "1"
    "Extension", "omni.graph.nodes"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Read Gamepad State"
    "Categories", "input:gamepad"
    "Generated Class Name", "OgnReadGamepadStateDatabase"
    "Python Module", "omni.graph.nodes"

