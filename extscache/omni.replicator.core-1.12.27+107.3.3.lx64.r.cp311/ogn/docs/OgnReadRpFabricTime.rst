.. _omni_replicator_core_ReadRpFabricTime_1:

.. _omni_replicator_core_ReadRpFabricTime:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Read Render Product Fabric Time
    :keywords: lang-en omnigraph node time threadsafe core read-rp-fabric-time


Read Render Product Fabric Time
===============================

.. <description>

Holds the values related to the current fabric time from a render product

.. </description>


Installation
------------

To use this node enable :ref:`omni.replicator.core<ext_omni_replicator_core>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Exec (*inputs:exec*)", "``execution``", "Trigger", "None"
    "Rp (*inputs:rp*)", "``uint64``", "Render results", "0"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Exec (*outputs:exec*)", "``execution``", "Trigger", "None"
    "Fabric Frame Time Denominator (*outputs:fabricFrameTimeDenominator*)", "``uint64``", "Fabric time represented as a rational number : denominator", "None"
    "Fabric Frame Time Numerator (*outputs:fabricFrameTimeNumerator*)", "``int64``", "Fabric time represented as a rational number : numerator", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.replicator.core.ReadRpFabricTime"
    "Version", "1"
    "Extension", "omni.replicator.core"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Read Render Product Fabric Time"
    "Categories", "time"
    "Generated Class Name", "OgnReadRpFabricTimeDatabase"
    "Python Module", "omni.replicator.core"

