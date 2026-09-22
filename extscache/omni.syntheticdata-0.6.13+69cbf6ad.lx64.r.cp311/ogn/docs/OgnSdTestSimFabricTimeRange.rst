.. _omni_syntheticdata_SdTestSimFabricTimeRange_1:

.. _omni_syntheticdata_SdTestSimFabricTimeRange:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Sd Test Sim Fabric Time Range
    :keywords: lang-en omnigraph node graph:simulation,internal,event compute-on-request syntheticdata sd-test-sim-fabric-time-range


Sd Test Sim Fabric Time Range
=============================

.. <description>

Testing node : on request write/update a Fabric time range of a given number of frames starting at the current simulation time.

.. </description>


Installation
------------

To use this node enable :ref:`omni.syntheticdata<ext_omni_syntheticdata>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Number Of Frames (*inputs:numberOfFrames*)", "``uint64``", "Number of frames to writes.", "0"
    "Time Range Begin Denominator Token (*inputs:timeRangeBeginDenominatorToken*)", "``token``", "Attribute name of the range begin time denominator", "timeRangeStartDenominator"
    "Time Range Begin Numerator Token (*inputs:timeRangeBeginNumeratorToken*)", "``token``", "Attribute name of the range begin time numerator", "timeRangeStartNumerator"
    "Time Range End Denominator Token (*inputs:timeRangeEndDenominatorToken*)", "``token``", "Attribute name of the range end time denominator", "timeRangeEndDenominator"
    "Time Range End Numerator Token (*inputs:timeRangeEndNumeratorToken*)", "``token``", "Attribute name of the range end time numerator", "timeRangeEndNumerator"
    "Time Range Name (*inputs:timeRangeName*)", "``token``", "Time range name used to write to the Fabric.", "TestSimFabricTimeRangeSD"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Exec (*outputs:exec*)", "``execution``", "Trigger", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.syntheticdata.SdTestSimFabricTimeRange"
    "Version", "1"
    "Extension", "omni.syntheticdata"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "__tokens", "[""fc_exportToRingbuffer""]"
    "Categories", "graph:simulation,internal,event"
    "Generated Class Name", "OgnSdTestSimFabricTimeRangeDatabase"
    "Python Module", "omni.syntheticdata"

