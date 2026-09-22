.. _omni_replicator_core_OgnCreateProjectionMaterial_1:

.. _omni_replicator_core_OgnCreateProjectionMaterial:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Create Projection Material
    :keywords: lang-en omnigraph node Replicator:Core compute-on-request core ogn-create-projection-material


Create Projection Material
==========================

.. <description>

This node prepares and/or projects a material on specified prims.

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
    "Material Prim (*inputs:materialPrim*)", "``target``", "Material to apply to each offset mesh.", "None"
    "Offset Scale (*inputs:offsetScale*)", "``float``", "Scale factor when extruding target_prim points.", "0.01"
    "Prims (*inputs:prims*)", "``target``", "Prim to project on to.", "None"
    "Proxy Prim (*inputs:proxyPrim*)", "``target``", "Prim to project from.", "None"
    "Semantics (*inputs:semantics*)", "``token``", "Semantics to apply to each projection.", ""


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Exec Out (*outputs:execOut*)", "``execution``", "exec", "None"
    "Prims (*outputs:prims*)", "``target``", "Prim path of the created projection.", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.replicator.core.OgnCreateProjectionMaterial"
    "Version", "1"
    "Extension", "omni.replicator.core"
    "Has State?", "False"
    "Implementation Language", "Python"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Create Projection Material"
    "Categories", "Replicator:Core"
    "__categoryDescriptions", "Replicator:Core,Core Replicator nodes"
    "Generated Class Name", "OgnCreateProjectionMaterialDatabase"
    "Python Module", "omni.replicator.core"

