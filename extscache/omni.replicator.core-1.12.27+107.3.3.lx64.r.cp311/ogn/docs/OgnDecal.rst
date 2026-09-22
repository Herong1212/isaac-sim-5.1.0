.. _omni_replicator_core_OgnDecal_1:

.. _omni_replicator_core_OgnDecal:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Ogn Decal
    :keywords: lang-en omnigraph node core ogn-decal


Ogn Decal
=========

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

    "Clip Depth (*inputs:clip_depth*)", "``float``", "Depth along the z-axis of the clip volume", "100.0"
    "Clip Height (*inputs:clip_height*)", "``float``", "Height along the y-axis of the clip volume", "100.0"
    "Clip Width (*inputs:clip_width*)", "``float``", "Width along the x-axis of the clip volume", "100.0"
    "Clip Xform (*inputs:clip_xform*)", "``matrixd[4]``", "Collider mesh", "[[1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0], [0.0, 0.0, 1.0, 0.0], [0.0, 0.0, 0.0, 1.0]]"
    "Exec In (*inputs:execIn*)", "``execution``", "Input execution.", "None"
    "Mesh (*inputs:mesh*)", "``bundle``", "Cloth geometry", "None"
    "Offset Depth (*inputs:offset_depth*)", "``float``", "", "0.0"
    "Offset Normal (*inputs:offset_normal*)", "``float``", "", "0.1"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Exec Out (*outputs:execOut*)", "``execution``", "Output execution.", "None"
    "Mesh (*outputs:mesh*)", "``bundle``", "Decal mesh geometry", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.replicator.core.OgnDecal"
    "Version", "1"
    "Extension", "omni.replicator.core"
    "Has State?", "True"
    "Implementation Language", "Python"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "Generated Class Name", "OgnDecalDatabase"
    "Python Module", "omni.replicator.core"

