.. _omni_replicator_core_OgnRefTimeGate_1:

.. _omni_replicator_core_OgnRefTimeGate:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Frame Gate
    :keywords: lang-en omnigraph node Replicator:Annotators core ogn-ref-time-gate


Frame Gate
==========

.. <description>

Gate that passes execution only if the reference time is within the list of valid times.

.. </description>


Installation
------------

To use this node enable :ref:`omni.replicator.core<ext_omni_replicator_core>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Enabled (*inputs:enabled*)", "``bool``", "If false, execution passes through the gate unchecked.", "False"
    "Exec (*inputs:exec*)", "``execution``", "Execution in", "None"
    "Reference Time Denominator (*inputs:referenceTimeDenominator*)", "``uint64``", "Reference time represented as a rational number : denominator", "0"
    "Reference Time Numerator (*inputs:referenceTimeNumerator*)", "``int64``", "Reference time represented as a rational number : numerator", "0"
    "Sim Times To Write (*inputs:simTimesToWrite*)", "``int[2][]``", "Sim times at which to allow further graph execution. Represented as numerator, denominator tuples. Must be in reduced form.", "[]"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Exec (*outputs:exec*)", "``execution``", "Execution out", "None"
    "Reference Time Denominator (*outputs:referenceTimeDenominator*)", "``uint64``", "Reference time represented as a rational number : denominator", "None"
    "Reference Time Numerator (*outputs:referenceTimeNumerator*)", "``int64``", "Reference time represented as a rational number : numerator", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.replicator.core.OgnRefTimeGate"
    "Version", "1"
    "Extension", "omni.replicator.core"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Frame Gate"
    "Categories", "Replicator:Annotators"
    "__categoryDescriptions", "Replicator:Annotators,Replicator annotator nodes."
    "Generated Class Name", "OgnRefTimeGateDatabase"
    "Python Module", "omni.replicator.core"

