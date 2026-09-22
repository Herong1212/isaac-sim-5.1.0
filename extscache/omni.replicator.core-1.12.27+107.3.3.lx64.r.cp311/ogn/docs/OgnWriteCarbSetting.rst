.. _omni_replicator_core_OgnWriteCarbSetting_1:

.. _omni_replicator_core_OgnWriteCarbSetting:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Write Carb Settings
    :keywords: lang-en omnigraph node Replicator:Core compute-on-request core ogn-write-carb-setting


Write Carb Settings
===================

.. <description>

Change carb renderer settings

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
    "Setting (*inputs:setting*)", "``string``", "Name of carb setting that is to be written", ""
    "Values (*inputs:values*)", "``any``", "Values to be assigned to the setting", "None"


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

    "Unique ID", "omni.replicator.core.OgnWriteCarbSetting"
    "Version", "1"
    "Extension", "omni.replicator.core"
    "Has State?", "True"
    "Implementation Language", "Python"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Write Carb Settings"
    "Categories", "Replicator:Core"
    "__categoryDescriptions", "Replicator:Core,Core Replicator nodes"
    "Generated Class Name", "OgnWriteCarbSettingDatabase"
    "Python Module", "omni.replicator.core"

