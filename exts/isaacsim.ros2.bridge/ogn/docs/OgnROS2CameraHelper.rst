.. _isaacsim_ros2_bridge_ROS2CameraHelper_2:

.. _isaacsim_ros2_bridge_ROS2CameraHelper:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: ROS2 Camera Helper
    :keywords: lang-en omnigraph node isaacRos2 bridge r-o-s2-camera-helper


ROS2 Camera Helper
==================

.. <description>

This node handles automation of the camera sensor pipeline

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
    "Enable Semantic Labels (*inputs:enableSemanticLabels*)", "``bool``", "Enable publishing of semantic labels, applies only to instance_segmentation, semantic_segmentation, bbox_2d_tight, bbox_2d_loose, bbox_3d", "False"
    "Enabled (*inputs:enabled*)", "``bool``", "True to enable the camera helper, False to disable", "True"
    "Exec In (*inputs:execIn*)", "``execution``", "Triggering this causes the sensor pipeline to be generated", "None"
    "Frame Id (*inputs:frameId*)", "``string``", "FrameId for ROS2 message, the nodeNamespace will not be prefixed to the frame id", "sim_camera"
    "Frame Skip Count (*inputs:frameSkipCount*)", "``uint``", "Specifies the number of simulation frames to skip between each message publish. (e.g. Set to 0 to publish each frame. Set 1 to publish every other frame)", "0"
    "Node Namespace (*inputs:nodeNamespace*)", "``string``", "Namespace of ROS2 Node, prepends any published/subscribed topic by the node namespace", ""
    "Qos Profile (*inputs:qosProfile*)", "``string``", "QoS profile config", ""
    "Queue Size (*inputs:queueSize*)", "``uint64``", "The number of messages to queue up before throwing some away, in case messages are collected faster than they can be sent. Only honored if 'history' QoS policy was set to 'keep last'. This setting can be overwritten by qosProfile input.", "10"
    "Render Product Path (*inputs:renderProductPath*)", "``token``", "Path of the render product used for capturing data", ""
    "Reset Simulation Time On Stop (*inputs:resetSimulationTimeOnStop*)", "``bool``", "If True the simulation time will reset when stop is pressed, False means time increases monotonically. This setting is ignored if useSystemTime is enabled.", "False"
    "Semantic Labels Topic Name (*inputs:semanticLabelsTopicName*)", "``string``", "Topic name used for publishing semantic labels, applies only to instance_segmentation, semantic_segmentation, bbox_2d_tight, bbox_2d_loose, bbox_3d", "semantic_labels"
    "Stereo Offset (*inputs:stereoOffset*)", "``float[2]``", "Stereo offset is the baseline between cameras in x and y component of the image plane in meters. (Tx, Ty is calculated using x and y component of StereoOffset value. i.e., Tx=fx*stereoOffset.X, Ty=fy*stereoOffset.Y). Used when publishing to the camera info topic", "[0, 0]"
    "Topic Name (*inputs:topicName*)", "``string``", "Topic name for sensor data", "rgb"
    "Type (*inputs:type*)", "``token``", "type", "rgb"
    "", "Metadata", "*allowedTokens* = rgb,depth,depth_pcl,instance_segmentation,semantic_segmentation,bbox_2d_tight,bbox_2d_loose,bbox_3d", ""
    "Use System Time (*inputs:useSystemTime*)", "``bool``", "If True, system timestamp will be included in messages. If False, simulation timestamp will be included in messages", "False"
    "Viewport (*inputs:viewport*)", "``token``", "DEPRECATED, use renderProductPath. Name of the desired viewport to publish", ""


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "isaacsim.ros2.bridge.ROS2CameraHelper"
    "Version", "2"
    "Extension", "isaacsim.ros2.bridge"
    "Icon", "ogn/icons/isaacsim.ros2.bridge.ROS2CameraHelper.svg"
    "Has State?", "False"
    "Implementation Language", "Python"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "ROS2 Camera Helper"
    "Categories", "isaacRos2"
    "Generated Class Name", "OgnROS2CameraHelperDatabase"
    "Python Module", "isaacsim.ros2.bridge"

