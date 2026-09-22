.. _isaacsim_ros2_bridge_ROS2RtxLidarHelper_1:

.. _isaacsim_ros2_bridge_ROS2RtxLidarHelper:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: ROS2 RTX Lidar Helper
    :keywords: lang-en omnigraph node isaacRos2 bridge r-o-s2-rtx-lidar-helper


ROS2 RTX Lidar Helper
=====================

.. <description>

Handles automation of Lidar Sensor pipeline

.. </description>


Installation
------------

To use this node enable :ref:`isaacsim.ros2.bridge<ext_isaacsim_ros2_bridge>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Context (*inputs:context*)", "``uint64``", "ROS2 context handle, default of zero will use the global context", "0"
    "Enabled (*inputs:enabled*)", "``bool``", "True to enable the lidar helper, False to disable", "True"
    "Exec In (*inputs:execIn*)", "``execution``", "Triggering this causes the sensor pipeline to be generated", "None"
    "Frame Id (*inputs:frameId*)", "``string``", "FrameID for the ROS2 message, the nodeNamespace will not be prefixed to the frame id", "sim_lidar"
    "Frame Skip Count (*inputs:frameSkipCount*)", "``uint``", "Specifies the number of simulation frames to skip between each message publish. (e.g. Set to 0 to publish each frame. Set 1 to publish every other frame)", "0"
    "Publish Full Scan (*inputs:fullScan*)", "``bool``", "If True publish a full scan when enough data has accumulated instead of partial scans each frame. Supports point cloud type only", "False"
    "Node Namespace (*inputs:nodeNamespace*)", "``string``", "Namespace of ROS2 Node, prepends and published/subscribed topic by the node namespace", ""
    "Qos Profile (*inputs:qosProfile*)", "``string``", "QoS profile config", ""
    "Queue Size (*inputs:queueSize*)", "``uint64``", "Number of message to queue up before throwing away, in case messages are collected faster than they can be sent. Only honored if 'history' QoS policy was set to 'keep last'. This setting can be overwritten by qosProfile input.", "10"
    "Render Product Path (*inputs:renderProductPath*)", "``token``", "Name of the render product path to publish lidar data", ""
    "Reset Time On Stop (*inputs:resetSimulationTimeOnStop*)", "``bool``", "If True the simulation time will reset when stop is pressed, False means time increases monotonically. This setting is ignored if useSystemTime is enabled.", "False"
    "Show Debug View (*inputs:showDebugView*)", "``bool``", "If True a debug view of the lidar particles will appear in the scene.", "False"
    "Topic Name (*inputs:topicName*)", "``string``", "Topic name for sensor data", "scan"
    "Type (*inputs:type*)", "``token``", "Data to publish from node", "laser_scan"
    "", "Metadata", "*allowedTokens* = laser_scan,point_cloud", ""
    "Use System Time (*inputs:useSystemTime*)", "``bool``", "If True, system timestamp will be included in messages. If False, simulation timestamp will be included in messages", "False"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "isaacsim.ros2.bridge.ROS2RtxLidarHelper"
    "Version", "1"
    "Extension", "isaacsim.ros2.bridge"
    "Icon", "ogn/icons/isaacsim.ros2.bridge.ROS2RtxLidarHelper.svg"
    "Has State?", "False"
    "Implementation Language", "Python"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "ROS2 RTX Lidar Helper"
    "Categories", "isaacRos2"
    "Generated Class Name", "OgnROS2RtxLidarHelperDatabase"
    "Python Module", "isaacsim.ros2.bridge"

