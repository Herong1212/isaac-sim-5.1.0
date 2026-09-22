.. _omni_flowusd_FlowSimTime_1:

.. _omni_flowusd_FlowSimTime:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Flow SimTime
    :keywords: lang-en omnigraph node FlowUsd flowusd flow-sim-time


Flow SimTime
============

.. <description>

Node exposing simulation time to OG

.. </description>


Installation
------------

To use this node enable :ref:`omni.flowusd<ext_omni_flowusd>` in the Extension Manager.


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Exec Out (*outputs:execOut*)", "``execution``", "Executes when values are updated", "None"
    "Last Absolute (*outputs:lastAbsoluteSimTime*)", "``double``", "Time when work submitted to Flow has flushed through", "0.0"
    "Last Fault Absolute (*outputs:lastFaultAbsoluteSimTime*)", "``double``", "Last time Flow hit max blocks", "0.0"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.flowusd.FlowSimTime"
    "Version", "1"
    "Extension", "omni.flowusd"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "tests"
    "uiName", "Flow SimTime"
    "Categories", "FlowUsd"
    "Generated Class Name", "OgnFlowSimTimeDatabase"
    "Python Module", "omni.flowusd"

