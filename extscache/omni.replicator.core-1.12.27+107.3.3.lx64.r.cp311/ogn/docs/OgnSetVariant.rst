.. _omni_replicator_core_OgnSetVariant_1:

.. _omni_replicator_core_OgnSetVariant:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Set Variant
    :keywords: lang-en omnigraph node Replicator:Core compute-on-request core ogn-set-variant


Set Variant
===========

.. <description>

Set variant on prims

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
    "Prims (*inputs:prims*)", "``target``", "Targets to count.", "None"
    "Values (*inputs:values*)", "``token[]``", "Variant value.", "[]"
    "Variant (*inputs:variant*)", "``token``", "Variant set name.", ""


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

    "Unique ID", "omni.replicator.core.OgnSetVariant"
    "Version", "1"
    "Extension", "omni.replicator.core"
    "Has State?", "True"
    "Implementation Language", "Python"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Set Variant"
    "Categories", "Replicator:Core"
    "__categoryDescriptions", "Replicator:Core,Core Replicator nodes"
    "Generated Class Name", "OgnSetVariantDatabase"
    "Python Module", "omni.replicator.core"

