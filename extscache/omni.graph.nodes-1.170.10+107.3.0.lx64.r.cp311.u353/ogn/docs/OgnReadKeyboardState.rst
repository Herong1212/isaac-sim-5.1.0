.. _omni_graph_nodes_ReadKeyboardState_1:

.. _omni_graph_nodes_ReadKeyboardState:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Read Keyboard State
    :keywords: lang-en omnigraph node input:keyboard threadsafe nodes read-keyboard-state


Read Keyboard State
===================

.. <description>

Reads the current state of the keyboard (i.e. which keys or combination of keys on the associated keyboard are pressed).

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.nodes<ext_omni_graph_nodes>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Key (*inputs:key*)", "``token``", "The key on the keyboard whose state is to be checked.", "A"
    "", "Metadata", "*displayGroup* = parameters", ""
    "", "Metadata", "*allowedTokens* = A,B,C,D,E,F,G,H,I,J,K,L,M,N,O,P,Q,R,S,T,U,V,W,X,Y,Z,Apostrophe,Backslash,Backspace,CapsLock,Comma,Del,Down,End,Enter,Equal,Escape,F1,F10,F11,F12,F2,F3,F4,F5,F6,F7,F8,F9,GraveAccent,Home,Insert,Key0,Key1,Key2,Key3,Key4,Key5,Key6,Key7,Key8,Key9,Left,LeftAlt,LeftBracket,LeftControl,LeftShift,LeftSuper,Menu,Minus,NumLock,Numpad0,Numpad1,Numpad2,Numpad3,Numpad4,Numpad5,Numpad6,Numpad7,Numpad8,Numpad9,NumpadAdd,NumpadDel,NumpadDivide,NumpadEnter,NumpadEqual,NumpadMultiply,NumpadSubtract,PageDown,PageUp,Pause,Period,PrintScreen,Right,RightAlt,RightBracket,RightControl,RightShift,RightSuper,ScrollLock,Semicolon,Slash,Space,Tab,Up", ""


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Alt (*outputs:altOut*)", "``bool``", "True if any Alt key on the keyboard is held.", "None"
    "Ctrl (*outputs:ctrlOut*)", "``bool``", "True if any Ctrl key on the keyboard is held.", "None"
    "Is Pressed (*outputs:isPressed*)", "``bool``", "True if the key is currently pressed, false otherwise.", "None"
    "Shift (*outputs:shiftOut*)", "``bool``", "True if any Shift key on the keyboard is held.", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.nodes.ReadKeyboardState"
    "Version", "1"
    "Extension", "omni.graph.nodes"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Read Keyboard State"
    "Categories", "input:keyboard"
    "Generated Class Name", "OgnReadKeyboardStateDatabase"
    "Python Module", "omni.graph.nodes"

