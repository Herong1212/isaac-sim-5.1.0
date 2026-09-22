.. _omni_replicator_core_OgnGetPrimAtPath_1:

.. _omni_replicator_core_OgnGetPrimAtPath:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Get Prim at Path
    :keywords: lang-en omnigraph node Replicator:Core compute-on-request core ogn-get-prim-at-path


Get Prim at Path
================

.. <description>

This node searches the stage by path and returns a prim in that path.

.. </description>


Installation
------------

To use this node enable :ref:`omni.replicator.core<ext_omni_replicator_core>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Exec In (*inputs:execIn*)", "``execution``", "exec", "None"
    "Paths (*inputs:paths*)", "``token[]``", "The path to the desired prim.", "[]"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Exec Out (*outputs:execOut*)", "``execution``", "exec", "None"
    "Prims (*outputs:prims*)", "``target``", "Prim paths from search result.", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.replicator.core.OgnGetPrimAtPath"
    "Version", "1"
    "Extension", "omni.replicator.core"
    "Has State?", "True"
    "Implementation Language", "Python"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Get Prim at Path"
    "Categories", "Replicator:Core"
    "__categoryDescriptions", "Replicator:Core,Core Replicator nodes"
    "Generated Class Name", "OgnGetPrimAtPathDatabase"
    "Python Module", "omni.replicator.core"

