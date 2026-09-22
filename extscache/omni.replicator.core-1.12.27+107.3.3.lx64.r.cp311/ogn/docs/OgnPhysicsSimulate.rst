.. _omni_replicator_core_OgnPhysicsSimulate_1:

.. _omni_replicator_core_OgnPhysicsSimulate:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Simulate Physics
    :keywords: lang-en omnigraph node Replicator:Core compute-on-request core ogn-physics-simulate


Simulate Physics
================

.. <description>

Simulate physics

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
    "Physics Scene (*inputs:physicsScene*)", "``target``", "Physics Scene to simulate.", "None"
    "Simulation Time (*inputs:simulationTime*)", "``float``", "Desired simulation time.", "1.0"
    "Step Dt (*inputs:stepDt*)", "``float``", "The per-step dt to simulate. A smaller value will require more steps but provide higher simulation accuracy.", "0.1"


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

    "Unique ID", "omni.replicator.core.OgnPhysicsSimulate"
    "Version", "1"
    "Extension", "omni.replicator.core"
    "Has State?", "True"
    "Implementation Language", "Python"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Simulate Physics"
    "Categories", "Replicator:Core"
    "__categoryDescriptions", "Replicator:Core,Core Replicator nodes"
    "Generated Class Name", "OgnPhysicsSimulateDatabase"
    "Python Module", "omni.replicator.core"

