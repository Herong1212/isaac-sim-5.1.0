.. _omni_replicator_core_OgnOnCondition_1:

.. _omni_replicator_core_OgnOnCondition:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: On Condition
    :keywords: lang-en omnigraph node Replicator:Core compute-on-request core ogn-on-condition


On Condition
============

.. <description>

Triggers when the evaluated condition is True

.. </description>


Installation
------------

To use this node enable :ref:`omni.replicator.core<ext_omni_replicator_core>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Condition (*inputs:condition*)", "``bool``", "Trigger condition. If evaluates to `True`, trigger is enabled. If `False`, trigger is disabled.", "False"
    "Max Execs (*inputs:maxExecs*)", "``int``", "Maximum number of executions", "-1"
    "Rt Subframes (*inputs:rt_subframes*)", "``uint64``", "Determines how many subframes to render in RealTime render mode on each trigger to reduce artifacts caused by sudden scene changes.", "16"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Exec (*outputs:exec*)", "``execution``", "Output Execution", "None"
    "Exec Counts (*outputs:execCounts*)", "``int``", "The number of times the trigger has executed.", "None"
    "Reference Time Denominator (*outputs:referenceTimeDenominator*)", "``uint64``", "Reference time represented as a rational number : denominator", "None"
    "Reference Time Numerator (*outputs:referenceTimeNumerator*)", "``int64``", "Reference time represented as a rational number : numerator", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.replicator.core.OgnOnCondition"
    "Version", "1"
    "Extension", "omni.replicator.core"
    "Has State?", "True"
    "Implementation Language", "Python"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "On Condition"
    "Categories", "Replicator:Core"
    "__categoryDescriptions", "Replicator:Core,Core Replicator nodes"
    "Generated Class Name", "OgnOnConditionDatabase"
    "Python Module", "omni.replicator.core"

