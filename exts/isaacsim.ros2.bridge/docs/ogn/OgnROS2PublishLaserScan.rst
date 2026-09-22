.. _isaacsim_ros2_bridge_ROS2PublishLaserScan_2:

.. _isaacsim_ros2_bridge_ROS2PublishLaserScan:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: ROS2 Publish Laser Scan
    :keywords: lang-en omnigraph node isaacRos2:publisher bridge r-o-s2-publish-laser-scan


ROS2 Publish Laser Scan
=======================

.. <description>

This node publishes LiDAR scans as a ROS2 LaserScan message

.. </description>


Installation
------------

To use this node enable :ref:`isaacsim.ros2.bridge<ext_isaacsim_ros2_bridge>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Azimuth Range (*inputs:azimuthRange*)", "``float[2]``", "The azimuth range [min, max] (deg). Always [-180, 180] for rotary lidars.", "[0.0, 0.0]"
    "Context (*inputs:context*)", "``uint64``", "ROS2 context handle, Default of zero will use the default global context", "0"
    "Depth Range (*inputs:depthRange*)", "``float[2]``", "Range for sensor to detect a hit [min, max] (m)", "[0, 0]"
    "Exec In (*inputs:execIn*)", "``execution``", "The input execution port", "None"
    "Frame Id (*inputs:frameId*)", "``string``", "FrameId for ROS2 message", "sim_lidar"
    "Horizontal Fov (*inputs:horizontalFov*)", "``float``", "Horizontal Field of View (deg)", "0"
    "Horizontal Resolution (*inputs:horizontalResolution*)", "``float``", "Increment between horizontal rays (deg)", "0"
    "Intensities Data (*inputs:intensitiesData*)", "``uchar[]``", "Intensity measurements from full scan, ordered by increasing azimuth", "[]"
    "Linear Depth Data (*inputs:linearDepthData*)", "``float[]``", "Linear depth measurements from full scan, ordered by increasing azimuth (m)", "[]"
    "Node Namespace (*inputs:nodeNamespace*)", "``string``", "Namespace of ROS2 Node, prepends any published/subscribed topic by the node namespace", ""
    "Num Cols (*inputs:numCols*)", "``int``", "Number of columns in buffers", "0"
    "Num Rows (*inputs:numRows*)", "``int``", "Number of rows in buffers", "0"
    "Qos Profile (*inputs:qosProfile*)", "``string``", "QoS profile config", ""
    "Queue Size (*inputs:queueSize*)", "``uint64``", "The number of messages to queue up before throwing some away, in case messages are collected faster than they can be sent. Only honored if 'history' QoS policy was set to 'keep last'. This setting can be overwritten by qosProfile input.", "10"
    "Rotation Rate (*inputs:rotationRate*)", "``float``", "Rotation rate of sensor in Hz", "0"
    "Timestamp (*inputs:timeStamp*)", "``double``", "ROS2 Timestamp in seconds", "0.0"
    "Topic Name (*inputs:topicName*)", "``string``", "Name of ROS2 Topic", "scan"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "isaacsim.ros2.bridge.ROS2PublishLaserScan"
    "Version", "2"
    "Extension", "isaacsim.ros2.bridge"
    "Icon", "ogn/icons/isaacsim.ros2.bridge.ROS2PublishLaserScan.svg"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "ROS2 Publish Laser Scan"
    "Categories", "isaacRos2:publisher"
    "Generated Class Name", "OgnROS2PublishLaserScanDatabase"
    "Python Module", "isaacsim.ros2.bridge"

