.. _omni_replicator_core_OgnWritePhysics_1:

.. _omni_replicator_core_OgnWritePhysics:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Write Physics Attribute
    :keywords: lang-en omnigraph node Replicator:Core compute-on-request core ogn-write-physics


Write Physics Attribute
=======================

.. <description>

This node writes to a specified physics attribute on specified prims.

.. </description>


Installation
------------

To use this node enable :ref:`omni.replicator.core<ext_omni_replicator_core>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Attribute (*inputs:attribute*)", "``string``", "Name of attribute that is to be written", ""
    "Exec In (*inputs:execIn*)", "``execution``", "exec", "None"
    "Overwrite Rigid Body (*inputs:overwriteRigidBody*)", "``bool``", "Whether to write children prim's rigid body api or not.", "False"
    "Physics Scene (*inputs:physicsScene*)", "``target``", "Path to PhysicsScene prim.", "None"
    "Prims (*inputs:prims*)", "``target``", "Prim(s) to set attribute", "None"
    "Values (*inputs:values*)", "``any``", "Values to be assigned to the physics attribute", "None"


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

    "Unique ID", "omni.replicator.core.OgnWritePhysics"
    "Version", "1"
    "Extension", "omni.replicator.core"
    "Has State?", "False"
    "Implementation Language", "Python"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Write Physics Attribute"
    "Categories", "Replicator:Core"
    "__categoryDescriptions", "Replicator:Core,Core Replicator nodes"
    "Generated Class Name", "OgnWritePhysicsDatabase"
    "Python Module", "omni.replicator.core"

