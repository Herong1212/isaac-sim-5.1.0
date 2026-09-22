.. _omni_replicator_core_OgnSetPivot_1:

.. _omni_replicator_core_OgnSetPivot:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Set Pivot
    :keywords: lang-en omnigraph node Replicator:Core core ogn-set-pivot


Set Pivot
=========

.. <description>

This node sets pivot to prims.

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
    "Pivot (*inputs:pivot*)", "``float[]``", "Relative pivot position of the prim.", "[]"
    "Prims (*inputs:prims*)", "``target``", "Prim(s) to set pivot", "None"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Exec Out (*outputs:execOut*)", "``execution``", "exec", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.replicator.core.OgnSetPivot"
    "Version", "1"
    "Extension", "omni.replicator.core"
    "Has State?", "False"
    "Implementation Language", "Python"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Set Pivot"
    "Categories", "Replicator:Core"
    "__categoryDescriptions", "Replicator:Core,Core Replicator nodes"
    "Generated Class Name", "OgnSetPivotDatabase"
    "Python Module", "omni.replicator.core"

