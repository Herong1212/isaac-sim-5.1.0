.. _omni_replicator_core_OgnLookAt_2:

.. _omni_replicator_core_OgnLookAt:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Make prim look at target
    :keywords: lang-en omnigraph node Replicator:Core core ogn-look-at


Make prim look at target
========================

.. <description>

Set prim rotation to look at the target coordinates

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
    "Prims (*inputs:prims*)", "``target``", "The prims whose orientation is to be changed", "None"
    "Target (*inputs:target*)", "``float[3]``", "The location of where the prim should look at", "[0.0, 0.0, 0.0]"
    "Target Prim (*inputs:targetPrim*)", "``target``", "The target prim(s) that the prim should look at", "None"
    "Up Axis (*inputs:upAxis*)", "``float[3]``", "The up axis to set to the input prims.", "[0.0, 0.0, 0.0]"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Exec Out (*outputs:execOut*)", "``execution``", "exec", "None"
    "Values (*outputs:values*)", "``double[3][]``", "Rotation to make prims look at the specified target(s)", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.replicator.core.OgnLookAt"
    "Version", "2"
    "Extension", "omni.replicator.core"
    "Has State?", "True"
    "Implementation Language", "Python"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Make prim look at target"
    "Categories", "Replicator:Core"
    "__categoryDescriptions", "Replicator:Core,Core Replicator nodes"
    "Generated Class Name", "OgnLookAtDatabase"
    "Python Module", "omni.replicator.core"

