.. _isaacsim_ros2_bridge_ROS2CameraInfoHelper_1:

.. _isaacsim_ros2_bridge_ROS2CameraInfoHelper:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: ROS2 Camera Info Helper
    :keywords: lang-en omnigraph node isaacRos2 bridge r-o-s2-camera-info-helper


ROS2 Camera Info Helper
=======================

.. <description>

This node automates the CameraInfo message pipeline for monocular and stereo cameras.

.. </description>


Installation
------------

To use this node enable :ref:`isaacsim.ros2.bridge<ext_isaacsim_ros2_bridge>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Context (*inputs:context*)", "``uint64``", "ROS2 context handle, Default of zero will use the default global context", "0"
    "Enabled (*inputs:enabled*)", "``bool``", "True to enable the camera helper, False to disable", "True"
    "Exec In (*inputs:execIn*)", "``execution``", "Triggering this causes the sensor pipeline to be generated", "None"
    "Frame Id (*inputs:frameId*)", "``string``", "FrameId for ROS2 message from the monocular or left stereo camera.", "sim_camera"
    "Frame Id Right (*inputs:frameIdRight*)", "``string``", "FrameId for ROS2 message from the right stereo camera.", "sim_camera_right"
    "Frame Skip Count (*inputs:frameSkipCount*)", "``uint``", "Specifies the number of simulation frames to skip between each message publish. (e.g. Set to 0 to publish each frame. Set 1 to publish every other frame)", "0"
    "Node Namespace (*inputs:nodeNamespace*)", "``string``", "Namespace of ROS2 Node, prepends any published/subscribed topic by the node namespace", ""
    "Qos Profile (*inputs:qosProfile*)", "``string``", "QoS profile config", ""
    "Queue Size (*inputs:queueSize*)", "``uint64``", "The number of messages to queue up before throwing some away, in case messages are collected faster than they can be sent. Only honored if 'history' QoS policy was set to 'keep last'. This setting can be overwritten by qosProfile input.", "10"
    "Render Product Path (*inputs:renderProductPath*)", "``token``", "Path of the render product used for capturing data from the monocular or left stereo camera", ""
    "Render Product Path Right (*inputs:renderProductPathRight*)", "``token``", "Path of the render product used for capturing data from the right stereo camera", "None"
    "Reset Simulation Time On Stop (*inputs:resetSimulationTimeOnStop*)", "``bool``", "If True the simulation time will reset when stop is pressed, False means time increases monotonically. This setting is ignored if useSystemTime is enabled.", "False"
    "Topic Name (*inputs:topicName*)", "``string``", "Topic name for the monocular or left stereo camera data.", "camera_info"
    "Topic Name Right (*inputs:topicNameRight*)", "``string``", "Topic name for the right stereo camera data.", "camera_info_right"
    "Use System Time (*inputs:useSystemTime*)", "``bool``", "If True, system timestamp will be included in messages. If False, simulation timestamp will be included in messages", "False"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "isaacsim.ros2.bridge.ROS2CameraInfoHelper"
    "Version", "1"
    "Extension", "isaacsim.ros2.bridge"
    "Icon", "ogn/icons/isaacsim.ros2.bridge.ROS2CameraInfoHelper.svg"
    "Has State?", "False"
    "Implementation Language", "Python"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "ROS2 Camera Info Helper"
    "Categories", "isaacRos2"
    "Generated Class Name", "OgnROS2CameraInfoHelperDatabase"
    "Python Module", "isaacsim.ros2.bridge"

