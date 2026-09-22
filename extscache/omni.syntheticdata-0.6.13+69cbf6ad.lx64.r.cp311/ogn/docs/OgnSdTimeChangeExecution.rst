.. _omni_syntheticdata_SdTimeChangeExecution_1:

.. _omni_syntheticdata_SdTimeChangeExecution:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Sd Time Change Execution
    :keywords: lang-en omnigraph node graph:postRender,graph:action syntheticdata sd-time-change-execution


Sd Time Change Execution
========================

.. <description>

Set its execution output if the input rational time is more recent that the last registered time.

.. </description>


Installation
------------

To use this node enable :ref:`omni.syntheticdata<ext_omni_syntheticdata>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Error On Future Change (*inputs:errorOnFutureChange*)", "``bool``", "Print error if the last update is in the future.", "False"
    "Exec (*inputs:exec*)", "``execution``", "Trigger", "None"
    "Last Update Time Denominator (*inputs:lastUpdateTimeDenominator*)", "``uint64``", "Time denominator of the last time change", "0"
    "Last Update Time Numerator (*inputs:lastUpdateTimeNumerator*)", "``int64``", "Time numerator of the last time change", "0"
    "Render Results (*inputs:renderResults*)", "``uint64``", "Render results", "0"


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

    "Unique ID", "omni.syntheticdata.SdTimeChangeExecution"
    "Version", "1"
    "Extension", "omni.syntheticdata"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "Categories", "graph:postRender,graph:action"
    "Generated Class Name", "OgnSdTimeChangeExecutionDatabase"
    "Python Module", "omni.syntheticdata"

