.. _omni_replicator_core_OgnGetPrims_1:

.. _omni_replicator_core_OgnGetPrims:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Get Prims
    :keywords: lang-en omnigraph node Replicator:Core compute-on-request core ogn-get-prims


Get Prims
=========

.. <description>

This node searches the stage by path and returns a list of prims.

.. </description>


Installation
------------

To use this node enable :ref:`omni.replicator.core<ext_omni_replicator_core>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Cache Prims (*inputs:cachePrims*)", "``bool``", "If set to True, the stage is parsed only once.", "True"
    "Exec In (*inputs:execIn*)", "``execution``", "exec", "None"
    "Ignore Case (*inputs:ignoreCase*)", "``bool``", "If set to True, use case-insensitive matching.", "True"
    "Path Match (*inputs:pathMatch*)", "``string``", "The path substring to match", ""
    "Path Pattern (*inputs:pathPattern*)", "``string``", "The RegEx (Regular Expression) path pattern to match", ""
    "Path Pattern Exclusion (*inputs:pathPatternExclusion*)", "``string``", "The RegEx (Regular Expression) path pattern to ignore", ""
    "Prim Types (*inputs:primTypes*)", "``token[]``", "List of prim types to include", "[]"
    "Prim Types Exclusion (*inputs:primTypesExclusion*)", "``token[]``", "List of prim types to ignore", "[]"
    "Semantics (*inputs:semantics*)", "``token[]``", "Semantic type-value pairs of semantics to include", "[]"
    "Semantics Exclusion (*inputs:semanticsExclusion*)", "``token[]``", "Semantic type-value pairs of semantics to ignore", "[]"


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

    "Unique ID", "omni.replicator.core.OgnGetPrims"
    "Version", "1"
    "Extension", "omni.replicator.core"
    "Has State?", "True"
    "Implementation Language", "Python"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Get Prims"
    "Categories", "Replicator:Core"
    "__categoryDescriptions", "Replicator:Core,Core Replicator nodes"
    "Generated Class Name", "OgnGetPrimsDatabase"
    "Python Module", "omni.replicator.core"

