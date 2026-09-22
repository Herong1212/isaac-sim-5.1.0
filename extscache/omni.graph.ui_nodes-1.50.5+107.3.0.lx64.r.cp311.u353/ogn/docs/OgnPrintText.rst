.. _omni_graph_ui_nodes_PrintText_1:

.. _omni_graph_ui_nodes_PrintText:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Print Text
    :keywords: lang-en omnigraph node debug ui_nodes print-text


Print Text
==========

.. <description>

Prints some text to the system log or to the screen

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.ui_nodes<ext_omni_graph_ui_nodes>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "In (*inputs:execIn*)", "``execution``", "Signal to the graph that this node is ready to be executed.", "None"
    "Log Level (*inputs:logLevel*)", "``token``", "The logging level for the message [Info, Warning, Error]", "Info"
    "", "Metadata", "*allowedTokens* = Info,Warning,Error", ""
    "Text (*inputs:text*)", "``string``", "The text to print", ""
    "To Screen (*inputs:toScreen*)", "``bool``", "When true, displays the text on the viewport for a few seconds, as well as the log", "False"
    "Viewport (*inputs:viewport*)", "``token``", "Name of the viewport if printing to screen, or empty for the default viewport", ""


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Out (*outputs:execOut*)", "``execution``", "Signal to the graph that execution can continue downstream.", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.ui_nodes.PrintText"
    "Version", "1"
    "Extension", "omni.graph.ui_nodes"
    "Has State?", "False"
    "Implementation Language", "Python"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "tests"
    "tags", "logging,toast,debug"
    "uiName", "Print Text"
    "Categories", "debug"
    "Generated Class Name", "OgnPrintTextDatabase"
    "Python Module", "omni.graph.ui_nodes"

