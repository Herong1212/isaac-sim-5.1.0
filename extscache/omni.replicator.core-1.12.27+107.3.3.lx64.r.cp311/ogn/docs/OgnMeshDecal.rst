.. _omni_replicator_core_OgnMeshDecal_1:

.. _omni_replicator_core_OgnMeshDecal:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Ogn Mesh Decal
    :keywords: lang-en omnigraph node Replicator:Core compute-on-request core ogn-mesh-decal


Ogn Mesh Decal
==============

.. <description>

Mesh decal node

.. </description>


Installation
------------

To use this node enable :ref:`omni.replicator.core<ext_omni_replicator_core>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Decal Prim (*inputs:decalPrim*)", "``target``", "Existing decal mesh to modify.", "None"
    "Diffuse (*inputs:diffuse*)", "``token``", "Diffuse texture path of the decal material.", ""
    "Exec In (*inputs:execIn*)", "``execution``", "Input execution.", "None"
    "Material Prim (*inputs:materialPrim*)", "``target``", "Material to apply to decal mesh.", "None"
    "Metallic (*inputs:metallic*)", "``token``", "Metallic texture path of the decal material.", ""
    "Normal (*inputs:normal*)", "``token``", "Normal texture path of the decal material.", ""
    "Offset Depth (*inputs:offsetDepth*)", "``float``", "Offset depth of the decal.", "0.0"
    "Offset Normal (*inputs:offsetNormal*)", "``float``", "Offset along the normal of the decal.", "0.1"
    "Opacity (*inputs:opacity*)", "``token``", "Opacity texture path of the decal material.", ""
    "Position (*inputs:position*)", "``float[3]``", "Position override of the decal.", "[0, 0, 0]"
    "Prims (*inputs:prims*)", "``target``", "Prim to create a mesh decal on.", "None"
    "Rotation (*inputs:rotation*)", "``float[3]``", "Rotation override of the decal.", "[0, 0, 0]"
    "Roughness (*inputs:roughness*)", "``token``", "Roughness texture path of the decal material.", ""
    "Scale (*inputs:scale*)", "``float[3]``", "Scale override of the decal.", "[1, 1, 1]"
    "Semantics (*inputs:semantics*)", "``token``", "Semantics to apply to decal.", ""
    "Texture Group (*inputs:textureGroup*)", "``token[]``", "Group of diffuse, normal, roughness and/or metallic textures.", "[]"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Exec Out (*outputs:execOut*)", "``execution``", "Output execution.", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.replicator.core.OgnMeshDecal"
    "Version", "1"
    "Extension", "omni.replicator.core"
    "Has State?", "True"
    "Implementation Language", "Python"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "Categories", "Replicator:Core"
    "__categoryDescriptions", "Replicator:Core,Core Replicator nodes"
    "Generated Class Name", "OgnMeshDecalDatabase"
    "Python Module", "omni.replicator.core"

