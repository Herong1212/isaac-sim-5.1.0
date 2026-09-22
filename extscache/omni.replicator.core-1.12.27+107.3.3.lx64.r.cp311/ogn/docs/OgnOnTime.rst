.. _omni_replicator_core_OgnOnTime_3:

.. _omni_replicator_core_OgnOnTime:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: On Time
    :keywords: lang-en omnigraph node Replicator:Core compute-on-request core ogn-on-time


On Time
=======

.. <description>

Triggers at the specified time interval. Note that the graph will run asynchronously to the new frame event

.. </description>


Installation
------------

To use this node enable :ref:`omni.replicator.core<ext_omni_replicator_core>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Interval (*inputs:interval*)", "``float``", "Trigger interval, in seconds.", "1"
    "Max Execs (*inputs:maxExecs*)", "``uint``", "Number of sequences triggered before stopping. If 0, continue indefinitely.", "0"
    "Reset Physics (*inputs:resetPhysics*)", "``bool``", "If True, reset physics simulation on trigger.", "True"
    "Rt Subframes (*inputs:rtSubframes*)", "``uint64``", "Determines how many subframes to render in RealTime render mode on each trigger to reduce artifacts caused by sudden scene changes.", "16"
    "Run (*inputs:run*)", "``bool``", "Run", "False"
    "Trigger On Last Frame (*inputs:triggerOnLastFrame*)", "``bool``", "If True, trigger on the frame before the interval time is reached.", "False"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Exec Counts (*outputs:execCounts*)", "``int``", "The number of times the trigger has executed.", "None"
    "Exec Out (*outputs:execOut*)", "``execution``", "Output Execution", "None"
    "Reference Time Denominator (*outputs:referenceTimeDenominator*)", "``uint64``", "Reference time represented as a rational number : denominator", "None"
    "Reference Time Numerator (*outputs:referenceTimeNumerator*)", "``int64``", "Reference time represented as a rational number : numerator", "None"
    "Time (*outputs:time*)", "``int``", "The current physx simulation time.", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.replicator.core.OgnOnTime"
    "Version", "3"
    "Extension", "omni.replicator.core"
    "Has State?", "True"
    "Implementation Language", "Python"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "On Time"
    "Categories", "Replicator:Core"
    "__categoryDescriptions", "Replicator:Core,Core Replicator nodes"
    "Generated Class Name", "OgnOnTimeDatabase"
    "Python Module", "omni.replicator.core"

