.. _omni_syntheticdata_SdTestRationalTimeSyncGate_1:

.. _omni_syntheticdata_SdTestRationalTimeSyncGate:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Sd Test Rational Time Sync Gate
    :keywords: lang-en omnigraph node graph:action,internal:test syntheticdata sd-test-rational-time-sync-gate


Sd Test Rational Time Sync Gate
===============================

.. <description>

This node triggers when all its input executions have triggered successively at the same rational time.

.. </description>


Installation
------------

To use this node enable :ref:`omni.syntheticdata<ext_omni_syntheticdata>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Execute In (*inputs:execIn*)", "``execution``", "The input execution", "None"
    "Sync Denominator (*inputs:rationalTimeDenominator*)", "``uint64``", "Denominator of the synchronization time.", "0"
    "Sync Numerator (*inputs:rationalTimeNumerator*)", "``int64``", "Numerator of the synchronization time.", "0"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Execute Out (*outputs:execOut*)", "``execution``", "The output execution", "None"
    "Sync Denominator (*outputs:rationalTimeDenominator*)", "``uint64``", "Denominator of the synchronization time.", "None"
    "Sync Numerator (*outputs:rationalTimeNumerator*)", "``int64``", "Numerator of the synchronization time.", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.syntheticdata.SdTestRationalTimeSyncGate"
    "Version", "1"
    "Extension", "omni.syntheticdata"
    "Has State?", "False"
    "Implementation Language", "Python"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "tests"
    "Categories", "graph:action,internal:test"
    "Generated Class Name", "OgnSdTestRationalTimeSyncGateDatabase"
    "Python Module", "omni.syntheticdata"

