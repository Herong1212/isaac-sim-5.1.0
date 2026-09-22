.. _isaacsim_ros2_bridge_ROS2PublishBbox3D_1:

.. _isaacsim_ros2_bridge_ROS2PublishBbox3D:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: ROS2 Publish Bbox3D
    :keywords: lang-en omnigraph node isaacRos2:publisher bridge r-o-s2-publish-bbox3-d


ROS2 Publish Bbox3D
===================

.. <description>

This node publishes ROS2 Bbox3d messages

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
    "Data (*inputs:data*)", "``uchar[]``", "Buffer array data", "[]"
    "Exec In (*inputs:execIn*)", "``execution``", "The input execution port.", "None"
    "Frame Id (*inputs:frameId*)", "``string``", "FrameId for ROS2 message", "sim_camera"
    "Node Namespace (*inputs:nodeNamespace*)", "``string``", "Namespace of ROS2 Node, prepends any published/subscribed topic by the node namespace", ""
    "Qos Profile (*inputs:qosProfile*)", "``string``", "QoS profile config", ""
    "Queue Size (*inputs:queueSize*)", "``uint64``", "The number of messages to queue up before throwing some away, in case messages are collected faster than they can be sent. Only honored if 'history' QoS policy was set to 'keep last'. This setting can be overwritten by qosProfile input.", "10"
    "Time Stamp (*inputs:timeStamp*)", "``double``", "Time in seconds to use when publishing the message", "0.0"
    "Topic Name (*inputs:topicName*)", "``string``", "Name of ROS2 Topic", "bbox3d"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "isaacsim.ros2.bridge.ROS2PublishBbox3D"
    "Version", "1"
    "Extension", "isaacsim.ros2.bridge"
    "Icon", "ogn/icons/isaacsim.ros2.bridge.ROS2PublishBbox3D.svg"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "ROS2 Publish Bbox3D"
    "Categories", "isaacRos2:publisher"
    "Generated Class Name", "OgnROS2PublishBbox3DDatabase"
    "Python Module", "isaacsim.ros2.bridge"

