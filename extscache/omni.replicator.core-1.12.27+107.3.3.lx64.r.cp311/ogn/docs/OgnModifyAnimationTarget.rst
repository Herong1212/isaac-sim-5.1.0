.. _omni_replicator_core_OgnModifyAnimationTarget_2:

.. _omni_replicator_core_OgnModifyAnimationTarget:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Modify Animation Target
    :keywords: lang-en omnigraph node Replicator:Core compute-on-request core ogn-modify-animation-target


Modify Animation Target
=======================

.. <description>

This modifies the target animation on a skeleton prim.

.. </description>


Installation
------------

To use this node enable :ref:`omni.replicator.core<ext_omni_replicator_core>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Exec (*inputs:exec*)", "``execution``", "exec", "None"
    "Prims (*inputs:prims*)", "``target``", "Skeleton prims to set attribute.", "None"
    "Reset Timeline (*inputs:reset_timeline*)", "``bool``", "Whether to reset the timeline after setting the new animation.", "False"
    "Values (*inputs:values*)", "``target``", "Animation path value to be assigned to the skeleton.", "None"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Exec (*outputs:exec*)", "``execution``", "exec", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.replicator.core.OgnModifyAnimationTarget"
    "Version", "2"
    "Extension", "omni.replicator.core"
    "Has State?", "False"
    "Implementation Language", "Python"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Modify Animation Target"
    "Categories", "Replicator:Core"
    "__categoryDescriptions", "Replicator:Core,Core Replicator nodes"
    "Generated Class Name", "OgnModifyAnimationTargetDatabase"
    "Python Module", "omni.replicator.core"

