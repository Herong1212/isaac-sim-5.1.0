.. _isaacsim_ros2_bridge_ROS2PublishTransformTree_1:

.. _isaacsim_ros2_bridge_ROS2PublishTransformTree:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: ROS2 Publish Transform Tree
    :keywords: lang-en omnigraph node isaacRos2:publisher bridge r-o-s2-publish-transform-tree


ROS2 Publish Transform Tree
===========================

.. <description>

This node publishes the pose of prims as a ROS2 Transform Tree

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
    "Node Namespace (*inputs:nodeNamespace*)", "``string``", "Namespace of ROS2 Node, prepends any published/subscribed topic by the node namespace", ""
    "Parent Prim (*inputs:parentPrim*)", "``target``", "Prim used as parent frame for poses, leave blank to use World", "None"
    "Qos Profile (*inputs:qosProfile*)", "``string``", "QoS profile config", ""
    "Queue Size (*inputs:queueSize*)", "``uint64``", "The number of messages to queue up before throwing some away, in case messages are collected faster than they can be sent. Only honored if 'history' QoS policy was set to 'keep last'. This setting can be overwritten by qosProfile input.", "10"
    "Static Publisher (*inputs:staticPublisher*)", "``bool``", "If enabled this will override QoS settings to publish static transform trees, similar to tf2::StaticTransformBroadcaster", "False"
    "Target Prims (*inputs:targetPrims*)", "``target``", "Target prims to publish poses for, if prim is an articulation, the entire articulation tree will be published", "None"
    "", "Metadata", "*allowMultiInputs* = 1", ""
    "Timestamp (*inputs:timeStamp*)", "``double``", "ROS2 Timestamp in seconds", "0.0"
    "Topic Name (*inputs:topicName*)", "``string``", "Name of ROS2 Topic", "tf"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "isaacsim.ros2.bridge.ROS2PublishTransformTree"
    "Version", "1"
    "Extension", "isaacsim.ros2.bridge"
    "Icon", "ogn/icons/isaacsim.ros2.bridge.ROS2PublishTransformTree.svg"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "ROS2 Publish Transform Tree"
    "Categories", "isaacRos2:publisher"
    "Generated Class Name", "OgnROS2PublishTransformTreeDatabase"
    "Python Module", "isaacsim.ros2.bridge"

