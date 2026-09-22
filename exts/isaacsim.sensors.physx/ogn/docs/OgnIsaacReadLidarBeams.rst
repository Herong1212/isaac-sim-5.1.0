.. _isaacsim_sensors_physx_IsaacReadLidarBeams_1:

.. _isaacsim_sensors_physx_IsaacReadLidarBeams:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Isaac Read Lidar Beams Node
    :keywords: lang-en omnigraph node isaacPhysxSensor physx isaac-read-lidar-beams


Isaac Read Lidar Beams Node
===========================

.. <description>

This node reads from the lidar sensor and holds data buffers for a full scan

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

    "Azimuth Range (*outputs:azimuthRange*)", "``float[2]``", "The azimuth range [min, max]", "[0.0, 0.0]"
    "Beam Time Data (*outputs:beamTimeData*)", "``float[]``", "Buffer array containing beam time data", "[]"
    "Depth Range (*outputs:depthRange*)", "``float[2]``", "The min and max range for sensor to detect a hit [min, max]", "[0, 0]"
    "Exec Out (*outputs:execOut*)", "``execution``", "Output execution triggers when lidar sensor has completed a full scan", "None"
    "Horizontal Fov (*outputs:horizontalFov*)", "``float``", "Horizontal Field of View in degrees", "0"
    "Horizontal Resolution (*outputs:horizontalResolution*)", "``float``", "Degrees in between rays for horizontal axis", "0"
    "Intensities Data (*outputs:intensitiesData*)", "``uchar[]``", "Buffer array containing intensities data", "[]"
    "Linear Depth Data (*outputs:linearDepthData*)", "``float[]``", "Buffer array containing linear depth data", "[]"
    "Num Cols (*outputs:numCols*)", "``int``", "Number of columns in buffers", "0"
    "Num Rows (*outputs:numRows*)", "``int``", "Number of rows in buffers", "0"
    "Rotation Rate (*outputs:rotationRate*)", "``float``", "Rotation rate of sensor in Hz", "0"
    "Vertical Fov (*outputs:verticalFov*)", "``float``", "Vertical Field of View in degrees", "0"
    "Vertical Resolution (*outputs:verticalResolution*)", "``float``", "Degrees in between rays for vertical axis", "0"
    "Zenith Range (*outputs:zenithRange*)", "``float[2]``", "The zenith range [min, max]", "[0.0, 0.0]"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "isaacsim.sensors.physx.IsaacReadLidarBeams"
    "Version", "1"
    "Extension", "isaacsim.sensors.physx"
    "Icon", "ogn/icons/isaacsim.sensors.physx.IsaacReadLidarBeams.svg"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Isaac Read Lidar Beams Node"
    "Categories", "isaacPhysxSensor"
    "Generated Class Name", "OgnIsaacReadLidarBeamsDatabase"
    "Python Module", "isaacsim.sensors.physx"

