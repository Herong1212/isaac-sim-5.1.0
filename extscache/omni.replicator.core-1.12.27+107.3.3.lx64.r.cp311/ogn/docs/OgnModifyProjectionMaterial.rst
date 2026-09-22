.. _omni_replicator_core_OgnModifyProjectionMaterial_1:

.. _omni_replicator_core_OgnModifyProjectionMaterial:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Modify Projection Material
    :keywords: lang-en omnigraph node Replicator:Core compute-on-request core ogn-modify-projection-material


Modify Projection Material
==========================

.. <description>

This node prepares and/or projects a material on a bundle of prims.

.. </description>


Installation
------------

To use this node enable :ref:`omni.replicator.core<ext_omni_replicator_core>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Diffuse (*inputs:diffuse*)", "``token[]``", "Diffuse texture path of the projection.", "[]"
    "Exec In (*inputs:execIn*)", "``execution``", "exec", "None"
    "Metallic (*inputs:metallic*)", "``token[]``", "Metallic texture path of the projection.", "[]"
    "Normal (*inputs:normal*)", "``token[]``", "Normal texture path of the projection.", "[]"
    "Position (*inputs:position*)", "``float[3][]``", "Position override of the projection.", "[]"
    "Prims (*inputs:prims*)", "``target``", "Projection prim to modify.", "None"
    "Rotation (*inputs:rotation*)", "``float[3][]``", "Rotation override of the projection.", "[]"
    "Roughness (*inputs:roughness*)", "``token[]``", "Roughness texture path of the projection.", "[]"
    "Scale (*inputs:scale*)", "``float[3][]``", "Scale override of the projection.", "[]"
    "Texture Group (*inputs:textureGroup*)", "``token[]``", "Group of diffuse, normal, roughness and/or metallic textures.", "[]"


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

    "Unique ID", "omni.replicator.core.OgnModifyProjectionMaterial"
    "Version", "1"
    "Extension", "omni.replicator.core"
    "Has State?", "False"
    "Implementation Language", "Python"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Modify Projection Material"
    "Categories", "Replicator:Core"
    "__categoryDescriptions", "Replicator:Core,Core Replicator nodes"
    "Generated Class Name", "OgnModifyProjectionMaterialDatabase"
    "Python Module", "omni.replicator.core"

