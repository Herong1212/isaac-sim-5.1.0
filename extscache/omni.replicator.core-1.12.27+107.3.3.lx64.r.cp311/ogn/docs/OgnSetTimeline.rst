.. _omni_replicator_core_OgnSetTimeline_1:

.. _omni_replicator_core_OgnSetTimeline:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Set Timeline
    :keywords: lang-en omnigraph node Replicator:Core compute-on-request core ogn-set-timeline


Set Timeline
============

.. <description>

Set visibility on prims

.. </description>


Installation
------------

To use this node enable :ref:`omni.replicator.core<ext_omni_replicator_core>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Exec In (*inputs:execIn*)", "``execution``", "exec", "None"
    "Modify Type (*inputs:modifyType*)", "``token``", "The method to modify the timeline.", ""
    "", "Metadata", "*allowedTokens* = Time,Start Time,End Time,Frame,Start Frame,End Frame", ""
    "Value (*inputs:value*)", "``float``", "Value used to modify the timeline.", "0.0"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Exec Out (*outputs:execOut*)", "``execution``", "exec", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.replicator.core.OgnSetTimeline"
    "Version", "1"
    "Extension", "omni.replicator.core"
    "Has State?", "True"
    "Implementation Language", "Python"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Set Timeline"
    "Categories", "Replicator:Core"
    "__categoryDescriptions", "Replicator:Core,Core Replicator nodes"
    "Generated Class Name", "OgnSetTimelineDatabase"
    "Python Module", "omni.replicator.core"

