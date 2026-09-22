.. _omni_flowusd_FlowNanoVdbReadback_1:

.. _omni_flowusd_FlowNanoVdbReadback:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Flow NanoVDB Readback
    :keywords: lang-en omnigraph node FlowUsd flowusd flow-nano-vdb-readback


Flow NanoVDB Readback
=====================

.. <description>

Access to NanoVDBs produced by Flow, with some latency due to async readback.

.. </description>


Installation
------------

To use this node enable :ref:`omni.flowusd<ext_omni_flowusd>` in the Extension Manager.


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Burn (*outputs:burn*)", "``uint[]``", "NanoVDB for Flow burn channel", "[]"
    "Divergence (*outputs:divergence*)", "``uint[]``", "NanoVDB for Flow divergence channel", "[]"
    "Exec Out (*outputs:execOut*)", "``execution``", "Executes when values are updated", "None"
    "Fuel (*outputs:fuel*)", "``uint[]``", "NanoVDB for Flow fuel channel", "[]"
    "Smoke (*outputs:smoke*)", "``uint[]``", "NanoVDB for Flow smoke channel", "[]"
    "Temperature (*outputs:temperature*)", "``uint[]``", "NanoVDB for Flow temperature channel", "[]"
    "Velocity (*outputs:velocity*)", "``uint[]``", "NanoVDB for Flow velocity channel", "[]"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.flowusd.FlowNanoVdbReadback"
    "Version", "1"
    "Extension", "omni.flowusd"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "tests"
    "uiName", "Flow NanoVDB Readback"
    "Categories", "FlowUsd"
    "Generated Class Name", "OgnFlowNanoVdbReadbackDatabase"
    "Python Module", "omni.flowusd"

