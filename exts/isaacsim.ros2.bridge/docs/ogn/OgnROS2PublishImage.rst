.. _isaacsim_ros2_bridge_ROS2PublishImage_1:

.. _isaacsim_ros2_bridge_ROS2PublishImage:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: ROS2 Publish Image
    :keywords: lang-en omnigraph node isaacRos2:publisher bridge r-o-s2-publish-image


ROS2 Publish Image
==================

.. <description>

This node publishes ROS2 Image messages

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
    "Data (*inputs:data*)", "``uchar[]``", "Buffer array data", "[]"
    "Data Ptr (*inputs:dataPtr*)", "``uint64``", "Pointer to the raw rgba array data", "0"
    "Encoding (*inputs:encoding*)", "``token``", "ROS encoding format for the input data, taken from the list of strings in include/sensor_msgs/image_encodings.h. Input data is expected to already be in this format, no conversions are performed", "rgb8"
    "", "Metadata", "*allowedTokens* = rgb8,rgba8,32FC1,32SC1", ""
    "Exec In (*inputs:execIn*)", "``execution``", "The input execution port.", "None"
    "Format (*inputs:format*)", "``uint64``", "Format", "0"
    "Frame Id (*inputs:frameId*)", "``string``", "FrameId for ROS2 message", "sim_camera"
    "Height (*inputs:height*)", "``uint``", "Buffer array height", "0"
    "Node Namespace (*inputs:nodeNamespace*)", "``string``", "Namespace of ROS2 Node, prepends any published/subscribed topic by the node namespace", ""
    "Qos Profile (*inputs:qosProfile*)", "``string``", "QoS profile config", ""
    "Queue Size (*inputs:queueSize*)", "``uint64``", "The number of messages to queue up before throwing some away, in case messages are collected faster than they can be sent. Only honored if 'history' QoS policy was set to 'keep last'. This setting can be overwritten by qosProfile input.", "10"
    "Time Stamp (*inputs:timeStamp*)", "``double``", "Time in seconds to use when publishing the message", "0.0"
    "Topic Name (*inputs:topicName*)", "``string``", "Name of ROS2 Topic", "rgb"
    "Width (*inputs:width*)", "``uint``", "Buffer array width", "0"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "isaacsim.ros2.bridge.ROS2PublishImage"
    "Version", "1"
    "Extension", "isaacsim.ros2.bridge"
    "Icon", "ogn/icons/isaacsim.ros2.bridge.ROS2PublishImage.svg"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "ROS2 Publish Image"
    "Categories", "isaacRos2:publisher"
    "Generated Class Name", "OgnROS2PublishImageDatabase"
    "Python Module", "isaacsim.ros2.bridge"

