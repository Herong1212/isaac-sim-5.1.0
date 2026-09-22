.. _omni_graph_action_ExitApplication_1:

.. _omni_graph_action_ExitApplication:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Exit Application
    :keywords: lang-en omnigraph node graph:action,flowControl action exit-application


Exit Application
================

.. <description>

Immediately exits the application. Uses a fast shutdown to avoid any cleanup that would otherwise be triggered.

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.action_nodes<ext_omni_graph_action_nodes>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Exec In (*inputs:execIn*)", "``execution``", "Signal to the graph that this node is ready to be executed, exiting the application.", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.action.ExitApplication"
    "Version", "1"
    "Extension", "omni.graph.action_nodes"
    "Has State?", "False"
    "Implementation Language", "Python"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "tests"
    "uiName", "Exit Application"
    "Categories", "graph:action,flowControl"
    "Generated Class Name", "OgnExitApplicationDatabase"
    "Python Module", "omni.graph.action_nodes"

