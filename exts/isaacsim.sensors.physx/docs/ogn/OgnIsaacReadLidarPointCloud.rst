.. _isaacsim_sensors_physx_IsaacReadLidarPointCloud_2:

.. _isaacsim_sensors_physx_IsaacReadLidarPointCloud:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Isaac Read Lidar Point Cloud Node
    :keywords: lang-en omnigraph node isaacPhysxSensor physx isaac-read-lidar-point-cloud


Isaac Read Lidar Point Cloud Node
=================================

.. <description>

This node reads from the lidar sensor and holds point cloud data buffers for a full scan

.. </description>


Installation
------------

To use this node enable :ref:`isaacsim.sensors.physx<ext_isaacsim_sensors_physx>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Exec In (*inputs:execIn*)", "``execution``", "The input execution port", "None"
    "Lidar Prim (*inputs:lidarPrim*)", "``target``", "Usd prim reference to the lidar prim", "None"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Data (*outputs:data*)", "``pointf[3][]``", "Buffer of 3d points containing point cloud data", "[]"
    "Exec Out (*outputs:execOut*)", "``execution``", "Output execution triggers when lidar sensor has completed a full scan", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "isaacsim.sensors.physx.IsaacReadLidarPointCloud"
    "Version", "2"
    "Extension", "isaacsim.sensors.physx"
    "Icon", "ogn/icons/isaacsim.sensors.physx.IsaacReadLidarPointCloud.svg"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Isaac Read Lidar Point Cloud Node"
    "Categories", "isaacPhysxSensor"
    "Generated Class Name", "OgnIsaacReadLidarPointCloudDatabase"
    "Python Module", "isaacsim.sensors.physx"

