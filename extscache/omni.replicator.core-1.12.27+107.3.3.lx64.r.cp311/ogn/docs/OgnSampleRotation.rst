.. _omni_replicator_core_OgnSampleRotation_1:

.. _omni_replicator_core_OgnSampleRotation:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Sample Rotation
    :keywords: lang-en omnigraph node Replicator:Core compute-on-request core ogn-sample-rotation


Sample Rotation
===============

.. <description>

This node assigns uniformly sampled rotations to the input prims.

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
    "Max Angle (*inputs:maxAngle*)", "``float[3]``", "maximum value for Euler angles in XYZ form (degrees)", "[180.0, 180.0, 180.0]"
    "Min Angle (*inputs:minAngle*)", "``float[3]``", "minimum value for Euler angles in XYZ form (degrees)", "[-180.0, -180.0, -180.0]"
    "Prims (*inputs:prims*)", "``target``", "prim(s) to set rotation", "None"
    "Seed (*inputs:seed*)", "``int``", "Random Number Generator seed. A value of less than 0 will indicate using the global seed.", "-1"


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

    "Unique ID", "omni.replicator.core.OgnSampleRotation"
    "Version", "1"
    "Extension", "omni.replicator.core"
    "Has State?", "True"
    "Implementation Language", "Python"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Sample Rotation"
    "Categories", "Replicator:Core"
    "__categoryDescriptions", "Replicator:Core,Core Replicator nodes"
    "Generated Class Name", "OgnSampleRotationDatabase"
    "Python Module", "omni.replicator.core"

