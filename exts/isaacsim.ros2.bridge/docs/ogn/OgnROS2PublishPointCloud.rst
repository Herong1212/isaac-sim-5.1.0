.. _isaacsim_ros2_bridge_ROS2PublishPointCloud_1:

.. _isaacsim_ros2_bridge_ROS2PublishPointCloud:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: ROS2 Publish Point Cloud
    :keywords: lang-en omnigraph node isaacRos2:publisher bridge r-o-s2-publish-point-cloud


ROS2 Publish Point Cloud
========================

.. <description>

This node publishes LiDAR scans as a ROS2 PointCloud2 message

.. </description>


Installation
------------

To use this node enable :ref:`isaacsim.ros2.bridge<ext_isaacsim_ros2_bridge>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Buffer Size (*inputs:bufferSize*)", "``uint``", "Size (in bytes) of the buffer (0 if the input is a texture)", "0"
    "Context (*inputs:context*)", "``uint64``", "ROS2 context handle, Default of zero will use the default global context", "0"
    "Cuda Device Index (*inputs:cudaDeviceIndex*)", "``int``", "Index of the device where the data lives (-1 for host data)", "-1"
    "Data (*inputs:data*)", "``pointf[3][]``", "Buffer array data, must contain data if dataPtr is null", "[]"
    "Data Ptr (*inputs:dataPtr*)", "``uint64``", "Pointer to the buffer data", "0"
    "Exec In (*inputs:execIn*)", "``execution``", "The input execution port", "None"
    "Frame Id (*inputs:frameId*)", "``string``", "FrameId for ROS2 message", "sim_lidar"
    "Node Namespace (*inputs:nodeNamespace*)", "``string``", "Namespace of ROS2 Node, prepends any published/subscribed topic by the node namespace", ""
    "Qos Profile (*inputs:qosProfile*)", "``string``", "QoS profile config", ""
    "Queue Size (*inputs:queueSize*)", "``uint64``", "The number of messages to queue up before throwing some away, in case messages are collected faster than they can be sent. Only honored if 'history' QoS policy was set to 'keep last'. This setting can be overwritten by qosProfile input.", "10"
    "Timestamp (*inputs:timeStamp*)", "``double``", "ROS2 Timestamp in seconds", "0.0"
    "Topic Name (*inputs:topicName*)", "``string``", "Name of ROS2 Topic", "point_cloud"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "isaacsim.ros2.bridge.ROS2PublishPointCloud"
    "Version", "1"
    "Extension", "isaacsim.ros2.bridge"
    "Icon", "ogn/icons/isaacsim.ros2.bridge.ROS2PublishPointCloud.svg"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "ROS2 Publish Point Cloud"
    "Categories", "isaacRos2:publisher"
    "Generated Class Name", "OgnROS2PublishPointCloudDatabase"
    "Python Module", "isaacsim.ros2.bridge"

