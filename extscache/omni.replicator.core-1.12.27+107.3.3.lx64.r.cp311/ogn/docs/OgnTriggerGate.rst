.. _omni_replicator_core_OgnTriggerGate_1:

.. _omni_replicator_core_OgnTriggerGate:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Trigger Gate
    :keywords: lang-en omnigraph node Replicator:Annotators compute-on-request core ogn-trigger-gate


Trigger Gate
============

.. <description>

Gate that passes execution only once per sync value and only when both exec and triggerExec signals are received.

.. </description>


Installation
------------

To use this node enable :ref:`omni.replicator.core<ext_omni_replicator_core>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Exec (*inputs:exec*)", "``execution``", "Execution in", "None"
    "Sync (*inputs:syncValue*)", "``uint64``", "Value of the synchronization reference.", "0"
    "Trigger Exec (*inputs:triggerExec*)", "``execution``", "Trigger Execution inputs", "None"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Exec (*outputs:exec*)", "``execution``", "Execution out", "None"
    "Sync (*outputs:syncValue*)", "``uint64``", "Value of the synchronization reference.", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.replicator.core.OgnTriggerGate"
    "Version", "1"
    "Extension", "omni.replicator.core"
    "Has State?", "True"
    "Implementation Language", "Python"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Trigger Gate"
    "Categories", "Replicator:Annotators"
    "__categoryDescriptions", "Replicator:Annotators,Replicator annotator nodes."
    "Generated Class Name", "OgnTriggerGateDatabase"
    "Python Module", "omni.replicator.core"

