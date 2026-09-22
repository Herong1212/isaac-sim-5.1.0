.. _omni_replicator_core_ReadFabricTime_1:

.. _omni_replicator_core_ReadFabricTime:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Read Fabric Time
    :keywords: lang-en omnigraph node time threadsafe core read-fabric-time


Read Fabric Time
================

.. <description>

Holds the values related to the current fabric time

.. </description>


Installation
------------

To use this node enable :ref:`omni.replicator.core<ext_omni_replicator_core>` in the Extension Manager.


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Fabric Frame Time Denominator (*outputs:fabricFrameTimeDenominator*)", "``uint64``", "Fabric time represented as a rational number : denominator", "None"
    "Fabric Frame Time Numerator (*outputs:fabricFrameTimeNumerator*)", "``int64``", "Fabric time represented as a rational number : numerator", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.replicator.core.ReadFabricTime"
    "Version", "1"
    "Extension", "omni.replicator.core"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Read Fabric Time"
    "Categories", "time"
    "Generated Class Name", "OgnReadFabricTimeDatabase"
    "Python Module", "omni.replicator.core"

