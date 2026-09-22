.. _omni_syntheticdata_SdTestStageSynchronization_1:

.. _omni_syntheticdata_SdTestStageSynchronization:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Sd Test Stage Synchronization
    :keywords: lang-en omnigraph node graph:simulation,graph:postRender,graph:action,internal:test syntheticdata sd-test-stage-synchronization


Sd Test Stage Synchronization
=============================

.. <description>

Synthetic Data node to test the pipeline stage synchronization

.. </description>


Installation
------------

To use this node enable :ref:`omni.syntheticdata<ext_omni_syntheticdata>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Exec (*inputs:exec*)", "``execution``", "OnDemand connection : trigger", "None"
    "gpuFoundations (*inputs:gpu*)", "``uint64``", "PostRender connection : pointer to shared context containing gpu foundations", "0"
    "Random Max Processing Time Us (*inputs:randomMaxProcessingTimeUs*)", "``uint``", "Maximum number of micro-seconds to randomly (uniformely) wait for in order to simulate varying workload", "0"
    "Random Seed (*inputs:randomSeed*)", "``uint``", "Random seed for the randomization", "0"
    "Render Results (*inputs:renderResults*)", "``uint64``", "OnDemand connection : pointer to render product results", "0"
    "renderProduct (*inputs:rp*)", "``uint64``", "PostRender connection : pointer to render product for this view", "0"
    "Swh Frame Number (*inputs:swhFrameNumber*)", "``uint64``", "Fabric frame number", "0"
    "Tag (*inputs:tag*)", "``token``", "A tag to identify the node", ""
    "Trace Error (*inputs:traceError*)", "``bool``", "If true print an error message when the frame numbers are out-of-sync", "False"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Exec (*outputs:exec*)", "``execution``", "OnDemand connection : trigger", "None"
    "Fabric SWH Frame Number (*outputs:fabricSWHFrameNumber*)", "``uint64``", "Fabric frame number from the fabric", "None"
    "Swh Frame Number (*outputs:swhFrameNumber*)", "``uint64``", "Fabric frame number", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.syntheticdata.SdTestStageSynchronization"
    "Version", "1"
    "Extension", "omni.syntheticdata"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "tests"
    "Categories", "graph:simulation,graph:postRender,graph:action,internal:test"
    "Generated Class Name", "OgnSdTestStageSynchronizationDatabase"
    "Python Module", "omni.syntheticdata"

