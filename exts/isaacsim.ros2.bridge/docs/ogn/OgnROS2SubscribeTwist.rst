.. _isaacsim_ros2_bridge_ROS2SubscribeTwist_1:

.. _isaacsim_ros2_bridge_ROS2SubscribeTwist:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: ROS2 Subscribe Twist
    :keywords: lang-en omnigraph node isaacRos2:subscriber bridge r-o-s2-subscribe-twist


ROS2 Subscribe Twist
====================

.. <description>

This node subscribes to a ROS2 Twist message

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
    "Exec In (*inputs:execIn*)", "``execution``", "The input execution port.", "None"
    "Node Namespace (*inputs:nodeNamespace*)", "``string``", "Namespace of ROS2 Node, prepends any published/subscribed topic by the node namespace", ""
    "Qos Profile (*inputs:qosProfile*)", "``string``", "QoS profile config", ""
    "Queue Size (*inputs:queueSize*)", "``uint64``", "The number of messages to queue up before throwing some away, in case messages are collected faster than they can be processed. Only honored if 'history' QoS policy was set to 'keep last'. This setting can be overwritten by qosProfile input.", "10"
    "Topic Name (*inputs:topicName*)", "``string``", "Name of ROS2 Topic", "cmd_vel"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Angular Velocity (*outputs:angularVelocity*)", "``vectord[3]``", "Angular velocity vector in rad/s", "[0.0, 0.0, 0.0]"
    "Exec Out (*outputs:execOut*)", "``execution``", "Output execution triggers when a new message is received", "None"
    "Linear Velocity (*outputs:linearVelocity*)", "``vectord[3]``", "Linear velocity vector in m/s", "[0.0, 0.0, 0.0]"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "isaacsim.ros2.bridge.ROS2SubscribeTwist"
    "Version", "1"
    "Extension", "isaacsim.ros2.bridge"
    "Icon", "ogn/icons/isaacsim.ros2.bridge.ROS2SubscribeTwist.svg"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "ROS2 Subscribe Twist"
    "Categories", "isaacRos2:subscriber"
    "Generated Class Name", "OgnROS2SubscribeTwistDatabase"
    "Python Module", "isaacsim.ros2.bridge"

