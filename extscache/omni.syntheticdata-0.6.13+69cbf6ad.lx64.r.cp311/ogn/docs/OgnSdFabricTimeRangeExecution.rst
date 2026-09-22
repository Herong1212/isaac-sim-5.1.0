.. _omni_syntheticdata_SdFabricTimeRangeExecution_1:

.. _omni_syntheticdata_SdFabricTimeRangeExecution:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Sd Fabric Time Range Execution
    :keywords: lang-en omnigraph node graph:postRender,graph:action syntheticdata sd-fabric-time-range-execution


Sd Fabric Time Range Execution
==============================

.. <description>

Read a rational time range from Fabric or RenderVars and signal its execution if the current time fall within this range. The range is [begin,end[, that is the end time does not belong to the range.

.. </description>


Installation
------------

To use this node enable :ref:`omni.syntheticdata<ext_omni_syntheticdata>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Exec (*inputs:exec*)", "``execution``", "Trigger", "None"
    "Gpu (*inputs:gpu*)", "``uint64``", "Pointer to shared context containing gpu foundations.", "0"
    "Render Results (*inputs:renderResults*)", "``uint64``", "Render results", "0"
    "Time Range Begin Denominator Token (*inputs:timeRangeBeginDenominatorToken*)", "``token``", "Attribute name of the range begin time denominator", "timeRangeStartDenominator"
    "Time Range Begin Numerator Token (*inputs:timeRangeBeginNumeratorToken*)", "``token``", "Attribute name of the range begin time numerator", "timeRangeStartNumerator"
    "Time Range End Denominator Token (*inputs:timeRangeEndDenominatorToken*)", "``token``", "Attribute name of the range end time denominator", "timeRangeEndDenominator"
    "Time Range End Numerator Token (*inputs:timeRangeEndNumeratorToken*)", "``token``", "Attribute name of the range end time numerator", "timeRangeEndNumerator"
    "Time Range Name (*inputs:timeRangeName*)", "``token``", "Time range name used to read from the Fabric or RenderVars.", ""


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Exec (*outputs:exec*)", "``execution``", "Trigger", "None"
    "Time Range Begin Denominator (*outputs:timeRangeBeginDenominator*)", "``uint64``", "Time denominator of the last time range change (begin)", "None"
    "Time Range Begin Numerator (*outputs:timeRangeBeginNumerator*)", "``int64``", "Time numerator of the last time range change (begin)", "None"
    "Time Range End Denominator (*outputs:timeRangeEndDenominator*)", "``uint64``", "Time denominator of the last time range change (end)", "None"
    "Time Range End Numerator (*outputs:timeRangeEndNumerator*)", "``int64``", "Time numerator of the last time range change (end)", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.syntheticdata.SdFabricTimeRangeExecution"
    "Version", "1"
    "Extension", "omni.syntheticdata"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "Categories", "graph:postRender,graph:action"
    "Generated Class Name", "OgnSdFabricTimeRangeExecutionDatabase"
    "Python Module", "omni.syntheticdata"

