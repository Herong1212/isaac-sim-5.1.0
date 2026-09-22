.. _omni_replicator_core_OgnMeshBoundsDecalPlacement_1:

.. _omni_replicator_core_OgnMeshBoundsDecalPlacement:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Ogn Mesh Bounds Decal Placement
    :keywords: lang-en omnigraph node Replicator:Core compute-on-request core ogn-mesh-bounds-decal-placement


Ogn Mesh Bounds Decal Placement
===============================

.. <description>

The position and rotation of a mesh for decal placement from mesh bounds.

.. </description>


Installation
------------

To use this node enable :ref:`omni.replicator.core<ext_omni_replicator_core>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Bounds Vector (*inputs:boundsVector*)", "``float[3]``", "Normalized vector to determine translation and rotation in bounds.", "[0.0, 0.0, 0.0]"
    "Exec In (*inputs:execIn*)", "``execution``", "Input execution.", "None"
    "Offset (*inputs:offset*)", "``float``", "How much to offset the final translation away from the bounds.", "0.0"
    "Prims (*inputs:prims*)", "``target``", "Input prims to calculate bounds from.", "None"
    "Rotation (*inputs:rotation*)", "``float[3]``", "Additional rotation.", "[0.0, 0.0, 0.0]"
    "Scale (*inputs:scale*)", "``float[3]``", "Scale to match bounds.", "[0.0, 0.0, 0.0]"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Exec Out (*outputs:execOut*)", "``execution``", "Output execution.", "None"
    "Rotation (*outputs:rotation*)", "``float[3]``", "The resulting local rotation (XYZ).", "None"
    "Scale (*outputs:scale*)", "``float[3]``", "The resulting local scale.", "None"
    "Translate (*outputs:translate*)", "``float[3]``", "The resulting world translation.", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.replicator.core.OgnMeshBoundsDecalPlacement"
    "Version", "1"
    "Extension", "omni.replicator.core"
    "Has State?", "False"
    "Implementation Language", "Python"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "Categories", "Replicator:Core"
    "__categoryDescriptions", "Replicator:Core,Core Replicator nodes"
    "Generated Class Name", "OgnMeshBoundsDecalPlacementDatabase"
    "Python Module", "omni.replicator.core"

