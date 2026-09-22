.. _omni_replicator_core_OgnPerAxisPose_1:

.. _omni_replicator_core_OgnPerAxisPose:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Per axis pose
    :keywords: lang-en omnigraph node Replicator:Core core ogn-per-axis-pose


Per axis pose
=============

.. <description>

Generate 3-Dimension array values from per axis input values

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
    "Full Values (*inputs:fullValues*)", "``float[3][]``", "Value on all three axes. Cannot co-exist with xValue, yValue or zValue.", "[]"
    "Mode (*inputs:mode*)", "``token``", "String value indicating which parameter to modify.", ""
    "Num Samples (*inputs:numSamples*)", "``int``", "Number of samples", "0"
    "Prims (*inputs:prims*)", "``target``", "The prims that their pose needs to be changed.", "None"
    "X Value (*inputs:xValue*)", "``float[]``", "Value of the x axis.", "[]"
    "Y Value (*inputs:yValue*)", "``float[]``", "Value of the y axis.", "[]"
    "Z Value (*inputs:zValue*)", "``float[]``", "Value of the z axis.", "[]"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Exec (*outputs:exec*)", "``execution``", "exec", "None"
    "Samples (*outputs:samples*)", "``double[3][]``", "3 Dimensional values on each axis.", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.replicator.core.OgnPerAxisPose"
    "Version", "1"
    "Extension", "omni.replicator.core"
    "Has State?", "False"
    "Implementation Language", "Python"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Per axis pose"
    "Categories", "Replicator:Core"
    "__categoryDescriptions", "Replicator:Core,Core Replicator nodes"
    "Generated Class Name", "OgnPerAxisPoseDatabase"
    "Python Module", "omni.replicator.core"

