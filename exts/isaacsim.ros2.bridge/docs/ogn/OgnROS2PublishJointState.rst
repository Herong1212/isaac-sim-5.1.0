.. _isaacsim_ros2_bridge_ROS2PublishJointState_1:

.. _isaacsim_ros2_bridge_ROS2PublishJointState:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: ROS2 Publish Joint State
    :keywords: lang-en omnigraph node isaacRos2:publisher bridge r-o-s2-publish-joint-state


ROS2 Publish Joint State
========================

.. <description>

This node publishes joint states of a robot in ROS2 JointState message

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
    "Node Namespace (*inputs:nodeNamespace*)", "``string``", "Name of ROS2 Node, prepends any topic published/subscribed by the node name", ""
    "Qos Profile (*inputs:qosProfile*)", "``string``", "QoS profile config", ""
    "Queue Size (*inputs:queueSize*)", "``uint64``", "The number of messages to queue up before throwing some away, in case messages are collected faster than they can be sent. Only honored if 'history' QoS policy was set to 'keep last'. This setting can be overwritten by qosProfile input.", "10"
    "Target Prim (*inputs:targetPrim*)", "``target``", "USD reference to the robot prim", "None"
    "Timestamp (*inputs:timeStamp*)", "``double``", "ROS2 Timestamp in seconds", "0.0"
    "Topic Name (*inputs:topicName*)", "``string``", "Name of ROS2 Topic", "joint_states"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "isaacsim.ros2.bridge.ROS2PublishJointState"
    "Version", "1"
    "Extension", "isaacsim.ros2.bridge"
    "Icon", "ogn/icons/isaacsim.ros2.bridge.ROS2PublishJointState.svg"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "ROS2 Publish Joint State"
    "Categories", "isaacRos2:publisher"
    "Generated Class Name", "OgnROS2PublishJointStateDatabase"
    "Python Module", "isaacsim.ros2.bridge"

