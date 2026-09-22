.. _isaacsim_ros2_bridge_ROS2PublishCameraInfo_2:

.. _isaacsim_ros2_bridge_ROS2PublishCameraInfo:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: ROS2 Publish Camera Info
    :keywords: lang-en omnigraph node isaacRos2:publisher bridge r-o-s2-publish-camera-info


ROS2 Publish Camera Info
========================

.. <description>

This node publishes camera info as a ROS2 CameraInfo message

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
    "Exec In (*inputs:execIn*)", "``execution``", "The input execution port", "None"
    "Frame Id (*inputs:frameId*)", "``string``", "FrameId for ROS2 message", "sim_camera"
    "Height (*inputs:height*)", "``uint``", "Height for output image", "0"
    "K (*inputs:k*)", "``double[]``", "3x3 Intrinsic camera matrix for the raw (distorted) images. Projects 3D points in the camera coordinate frame to 2D pixel coordinates using the focal lengths and principal point.", "[]"
    "Node Namespace (*inputs:nodeNamespace*)", "``string``", "Namespace of ROS2 Node, prepends any published/subscribed topic by the node namespace", ""
    "P (*inputs:p*)", "``double[]``", "3x4 Rectification matrix (stereo cameras only). A rotation matrix aligning the camera coordinate system to the ideal stereo image plane so that epipolar lines in both stereo images are parallel.", "[]"
    "Physical Distortion Coefficients (*inputs:physicalDistortionCoefficients*)", "``float[]``", "physical distortion model used for approximation, physicalDistortionModel must be set to use these coefficients", "[]"
    "Physical Distortion Model (*inputs:physicalDistortionModel*)", "``token``", "physical distortion model used for approximation, if blank projectionType is used", ""
    "Projection Type (*inputs:projectionType*)", "``token``", "projection type", ""
    "Qos Profile (*inputs:qosProfile*)", "``string``", "QoS profile config", ""
    "Queue Size (*inputs:queueSize*)", "``uint64``", "The number of messages to queue up before throwing some away, in case messages are collected faster than they can be sent. Only honored if 'history' QoS policy was set to 'keep last'. This setting can be overwritten by qosProfile input.", "10"
    "R (*inputs:r*)", "``double[]``", "3x3 Rectification matrix (stereo cameras only). A rotation matrix aligning the camera coordinate system to the ideal stereo image plane so that epipolar lines in both stereo images are parallel.", "[]"
    "Timestamp (*inputs:timeStamp*)", "``double``", "ROS2 Timestamp in seconds", "0.0"
    "Topic Name (*inputs:topicName*)", "``string``", "Name of ROS2 Topic", "camera_info"
    "Width (*inputs:width*)", "``uint``", "Width for output image", "0"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "isaacsim.ros2.bridge.ROS2PublishCameraInfo"
    "Version", "2"
    "Extension", "isaacsim.ros2.bridge"
    "Icon", "ogn/icons/isaacsim.ros2.bridge.ROS2PublishCameraInfo.svg"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "ROS2 Publish Camera Info"
    "Categories", "isaacRos2:publisher"
    "Generated Class Name", "OgnROS2PublishCameraInfoDatabase"
    "Python Module", "isaacsim.ros2.bridge"

