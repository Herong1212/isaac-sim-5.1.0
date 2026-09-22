.. _omni_replicator_core_OgnBindMaterial_2:

.. _omni_replicator_core_OgnBindMaterial:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Bind Material
    :keywords: lang-en omnigraph node Replicator:Core core ogn-bind-material


Bind Material
=============

.. <description>

This node binds a material on specified prims.

.. </description>


Installation
------------

To use this node enable :ref:`omni.replicator.core<ext_omni_replicator_core>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Exec (*inputs:exec*)", "``execution``", "exec", "None"
    "Material Paths (*inputs:materialPaths*)", "``token[]``", "Material paths to be bound to the prims.", "[]"
    "Material Prims (*inputs:materialPrims*)", "``target``", "Materials to be bound to the prims.", "None"
    "Prims (*inputs:prims*)", "``target``", "Prim(s) to bind material", "None"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Exec (*outputs:exec*)", "``execution``", "exec", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.replicator.core.OgnBindMaterial"
    "Version", "2"
    "Extension", "omni.replicator.core"
    "Has State?", "False"
    "Implementation Language", "Python"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Bind Material"
    "Categories", "Replicator:Core"
    "__categoryDescriptions", "Replicator:Core,Core Replicator nodes"
    "Generated Class Name", "OgnBindMaterialDatabase"
    "Python Module", "omni.replicator.core"

