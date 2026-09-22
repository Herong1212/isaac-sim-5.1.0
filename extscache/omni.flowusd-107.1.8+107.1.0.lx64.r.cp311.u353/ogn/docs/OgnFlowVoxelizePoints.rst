.. _omni_flowusd_FlowVoxelizePoints_1:

.. _omni_flowusd_FlowVoxelizePoints:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Flow Voxelize Points
    :keywords: lang-en omnigraph node FlowUsd flowusd flow-voxelize-points


Flow Voxelize Points
====================

.. <description>

Voxelize points to NanoVDB.

.. </description>


Installation
------------

To use this node enable :ref:`omni.flowusd<ext_omni_flowusd>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Cell Size (*inputs:cellSize*)", "``float``", "Voxel size", "0.1"
    "Colors (*inputs:colors*)", "``colorf[3][]``", "Point colors", "[]"
    "Local To World (*inputs:localToWorld*)", "``matrixd[4]``", "Local to World Transform", "[[1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0], [0.0, 0.0, 1.0, 0.0], [0.0, 0.0, 0.0, 1.0]]"
    "Max Flow Blocks (*inputs:maxBlocks*)", "``uint``", "Maximum Flow Block used during voxelization", "16384"
    "Points (*inputs:points*)", "``pointf[3][]``", "Point positions", "[]"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Alpha NanoVDB (*outputs:alphaNanoVdb*)", "``uint[]``", "NanoVDB with alpha channel", "None"
    "Blue NanoVDB (*outputs:blueNanoVdb*)", "``uint[]``", "NanoVDB with blue channel", "None"
    "Exec Out (*outputs:execOut*)", "``execution``", "Executes when values are updated", "None"
    "Green NanoVDB (*outputs:greenNanoVdb*)", "``uint[]``", "NanoVDB with green channel", "None"
    "Red NanoVDB (*outputs:redNanoVdb*)", "``uint[]``", "NanoVDB with red channel", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.flowusd.FlowVoxelizePoints"
    "Version", "1"
    "Extension", "omni.flowusd"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "tests"
    "uiName", "Flow Voxelize Points"
    "Categories", "FlowUsd"
    "Generated Class Name", "OgnFlowVoxelizePointsDatabase"
    "Python Module", "omni.flowusd"

