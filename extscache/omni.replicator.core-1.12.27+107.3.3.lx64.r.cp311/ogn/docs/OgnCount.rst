.. _omni_replicator_core_OgnCount_1:

.. _omni_replicator_core_OgnCount:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Count
    :keywords: lang-en omnigraph node Replicator:Core core ogn-count


Count
=====

.. <description>

Count prims

.. </description>


Installation
------------

To use this node enable :ref:`omni.replicator.core<ext_omni_replicator_core>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Mode (*inputs:mode*)", "``token``", "Select counting mode", "prims"
    "", "Metadata", "*allowedTokens* = prims,meshes,instances", ""
    "Prims (*inputs:prims*)", "``target``", "Targets to count", "None"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Count (*outputs:count*)", "``uint``", "Count", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.replicator.core.OgnCount"
    "Version", "1"
    "Extension", "omni.replicator.core"
    "Has State?", "True"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Count"
    "__tokens", "[""prims"", ""meshes"", ""instances""]"
    "Categories", "Replicator:Core"
    "__categoryDescriptions", "Replicator:Core,Core Replicator nodes"
    "Generated Class Name", "OgnCountDatabase"
    "Python Module", "omni.replicator.core"

